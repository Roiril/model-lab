"""Slice isolated v2 frame specimens with the production profiles and meters."""
import importlib.util
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v2_frame_plate", HERE / "plate.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
P.OUT = HERE / "build/v2-frame-slice"
P.BUILD = P.OUT
P.OUT.mkdir(exist_ok=True)
source = HERE / "build/v2-frame-probe"
ids = ["lower_frame", "upper_frame"] + [f"post_{i}" for i in range(4)]
ids += ["carrier_" + slot for slot in ("front", "right", "back", "left")]
logs = Path("G:/マイドライブ/shubie/reports")
results = []
for suffix, group in (("skeleton", ids[:6]), ("carriers", ids[6:])):
    parts = [P.part_mesh("frame/" + pid, source / (pid + ".stl")) for pid in group]
    result = P.slice_plate("v2-frame-" + suffix, parts, P.profiles(P.profile_data()), logs)
    for row in result["named_objects"]:
        print(json.dumps(row, ensure_ascii=False), flush=True)
    results.append(result)
P.write(logs / "F1-v2-frame-slice.json", results)
passed = all(result["slice_pass"] for result in results)
print("V2_FRAME_SLICE_PASS=" + str(passed), flush=True)
sys.exit(0 if passed else 1)
