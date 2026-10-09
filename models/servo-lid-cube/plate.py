"""刷る 3mf を作る（Bambu Studio の CLI で切った、そのまま印刷に送れる .gcode.3mf）。

    py -3.11 models/servo-lid-cube/plate.py

流れ:
  1. 刷る向きの STL（exports/servo-lid-cube-*.stl）を build/print/ へ。箱は 180° 回して後ろ面を奥へ向ける
  2. 平らにした標準プロファイル＋上書き（print_profile.py）で 1 度切る（CLI が自動で並べる）
  3. できた 3mf に「高さごとの層の厚み」を足して切り直す（箱の節の上面・蓋の筒の段を細かく）
  4. G-code を物体ごとに分けて確かめる: 層の厚みが変わったか、支えの無い押し出し、サポートの有無
出力: exports/servo-lid-cube-<材料>.gcode.3mf と exports/servo-lid-cube-crank-test-<材料>.gcode.3mf、
      build/plate_report.json
"""
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import print_profile  # noqa: E402
from slice_check import EXE, parse_gcode, floating_report  # noqa: E402

EXPORTS = os.path.join(ROOT, "exports")
WORK = os.path.join(HERE, "build", "print")
PARTS = ["box", "lid", "crank", "link", "pin", "clip"]
ROTATE_Z = {"box": 180.0}          # 箱の後ろ面（蝶番側）を奥へ。継ぎ目が後ろに寄る
# 高さごとの層の厚み（刷る姿勢の z、mm）。上向きの浅い丸みが外から見える所だけ細かくする
RANGES = {"box": [(74.0, 80.0, 0.08)], "lid": [(5.0, 10.4, 0.08)]}


def read_stl(path):
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[80:84])[0]
    return [struct.unpack("<9f", raw[84 + 50 * i + 12:84 + 50 * i + 48]) for i in range(n)]


def write_stl(path, tris):
    with open(path, "wb") as fh:
        fh.write(b"\0" * 80 + struct.pack("<I", len(tris)))
        for t in tris:
            fh.write(struct.pack("<12fH", 0, 0, 0, *t, 0))


def rotated(tris, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    out = []
    for t in tris:
        v = []
        for k in range(3):
            x, y, z = t[3 * k:3 * k + 3]
            v += [x * c - y * s, x * s + y * c, z]
        out.append(tuple(v))
    return out


def slice_cli(inputs, out_dir, out_name, material=None, arrange=True):
    os.makedirs(out_dir, exist_ok=True)
    cmd = [EXE, "--slice", "0", "--debug", "2", "--outputdir", out_dir, "--export-3mf", out_name]
    if arrange:
        cmd += ["--arrange", "1"]
    if material:
        m, p, f = print_profile.settings(material)
        cmd += ["--load-settings", f"{m};{p}", "--load-filaments", f]
    cmd += inputs
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    path = os.path.join(out_dir, out_name)
    if r.returncode != 0 or not os.path.exists(path):
        raise RuntimeError(f"slice failed ({r.returncode}): {(r.stdout or '')[-1500:]}{(r.stderr or '')[-800:]}")
    return path


def object_names(z):
    """物体の並び（layer_config_ranges.xml の object id は、この並びの 1 始まりの番号）と名前。

    model_settings.config に書かれる順は切るたびに変わる（並べ替えの結果）。スライサーが数えるのは
    3D/3dmodel.model の物体 id の小さい順なので、id で並べ直す（2026-10-10、順を取り違えて
    PLA では蓋、PETG では箱にしか層の厚みが効かなかった）。"""
    cfg = z.read("Metadata/model_settings.config").decode("utf-8")
    objs = re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]+)"', cfg)
    return sorted(((int(i), n) for i, n in objs), key=lambda t: t[0])


def add_ranges(src, dst, names):
    """Metadata/layer_config_ranges.xml（Bambu の高さ範囲の設定）を足した 3mf を作る。"""
    xml = ['<?xml version="1.0" encoding="utf-8"?>\n<objects>\n']
    for idx, name in enumerate(names, start=1):
        key = next((k for k in RANGES if name.endswith(f"-{k}") or name.endswith(f"-{k}.stl")), None)
        if not key:
            continue
        xml.append(f' <object id="{idx}">\n')
        for z0, z1, lh in RANGES[key]:
            xml.append(f'  <range min_z="{z0}" max_z="{z1}">\n   <option opt_key="extruder">0</option>\n'
                       f'   <option opt_key="layer_height">{lh}</option>\n  </range>\n')
        xml.append(' </object>\n')
    xml.append('</objects>\n')
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename.endswith(".gcode") or item.filename.endswith(".gcode.md5") or \
                    item.filename == "Metadata/layer_config_ranges.xml":
                continue
            zout.writestr(item, zin.read(item.filename))
        zout.writestr("Metadata/layer_config_ranges.xml", "".join(xml))


