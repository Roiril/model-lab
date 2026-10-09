"""Bambu Studio（CLI）で部品ごとにスライスし、G-code から「下の層に支えの無い押し出し」を数える。

    py -3.11 models/servo-lid-cube/slice_check.py

設定は Bambu Studio 同梱の標準プロファイル（X1C 0.4 / 0.20mm Standard / サポート無し）。
材料は PLA と PETG の 2 通り。出力: build/slice_report.json と build/slices/<材料>_<部品>.gcode
判定: 押し出しの各点について、1 つ下の層の押し出しが水平距離 R 以内にあれば「支えあり」。
ブリッジ（; FEATURE: Bridge）は両端で支えられる前提の機能なので別に数える。
計器の校正: 浮いた板（必ず検出）と 45° の斜面（検出されない）を同じ手順で通す。
"""
import json
import math
import os
import re
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EXPORTS = os.path.join(ROOT, "exports")
OUT = os.path.join(HERE, "build", "slices")
sys.stdout.reconfigure(encoding="utf-8")

EXE = r"C:\Program Files\Bambu Studio\bambu-studio.exe"
PROF = r"C:\Program Files\Bambu Studio\resources\profiles\BBL"
MACHINE = os.path.join(PROF, "machine", "Bambu Lab X1 Carbon 0.4 nozzle.json")
PROCESS = os.path.join(PROF, "process", "0.20mm Standard @BBL X1C.json")
FILAMENTS = {
    "PLA": os.path.join(PROF, "filament", "Bambu PLA Basic @BBL X1C.json"),
    "PETG": os.path.join(PROF, "filament", "Bambu PETG Basic @BBL X1C.json"),
}
PARTS = ["box", "lid", "crank", "link", "pin", "clip"]
R_SUP = 0.6      # 下の層の押し出しがこの水平距離にあれば支えあり（mm）。45° なら 1 層 0.2mm のずれ
CELL = 0.2


def slice_one(stl, material, tag):
    os.makedirs(OUT, exist_ok=True)
    work = tempfile.mkdtemp(prefix="slc_")
    cmd = [EXE, "--slice", "0", "--debug", "3", "--load-settings", f"{MACHINE};{PROCESS}",
           "--load-filaments", FILAMENTS[material], "--outputdir", work, "--export-3mf", f"{tag}.3mf", stl]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (r.stdout or "") + (r.stderr or "")
    gpath = os.path.join(work, "plate_1.gcode")
    if r.returncode != 0 or not os.path.exists(gpath):
        return None, log
    dst = os.path.join(OUT, f"{tag}.gcode")
    os.replace(gpath, dst)
    return dst, log


def parse_gcode(path):
    """層ごとの押し出し線分 [(x0,y0,x1,y1,feature)] と統計。"""
    layers = []
    cur = None
    x = y = z = 0.0
    feature = ""
    stats = {}
    rel_e = True
    for line in open(path, encoding="utf-8", errors="replace"):
        if line.startswith(";"):
            if line.startswith("; CHANGE_LAYER"):
                cur = dict(z=None, segs=[])
                layers.append(cur)
            elif line.startswith("; Z_HEIGHT:") and cur is not None:
                cur["z"] = float(line.split(":")[1])
            elif line.startswith("; FEATURE:"):
                feature = line.split(":", 1)[1].strip()
            elif "model printing time" in line or "total estimated time" in line:
                stats["time"] = line.strip("; \n")
            elif line.startswith("; total filament length"):
                stats["filament_mm"] = float(line.split(":")[1])
            elif line.startswith("; total filament weight"):
                stats["filament_g_header"] = line.split(":")[1].strip()
            continue
        if line.startswith("M83"):
            rel_e = True
        if line.startswith("M82"):
            rel_e = False
        if not (line.startswith("G1 ") or line.startswith("G0 ") or line.startswith("G2 ") or line.startswith("G3 ")):
            continue
        m = dict(re.findall(r"([XYZE])(-?[\d.]+)", line.split(";")[0]))
        nx = float(m.get("X", x))
        ny = float(m.get("Y", y))
        if "Z" in m:
            z = float(m["Z"])
        e = float(m.get("E", 0.0))
        if cur is not None and e > 0 and (line.startswith("G1") or line.startswith("G2") or line.startswith("G3")) \
                and (nx != x or ny != y):
            cur["segs"].append((x, y, nx, ny, feature))
        x, y = nx, ny
    return layers, stats


