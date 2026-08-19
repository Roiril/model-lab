"""持ち出しキットを exports/laser/kit-foot-spacer/ に一式生成する。

中身: pipe-foot-spacer.svg（本番）/ .dxf・.pdf（予備）/ preview.png / 手順.md / 手順.html

実行: py -3.10 models/pipe-foot-spacer/make_laser_kit.py
"""
import sys, os, shutil, base64

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

import laser
from laser_params import (
    SPAN, HOLE_D, PLATE_W, PLATE_L, PLATE_T, CORNER_R,
    SHEET_T, KERF, LAYERS, STACK_T, PIN_N, PIN_SPARE, PIN_LEN, PIN_TIGHT,
    GAP, MARGIN,
)

LASER_DIR = os.path.join(ROOT, "exports", "laser")
KIT = os.path.join(LASER_DIR, "kit-foot-spacer")
MM2IN = 1 / 25.4


def _patch(subpaths, dx, dy, fc):
    """外周＋穴の複合パス。matplotlib は nonzero 塗りなので穴は逆巻きにする。"""
    verts, codes = [], []
    for idx, lp in enumerate(subpaths):
        pts = list(lp)
        if idx > 0:
            pts = pts[::-1]
        if pts[0] != pts[-1]:
            pts = pts + [pts[0]]
        for i, (x, y) in enumerate(pts):
            verts.append((x + dx, y + dy))
            codes.append(Path.MOVETO if i == 0 else Path.LINETO)
        codes[-1] = Path.CLOSEPOLY
    return PathPatch(Path(verts, codes), fc=fc, ec="none")


def render(path, sheet, dpi=150, lw=0.8):
    W, H = sheet
    row_h = PLATE_W + GAP
    fig = plt.figure(figsize=(W * MM2IN, H * MM2IN))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.set_aspect("equal"); ax.axis("off"); ax.invert_yaxis()
    ax.add_patch(plt.Rectangle((0, 0), W, H, fc="#f7f4ee", ec="none"))
    # 材料が残る部分をグレーで（板 3 枚 + 角棒）
    for i in range(LAYERS):
        ax.add_patch(_patch(laser.plate_loops(),
                            MARGIN + PLATE_L / 2,
                            MARGIN + PLATE_W / 2 + i * row_h, "#cfcbc4"))
    n = PIN_N + PIN_SPARE
    y = MARGIN + LAYERS * row_h + laser.PIN_CUT_L / 2
    for i in range(n):
        x = MARGIN + laser.PIN_CUT_L / 2 + i * (laser.PIN_CUT_L + GAP)
        ax.add_patch(_patch([laser.rect(0, 0, laser.PIN_CUT_L, laser.PIN_CUT_W)],
                            x, y, "#cfcbc4"))
    # カット線
    for loop, dx, dy in laser.compose():
        xs = [p[0] + dx + MARGIN for p in loop] + [loop[0][0] + dx + MARGIN]
        ys = [p[1] + dy + MARGIN for p in loop] + [loop[0][1] + dy + MARGIN]
        ax.plot(xs, ys, "-", color="red", lw=lw)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


