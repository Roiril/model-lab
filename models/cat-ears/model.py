"""cat-ears — round-bot 用 猫耳カチューシャ。

ドーム半径に沿うアーチ状バンド（XZ平面の半円リング、幅 BAND_W は Y方向）＋
天面寄りに三角の猫耳2つ。アクセサリ座標はドーム中心を原点（z=0）に取り、
バンドの脚が z=0（ドーム基部）、頂点が z≈HEAD_R。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import math
from blender_utils import clear_scene, export_stl
from servo_core import add_cyl, add_box, boolean
from params import *

clear_scene()
MM = 0.001
R_in = (HEAD_R + FIT_CLR) * MM
R_out = R_in + BAND_T * MM
bw = BAND_W * MM

# --- バンド: XY のワッシャ（高さ bw）を作り、90°起こして XZ のリングにする ---
outer = add_cyl(R_out, bw, 0, "cat_band", verts=128)
hole = add_cyl(R_in, bw + 0.004, 0, "band_hole", verts=128)
boolean(outer, hole)
outer.rotation_euler = (math.radians(90), 0, 0)
bpy.context.view_layer.objects.active = outer
bpy.ops.object.transform_apply(rotation=True)
# 下半分を除去して上向きの C アーチに
cutb = add_box(R_out * 3, R_out * 3, R_out * 2, (0, 0, -R_out), "cutb")
boolean(outer, cutb)
band = outer

# --- 猫耳（平らにした円錐）を天面寄りに2つ ---
Rmid = (R_in + R_out) / 2
for sx in (-1, 1):
    x0 = sx * EAR_DX * MM
    z0 = math.sqrt(max(Rmid ** 2 - x0 ** 2, 1e-9))
    bpy.ops.mesh.primitive_cone_add(radius1=EAR_W / 2 * MM, radius2=0, depth=EAR_H * MM,
                                    location=(x0, 0, z0 + EAR_H / 2 * MM), vertices=48)
    ear = bpy.context.active_object
    ear.name = "cat_ear"
    ear.scale.y = (EAR_T * MM) / (EAR_W * MM)  # Y方向に薄く＝三角フィン化
    bpy.context.view_layer.objects.active = ear
    bpy.ops.object.transform_apply(scale=True)
    boolean(band, ear, op="UNION")

export_stl("cat-ears")
