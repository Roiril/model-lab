"""Slice the isolated v2 mounting specimens with production profiles and meters."""
import importlib.util
import argparse
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v2_mount_plate", HERE / "plate.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
parser = argparse.ArgumentParser()
parser.add_argument('--case', default='normal')
parser.add_argument('--common-only', action='store_true')
args = parser.parse_args()
suffix = '' if args.case == 'normal' else '-' + args.case
P.OUT = HERE / ("build/v2-mount-slice" + suffix)
P.BUILD = P.OUT
P.OUT.mkdir(exist_ok=True)
source = HERE / ("build/v2-mount-probe" + suffix)
specimens = (("blank", "key_l"), ("blank", "key_r"), ("blank", "panel"),
             ("link_lid", "panel"), ("three_pixels", "panel"), ("sector_flag", "panel"))
if args.case != 'normal':
    specimens = specimens[:3]
if args.common_only:
    specimens = [row for row in specimens if row[0] != 'link_lid']
parts = [P.part_mesh(face + "/" + pid, source / f"{face}-{pid}.stl")
         for face, pid in specimens]
logs = Path("G:/マイドライブ/shubie/reports")
label = "v2-mount" + suffix + ('-common' if args.common_only else '')
result = P.slice_plate(label, parts, P.profiles(P.profile_data()), logs)
for row in result["named_objects"]:
    print(json.dumps(row, ensure_ascii=False), flush=True)
P.write(logs / ("mystery-box-sg92r-f1-" + label + "-slice.json"), result)
print("V2_MOUNT_SLICE_PASS=" + str(result["slice_pass"]), flush=True)
sys.exit(0 if result["slice_pass"] else 1)
