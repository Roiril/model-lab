"""laser-bot を SVG(カット赤ヘアライン / 彫刻黒) に展開して exports/laser/ に出力。

各パネルに異なる表情を彫刻（face-sheet.png から輪郭抽出した黒シェイプ）。
彫刻＝フロストなので、色付き/濃色アクリルで「光る顔」として再現される。

実行: python models/laser-bot/build.py
（bpy 不要のプレーン Python。Blender は使わない）
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import laser_core as lc
import face_extract as fe
from params import W, D, H, GAP

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "exports", "laser")
os.makedirs(OUT_DIR, exist_ok=True)

# 各パネル → 使う表情 (row, col)（ユーザー指定: 下段1,3,5 / 上段2,4,6）
FACE_MAP = {
    "front":  (1, 3),   # まんまる目＋笑み（正面はこれ）
    "back":   (1, 5),   # まんまる目
    "left":   (0, 2),   # 縦長オーバル目
    "right":  (0, 6),   # 斜めリーフ目
    "top":    (0, 4),   # オーバル目＋波口
    "bottom": (1, 1),   # 半月目
}

INSET = 8.0     # パネル端からの彫刻安全マージン mm（フィンガー溝を避ける）
FILL = 0.92     # 安全域に対する顔の充填率


def panel_face_items(name, A, B):
    """パネル(A x B)ローカル座標に配置した顔の彫刻アイテム群を返す。
    返り: [subpaths, ...]（subpaths = ループのリスト, evenodd で穴）"""
    norm = fe.extract_face(*FACE_MAP[name])
    allpts = np.vstack([lp for pls in norm for lp in pls])
    cw = allpts[:, 0].max() - allpts[:, 0].min()
    ch = allpts[:, 1].max() - allpts[:, 1].min()
    aw, ah = A - 2 * INSET, B - 2 * INSET
    scale = min(aw / cw, ah / ch) * FILL
    cx, cy = A / 2.0, B / 2.0
    items = []
    for pls in norm:
        sub = []
        for lp in pls:
            pts = [(cx + x * scale, cy + y * scale) for x, y in lp]
            sub.append(pts)
        items.append(sub)
    return items


def compose():
    """6面＋各面の顔をシートに配置して (cut_loops, engrave_loops, panels) を返す。"""
    panels = lc.box_panels(W, D, H)
    # シート内レイアウト（3列 x 2行）
    order = [["front", "back", "right"], ["top", "bottom", "left"]]
    cut_loops = []
    engrave_loops = []
    y_cursor = 0.0
    for row in order:
        x_cursor = 0.0
        row_h = max(panels[n][1][1] for n in row)
        for name in row:
            loop, (A, B) = panels[name]
            dx, dy = x_cursor, y_cursor
            cut_loops.append((loop, dx, dy))
            for sub in panel_face_items(name, A, B):
                engrave_loops.append((sub, dx, dy))
            x_cursor += A + GAP
        y_cursor += row_h + GAP
    return cut_loops, engrave_loops, panels


def main():
    cut_loops, engrave_loops, panels = compose()
    svg_path = os.path.join(OUT_DIR, "laser-bot.svg")
    sheet = lc.write_svg(svg_path, cut_loops, engrave_loops)

    print(f"box outer (mm)   : {W} x {D} x {H}  (W x D x H)")
    print(f"material         : t={lc.MAT_T}mm  kerf={lc.KERF}mm")
    print("panels (faces)   :")
    for name, (_, (A, B)) in panels.items():
        print(f"  {name:7s}: {A:.1f} x {B:.1f}  face={FACE_MAP[name]}")
    print(f"sheet bbox (mm)  : {sheet[0]:.1f} x {sheet[1]:.1f}  (bed {lc.BED_W} x {lc.BED_H})")
    fit = "OK" if sheet[0] <= lc.BED_W and sheet[1] <= lc.BED_H else "OVER BED!"
    print(f"fit              : {fit}")
    print(f"wrote            : {svg_path}")


if __name__ == "__main__":
    main()
