"""全部品（shaft_clip は廃止。部品表は build/manifest.json）を Bambu Lab H2D の 1 枚のプレートに刷る向きで並べ、配置だけの 3mf を書く（スライスしない）。

    py -3.11 models/tangible-pixel-cube/plate_h2d.py

入力は prints/tangible-pixel-cube/parts/<id>.stl（刷る向き、底面 z=0。print_deliver.py が書く）。
Studio の「印刷プレート」は exports の STL 名を参照するので、exports/tangible-pixel-cube-print-<id>.stl へ写してから並べる。
出力: exports/tangible-pixel-cube-h2d-layout.3mf と prints/tangible-pixel-cube/tangible-pixel-cube-h2d-layout.3mf

汎用の棚づめ（tools/plate_3mf.py）は 280 x 347mm になり入らなかった。大物 3 枚（外装・ベゼル・案内板）を左の列に縦に積み、
残りを右の領域に種類ごとの棚で並べる。
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import plate_3mf as P3  # noqa: E402

BED_X, BED_Y, BED_Z = P3.BEDS["h2d"]["size"]   # 300 x 320 x 325（2 ノズル時の範囲で見る）
MARGIN = 5.0     # プレートの縁からの余白
GAP = 4.0        # 部品どうしの間隔
NAME = "tangible-pixel-cube-h2d-layout"
PARTS_DIR = os.path.join(ROOT, "prints", "tangible-pixel-cube", "parts")
PREFIX = "tangible-pixel-cube-print-"

LEFT = ["housing", "bezel", "guide_plate", "phase_comb"]
ROTATE_Z90 = {"phase_comb"}   # 13.2 x 86 の治具を Z まわりに 90° 回し、左の列の下に置く
# 右の領域に並べる順（棚ごと）。同じ種類を同じ棚にまとめる
RIGHT_GROUPS = [
    ["shaft_0", "shaft_1", "shaft_2", "shaft_3", "shaft_4"],
    [f"pixel_{i}_{j}" for j in range(5) for i in range(5)],
    [f"cam_{i}_{j}" for j in range(5) for i in range(5)],
    ["horn_coupler", "gear_0", "gear_1", "gear_2", "gear_3", "gear_4"],
    ["servo_clip_0", "servo_clip_1"],
]


def load(part_id):
    src = os.path.join(PARTS_DIR, part_id + ".stl")
    dst = os.path.join(P3.EXPORTS, PREFIX + part_id + ".stl")
    shutil.copyfile(src, dst)
    v, t = P3.read_stl(dst)
    if part_id in ROTATE_Z90:
        v = [(-y, x, z) for x, y, z in v]   # Z まわりの回転だけなので刷る向き（底面 z=0）は変わらない
    lo, hi = P3.bbox(v)
    return {"name": PREFIX + part_id, "v": v, "t": t, "lo": lo, "w": hi[0] - lo[0], "d": hi[1] - lo[1], "h": hi[2] - lo[2]}


def changed_since(rev):
    """rev（刷った版のコミット）から prints/.../parts の STL が変わった部品 id。消えた部品は含めない"""
    import subprocess
    ids = set()
    for name in os.listdir(PARTS_DIR):
        if not name.endswith(".stl"):
            continue
        rel = f"prints/tangible-pixel-cube/parts/{name}"
        old = subprocess.run(["git", "rev-parse", f"{rev}:{rel}"], cwd=ROOT, capture_output=True, text=True)
        new = subprocess.run(["git", "hash-object", rel], cwd=ROOT, capture_output=True, text=True, check=True)
        if old.returncode != 0 or old.stdout.strip() != new.stdout.strip():
            ids.add(os.path.splitext(name)[0])
    return ids


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    global LEFT, RIGHT_GROUPS, NAME
    reprint = None
    if len(sys.argv) > 2 and sys.argv[1] == "--reprint-since":
        # 刷り直しだけのプレート: 指定したコミットから形が変わった部品だけを並べる（Studio の表示は全部品の版のまま）
        reprint = changed_since(sys.argv[2])
        LEFT = [p for p in LEFT if p in reprint]
        RIGHT_GROUPS = [[p for p in g if p in reprint] for g in RIGHT_GROUPS]
        NAME = "tangible-pixel-cube-h2d-reprint"
        print(f"[h2d] {sys.argv[2]} から変わった部品 {len(reprint)} 個: {' '.join(sorted(reprint))}")
    every = set(LEFT) | {p for g in RIGHT_GROUPS for p in g}
    on_disk = {os.path.splitext(f)[0] for f in os.listdir(PARTS_DIR) if f.endswith(".stl")}
    if reprint is None and every != on_disk:
        raise SystemExit(f"部品の過不足: 足りない {sorted(on_disk - every)} / 余分 {sorted(every - on_disk)}")
    if reprint is not None and every != reprint:
        raise SystemExit(f"並びに無い部品: {sorted(reprint - every)}")

    placed = []
    # 左の列: 大物を縦に積む
    y = MARGIN
    left_w = 0.0
    for pid in LEFT:
        p = load(pid)
        placed.append((p["name"], p["v"], p["t"], MARGIN - p["lo"][0], y - p["lo"][1]))
        y += p["d"] + GAP
        left_w = max(left_w, p["w"])

    # 右の領域: 種類ごとの棚
    x0 = MARGIN + left_w + GAP
    x_max = BED_X - MARGIN
    y = MARGIN
    for group in RIGHT_GROUPS:
        if not group:
            continue
        x, shelf = x0, 0.0
        for pid in group:
            p = load(pid)
            if x > x0 and x + p["w"] > x_max:
                x, y, shelf = x0, y + shelf + GAP, 0.0
            placed.append((p["name"], p["v"], p["t"], x - p["lo"][0], y - p["lo"][1]))
            x += p["w"] + GAP
            shelf = max(shelf, p["d"])
        y += shelf + GAP

    # 検査: 枠どうしの重なり・はみ出し・高さ（棚づめの結果を信用しない）
    boxes = []
    for name, v, _, dx, dy in placed:
        lo, hi = P3.bbox(v)
        boxes.append((name, lo[0] + dx, lo[1] + dy, hi[0] + dx, hi[1] + dy, hi[2]))
    overlaps = [(a[0], b[0]) for i, a in enumerate(boxes) for b in boxes[i + 1:]
                if min(a[3], b[3]) - max(a[1], b[1]) > -GAP + 1e-6 and min(a[4], b[4]) - max(a[2], b[2]) > -GAP + 1e-6]
    off_bed = [b[0] for b in boxes if b[1] < MARGIN - 1e-6 or b[2] < MARGIN - 1e-6
               or b[3] > BED_X - MARGIN + 1e-6 or b[4] > BED_Y - MARGIN + 1e-6]
    tall = [b[0] for b in boxes if b[5] > BED_Z]
    used = (max(b[3] for b in boxes), max(b[4] for b in boxes))
    print(f"[h2d] {len(placed)} 部品 / 使う範囲 {used[0]:.1f} x {used[1]:.1f}mm（プレート {BED_X:.0f} x {BED_Y:.0f}、余白 {MARGIN:g}）")
    print(f"[h2d] 間隔 {GAP:g}mm 未満の組 {overlaps if overlaps else 'なし'} / はみ出し {off_bed if off_bed else 'なし'} / "
          f"高さ超え {tall if tall else 'なし'} / 最大高さ {max(b[5] for b in boxes):.1f}mm")
    if overlaps or off_bed or tall or len(placed) != len(every):
        raise SystemExit("[h2d] プレートに入らない")

    out = os.path.join(P3.EXPORTS, NAME + ".3mf")
    P3.write_3mf(out, placed)
    shutil.copyfile(out, os.path.join(ROOT, "prints", "tangible-pixel-cube", NAME + ".3mf"))
    print(f"[h2d] {out}（{os.path.getsize(out):,} バイト）")

    if reprint is not None:
        return
    # Studio の「印刷プレート」に載せる（viewer/studio/plates/tangible-pixel-cube.json と配置済みの STL）
    import studio_plate  # noqa: E402
    manifest = studio_plate.export_studio_plate("tangible-pixel-cube", out, bed=(BED_X, BED_Y))
    print(f"[h2d] Studio の印刷プレート: {len(manifest['parts'])} 部品 / {manifest['id'][:12]}")


if __name__ == "__main__":
    main()
