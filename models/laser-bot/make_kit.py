"""make_kit — 1209 持ち出しキットを exports/laser/kit-1209/ に一式生成。

中身: laser-bot.svg（カット用本体）/ laser-bot.pdf（1:1 ベクター, Ruby 入稿バックアップ）
      preview.png（顔つき展開プレビュー, 認識用）。手順MDは別途配置。

実行: python models/laser-bot/make_kit.py
"""
import sys, os, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

import laser_core as lc
import build  # compose() を再利用


def _subpaths(item):
    first, dx, dy = item
    if first and isinstance(first[0], (int, float)):
        return [first], dx, dy
    return first, dx, dy


def _compound_patch(subpaths, dx, dy):
    """複数ループを一つの PathPatch にして穴/島を表現。
    matplotlib は nonzero 塗りなので、穴(奇数番)を逆巻きにして穴を開ける
    （SVG 側は fill-rule:evenodd なので巻き方向に依らず正しい）。"""
    verts, codes = [], []
    for idx, lp in enumerate(subpaths):
        pts = list(lp)
        if idx % 2 == 1:           # 穴: 逆巻き
            pts = pts[::-1]
        if pts[0] != pts[-1]:
            pts = pts + [pts[0]]
        for i, (x, y) in enumerate(pts):
            verts.append((x + dx, y + dy))
            codes.append(Path.MOVETO if i == 0 else Path.LINETO)
        codes[-1] = Path.CLOSEPOLY
    return PathPatch(Path(verts, codes), fc="black", ec="none")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LASER_DIR = os.path.join(ROOT, "exports", "laser")
KIT = os.path.join(LASER_DIR, "kit-1209")
os.makedirs(KIT, exist_ok=True)
MM2IN = 1 / 25.4


def render(cut, eng, sheet, path, dpi=150, line_pdf=False):
    """1:1 でカット赤線・彫刻黒ベタを描画。line_pdf=True で PDF ベクター出力。"""
    W, H = sheet
    fig = plt.figure(figsize=(W * MM2IN, H * MM2IN))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.set_aspect("equal"); ax.axis("off")
    ax.invert_yaxis()  # SVG 系 y 下向きに合わせる
    # 彫刻（黒ベタ, 複合パスは evenodd で穴/島）
    for item in eng:
        sub, dx, dy = _subpaths(item)
        ax.add_patch(_compound_patch(sub, dx, dy))
    # カット（赤線）
    for loop, dx, dy in cut:
        ax.plot([x + dx for x, y in loop], [y + dy for x, y in loop],
                "-", color="red", lw=0.4 if line_pdf else 0.8)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def main():
    cut, eng, panels = build.compose()
    # 配置原点を margin に合わせる（write_svg と同じ +5mm マージン基準で bbox 再計算）
    all_pts = [(x + dx, y + dy) for loop, dx, dy in cut for (x, y) in loop]
    for item in eng:
        sub, dx, dy = _subpaths(item)
        all_pts += [(x + dx, y + dy) for lp in sub for (x, y) in lp]
    minx = min(p[0] for p in all_pts); miny = min(p[1] for p in all_pts)
    maxx = max(p[0] for p in all_pts); maxy = max(p[1] for p in all_pts)
    m = 5.0
    sheet = (maxx - minx + 2 * m, maxy - miny + 2 * m)
    off = (m - minx, m - miny)
    cut = [(l, dx + off[0], dy + off[1]) for l, dx, dy in cut]
    eng = [(l, dx + off[0], dy + off[1]) for l, dx, dy in eng]

    # 1) SVG（本番カット用）— build.py の出力を流用してコピー
    src_svg = os.path.join(LASER_DIR, "laser-bot.svg")
    if not os.path.exists(src_svg):
        build.main()
    shutil.copy(src_svg, os.path.join(KIT, "laser-bot.svg"))
    # 2) PDF（1:1 ベクター, 入稿バックアップ）
    render(cut, eng, sheet, os.path.join(KIT, "laser-bot.pdf"), line_pdf=True)
    # 3) preview PNG（認識用）
    render(cut, eng, sheet, os.path.join(KIT, "preview.png"), dpi=150)

    print("kit ->", KIT)
    for f in sorted(os.listdir(KIT)):
        print("  ", f)


if __name__ == "__main__":
    main()
