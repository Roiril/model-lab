"""100 mm高の水平ノートPCスタンド用フレームを生成する。"""
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


def rounded_rectangle(y_min, y_max, z_min, z_max, radius):
    """YZ平面の角丸長方形を反時計回りの点列で返す。"""
    if y_max <= y_min or z_max <= z_min:
        raise ValueError("rounded rectangle must have positive dimensions")
    if radius <= 0 or radius * 2 >= min(y_max - y_min, z_max - z_min):
        raise ValueError("rounded rectangle radius is outside its valid range")
    per_corner = ROUND_SEGMENTS // 4
    if per_corner < 2:
        raise ValueError("ROUND_SEGMENTS must provide at least two steps per corner")
    corners = (
        (y_min + radius, z_min + radius, math.pi, 1.5 * math.pi),
        (y_max - radius, z_min + radius, -0.5 * math.pi, 0.0),
        (y_max - radius, z_max - radius, 0.0, 0.5 * math.pi),
        (y_min + radius, z_max - radius, 0.5 * math.pi, math.pi),
    )
    points = []
    for center_y, center_z, start, end in corners:
        for step in range(per_corner):
            angle = start + (end - start) * step / per_corner
            points.append((
                center_y + radius * math.cos(angle),
                center_z + radius * math.sin(angle),
            ))
    return points


def create_chamfered_ring(name, outer, inner, outer_end, inner_end):
    """対応点を持つ角丸輪郭から、X端面取り済みの閉じた部品を作る。"""
    point_count = len(outer)
    if point_count < 3 or any(len(profile) != point_count for profile in (inner, outer_end, inner_end)):
        raise ValueError("ring profiles must have the same nonzero point count")
    half = FRAME_WIDTH / 2.0
    x_layers = (-half, -half + SIDE_CHAMFER, half - SIDE_CHAMFER, half)
    outer_profiles = (outer_end, outer, outer, outer_end)
    inner_profiles = (inner_end, inner, inner, inner_end)
    bm = bmesh.new()
    outer_loops = []
    inner_loops = []
    for x, outer_profile, inner_profile in zip(x_layers, outer_profiles, inner_profiles):
        outer_loops.append([bm.verts.new((x, y, z)) for y, z in outer_profile])
        inner_loops.append([bm.verts.new((x, y, z)) for y, z in inner_profile])
    for layer in range(len(x_layers) - 1):
        for index in range(point_count):
            following = (index + 1) % point_count
            bm.faces.new((
                outer_loops[layer][index],
                outer_loops[layer + 1][index],
                outer_loops[layer + 1][following],
                outer_loops[layer][following],
            ))
            bm.faces.new((
                inner_loops[layer][following],
                inner_loops[layer + 1][following],
                inner_loops[layer + 1][index],
                inner_loops[layer][index],
            ))
    for layer in (0, len(x_layers) - 1):
        for index in range(point_count):
            following = (index + 1) % point_count
            bm.faces.new((
                outer_loops[layer][index],
                outer_loops[layer][following],
                inner_loops[layer][following],
                inner_loops[layer][index],
            ))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate(verbose=True)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def clean_mesh(obj):
    """面取り後の微小重複を整理して三角形化する。"""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=CLEANUP_DISTANCE)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-10)
    bmesh.ops.triangulate(
        bm,
        faces=list(bm.faces),
        quad_method="BEAUTY",
        ngon_method="BEAUTY",
    )
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.validate(verbose=True)
    obj.data.update()


def mesh_metrics(obj, label):
    bpy.context.view_layer.update()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if not bm.verts or not bm.faces:
        bm.free()
        raise RuntimeError(f"{label} mesh is empty")
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
    low = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
    high = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
    result = {
        "components": components,
        "non_manifold": non_manifold,
        "degenerate": degenerate,
        "signed_volume_mm3": signed_volume * 1e9,
        "dimensions_mm": tuple(value * 1000.0 for value in high - low),
        "minimum_mm": tuple(value * 1000.0 for value in low),
        "maximum_mm": tuple(value * 1000.0 for value in high),
    }
    print(f"[{MODEL_NAME}] {label}", result)
    if components != 1 or non_manifold or degenerate or signed_volume <= 0:
        raise RuntimeError(f"invalid {label} mesh: {result}")
    return result


