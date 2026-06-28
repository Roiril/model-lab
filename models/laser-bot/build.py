"""laser-bot を SVG(カット赤ヘアライン / 彫刻黒) に展開して exports/laser/ に出力。

実行: python models/laser-bot/build.py
（bpy 不要のプレーン Python。Blender は使わない）
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import laser_core as lc
from params import (W, D, H, EYE_R, EYE_Y, EYE_DX, MOUTH_W, MOUTH_TH,
                    MOUTH_DIP, MOUTH_Y, CHEEK_R, CHEEK_Y, CHEEK_DX, GAP)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "exports", "laser")
os.makedirs(OUT_DIR, exist_ok=True)


def smile(cx, cy, w, th, dip, seg=40):
    """笑み口の帯（閉ループ）。SVG 系 y 下向き＝中央が下に膨らむ。"""
    top, bot = [], []
    for i in range(seg + 1):
        t = i / seg
        x = cx - w / 2 + w * t
        ymid = cy + dip * math.sin(math.pi * t)
        top.append((x, ymid - th / 2))
        bot.append((x, ymid + th / 2))
    return top + bot[::-1]


def face_engrave():
    """front パネル(W x H, ローカル原点左上 y 下)上の顔パーツ群を返す。"""
    loops = []
    ey = EYE_Y * H
    # 目
    loops.append(lc.circle(W * (0.5 - EYE_DX), ey, EYE_R))
    loops.append(lc.circle(W * (0.5 + EYE_DX), ey, EYE_R))
    # ほっぺ
    cy = CHEEK_Y * H
    loops.append(lc.circle(W * (0.5 - CHEEK_DX), cy, CHEEK_R))
    loops.append(lc.circle(W * (0.5 + CHEEK_DX), cy, CHEEK_R))
    # 口（笑み）
    loops.append(smile(W * 0.5, MOUTH_Y * H, MOUTH_W, MOUTH_TH, MOUTH_DIP))
    return loops


def main():
    panels = lc.box_panels(W, D, H)

    # シート内レイアウト（3列 x 2行）
    #  row0: front  back   right
    #  row1: top    bottom left
    order = [["front", "back", "right"], ["top", "bottom", "left"]]
    col_w = max(panels[n][1][0] for row in order for n in row)
    cut_loops = []
    engrave_loops = []
    # 列幅・行高はパネルごとに違うのでカーソルで積む
    y_cursor = 0.0
    for row in order:
        x_cursor = 0.0
        row_h = max(panels[n][1][1] for n in row)
        for name in row:
            loop, (A, B) = panels[name]
            dx, dy = x_cursor, y_cursor
            cut_loops.append((loop, dx, dy))
            if name == "front":
                for fl in face_engrave():
                    engrave_loops.append((fl, dx, dy))
            x_cursor += A + GAP
        y_cursor += row_h + GAP

    svg_path = os.path.join(OUT_DIR, "laser-bot.svg")
    sheet = lc.write_svg(svg_path, cut_loops, engrave_loops)

    # --- 報告 ---
    print(f"box outer (mm)   : {W} x {D} x {H}  (W x D x H)")
    print(f"material         : t={lc.MAT_T}mm  kerf={lc.KERF}mm")
    print("panels (W x H mm):")
    for name, (_, (A, B)) in panels.items():
        print(f"  {name:7s}: {A:.1f} x {B:.1f}  fingers {lc.finger_count(A)}/{lc.finger_count(B)}")
    print(f"sheet bbox (mm)  : {sheet[0]:.1f} x {sheet[1]:.1f}"
          f"  (bed {lc.BED_W} x {lc.BED_H})")
    fit = "OK" if sheet[0] <= lc.BED_W and sheet[1] <= lc.BED_H else "OVER BED!"
    print(f"fit              : {fit}")
    print(f"wrote            : {svg_path}")


if __name__ == "__main__":
    main()
