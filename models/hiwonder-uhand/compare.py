"""写真とレンダーを左右に並べた比較画像を作る。ラベルはファイル名から焼く。

py -3.11 models/hiwonder-uhand/compare.py <renders_dir> <out.png>
写真は ref/ に置く（ref_main.png / ref_side.png / ref_servo.png / ref_back.png）。
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = [("main", "ref_main.png"), ("side", "ref_side.png"), ("servo", "ref_servo.png"), ("back", "ref_back.png"), ("front", "ref_front.png")]
# 写真が右手版（左右反転）のもの。レンダーを左右反転して並べる
MIRRORED = {"servo", "back"}


def main():
    rdir, out = sys.argv[1], sys.argv[2]
    rows = []
    for view, ref in PAIRS:
        rp, fp = os.path.join(HERE, "ref", ref), os.path.join(rdir, f"{view}.png")
        if not os.path.exists(fp):
            continue
        if not os.path.exists(rp):
            sys.exit(f"missing reference: {rp}")
        a, b = Image.open(rp).convert("RGB"), Image.open(fp).convert("RGB")
        if view in MIRRORED:
            b = b.transpose(Image.FLIP_LEFT_RIGHT)
        h = 700
        a = a.resize((round(a.width * h / a.height), h))
        b = b.resize((round(b.width * h / b.height), h))
        row = Image.new("RGB", (a.width + b.width + 30, h + 34), "white")
        row.paste(a, (0, 34)); row.paste(b, (a.width + 30, 34))
        d = ImageDraw.Draw(row)
        d.text((6, 8), f"PHOTO {ref}", fill=(200, 0, 0))
        d.text((a.width + 36, 8), f"RENDER {view}.png" + (" (mirrored: photo is right-hand version)" if view in MIRRORED else ""), fill=(0, 0, 200))
        rows.append(row)
    if not rows:
        sys.exit("no renders found")
    W = max(r.width for r in rows)
    sheet = Image.new("RGB", (W, sum(r.height for r in rows)), "white")
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height
    sheet.save(out)
    print(out, sheet.size)


main()
