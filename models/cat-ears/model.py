"""cat-ears — round-bot 用 猫耳カチューシャ（バンドのみ）。

ドーム半径に沿うアーチ状バンド（XZ平面の半円リング、幅 BAND_W は Y方向）。
耳は別途 Blender で手作りして横置き印刷するため、ここはバンドだけを出力する。
アクセサリ座標はドーム中心を原点（z=0）に取り、脚が z=0（ドーム基部）、頂点が z≈HEAD_R。
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
band.name = "cat-ears"

# 耳は別途 Blender で手作りするため、ここはバンドのみ出力
export_stl("cat-ears")
