"""Measure isolated v2 skeleton parts with the production mesh and solid meters."""
import importlib.util
import itertools
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


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


C = load("v2_frame_compose", HERE / "compose.py")
F = load("v2_frame_candidate", HERE / "frame.py")
interface = C.read(HERE / "build/v2-mount-interface.json")
fragment = C.read(HERE / "build/v2-frame-interface.json")
interface["mount_geometry"].update(fragment["mount_geometry"])
interface["frame"] = fragment["frame"]
out = HERE / "build/v2-service-probe"
out.mkdir(exist_ok=True)
report = {"parts": [], "static_intersections": [], "paths": [], "retention": []}
common = C.common_params()
built = F.build(interface, common, include_services=True)
solids = {}
meter = Meter()
for pid, desc in built.items():
    if False:
        continue
    obj = desc["object"]
    C.clean_object(obj)
    obj.data.calc_loop_triangles()
    tris = np.asarray([[list(obj.data.vertices[i].co) for i in t.vertices]
                       for t in obj.data.loop_triangles], dtype=float)
    solids[pid] = Solid(pid, tris)
    turn = np.array(desc["print_rotation"], dtype=float)
    printed = tris @ turn[:3, :3].T
    turn[2, 3] = -printed[:, :, 2].min()
    printed += turn[:3, 3]
    row = {"part": pid, "topology": meshcheck.topology(tris),
           "components": len(meshcheck.components(tris)),
           "volume_mm3": abs(meshcheck.signed_volume(tris)),
           "grounding": meshcheck.grounding(printed)}
    report["parts"].append(row)
    C.export_binary(out / f"{pid}.stl", [obj], turn)
    print(json.dumps(row), flush=True)
for a, b in itertools.combinations(solids, 2):
    volume, _ = meter.common(solids[a], np.eye(4), solids[b], np.eye(4))
    if volume > VOLUME_FLOOR_MM3:
        row = {"a": a, "b": b, "volume_mm3": volume}
        report["static_intersections"].append(row)
        print(json.dumps(row), flush=True)
placed = set()
for step in F.assembly_steps(interface, common, include_services=True):
    moving = [pid for pid in step["moving"] if pid in solids]
    if not moving:
        continue
    hits = []
    for frame in step["frames"]:
        for a in moving:
            for b in placed:
                if a.startswith("post_") or a == "upper_frame" and b.startswith("post_"):
                    continue  # Post spring insertion is measured by the scoped snap allowance in mechgate.
                volume, _ = meter.common(solids[a], frame[a], solids[b], np.eye(4))
                if volume > VOLUME_FLOOR_MM3:
                    hits.append({"moving": a, "static": b, "volume_mm3": volume})
    row = {"step": step["id"], "contact_samples": len(hits), "first_hit": hits[:1]}
    report["paths"].append(row)
    print(json.dumps(row), flush=True)
    placed.update(moving)
for definition in F.interfaces(interface, common, include_services=True):
    if False:
        continue
    pid = definition["parts"][0]
    direction = np.asarray(definition["direction"], dtype=float)
    first = None
    for distance in np.arange(0.025, 0.551, 0.025):
        move = np.eye(4)
        move[:3, 3] = direction * distance
        if any(meter.common(solids[pid], move, solids[other], np.eye(4))[0] > VOLUME_FLOOR_MM3
               for other in solids if other != pid):
            first = round(float(distance), 4)
            break
    row = {"id": definition["id"], "first_collision_mm": first}
    report["retention"].append(row)
    print(json.dumps(row), flush=True)
temporary = out / "report.json.tmp"
temporary.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
json.loads(temporary.read_text(encoding="utf-8"))
temporary.replace(out / "report.json")
failed = any(not row["topology"]["pass"] or row["components"] != 1 for row in report["parts"])
failed |= bool(report["static_intersections"])
failed |= any(row["contact_samples"] for row in report["paths"])
failed |= any(row["first_collision_mm"] is None or row["first_collision_mm"] > 0.5 for row in report["retention"])
print("V2_FRAME_PROBE_PASS=" + str(not failed), flush=True)
sys.exit(1 if failed else 0)
