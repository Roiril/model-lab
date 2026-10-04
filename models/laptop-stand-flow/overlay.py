"""trace.py の輪郭を参考画像に重ねて確認する（py -3.11 overlay.py）。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_trace as T

K = 4
X0, Y0, X1, Y1 = 1140, 360, 1500, 570


def catmull(points, closed=True, n=12):
    pts = np.array(points, float)
    m = len(pts)
    out = []
    for i in range(m):
        p0, p1, p2, p3 = pts[(i - 1) % m], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


def main(out):
    im = Image.open(HERE / "design" / "reference.png").convert("RGB")
    c = im.crop((X0, Y0, X1, Y1)).resize(((X1 - X0) * K, (Y1 - Y0) * K), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    for pts, col in ((T.OUTER, (255, 0, 0)), (T.HOLE, (0, 160, 255))):
        s = catmull(pts)
        xy = [((x - X0) * K, (y - Y0) * K) for x, y in s]
        d.line(xy + [xy[0]], fill=col, width=2)
        for x, y in pts:
            r = 3
            d.ellipse([(x - X0) * K - r, (y - Y0) * K - r, (x - X0) * K + r, (y - Y0) * K + r], outline=col)
    x0, x1 = T.PLANK_X
    d.rectangle([(x0 - X0) * K, (T.PLANK_TOP_Y - Y0) * K, (x1 - X0) * K, (T.PLANK_BOTTOM_Y - Y0) * K], outline=(0, 200, 0))
    c.save(out)


if __name__ == "__main__":
    main(sys.argv[1])
