# -*- coding: utf-8 -*-
"""描いた画の明るさを数で見る。白く飛んだ画素の割合と、明るい側の百分位を出す。

py -3.11 tools/tableduo_figs/exposure_check.py IMG [IMG ...]
"""
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
for path in sys.argv[1:]:
    im = Image.open(path).convert("RGB")
    px = im.resize((im.width // 2, im.height // 2), Image.BOX)
    mx = [max(p) for p in px.get_flattened_data()]  # 3 色のうち一番明るい値（1 色でも飽和すれば色が抜ける）
    n = len(mx)
    mx.sort()

    def pct(q):
        return mx[min(n - 1, int(n * q))]

    over = lambda t: 100.0 * sum(1 for v in mx if v >= t) / n
    print(f"{path.split('/')[-1]:28s} >=250: {over(250):5.2f}%  >=240: {over(240):5.2f}%  >=225: {over(225):5.2f}%  "
          f"p50 {pct(.5)}  p90 {pct(.9)}  p99 {pct(.99)}  p99.9 {pct(.999)}  max {mx[-1]}")
