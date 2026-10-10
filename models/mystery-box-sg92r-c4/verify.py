"""C4のSTL、全動作域、組立経路、重力復帰を数値で検証する。"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../.."))
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.path.insert(0, HERE)

from mathutils import Matrix, Vector  # noqa: E402
from printmech.mesh import Mesh  # noqa: E402

import motion  # noqa: E402
import params as P  # noqa: E402

BUILD = os.path.join(HERE, "build")


def matrix_from_column_major(values):
    return Matrix([values[i:i + 4] for i in range(0, 16, 4)]).transposed()


def translation(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def topology(path):
    raw = open(path, "rb").read()
    if len(raw) < 84:
        raise ValueError(path)
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + 50 * count:
        raise ValueError(f"STL byte count mismatch: {path}")
    edges, degenerates, signed6 = {}, 0, 0.0
    parents = {}

    def root(vertex):
        parents.setdefault(vertex, vertex)
        while parents[vertex] != vertex:
            parents[vertex] = parents[parents[vertex]]
            vertex = parents[vertex]
        return vertex

    def join(a, b):
        ra, rb = root(a), root(b)
        if ra != rb:
            parents[rb] = ra
    lower = [float("inf")] * 3
    upper = [float("-inf")] * 3
    for i in range(count):
        xyz = struct.unpack_from("<9f", raw, 96 + i * 50)
        pts = [tuple(round(v, 5) for v in xyz[j:j + 3]) for j in (0, 3, 6)]
        for point in pts:
            for axis in range(3):
                lower[axis] = min(lower[axis], point[axis])
                upper[axis] = max(upper[axis], point[axis])
        a, b, c = (Vector(p) for p in pts)
        area2 = (b - a).cross(c - a).length
        if area2 < 1e-8:
            degenerates += 1
        signed6 += a.dot(b.cross(c))
        for u, v in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])):
            edge = tuple(sorted((u, v)))
            edges[edge] = edges.get(edge, 0) + 1
            join(u, v)
    bad = sum(1 for n in edges.values() if n != 2)
    components = len({root(vertex) for vertex in parents})
    return {"triangles": count, "bad_edges": bad, "degenerate_triangles": degenerates,
            "connected_components": components,
            "signed_volume_mm3": round(signed6 / 6.0, 3),
            "bounds_mm": [[round(v, 3) for v in lower], [round(v, 3) for v in upper]],
            "pass": bad == 0 and degenerates == 0 and abs(signed6) > 1e-6}


def topology_calibration():
    tris = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    def bad_edges(faces):
        edges = {}
        for face in faces:
            for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
                key = tuple(sorted((a, b)))
                edges[key] = edges.get(key, 0) + 1
        return sum(n != 2 for n in edges.values())
    closed = bad_edges(tris)
    opened = bad_edges(tris[:-1])
    def component_count(faces):
        links = {}
        def root(value):
            links.setdefault(value, value)
            if links[value] != value:
                links[value] = root(links[value])
            return links[value]
        for face in faces:
            base = root(face[0])
            for value in face[1:]:
                links[root(value)] = base
        return len({root(value) for value in links})
    one_component = component_count(tris)
    two_components = component_count(tris + [tuple(v + 4 for v in face) for face in tris])
    return {"closed_bad_edges": closed, "open_bad_edges": opened,
            "one_component_fixture": one_component, "two_component_fixture": two_components,
            "pass": closed == 0 and opened == 3 and one_component == 1 and two_components == 2}


def cube_mesh(center, size, name):
    cx, cy, cz = center
    h = size / 2
    verts = [Vector((cx + x * h, cy + y * h, cz + z * h))
             for x, y, z in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                             (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))]
    tris = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
            (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
            (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return Mesh(verts, tris, name)


def collision_calibration():
    fixed = cube_mesh((0, 0, 0), 10, "fixed")
    overlap = cube_mesh((7, 1, 1), 6, "overlap")
    clear = cube_mesh((25, 0, 0), 10, "clear")
    yes = bounded_contact(fixed, overlap)
    no = bounded_contact(fixed, clear)
    return {"overlap": yes, "clear": no,
            "pass": yes["hits"] > 0 and yes["depth"] > 0 and no["hits"] == 0 and no["depth"] == 0}


def exact_common_geometry(a, ma, b, mb, vertex_predicate=None):
    """EXACT Booleanで2メッシュの共通体積と範囲をmm単位で測る。"""
    objects = []
    for source, matrix, name in ((a, ma, "exact_a"), (b, mb, "exact_b")):
        data = bpy.data.meshes.new(name)
        data.from_pydata([tuple(matrix @ vertex) for vertex in source.v], [], source.t)
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
        if bm.verts:
            lower = [min(vertex.co[axis] for vertex in bm.verts) for axis in range(3)]
            upper = [max(vertex.co[axis] for vertex in bm.verts) for axis in range(3)]
            bounds = [[round(value, 4) for value in lower], [round(value, 4) for value in upper]]
            remaining = set(bm.verts)
            component_bounds = []
            while remaining:
                seed = remaining.pop()
                stack = [seed]
                component = [seed]
                while stack:
                    vertex = stack.pop()
                    for edge in vertex.link_edges:
                        other = edge.other_vert(vertex)
                        if other in remaining:
                            remaining.remove(other)
                            stack.append(other)
                            component.append(other)
                component_bounds.append([
                    [round(min(vertex.co[axis] for vertex in component), 4) for axis in range(3)],
                    [round(max(vertex.co[axis] for vertex in component), 4) for axis in range(3)],
                ])
            vertices_in_allowed_zone = (None if vertex_predicate is None else
                                        all(vertex_predicate(vertex.co) for vertex in bm.verts))
        else:
            bounds = None
            component_bounds = []
            vertices_in_allowed_zone = None if vertex_predicate is None else True
        bm.free()
    finally:
        for ob in objects:
            bpy.data.objects.remove(ob, do_unlink=True)
    return {"common_volume_mm3": round(volume, 6), "intersection_bounds_mm": bounds,
            "intersection_component_bounds_mm": component_bounds,
            "vertices_in_allowed_zone": vertices_in_allowed_zone}


def exact_common_volume(a, ma, b, mb):
    return exact_common_geometry(a, ma, b, mb)["common_volume_mm3"]


def exact_volume_calibration():
    cube = cube_mesh((0, 0, 0), 1.0, "exact_fixture")
    identity = Matrix.Identity(4)
    positive = exact_common_volume(cube, identity, cube, translation(x=0.5))
    negative = exact_common_volume(cube, identity, cube, translation(x=2.0))
    return {"positive_expected_mm3": 0.5,
            "positive_common_volume_mm3": round(positive, 6),
            "negative_expected_mm3": 0.0,
            "negative_common_volume_mm3": round(negative, 6),
            "pass": abs(positive - 0.5) <= 0.001 and negative <= 1e-7}


def load(name):
    return Mesh.load(os.path.join(BUILD, f"{name}.stl"), name)


def source_stl_hashes(names):
    """検証対象STLの個別SHA-256と順序付き集約SHA-256を返す。"""
    per_file = {}
    aggregate = hashlib.sha256()
    for name in names:
        path = os.path.join(BUILD, f"{name}.stl")
        with open(path, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        per_file[name] = digest
        aggregate.update(name.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\n")
    return {"aggregate_sha256": aggregate.hexdigest(), "per_file_sha256": per_file}


def bounded_contact(a, b, step=1):
    """外接箱を通った頂点だけ内外判定する。mesh.contactの外点誤検出を除く。"""
    lower_a, upper_a = a.bounds()
    lower_b, upper_b = b.bounds()
    if any(upper_a[axis] < lower_b[axis] or upper_b[axis] < lower_a[axis] for axis in range(3)):
        return {"hits": 0, "depth": 0.0}
    ba, bb = a.bvh(), b.bvh()
    pairs = ba.overlap(bb)
    max_depth = 0.0

    def inside_majority(bvh, point):
        directions = (Vector((0.2113, 0.3547, 0.9108)).normalized(),
                      Vector((0.7311, 0.2217, 0.6455)).normalized(),
                      Vector((-0.4173, 0.8061, 0.4227)).normalized())
        votes = 0
        for direction in directions:
            count, origin = 0, point.copy()
            for _ in range(120):
                hit = bvh.ray_cast(origin, direction)
                if hit[0] is None:
                    break
                count += 1
                origin = hit[0] + direction * 1e-4
            votes += count % 2
        return votes >= 2

    for mesh, other, bvh in ((a, b, bb), (b, a, ba)):
        lower, upper = other.bounds()
        for vertex in mesh.v[::step]:
            if any(vertex[i] < lower[i] - 1e-6 or vertex[i] > upper[i] + 1e-6 for i in range(3)):
                continue
            if inside_majority(bvh, vertex):
                nearest = bvh.find_nearest(vertex)
                if nearest[0] is not None:
                    max_depth = max(max_depth, nearest[3])
    return {"hits": len(pairs), "depth": round(max_depth, 3)}


def max_collision(current, a_name, a, b_name, b, servo_deg):
    result = bounded_contact(a, b, step=3)
    if result["depth"] > 0.1:
        item = {"a": a_name, "b": b_name, "servo_deg": servo_deg,
                "hits": result["hits"], "depth_mm": result["depth"]}
        if current is None or (item["depth_mm"], item["hits"]) > (current["depth_mm"], current["hits"]):
            return item
    return current


def motion_check(meshes, exact_scene):
    """全65姿勢のEXACT結果と、カム接点・案内かかり量の解析値をまとめる。"""
    min_pad_margin = 999.0
    for step in range(65):
        degree = P.SERVO_MIN_DEG + 2.5 * step
        theta = math.radians(motion.cam_theta_deg(degree))
        for ecc in P.CAM_E:
            contact_y = ecc * math.cos(theta) * 1000.0
            min_pad_margin = min(min_pad_margin, P.FOLLOWER_PAD_Y * 500.0 - abs(contact_y))
    cell_clearance = (P.HEX_OPEN_FLAT - P.HEX_CAP_FLAT) * 500.0
    guide_clearance = P.GUIDE_CLEARANCE * 1000.0
    min_engagement = (P.GUIDE_Z1 + 0.00025 - P.GUIDE_LUG_Z0
                      - motion.lift_m(0, P.SERVO_MAX_DEG)) * 1000.0
    moving_pairs = [row for row in exact_scene["pairs"] if row["pose_samples"] == 65]
    violations = [row for row in moving_pairs if not row["pass"]]
    guide_pass = cell_clearance >= 0.3 and guide_clearance >= 0.3 and min_engagement >= 2.9
    return {"step_deg": 2.5, "frames": 65, "pair_coverage": {
                "moving_candidate_pairs": len(moving_pairs),
                "all_scene_unique_pairs": exact_scene["unique_pairs"],
            }, "violations": violations,
            "follower_min_edge_margin_mm": round(min_pad_margin, 3),
            "carrier_guides": {
                "cell_clearance_per_side_mm": round(cell_clearance, 3),
                "guide_clearance_per_side_mm": round(guide_clearance, 3),
                "minimum_guide_engagement_mm": round(min_engagement, 3),
                "pass": guide_pass,
            },
            "pass": not violations and min_pad_margin >= 1.0 - 1e-6 and guide_pass}


def path_collision(moving, fixed, transforms):
    worst = None
    for index, mat in enumerate(transforms):
        result = bounded_contact(moving.moved(mat), fixed, step=3)
        if result["depth"] > 0.1:
            item = {"sample": index, "hits": result["hits"], "depth_mm": result["depth"]}
            if worst is None or (item["depth_mm"], item["hits"]) > (worst["depth_mm"], worst["hits"]):
                worst = item
    return worst


def static_geometry_check(exact_scene):
    """固定部品28組をEXACT全候補走査から抽出する。深さ許容は持たない。"""
    rows = [row for row in exact_scene["pairs"] if row["pose_samples"] == 1]
    violations = [row for row in rows if not row["pass"]]
    return {"parts": 8, "checked_pairs": len(rows), "expected_pairs": 28,
            "common_volume_limit_mm3": 0.001, "pairs": rows,
            "violations": violations,
            "pass": len(rows) == 28 and not violations}


def exact_interface_check(meshes):
    """主要な摺動部と軸受けを代表姿勢でも共通体積で再判定する。"""
    identity = Matrix.Identity(4)
    cases = (
        ("carrier_center_guide_frame", "carrier_center", 10.0, "guide_frame", None,
         "角柱案内は片側0.35mmの設計空隙。"),
        ("carrier_inner_guide_frame", "carrier_inner", 15.0, "guide_frame", None,
         "角柱案内は片側0.35mmの設計空隙。"),
        ("carrier_outer_guide_frame", "carrier_outer", 10.0, "guide_frame", None,
         "角柱案内は片側0.35mmの設計空隙。"),
        ("camshaft_housing", "camshaft", 35.0, "housing", None,
         "右軸受けは半径方向0.30mmの設計空隙。"),
        ("bearing_keeper_housing", "bearing_keeper", None, "housing", None,
         "保持爪だけが支持板の横穴へ掛かる。最終位置の本体面には貫通を設けない。"),
        ("guide_frame_servo_horn", "servo_horn", 15.0, "guide_frame", None,
         "案内枠はホーン掃引包絡の外へ置く。"),
        ("carrier_inner_outer", "carrier_inner", 120.0, "carrier_outer", 120.0,
         "3群の格子と連結腕は互いに交差しない。"),
        ("carrier_center_inner", "carrier_center", 122.5, "carrier_inner", 122.5,
         "3群の格子と連結腕は互いに交差しない。"),
        ("camshaft_guide_frame", "camshaft", 17.5, "guide_frame", None,
         "案内枠はカム軸とホーン受けの掃引包絡より上へ置く。"),
        ("bottom_housing", "bottom", None, "housing", None,
         "底板本体は片側0.3mmの空隙。保持爪は凹み内に収まる。"),
        ("servo_clip_housing", "servo_clip", None, "housing", None,
         "サーボ保持具は保持台の開口内に収まり、爪はSG92R本体だけへ掛かる。"),
        ("faceplate_guide_frame", "faceplate", None, "guide_frame", None,
         "天板保持爪には片側0.3mmの通過空隙を設ける。"),
        ("bearing_keeper_cam_outer", "bearing_keeper", None, "cam_outer", 12.5,
         "外環カムのハブ端と保持具本体の間に0.3mmの軸方向空隙を置く。"),
        ("faceplate_housing", "faceplate", None, "housing", None,
         "天板保持爪は外装の凹みに収まり、最終位置では共通体積を持たない。"),
    )
    results = {}
    for key, a_name, a_degree, b_name, b_degree, basis in cases:
        a_matrix = (identity if a_degree is None else
                    matrix_from_column_major(motion.transforms(a_degree)[a_name]))
        b_matrix = (identity if b_degree is None else
                    matrix_from_column_major(motion.transforms(b_degree)[b_name]))
        geometry = exact_common_geometry(meshes[a_name], a_matrix, meshes[b_name], b_matrix)
        results[key] = {
            "parts": [a_name, b_name],
            "servo_deg": a_degree if a_degree is not None else b_degree,
            **geometry,
            "maximum_common_volume_mm3": 0.001,
            "physical_basis": basis,
            "pass": geometry["common_volume_mm3"] <= 0.001,
        }
    return {"method": "Blender Boolean EXACT。体積校正後、主要界面の代表姿勢を再測定。",
            "interfaces": results,
            "pass": all(item["pass"] for item in results.values())}


def exact_scene_check(meshes):
    """全固定・可動候補を全姿勢で測る。AABB共通範囲が0の姿勢だけBooleanを省略する。"""
    static_ids = ("housing", "faceplate", "guide_frame", "bottom", "bearing_keeper",
                  "servo_clip", "servo_body", "servo_wire")
    moving_ids = ("camshaft", "horn_coupler", "cam_center", "cam_inner", "cam_outer", "servo_horn",
                  "carrier_center", "carrier_inner", "carrier_outer")
    all_ids = static_ids + moving_ids
    reference_ids = {"servo_body", "servo_horn", "servo_wire"}
    identity = Matrix.Identity(4)
    pairs = {}
    for step in range(65):
        degree = P.SERVO_MIN_DEG + 2.5 * step
        transforms = motion.transforms(degree)
        matrices = {
            name: (matrix_from_column_major(transforms[name]) if name in moving_ids else identity)
            for name in all_ids
        }
        bounds = {name: meshes[name].moved(matrices[name]).bounds() for name in all_ids}
        for index, a_name in enumerate(all_ids):
            for b_name in all_ids[index + 1:]:
                if step > 0 and a_name in static_ids and b_name in static_ids:
                    continue
                key = tuple(sorted((a_name, b_name)))
                row = pairs.setdefault(key, {
                    "parts": list(key),
                    "classification": ("sg_reference_internal" if a_name in reference_ids
                                           and b_name in reference_ids else "printed_or_mixed"),
                    "pose_samples": 0,
                    "aabb_zero_samples": 0,
                    "exact_samples": 0,
                    "maximum_common_volume_mm3": 0.0,
                    "maximum_at_servo_deg": None,
                    "intersection_bounds_mm": None,
                })
                row["pose_samples"] += 1
                lower_a, upper_a = bounds[a_name]
                lower_b, upper_b = bounds[b_name]
                if any(upper_a[axis] <= lower_b[axis] or upper_b[axis] <= lower_a[axis]
                       for axis in range(3)):
                    row["aabb_zero_samples"] += 1
                    continue
                geometry = exact_common_geometry(
                    meshes[a_name], matrices[a_name], meshes[b_name], matrices[b_name])
                row["exact_samples"] += 1
                volume = geometry["common_volume_mm3"]
                if volume > row["maximum_common_volume_mm3"]:
                    row["maximum_common_volume_mm3"] = volume
                    row["maximum_at_servo_deg"] = degree
                    row["intersection_bounds_mm"] = geometry["intersection_bounds_mm"]
    rows = []
    violations = []
    reference_internal = []
    for key in sorted(pairs):
        row = pairs[key]
        row["limit_mm3"] = None if row["classification"] == "sg_reference_internal" else 0.001
        row["pass"] = (True if row["classification"] == "sg_reference_internal" else
                       row["maximum_common_volume_mm3"] <= 0.001)
        rows.append(row)
        if row["classification"] == "sg_reference_internal":
            reference_internal.append(row)
        elif not row["pass"]:
            violations.append(row)
    return {
        "method": ("全17部品候補。固定組は1姿勢、可動部品を含む組は10〜170度を2.5度刻み。"
                   "AABB共通範囲が0なら数学的に共通体積0、それ以外はBlender Boolean EXACT。"),
        "parts": list(all_ids),
        "unique_pairs": len(rows),
        "expected_unique_pairs": len(all_ids) * (len(all_ids) - 1) // 2,
        "common_volume_limit_mm3": 0.001,
        "pairs": rows,
        "sg_reference_internal_raw": reference_internal,
        "violations": violations,
        "pass": len(rows) == len(all_ids) * (len(all_ids) - 1) // 2 and not violations,
    }


def point_in_snap_zone(kind, point):
    """交差頂点が指定した爪または板ばねの局所領域にあるかを調べる。"""
    x, y, z = point
    if kind == "faceplate":
        return abs(x) >= 34.5 and 7.5 <= abs(y) <= 16.5
    if kind == "bottom":
        return abs(x) >= 33.4 and 7.5 <= abs(y) <= 16.5
    if kind == "servo_clip":
        return -30.5 <= x <= -23.0 and (y <= -16.0 or y >= 6.0)
    if kind == "keeper_detent":
        tolerance = 0.001
        return (35.6 - tolerance <= x <= 38.0 + tolerance
                and 3.6 - tolerance <= y <= 10.3 + tolerance
                and 38.2 - tolerance <= z <= 44.8 + tolerance)
    return False


def exact_assembly_path(meshes, name, moving_name, fixed_names, offsets, snap=None):
    """剛体の区分経路をEXACTで測り、指定爪の途中変形だけを限定許可する。"""
    identity = Matrix.Identity(4)
    pair_rows = {}
    violations = []
    allowed_snap_contacts = []
    for sample, offset in enumerate(offsets):
        if isinstance(offset, dict):
            position = offset["position_mm"]
            moving_matrix = offset["matrix"]
        elif isinstance(offset, (tuple, list)):
            position = [float(value) for value in offset]
            moving_matrix = translation(*position)
        else:
            position = [0.0, 0.0, float(offset)]
            moving_matrix = translation(z=offset)
        moved = meshes[moving_name].moved(moving_matrix)
        lower_a, upper_a = moved.bounds()
        final = sample == len(offsets) - 1
        for fixed_name in fixed_names:
            pair = tuple(sorted((moving_name, fixed_name)))
            row = pair_rows.setdefault(pair, {
                "parts": list(pair), "pose_samples": 0, "aabb_zero_samples": 0,
                "exact_samples": 0, "maximum_common_volume_mm3": 0.0,
                "maximum_at_position_mm": None, "final_common_volume_mm3": 0.0,
            })
            row["pose_samples"] += 1
            lower_b, upper_b = meshes[fixed_name].bounds()
            if any(upper_a[axis] <= lower_b[axis] or upper_b[axis] <= lower_a[axis]
                   for axis in range(3)):
                row["aabb_zero_samples"] += 1
                geometry = {"common_volume_mm3": 0.0, "intersection_bounds_mm": None,
                            "intersection_component_bounds_mm": []}
            else:
                snap_match = snap is not None and pair == tuple(sorted(snap["parts"]))
                geometry = exact_common_geometry(
                    meshes[moving_name], moving_matrix, meshes[fixed_name], identity,
                    ((lambda point: point_in_snap_zone(snap["kind"], point))
                     if snap_match else None))
                row["exact_samples"] += 1
            volume = geometry["common_volume_mm3"]
            if final:
                row["final_common_volume_mm3"] = volume
            if volume > row["maximum_common_volume_mm3"]:
                row["maximum_common_volume_mm3"] = volume
                row["maximum_at_position_mm"] = position
            if volume <= 0.001:
                continue
            snap_match = snap is not None and pair == tuple(sorted(snap["parts"]))
            if (not final and snap_match and geometry["vertices_in_allowed_zone"]
                    and snap["strain_percent"] <= 2.0):
                allowed_snap_contacts.append({
                    "position_mm": position, "parts": list(pair),
                    "common_volume_mm3": volume,
                    "intersection_component_bounds_mm": geometry["intersection_component_bounds_mm"],
                })
            else:
                violations.append({
                    "position_mm": position, "parts": list(pair),
                    "common_volume_mm3": volume,
                    "intersection_bounds_mm": geometry["intersection_bounds_mm"],
                    "reason": ("final position must have zero common volume" if final else
                               "rigid collision outside the specified elastic contact zone"),
                })
    if snap is not None:
        snap_report = {**snap, "maximum_strain_percent": 2.0,
                       "zone_limited_contacts": len(allowed_snap_contacts),
                       "pass": snap["strain_percent"] <= 2.0}
    else:
        snap_report = None
    return {
        "name": name, "moving": moving_name, "fixed": list(fixed_names),
        "route": "piecewise rigid transform", "translation_step_mm": 1.0,
        "rotation_step_deg": 5.0, "sample_count": len(offsets),
        "pairs": [pair_rows[key] for key in sorted(pair_rows)],
        "snap": snap_report, "allowed_snap_contacts": allowed_snap_contacts,
        "violations": violations,
        "pass": not violations and (snap_report is None or snap_report["pass"]),
    }


def assembly_check(meshes):
    bottom_strain = (1.5 * P.BOTTOM_TAB_T
                     * max(0.0, P.BOTTOM_TAB_HOOK - P.BOTTOM_GAP)
                     / P.BOTTOM_TAB_L ** 2 * 100.0)
    face_strain = 1.5 * 1.8 * 0.4 / 14.0 ** 2 * 100.0
    clip_strain = (1.5 * P.SERVO_CLIP_T * P.SERVO_CLIP_HOOK
                   / P.SERVO_CLIP_FLEX_L ** 2 * 100.0)
    keeper_strain = 1.5 * 1.2 * 0.15 / 8.0 ** 2 * 100.0
    face_snap = {"kind": "faceplate", "parts": ["faceplate", "housing"],
                 "deflection_mm": 0.4, "strain_percent": round(face_strain, 3)}
    bottom_snap = {"kind": "bottom", "parts": ["bottom", "housing"],
                   "deflection_mm": round(mm(P.BOTTOM_TAB_HOOK - P.BOTTOM_GAP), 3),
                   "strain_percent": round(bottom_strain, 3)}
    clip_snap = {"kind": "servo_clip", "parts": ["servo_clip", "servo_body"],
                 "deflection_mm": round(mm(P.SERVO_CLIP_HOOK), 3),
                 "strain_percent": round(clip_strain, 3)}
    keeper_snap = {"kind": "keeper_detent", "parts": ["bearing_keeper", "housing"],
                   "deflection_mm": 0.15, "strain_percent": round(keeper_strain, 3),
                   "spring_free_length_mm": 8.0, "spring_thickness_mm": 1.2,
                   "allowed_zone_mm": [[35.6, 3.6, 38.2], [38.0, 10.3, 44.8]]}
    paths = [
        exact_assembly_path(meshes, "servo_from_bottom", "servo_body", ("housing",),
                            list(range(-36, 1))),
        exact_assembly_path(meshes, "servo_clip_from_bottom", "servo_clip",
                            ("housing", "servo_body"), list(range(-24, 1)), clip_snap),
    ]
    # ホーン受けは+X側から付属ホーンへ差す。主軸とは別部品なので閉じた左壁を通らない。
    paths.append(exact_assembly_path(
        meshes, "horn_coupler_from_positive_x", "horn_coupler",
        ("housing", "servo_horn"), [(x, 0, 0) for x in range(12, -1, -1)]))
    # カムは主軸より先に開いた底から最終位置へ置く。
    for cam in ("cam_center", "cam_inner", "cam_outer"):
        paths.append(exact_assembly_path(
            meshes, cam + "_from_bottom", cam, ("housing",), list(range(-32, 1))))
    # 主軸を+X外側から軸方向へ通し、3カムとホーン受けの六角差込へ入れる。
    paths.append(exact_assembly_path(
        meshes, "camshaft_from_positive_x", "camshaft",
        ("housing", "horn_coupler", "cam_center", "cam_inner", "cam_outer"),
        [(x, 0, 0) for x in range(42, -1, -1)]))
    # keeperは爪を左右キー溝へ合わせ、+X外側から入れてからX軸回りに90度戻す。
    keeper_pivot = translation(z=mm(P.CAM_AXIS_Z))
    keeper_unpivot = translation(z=-mm(P.CAM_AXIS_Z))
    keeper_insert = keeper_pivot @ Matrix.Rotation(math.radians(90), 4, "X") @ keeper_unpivot
    keeper_route = [
        {"position_mm": [float(x), 0.0, 0.0],
         "matrix": translation(x=x) @ keeper_insert}
        for x in range(12, -1, -1)
    ]
    keeper_route.extend({
        "position_mm": [0.0, 0.0, float(angle)],
        "matrix": (keeper_pivot @ Matrix.Rotation(math.radians(angle), 4, "X")
                   @ keeper_unpivot),
    } for angle in range(85, -1, -5))
    paths.append(exact_assembly_path(
        meshes, "bearing_keeper_bayonet", "bearing_keeper", ("housing", "camshaft"),
        keeper_route, keeper_snap))
    # 3格子と案内枠を箱外で組む。中心格子だけはC開口へ+X側から水平に入れる。
    paths.append(exact_assembly_path(
        meshes, "carrier_outer_into_guide_frame", "carrier_outer", ("guide_frame",),
        list(range(20, -1, -1))))
    paths.append(exact_assembly_path(
        meshes, "carrier_inner_into_guide_frame", "carrier_inner", ("guide_frame",),
        list(range(20, -1, -1))))
    paths.append(exact_assembly_path(
        meshes, "carrier_center_into_guide_frame", "carrier_center", ("guide_frame",),
        [(x, 0, 0) for x in range(12, -1, -1)]))
    # 組んだ4部品を同じZ変位で上から下ろす。相互位置は既に上の経路で検査済み。
    group_route = list(range(20, -1, -1))
    paths.append(exact_assembly_path(
        meshes, "guide_frame_group_into_housing", "guide_frame", ("housing",), group_route))
    carrier_fixed = ("housing", "camshaft", "horn_coupler",
                     "cam_center", "cam_inner", "cam_outer")
    for carrier in ("carrier_outer", "carrier_inner", "carrier_center"):
        paths.append(exact_assembly_path(
            meshes, carrier + "_with_guide_group", carrier, carrier_fixed, group_route))
    paths.extend([
        exact_assembly_path(meshes, "faceplate_from_top", "faceplate",
                            ("housing", "guide_frame", "carrier_center", "carrier_inner", "carrier_outer"),
                            list(range(20, -1, -1)), face_snap),
        exact_assembly_path(meshes, "bottom_from_below", "bottom",
                            ("housing", "servo_body", "servo_clip", "bearing_keeper"),
                            list(range(-20, 1)), bottom_snap),
    ])
    failures = []
    for path in paths:
        if path["pass"]:
            continue
        worst = (max(path["violations"], key=lambda item: item["common_volume_mm3"])
                 if path["violations"] else None)
        failures.append({"name": path["name"],
                         "violation_samples": len(path["violations"]),
                         "worst": worst})
    return {
        "method": ("組立STLを1mm刻みで並進し、keeper回転は5度刻みで検査。"
                   "AABB共通範囲が0なら数学的に体積0、それ以外はBlender Boolean EXACT。"
                   "最終位置はスナップも体積0。"),
        "paths": paths,
        "failure_summary": failures,
        "snap_limit_percent": 2.0,
        "cam_hex_clearance_per_side_mm": round(
            (P.CAM_BORE_FLAT - P.CAM_SHAFT_FLAT) * 500.0, 3),
        "bearing_radial_clearance_mm": round(P.BEARING_CLEARANCE * 1000.0, 3),
        "pass": all(path["pass"] for path in paths),
    }


def mm(value):
    return value * 1000.0


def physics(meshes):
    names = ("carrier_center", "carrier_inner", "carrier_outer")
    masses = []
    for name in names:
        props = meshes[name].mass_props()
        masses.append(abs(props["volume"]) * 1e-9 * P.PLA_DENSITY)
    gravity_torque = sum(m * P.GRAVITY * e for m, e in zip(masses, P.CAM_E))
    friction_upper = gravity_torque * P.GUIDE_FRICTION_MU
    required = gravity_torque + friction_upper
    limit = P.SERVO_STALL_TORQUE / 3.0
    peg_d = P.SHAFT_JOINT_FLAT
    required_peg_shear = 16.0 * required / (math.pi * peg_d ** 3)
    limit_peg_shear = 16.0 * limit / (math.pi * peg_d ** 3)
    strokes = [motion.lift_m(i, P.SERVO_MAX_DEG) * 1000.0 for i in range(3)]
    return {
        "carrier_mass_g": [round(m * 1000, 3) for m in masses],
        "stroke_mm": [round(x, 3) for x in strokes],
        "gravity_torque_Nm": round(gravity_torque, 6),
        "friction_upper_Nm": round(friction_upper, 6),
        "required_Nm": round(required, 6),
        "stall_fraction": round(required / P.SERVO_STALL_TORQUE, 4),
        "one_third_stall_fraction": round(required / limit, 4),
        "shaft_joint_reference": {
            "hex_flat_mm": round(mm(P.SHAFT_JOINT_FLAT), 3),
            "socket_flat_mm": round(mm(P.SHAFT_JOINT_SOCKET_FLAT), 3),
            "engagement_mm": round(mm(P.SHAFT_JOINT_L), 3),
            "one_third_stall_torque_Nm": round(limit, 4),
            "required_torque_inscribed_circle_shear_MPa": round(required_peg_shear / 1e6, 4),
            "one_third_stall_inscribed_circle_shear_MPa": round(limit_peg_shear / 1e6, 4),
            "basis": "対辺3.6mm六角に内接する直径3.6mm円柱を下限とし、最大せん断応力を16T/(pi*d^3)で算出",
        },
        "power_off": ("格子への重力は全域で閉方向だが、無通電SG92Rを逆駆動できるとは限らない。"
                      "停止角度付近に残り得るため、復電後に低速で10度へ戻す。"),
        "pass": required <= limit and all(abs(a - b) < 0.002 for a, b in zip(strokes, (5.909, 3.939, 1.970))),
    }


def main():
    scene_names = ("housing", "faceplate", "guide_frame", "bottom", "carrier_center", "carrier_inner", "carrier_outer",
                   "camshaft", "horn_coupler", "cam_center", "cam_inner", "cam_outer", "bearing_keeper", "servo_clip",
                   "servo_body", "servo_horn", "servo_wire")
    required = scene_names + ("print_test",)
    source_hash_start = source_stl_hashes(scene_names)
    meshes = {name: load(name) for name in required}
    topo_cal = topology_calibration()
    collision_cal = collision_calibration()
    exact_cal = exact_volume_calibration()
    reference_names = {"servo_body", "servo_horn", "servo_wire"}
    stl = {name: topology(os.path.join(BUILD, f"{name}.stl"))
           for name in required if name not in reference_names}
    for name, item in stl.items():
        item["expected_connected_components"] = 3 if name == "print_test" else 1
        item["pass"] = item["pass"] and item["connected_components"] == item["expected_connected_components"]
    reference_stl = {name: topology(os.path.join(BUILD, f"{name}.stl")) for name in reference_names}
    printed_names = ("housing", "faceplate", "guide_frame", "bottom", "carrier_center", "carrier_inner", "carrier_outer",
                     "camshaft", "horn_coupler", "cam_center", "cam_inner", "cam_outer", "bearing_keeper", "servo_clip")
    print_stl = {name: topology(os.path.join(BUILD, f"print_{name}.stl")) for name in printed_names}
    for item in print_stl.values():
        item["on_bed"] = abs(item["bounds_mm"][0][2]) <= 0.001
        item["expected_connected_components"] = 1
        item["pass"] = item["pass"] and item["on_bed"] and item["connected_components"] == 1
    exact_scene = exact_scene_check(meshes)
    static_geometry = static_geometry_check(exact_scene)
    moving = motion_check(meshes, exact_scene)
    exact_interfaces = exact_interface_check(meshes)
    assembly = assembly_check(meshes)
    physical = physics(meshes)
    source_hash_end = source_stl_hashes(scene_names)
    source_stl_integrity = {
        "start": source_hash_start,
        "end": source_hash_end,
        "pass": source_hash_start == source_hash_end,
    }
    raised_mesh_z = max(
        meshes[name].moved(matrix_from_column_major(motion.transforms(P.SERVO_MAX_DEG)[name])).bounds()[1][2]
        for name in ("carrier_center", "carrier_inner", "carrier_outer")
    )
    dimensions = {
        "closed_mm": [76.0, 76.0, 76.0],
        "raised_height_mm": round(raised_mesh_z, 3),
        "raised_height_source": "STL実頂点へservo=170度のmotion変換を適用した最大Z",
        "face_count": 19,
        "ring_counts": [1, 6, 12],
        "hex_open_flat_mm": P.HEX_OPEN_FLAT * 1000,
        "pitch_mm": P.HEX_PITCH * 1000,
    }
    overall = (topo_cal["pass"] and collision_cal["pass"] and exact_cal["pass"]
               and all(x["pass"] for x in stl.values())
               and all(x["pass"] for x in print_stl.values())
               and static_geometry["pass"] and moving["pass"] and exact_interfaces["pass"]
               and exact_scene["pass"] and assembly["pass"] and physical["pass"]
               and source_stl_integrity["pass"])
    report = {
        "pass": overall,
        "calibration": {"topology": topo_cal, "collision": collision_cal, "exact_volume": exact_cal},
        "source_stl_integrity": source_stl_integrity,
        "dimensions": dimensions,
        "stl_direct_parse": stl,
        "canonical_reference_stl": reference_stl,
        "print_stl_direct_parse": print_stl,
        "static_geometry": static_geometry,
        "motion": moving,
        "exact_interfaces": exact_interfaces,
        "exact_scene": exact_scene,
        "assembly": assembly,
        "physics": physical,
        "limitations": [
            "剛体候補136組はAABB非交差を数学的0とし、それ以外をBoolean EXACTで実体積測定した。対応するカムと従動パッドの接触は解析式でも追跡した。",
            "組立経路は並進1mm刻み、keeper回転5度刻みの離散検査。指定したスナップ爪とkeeper板ばね以外の共通体積は許容していない。",
            "SG92R正本の参照STLは形状を改変せず別欄に記録した。印刷部品のトポロジー合否には含めない。",
            "摩擦係数、ホーン嵌め合い、底板スナップ、PLA/PETGの収縮は実物未検証。",
            "電源断では停止角度付近に残り得る。復電後に低速で10度へ戻し、格子の閉鎖を実物確認する。",
        ],
    }
    path = os.path.join(BUILD, "verify_report.json")
    with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(path + ".tmp", path)
    print(json.dumps({"pass": overall,
                      "static_geometry_pass": static_geometry["pass"],
                      "motion_pass": moving["pass"],
                      "exact_scene_pass": exact_scene["pass"],
                      "exact_scene_violations": exact_scene["violations"],
                      "exact_interfaces_pass": exact_interfaces["pass"],
                      "assembly_pass": assembly["pass"],
                      "assembly_failures": assembly["failure_summary"],
                      "source_stl_integrity_pass": source_stl_integrity["pass"],
                      "source_stl_aggregate_sha256": source_hash_end["aggregate_sha256"],
                      "physics_pass": physical["pass"]}, ensure_ascii=False))
    if not overall:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
