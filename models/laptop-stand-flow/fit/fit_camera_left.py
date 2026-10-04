"""左の脚だけで、カメラを決め直す（輪郭の食い違いを最小に）。"""
import sys, json, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import fwd, ref_mask, shape_field as P
from nm import nelder_mead
from PIL import Image

STEP = 3
ROI = (30, 190, 760, 900)
comp, care_full = ref_mask.left_unit()
h_, w_ = comp.shape
x0, y0, x1, y1 = [v // STEP for v in ROI]
target = comp[STEP // 2:h_:STEP, STEP // 2:w_:STEP][y0:y1, x0:x1]
care = care_full[STEP // 2:h_:STEP, STEP // 2:w_:STEP][y0:y1, x0:x1]
F = fwd.Field()
SEEDS = np.array(P.SEEDS, float)
h, xcf = F.thickness(SEEDS)
shape = (1024, 1536)

def run(p):
    cam = dict(az=p[0], el=p[1], roll=p[2], dist=np.exp(p[3]), f=np.exp(p[4]), cx=p[5], cy=p[6])
    m = fwd.silhouette(h, cam, shape, STEP, ROI, 0.0, 0.0, xc_field=xcf)
    xor = (m ^ target) & care
    return xor.sum() / (target & care).sum(), m

best = None
for az in (40, 48):
    for cx, cy in ((660, 480), (560, 420), (760, 560)):
        s0 = [az, 11.0, 6.5, 6.59, 7.63, cx, cy]
        x, v = nelder_mead(lambda p: run(p)[0], s0, [6, 4, 2, 0.12, 0.15, 60, 60], iters=250)
        print(round(v, 4), np.round(x, 2), flush=True)
        if best is None or v < best[0]:
            best = (v, x)
v, x = best
for k in range(2):
    x, v = nelder_mead(lambda p: run(p)[0], x, [2, 1.5, 0.8, 0.04, 0.06, 15, 15], iters=300)
    print("refine", round(v, 4), np.round(x, 3), flush=True)
json.dump({"loss": v, "params": list(map(float, x))}, open(HERE / "camera_left.json", "w"))
e, m = run(x)
out = np.zeros(m.shape + (3,), np.uint8)
out[target] = (255, 0, 0)
out[m] = out[m] + np.array((0, 0, 255), np.uint8)
Image.fromarray(out).resize((out.shape[1] * 2, out.shape[0] * 2), Image.NEAREST).save(sys.argv[1])
