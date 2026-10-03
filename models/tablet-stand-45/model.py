"""45 度固定の横置きタブレットスタンドを生成する。"""
import math
import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import bmesh
from mathutils import Vector

from blender_utils import clear_scene, export_stl
from params import *


def _cross_2d(a, b):
    return a[0] * b[1] - a[1] * b[0]


def rounded_polygon(points, radii, segments=ROUND_SEGMENTS):
    """直線輪郭の各頂点を指定半径の接線円弧へ置き換える。"""
    if len(points) != len(radii) or len(points) < 3:
        raise ValueError("points and radii must describe the same polygon")
    result = []
    count = len(points)
    for index, (point, radius) in enumerate(zip(points, radii)):
        before = Vector(points[(index - 1) % count])
        current = Vector(point)
        after = Vector(points[(index + 1) % count])
        to_before = before - current
        to_after = after - current
        if min(to_before.length, to_after.length) < 1e-8:
            raise ValueError("polygon contains a zero-length edge")
        to_before.normalize()
        to_after.normalize()
        cosine = max(-1.0, min(1.0, to_before.dot(to_after)))
        corner = math.acos(cosine)
        if radius <= 0 or corner < 1e-5 or abs(math.pi - corner) < 1e-5:
            result.append(tuple(current))
            continue
        tangent = radius / math.tan(corner / 2.0)
        available = min((before - current).length, (after - current).length) * 0.45
        if tangent > available:
            tangent = available
            radius = tangent * math.tan(corner / 2.0)
        start = current + to_before * tangent
        end = current + to_after * tangent
        bisector = (to_before + to_after).normalized()
        center = current + bisector * (radius / math.sin(corner / 2.0))
        a0 = math.atan2(start.y - center.y, start.x - center.x)
        a1 = math.atan2(end.y - center.y, end.x - center.x)
        incoming = current - before
        outgoing = after - current
        turn = _cross_2d(incoming, outgoing)
        if turn > 0:
            while a1 <= a0:
                a1 += 2.0 * math.pi
        else:
            while a1 >= a0:
                a1 -= 2.0 * math.pi
        steps = max(2, int(math.ceil(abs(a1 - a0) / (2.0 * math.pi) * segments)))
        for step in range(steps + 1):
            if result and step == 0:
                continue
            angle = a0 + (a1 - a0) * step / steps
            result.append((center.x + radius * math.cos(angle),
                           center.y + radius * math.sin(angle)))
    return result


