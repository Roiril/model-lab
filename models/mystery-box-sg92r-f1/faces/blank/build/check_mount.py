"""Local deterministic smoke check; full model certification belongs to certify.py."""
import importlib.util
import json
from pathlib import Path
import sys

import bmesh
import bpy
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parents[3]


def load(name, filename, package=False):
    spec = importlib.util.spec_from_file_location(name, filename,
                                                submodule_search_locations=[str(filename.parent)] if package else None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


params = load("f1_smoke_params", HERE / "params.py")
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from tools.mechgate_lib import meshcheck
from printmech.solid_meter import Solid, Meter, VOLUME_FLOOR_MM3
frame = load("f1_smoke_frame", HERE / "frame.py")
blank = load("f1_smoke_blank", HERE / "faces/blank/geometry.py", True)
interface = json.loads((HERE / "interface.json").read_text(encoding="utf-8"))
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
parts = frame.build(interface, params)
parts.update({f"blank/{name}": descriptor for name, descriptor in blank.build(interface, params).items()})
failed = False
for name, descriptor in parts.items():
    obj = descriptor["object"]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    visited = set()
    components = 0
    for vertex in bm.verts:
        if vertex in visited:
            continue
        components += 1
        pending = [vertex]
        visited.add(vertex)
        while pending:
            current = pending.pop()
            for edge in current.link_edges:
                neighbor = edge.other_vert(current)
                if neighbor not in visited:
                    visited.add(neighbor)
                    pending.append(neighbor)
    volume = abs(bm.calc_volume(signed=True))
    bm.free()
    bounds = [[min(v.co[i] for v in obj.data.vertices), max(v.co[i] for v in obj.data.vertices)] for i in range(3)]
    obj.data.calc_loop_triangles()
    triangles = np.array([[list(obj.data.vertices[i].co) for i in t.vertices] for t in obj.data.loop_triangles], dtype=np.float32).astype(float)
    triangle_topology = meshcheck.topology(triangles)
    if triangle_topology.get("degenerateTriangles"):
        cross = np.linalg.norm(np.cross(triangles[:,1]-triangles[:,0], triangles[:,2]-triangles[:,0]), axis=1)
        print(json.dumps({"part": name, "degenerate": triangles[cross <= 1e-12].tolist()}))
    if components != 1:
        for comp in meshcheck.components(triangles):
            lo, hi = meshcheck.bounds(triangles[comp])
            print(json.dumps({"part": name, "component_triangles": len(comp), "component_bounds": [lo.tolist(), hi.tolist()]}))
    print(json.dumps({"part": name, "triangles": triangle_topology}, ensure_ascii=False))
    print(json.dumps({"part": name, "nonmanifold": nonmanifold, "components": components,
                      "volume_mm3": round(volume, 5), "bounds_mm": bounds}, ensure_ascii=False))
    failed |= nonmanifold != 0 or components != 1 or volume <= 0 or not triangle_topology["pass"]
if failed:
    raise RuntimeError("Mount smoke check failed")
print("MOUNT_SMOKE_PASS")

world_parts = {name: descriptor for name, descriptor in parts.items() if not name.startswith("blank/")}
for slot, matrix in interface["slot_transforms_mm"].items():
    for name, descriptor in blank.build(interface, params).items():
        descriptor["object"].data.transform(__import__("mathutils").Matrix(matrix))
        world_parts[f"{slot}/{name}"] = descriptor
solids = {}
for name, descriptor in world_parts.items():
    mesh = descriptor["object"].data
    mesh.calc_loop_triangles()
    triangles = np.array([[list(mesh.vertices[i].co) for i in face.vertices] for face in mesh.loop_triangles], dtype=np.float32).astype(float)
    solids[name] = Solid(name, triangles)
meter = Meter()
names = list(solids)
violations = []
for i, name in enumerate(names):
    for other in names[i+1:]:
        volume, locations = meter.common(solids[name], np.eye(4), solids[other], np.eye(4))
        if volume > VOLUME_FLOOR_MM3:
            violations.append({"parts": [name,other], "mm3": volume, "locations": locations})
print(json.dumps({"static_violations": violations}, ensure_ascii=False))
if violations:
    raise RuntimeError("Static mount interference")
print("MOUNT_STATIC_PASS")

state = {}
assembly_rows = []
for step in frame.assembly_steps(interface, params):
    maxima = {}
    for index, transforms in enumerate(step["frames"]):
        present = {**state, **transforms}
        for moving in step["moving"]:
            for fixed in present:
                if moving == fixed or fixed in step["moving"]:
                    continue
                volume, locations = meter.common(solids[moving], present[moving], solids[fixed], present[fixed])
                if volume > VOLUME_FLOOR_MM3:
                    key = (moving, fixed)
                    row = maxima.setdefault(key, {"parts": list(key), "max_mm3": 0, "remaining_mm": [], "locations": []})
                    row["max_mm3"] = max(row["max_mm3"], volume)
                    row["remaining_mm"].append(float(np.linalg.norm(transforms[moving][:3,3])))
                    row["locations"] = locations
    state.update(step["frames"][-1])
    for row in maxima.values():
        row["remaining_mm"] = [min(row["remaining_mm"]), max(row["remaining_mm"])]
    assembly_rows.append({"step": step["id"], "contacts": list(maxima.values())})
print(json.dumps({"frame_assembly_contacts": assembly_rows}, ensure_ascii=False))
