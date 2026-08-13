"""プリント・イン・プレース回転台。

固定部（ベース＋軸＋傘）とローター（リング円板）を隙間を空けて一体プリント。
組立不要で、ローターが軸まわりに自由回転する。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


def add_cyl(r, h, z_center, name, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h,
                                         location=(0, 0, z_center), vertices=verts)
    o = bpy.context.active_object
    o.name = name
    return o


def add_box(w, d, h, location, name):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location)  # edge=2 -> scale w/2 gives w
    o = bpy.context.active_object
    o.scale = (w / 2, d / 2, h / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.name = name
    return o


def boolean(target, cutter, op="DIFFERENCE"):
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier="bool")
    bpy.data.objects.remove(cutter, do_unlink=True)


# ============================================================
# 固定部（stator）= ベース + 軸 + 傘 を UNION
# ============================================================
base = add_cyl(BASE_R, BASE_T, BASE_T / 2, "stator")

# 中心軸: z = BASE_T 〜 SHAFT_TOP
shaft_h = SHAFT_TOP - BASE_T
shaft = add_cyl(SHAFT_R, shaft_h, BASE_T + shaft_h / 2, "shaft")
boolean(base, shaft, op="UNION")

# 傘: z = CAP_Z0 〜 TOTAL_H
cap = add_cyl(CAP_R, CAP_T, CAP_Z0 + CAP_T / 2, "cap")
boolean(base, cap, op="UNION")

# 固定部マーカー（ベース外縁の +X 側、基準点）
sm = add_box(MARK_W, MARK_W, MARK_H,
             location=(BASE_R - MARK_W, 0, BASE_T + MARK_H / 2), name="stator_mark")
boolean(base, sm, op="UNION")

# ============================================================
# ローター = リング円板（軸まわりに回る）
# ============================================================
rotor = add_cyl(ROTOR_R, ROTOR_T, ROTOR_Z0 + ROTOR_T / 2, "rotor")
# 中心穴を掘る（軸 + 半径クリアランス）。上下に突き出して面一回避
bore = add_cyl(ROTOR_IR, ROTOR_T + 0.002, ROTOR_Z0 + ROTOR_T / 2, "bore")
boolean(rotor, bore)

# ローターマーカー（外縁 +X、回転が見える突起）
rm = add_box(MARK_W, MARK_W, MARK_H,
             location=(ROTOR_R - MARK_W, 0, ROTOR_Z1 + MARK_H / 2), name="rotor_mark")
boolean(rotor, rm, op="UNION")

export_stl("turntable")
