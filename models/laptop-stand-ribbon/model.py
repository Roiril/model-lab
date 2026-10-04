"""使用姿勢の底を下にして造形できる、一体型リボンスタンドを作る。"""
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(HERE))

import bpy
import bmesh
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from blender_utils import clear_scene, export_stl
from params import *

OUT = ROOT / "exports" / MODEL_NAME


def load_overrides():
    path = os.environ.get("MODEL_PARAMS_JSON")
    allowed = {"LENGTH", "HEIGHT", "FOOT_WIDTH", "RAIL_WIDTH",
               "LIP_RISE", "LIP_LENGTH"}
    if path:
        values = json.loads(Path(path).read_text(encoding="utf-8"))
        for key in allowed & values.keys():
            value = float(values[key])
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{key} must be a positive finite length")
            globals()[key] = value
    if LIP_LENGTH >= LENGTH / 2 or LIP_RISE >= HEIGHT / 5:
        raise ValueError("Lip dimensions are outside the supported printable range")


def lerp(a, b, t):
    return a + (b - a) * t


def densify(points, step, closed=False):
    result = []
    count = len(points) if closed else len(points) - 1
    for i in range(count):
        a, b = points[i], points[(i + 1) % len(points)]
        divisions = max(1, math.ceil(math.dist(a, b) / step))
        result.extend((lerp(a[0], b[0], j / divisions),
                       lerp(a[1], b[1], j / divisions))
                      for j in range(divisions))
    if not closed:
        result.append(points[-1])
    return result


def chaikin_open(points, rounds=3):
    """端点を保った角切りで後側のS字輪郭を滑らかにする。"""
    result = list(points)
    for _ in range(rounds):
        refined = [result[0]]
        for a, b in zip(result, result[1:]):
            refined.append((lerp(a[0], b[0], .25), lerp(a[1], b[1], .25)))
            refined.append((lerp(a[0], b[0], .75), lerp(a[1], b[1], .75)))
        refined.append(result[-1])
        result = refined
    return result


def cubic_bezier(start, control1, control2, end, count=24):
    result = []
    for i in range(count + 1):
        t = i / count
        u = 1 - t
        result.append((u**3 * start[0] + 3*u*u*t * control1[0]
                       + 3*u*t*t * control2[0] + t**3 * end[0],
                       u**3 * start[1] + 3*u*u*t * control1[1]
                       + 3*u*t*t * control2[1] + t**3 * end[1]))
    return result


def smoothstep5(value):
    value = max(0.0, min(1.0, value))
    return value**3 * (10 - 15 * value + 6 * value * value)


def upper_surface():
    points = []
    y0, y1 = .026 * LENGTH / .280, .263 * LENGTH / .280
    count = max(2, math.ceil((y1 - y0) / boundary_step))
    for i in range(count + 1):
        y = lerp(y0, y1, i / count)
        base_y = y * .280 / LENGTH
        lip_start = .263 - LIP_LENGTH * .280 / LENGTH
        rise = smoothstep5((base_y - lip_start) / (LIP_LENGTH * .280 / LENGTH))
        z = (.152 - .177 * (base_y - .012)) * HEIGHT / .152
        points.append((y, z + LIP_RISE * rise))
    return points


def contours():
    sy, sz = LENGTH / .280, HEIGHT / .152
    rear = [(-.008 * sy, 0.0), (.004 * sy, .015 * sz),
            (.030 * sy, .045 * sz), (.036 * sy, .065 * sz),
            (.015 * sy, .100 * sz), (0.0, .125 * sz),
            (.002 * sy, .140 * sz)]
    rear = densify(chaikin_open(rear), boundary_step)
    top = upper_surface()
    crest = (.015 * sy, .152 * sz)
    shoulder1 = cubic_bezier(rear[-1], (.002 * sy, .149 * sz),
                             (.008 * sy, .152 * sz), crest)
    end = top[0]
    end_control = (.022 * sy, end[1] + .004 * .177 * sz)
    shoulder2 = cubic_bezier(crest, (.019 * sy, .152 * sz), end_control, end)
    rear.extend(shoulder1[1:])
    rear.extend(shoulder2[1:])
    outer = [rear[0], (.272 * sy, 0.0), top[-1]]
    outer.extend(reversed(top[:-1]))
    outer.extend(reversed(rear[1:-1]))
    outer = densify(outer, boundary_step, closed=True)

    apex = (.155 * sy, .104 * sz)
    right, left = (.230 * sy, .018 * sz), (.080 * sy, .018 * sz)
    centre_y = (left[0] + right[0]) / 2
    radius_y = (right[0] - left[0]) / 2
    bowl = [(centre_y + radius_y * math.cos(math.pi * i / 48),
             .018 * sz - .006 * sz * math.sin(math.pi * i / 48))
            for i in range(49)]
    hole = densify([apex, right], boundary_step)
    hole.extend(densify(bowl, boundary_step)[1:])
    hole.extend(densify([left, apex], boundary_step)[1:-1])
    return outer, hole


def point_in_polygon(point, polygon):
    y, z = point
    inside = False
    previous = polygon[-1]
    for current in polygon:
        y1, z1 = previous
        y2, z2 = current
        if (z1 > z) != (z2 > z):
            crossing = (y2 - y1) * (z - z1) / (z2 - z1) + y1
            if y < crossing:
                inside = not inside
        previous = current
    return inside


