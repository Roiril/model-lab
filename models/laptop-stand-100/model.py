"""2つの曲線開口を持つ連続曲面の100 mm高ノートPCスタンドを生成する。"""
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


def rounded_rectangle_xy(width, depth, radius):
    """円弧端点を含む132点の角丸長方形を反時計回りで返す。"""
    half_width = width / 2.0
    y_min = (FRAME_DEPTH - depth) / 2.0
    y_max = y_min + depth
    per_corner = LOFT_PROFILE_POINTS // 4
    corners = (
        (-half_width + radius, y_min + radius, math.pi, 1.5 * math.pi),
        (half_width - radius, y_min + radius, -0.5 * math.pi, 0.0),
        (half_width - radius, y_max - radius, 0.0, 0.5 * math.pi),
        (-half_width + radius, y_max - radius, 0.5 * math.pi, math.pi),
    )
    result = [
        (center_x + radius * math.cos(start + (end - start) * step / (per_corner - 1)),
         center_y + radius * math.sin(start + (end - start) * step / (per_corner - 1)))
        for center_x, center_y, start, end in corners
        for step in range(per_corner)
    ]
    if len(result) != LOFT_PROFILE_POINTS:
        raise RuntimeError("rounded rectangle profile has an unexpected point count")
    return result


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
    point_count = len(layers[0][1])
    if point_count < 3 or any(len(profile) != point_count for _, profile in layers):
        raise ValueError("loft profiles must have the same point count")
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


def rounded_polygon(points, radii, segments=8):
    """各頂点を指定半径の接線円弧で結んだ反時計回り輪郭を返す。"""
    result = []
    count = len(points)
    for index, point in enumerate(points):
        previous = Vector(points[(index - 1) % count])
        current = Vector(point)
        following = Vector(points[(index + 1) % count])
        incoming = (current - previous).normalized()
        outgoing = (following - current).normalized()
        interior = math.acos(max(-1.0, min(1.0, (-incoming).dot(outgoing))))
        radius = radii[index]
        tangent_distance = radius / math.tan(interior / 2.0)
        if tangent_distance >= min((current - previous).length, (following - current).length) / 2.0:
            raise ValueError("fillet radius is too large for opening profile")
        start = current - incoming * tangent_distance
        center = start + Vector((-incoming.y, incoming.x)) * radius
        end = current + outgoing * tangent_distance
        start_angle = math.atan2(start.y - center.y, start.x - center.x)
        end_angle = math.atan2(end.y - center.y, end.x - center.x)
        while end_angle <= start_angle:
            end_angle += 2.0 * math.pi
        result.extend(tuple(center + Vector((
            math.cos(start_angle + (end_angle - start_angle) * step / segments),
            math.sin(start_angle + (end_angle - start_angle) * step / segments),
        )) * radius) for step in range(segments + 1))
    return result


def opening_profile(center_y):
    shoulder_z = HOLE_THEORETICAL_PEAK - HOLE_ROOF_SLOPE * HOLE_HALF_WIDTH
    points = (
        (center_y - HOLE_HALF_WIDTH, HOLE_FLOOR),
        (center_y + HOLE_HALF_WIDTH, HOLE_FLOOR),
        (center_y + HOLE_HALF_WIDTH, shoulder_z),
        (center_y, HOLE_THEORETICAL_PEAK),
        (center_y - HOLE_HALF_WIDTH, shoulder_z),
    )
    return rounded_polygon(
        points,
        (HOLE_FLOOR_R, HOLE_FLOOR_R, HOLE_SHOULDER_R,
         HOLE_CROWN_R, HOLE_SHOULDER_R),
    )


