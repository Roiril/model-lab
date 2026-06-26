"""rabbit-ears — square-bot 用 うさ耳カチューシャ（バンドのみ）。

角頭にかぶせるコの字バンド（天面バー＋両脇の脚、幅 BAND_W は Y方向）。
耳は別途 Blender で手作りして横置き印刷するため、ここはバンドだけを出力する。
アクセサリ座標は頭の天面を z=0 に取る。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from servo_core import add_box, boolean
from params import *

clear_scene()
MM = 0.001
HW = (HEAD_W / 2 + FIT_CLR) * MM   # 内側ハーフ幅
BT = BAND_T * MM
bw = BAND_W * MM
drop = DROP * MM

# --- コの字バンド: 外箱 − 内箱 ---
# 天面バー z[0,BT] / 脚 z[-drop,0]
outer_w = 2 * (HW + BT)
outer_h = drop + BT
outer = add_box(outer_w, bw, outer_h, (0, 0, (BT - drop) / 2), "rab_band")
inner = add_box(2 * HW, bw + 0.004, drop + 0.01, (0, 0, (-(drop) - 0.01) / 2 + 0.0), "band_in")
boolean(outer, inner)
band = outer
band.name = "rabbit-ears"

# 耳は別途 Blender で手作りするため、ここはバンドのみ出力
export_stl("rabbit-ears")
