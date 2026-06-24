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
    cut_servo_mount, add_thrust_ring, cut_horn_coupling, SERVO,
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

# サーボ・マウントを彫る（デッキ貫通穴・フランジ座・ネジ下穴・配線溝）
cut_servo_mount(body, deck_top_z=BODY_H, deck_t=DECK_T, clr=SERVO_CLR, screws=bool(SERVO_SCREWS))

# スラストリング（デッキ上面）。頭スカートが乗る
RING_OUTER = BODY_R - RING_INSET
ring_top = add_thrust_ring(body, deck_top_z=BODY_H, ring_outer_r=RING_OUTER,
                           ring_t=RING_T, ring_wall=RING_WALL)

# ============================================================
# 頭（半球ドーム）
# ============================================================
PLANE = ring_top                    # 頭の底面（リング上面に乗る）
# ホーン結合面 = 胴上面 + ケース上突起 + ギアカバー座高さ + すき間（サーボ実寸から自動）
COUPLING_Z = BODY_H + SERVO.NUB_ABOVE_DECK + SERVO.BOSS_H + COUPLING_GAP
# 軸逃げ径はギアカバー座を確実にクリア
CLEAR_R = max(CLEAR_R, SERVO.BOSS_DIA / 2 + 0.0015)

head = add_sphere(HEAD_R, (0, 0, PLANE), "round_head", segs=96, rings=48)
# 接合面より下を平らに切る（半球化）
cutoff = add_box(HEAD_R * 3, HEAD_R * 3, HEAD_R * 2,
                 (0, 0, PLANE - HEAD_R), "head_cutoff")
boolean(head, cutoff)

# 軸＋サーボ突起の逃げ（中央クリアランス・ボア）
bore_h = COUPLING_Z - PLANE + 0.002
bore = add_cyl(CLEAR_R, bore_h, PLANE + bore_h / 2 - 0.001, "head_bore")
boolean(head, bore)

# ホーン結合（クロス溝 + ハブ + センタービス穴）
cut_horn_coupling(head, coupling_z=COUPLING_Z, clr=SERVO_CLR)

# 点目（前面 +Y のくぼみ）。表面上の点に小球カッターを置く
import math
ey = math.sqrt(max(HEAD_R**2 - EYE_DX**2 - EYE_H**2, 1e-6))
for sx in (-1, 1):
    eye = add_sphere(EYE_R, (sx * EYE_DX, ey, PLANE + EYE_H), "eye", segs=32, rings=16)
    boolean(head, eye)

export_stl("round-bot")