MD = f"""# 足まわり芯間合わせ板 — レーザーカット手順

このフォルダ（`kit-foot-spacer`）をそのままレーザーPCへ渡して、上から順にやる。

## 何を作るか

脚パイプ 2 本の**下端の芯間を {SPAN:.0f}mm に固定する板**。上端は M 字ジョイントが
{SPAN:.0f}mm で咥えているので、下でも同じ間隔を与えるとパイプが 2 点で拘束されて垂直に立つ。

3Dプリント版は 1 枚 {PLATE_T:.0f}mm 厚。レーザー版は **{SHEET_T:.0f}mm 板を {LAYERS} 枚重ねて {STACK_T:.0f}mm** にする。
ソケットを掴む長さが 1mm 伸びるだけで、止まる高さも掴む位置も変わらない。

| ファイル | 用途 |
|---|---|
| **pipe-foot-spacer.svg** | ← Ruby に読み込む本番カットデータ |
| pipe-foot-spacer.pdf / .dxf | SVG が読めなかったときの予備（1:1 ベクター） |
| preview.png | 何を切るかの確認用（グレー＝残る材料） |
| 手順.md / 手順.html | これ |

切り出すのは **板 {LAYERS} 枚**（{PLATE_L:.0f} x {PLATE_W:.0f}mm、Φ{HOLE_D} の穴 2 個）と
**位置決めの角棒 {PIN_N + PIN_SPARE} 本**（{PIN_LEN:.1f} x {PIN_TIGHT:.1f}mm。使うのは {PIN_N} 本、残りは予備）。

---

## 準備するもの
- [ ] **{SHEET_T:.0f}mm アクリル板**（**{{SHEET_W:.0f}} x {{SHEET_H:.0f}}mm 以上**）。色は見た目だけの話なので何でもよい
- [ ] アクリル用の**溶剤系接着剤**（アクリサンデー等）。無ければ瞬間接着剤か 2 液エポキシ

---

## 手順

### A. 現地セット
1. [ ] **窓を開ける**（ダクト排気）
2. [ ] レーザーカッターの **電源 ON**
3. [ ] アクリル板を加工エリアに **置く**
4. [ ] 上下ボタンで **ワークエリアを上げる**
5. [ ] **ピント調整器具**をヘッドに引っかけ、板を少しずつ上げる → 器具が外れて倒れた高さが焦点。器具を外す
6. [ ] 上下左右キーで **ヘッドを切りたい位置へ** 移動

### B. Ruby（ソフト）
7. [ ] Ruby を開く（`share.fms` アカウント。2段階認証が出たら現地PCのChromeのGmailで番号確認）
8. [ ] **pipe-foot-spacer.svg を管理画面にドラッグ&ドロップ**（読めなければ .pdf か .dxf で）
9. [ ] 寸法確認：**板 1 枚の長辺が約 {PLATE_L:.0f}mm**、**穴が Φ約 {HOLE_D}** で出ているか。違ったらスケール調整
10. [ ] **赤（細線）＝カット** を割り当てる（このデータに彫刻は無い。色は赤 1 色だけ）
11. [ ] **ジョブ画面**で図面をヘッド位置［＋］に合わせ、**キュー作成**
12. [ ] **再生ボタンで加工開始**

> ⚠ 保護シートは**剥がさなくてよい**（彫刻が無いので）。剥がすのは接着の直前。

### C. 重ねて貼る
> 穴がずれると、ずれたぶんだけ穴が実質的に細くなる。**0.5mm ずれると Φ36.6 のソケットに入らなくなる**。
> 角棒はそのために入っている。

13. [ ] 板 3 枚の**接着面の保護シートを剥がす**（外側の面は最後まで貼ったままでよい）
14. [ ] 3 枚を重ね、**小さい穴 4 つに角棒を上から刺す**。上段の 2 本が左右方向、下段の 2 本が前後方向を決める
15. [ ] 角棒の向き：**ツヤのある面（板の表と裏だった面）を長穴の長い方へ向ける**。
      切り口（すりガラス状の面）の側が {PIN_TIGHT:.1f}mm ちょうどで、そちらで位置が決まる
16. [ ] 角棒が入りにくければ、**紙やすりで切り口を軽く落とす**（アクリルの実厚は公称より厚いことがある）。
      **叩き込まない**。アクリルは粘らずに割れる
17. [ ] 平らな台の上で**上から押さえ**、**合わせ目に溶剤系接着剤を流す**（毛細管現象で吸い込まれる。数十秒で固定）
18. [ ] 角棒は**刺したまま**でよい。頭は {STACK_T - PIN_LEN:.1f}mm 沈むので出っ張らない
19. [ ] 固まるまで **30 分**は動かさない

### D. 現物合わせ
20. [ ] 足ジョイント 2 個を床に置き、**上から板を落とす**。ソケット（Φ36.6）を掴んでリブの頂点（床から 47.3mm）で止まれば正解
21. [ ] パイプは板を通す前でも後でもよい

---

## ⚠ 安全（必ず守る）
- **加工中は絶対に離席しない**。アクリルは発火することがある
- 火が出たら 10秒程度は様子見 → 続くなら **1209のエアロゾル消火器**。広がったら廊下の消火器
- 加工後のパーツは熱い・エッジが鋭いことがある

---

## うまく合わなかった時（次回用メモ）
- **穴がソケットに入らない** → `models/pipe-foot-spacer/params.py` の `CLEAR` を上げる（0.25 → 0.35）
- **入るがガタつく** → `CLEAR` を下げる（0.25 → 0.15）。ガタは芯間の誤差にそのまま乗る
- **角棒が穴に入らない** → `laser_params.py` の `PIN_SLOP` を上げる（0.6 → 0.9）
- **角棒がゆるい** → `PIN_FIT` を下げる（0.10 → 0.05）
- 切り口が全体に太い／細い → `lib/laser_core.py` の `KERF`（現在 {KERF}）を実測値に直す
- 直したら `py -3.10 models/pipe-foot-spacer/laser.py` → `py -3.10 models/pipe-foot-spacer/make_laser_kit.py` で再生成
"""

