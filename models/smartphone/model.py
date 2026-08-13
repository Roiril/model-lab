"""Simple smartphone model."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


def add_rounded_box(w, d, h, r, location=(0, 0, 0), name="part"):
    """角丸の直方体（Bevel modifier 適用）。"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (w / 2, d / 2, h / 2)
    bpy.ops.object.transform_apply(scale=True)
    bevel = obj.modifiers.new("bevel", "BEVEL")
    bevel.width = r
    bevel.segments = 8
    bevel.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier="bevel")
    return obj


# --- 本体 ---
body = add_rounded_box(WIDTH, DEPTH, HEIGHT, CORNER_R, name="body")

# --- 画面のくぼみ（前面 = +Z） ---
screen_w = WIDTH - SCREEN_MARGIN * 2
screen_d = DEPTH - SCREEN_MARGIN * 2
bpy.ops.mesh.primitive_cube_add(size=1)
screen_cut = bpy.context.active_object
screen_cut.name = "screen_cut"
screen_cut.scale = (screen_w / 2, screen_d / 2, SCREEN_DEPTH)
screen_cut.location = (0, 0, HEIGHT / 2)  # 上面から少し突き出す
bpy.ops.object.transform_apply(scale=True, location=False)

mod = body.modifiers.new("screen", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = screen_cut
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="screen")
bpy.data.objects.remove(screen_cut, do_unlink=True)

# --- カメラバンプ（背面 = -Z） ---
cam_z = -HEIGHT / 2 - CAM_BUMP_T / 2
cam_loc = (CAM_OFFSET_X, CAM_OFFSET_Y, cam_z)
cam_bump = add_rounded_box(
    CAM_BUMP_W, CAM_BUMP_H, CAM_BUMP_T, CAM_BUMP_R,
    location=cam_loc, name="cam_bump"
)

# 本体と結合
bpy.context.view_layer.objects.active = body
mod = body.modifiers.new("union", "BOOLEAN")
mod.operation = "UNION"
mod.object = cam_bump
mod.solver = "EXACT"
bpy.ops.object.modifier_apply(modifier="union")
bpy.data.objects.remove(cam_bump, do_unlink=True)

# --- 3つのレンズ ---
lens_z = -HEIGHT / 2 - CAM_BUMP_T - LENS_T / 2 + 0.0001
for i, dy in enumerate([-LENS_SPACING, 0, LENS_SPACING]):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=LENS_R, depth=LENS_T,
        location=(CAM_OFFSET_X, CAM_OFFSET_Y + dy, lens_z),
        vertices=48,
    )
    lens = bpy.context.active_object
    lens.name = f"lens_{i}"
    bpy.context.view_layer.objects.active = body
    mod = body.modifiers.new(f"lens_{i}", "BOOLEAN")
    mod.operation = "UNION"
    mod.object = lens
    mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=f"lens_{i}")
    bpy.data.objects.remove(lens, do_unlink=True)

export_stl("smartphone")
