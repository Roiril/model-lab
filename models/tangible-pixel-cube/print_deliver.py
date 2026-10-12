"""刷るファイルを作る: 部品ごとの STL、プレートに並べた 3mf（PLA / PETG）、試し刷りのプレート、質量の見込み。

    py -3.11 models/tangible-pixel-cube/print_deliver.py

前提（この順に流す）:
  1. model.py        build/print_<id>.stl（刷る向き）
  2. print_trials.py  prints/tangible-pixel-cube/trial/*.stl（試し刷りの小片。Blender）
  3. print_review.py  build/print_review.json（刷れるかの精査と部品ごとの質量）

出力（prints/tangible-pixel-cube/）:
  parts/<id>.stl, trial/<名前>.stl
  tangible-pixel-cube-<プレート>-<PLA|PETG>.3mf   … tools/plate_3mf.py で並べ、Bambu Studio の CLI で
                                                   X1C 0.4 / 0.20mm Standard / 材料を埋めた（スライスはしない）
  plates.json                                       … プレートの分け方・理由・配置の検査・質量の見込み

配置は tools/plate_3mf.py（棚づめ、部品の間 6mm、余白 10mm、X1C 256 x 256、手前左 18 x 28 は除外域）。
Bambu Studio の CLI は --arrange 0 で配置を保ったまま、プロファイル（材料・工程）だけを 3mf へ入れる。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.stdout.reconfigure(encoding="utf-8")

import print_kit as K  # noqa: E402
from bambu_profiles import resolve, write_flat  # noqa: E402

BUILD = os.path.join(HERE, "build")
PRINTS = os.path.join(ROOT, "prints", "tangible-pixel-cube")
PARTS_DIR = os.path.join(PRINTS, "parts")
TRIAL_DIR = os.path.join(PRINTS, "trial")
EXE = r"C:\Program Files\Bambu Studio\bambu-studio.exe"
WORK = None                                           # main() が一時ディレクトリを入れる
MODEL = "tangible-pixel-cube"

MACHINE = "Bambu Lab X1 Carbon 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL X1C"
FILAMENT = {"PLA": "Bambu PLA Basic @BBL X1C", "PETG": "Bambu PETG Basic @BBL X1C"}
OVERRIDES = {"curr_bed_type": "Textured PEI Plate", "seam_position": "back", "exclude_object": "1", "enable_support": "0"}

BED = (256.0, 256.0, 250.0)
EXCLUDE = (18.0, 28.0)

pixels = [f"pixel_{i}_{j}" for j in range(5) for i in range(5)]
cams = [f"cam_{i}_{j}" for j in range(5) for i in range(5)]
shafts = [f"shaft_{j}" for j in range(5)]
gears = [f"gear_{j}" for j in range(5)]
shaft_clips = [f"shaft_clip_{j}" for j in range(5)]
servo_clips = ["servo_clip_0", "servo_clip_1"]

PLATES = [
    {"id": "plate1-shell", "title": "外装・ベゼル・案内板・受け・治具",
     "parts": ["housing", "bezel", "guide_plate", "horn_coupler", "phase_comb"],
     "reason": "大きい 3 部品（96 x 96、96 x 96、90 x 92）と受け・治具。外装 93mm と案内板 28mm の高さが違うので、"
               "細かい部品と同じ板に混ぜない（背の高い外装の周りへヘッドが何度も回る）。外装とベゼルは見える面を刷るので、"
               "ほかの物の失敗に巻き込まない"},
    {"id": "plate2-pixels", "title": "画素 25 個", "parts": pixels,
     "reason": "画素は 36mm の高さで 25 個。1 層ごとに 25 個を順に積むので時間の大半を占める。物体ごとに止められる設定"
               "（exclude_object）で、失敗した 1 個だけ外して続けられる。足の向きがそろうので配置も単純"},
    {"id": "plate3-mechanism", "title": "カム 25・軸 5・歯車 5・クリップ 7",
     "parts": cams + shafts + gears + shaft_clips + servo_clips,
     "reason": "カム・軸・歯車・クリップは高さ 17mm 以下の低い部品で、かたまりで刷れる。画素と外装を合わせた 1 枚には、"
               "全部品の外接面積は合計およそ 5.2 万 mm2、部品間 6mm の間隔を足すと約 7.4 万 mm2 で、プレートの実効面積（余白 10mm を除いて約 5.4 万 mm2）の 1.4 倍。1 枚には入らない"},
]

TRIAL_PLATES = [
    {"id": "trial1-rotating", "title": "試し刷り 1: 回す・噛み合わせる部分",
     "parts": ["horn_coupler", "shaft_2_plusX_end", "shaft_2_minusX_end", "cam_4_2", "gear_2", "shaft_clip_2"],
     "reason": "受けとホーン、軸とカム・歯車（潰しリブ）、C クリップ。実物（SG92R とホーン）が要るのは受けだけ"},
    {"id": "trial2-shell-guide-pixel", "title": "試し刷り 2: 外装・案内・画素・ベゼル",
     "parts": ["housing_Uslot_shaft1_plusX", "housing_servo_block_minusY", "servo_clip_0", "guide_plate_cell_2_2",
               "guide_plate_tongue_plusX", "pixel_2_2_top", "pixel_2_2_foot", "bezel_window_2_2", "bezel_barb_plusX",
               "housing_endwall_pockets_plusX"],
     "reason": "外装の U 溝と柵、案内板の十字穴・舌と画素、ベゼルの窓と爪と外装の端壁の窪み。どれも小片で、軸の丸・サーボの耳・"
               "画素の頭と足を実際に当てて確かめる"},
]


def part_path(name):
    p = os.path.join(PARTS_DIR, f"{name}.stl")
    return p if os.path.exists(p) else os.path.join(TRIAL_DIR, f"{name}.stl")


# =============================================================================================
# 3mf の検査（Bambu Studio が書いた最終ファイルを読んで、配置を独立に確かめる）
# =============================================================================================
CORE = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
PROD = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"


def apply_tf(vs, tf):
    a, b, c, d, e, f, g, h, i, tx, ty, tz = tf
    m = np.array([[a, b, c], [d, e, f], [g, h, i]])
    return vs @ m + np.array([tx, ty, tz])


def verify_3mf(path, expected):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    root = ET.fromstring(z.read("3D/3dmodel.model"))
    cfg = ET.fromstring(z.read("Metadata/model_settings.config"))
    obj_name = {}
    for o in cfg.findall("object"):
        obj_name[o.get("id")] = next((m.get("value") for m in o.findall("metadata") if m.get("key") == "name"), None)
    resources = {}
    cache = {}
    for o in root.iter(CORE + "object"):
        comps = []
        for c in o.iter(CORE + "component"):
            comps.append((c.get(PROD + "path"), c.get("objectid"),
                          [float(v) for v in (c.get("transform") or "1 0 0 0 1 0 0 0 1 0 0 0").split()]))
        resources[o.get("id")] = comps
    boxes = {}
    all_vertices = {}
    for it in root.iter(CORE + "item"):
        oid = it.get("objectid")
        tf = [float(v) for v in (it.get("transform") or "1 0 0 0 1 0 0 0 1 0 0 0").split()]
        vs_all = []
        for pth, cid, ctf in resources[oid]:
            key = pth.lstrip("/")
            if key not in cache:
                cache[key] = z.read(key).decode("utf-8")
            text = cache[key]
            m = re.search(rf'<object id="{cid}"[^>]*>(.*?)</object>', text, re.S)
            body = m.group(1) if m else text
            vs = np.array([[float(x), float(y), float(zz)] for x, y, zz in
                           re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', body)])
            vs_all.append(apply_tf(apply_tf(vs, ctf), tf))
        vs = np.vstack(vs_all)
        nm = obj_name.get(oid) or oid
        boxes[nm] = (vs.min(axis=0), vs.max(axis=0))
        all_vertices[nm] = vs
    got = sorted(boxes)
    sep_min, pair = float("inf"), None
    ns = list(boxes)
    for i in range(len(ns)):
        for j in range(i + 1, len(ns)):
            a, b = boxes[ns[i]], boxes[ns[j]]
            gap = max(max(a[0][0] - b[1][0], b[0][0] - a[1][0]), max(a[0][1] - b[1][1], b[0][1] - a[1][1]))
            if gap < sep_min:
                sep_min, pair = gap, (ns[i], ns[j])
    lo = np.min([b[0] for b in boxes.values()], axis=0)
    hi = np.max([b[1] for b in boxes.values()], axis=0)
    excl = [n for n, v in all_vertices.items() if np.any((v[:, 0] < EXCLUDE[0]) & (v[:, 1] < EXCLUDE[1]))]
    off = [n for n, (a, b) in boxes.items() if a[0] < 0 or a[1] < 0 or b[0] > BED[0] or b[1] > BED[1] or b[2] > BED[2]]
    ps = json.loads(z.read("Metadata/project_settings.config").decode("utf-8"))
    return {
        "objects": len(boxes), "names_match": got == sorted(expected),
        "min_gap_between_boxes_mm": round(sep_min, 2), "closest_pair": pair,
        "overlap": bool(sep_min < 0), "off_bed": off, "in_exclusion_zone": excl,
        "xy_extent_mm": [round(float(lo[0]), 1), round(float(lo[1]), 1), round(float(hi[0]), 1), round(float(hi[1]), 1)],
        "max_height_mm": round(float(hi[2]), 1),
        "filament_type": ps.get("filament_type"), "filament_preset": ps.get("filament_settings_id"),
        "printer_preset": ps.get("printer_settings_id"), "process_preset": ps.get("print_settings_id"),
        "bed_type": ps.get("curr_bed_type"), "elefant_foot_compensation": ps.get("elefant_foot_compensation"),
        "wall_loops": ps.get("wall_loops"), "sparse_infill_density": ps.get("sparse_infill_density"),
        "seam_position": ps.get("seam_position"), "enable_support": ps.get("enable_support"),
        "has_gcode": any(n.endswith(".gcode") for n in names),
    }


# =============================================================================================
def run_plate_tool(plate_id, parts):
    """tools/plate_3mf.py で並べる。exports/ に書かれる 3mf を WORK へ移し、標準出力を返す。"""
    tmp_name = f"tpc-{plate_id}"
    exports_file = os.path.join(ROOT, "exports", tmp_name + ".3mf")
    if os.path.exists(exports_file):
        os.remove(exports_file)
    files = [part_path(p) for p in parts]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "plate_3mf.py"), tmp_name] + files,
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0 or not os.path.exists(exports_file):
        raise SystemExit(f"plate_3mf.py が失敗: {r.stdout[-800:]}{r.stderr[-800:]}")
    dest = os.path.join(WORK, f"{plate_id}-placement.3mf")
    if os.path.exists(dest):
        os.remove(dest)
    shutil.move(exports_file, dest)
    log = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("[plate]")]
    return dest, log


def export_project(placement, material, out_name, profiles):
    """配置を保ったまま、X1C・0.20mm Standard・材料のプロファイルを埋めた 3mf にする（スライスしない）。"""
    m, p, f = profiles[material]
    cmd = [EXE, "--export-3mf", out_name, "--outputdir", PRINTS, "--load-settings", f"{m};{p}", "--load-filaments", f,
           "--arrange", "0", placement]
    r = subprocess.run(cmd, cwd=WORK, capture_output=True, text=True, encoding="utf-8", errors="replace")
    path = os.path.join(PRINTS, out_name)
    if r.returncode != 0 or not os.path.exists(path):
        raise SystemExit(f"bambu-studio の書き出しが失敗 ({r.returncode}): {(r.stdout or '')[-800:]}{(r.stderr or '')[-800:]}")
    return path


def main():
    global WORK
    WORK = tempfile.mkdtemp(prefix="tpc-deliver-")        # 配置の途中ファイルとプロファイルの置き場（終わったら消す）
    try:
        run()
    finally:
        shutil.rmtree(WORK, ignore_errors=True)


def run():
    os.makedirs(PARTS_DIR, exist_ok=True)
    review = json.load(open(os.path.join(BUILD, "print_review.json"), encoding="utf-8"))
    if "parts" not in review:
        raise SystemExit("build/print_review.json が校正に失敗した状態。先に print_review.py を通す")
    manifest = json.load(open(os.path.join(BUILD, "manifest.json"), encoding="utf-8"))
    print_ids = [p["id"] for p in manifest["parts"] if p.get("print")]
    for pid in print_ids:
        shutil.copyfile(os.path.join(BUILD, f"print_{pid}.stl"), os.path.join(PARTS_DIR, f"{pid}.stl"))
    trial_names = sorted(review.get("trial_pieces", {}))
    for name in trial_names:
        if not os.path.exists(os.path.join(TRIAL_DIR, f"{name}.stl")):
            raise SystemExit(f"試し刷りの小片がない: {name}（print_trials.py を先に流す）")

    # プロファイル（継承を解いて平らにする）
    m = resolve("machine", MACHINE)
    p = resolve("process", PROCESS)
    p.update(OVERRIDES)
    profiles = {}
    for mat, fn in FILAMENT.items():
        profiles[mat] = (write_flat(os.path.join(WORK, "machine.json"), m), write_flat(os.path.join(WORK, "process.json"), p),
                         write_flat(os.path.join(WORK, f"filament_{mat}.json"), resolve("filament", fn)))

    # 部品が全部どこかのプレートに載るか
    placed = [x for pl in PLATES for x in pl["parts"]]
    assert sorted(placed) == sorted(print_ids), "プレートの分け方が印刷部品と合わない"
    assert sorted(x for pl in TRIAL_PLATES for x in pl["parts"]) == sorted(trial_names), "試し刷りの割り当てが小片と合わない"

    def mass_of(name):
        if name in review["parts"]:
            return review["parts"][name]["mass_pla"]
        return review["trial_pieces"][name]["mass_pla"]

    out_plates = []
    for kind, plates in (("main", PLATES), ("trial", TRIAL_PLATES)):
        for pl in plates:
            placement, log = run_plate_tool(pl["id"], pl["parts"])
            files = {}
            verify = {}
            for mat in ("PLA", "PETG"):
                out_name = f"{MODEL}-{pl['id']}-{mat}.3mf"
                path = export_project(placement, mat, out_name, profiles)
                files[mat] = os.path.relpath(path, ROOT).replace("\\", "/")
                verify[mat] = verify_3mf(path, pl["parts"])
            mass = sum(mass_of(x)["mass_g"] for x in pl["parts"])
            solid = sum(mass_of(x)["solid_g"] for x in pl["parts"])
            hts = [max(review["parts"][x]["size_mm"][2] if x in review["parts"] else review["trial_pieces"][x]["size_mm"][2]
                       for x in pl["parts"])]
            row = {"kind": kind, "id": pl["id"], "title": pl["title"], "reason": pl["reason"], "n_parts": len(pl["parts"]),
                   "parts": pl["parts"], "files": files, "plate_tool_log": log, "verify": verify,
                   "mass_pla_g": round(mass, 1), "mass_solid_upper_g": round(solid, 1), "tallest_part_mm": hts[0]}
            out_plates.append(row)
            v = verify["PLA"]
            print(f"  {pl['id']:28s} {len(pl['parts']):3d} 部品  {v['xy_extent_mm']} 高さ {v['max_height_mm']}  "
                  f"重なり {'あり' if v['overlap'] else 'なし'}（最小の間隔 {v['min_gap_between_boxes_mm']}mm）"
                  f" はみ出し {v['off_bed'] or 'なし'} 除外域 {v['in_exclusion_zone'] or 'なし'}  PLA {mass:.1f}g")
            for ln in log:
                print("     ", ln)

    mass_rows = {k: v["mass_pla"] for k, v in review["parts"].items()}
    total = round(sum(v["mass_g"] for v in mass_rows.values()), 1)
    total_solid = round(sum(v["solid_g"] for v in mass_rows.values()), 1)
    doc = {
        "model": MODEL, "generated_by": "models/tangible-pixel-cube/print_deliver.py",
        "settings": {"machine": MACHINE, "process": PROCESS, "filament": FILAMENT, "overrides": OVERRIDES,
                     "bed_mm": BED, "exclusion_front_left_mm": EXCLUDE,
                     "note": "スライスはしていない（G-code なし）。Bambu Studio で開いて切る。時間は Bambu Studio で確認"},
        "mass_formula": K.estimate_mass.__doc__.strip(),
        "mass_total_pla_g": total, "mass_total_solid_upper_g": total_solid,
        "plates": out_plates, "mass_by_part": mass_rows,
        "trial_mass_by_piece": {n: review["trial_pieces"][n]["mass_pla"] for n in trial_names},
    }
    path = os.path.join(PRINTS, "plates.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    print(f"== 全部品 PLA {total}g（全部中実なら上限 {total_solid}g）、プレート {len(out_plates)} 枚（うち試し刷り 2）-> {path}")


if __name__ == "__main__":
    main()
