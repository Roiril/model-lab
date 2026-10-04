"""参考画像の左の脚と、iso.png を並べて cmp.png に書く（py -3.11 compare.py <out.png>）。"""
import sys
from pathlib import Path
from PIL import Image
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def crop_unit(img, ref_color_xy=(30, 990), thr=38):
    arr = np.array(img).astype(int)
    bgc = arr[ref_color_xy[1], ref_color_xy[0]]
    mask = np.abs(arr - bgc).sum(axis=2) > thr
    ys, xs = np.where(mask)
    return img.crop((max(xs.min() - 20, 0), max(ys.min() - 20, 0), xs.max() + 20, ys.max() + 20))


a = Image.open(HERE / "design" / "reference.png").convert("RGB").crop((40, 180, 720, 860))
b = Image.open(ROOT / "exports" / "laptop-stand-flow" / "iso.png").convert("RGB")
b = crop_unit(b)
h = 680
b = b.resize((int(b.width * h / b.height), h))
c = Image.new("RGB", (a.width + b.width, h), (255, 255, 255))
c.paste(a, (0, 0))
c.paste(b, (a.width, 0))
c.save(sys.argv[1])
print(c.size)
