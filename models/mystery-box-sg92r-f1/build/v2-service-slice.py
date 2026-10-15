import importlib.util
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v2_service_plate", HERE / "plate.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
P.OUT = P.BUILD = HERE / "build/v2-service-slice"
P.OUT.mkdir(exist_ok=True)
parts = [P.part_mesh("frame/" + part, HERE / "build/v2-service-probe" / (part + ".stl"))
         for part in ("wiring", "tray", "lower_frame", "carrier_back")]
result = P.slice_plate("v2-service", parts, P.profiles(P.profile_data()),
                       Path("G:/マイドライブ/shubie/reports"))
for row in result["named_objects"]:
    print(row, flush=True)
sys.exit(0 if result["slice_pass"] else 1)
