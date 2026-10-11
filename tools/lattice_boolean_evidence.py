"""格子箱C3/C4のSTL閉鎖性と自己交差を検査する。

Blender --background --python-exit-code 1 --python tools/lattice_boolean_evidence.py -- all
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
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
MODELS = {
    "c3": ROOT / "models" / "mystery-box-sg92r-c3",
    "c4": ROOT / "models" / "mystery-box-sg92r-c4",
}
GEOMETRY_TOLERANCE_MM = 1e-7


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def read_stl(path):
    raw = Path(path).read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + count * 50:
        raise ValueError(f"Invalid binary STL: {path}")
    dtype = np.dtype([("normal", "<f4", 3), ("vertex", "<f4", (3, 3)), ("attr", "<u2")])
    return np.frombuffer(raw, dtype=dtype, offset=84, count=count)["vertex"].astype(float)


def polygon_area_2d(points):
    return sum(a[0] * b[1] - a[1] * b[0]
               for a, b in zip(points, np.roll(points, -1, axis=0))) / 2


def cross_2d(first, second):
    return first[0] * second[1] - first[1] * second[0]


def convex_intersection_area_2d(subject, clipping, tolerance=GEOMETRY_TOLERANCE_MM):
    subject = list(subject if polygon_area_2d(subject) >= 0 else subject[::-1])
    clipping = clipping if polygon_area_2d(clipping) >= 0 else clipping[::-1]
    for clip_a, clip_b in zip(clipping, np.roll(clipping, -1, axis=0)):
        source = subject
        subject = []
        if not source:
            break
        for current, previous in zip(source, source[-1:] + source[:-1]):
            edge = clip_b - clip_a
            current_side = cross_2d(edge, current - clip_a)
            previous_side = cross_2d(edge, previous - clip_a)
            current_inside = current_side >= -tolerance
            previous_inside = previous_side >= -tolerance
            if current_inside != previous_inside:
                delta = current - previous
                denominator = cross_2d(delta, edge)
                if abs(denominator) > tolerance:
                    factor = cross_2d(clip_a - previous, edge) / denominator
                    subject.append(previous + factor * delta)
            if current_inside:
                subject.append(current)
    return abs(polygon_area_2d(np.asarray(subject))) if len(subject) >= 3 else 0.0


def point_in_triangle(point, triangle, tolerance=GEOMETRY_TOLERANCE_MM):
    a, b, c = triangle
    v0, v1, v2 = c - a, b - a, point - a
    dot00, dot01, dot02 = np.dot(v0, v0), np.dot(v0, v1), np.dot(v0, v2)
    dot11, dot12 = np.dot(v1, v1), np.dot(v1, v2)
    denominator = dot00 * dot11 - dot01 * dot01
    if abs(denominator) <= tolerance:
        return False
    u = (dot11 * dot02 - dot01 * dot12) / denominator
    v = (dot00 * dot12 - dot01 * dot02) / denominator
    return u >= -tolerance and v >= -tolerance and u + v <= 1 + tolerance


def triangle_intersection(first, second, tolerance=GEOMETRY_TOLERANCE_MM):
    normal_a = np.cross(first[1] - first[0], first[2] - first[0])
    normal_b = np.cross(second[1] - second[0], second[2] - second[0])
    length_a, length_b = np.linalg.norm(normal_a), np.linalg.norm(normal_b)
    if length_a <= tolerance or length_b <= tolerance:
        return {"kind": "degenerate", "proper": False}
    normal_a, normal_b = normal_a / length_a, normal_b / length_b
    if np.linalg.norm(np.cross(normal_a, normal_b)) <= tolerance and abs(
            np.dot(normal_a, second[0] - first[0])) <= tolerance:
        axis = int(np.argmax(np.abs(normal_a)))
        area = convex_intersection_area_2d(
            np.delete(first, axis, axis=1), np.delete(second, axis, axis=1), tolerance)
        return {"kind": "coplanar", "proper": area > tolerance,
                "overlapAreaMm2": float(area)}
    hits = []
    for triangle, other, normal in ((first, second, normal_b), (second, first, normal_a)):
        for start, end in zip(triangle, np.roll(triangle, -1, axis=0)):
            delta = end - start
            denominator = np.dot(normal, delta)
            if abs(denominator) <= tolerance:
                continue
            factor = np.dot(normal, other[0] - start) / denominator
            if -tolerance <= factor <= 1 + tolerance:
                point = start + factor * delta
                if point_in_triangle(point, other, tolerance) and not any(
                        np.linalg.norm(point - known) <= tolerance for known in hits):
                    hits.append(point)
    length = float(np.linalg.norm(hits[1] - hits[0])) if len(hits) >= 2 else 0.0
    return {"kind": "transverse", "proper": len(hits) >= 2,
            "intersectionLengthMm": length, "pointsMm": [point.tolist() for point in hits[:2]]}


def indexed_mesh(triangles):
    vertices, index = np.unique(triangles.reshape(-1, 3), axis=0, return_inverse=True)
    return vertices, index.reshape(-1, 3)


def self_intersections(vertices, faces):
    tree = BVHTree.FromPolygons(vertices.tolist(), faces.tolist(), all_triangles=True)
    rows = []
    for first_index, second_index in tree.overlap(tree):
        if first_index >= second_index:
            continue
        if set(map(int, faces[first_index])) & set(map(int, faces[second_index])):
            continue
        measured = triangle_intersection(vertices[faces[first_index]], vertices[faces[second_index]])
        if measured["proper"]:
            rows.append({"triangles": [int(first_index), int(second_index)], **measured})
    return rows


def inspect_triangles(triangles):
    vertices, faces = indexed_mesh(triangles)
    directed = {}
    undirected = {}
    for face in faces:
        for a, b in zip(face, np.roll(face, -1)):
            a, b = int(a), int(b)
            directed[(a, b)] = directed.get((a, b), 0) + 1
            edge = tuple(sorted((a, b)))
            undirected[edge] = undirected.get(edge, 0) + 1
    edges_not_twice = sum(count != 2 for count in undirected.values())
    same_direction = sum(count == 2 and (directed.get(edge, 0) != 1 or
                                         directed.get(edge[::-1], 0) != 1)
                         for edge, count in undirected.items())
    duplicate_faces = len(faces) - len({tuple(sorted(map(int, face))) for face in faces})
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    area = np.linalg.norm(cross, axis=1) / 2
    signed_volume = float(np.einsum(
        "ij,ij->i", triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])).sum() / 6)
    intersections = self_intersections(vertices, faces)
    topologically_watertight = edges_not_twice == 0 and same_direction == 0
    geometry_valid = (not intersections and duplicate_faces == 0 and
                      not np.any(area <= 1e-12) and signed_volume > 0)
    return {
        "vertices": len(vertices), "triangles": len(faces), "edges": len(undirected),
        "edgesNotUsedTwice": edges_not_twice,
        "sharedEdgesWithSameDirection": same_direction,
        "duplicateTriangles": duplicate_faces,
        "zeroAreaTriangles": int(np.count_nonzero(area <= 1e-12)),
        "minimumTriangleAreaMm2": float(area.min()) if len(area) else None,
        "signedVolumeMm3": signed_volume,
        "outwardOriented": signed_volume > 0,
        "topologicallyWatertight": topologically_watertight,
        "properNonadjacentIntersections": len(intersections),
        "intersectionExamples": intersections[:20],
        "geometryValidClosedSolid": topologically_watertight and geometry_valid,
    }


def inspect_path(path):
    if not path.exists():
        return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "exists": False}
    triangles = read_stl(path)
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "exists": True,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        **inspect_triangles(triangles),
    }


def calibration():
    crossing = np.asarray([
        [[0., 0., 0.], [2., 0., 0.], [0., 2., 0.]],
        [[.5, -.5, -1.], [.5, 1.5, 1.], [.5, 1.5, -1.]],
    ])
    shared_edge = np.asarray([
        [[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]],
        [[1., 0., 0.], [1., 1., 0.], [0., 1., 0.]],
    ])
    plane_touch = triangle_intersection(
        np.asarray([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]]),
        np.asarray([[1., 0., 0.], [2., 0., 0.], [1., 1., 0.]]))
    crossing_count = len(self_intersections(*indexed_mesh(crossing)))
    shared_count = len(self_intersections(*indexed_mesh(shared_edge)))
    return [
        {"id": "transverse-intersection", "pass": crossing_count == 1,
         "detail": {"measuredProperIntersections": crossing_count, "expected": 1}},
        {"id": "shared-edge", "pass": shared_count == 0,
         "detail": {"measuredProperIntersections": shared_count, "expected": 0}},
        {"id": "coplanar-edge-contact", "pass": not plane_touch["proper"],
         "detail": {"measurement": plane_touch, "expectedProperIntersection": False}},
    ]


def mesh_data(name, triangles):
    vertices, faces = indexed_mesh(triangles)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices.tolist(), [], faces.tolist())
    mesh.update()
    return mesh


def boolean_result(data_a, data_b, travel, solver):
    from solid_volume import closed_boundary_volume
    left = bpy.data.objects.new("evidence_moving", data_a.copy())
    right = bpy.data.objects.new("evidence_fixed", data_b)
    bpy.context.collection.objects.link(left)
    bpy.context.collection.objects.link(right)
    left.matrix_world = Matrix.Translation((travel, 0, 0))
    bpy.context.view_layer.objects.active = left
    modifier = left.modifiers.new("evidence_common", "BOOLEAN")
    modifier.operation = "INTERSECT"
    modifier.solver = solver
    modifier.object = right
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm = bmesh.new()
        bm.from_mesh(left.data)
        try:
            nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
            try:
                volume, error = closed_boundary_volume(bm), None
            except ValueError as caught:
                volume, error = None, str(caught)
            return {"vertices": len(bm.verts), "faces": len(bm.faces),
                    "nonmanifoldEdges": nonmanifold,
                    "closedBoundaryVolumeMm3": volume, "error": error}
        finally:
            bm.free()
    finally:
        copied = left.data
        bpy.data.objects.remove(left, do_unlink=True)
        bpy.data.objects.remove(right, do_unlink=True)
        bpy.data.meshes.remove(copied)


def c3_shaft_cap_probe(model_dir, params):
    shaft_path, cap_path = model_dir / "build/camshaft.stl", model_dir / "build/cap_right.stl"
    shaft_triangles, cap_triangles = read_stl(shaft_path), read_stl(cap_path)
    shaft, cap = mesh_data("evidence_camshaft", shaft_triangles), mesh_data("evidence_cap", cap_triangles)
    try:
        solvers = {solver: boolean_result(shaft, cap, .25, solver)
                   for solver in ("EXACT", "MANIFOLD")}
    finally:
        bpy.data.meshes.remove(shaft)
        bpy.data.meshes.remove(cap)
    cap_inner = (params.SHAFT_MAIN_X + params.AXIAL_PLAY / 2) * 1000
    keyed_end = params.SHAFT_MAIN_X * 1000 + .25
    hex_area = math.sqrt(3) / 2 * (params.SHAFT_AF * 1000) ** 2
    bore_area = 24 * (params.CAP_BORE_D * 500) ** 2 * math.sin(math.pi / 24)
    penetration = max(0.0, keyed_end - cap_inner)
    return {
        "id": "shaft-plus", "servoDeg": params.SERVO_HOME_DEG,
        "rotationDeg": 0.0, "travelMm": .25, "direction": [1, 0, 0],
        "sourceStlSha256": {
            "moving": hashlib.sha256(shaft_path.read_bytes()).hexdigest(),
            "fixed": hashlib.sha256(cap_path.read_bytes()).hexdigest(),
        },
        "independentSection": {
            "capMaterialStartsXmm": cap_inner,
            "shiftedShaftKeyedEndXmm": keyed_end,
            "constantHexAxialPenetrationMm": penetration,
            "shaftHexAreaMm2": hex_area,
            "capBore48GonAreaMm2": bore_area,
            "materialOverlapAreaMm2": hex_area - bore_area,
            "volumeLowerBoundMm3": penetration * (hex_area - bore_area),
        },
        "solvers": solvers,
    }


def load_params(model_dir):
    spec = importlib.util.spec_from_file_location("boolean_evidence_params", model_dir / "params.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def model_report(model_id):
    model_dir = MODELS[model_id]
    manifest = json.loads((model_dir / "build/manifest.json").read_text(encoding="utf-8"))
    assembly, printable = [], []
    for part in manifest["parts"]:
        assembly.append({"id": part["id"], **inspect_path(model_dir / part["assembly"])})
        if part.get("print"):
            printable.append({"id": part["id"], **inspect_path(model_dir / part["print"])})
    delivered_dir = ROOT / "prints" / model_dir.name
    delivered = [inspect_path(path) for path in sorted(delivered_dir.glob("*.stl"))]
    calibrations = calibration()
    report = {
        "schemaVersion": 1,
        "model": model_dir.name,
        "algorithmSha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), ROOT / "lib/solid_volume.py")
        },
        "method": {
            "coordinates": "binary STL float32 vertices in mm; no coordinate rounding",
            "topology": "exact shared vertices; each undirected edge must have two opposite directed uses",
            "selfIntersection": "BVH candidates; shared-vertex pairs excluded; triangle intersection must have nonzero line length or coplanar area",
            "geometryToleranceMm": GEOMETRY_TOLERANCE_MM,
        },
        "calibration": calibrations,
        "assemblyStls": assembly,
        "printStls": printable,
        "deliveredPrintStls": delivered,
        "shaftCapProbe": c3_shaft_cap_probe(model_dir, load_params(model_dir)) if model_id == "c3" else None,
    }
    all_rows = assembly + printable + delivered
    report["summary"] = {
        "calibrationPass": all(row["pass"] for row in calibrations),
        "filesChecked": len(all_rows),
        "missingFiles": sum(not row["exists"] for row in all_rows),
        "invalidClosedSolids": sum(row.get("exists") and not row.get("geometryValidClosedSolid")
                                   for row in all_rows),
        "properNonadjacentIntersections": sum(row.get("properNonadjacentIntersections", 0)
                                               for row in all_rows),
    }
    output = model_dir / "build/boolean_evidence.json"
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=json_default),
                         encoding="utf-8", newline="\n")
    os.replace(temporary, output)
    return output, report["summary"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model", nargs="?", choices=("c3", "c4", "all"), default="all")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    selected = MODELS if args.model == "all" else {args.model: MODELS[args.model]}
    results = []
    for model_id in selected:
        output, summary = model_report(model_id)
        results.append({"model": model_id, "output": str(output), **summary})
    print(json.dumps(results, ensure_ascii=False, default=json_default))
    if any(not row["calibrationPass"] or row["missingFiles"] or row["invalidClosedSolids"]
           or row["properNonadjacentIntersections"] for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
