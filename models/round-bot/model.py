"""round-bot — まるっぽい1サーボ・キャラ（パン）。

構造（同軸・z上向き、z=0 が胴底面）:
  胴   = 円筒シェル（底開き）+ 上部デッキ。デッキに SG90 を縦置きで仕込む。
  頭   = 半球ドーム + 前面の点目2つ。裏にホーン結合。サーボ軸で左右にパン。
サーボは胴と頭の間に隠れる。胴と頭は別パーツ（サーボを挟んで組む）。
プレビューは組み上がり姿勢で両パーツを表示する。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from servo_core import (
    add_cyl, add_box, add_sphere, boolean,
    cut_servo_mount, cut_servo_head_clearance, cut_horn_coupling, cut_wire_exit, SERVO,
)
from params import *

clear_scene()

# ============================================================
# 胴（円筒シェル + デッキ）
# ============================================================
body = add_cyl(BODY_R, BODY_H, BODY_H / 2, "round_body")

# 中空化（底開き）: 内側を z=[-2mm, BODY_H-DECK_T] で抜く
inner_top = BODY_H - DECK_T
inner_h = inner_top + 0.002
inner = add_cyl(BODY_R - WALL, inner_h, inner_top - inner_h / 2, "body_inner")
boolean(body, inner)

# サーボ・マウントを彫る（デッキ貫通穴・フランジ座・ネジ下穴）
cut_servo_mount(body, deck_top_z=BODY_H, deck_t=DECK_T, clr=SERVO_CLR,
                screws=bool(SERVO_SCREWS), wire_notch_w=WIRE_NOTCH_W)

# 配線出口（サーボ長手 +X 側 の下端）。線は中空内部を通ってここから出る
cut_wire_exit(body, back_x=BODY_R, wall=WALL, width=WIRE_W, height=WIRE_H)

# ============================================================
# 頭（半球ドーム）。デッキ上面に直接乗って軸まわりに回る（リング無し）
# ============================================================
PLANE = BODY_H                      # 頭の底面 = デッキ上面
# ホーン結合面 = 胴上面 + ケース上突起 + ギアカバー座高さ + すき間（サーボ実寸から自動）
COUPLING_Z = BODY_H + SERVO.NUB_ABOVE_DECK + SERVO.BOSS_H + COUPLING_GAP

head = add_sphere(HEAD_R, (0, 0, PLANE), "round_head", segs=96, rings=48)
# 接合面より下を平らに切る（半球化）
cutoff = add_box(HEAD_R * 3, HEAD_R * 3, HEAD_R * 2,
                 (0, 0, PLANE - HEAD_R), "head_cutoff")
boolean(head, cutoff)

# サーボのデッキ上突起の逃げ（回転対応の丸逃げ）＋ホーン結合
cut_servo_head_clearance(head, plane_z=PLANE, deck_top_z=BODY_H,
                         coupling_z=COUPLING_Z, clr=SERVO_CLR)
cut_horn_coupling(head, coupling_z=COUPLING_Z, clr=SERVO_CLR)

# 点目（前面 +Y のくぼみ）。表面上の点に小球カッターを置く
import math
ey = math.sqrt(max(HEAD_R**2 - EYE_DX**2 - EYE_H**2, 1e-6))
for sx in (-1, 1):
    eye = add_sphere(EYE_R, (sx * EYE_DX, ey, PLANE + EYE_H), "eye", segs=32, rings=16)
    boolean(head, eye)

export_stl("round-bot")
