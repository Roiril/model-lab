import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()

# --- 外形 ---
outer_x = CAVITY_X + WALL * 2
outer_y = CAVITY_Y + WALL * 2
outer_z = CAVITY_Z + WALL          # 底 1 枚ぶんだけ足す（上は開口）

bpy.ops.mesh.primitive_cube_add(size=1)
base = bpy.context.active_object
base.name = "box_shell"
base.scale = (outer_x, outer_y, outer_z)
bpy.ops.object.transform_apply(scale=True)
base.location = (0, 0, outer_z / 2)

# --- 上方向にキャビティをくりぬく ---
bpy.ops.mesh.primitive_cube_add(size=1)
cut = bpy.context.active_object
cut.scale = (CAVITY_X, CAVITY_Y, CAVITY_Z + CUT_MARGIN)
bpy.ops.object.transform_apply(scale=True)
# 空洞の底は z=WALL、上端は天面より CUT_MARGIN 突き出す
cut.location = (0, 0, WALL + (CAVITY_Z + CUT_MARGIN) / 2)

mod = base.modifiers.new("cut", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = cut
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier="cut")
bpy.data.objects.remove(cut, do_unlink=True)

print(f"[box-shell] cavity {CAVITY_X*1000:.1f} x {CAVITY_Y*1000:.1f} x {CAVITY_Z*1000:.1f} mm")
print(f"[box-shell] outer  {outer_x*1000:.1f} x {outer_y*1000:.1f} x {outer_z*1000:.1f} mm")

export_stl("box-shell")
