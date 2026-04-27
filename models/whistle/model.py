"""
whistle: ヘルムホルツ共鳴器（空気の塊がバネ-マス系として振動する笛）。

構成:
- 外殻: 球 (半径 CAVITY_R + WALL) + 上方向のネック円柱
- 空洞: 球 (半径 CAVITY_R) + ネック円柱 (半径 NECK_R、貫通)
- 底面を水平カット → 3D プリント時に自立
- ネック開口（上部）は開放。端を横切る気流で励振する。

音響的性質:
- ネック内の空気が「質量」、キャビティ空気が「バネ」として働き、単一周波数で共鳴。
- f = (c/2π)√(A/(V·L')) で設計。DESIGN_FREQ を params.py で計算して出力する。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import (
    CAVITY_R, WALL, NECK_R, NECK_L, NECK_WALL,
    BASE_FLAT_Z, DESIGN_FREQ,
)

clear_scene()

OUTER_R   = CAVITY_R + WALL          # 外球半径
NECK_OR   = NECK_R + NECK_WALL       # ネック外半径
NECK_TOP  = OUTER_R + NECK_L         # ネック先端 z 座標


# --- 外殻 ---
# 外球
bpy.ops.mesh.primitive_uv_sphere_add(radius=OUTER_R, segments=64, ring_count=32, location=(0, 0, 0))
outer_sphere = bpy.context.active_object
outer_sphere.name = "outer_sphere"

# ネック外筒（球内部にも少し食い込ませる → union で滑らか結合）
bpy.ops.mesh.primitive_cylinder_add(
    radius=NECK_OR, depth=NECK_L + OUTER_R, vertices=64,
    location=(0, 0, OUTER_R / 2 + NECK_L / 2),
)
neck_outer = bpy.context.active_object
neck_outer.name = "neck_outer"

# 外殻の union
bpy.context.view_layer.objects.active = outer_sphere
mod = outer_sphere.modifiers.new("union_neck", "BOOLEAN")
mod.operation = "UNION"
mod.object = neck_outer
mod.solver = "EXACT"
bpy.ops.object.modifier_apply(modifier="union_neck")
bpy.data.objects.remove(neck_outer, do_unlink=True)


# --- 空洞（後で subtract する立体） ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=CAVITY_R, segments=64, ring_count=32, location=(0, 0, 0))
cavity_sphere = bpy.context.active_object
cavity_sphere.name = "cavity"

# ネック内筒（キャビティを貫通して外部へ）
bpy.ops.mesh.primitive_cylinder_add(
    radius=NECK_R,
    depth=NECK_TOP + 0.001,  # 貫通保証
    vertices=64,
    location=(0, 0, (NECK_TOP + 0.001) / 2),
)
neck_inner = bpy.context.active_object
neck_inner.name = "neck_inner"

# 空洞 union
bpy.context.view_layer.objects.active = cavity_sphere
mod = cavity_sphere.modifiers.new("union_bore", "BOOLEAN")
mod.operation = "UNION"
mod.object = neck_inner
mod.solver = "EXACT"
bpy.ops.object.modifier_apply(modifier="union_bore")
bpy.data.objects.remove(neck_inner, do_unlink=True)


# --- 外殻から空洞を引く ---
bpy.context.view_layer.objects.active = outer_sphere
mod = outer_sphere.modifiers.new("hollow", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = cavity_sphere
mod.solver = "EXACT"
bpy.ops.object.modifier_apply(modifier="hollow")
bpy.data.objects.remove(cavity_sphere, do_unlink=True)


# --- 底面カット（印刷時の接地用） ---
# BASE_FLAT_Z より下を大きなキューブで削る
bpy.ops.mesh.primitive_cube_add(
    size=max(OUTER_R * 3, NECK_TOP * 2),
    location=(0, 0, BASE_FLAT_Z - max(OUTER_R * 3, NECK_TOP * 2) / 2),
)
base_cut = bpy.context.active_object
base_cut.name = "base_cut"

bpy.context.view_layer.objects.active = outer_sphere
mod = outer_sphere.modifiers.new("base_flat", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = base_cut
mod.solver = "EXACT"
bpy.ops.object.modifier_apply(modifier="base_flat")
bpy.data.objects.remove(base_cut, do_unlink=True)


outer_sphere.name = "whistle"
bpy.context.view_layer.objects.active = outer_sphere
outer_sphere.select_set(True)

print(f"[whistle] cavity_r = {CAVITY_R*1000:.1f}mm, neck {NECK_R*1000:.1f}mm x L {NECK_L*1000:.1f}mm")
print(f"[whistle] design frequency ≒ {DESIGN_FREQ:.0f} Hz")

export_stl("whistle")
