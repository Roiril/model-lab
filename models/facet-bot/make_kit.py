"""make_kit — facet-bot の 1209 持ち出しキットを exports/laser/kit-facet-1209/ に生成。

実行: python models/facet-bot/make_kit.py
"""
import sys, os, shutil, base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../laser-bot"))
sys.path.insert(0, os.path.dirname(__file__))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

import laser_core as lc
import build

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LASER_DIR = os.path.join(ROOT, "exports", "laser")
KIT = os.path.join(LASER_DIR, "kit-facet-1209")
os.makedirs(KIT, exist_ok=True)
MM2IN = 1 / 25.4


def _compound(sub, dx, dy):
    verts, codes = [], []
    for idx, lp in enumerate(sub):
        pts = list(lp)
        if idx % 2 == 1:
            pts = pts[::-1]
        for i, (x, y) in enumerate(pts):
            verts.append((x + dx, y + dy))
            codes.append(Path.MOVETO if i == 0 else Path.LINETO)
        codes[-1] = Path.CLOSEPOLY
    return PathPatch(Path(verts, codes), fc="black", ec="none")


def render(cut, eng, elines, sheet, off, path, dpi=150, line_pdf=False):
    W, H = sheet
    fig = plt.figure(figsize=(W * MM2IN, H * MM2IN))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.set_aspect("equal"); ax.axis("off"); ax.invert_yaxis()
    ox, oy = off
    for sub, dx, dy in eng:
        ax.add_patch(_compound(sub, dx + ox, dy + oy))
    lw = lc.ENGRAVE_LINE_W / 25.4 * 72
    for loops, dx, dy in elines:
        for lp in loops:
            ax.plot([x + dx + ox for x, y in lp] + [lp[0][0] + dx + ox],
                    [y + dy + oy for x, y in lp] + [lp[0][1] + dy + oy],
                    "k-", lw=lw, solid_capstyle="round")
    rlw = 0.4 if line_pdf else 0.7
    for loop, dx, dy in cut:
        ax.plot([x + dx + ox for x, y in loop] + [loop[0][0] + dx + ox],
                [y + dy + oy for x, y in loop] + [loop[0][1] + dy + oy], "r-", lw=rlw)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


PROC = [
 ("A. 現地セット", ["窓を開ける（ダクト排気）","電源 ON","アクリル板(3mm・濃色推奨)を置く","ワークエリアを上げてピント合わせ","ヘッドを切りたい位置へ"]),
 ("B. Ruby", ["facet-bot.svg をD&D（ダメなら .pdf）","色割り当て → 赤=カット / 黒=彫刻","3mmアクリル用のパワー/スピード","ジョブ作成 → 再生"]),
 ("C. 組み立て（曲げない・接着）", ["部品は 平パネル9枚（前面＝顔1＋背面8）＋ D字フタ2枚","片方のフタのスロットに、前面(顔)パネルから順に各パネルのタブを差し込む","もう片方のフタを上から被せて全パネルのタブを受ける","隣り合うパネルの合わせ目＋タブをアクリル接着剤で固定","顔パネルが正面。背面は多面体で丸く見える"]),
]


def write_docs(preview_png):
    b64 = base64.b64encode(open(preview_png, "rb").read()).decode()
    md = ["# 1209 レーザーカット手順 — facet-bot（多面体のまるい子）",
          "",
          "曲げないで「丸い胴体」を作るバージョン。背面を平らなファセットに分割してあるので",
          "**アクリルで割れない**（リビングヒンジ版 curve-bot のアクリル代替）。",
          "",
          "## 中身",
          "| ファイル | 用途 |",
          "|---|---|",
          "| **facet-bot.svg** | 本番カットデータ |",
          "| facet-bot.pdf | 予備（1:1） |",
          "| preview.png | 展開図の確認用 |",
          "",
          "部品: 平パネル9枚（前面＝顔1＋背面ファセット8）＋ D字フタ2枚 ＝計11枚。",
          "**素材は3mmアクリル（濃色推奨）**。顔は彫刻＝フロストで白く光る。",
          ""]
    for title, items in PROC:
        md.append(f"### {title}")
        for it in items:
            md.append(f"- [ ] {it}")
        md.append("")
    md += ["## ⚠ 安全",
           "- 加工中は離席しない（発火注意・消火器1209）",
           "- 接着はアクリル用（溶剤系）を内側から。瞬間接着剤は白化に注意"]
    open(os.path.join(KIT, "手順.md"), "w", encoding="utf-8").write("\n".join(md))

    rows = ""
    for title, items in PROC:
        rows += f"<h2>{title}</h2><ul>" + "".join(
            f"<li><label><input type=checkbox> {it}</label></li>" for it in items) + "</ul>"
    html = f"""<!doctype html><html lang=ja><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>facet-bot 手順</title>
<style>body{{font-family:system-ui,sans-serif;max-width:680px;margin:0 auto;padding:16px;line-height:1.7;background:#fffdf7;color:#1a1a1a}}
h1{{font-size:1.35rem}}h2{{font-size:1.05rem;margin-top:1.3em;border-bottom:2px solid #c0392b;padding-bottom:.2em}}
img{{width:100%;border:1px solid #ddd;border-radius:6px}}ul{{list-style:none;padding-left:0}}li{{margin:.5em 0}}
input{{transform:scale(1.3);margin-right:.6em}}.note{{color:#666;font-size:.9em}}
.warn{{background:#fdecea;border-left:4px solid #c0392b;padding:.7em 1em;border-radius:4px;margin-top:1.4em}}</style>
<h1>facet-bot（多面体のまるい子）— レーザーカット手順</h1>
<p class=note>曲げない“丸い胴体”版。背面を平らなファセットに割ってあるので<b>アクリルで割れない</b>。<br>
部品＝平パネル9枚（前面＝顔1＋背面8）＋D字フタ2枚。<b>素材3mmアクリル・濃色推奨</b>。</p>
<img src="data:image/png;base64,{b64}" alt=preview>
<p class=note>↑左=展開図。フタのスロットに各パネルのタブを差し、隣同士を接着して丸くする。</p>
{rows}
<div class=warn><b>⚠ 安全</b><br>・加工中は離席しない（発火注意・消火器1209）<br>・接着はアクリル用を内側から</div>
</html>"""
    open(os.path.join(KIT, "手順.html"), "w", encoding="utf-8").write(html)


def main():
    cut, eng, elines, fac, rim = build.compose()
    pts = [(x + dx, y + dy) for loop, dx, dy in cut for (x, y) in loop]
    pts += [(x + dx, y + dy) for sub, dx, dy in eng for lp in sub for (x, y) in lp]
    for loops, dx, dy in elines:
        pts += [(x + dx, y + dy) for lp in loops for (x, y) in lp]
    minx = min(p[0] for p in pts); miny = min(p[1] for p in pts)
    maxx = max(p[0] for p in pts); maxy = max(p[1] for p in pts)
    m = 5.0
    sheet = (maxx - minx + 2 * m, maxy - miny + 2 * m)
    off = (m - minx, m - miny)

    build.main()
    shutil.copy(os.path.join(LASER_DIR, "facet-bot.svg"), os.path.join(KIT, "facet-bot.svg"))
    render(cut, eng, elines, sheet, off, os.path.join(KIT, "facet-bot.pdf"), line_pdf=True)
    render(cut, eng, elines, sheet, off, os.path.join(KIT, "preview.png"), dpi=150)
    write_docs(os.path.join(KIT, "preview.png"))
    print("kit ->", KIT)
    for f in sorted(os.listdir(KIT)):
        print("  ", f)


if __name__ == "__main__":
    main()
