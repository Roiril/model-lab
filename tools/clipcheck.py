"""描いた画の白飛び・黒つぶれの割合を出す。 py -3.11 tools/clipcheck.py a.png [b.png ...]"""
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
for p in sys.argv[1:]:
    im = Image.open(p).convert("RGB")
    n = im.width * im.height
    px = list(im.getdata())
    hi = sum(1 for r, g, b in px if max(r, g, b) >= 250) / n
    hi_all = sum(1 for r, g, b in px if min(r, g, b) >= 245) / n
    lo = sum(1 for r, g, b in px if max(r, g, b) <= 8) / n
    L = sorted(0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in px)
    print(f"{p}: 1ch>=250 {hi:.2%} / 白(全ch>=245) {hi_all:.2%} / 黒(<=8) {lo:.2%} / 輝度 p50 {L[n // 2]:.0f} p99 {L[int(n * .99)]:.0f}")
