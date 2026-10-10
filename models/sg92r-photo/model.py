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
from profiles import load_profile

_profile = load_profile(os.environ.get("SG92R_PROFILE", "approved"), globals())
globals().update(vars(_profile))


EPS = 0.00002  # 0.02 mm overlap keeps adjacent solids stable under EXACT union


def require_positive(*names):
    for name in names:
        if globals()[name] <= 0:
            raise ValueError(f"{name} must be positive")


require_positive(
    "BODY_L", "BODY_W", "BODY_H", "FLANGE_L", "FLANGE_W", "FLANGE_T",
    "GEAR_COVER_L", "GEAR_COVER_W", "GEAR_NECK_DIA", "GEAR_COVER_H", "SHAFT_DIA", "SHAFT_H",
    "HORN_SPAN_Y", "HORN_ROOT_W", "HORN_TIP_W", "HORN_SHORT_W", "HORN_ARM_T",
    "HORN_HUB_DIA", "MOUNT_HOLE_SPACING", "MOUNT_HOLE_DIA", "MOUNT_SLOT_W",
    "WIRE_W", "WIRE_LENGTH", "WIRE_T", "WIRE_EXIT_Z", "HORN_SOCKET_DIA",
    "CENTER_HOLE_DIA", "ARM_HOLE_DIA",
)
if HORN_LEFT_X >= 0 or HORN_RIGHT_X <= 0:
    raise ValueError("The long horn arm must span both sides of the shaft origin")
if HORN_TIP_W > HORN_ROOT_W or HORN_SHORT_W > HORN_HUB_DIA:
    raise ValueError("Horn arm widths must fit the hub and taper toward the tips")
if HORN_SOCKET_TOP_Z <= HORN_HUB_BOTTOM_Z or HORN_SOCKET_TOP_Z >= HORN_TOP_Z:
    raise ValueError("Horn socket top must be inside the hub")
if (WIRE_W - WIRE_T) / 2 >= WIRE_T or WIRE_T >= WIRE_LENGTH:
    raise ValueError("Cable dimensions must make the three wires overlap along their length")


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


def add_cylinder_x(name, diameter, length, location, vertices=48):
    obj = add_cylinder(name, diameter, length, location, vertices)
    obj.rotation_euler[1] = math.pi / 2
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
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
    flange = add_box(
        "mounting_flange", (FLANGE_L, FLANGE_W, FLANGE_T),
        (BODY_CENTER_X, 0, FLANGE_BOTTOM_Z + FLANGE_T / 2),
    )
    cover_z = GEAR_COVER_BOTTOM_Z + GEAR_COVER_H / 2 - EPS / 2
    cover = add_cylinder(
        "gear_cover", GEAR_COVER_W, GEAR_COVER_H + EPS, (0, 0, cover_z)
    )
    neck_center_x = -GEAR_COVER_L + GEAR_COVER_W / 2 + GEAR_NECK_DIA / 2
    union(cover, add_cylinder(
        "gear_cover_neck", GEAR_NECK_DIA, GEAR_COVER_H + EPS,
        (neck_center_x, 0, cover_z),
    ))
    shaft = add_cylinder(
        "output_shaft",
        SHAFT_DIA,
        SHAFT_H + EPS,
        (0, 0, SHAFT_BOTTOM_Z + (SHAFT_H - EPS) / 2),
    )
    union(body, flange, cover, shaft)
    hole_z = FLANGE_BOTTOM_Z + FLANGE_T / 2
    for sign in (-1, 1):
        hole_x = BODY_CENTER_X + sign * MOUNT_HOLE_SPACING / 2
        hole = add_cylinder(
            "mount_hole",
            MOUNT_HOLE_DIA,
            FLANGE_T + 0.002,
            (hole_x, 0, hole_z),
            vertices=48,
        )
        boolean(body, hole, "DIFFERENCE")
        outer_x = BODY_CENTER_X + sign * (FLANGE_L / 2 + 0.0005)
        slot = add_box(
            "mount_slot",
            (abs(outer_x - hole_x), MOUNT_SLOT_W, FLANGE_T + 0.002),
            ((outer_x + hole_x) / 2, 0, hole_z),
        )
        boolean(body, slot, "DIFFERENCE")
    body.name = "sg92r-photo-body"
    body.data.materials.append(material("SG92R translucent blue", (0.025, 0.12, 0.8), alpha=0.72))
    return body


def build_cable():
    pitch = (WIRE_W - WIRE_T) / 2
    start_x = BODY_CENTER_X + BODY_L / 2
    cable_x = start_x + WIRE_LENGTH / 2
    colors = (
        ("Cable brown", (0.22, 0.055, 0.018)),
        ("Cable red", (0.7, 0.025, 0.018)),
        ("Cable yellow", (0.95, 0.58, 0.025)),
    )
    cable_materials = [material(name, color, roughness=0.5) for name, color in colors]
    wires = []
    for index, y in enumerate((-pitch, 0, pitch)):
        wire = add_cylinder_x(
            f"wire_{index + 1}", WIRE_T, WIRE_LENGTH,
            (cable_x, y, WIRE_EXIT_Z),
        )
        for mat in cable_materials:
            wire.data.materials.append(mat)
        for polygon in wire.data.polygons:
            polygon.material_index = index
        wires.append(wire)
    cable = union(wires[0], wires[1], wires[2])
    cable.name = "sg92r-photo-wire"
    return cable


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


def write_validation(body, horn, cable):
    boxes = [object_bbox_mm(body), object_bbox_mm(horn), object_bbox_mm(cable)]
    assembly_min = [min(box["min"][i] for box in boxes) for i in range(3)]
    assembly_max = [max(box["max"][i] for box in boxes) for i in range(3)]
    data = {
        "units": "mm",
        "body": {"bbox": boxes[0], **mesh_metrics(body)},
        "horn": {"bbox": boxes[1], **mesh_metrics(horn)},
        "wire": {"bbox": boxes[2], **mesh_metrics(cable)},
        "assembly": {
            "bbox": {
                "min": assembly_min,
                "max": assembly_max,
                "size": [round(assembly_max[i] - assembly_min[i], 4) for i in range(3)],
            },
            "separateClosedParts": 3,
        },
        "note": f"Flange centre X={BODY_CENTER_X * 1000:.2f} mm; dimension profile {PROFILE_ID}.",
    }
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    data["dimension_profile"] = PROFILE_ID
    path = os.path.join(EXPORTS_DIR, f"{REFERENCE_PREFIX}-validation.json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print("Validation:", path)
    print(json.dumps(data, ensure_ascii=False))


clear_scene()
body = build_body()
horn = build_horn()
cable = build_cable()

export_stl(f"{REFERENCE_PREFIX}-body", only=[body])
export_stl(f"{REFERENCE_PREFIX}-horn", only=[horn])
export_stl(f"{REFERENCE_PREFIX}-wire", only=[cable])
export_stl(REFERENCE_PREFIX, only=[body, horn, cable])
write_validation(body, horn, cable)
