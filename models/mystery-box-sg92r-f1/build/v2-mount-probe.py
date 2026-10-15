"""Build only the v2 common-mount evidence; production files remain untouched."""
import importlib.util
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT))
from tools.mechgate_lib import meshcheck
from printmech.solid_meter import Solid, Meter, VOLUME_FLOOR_MM3
from printmech.contract import rotation, translation

spec = importlib.util.spec_from_file_location("v2_mount_compose", HERE / "compose.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
parser = argparse.ArgumentParser()
parser.add_argument('--case', default='normal')
parser.add_argument('--faces', nargs='+', default=["blank", "template", "link_lid", "three_pixels", "sector_flag"])
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
interface = C.read(HERE / "build/v2-mount-interface.json")
if args.case == 'no-fingerwell':
    interface['mount_geometry']['parts']['panel']['operations'] = [
        row for row in interface['mount_geometry']['parts']['panel']['operations']
        if abs(row['shape']['center_mm'][0]) != 36]
if args.case == 'fingerwell-pyramid':
    for row in interface['mount_geometry']['parts']['panel']['operations']:
        s = row['shape']
        if abs(s['center_mm'][0]) == 36:
            u = s['center_mm'][0]
            row['shape'] = {'type': 'loft_box', 'center_mm': [u, -22, .225], 'size_mm': [2, 2, 1.45],
                            'sections': [{'d_mm': -.5, 'center_uv_mm': [u, -22], 'size_uv_mm': [2, 2]},
                                         {'d_mm': 0, 'center_uv_mm': [u, -22], 'size_uv_mm': [2, 2]},
                                         {'d_mm': .95, 'center_uv_mm': [u, -22], 'size_uv_mm': [.1, .1]}]}
if args.case == 'fingerwell-through':
    for row in interface['mount_geometry']['parts']['panel']['operations']:
        s = row['shape']
        if row['op'] == 'difference' and s['type'] == 'box' and abs(s['center_mm'][0]) == 36:
            s['center_mm'][2] = 1.5
            s['size_mm'][2] = 5
suffix = '' if args.case == 'normal' else '-' + args.case
out = HERE / ("build/v2-mount-probe" + suffix)
out.mkdir(exist_ok=True)
report = {"parts": [], "key_paths": []}
common = C.common_params()
meter = Meter()


def triangles(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    return np.array([[list(mesh.vertices[i].co) for i in t.vertices] for t in mesh.loop_triangles], dtype=np.float32).astype(float)


for face in args.faces:
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    modules = C.face_package(face, "v2_probe_" + face, with_geometry=True)
    built = modules["geometry"].build(interface, common)
    solids = {}
    for pid in ("panel", "key_l", "key_r"):
        desc = built[pid]
        obj = desc["object"]
        C.clean_object(obj)
        tris = triangles(obj)
        solids[pid] = Solid(pid, tris)
        turn = np.array(desc["print_rotation"], dtype=float)
        printed = tris @ turn[:3, :3].T
        turn[2, 3] = -printed[:, :, 2].min()
        printed += turn[:3, 3]
        topology = meshcheck.topology(tris)
        row = {"face": face, "part": pid, "topology": topology,
               "components": len(meshcheck.components(tris)),
               "volume_mm3": abs(meshcheck.signed_volume(tris)),
               "grounding": meshcheck.grounding(printed)}
        report["parts"].append(row)
        C.export_binary(out / f"{face}-{pid}.stl", [obj], turn)
        print(json.dumps(row), flush=True)
    if face in ("blank", "link_lid", "three_pixels", "sector_flag"):
        for i, pid in enumerate(("key_l", "key_r")):
            keys = interface["mount"]["keys"]
            angle = keys["release_rotation_deg"] * (-1 if i == 0 else 1)
            pivot = (*keys["release_pivot_uv_mm"][i], 0)
            turn = rotation((0, 0, 1), angle, pivot)
            path = [translation(0, 0, -distance) @ turn for distance in np.linspace(40, 0, 161)]
            path += [rotation((0, 0, 1), a, pivot) for a in np.linspace(angle, 0, 21)]
            contacts = [meter.common(solids[pid], matrix, solids["panel"], np.eye(4))[0] for matrix in path]
            row = {"face": face, "key": pid, "samples": len(path), "max_panel_mm3": max(contacts),
                   "contact_samples": sum(v > VOLUME_FLOOR_MM3 for v in contacts)}
            report["key_paths"].append(row)
            print(json.dumps(row), flush=True)

temporary = out / "report.json.tmp"
temporary.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
json.loads(temporary.read_text(encoding="utf-8"))
temporary.replace(out / "report.json")
if any(not r["topology"]["pass"] or r["components"] != 1 for r in report["parts"]):
    raise RuntimeError("v2 mount topology failed")
if any(r["contact_samples"] for r in report["key_paths"]):
    raise RuntimeError("v2 key path intersects panel")
print("V2_MOUNT_PROBE_PASS", flush=True)
