"""Bambu Studio（CLI）で部品ごとにスライスし、G-code から「下の層に支えの無い押し出し」を数える。

    py -3.11 models/servo-lid-cube/slice_check.py

設定は Bambu Studio 同梱の標準プロファイル（X1C 0.4 / 0.20mm Standard / サポート無し）。
材料は PLA と PETG の 2 通り。出力: build/slice_report.json と build/slices/<材料>_<部品>.gcode
判定: 押し出しの各点について、1 つ下の層の押し出しが水平距離 R 以内にあれば「支えあり」。
ブリッジ（; FEATURE: Bridge）は両端で支えられる前提の機能なので別に数える。
計器の校正: 浮いた板（必ず検出）と 45° の斜面（検出されない）を同じ手順で通す。
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EXPORTS = os.path.join(ROOT, "exports")
OUT = os.path.join(HERE, "build", "slices")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(ROOT, "lib"))

EXE = r"C:\Program Files\Bambu Studio\bambu-studio.exe"
PROF = r"C:\Program Files\Bambu Studio\resources\profiles\BBL"
sys.path.insert(0, HERE)
import print_profile  # noqa: E402
from printmech.gcode import CELL, R_SUP, floating_report, parse_gcode  # noqa: E402
from printmech.stl import box_triangles as box_tris, write_binary_stl as write_stl  # noqa: E402

# 標準プロファイルは継承を解いてから渡す（CLI は inherits をたどらない）。上書きは print_profile.py
FILAMENTS = {}
for _m in ("PLA", "PETG"):
    MACHINE, PROCESS, FILAMENTS[_m] = print_profile.settings(_m)
PARTS = ["box", "lid", "crank", "link", "pin", "clip"]


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


if __name__ == "__main__":
    main()