def extrude_profile(name, profile, width):
    """YZ 断面を X 方向へ押し出した閉じたメッシュを作る。"""
    if len(profile) < 3 or width <= 0:
        raise ValueError("profile extrusion must be nonempty")
    half = width / 2.0
    bm = bmesh.new()
    left = [bm.verts.new((-half, y, z)) for y, z in profile]
    right = [bm.verts.new((half, y, z)) for y, z in profile]
    bm.faces.new(list(reversed(left)))
    bm.faces.new(right)
    for index in range(len(profile)):
        following = (index + 1) % len(profile)
        bm.faces.new((left[index], right[index], right[following], left[following]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate(verbose=True)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def support_frame():
    angle = math.radians(ANGLE_DEG)
    upward = Vector((math.cos(angle), math.sin(angle)))
    normal = Vector((-math.sin(angle), math.cos(angle)))
    origin = Vector((SEAT_Y, SEAT_Z))
    return origin, upward, normal


def outer_profile():
    origin, upward, normal = support_frame()
    groove_inner = origin + normal * GROOVE_WIDTH
    lip_inner_top = groove_inner + Vector((0.0, LIP_HEIGHT / math.sin(math.radians(ANGLE_DEG))))
    lip_outer_bottom = groove_inner + Vector((-LIP_THICKNESS, 0.0))
    lip_outer_top = lip_inner_top + Vector((-LIP_THICKNESS, 0.0))
    support_top = origin + upward * SUPPORT_LENGTH
    deck_back_top = support_top - normal * DECK_THICKNESS
    points = [
        (0.0, 0.0),
        (0.0, BASE_THICKNESS),
        tuple(lip_outer_bottom),
        tuple(lip_outer_top),
        tuple(lip_inner_top),
        tuple(groove_inner),
        tuple(origin),
        tuple(support_top),
        tuple(deck_back_top),
        (DEPTH, BASE_THICKNESS),
        (DEPTH, 0.0),
    ]
    radii = [
        0.0,
        LOWER_OUTER_R,
        LIP_OUTER_R,
        LIP_OUTER_R,
        LIP_OUTER_R,
        INNER_CORNER_R,
        INNER_CORNER_R,
        SUPPORT_TOP_R,
        SUPPORT_TOP_R,
        LOWER_OUTER_R,
        0.0,
    ]
    return rounded_polygon(points, radii)


def hole_profile():
    """床上面、デッキ裏、後柱裏が作る角丸三角穴。"""
    origin, upward, normal = support_frame()
    deck_line_point = origin - normal * DECK_THICKNESS
    front_distance = (BASE_THICKNESS - deck_line_point.y) / upward.y
    front = deck_line_point + upward * front_distance

    outer_top = origin + upward * SUPPORT_LENGTH - normal * DECK_THICKNESS
    outer_bottom = Vector((DEPTH, BASE_THICKNESS))
    rear_direction = (outer_bottom - outer_top).normalized()
    inward = Vector((rear_direction.y, -rear_direction.x))
    if inward.x > 0:
        inward.negate()
    rear_line_point = outer_top + inward * REAR_THICKNESS
    rear_floor_y = rear_line_point.x + (
        (BASE_THICKNESS - rear_line_point.y) * rear_direction.x / rear_direction.y
    )
    rear = Vector((rear_floor_y, BASE_THICKNESS))
    denominator = _cross_2d(upward, rear_direction)
    if abs(denominator) < 1e-8:
        raise RuntimeError("deck and rear inner lines do not intersect")
    deck_distance = _cross_2d(rear_line_point - deck_line_point, rear_direction) / denominator
    top = deck_line_point + upward * deck_distance
    return rounded_polygon(
        [tuple(front), tuple(top), tuple(rear)],
        [HOLE_CORNER_R, HOLE_CORNER_R, HOLE_CORNER_R],
    )


def _apply_boolean_difference(base, cutter):
    bpy.context.view_layer.objects.active = base
    base.select_set(True)
    modifier = base.modifiers.new("arched_side_opening", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def _chamfer_side_edges(obj):
    half = WIDTH / 2.0
    attribute = obj.data.attributes.get("bevel_weight_edge")
    if attribute is None:
        attribute = obj.data.attributes.new("bevel_weight_edge", "FLOAT", "EDGE")
    marked = 0
    for edge, weight in zip(obj.data.edges, attribute.data):
        a = obj.data.vertices[edge.vertices[0]].co
        b = obj.data.vertices[edge.vertices[1]].co
        on_end = ((abs(abs(a.x) - half) < 1e-6) and
                  (abs(abs(b.x) - half) < 1e-6) and a.x * b.x > 0)
        weight.value = 1.0 if on_end else 0.0
        marked += int(on_end)
    if marked == 0:
        raise RuntimeError("no side edges were found for chamfering")
    bevel = obj.modifiers.new("side_edge_chamfer", "BEVEL")
    bevel.limit_method = "WEIGHT"
    bevel.width = SIDE_CHAMFER
    bevel.segments = 1
    bevel.affect = "EDGES"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)


def _clean_mesh(obj):
    """Boolean と面取りで生じた公差未満の辺を整理して三角形化する。"""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-10)
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.validate(verbose=True)
    obj.data.update()


def mesh_metrics(obj):
    bpy.context.view_layer.update()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if not bm.verts or not bm.faces:
        bm.free()
        raise RuntimeError("stand mesh is empty")
    non_manifold = sum(not edge.is_manifold for edge in bm.edges)
    degenerate = sum(face.calc_area() < 1e-12 for face in bm.faces)
    signed_volume = bm.calc_volume(signed=True)
    adjacency = {vertex.index: set() for vertex in bm.verts}
    for edge in bm.edges:
        a, b = edge.verts
        adjacency[a.index].add(b.index)
        adjacency[b.index].add(a.index)
    unseen = set(adjacency)
    components = 0
    while unseen:
        components += 1
        queue = deque([unseen.pop()])
        while queue:
            current = queue.popleft()
            reached = adjacency[current] & unseen
            unseen.difference_update(reached)
            queue.extend(reached)
    bm.free()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    low = Vector((min(point.x for point in corners), min(point.y for point in corners), min(point.z for point in corners)))
    high = Vector((max(point.x for point in corners), max(point.y for point in corners), max(point.z for point in corners)))
    dimensions = high - low
    result = {
        "components": components,
        "non_manifold": non_manifold,
        "degenerate": degenerate,
        "signed_volume_mm3": signed_volume * 1e9,
        "dimensions_mm": tuple(value * 1000 for value in dimensions),
        "minimum_mm": tuple(value * 1000 for value in low),
    }
    print("[tablet-stand-45] mesh", result)
    if components != 1 or non_manifold or degenerate or signed_volume <= 0:
        raise RuntimeError(f"invalid stand mesh: {result}")
    return result


def build_stand():
    stand = extrude_profile("tablet_stand_45", outer_profile(), WIDTH)
    cutter = extrude_profile("arched_opening_cutter", hole_profile(), WIDTH + 0.004)
    _apply_boolean_difference(stand, cutter)
    _chamfer_side_edges(stand)
    _clean_mesh(stand)
    metrics = mesh_metrics(stand)
    expected = (WIDTH * 1000, DEPTH * 1000)
    if abs(metrics["dimensions_mm"][0] - expected[0]) > 0.02:
        raise RuntimeError("width changed outside tolerance")
    if abs(metrics["dimensions_mm"][1] - expected[1]) > 0.02:
        raise RuntimeError("depth changed outside tolerance")
    return stand


def export_outputs(stand):
    export_stl(MODEL_NAME, only=[stand])
    standing_mesh = stand.data.copy()

    stand.rotation_euler.y = -math.pi / 2.0
    bpy.context.view_layer.objects.active = stand
    stand.select_set(True)
    bpy.ops.object.transform_apply(rotation=True)
    minimum_z = min((stand.matrix_world @ vertex.co).z for vertex in stand.data.vertices)
    stand.location.z -= minimum_z
    bpy.ops.object.transform_apply(location=True)
    print_metrics = mesh_metrics(stand)
    print("[tablet-stand-45] print_dimensions_mm", print_metrics["dimensions_mm"])
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                             "exports", MODEL_NAME), exist_ok=True)
    export_stl(f"{MODEL_NAME}/print", only=[stand])

    old_mesh = stand.data
    stand.data = standing_mesh
    stand.location = (0.0, 0.0, 0.0)
    stand.rotation_euler = (0.0, 0.0, 0.0)
    bpy.data.meshes.remove(old_mesh)
    mesh_metrics(stand)
    export_stl(MODEL_NAME, only=[stand])


def main():
    clear_scene()
    stand = build_stand()
    export_outputs(stand)


if __name__ == "__main__":
    main()
