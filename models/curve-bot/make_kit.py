"""make_kit — curve-bot の 1209 持ち出しキットを exports/laser/kit-curve-1209/ に生成。

中身: curve-bot.svg（本番カット）/ .pdf（1:1）/ preview.png / 手順.md / 手順.html。
実行: python models/curve-bot/make_kit.py
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
KIT = os.path.join(LASER_DIR, "kit-curve-1209")
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


def render(cut, clines, eng, elines, sheet, off, path, dpi=150, line_pdf=False):
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
    for pl, dx, dy in clines:
        ax.plot([x + dx + ox for x, y in pl], [y + dy + oy for x, y in pl], "r-", lw=rlw)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


PROC = [
 ("A. 現地セット", ["窓を開ける（ダクト排気）","電源 ON","MDF/合板(2.5-3mm)を置く","ワークエリアを上げる","ピント調整器具で焦点合わせ→器具を外す","ヘッドを切りたい位置へ"]),
 ("B. Ruby", ["Ruby を開く（share.fms）","curve-bot.svg をD&D（ダメなら .pdf）","色割り当て → 赤=カット / 黒=彫刻。※ヒンジのスリットも赤=カット","MDF/合板用のパワー/スピード（アクリルより弱めが目安）","ジョブ作成 → 再生"]),
 ("C. 組み立て", ["帯のヒンジ部分をゆっくり曲げて筒にする（無理に急がず、割れたら出力弱めを再検討）","前面フラット部＝顔スクリーン。左右がカーブ","帯の上下タブを D字フタのスロットに差し込む（上フタ・下フタ）","継ぎ目とタブは接着剤で固定（木工用/瞬間）"]),
]


def write_docs(preview_png):
    b64 = base64.b64encode(open(preview_png, "rb").read()).decode()
    md = ["# 1209 レーザーカット手順 — curve-bot（まるい子）",
          "",
          "リビングヒンジで胴体を巻く円筒（正確には前面フラットの“かまぼこ”型）ロボット。",
          "**素材は 2.5〜3mm の MDF / シナ合板**（アクリルはヒンジで割れやすいので不可）。",
          "",
          "## 中身",
          "| ファイル | 用途 |",
          "|---|---|",
          "| **curve-bot.svg** | 本番カットデータ |",
          "| curve-bot.pdf | 予備（1:1） |",
          "| preview.png | 展開図の確認用 |",
          "",
          "パーツ: 帯1枚（ヒンジ＋顔）＋ D字フタ2枚。",
          "",
          "> ⚠ **これは実験的デザイン**。リビングヒンジの曲げやすさ（スリット密度）とタブの嵌合は、",
          "> 素材ロットで変わるので**初回は要調整**。うまく曲がらない/割れる場合は"
          "`models/curve-bot/params.py` の `HINGE_LIG`（小さく＝柔らかい）等を詰める。",
          ""]
    for title, items in PROC:
        md.append(f"### {title}")
        for it in items:
            md.append(f"- [ ] {it}")
        md.append("")
    md += ["## ⚠ 安全",
           "- 加工中は離席しない（発火注意・消火器は1209）",
           "- MDFは煙が多いので排気を確実に"]
    open(os.path.join(KIT, "手順.md"), "w", encoding="utf-8").write("\n".join(md))

    rows = ""
    for title, items in PROC:
        rows += f"<h2>{title}</h2><ul>" + "".join(
            f"<li><label><input type=checkbox> {it}</label></li>" for it in items) + "</ul>"
    html = f"""<!doctype html><html lang=ja><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>curve-bot 手順</title>
<style>body{{font-family:system-ui,sans-serif;max-width:680px;margin:0 auto;padding:16px;line-height:1.7;background:#fffdf7;color:#1a1a1a}}
h1{{font-size:1.35rem}}h2{{font-size:1.05rem;margin-top:1.3em;border-bottom:2px solid #c0392b;padding-bottom:.2em}}
img{{width:100%;border:1px solid #ddd;border-radius:6px}}ul{{list-style:none;padding-left:0}}li{{margin:.5em 0}}
input{{transform:scale(1.3);margin-right:.6em}}.note{{color:#666;font-size:.9em}}
.warn{{background:#fdecea;border-left:4px solid #c0392b;padding:.7em 1em;border-radius:4px;margin-top:1.4em}}</style>
<h1>curve-bot（まるい子）— レーザーカット手順</h1>
<p class=note>リビングヒンジで胴体を巻く円筒ロボット。<b>素材は2.5〜3mmのMDF/シナ合板</b>（アクリルはヒンジで割れる）。<br>
パーツ＝帯1枚（ヒンジ＋顔）＋D字フタ2枚。<b>ヒンジのスリットも赤=カット</b>で処理。</p>
<img src="data:image/png;base64,{b64}" alt=preview>
<p class=note>↑実験的デザイン。ヒンジの曲げやすさ・タブ嵌合は初回要調整（params.py の HINGE_LIG 等）。</p>
{rows}
<div class=warn><b>⚠ 安全</b><br>・加工中は離席しない（発火注意・消火器1209）<br>・MDFは煙が多いので排気を確実に</div>
</html>"""
    open(os.path.join(KIT, "手順.html"), "w", encoding="utf-8").write(html)


def main():
    cut, clines, eng, elines = build.compose()
    pts = [(x + dx, y + dy) for loop, dx, dy in cut for (x, y) in loop]
    pts += [(x + dx, y + dy) for pl, dx, dy in clines for (x, y) in pl]
    pts += [(x + dx, y + dy) for sub, dx, dy in eng for lp in sub for (x, y) in lp]
    for loops, dx, dy in elines:
        pts += [(x + dx, y + dy) for lp in loops for (x, y) in lp]
    minx = min(p[0] for p in pts); miny = min(p[1] for p in pts)
    maxx = max(p[0] for p in pts); maxy = max(p[1] for p in pts)
    m = 5.0
    sheet = (maxx - minx + 2 * m, maxy - miny + 2 * m)
    off = (m - minx, m - miny)

    build.main()  # exports/laser/curve-bot.svg を最新化
    shutil.copy(os.path.join(LASER_DIR, "curve-bot.svg"), os.path.join(KIT, "curve-bot.svg"))
    render(cut, clines, eng, elines, sheet, off, os.path.join(KIT, "curve-bot.pdf"), line_pdf=True)
    render(cut, clines, eng, elines, sheet, off, os.path.join(KIT, "preview.png"), dpi=150)
    write_docs(os.path.join(KIT, "preview.png"))
    print("kit ->", KIT)
    for f in sorted(os.listdir(KIT)):
        print("  ", f)


if __name__ == "__main__":
    main()