def build_frame():
    if abs(BASE_THICKNESS - BOTTOM_BEAM) > 1e-9:
        raise RuntimeError("BASE_THICKNESS must reference BOTTOM_BEAM")
    if PAD_WIDTH > FRAME_WIDTH - 2.0 * SIDE_CHAMFER:
        raise RuntimeError("PAD_WIDTH exceeds the flat X contact surface")
    for pad_y in (PAD_FRONT_Y, PAD_REAR_Y):
        if pad_y < OUTER_R or pad_y + PAD_LENGTH > FRAME_DEPTH - OUTER_R:
            raise RuntimeError("pad leaves the flat Y contact surface")
    outer = rounded_rectangle(0.0, FRAME_DEPTH, 0.0, BODY_HEIGHT, OUTER_R)
    inner = rounded_rectangle(
        END_COLUMN,
        FRAME_DEPTH - END_COLUMN,
        BOTTOM_BEAM,
        BODY_HEIGHT - TOP_BEAM,
        INNER_R,
    )
    outer_end = rounded_rectangle(
        SIDE_CHAMFER,
        FRAME_DEPTH - SIDE_CHAMFER,
        SIDE_CHAMFER,
        BODY_HEIGHT - SIDE_CHAMFER,
        OUTER_R - SIDE_CHAMFER,
    )
    inner_end = rounded_rectangle(
        END_COLUMN - SIDE_CHAMFER,
        FRAME_DEPTH - END_COLUMN + SIDE_CHAMFER,
        BOTTOM_BEAM - SIDE_CHAMFER,
        BODY_HEIGHT - TOP_BEAM + SIDE_CHAMFER,
        INNER_R + SIDE_CHAMFER,
    )
    frame = create_chamfered_ring("frame_local", outer, inner, outer_end, inner_end)
    clean_mesh(frame)
    metrics = mesh_metrics(frame, "use_frame_local")
    expected = (FRAME_WIDTH * 1000.0, FRAME_DEPTH * 1000.0, BODY_HEIGHT * 1000.0)
    for actual, target in zip(metrics["dimensions_mm"], expected):
        if abs(actual - target) > 0.02:
            raise RuntimeError(f"frame dimension {actual:.4f} mm differs from {target:.4f} mm")
    return frame


def make_print_copy(frame):
    print_obj = frame.copy()
    print_obj.data = frame.data.copy()
    print_obj.name = "frame_print_side_down"
    bpy.context.collection.objects.link(print_obj)
    root_two = math.sqrt(2.0)
    for vertex in print_obj.data.vertices:
        x, y, z = vertex.co
        vertex.co = (
            (y - FRAME_DEPTH / 2.0 - (z - BODY_HEIGHT / 2.0)) / root_two,
            (y - FRAME_DEPTH / 2.0 + z - BODY_HEIGHT / 2.0) / root_two,
            x + FRAME_WIDTH / 2.0,
        )
    print_obj.data.update()
    metrics = mesh_metrics(print_obj, "print_frame")
    if abs(metrics["minimum_mm"][2]) > 0.01 or abs(metrics["maximum_mm"][2] - FRAME_WIDTH * 1000) > 0.01:
        raise RuntimeError("print frame must lie on Z=0 at the frame width")
    return print_obj


def remove_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)


def assert_scene_meshes(expected_names):
    actual = {obj.name for obj in bpy.context.scene.objects if obj.type == "MESH"}
    if actual != set(expected_names):
        raise RuntimeError(f"unexpected scene meshes: {sorted(actual)}")


def export_print_frame(frame, print_obj):
    remove_object(frame)
    assert_scene_meshes([print_obj.name])
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                             "exports", MODEL_NAME), exist_ok=True)
    export_stl(f"{MODEL_NAME}/frame", only=[print_obj])


def create_assembly(frame_mesh, print_obj):
    remove_object(print_obj)
    left = bpy.data.objects.new("left_frame", frame_mesh.copy())
    right = bpy.data.objects.new("right_frame", frame_mesh.copy())
    bpy.context.collection.objects.link(left)
    bpy.context.collection.objects.link(right)
    left.location = (-RAIL_CENTER, 0.0, PAD_THICKNESS)
    right.location = (RAIL_CENTER, 0.0, PAD_THICKNESS)
    mesh_metrics(left, "left_use_frame")
    mesh_metrics(right, "right_use_frame")
    assert_scene_meshes([left.name, right.name])
    bpy.context.view_layer.update()
    minimum = Vector((
        min((obj.matrix_world @ Vector(corner)).x for obj in (left, right) for corner in obj.bound_box),
        min((obj.matrix_world @ Vector(corner)).y for obj in (left, right) for corner in obj.bound_box),
        min((obj.matrix_world @ Vector(corner)).z for obj in (left, right) for corner in obj.bound_box),
    ))
    maximum = Vector((
        max((obj.matrix_world @ Vector(corner)).x for obj in (left, right) for corner in obj.bound_box),
        max((obj.matrix_world @ Vector(corner)).y for obj in (left, right) for corner in obj.bound_box),
        max((obj.matrix_world @ Vector(corner)).z for obj in (left, right) for corner in obj.bound_box),
    ))
    dimensions = (maximum - minimum) * 1000.0
    print(f"[{MODEL_NAME}] assembly_components 2")
    print(f"[{MODEL_NAME}] assembly_dimensions_mm", tuple(dimensions))
    print(f"[{MODEL_NAME}] assembly_minimum_mm", tuple(minimum * 1000.0))
    expected = ((RAIL_CENTER * 2 + FRAME_WIDTH) * 1000, FRAME_DEPTH * 1000, BODY_HEIGHT * 1000)
    for actual, target in zip(dimensions, expected):
        if abs(actual - target) > 0.02:
            raise RuntimeError(f"assembly dimension {actual:.4f} mm differs from {target:.4f} mm")
    if abs(minimum.z - PAD_THICKNESS) > 0.00001 or abs(maximum.z - PAD_THICKNESS - BODY_HEIGHT) > 0.00001:
        raise RuntimeError("assembly body must allow for the bottom pad")
    return left, right


def main():
    clear_scene()
    bpy.context.preferences.filepaths.save_version = 0
    frame = build_frame()
    frame_mesh = frame.data
    print_obj = make_print_copy(frame)
    export_print_frame(frame, print_obj)
    left, right = create_assembly(frame_mesh, print_obj)
    export_stl(MODEL_NAME, only=[left, right])


if __name__ == "__main__":
    main()
