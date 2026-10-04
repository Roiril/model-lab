"""参考画像から、大きい2脚（左・中）の輪郭マスクを取り出す。numpy + PIL。"""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "design" / "reference.png"


def label_components(mask):
    """4近傍の連結成分ラベル。小さい画像向けの素朴な実装。"""
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    n = 0
    sizes = [0]
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n += 1
        stack = [(y0, x0)]
        lab[y0, x0] = n
        count = 0
        while stack:
            y, x = stack.pop()
            count += 1
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    stack.append((ny, nx))
        sizes.append(count)
    return lab, sizes


def stand_mask(region=(0, 0, 1536, 1024)):
    im = np.array(Image.open(REF).convert("RGB")).astype(int)
    rb = im[:, :, 0] - im[:, :, 2]
    mean = im.mean(axis=2)
    m = (rb >= 17) | (mean >= 208)
    m &= im.sum(axis=2) > 150
    x0, y0, x1, y1 = region
    keep = np.zeros_like(m)
    keep[y0:y1, x0:x1] = True
    m &= keep
    img = Image.fromarray((m * 255).astype(np.uint8))
    img = img.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))   # 閉じる
    img = img.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))   # 開く
    m = np.array(img) > 127
    lab, sizes = label_components(m)
    out = np.zeros_like(m)
    for i, s in enumerate(sizes):
        if i and s > 8000:
            out |= lab == i
    return out


if __name__ == "__main__":
    import sys
    m = stand_mask((0, 150, 1130, 900))
    Image.fromarray((m * 255).astype(np.uint8)).save(sys.argv[1])
    print(m.sum())


# 左の脚と中の脚が重なる・接する場所。数えない（care=False）。
DONT_CARE = [(598, 300, 705, 410), (540, 580, 600, 640), (560, 595, 960, 705)]
# 左の脚のレール板の先端（後ろに中の脚の柱が重なるのでマスクでは取れない）。手で読んだ輪郭（画像ピクセル）
TIP_POLY = [(596, 326), (620, 337), (640, 345), (660, 343), (677, 343), (685, 350), (686, 358),
            (680, 366), (664, 369), (640, 370), (618, 366), (600, 362), (590, 352)]


def left_unit(seed=(200, 300)):
    """左の脚（手前）だけのマスクと、数える領域。画像全体の大きさ。

    レール板の先端は後ろに中の脚の柱が重なってマスクでは取れないので、手で読んだ輪郭（TIP_POLY）を使う。
    先端の輪郭の少し外側は「何も無いはず」の領域として数える（返しが垂れ下がるのを防ぐ）。"""
    from PIL import ImageDraw, ImageFilter
    m = stand_mask((0, 150, 1130, 900))
    care = np.ones_like(m)
    cut = m.copy()
    for x0, y0, x1, y1 in DONT_CARE:
        care[y0:y1, x0:x1] = False
        cut[y0:y1, x0:x1] = False
    lab, sizes = label_components(cut)
    comp = (lab == lab[seed[1], seed[0]]) & care
    img = Image.new("L", (m.shape[1], m.shape[0]), 0)
    ImageDraw.Draw(img).polygon(TIP_POLY, fill=255)
    tip = np.array(img) > 127
    zone = np.array(img.filter(ImageFilter.MaxFilter(25))) > 127     # 先端の輪郭 + 12px
    care |= zone
    comp |= tip
    return comp, care