def coverage(segs):
    cells = set()
    for x0, y0, x1, y1, _ in segs:
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / (CELL * 0.7)))
        for i in range(n + 1):
            px = x0 + (x1 - x0) * i / n
            py = y0 + (y1 - y0) * i / n
            cells.add((int(math.floor(px / CELL)), int(math.floor(py / CELL))))
    return cells


def supported(cells, px, py):
    k = int(math.ceil(R_SUP / CELL))
    cx, cy = int(math.floor(px / CELL)), int(math.floor(py / CELL))
    for dx in range(-k, k + 1):
        for dy in range(-k, k + 1):
            if dx * dx + dy * dy <= k * k and (cx + dx, cy + dy) in cells:
                return True
    return False


INTERNAL = ("Sparse infill", "Internal solid infill", "Floating vertical shell", "Internal Bridge")


def floating_report(layers):
    """支えの無い押し出しを、外に見える機能（壁・ブリッジ）と中の詰め物に分けて数え、場所を返す。

    座標は押し出し全体の外接箱の中心からの相対（部品の XY にほぼ一致）。"""
    xs = [v for L in layers for s in L["segs"] for v in (s[0], s[2])]
    ys = [v for L in layers for s in L["segs"] for v in (s[1], s[3])]
    cx = (min(xs) + max(xs)) / 2 if xs else 0.0
    cy = (min(ys) + max(ys)) / 2 if ys else 0.0
    rows = []
    prev = None
    total = dict(external_unsupported_mm=0.0, bridge_mm=0.0, bridge_unsupported_mm=0.0, internal_unsupported_mm=0.0)
    by_feature = {}
    for li, L in enumerate(layers):
        if not L["segs"]:
            continue
        if prev is None:
            prev = coverage(L["segs"])
            continue
        found = {}
        for x0, y0, x1, y1, feat in L["segs"]:
            length = math.hypot(x1 - x0, y1 - y0)
            n = max(1, int(length / 0.2))
            bad = []
            for i in range(n + 1):
                px = x0 + (x1 - x0) * i / n
                py = y0 + (y1 - y0) * i / n
                if not supported(prev, px, py):
                    bad.append((px - cx, py - cy))
            seg_un = length * len(bad) / (n + 1)
            if any(k in feat for k in INTERNAL):
                total["internal_unsupported_mm"] += seg_un
                continue
            if "Bridge" in feat:
                total["bridge_mm"] += length
                total["bridge_unsupported_mm"] += seg_un
            else:
                total["external_unsupported_mm"] += seg_un
            by_feature[feat] = by_feature.get(feat, 0.0) + seg_un
            if bad:
                found.setdefault(feat, []).extend(bad)
        for feat, pts in found.items():
            if len(pts) < 3:
                continue
            rows.append(dict(layer=li, z=L["z"], feature=feat, points=len(pts),
                             x=[round(min(p[0] for p in pts), 1), round(max(p[0] for p in pts), 1)],
                             y=[round(min(p[1] for p in pts), 1), round(max(p[1] for p in pts), 1)]))
        prev = coverage(L["segs"])
    total = {k: round(v, 2) for k, v in total.items()}
    return total, rows, {k: round(v, 2) for k, v in by_feature.items() if v > 0.05}


def write_stl(path, tris):
    with open(path, "wb") as fh:
        fh.write(b"\0" * 80 + struct.pack("<I", len(tris)))
        for t in tris:
            fh.write(struct.pack("<12fH", 0, 0, 0, *t[0], *t[1], *t[2], 0))


