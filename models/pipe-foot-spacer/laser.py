"""芯間合わせ板のレーザーカット版を書き出す。

出力:
    exports/laser/pipe-foot-spacer.svg   Ruby へ読ませる本番データ（赤ヘアライン＝カット）
    exports/laser/pipe-foot-spacer.dxf   SVG が読めなかったときの予備
    exports/laser/kit-foot-spacer/       持ち出し一式（svg / pdf / preview.png / 手順）

実行: py -3.10 models/pipe-foot-spacer/laser.py
      （pdf と preview.png に matplotlib を使う。3.11 には入っていない）
"""
import sys, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.path.insert(0, HERE)

import laser_core as lc
import make_vector as mv
from laser_params import (
    SPAN, HOLE_D, PLATE_W, PLATE_L, PLATE_T, CORNER_R,
    SHEET_T, KERF, LAYERS, STACK_T,
    PIN_N, PIN_SPARE, PIN_X, PIN_Y, PIN_FIT, PIN_SLOP, PIN_TIGHT, PIN_LEN,
    GAP, MARGIN,
)

LASER_DIR = os.path.join(ROOT, "exports", "laser")
KIT = os.path.join(LASER_DIR, "kit-foot-spacer")
SEG = 96
CORNER_SEG = 16

# ============================================================
#  カーフ補正
# ============================================================
# 切り線の両側が KERF/2 ずつ溶ける。
#   外周・角棒（材料が残る側が内側）→ 線を外へ KERF/2 ふくらませる…のではなく、
#                                    仕上がりを公称にするため線を内へ寄せる
#   穴（材料が残る側が外側）        → 線を内へ寄せる＝径を KERF 小さく描く
HALF = KERF / 2.0


def rounded_rect(hl, hw, r, seg=CORNER_SEG):
    """原点中心・長辺 2*hl・短辺 2*hw・角丸 r の反時計回りポリゴン。"""
    pts = []
    for cx, cy, a0 in ((hl - r, hw - r, 0.0), (-(hl - r), hw - r, math.pi / 2),
                       (-(hl - r), -(hw - r), math.pi), (hl - r, -(hw - r), 1.5 * math.pi)):
        for i in range(seg + 1):
            a = a0 + math.pi / 2 * i / seg
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def circle(cx, cy, r, seg=SEG):
    return [(cx + r * math.cos(2 * math.pi * i / seg),
             cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


def rect(cx, cy, w, h):
    hw, hh = w / 2.0, h / 2.0
    return [(cx - hw, cy - hh), (cx + hw, cy - hh), (cx + hw, cy + hh), (cx - hw, cy + hh)]


# ---- 描く寸法（カーフ補正後）----
OUT_HL = PLATE_L / 2 - HALF
OUT_HW = PLATE_W / 2 - HALF
OUT_R = CORNER_R - HALF
HOLE_R_CUT = (HOLE_D - KERF) / 2.0             # 仕上がり Φ37.1
PIN_HOLE_TIGHT = PIN_TIGHT + PIN_FIT - KERF    # 3.00 描き → 3.10 仕上がり
PIN_HOLE_LOOSE = SHEET_T + PIN_SLOP - KERF     # 3.50 描き → 3.60 仕上がり
PIN_CUT_W = PIN_TIGHT + KERF                   # 3.10 描き → 3.00 仕上がり
PIN_CUT_L = PIN_LEN + KERF                     # 8.70 描き → 8.60 仕上がり


def plate_loops():
    """板 1 枚ぶんのカット閉ループ（原点中心）。外周 → 大穴 → 角棒の受け穴。"""
    loops = [rounded_rect(OUT_HL, OUT_HW, OUT_R)]
    for s in (+1, -1):
        loops.append(circle(s * SPAN / 2, 0.0, HOLE_R_CUT))
    for sx in (+1, -1):
        # 上段: X を詰めて Y を逃がす / 下段: Y を詰めて X を逃がす
        loops.append(rect(sx * PIN_X, +PIN_Y, PIN_HOLE_TIGHT, PIN_HOLE_LOOSE))
        loops.append(rect(sx * PIN_X, -PIN_Y, PIN_HOLE_LOOSE, PIN_HOLE_TIGHT))
    return loops


def compose():
    """[(loop, dx, dy)] の板取りを返す。原点は左上（SVG と同じ y 下向き）。"""
    cut = []
    row_h = PLATE_W + GAP
    for i in range(LAYERS):
        cx, cy = PLATE_L / 2, PLATE_W / 2 + i * row_h
        for lp in plate_loops():
            cut.append((lp, cx, cy))
    # 角棒は板の下に一列
    n = PIN_N + PIN_SPARE
    y = LAYERS * row_h + PIN_CUT_L / 2
    for i in range(n):
        x = PIN_CUT_L / 2 + i * (PIN_CUT_L + GAP)
        cut.append((rect(0, 0, PIN_CUT_L, PIN_CUT_W), x, y))
    return cut


def main():
    os.makedirs(LASER_DIR, exist_ok=True)
    cut = compose()

    svg = os.path.join(LASER_DIR, "pipe-foot-spacer.svg")
    W, H = lc.write_svg(svg, cut, margin=MARGIN)

    # DXF（予備）— make_vector は [(rings, dx, dy)] を取る
    dxf = os.path.join(LASER_DIR, "pipe-foot-spacer.dxf")
    mv.write_dxf([([lp], dx + MARGIN, dy + MARGIN) for lp, dx, dy in cut], dxf)

    print(f"sheet   : {W:.1f} x {H:.1f} mm")
    print(f"plate   : {PLATE_L} x {PLATE_W} mm x {LAYERS} 枚 = {STACK_T}mm 厚")
    print(f"hole    : Φ{HOLE_D} 仕上がり（描き Φ{HOLE_R_CUT*2:.2f}）芯間 {SPAN}")
    print(f"pin hole: {PIN_HOLE_TIGHT:.2f} x {PIN_HOLE_LOOSE:.2f} 描き "
          f"→ {PIN_HOLE_TIGHT+KERF:.2f} x {PIN_HOLE_LOOSE+KERF:.2f} 仕上がり")
    print(f"pin     : {PIN_CUT_L:.2f} x {PIN_CUT_W:.2f} 描き "
          f"→ {PIN_LEN:.2f} x {PIN_TIGHT:.2f} 仕上がり x {PIN_N+PIN_SPARE} 本")
    print("->", svg)
    print("->", dxf)
    return cut, (W, H)


if __name__ == "__main__":
    main()
