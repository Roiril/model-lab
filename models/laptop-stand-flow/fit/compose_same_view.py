"""same-view.png（参考画像 / 同じカメラのモデル / 輪郭の重ね）を作る。py -3.11 compose_same_view.py <render.png> <out.png> <xor%>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
render, out_path, xor = sys.argv[1], sys.argv[2], sys.argv[3]
ref = Image.open(HERE.parent / "design" / "reference.png").convert("RGB")
mine = Image.open(render).convert("RGB")
box = (40, 180, 740, 880)
a, b = ref.crop(box), mine.crop(box)
m = np.load(ROOT / "exports" / "laptop-stand-flow" / "measure_mask.npz")["mask"]
t = np.load(HERE / "left_target.npz")["target"]


def edge(mk):
    p = np.pad(mk, 1)
    inner = p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return mk & ~inner


ov = np.array(ref).copy()
ov[edge(t)] = (0, 200, 0)
ov[edge(m)] = (230, 30, 30)
c = Image.fromarray(ov).crop(box)
w = a.width
out = Image.new("RGB", (w * 3, a.height + 40), (255, 255, 255))
out.paste(a, (0, 40)); out.paste(b, (w, 40)); out.paste(c, (2 * w, 40))
d = ImageDraw.Draw(out)
d.text((10, 12), "reference (AI image)", fill=(0, 0, 0))
d.text((w + 10, 12), "this model, same camera", fill=(0, 0, 0))
d.text((2 * w + 10, 12), f"outline: red = model, green = reference   xor/area = {xor}", fill=(0, 0, 0))
out.save(out_path)
