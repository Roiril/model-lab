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


def boolean(base, other, op):
    bpy.context.view_layer.objects.active = base
    mod = base.modifiers.new("b", "BOOLEAN")
    mod.operation = op
    mod.object = other
    mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier="b")
    bpy.data.objects.remove(other, do_unlink=True)


def make_frame(outer, inner, height, z_bottom):
    """Hollow square frame: outer-inner cube with the inside removed."""
    z_center = z_bottom + height / 2
    block = make_box(outer, outer, height, (0, 0, z_center))
    cutter = make_box(inner, inner, height + 0.001, (0, 0, z_center))
    boolean(block, cutter, "DIFFERENCE")
    return block


# --- 1. floor (full outer footprint) ---
floor = make_box(OUTER, OUTER, THICKNESS, (0, 0, THICKNESS / 2))

# --- 2. outer wall: frame around the perimeter ---
wall = make_frame(OUTER, WALL_INNER, WALL_H_FROM_FLOOR, THICKNESS)
boolean(floor, wall, "UNION")

# --- 3. inner visual rim: small frame between play area and wall ---
rim = make_frame(RIM_OUTER, PLAY, RIM_H, THICKNESS)
boolean(floor, rim, "UNION")

# --- 4. grooves on the play area (top face of floor) ---
CUTTER_H = GROOVE_D + 0.002
CUTTER_Z = THICKNESS - GROOVE_D + CUTTER_H / 2
GROOVE_LEN = PLAY  # grooves stay inside the play area, not crossing the rim

for i in range(1, N):
    x = -PLAY / 2 + i * SQUARE
    cutter = make_box(GROOVE_W, GROOVE_LEN, CUTTER_H, (x, 0, CUTTER_Z))
    boolean(floor, cutter, "DIFFERENCE")

for i in range(1, N):
    y = -PLAY / 2 + i * SQUARE
    cutter = make_box(GROOVE_LEN, GROOVE_W, CUTTER_H, (0, y, CUTTER_Z))
    boolean(floor, cutter, "DIFFERENCE")

# --- 5. wood-joinery corner joints on top of the wall (4 lines, all same direction) ---
WALL_CUTTER_Z = WALL_H - GROOVE_D + CUTTER_H / 2
WALL_OFF = (WALL_INNER + OUTER) / 4  # center of wall strip from origin
WALL_HALF = WALL_INNER / 2           # inner edge of wall

# All 4 corner joints run along x (N/S strips extend to outer corners).
for sx in (-1, 1):
    for sy in (-1, 1):
        cutter = make_box(WALL_W, GROOVE_W, CUTTER_H,
                          (sx * WALL_OFF, sy * WALL_HALF, WALL_CUTTER_Z))
        boolean(floor, cutter, "DIFFERENCE")

# --- 6. matching joints on the outer east/west side faces (vertical grooves) ---
# Each top-corner cut continues as a vertical groove on the corresponding outer side face.
SIDE_CUTTER_DEPTH = GROOVE_D + 0.001   # protrudes 0.5mm past the outer face
SIDE_CUTTER_X_OFFSET = OUTER / 2 + (0.0005 - GROOVE_D) / 2  # center such that inner edge at OUTER/2 - GROOVE_D, outer edge at OUTER/2 + 0.0005
SIDE_CUTTER_H = WALL_H + 0.001         # full height + overhang
SIDE_CUTTER_Z = WALL_H / 2             # centered

for sx in (-1, 1):
    for sy in (-1, 1):
        cutter = make_box(SIDE_CUTTER_DEPTH, GROOVE_W, SIDE_CUTTER_H,
                          (sx * SIDE_CUTTER_X_OFFSET, sy * WALL_HALF, SIDE_CUTTER_Z))
        boolean(floor, cutter, "DIFFERENCE")

export_stl("chessboard")
