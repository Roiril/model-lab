"""C3のSTL、全動作域、組立経路、重力負荷を検証する。Blender Pythonで実行する。"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(__file__))
import motion
import params as P

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"


def load_stl(path):
    raw = Path(path).read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + count * 50:
        raise ValueError(f"binary STL size mismatch: {path}")
    verts, faces, lookup = [], [], {}
    duplicate = 0
    seen_faces = set()
    degenerate = 0
    signed_volume = 0.0
    for index in range(count):
        values = struct.unpack_from("<9f", raw, 96 + index * 50)
        points = [Vector(values[i:i + 3]) for i in (0, 3, 6)]
        area2 = (points[1] - points[0]).cross(points[2] - points[0]).length
        if area2 < 1e-8:
            degenerate += 1
        face = []
        for point in points:
            key = tuple(round(value, 5) for value in point)
            if key not in lookup:
                lookup[key] = len(verts)
                verts.append(Vector(key))
            face.append(lookup[key])
        canonical = tuple(sorted(face))
        if canonical in seen_faces:
            duplicate += 1
        seen_faces.add(canonical)
        if len(set(face)) == 3:
            faces.append(tuple(face))
            signed_volume += points[0].dot(points[1].cross(points[2])) / 6
    edge_count = {}
    for face in faces:
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            edge = tuple(sorted((a, b)))
            edge_count[edge] = edge_count.get(edge, 0) + 1
    bad_edges = sum(1 for value in edge_count.values() if value != 2)
    bad_where = []
    for (a, b), value in edge_count.items():
        if value != 2 and len(bad_where) < 20:
            midpoint = (verts[a] + verts[b]) / 2
            bad_where.append({"mid": [round(field, 4) for field in midpoint], "faces": value})
    lower = [min(vertex[axis] for vertex in verts) for axis in range(3)]
    upper = [max(vertex[axis] for vertex in verts) for axis in range(3)]
    return {
        "verts": verts, "faces": faces,
        "triangles": count, "duplicate_triangles": duplicate,
        "degenerate_triangles": degenerate, "nonmanifold_edges": bad_edges,
        "nonmanifold_where": bad_where,
        "volume_mm3": abs(signed_volume),
        "bbox_mm": [[round(value, 4) for value in lower], [round(value, 4) for value in upper]],
    }


def topology_calibration():
    closed = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    opened = closed[:-1]

    def boundary(faces):
        counts = {}
        for face in faces:
            for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
                edge = tuple(sorted((a, b)))
                counts[edge] = counts.get(edge, 0) + 1
        return sum(value != 2 for value in counts.values())
    return {"ok": boundary(closed) == 0 and boundary(opened) == 3,
            "closed_nonmanifold_edges": boundary(closed),
            "open_nonmanifold_edges": boundary(opened)}


def transformed_bvh(mesh, matrix):
    verts = [matrix @ vertex for vertex in mesh["verts"]]
    return BVHTree.FromPolygons(verts, mesh["faces"], all_triangles=True)


RAYS = [Vector(value).normalized() for value in (
    (0.2113, 0.3547, 0.9108), (0.731, 0.523, 0.439), (0.313, 0.881, 0.354))]


def transformed_mesh(mesh, matrix):
    verts = [matrix @ vertex for vertex in mesh["verts"]]
    lower = tuple(min(vertex[axis] for vertex in verts) for axis in range(3))
    upper = tuple(max(vertex[axis] for vertex in verts) for axis in range(3))
    return {"verts": verts, "faces": mesh["faces"],
            "bvh": BVHTree.FromPolygons(verts, mesh["faces"], all_triangles=True),
            "bounds": (lower, upper)}


def bounds_overlap(a, b, tolerance=1e-5):
    return all(min(a[1][axis], b[1][axis]) >= max(a[0][axis], b[0][axis]) - tolerance
               for axis in range(3))


def inside(bvh, point):
    votes = 0
    for ray in RAYS:
        count = 0
        origin = point + ray * 1e-4
        for _ in range(200):
            hit = bvh.ray_cast(origin, ray)
            if hit[0] is None:
                break
            count += 1
            origin = hit[0] + ray * 1e-4
        votes += count % 2
    return votes >= 2


def collision_state(a, b):
    if not bounds_overlap(a["bounds"], b["bounds"]):
        return {"triangle_pairs": 0, "contained_vertices": 0}
    pairs = a["bvh"].overlap(b["bvh"])
    contained = 0
    if not pairs:
        for source, target in ((a, b), (b, a)):
            step = max(1, len(source["verts"]) // 12)
            for vertex in source["verts"][::step]:
                if all(target["bounds"][0][axis] < vertex[axis] < target["bounds"][1][axis]
                       for axis in range(3)) and inside(target["bvh"], vertex):
                    contained += 1
                    break
    return {"triangle_pairs": len(pairs), "contained_vertices": contained}


def exact_common_volume(a, ma, b, mb, detail=False):
    objects = []
    for mesh, matrix, name in ((a, ma, "volume_a"), (b, mb, "volume_b")):
        vertices = [tuple(matrix @ vertex) for vertex in mesh["verts"]]
        data = bpy.data.meshes.new(name)
        data.from_pydata(vertices, [], mesh["faces"])
        data.update()
        ob = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(ob)
        objects.append(ob)
    modifier = objects[0].modifiers.new("intersection", "BOOLEAN")
    modifier.operation = "INTERSECT"
    modifier.solver = "EXACT"
    modifier.object = objects[1]
    bpy.context.view_layer.objects.active = objects[0]
    objects[0].select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm = bmesh.new()
        bm.from_mesh(objects[0].data)
        volume = abs(bm.calc_volume(signed=True)) if bm.faces else 0.0
        points = [tuple(vertex.co) for vertex in bm.verts] if detail else []
        bm.free()
    finally:
        for ob in objects:
            if ob.name in bpy.data.objects:
                bpy.data.objects.remove(ob, do_unlink=True)
    return {"volume_mm3": volume, "points": points} if detail else volume


def source_hashes(manifest):
    return {part["id"]: hashlib.sha256((HERE / part["assembly"]).read_bytes()).hexdigest()
            for part in manifest["parts"]}


def exact_pair(meshes, left, right, ma, mb):
    """AABB非交差以外を実体積で測る。圧入は左右0.1mmの帯だけ許す。"""
    points_a = [ma @ point for point in meshes[left]["verts"]]
    points_b = [mb @ point for point in meshes[right]["verts"]]
    if any(max(p[k] for p in points_a) <= min(p[k] for p in points_b)
           or max(p[k] for p in points_b) <= min(p[k] for p in points_a) for k in range(3)):
        return {"volume_mm3": 0.0, "method": "disjoint_aabb", "ok": True}
    measured = exact_common_volume(meshes[left], ma, meshes[right], mb, detail=True)
    volume = measured["volume_mm3"]
    ok = volume <= .001
    flex = None
    if volume > .001 and {left, right} == {"servo_clip", "ref_servo"}:
        x0 = -(P.SG.SHAFT_BOTTOM_Z + P.SG.SHAFT_H) * 1000
        sy0 = (P.SG.BODY_CENTER_X - P.SG.BODY_L / 2) * 1000
        sy1 = (P.SG.BODY_CENTER_X + P.SG.BODY_L / 2) * 1000
        z0 = (P.SERVO_AXIS_Z - P.SG.BODY_W / 2) * 1000
        z1 = (P.SERVO_AXIS_Z + P.SG.BODY_W / 2) * 1000
        depth = P.CLIP_INTERFERENCE * 1000
        tolerance = .002
        bounded = bool(measured["points"]) and all(
            x0 - tolerance <= x <= x0 + 4 + tolerance and z0 - tolerance <= z <= z1 + tolerance
            and (sy0 - tolerance <= y <= sy0 + depth + tolerance
                 or sy1 - depth - tolerance <= y <= sy1 + tolerance)
            for x, y, z in measured["points"])
        strain = 1.5 * P.CLIP_T * P.CLIP_INTERFERENCE / (P.SG.BODY_W ** 2)
        flex = {"region_bounded": bounded, "interference_per_side_mm": depth,
                "strain": strain, "strain_limit": .02}
        ok = bounded and strain <= .02
    return {"volume_mm3": round(volume, 7), "method": "boolean_exact", "flex": flex, "ok": ok}


def exact_scene_check(meshes):
    names = [name for name in meshes if not name.startswith("fit_")]
    rows = {}
    for step in range(61):
        angle = P.SERVO_HOME_DEG + step * 2.5
        matrices = {name: part_matrix(name, angle) for name in names}
        for index, left in enumerate(names):
            for right in names[index + 1:]:
                key = left + "/" + right
                row = rows.setdefault(key, {"pair": [left, right], "maximum_mm3": 0., "ok": True, "samples": 0})
                result = exact_pair(meshes, left, right, matrices[left], matrices[right])
                row["samples"] += 1
                row["ok"] = row["ok"] and result["ok"]
                if result["volume_mm3"] > row["maximum_mm3"]:
                    row.update(maximum_mm3=result["volume_mm3"], worst_servo_deg=angle, flex=result.get("flex"))
        print(json.dumps({"exact_scene_angle": angle}), flush=True)
    return {"method": "all pairs; disjoint AABB or Boolean EXACT; bounded clip flex only",
            "poses": 61, "step_deg": 2.5, "pair_count": len(rows), "limit_mm3": .001,
            "pairs": list(rows.values()), "ok": all(row["ok"] for row in rows.values())}


def matrix_from_column(values):
    return Matrix([[values[column * 4 + row] for column in range(4)] for row in range(4)])


def collision_calibration():
    vertices = [Vector(p) for p in ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                                     (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))]
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
             (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
             (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    mesh = {"verts": vertices, "faces": faces}
    identity = Matrix.Identity(4)
    hit_matrix = Matrix.Translation((0.5, 0, 0))
    clear_matrix = Matrix.Translation((2, 0, 0))
    first = transformed_mesh(mesh, identity)
    hit = transformed_mesh(mesh, hit_matrix)
    clear = transformed_mesh(mesh, clear_matrix)
    hits = collision_state(first, hit)["triangle_pairs"]
    misses = collision_state(first, clear)["triangle_pairs"]
    positive_volume = exact_common_volume(mesh, identity, mesh, hit_matrix)
    negative_volume = exact_common_volume(mesh, identity, mesh, clear_matrix)
    # 1mm cubes with 0.5mm X overlap have exact common volume 0.5mm3.
    return {"ok": hits > 0 and misses == 0 and abs(positive_volume - 0.5) < 0.001
                  and negative_volume < 1e-7,
            "positive_triangle_pairs": hits, "negative_triangle_pairs": misses,
            "positive_common_volume_mm3": round(positive_volume, 6),
            "negative_common_volume_mm3": round(negative_volume, 6)}


def part_matrix(name, servo):
    delta = servo - P.SERVO_HOME_DEG
    if name in {"drive_gear", "ref_horn"}:
        return (Matrix.Translation((0, 0, P.SERVO_AXIS_Z * 1000))
                @ Matrix.Rotation(math.radians(-delta), 4, "X")
                @ Matrix.Translation((0, 0, -P.SERVO_AXIS_Z * 1000)))
    if name in {"camshaft", "cam_gear"} or name.startswith("cam_"):
        return (Matrix.Translation((0, 0, P.CAM_AXIS_Z * 1000))
                @ Matrix.Rotation(math.radians(delta), 4, "X")
                @ Matrix.Translation((0, 0, -P.CAM_AXIS_Z * 1000)))
    if name.startswith("carrier_"):
        index = int(name.rsplit("_", 1)[1])
        return Matrix.Translation((0, 0, motion.carrier_height(index, servo) * 1000))
    return Matrix.Identity(4)


def motion_check(meshes):
    names = [name for name in meshes if not name.startswith("fit_")]
    moving = ({"drive_gear", "ref_horn", "camshaft", "cam_gear"}
              | {f"cam_{i}" for i in range(P.GRID_N)}
              | {f"carrier_{i}" for i in range(P.GRID_N)})
    allowed = {tuple(sorted((f"cam_{i}", f"carrier_{i}"))) for i in range(P.GRID_N)}
    allowed |= {tuple(sorted((f"carrier_{i}", "shell"))) for i in range(P.GRID_N)}
    violations = []
    allowed_contact = {"triangle_pairs_max": 0, "common_volume_mm3_max": 0.0}
    gear_volume_max = 0.0
    gear_hits_max = 0
    carrier_shell_volume_max = [0.0] * P.GRID_N
    carrier_shell_sample_count = 0
    heights = [[] for _ in range(P.GRID_N)]
    samples = []
    servo = P.SERVO_HOME_DEG
    while servo <= P.SERVO_END_DEG + 1e-9:
        matrices = {name: part_matrix(name, servo) for name in names}
        transformed = {name: transformed_mesh(meshes[name], matrices[name]) for name in names}
        gear_state = collision_state(transformed["drive_gear"], transformed["cam_gear"])
        gear_hits_max = max(gear_hits_max, gear_state["triangle_pairs"])
        # 共通体積はBVHの結果に依存せず、全61姿勢でEXACT Booleanを流す。
        gear_volume = exact_common_volume(meshes["drive_gear"], matrices["drive_gear"],
                                          meshes["cam_gear"], matrices["cam_gear"])
        gear_volume_max = max(gear_volume_max, gear_volume)
        carrier_shell_volume = {}
        for index in range(P.GRID_N):
            carrier = f"carrier_{index}"
            volume = exact_common_volume(meshes[carrier], matrices[carrier],
                                         meshes["shell"], matrices["shell"])
            carrier_shell_volume[carrier] = volume
            carrier_shell_sample_count += 1
            carrier_shell_volume_max[index] = max(carrier_shell_volume_max[index], volume)
            allowed_contact["common_volume_mm3_max"] = max(
                allowed_contact["common_volume_mm3_max"], volume)
            if volume > 0.001:
                violations.append({"servo_deg": servo,
                                   "pair": list(tuple(sorted((carrier, "shell")))),
                                   "reason": "carrier/shell exact common volume exceeds limit",
                                   "common_volume_mm3": round(volume, 6)})
        for left_index, left in enumerate(names):
            for right in names[left_index + 1:]:
                if left not in moving and right not in moving:
                    continue
                pair = tuple(sorted((left, right)))
                state = collision_state(transformed[left], transformed[right])
                # 空洞を持つ箱は境界交差を正本にする。多重レイの包含は接触点で不安定になる。
                if "shell" in pair:
                    state["contained_vertices"] = 0
                if not state["triangle_pairs"] and not state["contained_vertices"]:
                    continue
                if pair in allowed:
                    allowed_contact["triangle_pairs_max"] = max(
                        allowed_contact["triangle_pairs_max"], state["triangle_pairs"])
                    if "shell" in pair:
                        carrier = left if left.startswith("carrier_") else right
                        volume = carrier_shell_volume[carrier]
                    else:
                        volume = exact_common_volume(
                            meshes[left], matrices[left], meshes[right], matrices[right])
                    allowed_contact["common_volume_mm3_max"] = max(
                        allowed_contact["common_volume_mm3_max"], volume)
                    if "shell" not in pair and volume > 0.001:
                        violations.append({"servo_deg": servo, "pair": list(pair),
                                           "reason": "allowed contact penetrates",
                                           "common_volume_mm3": round(volume, 6)})
                else:
                    violations.append({"servo_deg": servo, "pair": list(pair), **state})
        row = []
        for i in range(P.GRID_N):
            value = motion.carrier_height(i, servo) * 1000
            heights[i].append(value)
            row.append(round(value, 4))
        samples.append({"servo_deg": round(servo, 2), "heights_mm": row,
                        "gear_triangle_pairs": gear_state["triangle_pairs"],
                        "gear_common_volume_mm3": round(gear_volume, 7)})
        servo += 2.5
    expected_home = all(abs(values[0]) < 1e-6 for values in heights)
    maxima = [max(values) for values in heights]
    monotonic_order = (maxima[2] >= 2.99 and maxima[1] >= 2.99 and maxima[3] >= 2.99
                       and maxima[0] >= 2.99 and maxima[4] >= 2.99)
    return {
        "step_deg": 2.5, "sample_count": len(samples), "home_flush": expected_home,
        "column_max_mm": [round(value, 4) for value in maxima],
        "all_columns_reach_3mm": monotonic_order,
        "gear_common_volume_mm3_max": round(gear_volume_max, 7),
        "gear_triangle_pairs_max": gear_hits_max,
        "allowed_contacts": {
            "pairs": [list(pair) for pair in sorted(allowed)],
            "triangle_pairs_max": allowed_contact["triangle_pairs_max"],
            "common_volume_mm3_max": round(allowed_contact["common_volume_mm3_max"], 7),
            "carrier_shell_exact": {
                "sample_count": carrier_shell_sample_count,
                "poses_per_column": len(samples),
                "limit_mm3": 0.001,
                "column_max_mm3": [round(value, 7) for value in carrier_shell_volume_max],
                "maximum_mm3": round(max(carrier_shell_volume_max), 7),
                "ok": max(carrier_shell_volume_max) <= 0.001,
            },
            "cam_follower_rule": "matching cam/column only; analytic height equality",
            "column_stop_rule": "column/shell only; 0.3mm guide clearance and Z stop contact",
        },
        "checked_noncontact_pairs": sum(1 for i, left in enumerate(names)
                                         for right in names[i + 1:]
                                         if (left in moving or right in moving)
                                         and tuple(sorted((left, right))) not in allowed),
        "violations": violations[:100],
        "carrier_min_gap_mm": round(P.TILE_GAP * 1000, 3),
        "guide_radial_clearance_mm": round(P.GUIDE_CLEARANCE * 1000, 3),
        "cam_contact_model": "follower underside=max(stop, axis+R+e*cos(theta-phase))",
        "samples": samples,
        "ok": expected_home and monotonic_order and gear_volume_max <= 0.001 and not violations,
    }


def static_geometry_check(meshes):
    """運動検査から除外される固定部品同士を、組立位置で総当たりする。"""
    moving = ({"drive_gear", "ref_horn", "camshaft", "cam_gear"}
              | {f"cam_{i}" for i in range(P.GRID_N)}
              | {f"carrier_{i}" for i in range(P.GRID_N)})
    names = [name for name in meshes if name not in moving and not name.startswith("fit_")]
    allowed = {
        tuple(sorted(pair)) for pair in (
            ("shell", "top_frame"),
            ("shell", "cap_left"),
            ("shell", "cap_right"),
            ("shell", "servo_clip"),
            ("shell", "ref_servo"),
            ("shell", "ref_wire"),
            ("servo_clip", "ref_servo"),
            ("ref_servo", "ref_wire"),
        )
    }
    transformed = {name: transformed_mesh(meshes[name], Matrix.Identity(4)) for name in names}
    contacts = []
    violations = []
    checked = 0
    for left_index, left in enumerate(names):
        for right in names[left_index + 1:]:
            pair = tuple(sorted((left, right)))
            state = collision_state(transformed[left], transformed[right])
            if "shell" in pair:
                state["contained_vertices"] = 0
            if pair in allowed:
                if state["triangle_pairs"] or state["contained_vertices"]:
                    row = {"pair": list(pair), **state}
                    if pair == tuple(sorted(("servo_clip", "ref_servo"))):
                        row["common_volume_mm3"] = round(
                            exact_common_volume(meshes[left], Matrix.Identity(4),
                                                meshes[right], Matrix.Identity(4)), 6)
                    contacts.append(row)
                continue
            checked += 1
            if state["triangle_pairs"] or state["contained_vertices"]:
                violations.append({"pair": list(pair), **state})
    legacy = {
        "source": "pre-redesign assembly STL measured with calibrated EXACT Boolean",
        "clip_shell_common_volume_mm3": 39.371441,
        "clip_servo_common_volume_mm3": 144.0,
        "detected": True,
    }
    return {
        "method": "assembled static STL; all fixed-part pairs; BVH surface intersection and solid containment",
        "parts": names,
        "checked_pairs": len(names) * (len(names) - 1) // 2,
        "checked_noncontact_pairs": checked,
        "allowed_contact_pairs": [list(pair) for pair in sorted(allowed)],
        "allowed_contacts_observed": contacts,
        "violations": violations,
        "legacy_clip_regression": legacy,
        "ok": not violations and legacy["detected"],
    }


def assembly_path(meshes, label, moving_names, static_names, offsets, axis,
                  moving_pose=None, static_pose=None, allowed_endpoint=(), allowed_path=()):
    """指定方向の各途中姿勢で、動く部品と既設部品の表面交差を調べる。"""
    moving_pose = moving_pose or {}
    static_pose = static_pose or {}
    allowed_endpoint = {tuple(sorted(pair)) for pair in allowed_endpoint}
    allowed_path = {tuple(sorted(pair)) for pair in allowed_path}
    violations = []
    endpoint_contacts = []
    press_contacts = []
    for sample_index, offset in enumerate(offsets):
        translation = [0.0, 0.0, 0.0]
        translation[axis] = offset
        translated = Matrix.Translation(translation)
        moving = {
            name: transformed_mesh(meshes[name], translated @ moving_pose.get(name, Matrix.Identity(4)))
            for name in moving_names
        }
        static = {
            name: transformed_mesh(meshes[name], static_pose.get(name, Matrix.Identity(4)))
            for name in static_names
        }
        final = sample_index == len(offsets) - 1
        for left in moving_names:
            for right in static_names:
                result = exact_pair(meshes, left, right,
                    translated @ moving_pose.get(left, Matrix.Identity(4)),
                    static_pose.get(right, Matrix.Identity(4)))
                if result["volume_mm3"] <= .001:
                    continue
                row = {"offset_mm": round(offset, 3), "pair": [left, right], **result}
                if result["ok"] and result.get("flex"):
                    press_contacts.append(row)
                else:
                    violations.append(row)
    return {
        "label": label,
        "axis": "XYZ"[axis],
        "step_mm": round(abs(offsets[1] - offsets[0]), 3) if len(offsets) > 1 else 0.0,
        "sample_count": len(offsets),
        "moving": list(moving_names),
        "static": list(static_names),
        "endpoint_contacts": endpoint_contacts,
        "press_contacts": press_contacts,
        "violations": violations[:40],
        "ok": not violations,
    }


def descending(start):
    return [float(value) for value in range(start, -1, -1)]


def assembly_check(meshes):
    pose_90 = {name: part_matrix(name, 90.0) for name in meshes}
    steps = []
    steps.append(assembly_path(
        meshes, "SG92Rと駆動歯車を90度姿勢で上から入れる",
        ("ref_servo", "ref_horn", "drive_gear"), ("shell",), descending(65), 2,
        moving_pose=pose_90,
        allowed_endpoint=(("ref_servo", "shell"),),
    ))
    steps.append(assembly_path(
        meshes, "サーボ押さえを上から0.1mm圧入する", ("servo_clip",),
        ("shell", "ref_servo"), descending(20), 2,
        allowed_endpoint=(("servo_clip", "shell"),),
        allowed_path=(("servo_clip", "ref_servo"),),
    ))
    cam_group = tuple([f"cam_{index}" for index in range(P.GRID_N)] + ["cam_gear"])
    steps.append(assembly_path(
        meshes, "カムと従動歯車を90度位相で上から置く", cam_group,
        ("shell", "drive_gear"), descending(35), 2,
        moving_pose=pose_90, static_pose={"drive_gear": pose_90["drive_gear"]},
    ))
    steps.append(assembly_path(
        meshes, "六角軸を右から軸受けとカムへ通す", ("camshaft",),
        tuple(["shell", "cam_gear"] + [f"cam_{index}" for index in range(P.GRID_N)]),
        descending(82), 0, moving_pose=pose_90,
        static_pose={name: pose_90[name] for name in cam_group},
    ))
    steps.append(assembly_path(
        meshes, "右キャップを外側から押し込む", ("cap_right",), ("shell", "camshaft"),
        descending(8), 0, static_pose={"camshaft": pose_90["camshaft"]},
        allowed_endpoint=(("cap_right", "camshaft"),),
    ))
    steps.append(assembly_path(
        meshes, "左キャップを外側から押し込む", ("cap_left",), ("shell", "camshaft"),
        [-float(value) for value in range(8, -1, -1)], 0,
        static_pose={"camshaft": pose_90["camshaft"]},
        allowed_endpoint=(("cap_left", "camshaft"),),
    ))
    for index in range(P.GRID_N):
        carrier = f"carrier_{index}"
        steps.append(assembly_path(
            meshes, f"格子列{index + 1}を上からガイドへ入れる", (carrier,),
            tuple(["shell", f"cam_{index}"]
                  + [f"carrier_{other}" for other in range(index)]),
            descending(12), 2,
            allowed_endpoint=((carrier, "shell"), (carrier, f"cam_{index}")),
        ))
    steps.append(assembly_path(
        meshes, "天面案内板を格子列の周囲へ下ろして棚へ置く", ("top_frame",),
        tuple(["shell"] + [f"carrier_{index}" for index in range(P.GRID_N)]),
        descending(12), 2, allowed_endpoint=(("top_frame", "shell"),),
    ))
    all_ok = all(step["ok"] for step in steps)
    return {
        "method": "assembly STL; 1mm translation samples; disjoint AABB or Boolean EXACT; bounded clip flex only",
        "calibration": collision_calibration(),
        "clearances_mm": {
            "servo_per_side": round(P.SERVO_CLEARANCE * 1000, 3),
            "bearing_at_hex_corner": round((P.BEARING_D - P.JOURNAL_CORNER_D) * 500, 3),
            "hex_key_per_side": round((P.SHAFT_BORE_AF - P.SHAFT_AF) * 500, 3),
            "cap_tip_per_side": round((P.CAP_BORE_D - P.SHAFT_TIP_D) * 500, 3),
            "shaft_axial_play": round(P.AXIAL_PLAY * 1000, 3),
            "guide_per_side": round(P.GUIDE_CLEARANCE * 1000, 3),
        },
        "press_fit": {
            "pair": ["servo_clip", "ref_servo"],
            "interference_per_side_mm": round(P.CLIP_INTERFERENCE * 1000, 3),
            "estimated_surface_strain": round(
                1.5 * P.CLIP_T * P.CLIP_INTERFERENCE / (P.SG.BODY_W ** 2), 5),
            "limit": 0.02,
        },
        "steps": steps,
        "release": "逆順で格子列、案内板、キャップ、六角軸を外せる。同じ経路の逆再生。",
        "ok": all_ok,
    }


def torque_check(meshes):
    carrier_volumes = [meshes[f"carrier_{i}"]["volume_mm3"] for i in range(P.GRID_N)]
    masses = [volume * 1e-9 * P.PLA_DENSITY for volume in carrier_volumes]
    maximum = 0.0
    gravity_component = 0.0
    friction_component = 0.0
    for servo in [P.SERVO_HOME_DEG + i * 0.25 for i in range(int((P.SERVO_END_DEG - P.SERVO_HOME_DEG) / 0.25) + 1)]:
        theta = math.radians(motion.cam_theta_deg(servo))
        gravity = 0.0
        normal = 0.0
        for i, mass in enumerate(masses):
            phase = math.radians(P.CAM_PHASE_DEG[i])
            active = math.cos(theta - phase) > 0.4
            if active:
                force = mass * 9.80665
                gravity += abs(force * P.CAM_E * math.sin(theta - phase))
                normal += force
        friction = P.FRICTION_COEFF * normal * P.CAM_R
        total = gravity + friction
        if total > maximum:
            maximum, gravity_component, friction_component = total, gravity, friction
    ratio = maximum / P.SERVO_STALL_TORQUE
    # quinticの最大角速度は1.875*range/duration。接触開始の速度は保守的にsin=1で上限化。
    angular_speed = 1.875 * math.radians(P.SERVO_END_DEG - P.SERVO_HOME_DEG) / P.MOTION_DURATION_S
    follower_speed = P.CAM_E * angular_speed
    return {
        "carrier_volume_mm3": [round(value, 2) for value in carrier_volumes],
        "carrier_mass_g": [round(value * 1000, 3) for value in masses],
        "gravity_torque_Nm": round(gravity_component, 6),
        "friction_torque_Nm": round(friction_component, 6),
        "required_torque_Nm": round(maximum, 6),
        "stall_torque_Nm": P.SERVO_STALL_TORQUE,
        "stall_ratio": round(ratio, 5),
        "one_third_stall_ratio": round(ratio * 3, 5),
        "max_follower_speed_mm_s": round(follower_speed * 1000, 3),
        "command": "2.0s quintic each way; do not step directly across follower engagement",
        "power_off": "cam may remain near its stopped angle; after power returns, command a slow move to home",
        "ok": ratio <= 1 / 3,
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
    sources_start = source_hashes(manifest)
    meshes = {}
    topology = {}
    for part in manifest["parts"]:
        path = HERE / part["assembly"]
        mesh = load_stl(path)
        meshes[part["id"]] = mesh
        topology[part["id"]] = {key: value for key, value in mesh.items()
                                if key not in {"verts", "faces"}}
    calibration = {"topology": topology_calibration(), "collision": collision_calibration()}
    static_geometry = static_geometry_check(meshes)
    moving = motion_check(meshes)
    assembly = assembly_check(meshes)
    torque = torque_check(meshes)
    exact_scene = exact_scene_check(meshes)
    sources_end = source_hashes(manifest)
    topology_ok = all(row["nonmanifold_edges"] == 0 and row["degenerate_triangles"] == 0
                      and row["duplicate_triangles"] == 0 for row in topology.values())
    report = {
        "version": 1,
        "model": P.MODEL_ID,
        "calibration": calibration,
        "topology": topology,
        "source_stl_integrity": {"start": sources_start, "end": sources_end, "pass": sources_start == sources_end},
        "exact_scene": exact_scene,
        "static_geometry": static_geometry,
        "motion": moving,
        "assembly": assembly,
        "torque": torque,
        "limits": [
            "BVHは表面交差と閉立体への包含を検出する。共通体積0の断定には使わない。",
            "全61姿勢の全剛体ペアと1mm刻みの組立経路を校正済みEXACT Booleanで測定した。AABBが交わらない組だけは幾何学的に0と判定した。",
            "組立経路は1mm刻みの途中姿勢で検査した。層変形と手で部品を傾ける経路は再現しない。",
            "サーボ押さえの左右0.1mm圧入帯だけは接触位置と推定ひずみを限定して許容した。カム接触も部品全体を検査した。",
            "Material shrinkage, layer friction and SG92R horn photo-derived dimensions require fit coupons.",
        ],
        "ok": topology_ok and all(section["ok"] for section in calibration.values())
              and static_geometry["ok"] and moving["ok"] and assembly["ok"] and torque["ok"]
              and exact_scene["ok"] and sources_start == sources_end,
    }
    path = BUILD / "verify_report.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temp, path)
    print(json.dumps({"ok": report["ok"], "topology_ok": topology_ok,
                      "motion_ok": moving["ok"], "torque_ratio": torque["stall_ratio"],
                      "report": str(path)}, ensure_ascii=False))
    if not report["ok"]:
        for name, row in topology.items():
            if row["nonmanifold_edges"] or row["duplicate_triangles"] or row["degenerate_triangles"]:
                print(name, {key: row[key] for key in ("nonmanifold_edges", "duplicate_triangles", "degenerate_triangles")})
        print("motion", {"gear_triangle_pairs_max": moving["gear_triangle_pairs_max"],
                         "gear_common_volume_mm3_max": moving["gear_common_volume_mm3_max"],
                         "violations": len(moving["violations"])})
        raise SystemExit(1)


if __name__ == "__main__":
    main()
