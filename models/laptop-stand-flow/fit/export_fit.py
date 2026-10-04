"""cma_state.json（最適化の結果）を、本体モデルが読む fit_state.json へ書き出す。"""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cma_fit as C

st = json.load(open(HERE / "cma_state.json"))
x = np.array(st["x"], float)
cam, hs, xcs, disp, pl = C.unpack(x)
out = {
    "loss": st["loss"],
    "camera": {k: float(v) for k, v in cam.items()},
    "h": [float(v) for v in hs],
    "xc": [float(v) for v in xcs],
    "disp": [float(v) for v in disp.ravel()],
    "plank": [float(v) for v in pl],
}
json.dump(out, open(HERE.parent / "fit_state.json", "w"), indent=1)
print("wrote fit_state.json loss", st["loss"])
json.dump({"loss": st["loss"], "params": [float(v) for v in x[:7]]}, open(HERE / "camera_left.json", "w"))
print("wrote camera_left.json")
