"""長いS字の連続曲面を持つ100 mm高ノートPCスタンドを生成する。"""
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


def rounded_rectangle(width, y_min, depth, radius, segments=16):
    half_width = width / 2.0
    y_max = y_min + depth
    corners = (
        (-half_width + radius, y_min + radius, math.pi, 1.5 * math.pi),
        (half_width - radius, y_min + radius, -0.5 * math.pi, 0.0),
        (half_width - radius, y_max - radius, 0.0, 0.5 * math.pi),
        (-half_width + radius, y_max - radius, 0.5 * math.pi, math.pi),
    )
    return [
        (cx + radius * math.cos(start + (end - start) * step / segments),
         cy + radius * math.sin(start + (end - start) * step / segments))
        for cx, cy, start, end in corners
        for step in range(segments)
    ]


def create_layered_prism(name, layers):
    point_count = len(layers[0][1])
    if any(len(profile) != point_count for _, profile in layers):
        raise ValueError("Prism profiles must have the same point count")
    bm = bmesh.new()
    loops = [[bm.verts.new((x, y, z)) for x, y in profile] for z, profile in layers]
    for lower, upper in zip(loops, loops[1:]):
        for index in range(point_count):
            following = (index + 1) % point_count
            bm.faces.new((lower[index], upper[index], upper[following], lower[following]))
    bm.faces.new(tuple(reversed(loops[0])))
    bm.faces.new(tuple(loops[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return object_from_bmesh(name, bm)


def create_rounded_prism(name, width, y_min, depth, radius, z_min, z_max, edge_radius):
    layers = (
        (z_min, rounded_rectangle(width - 2.0 * edge_radius,
                                  y_min + edge_radius,
                                  depth - 2.0 * edge_radius,
                                  radius - edge_radius)),
        (z_min + edge_radius, rounded_rectangle(width, y_min, depth, radius)),
        (z_max - edge_radius, rounded_rectangle(width, y_min, depth, radius)),
        (z_max, rounded_rectangle(width - 2.0 * edge_radius,
                                  y_min + edge_radius,
                                  depth - 2.0 * edge_radius,
                                  radius - edge_radius)),
    )
    return create_layered_prism(name, layers)


def cubic_bezier(points, t):
    p0, p1, p2, p3 = (Vector(point) for point in points)
    u = 1.0 - t
    center = u ** 3 * p0 + 3.0 * u * u * t * p1 + 3.0 * u * t * t * p2 + t ** 3 * p3
    tangent = 3.0 * u * u * (p1 - p0) + 6.0 * u * t * (p2 - p1) + 3.0 * t * t * (p3 - p2)
    return center, tangent


def smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def create_bezier_sweep(name, points, side_radius, x_radius,
                        root_side_radius, root_x_radius):
    bm = bmesh.new()
    loops = []
    for step in range(CURVE_STEPS + 1):
        t = step / CURVE_STEPS
        center, tangent = cubic_bezier(points, t)
        if tangent.length < 1e-10:
            raise ValueError(f"{name} has a zero-length tangent")
        tangent.normalize()
        normal = Vector((-tangent.y, tangent.x))
        root_amount = smoothstep((t - 0.62) / 0.38)
        local_side_radius = side_radius + (root_side_radius - side_radius) * root_amount
        local_x_radius = x_radius + (root_x_radius - x_radius) * root_amount
        ring = []
        for ring_step in range(RING_STEPS):
            angle = 2.0 * math.pi * ring_step / RING_STEPS
            yz = center + normal * (local_side_radius * math.sin(angle))
            ring.append(bm.verts.new((local_x_radius * math.cos(angle), yz.x, yz.y)))
        loops.append(ring)
    for lower, upper in zip(loops, loops[1:]):
        for index in range(RING_STEPS):
            following = (index + 1) % RING_STEPS
            bm.faces.new((lower[index], upper[index], upper[following], lower[following]))
    bm.faces.new(tuple(reversed(loops[0])))
    bm.faces.new(tuple(loops[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return object_from_bmesh(name, bm)


def join_objects(objects, name):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    objects[0].name = name
    return objects[0]


def clean_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=CLEANUP_DISTANCE)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-10)
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-9)
    previous_tiny_count = None
    for _ in range(8):
        tiny_faces = [face for face in bm.faces if face.calc_area() < 1e-12]
        if not tiny_faces:
            break
        if previous_tiny_count is not None and len(tiny_faces) >= previous_tiny_count:
            break
        previous_tiny_count = len(tiny_faces)
        collapse_edges = {min(face.edges, key=lambda edge: edge.calc_length())
                          for face in tiny_faces}
        bmesh.ops.collapse(bm, edges=list(collapse_edges), uvs=True)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-10)
        bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
    loose = [vertex for vertex in bm.verts if not vertex.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.validate(verbose=True)
    obj.data.update()


def apply_voxel_fusion(obj):
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new("flow_fusion", "REMESH")
    modifier.mode = "VOXEL"
    modifier.voxel_size = REMESH_VOXEL
    modifier.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    if SMOOTH_ITERATIONS:
        modifier = obj.modifiers.new("surface_relax", "SMOOTH")
        modifier.factor = SMOOTH_FACTOR
        modifier.iterations = SMOOTH_ITERATIONS
        bpy.ops.object.modifier_apply(modifier=modifier.name)


def normalize_xy_bounds(obj):
    low_x = min(vertex.co.x for vertex in obj.data.vertices)
    high_x = max(vertex.co.x for vertex in obj.data.vertices)
    low_y = min(vertex.co.y for vertex in obj.data.vertices)
    high_y = max(vertex.co.y for vertex in obj.data.vertices)
    center_x = (low_x + high_x) / 2.0
    scale_x = FOOT_WIDTH / (high_x - low_x)
    scale_y = FOOT_DEPTH / (high_y - low_y)
    for vertex in obj.data.vertices:
        vertex.co.x = (vertex.co.x - center_x) * scale_x
        vertex.co.y = FOOT_FRONT_Y + (vertex.co.y - low_y) * scale_y
    obj.data.update()


def create_clip_box():
    bpy.ops.mesh.primitive_cube_add(location=(0.0, FOOT_FRONT_Y + FOOT_DEPTH / 2.0,
                                               BODY_HEIGHT / 2.0))
    clip = bpy.context.object
    clip.name = "dimension_clip"
    clip.dimensions = (FOOT_WIDTH + 2.0 * CLIP_OVERLAP,
                       FOOT_DEPTH + 2.0 * CLIP_OVERLAP,
                       BODY_HEIGHT)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return clip


def clip_to_dimensions(body):
    clip = create_clip_box()
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    modifier = body.modifiers.new("exact_dimensions", "BOOLEAN")
    modifier.operation = "INTERSECT"
    modifier.solver = "EXACT"
    modifier.object = clip
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(clip, do_unlink=True)
    clean_mesh(body)


def mesh_metrics(obj, label):
    bpy.context.view_layer.update()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if not bm.verts or not bm.faces:
        bm.free()
        raise RuntimeError(f"{label} mesh is empty")
    non_manifold = sum(not edge.is_manifold for edge in bm.edges)
    degenerate = sum(face.calc_area() < 1e-12 for face in bm.faces)
    volume = bm.calc_volume(signed=True)
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
        "signed_volume_mm3": volume * 1e9,
        "dimensions_mm": tuple(value * 1000.0 for value in high - low),
        "minimum_mm": tuple(value * 1000.0 for value in low),
        "maximum_mm": tuple(value * 1000.0 for value in high),
    }
    print(f"[{MODEL_NAME}] {label}", result)
    if components != 1 or non_manifold or degenerate or volume <= 0:
        raise RuntimeError(f"invalid {label} mesh: {result}")
    return result


def verify_contact_planes(body):
    samples = []
    for label, y_start in (("top_front", PAD_FRONT_Y), ("top_rear", PAD_REAR_Y)):
        y = y_start + PAD_LENGTH / 2.0
        for x in (-PAD_WIDTH / 2.0, 0.0, PAD_WIDTH / 2.0):
            hit, location, normal, _ = body.ray_cast((x, y, BODY_HEIGHT + 0.010),
                                                      (0.0, 0.0, -1.0),
                                                      distance=BODY_HEIGHT + 0.020)
            if not hit or abs(location.z - BODY_HEIGHT) > 0.00005 or normal.z < 0.99:
                raise RuntimeError(f"{label} pad sample is not on the top plane")
            samples.append((label, x * 1000.0, y * 1000.0, location.z * 1000.0))
    for label, y_start in (("base_front", BASE_PAD_FRONT_Y), ("base_rear", BASE_PAD_REAR_Y)):
        y = y_start + BASE_PAD_LENGTH / 2.0
        for x in (-BASE_PAD_WIDTH / 2.0, 0.0, BASE_PAD_WIDTH / 2.0):
            hit, location, normal, _ = body.ray_cast((x, y, -0.010),
                                                      (0.0, 0.0, 1.0),
                                                      distance=BODY_HEIGHT + 0.020)
            if not hit or abs(location.z) > 0.00005 or normal.z > -0.99:
                raise RuntimeError(f"{label} pad sample is not on the bottom plane")
            samples.append((label, x * 1000.0, y * 1000.0, location.z * 1000.0))
    print(f"[{MODEL_NAME}] contact_plane_samples_mm", samples)


def build_body():
    # The planted footprint rolls continuously into a narrow rounded ridge.
    # No horizontal platform remains around the roots of the curved supports.
    foot_center = FOOT_FRONT_Y + FOOT_DEPTH / 2
    foot = create_layered_prism("foot", [
        (z, rounded_rectangle(width, foot_center - depth / 2, depth,
                               min(FOOT_ROUND, width * 0.48), segments=32))
        for z, width, depth in FOOT_PROFILE
    ])
    top = create_rounded_prism(
        "top_beam",
        UPPER_WIDTH,
        0.0,
        FRAME_DEPTH,
        TOP_END_RADIUS,
        BODY_HEIGHT - TOP_BEAM - 0.001,
        BODY_HEIGHT + CLIP_OVERLAP,
        TOP_EDGE_RADIUS,
    )
    main_s = create_bezier_sweep(
        "main_s_support", S_CURVE_POINTS, S_SIDE_RADIUS, S_X_RADIUS,
        S_ROOT_SIDE_RADIUS, S_ROOT_X_RADIUS,
    )
    rear = create_bezier_sweep(
        "rear_support", REAR_CURVE_POINTS, REAR_SIDE_RADIUS, REAR_X_RADIUS,
        REAR_ROOT_SIDE_RADIUS, REAR_ROOT_X_RADIUS,
    )
    body = join_objects((foot, top, main_s, rear), "body_local")
    apply_voxel_fusion(body)
    normalize_xy_bounds(body)
    clip_to_dimensions(body)
    for polygon in body.data.polygons:
        heights = [body.data.vertices[index].co.z for index in polygon.vertices]
        is_cap = (max(abs(z) for z in heights) < 1e-7 or
                  max(abs(z - BODY_HEIGHT) for z in heights) < 1e-7)
        polygon.use_smooth = not is_cap
    body.data.update()
    metrics = mesh_metrics(body, "body_local")
    expected = (FOOT_WIDTH * 1000.0, FOOT_DEPTH * 1000.0, BODY_HEIGHT * 1000.0)
    if any(abs(actual - target) > 0.05 for actual, target in zip(metrics["dimensions_mm"], expected)):
        raise RuntimeError("body dimensions differ from the specification")
    expected_minimum = (-FOOT_WIDTH * 500.0, FOOT_FRONT_Y * 1000.0, 0.0)
    if any(abs(actual - target) > 0.05 for actual, target in zip(metrics["minimum_mm"], expected_minimum)):
        raise RuntimeError("body minimum bounds differ from the specification")
    verify_contact_planes(body)
    return body


def copy_object(source, name):
    result = source.copy()
    result.data = source.data.copy()
    result.name = name
    bpy.context.collection.objects.link(result)
    return result


def keep_only(objects):
    retained = set(objects)
    for other in list(bpy.context.scene.objects):
        if other not in retained:
            bpy.data.objects.remove(other, do_unlink=True)
    actual = {obj.name for obj in bpy.context.scene.objects if obj.type == "MESH"}
    expected = {obj.name for obj in objects}
    if actual != expected:
        raise RuntimeError(f"unexpected scene meshes: {sorted(actual)}")


def make_print_body(body):
    result = copy_object(body, "body")
    center_y = FOOT_FRONT_Y + FOOT_DEPTH / 2.0
    root_two = math.sqrt(2.0)
    for vertex in result.data.vertices:
        x, y, z = vertex.co
        y -= center_y
        vertex.co = ((x - y) / root_two, (x + y) / root_two, z)
    result.data.update()
    clean_mesh(result)
    metrics = mesh_metrics(result, "print_body")
    extreme = max(result.data.vertices, key=lambda vertex: vertex.co.x)
    print(f"[{MODEL_NAME}] print_positive_x_extreme_mm",
          tuple(value * 1000.0 for value in extreme.co))
    if max(metrics["dimensions_mm"][:2]) + 8.0 > 248.40:
        raise RuntimeError("45-degree print body exceeds the 248.4 mm brim target")
    return result


def build_assembly(body_mesh):
    clear_scene()
    left = bpy.data.objects.new("left_body", body_mesh.copy())
    right = bpy.data.objects.new("right_body", body_mesh.copy())
    for obj, x in ((left, -RAIL_CENTER), (right, RAIL_CENTER)):
        bpy.context.collection.objects.link(obj)
        obj.location = (x, 0.0, PAD_THICKNESS)
        mesh_metrics(obj, obj.name)
    keep_only((left, right))
    corners = [obj.matrix_world @ Vector(corner) for obj in (left, right) for corner in obj.bound_box]
    low = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
    high = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
    dimensions = tuple(value * 1000.0 for value in high - low)
    print(f"[{MODEL_NAME}] assembly_components 2")
    print(f"[{MODEL_NAME}] assembly_dimensions_mm", dimensions)
    print(f"[{MODEL_NAME}] assembly_minimum_mm", tuple(value * 1000.0 for value in low))
    expected = ((2.0 * RAIL_CENTER + FOOT_WIDTH) * 1000.0,
                FOOT_DEPTH * 1000.0, BODY_HEIGHT * 1000.0)
    if any(abs(actual - target) > 0.05 for actual, target in zip(dimensions, expected)):
        raise RuntimeError("assembly dimensions differ from the specification")
    if abs(low.z - PAD_THICKNESS) > 0.00005:
        raise RuntimeError("assembly bottom is not on the lower pads")
    return left, right


def main():
    clear_scene()
    bpy.context.preferences.filepaths.save_version = 0
    body = build_body()
    body_mesh = body.data.copy()

    print_body = make_print_body(body)
    keep_only((print_body,))
    export_stl(f"{MODEL_NAME}/body", only=[print_body])

    assembly = build_assembly(body_mesh)
    export_stl(MODEL_NAME, only=list(assembly))


if __name__ == "__main__":
    main()
