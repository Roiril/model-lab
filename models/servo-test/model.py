"""servo-test — 機構検証用の最小テスト治具。

2パーツ（組立不要の同時プリント可）:
  プレート = 平らなマウント板。上面に SG92R を縦置きで固定（本体は板の下にぶら下がる）。
             フランジ座・ネジ穴・配線溝・スラストリングを備える。
  キャップ = リング上に乗って回るカップ。裏でサーボホーンに結合し、上にポインタ。

確認項目: socket フィット / フランジ着座 / ネジ穴位置 / リング上の滑らかな回転 / ホーン噛み。
プレビューは組み上がり姿勢で両パーツを表示する（実際は別パーツ）。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from servo_core import (
    add_cyl, add_box, boolean, round_box_xy,
    cut_servo_mount, add_thrust_ring, cut_horn_coupling, add_servo_dummy, SERVO,
)
from params import *

clear_scene()

# ============================================================
# プレート（マウント板）
# ============================================================
plate = round_box_xy(PLATE_W, PLATE_D, PLATE_T, PLATE_FILLET, PLATE_T / 2, "plate")

# サーボ・マウント（デッキ穴・フランジ座・ネジ穴・配線溝）。板そのものをデッキとして使う
cut_servo_mount(plate, deck_top_z=PLATE_T, deck_t=PLATE_T, clr=SERVO_CLR, screws=bool(SERVO_SCREWS))

# スラストリング
ring_top = add_thrust_ring(plate, deck_top_z=PLATE_T, ring_outer_r=RING_OUTER,
                           ring_t=RING_T, ring_wall=RING_WALL)

# 固定側の基準マーク（前縁 +Y。キャップが中心に戻るか見る用）
ref = add_box(0.002, 0.002, 0.0015, (0, PLATE_D / 2 - 0.001, PLATE_T + 0.00075), "ref_mark")
boolean(plate, ref, op="UNION")

# ============================================================
# キャップ（回る側・カップ形）
# ============================================================
PLANE = ring_top
COUPLING_Z = PLATE_T + SERVO.NUB_ABOVE_DECK + SERVO.BOSS_H + COUPLING_GAP
CLEAR_R = max(CLEAR_R, SERVO.BOSS_DIA / 2 + 0.0015)
CAP_TOP = COUPLING_Z + CAP_TOP_T

cap = add_cyl(CAP_R, CAP_TOP - PLANE, (PLANE + CAP_TOP) / 2, "cap")

# 中空化（底開き）: 天面 CAP_TOP_T を残す
inner_top = CAP_TOP - CAP_TOP_T
inner_h = inner_top - PLANE + 0.004
inner = add_cyl(CAP_R - CAP_WALL, inner_h, inner_top - inner_h / 2, "cap_inner")
boolean(cap, inner)

# 軸＋サーボ突起の逃げ（中央）
bore_h = COUPLING_Z - PLANE + 0.004
bore = add_cyl(CLEAR_R, bore_h, PLANE + bore_h / 2 - 0.002, "cap_bore")
boolean(cap, bore)

# ホーン結合（クロス溝 + ハブ + センタービス穴）
cut_horn_coupling(cap, coupling_z=COUPLING_Z, clr=SERVO_CLR)

# 回転が見えるポインタ（天面 +X 側に1本）
ptr = add_box(POINTER_L, POINTER_W, POINTER_H,
              (CAP_R - POINTER_L / 2, 0, CAP_TOP + POINTER_H / 2), "pointer")
boolean(cap, ptr, op="UNION")

# ============================================================
# サーボ実体ダミー（重ね表示・シミュレーション用）
# ============================================================
if SHOW_SERVO:
    add_servo_dummy(flange_top_z=PLATE_T, name="servo")

export_stl("servo-test")
