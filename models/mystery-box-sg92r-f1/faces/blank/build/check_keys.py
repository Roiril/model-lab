"""Measure the actual cassette-key insertion and lock paths using solid_meter."""
import importlib.util
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parents[3]
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT))
from printmech import geometry as G
from printmech.contract import rotation, translation
from printmech.solid_meter import Solid, Meter, read_stl, VOLUME_FLOOR_MM3
from tools.mechgate_lib import meshcheck

spec = importlib.util.spec_from_file_location("f1_key_geometry", HERE / "faces/blank/geometry.py")
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)
interface = json.loads((HERE / "interface.json").read_text(encoding="utf-8"))
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
panel, key_l, key_r = geometry.build_mount(interface)


def solid(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    triangles = np.array([[list(mesh.vertices[i].co) for i in face.vertices]
                          for face in mesh.loop_triangles], dtype=np.float32).astype(float)
    topology = meshcheck.topology(triangles)
    if not topology["pass"]:
        raise RuntimeError(f"Invalid topology: {obj.name}: {topology}")
    return Solid(obj.name, triangles)


def local_reference(part):
    matrix = np.linalg.inv(np.array(interface["slot_transforms_mm"]["front"]))
    triangles = read_stl(HERE / f"build/parts/front/{part}.stl")
    triangles = triangles @ matrix[:3,:3].T + matrix[:3,3]
    return Solid(part, triangles)


def object_from_solid(reference):
    mesh = bpy.data.meshes.new(reference.name)
    mesh.from_pydata(reference.verts.tolist(), [], reference.faces.tolist())
    mesh.update()
    obj = bpy.data.objects.new(reference.name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# Apply only the new standard windows to the real, already built front panel.
front = object_from_solid(local_reference("panel"))
for row in interface["mount_geometry"]["parts"]["panel"]["operations"]:
    shape = row["shape"]
    if row["op"] == "difference" and shape["type"] == "box" and abs(shape["center_mm"][0]) == 31:
        G.cut(front, geometry.primitive(shape, "key_window"))
front.name = "front_panel"
fixed = {"blank_panel": solid(panel), "front_panel": solid(front), "front_support": local_reference("support")}
meter = Meter()
report = {"steps": [], "support_suggested_notches": []}
for index, obj in enumerate((key_l, key_r)):
    key = solid(obj)
    sign = -1 if index == 0 else 1
    angle = interface["mount"]["keys"]["release_rotation_deg"] * sign
    pivot = (*interface["mount"]["keys"]["release_pivot_uv_mm"][index], 0)
    turn = rotation((0,0,1), angle, pivot)
    paths = {
        "insert": [translation(0,0,-distance) @ turn for distance in np.linspace(40,0,161)],
        "lock": [rotation((0,0,1), degree, pivot) for degree in np.linspace(angle,0,21)],
        "release": [rotation((0,0,1), degree, pivot) for degree in np.linspace(0,angle,21)],
        "extract": [translation(0,0,-distance) @ turn for distance in np.linspace(0,40,161)]
    }
    for phase, path in paths.items():
        for fixed_name, target in fixed.items():
            contacts = []
            for progress, matrix in enumerate(path):
                volume, bounds = meter.common(key, matrix, target, np.eye(4))
                if volume > VOLUME_FLOOR_MM3:
                    contacts.append({"sample": progress, "volume_mm3": volume, "bounds_mm": bounds})
            row = {"key": obj.name, "phase": phase, "fixed": fixed_name,
                   "samples": len(path), "contact_samples": len(contacts),
                   "max_mm3": max((c["volume_mm3"] for c in contacts), default=0)}
            if contacts:
                boxes = np.array([bounds for contact in contacts for bounds in contact["bounds_mm"]])
                row["contact_union_bounds_mm"] = [boxes[:,0].min(axis=0).tolist(), boxes[:,1].max(axis=0).tolist()]
                regions = {}
                for name, mask in (("root", boxes[:,1,1] < -18), ("tip", boxes[:,0,1] > -10)):
                    subset = boxes[mask]
                    if len(subset):
                        regions[name] = [subset[:,0].min(axis=0).tolist(), subset[:,1].max(axis=0).tolist()]
                row["contact_regions_mm"] = regions
            report["steps"].append(row)
            print(json.dumps(row))
report["panel_paths_pass"] = all(row["contact_samples"] == 0 for row in report["steps"] if row["fixed"] != "front_support")
report_path = Path(__file__).with_name("key_path_report.json")
temporary = report_path.with_suffix(".json.tmp")
temporary.write_text(json.dumps(report, ensure_ascii=False, indent=1)+"\n", encoding="utf-8")
temporary.replace(report_path)
if not report["panel_paths_pass"]:
    raise RuntimeError("Key paths intersect the panel")
print("KEY_PANEL_PATHS_PASS")
