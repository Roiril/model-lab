"""Photo-dimensioned SG92R servo body and asymmetric cross horn."""

import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bmesh
import bpy
from mathutils import Vector

from blender_utils import EXPORTS_DIR, clear_scene, export_stl
from params import *


EPS = 0.00002  # 0.02 mm overlap keeps adjacent solids stable under EXACT union


def require_positive(*names):
    for name in names:
        if globals()[name] <= 0:
            raise ValueError(f"{name} must be positive")


require_positive(
    "BODY_L", "BODY_W", "BODY_H", "FLANGE_L", "FLANGE_W", "FLANGE_T",
    "GEAR_COVER_L", "GEAR_COVER_W", "GEAR_COVER_H", "SHAFT_DIA", "SHAFT_H",
    "HORN_SPAN_Y", "HORN_ROOT_W", "HORN_TIP_W", "HORN_SHORT_W", "HORN_ARM_T",
    "HORN_HUB_DIA", "MOUNT_HOLE_SPACING", "MOUNT_HOLE_DIA", "HORN_SOCKET_DIA",
    "CENTER_HOLE_DIA", "ARM_HOLE_DIA",
)
if HORN_LEFT_X >= 0 or HORN_RIGHT_X <= 0:
    raise ValueError("The long horn arm must span both sides of the shaft origin")
if HORN_TIP_W > HORN_ROOT_W or HORN_SHORT_W > HORN_HUB_DIA:
    raise ValueError("Horn arm widths must fit the hub and taper toward the tips")
if HORN_SOCKET_TOP_Z <= HORN_HUB_BOTTOM_Z or HORN_SOCKET_TOP_Z >= HORN_TOP_Z:
    raise ValueError("Horn socket top must be inside the hub")


def add_box(name, size, location):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = tuple(value / 2 for value in size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def add_cylinder(name, diameter, height, location, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=diameter / 2, depth=height, location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def boolean(target, other, operation):
    modifier = target.modifiers.new(f"{operation.lower()}_{other.name}", "BOOLEAN")
    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = other
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(other, do_unlink=True)


def union(target, *parts):
    for part in parts:
        boolean(target, part, "UNION")
    return target


def add_capsule_x(name, left, right, width, bottom, top):
    radius = width / 2
    if right - left <= width:
        raise ValueError(f"{name} length must be greater than its width")
    height = top - bottom
    z = (bottom + top) / 2
    left_center = left + radius
    right_center = right - radius
    base = add_box(name, (right_center - left_center + 2 * EPS, width, height),
                   ((left_center + right_center) / 2, 0, z))
    return union(
        base,
        add_cylinder(f"{name}_left", width, height, (left_center, 0, z)),
        add_cylinder(f"{name}_right", width, height, (right_center, 0, z)),
    )


def add_capsule_y(name, span, width, bottom, top):
    radius = width / 2
    if span <= width:
        raise ValueError(f"{name} span must be greater than its width")
    height = top - bottom
    z = (bottom + top) / 2
    end_center = span / 2 - radius
    base = add_box(name, (width, 2 * end_center + 2 * EPS, height), (0, 0, z))
    return union(
        base,
        add_cylinder(f"{name}_front", width, height, (0, end_center, z)),
        add_cylinder(f"{name}_back", width, height, (0, -end_center, z)),
    )


def add_long_arm(name):
    radius = HORN_TIP_W / 2
    left_center = HORN_LEFT_X + radius
    right_center = HORN_RIGHT_X - radius
    root_x = HORN_HUB_DIA / 2
    root_half = HORN_ROOT_W / 2
    points = []
    for i in range(9):
        angle = math.pi + i * math.pi / 16
        points.append((left_center + radius * math.cos(angle), radius * math.sin(angle)))
    points.extend([(-root_x, -root_half), (root_x, -root_half), (right_center, -radius)])
    for i in range(1, 17):
        angle = -math.pi / 2 + i * math.pi / 16
        points.append((right_center + radius * math.cos(angle), radius * math.sin(angle)))
    points.extend([(root_x, root_half), (-root_x, root_half), (left_center, radius)])
    for i in range(1, 9):
        angle = math.pi / 2 + i * math.pi / 16
        points.append((left_center + radius * math.cos(angle), radius * math.sin(angle)))

    bottom = HORN_ARM_BOTTOM_Z
    top = HORN_ARM_BOTTOM_Z + HORN_ARM_T
    vertices = [(x, y, bottom) for x, y in points] + [(x, y, top) for x, y in points]
    count = len(points)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, count + j, count + i))
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def material(name, color, metallic=0.0, roughness=0.45, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, alpha)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, alpha)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1:
        mat.surface_render_method = "DITHERED"
    return mat


