import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


def make_box(sx, sy, sz, location):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, scale=True)
    return obj


def make_cyl(r, h, location, axis="Z"):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=location, vertices=32)
    obj = bpy.context.active_object
    if axis == "X":
        obj.rotation_euler = (0, 1.5707963, 0)
    elif axis == "Y":
        obj.rotation_euler = (1.5707963, 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return obj


def make_sphere(r, location):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=location, segments=24, ring_count=12)
    return bpy.context.active_object


def make_ellipsoid(rx, ry, rz, location):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=location, segments=24, ring_count=12)
    obj = bpy.context.active_object
    obj.scale = (rx, ry, rz)
    bpy.ops.object.transform_apply(location=False, scale=True)
    return obj


def boolean(base, other, op):
    bpy.context.view_layer.objects.active = base
    mod = base.modifiers.new("b", "BOOLEAN")
    mod.operation = op
    mod.object = other
    mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier="b")
    bpy.data.objects.remove(other, do_unlink=True)


def join(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    return bpy.context.active_object


# --- 1. floor slab (1.8 x 1.8) ---
floor = make_box(BOOTH, BOOTH, FLOOR_THICKNESS, (0, 0, FLOOR_THICKNESS / 2))

# --- 2. border highlight (perimeter strip on top of floor) ---
border_outer = make_box(BOOTH, BOOTH, BORDER_H,
                        (0, 0, FLOOR_THICKNESS + BORDER_H / 2))
inner = BOOTH - 2 * BORDER_W
cutter = make_box(inner, inner, BORDER_H + 0.001,
                  (0, 0, FLOOR_THICKNESS + BORDER_H / 2))
boolean(border_outer, cutter, "DIFFERENCE")
floor = join([floor, border_outer])

# --- 3. corner posts (volume markers, 2m tall) ---
half = BOOTH / 2 - POST_SIZE / 2
for sx in (-1, 1):
    for sy in (-1, 1):
        post = make_box(POST_SIZE, POST_SIZE, POST_H,
                        (sx * half, sy * half, FLOOR_THICKNESS + POST_H / 2))
        floor = join([floor, post])


def make_human(x, y, rotation_z=0.0):
    """Simple human reference figure at (x, y), feet on z=FLOOR_THICKNESS."""
    z0 = FLOOR_THICKNESS  # ground level (top of floor slab)
    parts = []

    # legs (two cylinders side by side)
    leg_z = z0 + LEG_H / 2
    for sx in (-1, 1):
        leg = make_cyl(LEG_R, LEG_H, (sx * LEG_OFFSET, 0, leg_z))
        parts.append(leg)

    # hip (short cylinder bridging legs)
    hip_z = z0 + LEG_H + HIP_H / 2
    parts.append(make_ellipsoid(TORSO_R_X * 0.9, TORSO_R_Y * 0.9, HIP_H / 2,
                                (0, 0, hip_z)))

    # torso (ellipsoid for shoulders-wide)
    torso_z = z0 + LEG_H + HIP_H + TORSO_H / 2
    parts.append(make_ellipsoid(TORSO_R_X, TORSO_R_Y, TORSO_H / 2,
                                (0, 0, torso_z)))

    # arms (cylinders alongside torso)
    arm_z = z0 + LEG_H + HIP_H + TORSO_H - ARM_H / 2 + 0.05
    for sx in (-1, 1):
        parts.append(make_cyl(ARM_R, ARM_H,
                              (sx * SHOULDER_OFFSET, 0, arm_z)))

    # neck
    neck_z = z0 + LEG_H + HIP_H + TORSO_H + NECK_H / 2
    parts.append(make_cyl(NECK_R, NECK_H, (0, 0, neck_z)))

    # head
    head_z = z0 + LEG_H + HIP_H + TORSO_H + NECK_H + HEAD_R
    parts.append(make_sphere(HEAD_R, (0, 0, head_z)))

    body = join(parts)

    # rotate + translate as one
    if rotation_z != 0.0:
        body.rotation_euler = (0, 0, rotation_z)
    body.location.x += x
    body.location.y += y
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return body


# --- 4. human reference figures ---
# Place two visitors near opposite edges, facing roughly inward.
make_human(-0.55, -0.3, rotation_z=0.3)
make_human(0.55, 0.4, rotation_z=3.4)

export_stl("ivrc-booth")