def check(path3mf, names):
    """切った結果を物体ごとに確かめる。"""
    z = zipfile.ZipFile(path3mf)
    si = z.read("Metadata/slice_info.config").decode("utf-8")
    gname = [n for n in z.namelist() if n.endswith(".gcode")][0]
    tmp = os.path.join(tempfile.mkdtemp(prefix="plate_"), "plate.gcode")
    with open(tmp, "wb") as fh:
        fh.write(z.read(gname))
    layers, stats = parse_gcode(tmp)
    # 物体 id（ラベル）→ 名前。slice_info の object 行の並びと model_settings の並びは同じ
    labels = re.findall(r'<object identify_id="(\d+)" name="([^"]+)"', si)
    label_name = {int(i): n for i, n in labels}
    per = {}
    for L in layers:
        for s in L["segs"]:
            per.setdefault(s[5], []).append(s)
    out = dict(support_used=re.search(r'key="support_used" value="(\w+)"', si).group(1),
               prediction_s=int(re.search(r'key="prediction" value="(\d+)"', si).group(1)),
               weight_g=re.search(r'key="weight" value="([\d.]*)"', si).group(1),
               filament=re.findall(r'<filament [^>]*used_m="([\d.]+)" used_g="([\d.]+)"', si),
               stats=stats, objects={})
    for oid, segs in per.items():
        name = label_name.get(oid, str(oid))
        zs = sorted({round(s[6], 3) for s in segs})
        steps = {}
        for a, b in zip(zs[:-1], zs[1:]):
            steps.setdefault(round(b - a, 2), []).append(a)
        # 物体だけの層に組み直して支えの判定
        by_z = {}
        for s in segs:
            by_z.setdefault(round(s[6], 3), []).append(s)
        obj_layers = [dict(z=zz, segs=by_z[zz]) for zz in sorted(by_z)]
        tot, rows, feats = floating_report(obj_layers)
        out["objects"][name] = dict(
            layers=len(zs), z_top=zs[-1] if zs else None,
            layer_steps={str(k): [round(min(v), 2), round(max(v), 2), len(v)] for k, v in sorted(steps.items())},
            floating=tot, overhang_walls=[r for r in rows if r["feature"] != "Bridge"][:6])
    return out


def build(material, parts, out_name, ranges=True):
    os.makedirs(WORK, exist_ok=True)
    inputs = []
    for p in parts:
        tris = read_stl(os.path.join(EXPORTS, f"servo-lid-cube-{p}.stl"))
        if p in ROTATE_Z:
            tris = rotated(tris, ROTATE_Z[p])
        path = os.path.join(WORK, f"servo-lid-cube-{p}.stl")
        write_stl(path, tris)
        inputs.append(path)
    d1 = os.path.join(WORK, f"{out_name}_1")
    first = slice_cli(inputs, d1, "first.3mf", material=material)
    names = [n for _, n in object_names(zipfile.ZipFile(first))]
    final_dir = os.path.join(WORK, f"{out_name}_2")
    os.makedirs(final_dir, exist_ok=True)
    if ranges:
        mod = os.path.join(final_dir, "with_ranges.3mf")
        add_ranges(first, mod, names)
        final = slice_cli([mod], final_dir, "final.3mf", arrange=False)
    else:
        final = first
    dst = os.path.join(EXPORTS, f"{out_name}.gcode.3mf")
    shutil.copyfile(final, dst)
    res = check(final, names)
    res["file"] = dst
    res["object_order"] = names
    return res


def main():
    report = {"settings": dict(machine=print_profile.MACHINE, process=print_profile.PROCESS,
                               overrides=print_profile.OVERRIDES, ranges=RANGES)}
    for material in ("PLA", "PETG"):
        r = build(material, PARTS, f"servo-lid-cube-{material}")
        report[material] = r
        print(f"\n== {material}: {r['file']}")
        print(f"   support_used={r['support_used']} 予測 {r['prediction_s'] / 3600:.2f} h  filament {r['filament']}")
        for name, o in r["objects"].items():
            print(f"   {name}: layers {o['layers']} top {o['z_top']} steps {o['layer_steps']}")
            print(f"      floating {o['floating']}  overhang walls {o['overhang_walls'][:3]}")
    r = build("PLA", ["crank"], "servo-lid-cube-crank-test-PLA", ranges=False)
    report["crank_test"] = r
    print(f"\n== crank test: {r['file']} support_used={r['support_used']} 予測 {r['prediction_s'] / 60:.1f} min")
    with open(os.path.join(HERE, "build", "plate_report.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