def triangulate_section(outer, hole):
    coords = [Vector(point) for point in outer + hole]
    constraints = [(i, (i + 1) % len(outer)) for i in range(len(outer))]
    offset = len(outer)
    constraints += [(offset + i, offset + (i + 1) % len(hole))
                    for i in range(len(hole))]
    min_y, max_y = min(p[0] for p in outer), max(p[0] for p in outer)
    max_z = max(p[1] for p in outer)
    y_count = math.ceil((max_y - min_y) / triangulation_step)
    z_count = math.ceil(max_z / triangulation_step)
    for zi in range(1, z_count):
        z = zi * max_z / z_count
        shift = (zi % 2) * triangulation_step / 2
        for yi in range(y_count):
            y = min_y + shift + (yi + .5) * (max_y - min_y) / y_count
            point = (y, z)
            if point_in_polygon(point, outer) and not point_in_polygon(point, hole):
                coords.append(Vector(point))
    result = delaunay_2d_cdt(coords, constraints, [], 0, 1e-9)
    vertices = [(float(v.x), float(v.y)) for v in result[0]]
    triangles = []
    for face in result[2]:
        if len(face) != 3:
            continue
        centre = (sum(vertices[i][0] for i in face) / 3,
                  sum(vertices[i][1] for i in face) / 3)
        if point_in_polygon(centre, outer) and not point_in_polygon(centre, hole):
            triangles.append(tuple(face))
    if not triangles:
        raise ValueError("Constrained triangulation produced no solid faces")
    return vertices, triangles


def half_width(y, z):
    rail, foot = RAIL_WIDTH / 2, FOOT_WIDTH / 2
    # The floor is widest near the middle and narrows organically at both ends.
    normalized = min(1.0, abs(y / LENGTH - .5) / .5)
    variation = 1.0 - .30 * normalized**1.7
    top_decay = math.exp(-HEIGHT / .035)
    taper = max(0.0, (math.exp(-z / .035) - top_decay) / (1 - top_decay))
    return rail + (foot - rail) * taper * variation


def continuous_body():
    outer, hole = contours()
    section_vertices, triangles = triangulate_section(outer, hole)
    vertices = []
    for y, z in section_vertices:
        width = half_width(y, z)
        vertices.extend(((-width, y, z), (width, y, z)))
    faces, smooth_faces = [], []
    edge_counts = Counter()
    for a, b, c in triangles:
        faces.append((2*a, 2*c, 2*b))
        smooth_faces.append(len(faces) - 1)
        faces.append((2*a+1, 2*b+1, 2*c+1))
        smooth_faces.append(len(faces) - 1)
        edge_counts.update(tuple(sorted(edge)) for edge in ((a, b), (b, c), (c, a)))
    for (a, b), count in edge_counts.items():
        if count == 1:
            faces.append((2*a, 2*b, 2*b+1, 2*a+1))

    mesh = bpy.data.meshes.new("Continuous printable ribbon")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(MODEL_NAME, mesh)
    bpy.context.collection.objects.link(obj)
    for index in smooth_faces:
        mesh.polygons[index].use_smooth = True
    return obj


def validate(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    remaining, components = set(bm.verts), 0
    while remaining:
        components += 1
        pending = [remaining.pop()]
        while pending:
            vertex = pending.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in remaining:
                    remaining.remove(other)
                    pending.append(other)
    overhang_area = worst_overhang = 0.0
    downward_faces = 0
    for face in bm.faces:
        on_floor = all(abs(vertex.co.z) < 1e-7 for vertex in face.verts)
        if on_floor or face.normal.z >= -1e-8:
            continue
        downward_faces += 1
        angle = math.degrees(math.asin(min(1.0, -face.normal.z)))
        worst_overhang = max(worst_overhang, angle)
        if angle > overhang_limit_deg + 1e-4:
            overhang_area += face.calc_area()
    stats = {
        "vertices": len(bm.verts), "triangles": len(bm.faces),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
        "zero_area_faces": sum(face.calc_area() < 1e-16 for face in bm.faces),
        "components": components,
        "volume_cm3": round(abs(bm.calc_volume(signed=True)) * 1e6, 3),
        "downward_faces_checked": downward_faces,
        "maximum_downward_overhang_deg": round(worst_overhang, 4),
        "over_45deg_area_mm2": round(overhang_area * 1e6, 6),
        "overhang_limit_deg": overhang_limit_deg,
        "design_overhang_deg": design_overhang_deg,
    }
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    bpy.context.view_layer.update()
    stats["dimensions_mm"] = [round(v * 1000, 3) for v in obj.dimensions]
    stats["bottom_z_mm"] = round(min(v.co.z for v in obj.data.vertices) * 1000, 6)
    if (components != 1 or stats["non_manifold_edges"] or stats["zero_area_faces"]
            or stats["volume_cm3"] <= 0 or stats["over_45deg_area_mm2"] > 0):
        raise ValueError(stats)
    return stats


def main():
    load_overrides()
    clear_scene()
    OUT.mkdir(parents=True, exist_ok=True)
    obj = continuous_body()
    stats = validate(obj)
    stats["design"] = "One continuous wall with a pointed teardrop through-hole"
    export_stl(MODEL_NAME, only=[obj])
    (OUT / "build.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