HTML_HEAD = """<!doctype html><html lang=ja><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>芯間合わせ板 レーザーカット手順</title>
<style>
body{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;max-width:680px;margin:0 auto;padding:16px;line-height:1.7;color:#1a1a1a;background:#fffdf7}
h1{font-size:1.4rem} h2{font-size:1.05rem;margin-top:1.4em;border-bottom:2px solid #c0392b;padding-bottom:.2em}
img{width:100%;border:1px solid #ddd;border-radius:6px}
ul{list-style:none;padding-left:0} li{margin:.5em 0} label{cursor:pointer}
input{transform:scale(1.3);margin-right:.6em}
table{border-collapse:collapse;width:100%;font-size:.92em}
th,td{border:1px solid #ddd;padding:.4em .6em;text-align:left}
th{background:#f2ede3}
code{background:#f2ede3;padding:.1em .35em;border-radius:3px;font-size:.9em}
.warn{background:#fdecea;border-left:4px solid #c0392b;padding:.8em 1em;border-radius:4px;margin-top:1.5em}
.note{color:#666;font-size:.9em}
</style>
"""


def md_to_html(md, img_b64):
    """この手順書の書式だけを扱う最小変換（見出し/表/チェック/箇条書き/引用）。"""
    out, in_tbl, in_list = [], False, False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>"); in_list = False

    def close_tbl():
        nonlocal in_tbl
        if in_tbl:
            out.append("</table>"); in_tbl = False

    def inline(t):
        import re
        t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
        return t

    import re as _re
    CHECK = _re.compile(r"^(?:- |\d+\. )\[ \] (.*)$")

    for line in md.splitlines():
        s = line.rstrip()
        if in_list and s.startswith("   ") and s.strip():
            # 直前の項目の続き行（手順の補足）
            out[-1] = out[-1].replace("</label></li>", " " + inline(s.strip()) + "</label></li>")
            continue
        if s.startswith("# "):
            close_list(); close_tbl()
            out.append(f"<h1>{inline(s[2:])}</h1>")
            out.append(f'<img src="data:image/png;base64,{img_b64}" alt="板取り">')
        elif s.startswith("### "):
            close_list(); close_tbl(); out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("## "):
            close_list(); close_tbl(); out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("|"):
            close_list()
            cells = [c.strip() for c in s.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            if not in_tbl:
                out.append("<table>"); in_tbl = True
                out.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
            else:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
        elif CHECK.match(s):
            close_tbl()
            body = CHECK.match(s).group(1)
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li><label><input type=checkbox>{inline(body)}</label></li>")
        elif s.startswith("- "):
            close_tbl()
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{inline(s[2:])}</li>")
        elif s.startswith("> "):
            close_list(); close_tbl()
            out.append(f'<p class=note>{inline(s[2:])}</p>')
        elif s.startswith("---"):
            close_list(); close_tbl(); out.append("<hr>")
        elif not s:
            close_list(); close_tbl()
        else:
            close_list(); close_tbl()
            out.append(f"<p>{inline(s)}</p>")
    close_list(); close_tbl()
    html = "\n".join(out)
    html = html.replace("<h2>⚠ 安全（必ず守る）</h2>",
                        '<div class=warn><h2 style="border:none;margin-top:0">⚠ 安全（必ず守る）</h2>')
    html = html.replace("<h2>うまく合わなかった時（次回用メモ）</h2>",
                        '</div><h2>うまく合わなかった時（次回用メモ）</h2>')
    html = html.replace("<hr>\n</div>", "</div>")   # 注意書きの箱の中に線が残らないように
    return HTML_HEAD + html + "\n</html>\n"


def main():
    os.makedirs(KIT, exist_ok=True)
    _, sheet = laser.main()

    png = os.path.join(KIT, "preview.png")
    render(png, sheet, dpi=150)
    render(os.path.join(KIT, "pipe-foot-spacer.pdf"), sheet, lw=0.4)
    for f in ("pipe-foot-spacer.svg", "pipe-foot-spacer.dxf"):
        shutil.copy(os.path.join(LASER_DIR, f), os.path.join(KIT, f))

    md = MD.format(SHEET_W=sheet[0], SHEET_H=sheet[1])
    open(os.path.join(KIT, "手順.md"), "w", encoding="utf-8").write(md)
    b64 = base64.b64encode(open(png, "rb").read()).decode()
    open(os.path.join(KIT, "手順.html"), "w", encoding="utf-8").write(md_to_html(md, b64))

    print("kit ->", KIT)
    for f in sorted(os.listdir(KIT)):
        p = os.path.join(KIT, f)
        print(f"   {f}  {os.path.getsize(p)/1024:.0f}KB")


if __name__ == "__main__":
    main()
