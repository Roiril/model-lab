"""広い流線型底を持つ100 mm高ノートPCスタンドを生成する。"""
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
    """YZ平面の角丸長方形を反時計回りの対応点列で返す。"""
    if radius <= 0 or radius * 2.0 >= min(y_max - y_min, z_max - z_min):
        raise ValueError("rounded rectangle radius is outside its valid range")
    per_corner = ROUND_SEGMENTS // 4
    corners = (
        (y_min + radius, z_min + radius, math.pi, 1.5 * math.pi),
        (y_max - radius, z_min + radius, -0.5 * math.pi, 0.0),
        (y_max - radius, z_max - radius, 0.0, 0.5 * math.pi),
        (y_min + radius, z_max - radius, 0.5 * math.pi, math.pi),
    )
    return [
        (center_y + radius * math.cos(start + (end - start) * step / per_corner),
         center_z + radius * math.sin(start + (end - start) * step / per_corner))
        for center_y, center_z, start, end in corners
        for step in range(per_corner + 1)
    ]


def rounded_rectangle_xy(width, depth, radius):
    """原点X、FRAME_DEPTH中央Yの角丸長方形を返す。"""
    half_width = width / 2.0
    y_min = (FRAME_DEPTH - depth) / 2.0
    y_max = y_min + depth
    per_corner = ROUND_SEGMENTS // 4
    corners = (
        (-half_width + radius, y_min + radius, math.pi, 1.5 * math.pi),
        (half_width - radius, y_min + radius, -0.5 * math.pi, 0.0),
        (half_width - radius, y_max - radius, 0.0, 0.5 * math.pi),
        (-half_width + radius, y_max - radius, 0.5 * math.pi, math.pi),
    )
    return [
        (center_x + radius * math.cos(start + (end - start) * step / per_corner),
         center_y + radius * math.sin(start + (end - start) * step / per_corner))
        for center_x, center_y, start, end in corners
        for step in range(per_corner + 1)
    ]