def create_prism_cutter(name, profile):
    """穴の内面から外面までを丸い断面でつなぐ閉じたカッター。"""
    points = [Vector(point) for point in profile]
    outward = []
    for index, point in enumerate(points):
        incoming = (point - points[index - 1]).normalized()
        outgoing = (points[(index + 1) % len(points)] - point).normalized()
        previous_normal = Vector((incoming.y, -incoming.x))
        following_normal = Vector((outgoing.y, -outgoing.x))
        bisector = (previous_normal + following_normal).normalized()
        outward.append(bisector / bisector.dot(previous_normal))

    def ring(side, theta, outside=False):
        offset = HOLE_EDGE_R * (1.0 - math.cos(theta))
        result = []
        for point, normal in zip(points, outward):
            y, z = point + normal * offset
            width, *_ = flow_section(z)
            x = .060 if outside else width / 2.0 - HOLE_EDGE_R * (1.0 - math.sin(theta))
            if not outside:
                x += 1e-7 * math.sin(theta) ** 2
            result.append((side * x, y, z))
        return result

    # The cutter carries the rounding itself. Beveling a Boolean-created face
    # with two holes can fold its connecting triangles into the exterior face.
    angles = [math.pi * step / 16.0 for step in range(9)]
    rings = [ring(-1, math.pi / 2, outside=True)]
    rings.extend(ring(-1, theta) for theta in reversed(angles))
    rings.extend(ring(1, theta) for theta in angles)
    rings.append(ring(1, math.pi / 2, outside=True))
    bm = bmesh.new()
    loops = [[bm.verts.new(co) for co in coordinates] for coordinates in rings]
    count = len(profile)
    for low, high in zip(loops, loops[1:]):
        for index in range(count):
            following = (index + 1) % count
            bm.faces.new((low[index], low[following], high[following], high[index]))
    bm.faces.new(tuple(reversed(loops[0])))
    bm.faces.new(tuple(loops[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return object_from_bmesh(name, bm)


def clean_mesh(obj, triangulate=True):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=CLEANUP_DISTANCE)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-10)
    if triangulate:
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


def flow_section(z):
    """外形曲面とその接線を同じ寸法式から求める。"""
    height = z - BOTTOM_CHAMFER
    raw = math.exp(-((height / FLOW_HEIGHT) ** 2))
    raw_derivative = -2.0 * height * raw / FLOW_HEIGHT ** 2
    # Fade the last small tail to an exactly planar upper surface. Its position,
    # slope and curvature are continuous at both ends of this transition.
    fade_start, fade_end = 2.0 * FLOW_HEIGHT, 2.6 * FLOW_HEIGHT
    amount = (height - fade_start) / (fade_end - fade_start)
    if amount <= 0:
        weight, weight_derivative = 1.0, 0.0
    elif amount >= 1:
        weight, weight_derivative = 0.0, 0.0
    else:
        weight = 1.0 - (6 * amount ** 5 - 15 * amount ** 4 + 10 * amount ** 3)
        weight_derivative = -30 * amount ** 2 * (amount - 1) ** 2 / (fade_end - fade_start)
    f = raw * weight
    derivative = raw_derivative * weight + raw * weight_derivative
    return (
        UPPER_WIDTH + (FOOT_WIDTH - UPPER_WIDTH) * f,
        FLOW_UPPER_DEPTH + (FOOT_DEPTH - FLOW_UPPER_DEPTH) * f,
        FLOW_UPPER_ROUND + (FOOT_ROUND - FLOW_UPPER_ROUND) * f,
        (FOOT_WIDTH - UPPER_WIDTH) * derivative,
        (FOOT_DEPTH - FLOW_UPPER_DEPTH) * derivative,
        (FOOT_ROUND - FLOW_UPPER_ROUND) * derivative,
    )


def shade_continuous_outer_surface(body):
    """穴加工で不均一になった頂点の陰影を実際の外形接線へ戻す。"""
    mesh = body.data
    mesh.update()
    normals = [tuple(normal.vector) for normal in mesh.corner_normals]
    adjusted = 0
    for loop in mesh.loops:
        x, y, z = mesh.vertices[loop.vertex_index].co
        if z < BOTTOM_CHAMFER or z > BODY_HEIGHT + 1e-7:
            continue
        if z <= FLOW_TOP_Z:
            width, depth, radius, width_d, depth_d, radius_d = flow_section(z)
            horizontal_factor = 1.0
            vertical_factor = None
        else:
            theta = math.asin(max(0.0, min(1.0, (z - FLOW_TOP_Z) / TOP_FILLET)))
            offset = TOP_FILLET * (1.0 - math.cos(theta))
            width = UPPER_WIDTH - 2.0 * offset
            depth = FLOW_UPPER_DEPTH - 2.0 * offset
            radius = FLOW_UPPER_ROUND - offset
            horizontal_factor = math.cos(theta)
            vertical_factor = math.sin(theta)
        minimum_y = (FRAME_DEPTH - depth) / 2.0
        maximum_y = (FRAME_DEPTH + depth) / 2.0
        side_sign = 1.0 if x >= 0 else -1.0
        end_sign = 1.0 if y >= FRAME_DEPTH / 2.0 else -1.0
        corner_x = side_sign * (width / 2.0 - radius)
        corner_y = maximum_y - radius if end_sign > 0 else minimum_y + radius
        # The whole outer outline uses the same tangent field. A Boolean-created
        # large triangle must not interpolate between corrected sides and an
        # uncorrected round end. Opening rolls and interior faces stay untouched.
        tolerance = .00008
        if minimum_y + radius <= y <= maximum_y - radius:
            if abs(abs(x) - width / 2.0) > tolerance:
                continue
            nx, ny = side_sign, 0.0
            nz = -width_d / 2.0 if vertical_factor is None else vertical_factor
        elif abs(x) <= width / 2.0 - radius:
            edge_y = maximum_y if end_sign > 0 else minimum_y
            if abs(y - edge_y) > tolerance:
                continue
            nx, ny = 0.0, end_sign
            nz = -depth_d / 2.0 if vertical_factor is None else vertical_factor
        else:
            radial = Vector((x - corner_x, y - corner_y))
            if abs(radial.length - radius) > tolerance:
                continue
            radial.normalize()
            nx, ny = radial
            if vertical_factor is None:
                center_x_d = side_sign * (width_d / 2.0 - radius_d)
                center_y_d = end_sign * (depth_d / 2.0 - radius_d)
                nz = -nx * center_x_d - ny * center_y_d - radius_d
            else:
                nz = vertical_factor
        normal = Vector((nx * horizontal_factor, ny * horizontal_factor, nz))
        if normal.length < 1e-8:
            continue
        normal.normalize()
        normals[loop.index] = tuple(normal)
        adjusted += 1
    if not adjusted:
        raise RuntimeError("No outer-surface corner normals were assigned")
    mesh.normals_split_custom_set(normals)
    print(f"[{MODEL_NAME}] continuous_outer_corner_normals", adjusted)


def build_body():
    layers = [
        (0.0, rounded_rectangle_xy(FOOT_WIDTH - 2.0 * BOTTOM_CHAMFER,
                                   FOOT_DEPTH - 2.0 * BOTTOM_CHAMFER,
                                   FOOT_ROUND - BOTTOM_CHAMFER)),
        (BOTTOM_CHAMFER, rounded_rectangle_xy(FOOT_WIDTH, FOOT_DEPTH, FOOT_ROUND)),
    ]
    for step in range(FLOW_STEPS + 1):
        z = BOTTOM_CHAMFER + (FLOW_TOP_Z - BOTTOM_CHAMFER) * step / FLOW_STEPS
        width, depth, radius, *_ = flow_section(z)
        if step == 0:
            layers[-1] = (z, rounded_rectangle_xy(width, depth, radius))
        else:
            layers.append((z, rounded_rectangle_xy(width, depth, radius)))
    for step in range(1, TOP_FILLET_STEPS + 1):
        theta = 0.5 * math.pi * step / TOP_FILLET_STEPS
        offset = TOP_FILLET * (1.0 - math.cos(theta))
        z = FLOW_TOP_Z + TOP_FILLET * math.sin(theta)
        layers.append((z, rounded_rectangle_xy(
            UPPER_WIDTH - 2.0 * offset,
            FLOW_UPPER_DEPTH - 2.0 * offset,
            FLOW_UPPER_ROUND - offset,
        )))
    body = create_closed_loft("body_local", layers)
    profiles = [opening_profile(center) for center in HOLE_CENTERS]
    for index, profile in enumerate(profiles, start=1):
        cutter = create_prism_cutter(f"opening_{index}_cutter", profile)
        bpy.context.view_layer.objects.active = body
        body.select_set(True)
        modifier = body.modifiers.new(f"opening_{index}", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
    clean_mesh(body)
    for polygon in body.data.polygons:
        polygon.use_smooth = polygon.normal.z < 0.999
    body.data.update()
    shade_continuous_outer_surface(body)
    metrics = mesh_metrics(body, "body_local")
    expected = (FOOT_WIDTH * 1000.0, FOOT_DEPTH * 1000.0, BODY_HEIGHT * 1000.0)
    if any(abs(actual - target) > 0.03 for actual, target in zip(metrics["dimensions_mm"], expected)):
        raise RuntimeError("body dimensions differ from the specification")
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
    root_two = math.sqrt(2.0)
    normals = [tuple(normal.vector) for normal in result.data.corner_normals]
    for vertex in result.data.vertices:
        x, y, z = vertex.co
        vertex.co = ((x - (y - FRAME_DEPTH / 2.0)) / root_two,
                     (x + y - FRAME_DEPTH / 2.0) / root_two,
                     z)
    result.data.update()
    result.data.normals_split_custom_set([
        ((x - y) / root_two, (x + y) / root_two, z) for x, y, z in normals
    ])
    mesh_metrics(result, "print_body")
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
    if any(abs(actual - target) > 0.03 for actual, target in zip(dimensions, expected)):
        raise RuntimeError("assembly dimensions differ from the specification")
    if abs(low.z - PAD_THICKNESS) > 1e-8 or abs(high.z - (PAD_THICKNESS + BODY_HEIGHT)) > 1e-8:
        raise RuntimeError("assembly Z bounds differ from the specification")
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