def build_body():
    body = add_box(
        "sg92r-photo-body",
        (BODY_L, BODY_W, BODY_H),
        (BODY_CENTER_X, 0, BODY_H / 2),
    )
    flange = add_capsule_x(
        "mounting_flange",
        BODY_CENTER_X - FLANGE_L / 2,
        BODY_CENTER_X + FLANGE_L / 2,
        FLANGE_W,
        FLANGE_BOTTOM_Z,
        FLANGE_BOTTOM_Z + FLANGE_T,
    )
    cover = add_capsule_x(
        "gear_cover",
        GEAR_COVER_LEFT_X,
        GEAR_COVER_LEFT_X + GEAR_COVER_L,
        GEAR_COVER_W,
        GEAR_COVER_BOTTOM_Z - EPS,
        GEAR_COVER_BOTTOM_Z + GEAR_COVER_H,
    )
    shaft = add_cylinder(
        "output_shaft",
        SHAFT_DIA,
        SHAFT_H + EPS,
        (0, 0, SHAFT_BOTTOM_Z + (SHAFT_H - EPS) / 2),
    )
    union(body, flange, cover, shaft)
    hole_z = FLANGE_BOTTOM_Z + FLANGE_T / 2
    for sign in (-1, 1):
        hole = add_cylinder(
            "mount_hole",
            MOUNT_HOLE_DIA,
            FLANGE_T + 0.002,
            (BODY_CENTER_X + sign * MOUNT_HOLE_SPACING / 2, 0, hole_z),
            vertices=48,
        )
        boolean(body, hole, "DIFFERENCE")
    body.name = "sg92r-photo-body"
    body.data.materials.append(material("SG92R translucent blue", (0.025, 0.12, 0.8), alpha=0.72))
    return body


def build_horn():
    horn = add_long_arm("sg92r-photo-horn")
    short_arm = add_capsule_y(
        "short_arm", HORN_SPAN_Y, HORN_SHORT_W,
        HORN_ARM_BOTTOM_Z, HORN_ARM_BOTTOM_Z + HORN_ARM_T,
    )
    hub = add_cylinder(
        "horn_hub", HORN_HUB_DIA, HORN_TOP_Z - HORN_HUB_BOTTOM_Z,
        (0, 0, (HORN_HUB_BOTTOM_Z + HORN_TOP_Z) / 2),
    )
    union(horn, short_arm, hub)

    socket = add_cylinder(
        "shaft_socket", HORN_SOCKET_DIA,
        HORN_SOCKET_TOP_Z - HORN_HUB_BOTTOM_Z + EPS,
        (0, 0, (HORN_HUB_BOTTOM_Z + HORN_SOCKET_TOP_Z - EPS) / 2),
    )
    boolean(horn, socket, "DIFFERENCE")
    center_hole = add_cylinder(
        "center_hole", CENTER_HOLE_DIA,
        HORN_TOP_Z - HORN_SOCKET_TOP_Z + 2 * EPS,
        (0, 0, (HORN_SOCKET_TOP_Z + HORN_TOP_Z) / 2),
        vertices=48,
    )
    boolean(horn, center_hole, "DIFFERENCE")

    for x in (*ARM_HOLES_X_LEFT, *ARM_HOLES_X_RIGHT):
        cutter = add_cylinder(
            "arm_hole_x", ARM_HOLE_DIA, HORN_ARM_T + 0.002,
            (x, 0, HORN_ARM_BOTTOM_Z + HORN_ARM_T / 2), vertices=32,
        )
        boolean(horn, cutter, "DIFFERENCE")
    for y in ARM_HOLES_Y:
        cutter = add_cylinder(
            "arm_hole_y", ARM_HOLE_DIA, HORN_ARM_T + 0.002,
            (0, y, HORN_ARM_BOTTOM_Z + HORN_ARM_T / 2), vertices=32,
        )
        boolean(horn, cutter, "DIFFERENCE")
    horn.name = "sg92r-photo-horn"
    horn.data.materials.append(material("Horn black", (0.008, 0.008, 0.012), roughness=0.3))
    return horn


def object_bbox_mm(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(point[axis] for point in corners) for axis in range(3)]
    maxs = [max(point[axis] for point in corners) for axis in range(3)]
    return {
        "min": [round(value * 1000, 4) for value in mins],
        "max": [round(value * 1000, 4) for value in maxs],
        "size": [round((maxs[i] - mins[i]) * 1000, 4) for i in range(3)],
    }


def mesh_metrics(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
    unseen = set(bm.verts)
    components = 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            vertex = stack.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in unseen:
                    unseen.remove(other)
                    stack.append(other)
    bm.free()
    return {"nonManifoldEdges": non_manifold, "connectedComponents": components}


def write_validation(body, horn):
    boxes = [object_bbox_mm(body), object_bbox_mm(horn)]
    assembly_min = [min(box["min"][i] for box in boxes) for i in range(3)]
    assembly_max = [max(box["max"][i] for box in boxes) for i in range(3)]
    data = {
        "units": "mm",
        "body": {"bbox": boxes[0], **mesh_metrics(body)},
        "horn": {"bbox": boxes[1], **mesh_metrics(horn)},
        "assembly": {
            "bbox": {
                "min": assembly_min,
                "max": assembly_max,
                "size": [round(assembly_max[i] - assembly_min[i], 4) for i in range(3)],
            },
            "separateClosedParts": 2,
        },
        "note": "The photo-consistent flange is centred at body X=-5 mm, so the assembly X envelope is 37 mm rather than 34 mm.",
    }
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    path = os.path.join(EXPORTS_DIR, "sg92r-photo-validation.json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print("Validation:", path)
    print(json.dumps(data, ensure_ascii=False))


clear_scene()
body = build_body()
horn = build_horn()

export_stl("sg92r-photo-body", only=[body])
export_stl("sg92r-photo-horn", only=[horn])
export_stl("sg92r-photo", only=[body, horn])
write_validation(body, horn)