def create_chamfered_ring(name, outer, inner, outer_end, inner_end):
    """現行の閉じたextruded ring構造を使ってフレームを作る。"""
    point_count = len(outer)
    if point_count < 3 or any(len(profile) != point_count for profile in (inner, outer_end, inner_end)):
        raise ValueError("ring profiles must have the same point count")
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
            bm.faces.new((outer_loops[layer][index], outer_loops[layer + 1][index],
                          outer_loops[layer + 1][following], outer_loops[layer][following]))
            bm.faces.new((inner_loops[layer][following], inner_loops[layer + 1][following],
                          inner_loops[layer + 1][index], inner_loops[layer][index]))
    for layer in (0, len(x_layers) - 1):
        for index in range(point_count):
            following = (index + 1) % point_count
            bm.faces.new((outer_loops[layer][index], outer_loops[layer][following],
                          inner_loops[layer][following], inner_loops[layer][index]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return object_from_bmesh(name, bm)


def object_from_bmesh(name, bm):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate(verbose=True)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def create_closed_loft(name, layers):
    """対応点を持つ輪郭段から上下を閉じたloft meshを作る。"""
    point_count = len(layers[0][1])
    if point_count < 3 or any(len(profile) != point_count for _, profile in layers):
        raise ValueError("loft profiles must have the same point count")
    bm = bmesh.new()
    loops = [[bm.verts.new((x, y, z)) for x, y in profile] for z, profile in layers]
    for layer in range(len(loops) - 1):
        for index in range(point_count):
            following = (index + 1) % point_count
            bm.faces.new((loops[layer][index], loops[layer + 1][index],
                          loops[layer + 1][following], loops[layer][following]))
    bm.faces.new(tuple(reversed(loops[0])))
    bm.faces.new(tuple(loops[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return object_from_bmesh(name, bm)


def clean_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=CLEANUP_DISTANCE)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-10)
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
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
            reached = adjacency[queue.popleft()] & unseen
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
    z_min = 0.0
    z_max = z_min + BODY_HEIGHT
    outer = rounded_rectangle(0.0, FRAME_DEPTH, z_min, z_max, OUTER_R)
    inner = rounded_rectangle(END_COLUMN, FRAME_DEPTH - END_COLUMN,
                              z_min + BOTTOM_BEAM, z_max - TOP_BEAM, INNER_R)
    outer_end = rounded_rectangle(SIDE_CHAMFER, FRAME_DEPTH - SIDE_CHAMFER,
                                  z_min + SIDE_CHAMFER, z_max - SIDE_CHAMFER,
                                  OUTER_R - SIDE_CHAMFER)
    inner_end = rounded_rectangle(END_COLUMN - SIDE_CHAMFER,
                                  FRAME_DEPTH - END_COLUMN + SIDE_CHAMFER,
                                  z_min + BOTTOM_BEAM - SIDE_CHAMFER,
                                  z_max - TOP_BEAM + SIDE_CHAMFER,
                                  INNER_R + SIDE_CHAMFER)
    frame = create_chamfered_ring("frame_local", outer, inner, outer_end, inner_end)
    clean_mesh(frame)
    metrics = mesh_metrics(frame, "use_frame_local")
    expected = (FRAME_WIDTH * 1000.0, FRAME_DEPTH * 1000.0, BODY_HEIGHT * 1000.0)
    if any(abs(actual - target) > 0.02 for actual, target in zip(metrics["dimensions_mm"], expected)):
        raise RuntimeError("frame dimensions differ from the specification")
    return frame


def smoothstep(value):
    return value * value * (3.0 - 2.0 * value)


def build_foot():
    layers = [(0.0, rounded_rectangle_xy(FOOT_BOTTOM_WIDTH, FOOT_BOTTOM_DEPTH, FOOT_BOTTOM_ROUND)),
              (FOOT_CHAMFER, rounded_rectangle_xy(FOOT_WIDTH, FOOT_DEPTH, FOOT_ROUND))]
    for step in range(1, FOOT_LOFT_STEPS + 1):
        amount = step / FOOT_LOFT_STEPS
        blend = smoothstep(amount)
        z = FOOT_CHAMFER + (FOOT_HEIGHT - FOOT_CHAMFER) * amount
        width = FOOT_WIDTH + (FOOT_TOP_WIDTH - FOOT_WIDTH) * blend
        depth = FOOT_DEPTH + (FOOT_TOP_DEPTH - FOOT_DEPTH) * blend
        radius = FOOT_ROUND + (FOOT_TOP_ROUND - FOOT_ROUND) * blend
        layers.append((z, rounded_rectangle_xy(width, depth, radius)))
    foot = create_closed_loft("foot_local", layers)
    slot_y_min = (FRAME_DEPTH - SLOT_DEPTH) / 2.0
    slot_y_max = slot_y_min + SLOT_DEPTH

    def rectangle(width, y_min, y_max):
        half = width / 2.0
        return [(-half, y_min), (half, y_min), (half, y_max), (-half, y_max)]

    slot = create_closed_loft("slot_cutter", (
        (FOOT_FLOOR, rectangle(SLOT_WIDTH, slot_y_min, slot_y_max)),
        (FOOT_HEIGHT - ENTRY_CHAMFER, rectangle(SLOT_WIDTH, slot_y_min, slot_y_max)),
        (FOOT_HEIGHT,
         rectangle(SLOT_WIDTH + 2.0 * ENTRY_CHAMFER,
                   slot_y_min - ENTRY_CHAMFER, slot_y_max + ENTRY_CHAMFER)),
        (FOOT_HEIGHT + ENTRY_CHAMFER,
         rectangle(SLOT_WIDTH + 2.0 * ENTRY_CHAMFER,
                   slot_y_min - ENTRY_CHAMFER, slot_y_max + ENTRY_CHAMFER)),
    ))
    bpy.context.view_layer.objects.active = foot
    foot.select_set(True)
    modifier = foot.modifiers.new("frame_slot", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = slot
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(slot, do_unlink=True)
    clean_mesh(foot)
    for polygon in foot.data.polygons:
        center = polygon.center
        is_outer_side = (abs(center.x) >= FOOT_TOP_WIDTH / 2.0 - 0.0001 or
                         center.y <= (FRAME_DEPTH - FOOT_TOP_DEPTH) / 2.0 + 0.0001 or
                         center.y >= (FRAME_DEPTH + FOOT_TOP_DEPTH) / 2.0 - 0.0001)
        polygon.use_smooth = is_outer_side and abs(polygon.normal.z) < 0.95
    foot.data.update()
    metrics = mesh_metrics(foot, "use_foot_local")
    expected = (FOOT_WIDTH * 1000.0, FOOT_DEPTH * 1000.0, FOOT_HEIGHT * 1000.0)
    if any(abs(actual - target) > 0.02 for actual, target in zip(metrics["dimensions_mm"], expected)):
        raise RuntimeError("foot dimensions differ from the specification")
    return foot


def copy_object(source, name):
    result = source.copy()
    result.data = source.data.copy()
    result.name = name
    bpy.context.collection.objects.link(result)
    return result


def make_print_frame(frame):
    result = copy_object(frame, "frame_print_side_down")
    root_two = math.sqrt(2.0)
    center_z = BODY_HEIGHT / 2.0
    for vertex in result.data.vertices:
        x, y, z = vertex.co
        vertex.co = ((y - FRAME_DEPTH / 2.0 - (z - center_z)) / root_two,
                     (y - FRAME_DEPTH / 2.0 + z - center_z) / root_two,
                     x + FRAME_WIDTH / 2.0)
    result.data.update()
    mesh_metrics(result, "print_frame")
    return result


def make_print_foot(foot):
    result = copy_object(foot, "foot_print_45deg")
    root_two = math.sqrt(2.0)
    for vertex in result.data.vertices:
        x, y, z = vertex.co
        vertex.co = ((x - (y - FRAME_DEPTH / 2.0)) / root_two,
                     (x + y - FRAME_DEPTH / 2.0) / root_two, z)
    result.data.update()
    mesh_metrics(result, "print_foot")
    return result


def assert_scene_meshes(expected_names):
    actual = {obj.name for obj in bpy.context.scene.objects if obj.type == "MESH"}
    if actual != set(expected_names):
        raise RuntimeError(f"unexpected scene meshes: {sorted(actual)}")


def keep_only(obj):
    for other in list(bpy.context.scene.objects):
        if other != obj:
            bpy.data.objects.remove(other, do_unlink=True)
    assert_scene_meshes([obj.name])


def build_assembly(frame_mesh, foot_mesh):
    clear_scene()
    left_frame = bpy.data.objects.new("left_frame", frame_mesh.copy())
    right_frame = bpy.data.objects.new("right_frame", frame_mesh.copy())
    left_foot = bpy.data.objects.new("left_foot", foot_mesh.copy())
    right_foot = bpy.data.objects.new("right_foot", foot_mesh.copy())
    for obj in (left_frame, right_frame, left_foot, right_foot):
        bpy.context.collection.objects.link(obj)
    left_frame.location = (-RAIL_CENTER, 0.0, FRAME_ASSEMBLY_Z)
    right_frame.location = (RAIL_CENTER, 0.0, FRAME_ASSEMBLY_Z)
    left_foot.location = (-RAIL_CENTER, 0.0, PAD_THICKNESS)
    right_foot.location = (RAIL_CENTER, 0.0, PAD_THICKNESS)
    objects = (left_frame, right_frame, left_foot, right_foot)
    for obj in objects:
        mesh_metrics(obj, obj.name)
    assert_scene_meshes([obj.name for obj in objects])
    corners = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    low = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
    high = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
    dimensions = tuple(value * 1000.0 for value in high - low)
    print(f"[{MODEL_NAME}] assembly_components 4")
    print(f"[{MODEL_NAME}] assembly_dimensions_mm", dimensions)
    print(f"[{MODEL_NAME}] assembly_minimum_mm", tuple(value * 1000.0 for value in low))
    expected = ((2.0 * RAIL_CENTER + FOOT_WIDTH) * 1000.0,
                FOOT_DEPTH * 1000.0,
                (FOOT_FLOOR + BODY_HEIGHT) * 1000.0)
    if any(abs(actual - target) > 0.02 for actual, target in zip(dimensions, expected)):
        raise RuntimeError("assembly dimensions differ from the derived specification")
    expected_top = FRAME_ASSEMBLY_Z + BODY_HEIGHT
    if abs(low.z - PAD_THICKNESS) > 1e-8 or abs(high.z - expected_top) > 1e-8:
        raise RuntimeError("assembly object Z bounds differ from the derived specification")
    return objects


def main():
    clear_scene()
    bpy.context.preferences.filepaths.save_version = 0
    frame = build_frame()
    foot = build_foot()
    frame_mesh = frame.data.copy()
    foot_mesh = foot.data.copy()

    print_frame = make_print_frame(frame)
    keep_only(print_frame)
    export_stl(f"{MODEL_NAME}/frame", only=[print_frame])

    clear_scene()
    source_foot = bpy.data.objects.new("foot_export_source", foot_mesh.copy())
    bpy.context.collection.objects.link(source_foot)
    print_foot = make_print_foot(source_foot)
    keep_only(print_foot)
    export_stl(f"{MODEL_NAME}/foot", only=[print_foot])

    assembly = build_assembly(frame_mesh, foot_mesh)
    export_stl(MODEL_NAME, only=list(assembly))


if __name__ == "__main__":
    main()
