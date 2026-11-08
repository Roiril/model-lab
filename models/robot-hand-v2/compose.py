"""比較の画像を組む。並べる画像が 1 つでも無ければ組まずに止まる。各画像の下にファイル名を焼く。

py -3.11 models/robot-hand-v2/compose.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

OUT = r"G:\マイドライブ\shubie\renders\robot-hand-v2"
DS = r"G:\マイドライブ\shubie\design-study\2026-11-07-robot-hand"
SHEETS = {
    "compare-target.png": [(DS + r"\v2\target-a.png", "目標 target-a"), (OUT + r"\model-target.png", "モデル model-target")],
    "compare-side.png": [(r"C:\Users\kouga\Pictures\Screenshots\スクリーンショット 2026-11-08 100411.png", "厚みの参考"),
                         (OUT + r"\model-side-curl.png", "モデル 横（90° 回して指を左へ）")],
    "compare-wrist.png": [(DS + r"\ref\wrist-ref-x8.png", "手首の参考（8 倍）"), (OUT + r"\model-wrist.png", "モデル 手首の寄り"),
                          (OUT + r"\model-wrist-flex.png", "モデル 手首を曲げて偏らせた姿勢")],
    "views-3.png": [(OUT + r"\model-front.png", "正面"), (OUT + r"\model-rear.png", "真後ろ"), (OUT + r"\model-oblique.png", "斜め後ろ")],
}
ROTATE = {"model-side-curl.png": 90}
H = 900


def font(size):
    for p in (r"C:\Windows\Fonts\YuGothM.ttc", r"C:\Windows\Fonts\meiryo.ttc", r"C:\Windows\Fonts\msgothic.ttc"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def sheet(items, path):
    missing = [p for p, _ in items if not os.path.exists(p)]
    if missing:
        sys.exit("無い画像: " + ", ".join(missing))
    tiles = []
    for p, label in items:
        im = Image.open(p).convert("RGB")
        r = ROTATE.get(os.path.basename(p))
        if r:
            im = im.rotate(r, expand=True)
        im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
        tiles.append((im, f"{label}  ({os.path.basename(p)})"))
    W = sum(t.width for t, _ in tiles) + 20 * (len(tiles) + 1)
    out = Image.new("RGB", (W, H + 90), (255, 255, 255))
    d = ImageDraw.Draw(out)
    f = font(26)
    x = 20
    for im, label in tiles:
        out.paste(im, (x, 20))
        d.text((x, H + 35), label, fill=(30, 30, 30), font=f)
        x += im.width + 20
    out.save(path)
    print("書いた:", path, out.size)


if __name__ == "__main__":
    only = sys.argv[1:] or list(SHEETS)
    for name in only:
        sheet(SHEETS[name], os.path.join(OUT, name))
