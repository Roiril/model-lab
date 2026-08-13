"""ロボットハンド(54.5x27.5mm)を安定して載せる台座。

構成:
  - 広いベースプレート（転倒防止）
  - その上にカップ状の壁付きポケット（ハンドをはめ込み保持）
  - 片側壁にケーブル逃げの切り欠き
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


def add_box(w, d, h, location=(0, 0, 0), name="box"):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location)  # edge=2 -> scale w/2 gives w
    obj = bpy.context.active_object
    obj.scale = (w / 2, d / 2, h / 2)
    bpy.ops.object.transform_apply(scale=True)
    obj.name = name
    return obj


def boolean(target, cutter, op="DIFFERENCE"):
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier="bool")
    bpy.data.objects.remove(cutter, do_unlink=True)


# ============================================================
# 1. ベースプレート（z=0 が底面）
# ============================================================
base = add_box(BASE_W, BASE_D, BASE_T,
               location=(0, 0, BASE_T / 2), name="base_plate")

# ============================================================
# 2. カップ（壁付きポケット部）— ベースプレートの上に乗る
# ============================================================
cup_z0 = BASE_T            # カップ底面 = ベースプレート上面
cup = add_box(CUP_W, CUP_D, CUP_H,
              location=(0, 0, cup_z0 + CUP_H / 2), name="cup")

# ポケットを掘る（上面から POCKET_DEPTH ぶん）
# カッターをカップ上面より 0.5mm 突き出して配置（面一回避）
pocket_top = cup_z0 + CUP_H + 0.0005
pocket_h = POCKET_DEPTH + 0.0005 + 0.001  # 上突き出し + 余裕
pocket = add_box(POCKET_IW, POCKET_ID, pocket_h,
                 location=(0, 0, pocket_top - pocket_h / 2), name="pocket_cutter")
boolean(cup, pocket)

# ============================================================
# 3. ケーブル逃げの切り欠き（-Y 側の壁）
# ============================================================
# 壁上端から CABLE_DEPTH ぶん下げて、幅 CABLE_W のスリットを掘る
cable_top = cup_z0 + CUP_H + 0.0005
cable_h = CABLE_DEPTH + 0.0005
# -Y 壁をまたぐように Y 方向に十分長く
cable = add_box(CABLE_W, WALL * 3, cable_h,
                location=(0, -CUP_D / 2, cable_top - cable_h / 2),
                name="cable_cutter")
boolean(cup, cable)

# ============================================================
# 4. ベースとカップを結合
# ============================================================
boolean(base, cup, op="UNION")

# ============================================================
# 5. 縁を面取り（角・上端を落とす）
# ============================================================
bev = base.modifiers.new("bevel", "BEVEL")
bev.width = EDGE_BEVEL
bev.segments = 2
bev.limit_method = "ANGLE"
bev.angle_limit = 0.785  # 45deg
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier="bevel")

export_stl("hand-stand")
