"""C4格子の貫通六角穴が支柱で塞がれていないことを実STLで検査する。

Blender --background --python-exit-code 1 --python tools/lattice_hole_clearance.py -- mystery-box-sg92r-c4
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "mystery-box-sg92r-c4"
MODEL_DIR = ROOT / "models" / MODEL_ID
BUILD = MODEL_DIR / "build"
sys.path.insert(0, str(ROOT / "lib"))


class Mesh:
    def __init__(self, vertices, triangles, name):
        self.vertices = [Vector(vertex) for vertex in vertices]
        self.triangles = triangles
        self.name = name


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_params():
    spec = importlib.util.spec_from_file_location("c4_hole_params", MODEL_DIR / "params.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_stl(path, name):
    raw = path.read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + count * 50:
        raise ValueError(f"binary STL expected: {path}")
    vertices = []
    triangles = []
    indices = {}
    offset = 84
    for _ in range(count):
        values = struct.unpack_from("<12fH", raw, offset)
        offset += 50
        face = []
        for vertex in (values[3:6], values[6:9], values[9:12]):
            key = tuple(vertex)
            if key not in indices:
                indices[key] = len(vertices)
                vertices.append(key)
            face.append(indices[key])
        triangles.append(tuple(face))
    return Mesh(vertices, triangles, name)


def polygon(flat, center=(0.0, 0.0), count=6):
    radius = flat / math.sqrt(3.0)
    return [
        (center[0] + radius * math.cos(math.radians(30 + 360 * index / count)),
         center[1] + radius * math.sin(math.radians(30 + 360 * index / count)))
        for index in range(count)
    ]


def prism_mesh(points, z0, z1, name):
    count = len(points)
    vertices = [(x, y, z0) for x, y in points] + [(x, y, z1) for x, y in points]
    triangles = []
    for index in range(1, count - 1):
        triangles.append((0, index + 1, index))
        triangles.append((count, count + index, count + index + 1))
    for index in range(count):
        nxt = (index + 1) % count
        triangles.extend(((index, nxt, count + nxt), (index, count + nxt, count + index)))
    return Mesh(vertices, triangles, name)


def ring_mesh(outer, inner, z0, z1, name):
    count = len(outer)
    vertices = ([(x, y, z0) for x, y in outer] + [(x, y, z1) for x, y in outer] +
                [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in inner])
    ob, ot, ib, it = 0, count, count * 2, count * 3
    triangles = []
    for index in range(count):
        nxt = (index + 1) % count
        triangles.extend((
            (ob + index, ob + nxt, ot + nxt), (ob + index, ot + nxt, ot + index),
            (ib + index, it + nxt, ib + nxt), (ib + index, it + index, it + nxt),
            (ot + index, ot + nxt, it + nxt), (ot + index, it + nxt, it + index),
            (ob + index, ib + nxt, ob + nxt), (ob + index, ib + index, ib + nxt),
        ))
    return Mesh(vertices, triangles, name)


def cylinder_mesh(center, radius, z0, z1, count, name):
    return prism_mesh([
        (center[0] + radius * math.cos(2 * math.pi * index / count),
         center[1] + radius * math.sin(2 * math.pi * index / count))
        for index in range(count)
    ], z0, z1, name)


def object_from_mesh(mesh, name):
    data = bpy.data.meshes.new(name)
    data.from_pydata([tuple(vertex) for vertex in mesh.vertices], [], mesh.triangles)
    data.update()
    probe = bmesh.new()
    probe.from_mesh(data)
    bad_edges = sum(not edge.is_manifold for edge in probe.edges)
    probe.free()
    if bad_edges:
        bpy.data.meshes.remove(data)
        raise ValueError(f"{name}: input is not closed, bad_edges={bad_edges}")
    ob = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(ob)
    return ob


def common_volume(first, second):
    objects = [object_from_mesh(first, "hole_exact_a"), object_from_mesh(second, "hole_exact_b")]
    bpy.ops.object.select_all(action="DESELECT")
    modifier = objects[0].modifiers.new("intersection", "BOOLEAN")
    modifier.operation = "INTERSECT"
    modifier.solver = "MANIFOLD"
    modifier.object = objects[1]
    bpy.context.view_layer.objects.active = objects[0]
    objects[0].select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm = bmesh.new()
        bm.from_mesh(objects[0].data)
        from solid_volume import closed_boundary_volume
        volume = closed_boundary_volume(bm)
        bm.free()
    finally:
        for ob in objects:
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data.users == 0:
                bpy.data.meshes.remove(data)
    return round(volume, 9)


def centers(params):
    groups = {0: [], 1: [], 2: []}
    pitch = params.HEX_PITCH * 1000
    for q in range(-2, 3):
        for r in range(-2, 3):
            ring = max(abs(q), abs(r), abs(-q - r))
            if ring <= 2:
                groups[ring].append((pitch * (q + r / 2), pitch * math.sqrt(3) * r / 2))
    for group in groups:
        groups[group].sort(key=lambda point: math.atan2(point[1], point[0]))
    return groups


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("model", nargs="?", choices=(MODEL_ID,), default=MODEL_ID)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    assert args.model == MODEL_ID
    params = load_params()
    hole_z0 = params.HOLE_CLEAR_Z0 * 1000
    hole_z1 = params.HOLE_CLEAR_Z1 * 1000
    hole_flat = params.HEX_HOLE_FLAT * 1000
    outer_flat = params.STEM_OUTER_FLAT * 1000
    fixture_hole = prism_mesh(polygon(hole_flat), hole_z0, hole_z1, "fixture_hole")
    angle = math.radians(30)
    old_center = (4.2 * math.cos(angle), 4.2 * math.sin(angle))
    old_stem = cylinder_mesh(old_center, params.STEM_D * 500,
                             hole_z0, params.HEX_HOME_TOP * 1000, 28, "old_stem")
    empty_ring = ring_mesh(polygon(outer_flat), polygon(hole_flat),
                           hole_z0, hole_z1, "empty_hole")
    calibration = {
        "old_unclipped_stem_common_volume_mm3": common_volume(old_stem, fixture_hole),
        "empty_hole_common_volume_mm3": common_volume(empty_ring, fixture_hole),
    }
    calibration["pass"] = (
        calibration["old_unclipped_stem_common_volume_mm3"] > 0.001 and
        calibration["empty_hole_common_volume_mm3"] <= 0.001
    )

    carrier_paths = {
        0: BUILD / "carrier_center.stl",
        1: BUILD / "carrier_inner.stl",
        2: BUILD / "carrier_outer.stl",
    }
    carriers = {group: read_stl(path, path.stem) for group, path in carrier_paths.items()}
    holes = []
    for group, group_centers in centers(params).items():
        for index, center in enumerate(group_centers):
            cutter = prism_mesh(polygon(hole_flat, center), hole_z0, hole_z1,
                                f"hole_{group}_{index}")
            measured = common_volume(carriers[group], cutter)
            holes.append({
                "group": group,
                "index": index,
                "center_mm": [round(value, 6) for value in center],
                "common_volume_mm3": measured,
                "pass": measured <= 0.001,
            })

    source_paths = [Path(__file__), MODEL_DIR / "model.py", MODEL_DIR / "params.py",
                    *carrier_paths.values()]
    report = {
        "schemaVersion": 1,
        "model": MODEL_ID,
        "method": "MANIFOLD Boolean common volume in binary assembly STL coordinates",
        "common_volume_limit_mm3": 0.001,
        "dimensions_mm": {
            "stem_diameter": params.STEM_D * 1000,
            "stem_center_radius": 4.2,
            "stem_outer_clip_flat": outer_flat,
            "hole_flat": hole_flat,
            "hole_clear_z": [hole_z0, hole_z1],
            "effective_flat_wall": (outer_flat - hole_flat) / 2,
            "faceplate_opening_flat": params.HEX_OPEN_FLAT * 1000,
            "faceplate_radial_clearance": (params.HEX_OPEN_FLAT - params.STEM_OUTER_FLAT) * 500,
        },
        "calibration": calibration,
        "holes": holes,
        "maximum_common_volume_mm3": max(row["common_volume_mm3"] for row in holes),
        "source_sha256": {path.relative_to(ROOT).as_posix(): sha256(path) for path in source_paths},
    }
    report["pass"] = calibration["pass"] and all(row["pass"] for row in holes)
    output = BUILD / "hole_clearance.json"
    write_json(output, report)
    print(json.dumps({
        "output": output.relative_to(ROOT).as_posix(),
        "pass": report["pass"],
        "holes": len(holes),
        "maximum_common_volume_mm3": report["maximum_common_volume_mm3"],
        "calibration": calibration,
    }, ensure_ascii=False))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
