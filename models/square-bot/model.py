"""square-bot — しかくっぽい1サーボ・キャラ（パン）。

構造（z=0 が胴底面）:
  胴 = 角丸ボックスのシェル（底開き）+ 上部デッキ。SG90 を縦置きで仕込む。
  頭 = 角丸ボックス + 前面の点目2つ。裏にホーン結合。サーボ軸で左右にパン。
機構コアは round-bot と完全共有（lib/servo_core.py）。外皮だけが違う。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import math
from blender_utils import clear_scene, export_stl
from servo_core import (
    add_cyl, add_box, add_sphere, boolean, round_box_xy,
    cut_servo_mount, cut_servo_head_clearance, cut_horn_coupling, SERVO,
)
from params import *

clear_scene()

# ============================================================
# 胴（角丸ボックスのシェル + デッキ）
# ============================================================
body = round_box_xy(BODY_W, BODY_D, BODY_H, BODY_FILLET, BODY_H / 2, "square_body")

# 中空化（底開き）
inner_top = BODY_H - DECK_T
inner_h = inner_top + 0.002
inner = round_box_xy(BODY_W - 2 * WALL, BODY_D - 2 * WALL, inner_h,
                     max(BODY_FILLET - WALL, 0.001), inner_top - inner_h / 2, "body_inner")
boolean(body, inner)

# サーボ・マウント（配線は中空内部→底開口へ）
cut_servo_mount(body, deck_top_z=BODY_H, deck_t=DECK_T, clr=SERVO_CLR, screws=bool(SERVO_SCREWS))

# ============================================================
# 頭（角丸ボックス）。デッキ上面に直接乗って軸まわりに回る（リング無し）
# ============================================================
PLANE = BODY_H
COUPLING_Z = BODY_H + SERVO.NUB_ABOVE_DECK + SERVO.BOSS_H + COUPLING_GAP
head_cz = PLANE + HEAD_H / 2

head = round_box_xy(HEAD_W, HEAD_D, HEAD_H, HEAD_FILLET, head_cz, "square_head")

# サーボのデッキ上突起の逃げ（回転対応の丸逃げ）＋ホーン結合
cut_servo_head_clearance(head, plane_z=PLANE, deck_top_z=BODY_H,
                         coupling_z=COUPLING_Z, clr=SERVO_CLR)
cut_horn_coupling(head, coupling_z=COUPLING_Z, clr=SERVO_CLR)

# 点目（前面 +Y のくぼみ）。前面板から EYE_DEPTH だけ彫る
face_y = BODY_D / 2  # 頭前面（おおよそ胴と同じ）
for sx in (-1, 1):
    eye = add_sphere(EYE_R, (sx * EYE_DX, face_y + EYE_R - EYE_DEPTH, PLANE + EYE_H),
                     "eye", segs=32, rings=16)
    boolean(head, eye)

export_stl("square-bot")