def box_tris(x0, x1, y0, y1, z0, z1):
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    f = [(0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6), (0, 1, 5), (0, 5, 4), (2, 6, 7), (2, 7, 3),
         (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5)]
    return [(v[a], v[b], v[c]) for a, b, c in f]


def calibration():
    """校正: (1) 柱の上に横へ 10mm 張り出した板（必ず浮く） (2) 45° の斜面（浮かない）。"""
    tmp = tempfile.mkdtemp(prefix="cal_")
    a = os.path.join(tmp, "cal_overhang.stl")
    # Γ 形（柱の上の板が横へ 10mm 張り出す）を 1 つの閉じたメッシュで
    poly = [(0, 0), (10, 0), (10, 10), (20, 10), (20, 12), (0, 12)]
    tri = [(0, 1, 2), (0, 2, 5), (2, 3, 4), (2, 4, 5)]
    v0 = [(x, 0.0, z) for x, z in poly]
    v1 = [(x, 10.0, z) for x, z in poly]
    tris = [(v0[c], v0[b], v0[a]) for a, b, c in tri] + [(v1[a], v1[b], v1[c]) for a, b, c in tri]
    for i in range(6):
        j = (i + 1) % 6
        tris += [(v0[i], v0[j], v1[j]), (v0[i], v1[j], v1[i])]
    write_stl(a, tris)
    b = os.path.join(tmp, "cal_slope.stl")
    # 45° に傾いた板: 底 0..10、上へ行くほど +X に 1:1 でずれる 20mm 高
    v = [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0), (20, 0, 20), (30, 0, 20), (30, 10, 20), (20, 10, 20)]
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
         (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    write_stl(b, [(v[i], v[j], v[k]) for i, j, k in f])
    res = {}
    for name, path in (("overhang_10mm", a), ("slope_45", b)):
        g, log = slice_one(path, "PLA", f"cal_{name}")
        if g is None:
            res[name] = dict(error=log[-500:])
            continue
        layers, _ = parse_gcode(g)
        tot, rows, feats = floating_report(layers)
        res[name] = dict(total=tot, features=feats)
    ov = res.get("overhang_10mm", {}).get("total", {})
    sl = res.get("slope_45", {}).get("total", {})
    # 「Bridge」は中の詰め物の上に張る橋渡しにも付くので判定に使わない。外に見える壁（Overhang wall 等）で見る
    ok = ov.get("external_unsupported_mm", 0) > 20 and sl.get("external_unsupported_mm", 99) < 1.0
    res["ok"] = ok
    return res


def main():
    report = dict(settings=dict(machine=os.path.basename(MACHINE), process=os.path.basename(PROCESS),
                                support="off（標準プロファイルのまま enable_support=0）", R_support_mm=R_SUP))
    report["calibration"] = calibration()
    print("calibration", json.dumps(report["calibration"], ensure_ascii=False))
    report["parts"] = {}
    for mat in FILAMENTS:
        for p in PARTS:
            stl = os.path.join(EXPORTS, f"servo-lid-cube-{p}.stl")
            g, log = slice_one(stl, mat, f"{mat}_{p}")
            warn = [l.strip() for l in log.splitlines()
                    if re.search(r"float|cantilever|overhang|empty layer|error|support", l, re.I)
                    and not re.search(r"\[trace\]|\[debug\]", l)][:8]
            if g is None:
                report["parts"][f"{mat}/{p}"] = dict(error=log[-800:])
                print(mat, p, "slice failed")
                continue
            layers, stats = parse_gcode(g)
            tot, rows, feats = floating_report(layers)
            report["parts"][f"{mat}/{p}"] = dict(layers=len(layers), stats=stats, floating=tot,
                                                  floating_by_feature=feats, worst_layers=rows[:6],
                                                  log_warnings=warn)
            print(mat, p, len(layers), stats.get("time"), tot, feats)
            for r in rows[:10]:
                print("    ", r)
    with open(os.path.join(HERE, "build", "slice_report.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)


main()
