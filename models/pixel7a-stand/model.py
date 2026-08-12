"""Pixel 7a 固定スタンド — スマホは斜面の内側スロットに収まり、カメラバーだけが窓から外へ出る。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()

# --- 斜面のローカル座標系 -------------------------------------------------
# s: 斜面を上る方向 / h: 斜面の外向き法線（h=0 が斜面の外表面）
A = math.radians(TILT_DEG)
UY, UZ = math.cos(A), math.sin(A)
NY, NZ = -math.sin(A), math.cos(A)
BASE_Y = -STAND_D / 2   # 斜面の下端エッジ＝前壁の上端
BASE_Z = FRONT_H
BIG = 0.4


def sp(s, h, x=0.0):
    """斜面座標 (s, h) をワールド座標へ。"""
    return (x, BASE_Y + s * UY + h * NY, BASE_Z + s * UZ + h * NZ)


def add_box(name, size, loc, rot_x=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=(rot_x, 0.0, 0.0))
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return o


def _apply(target, other, op):
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.object = other
    m.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(other, do_unlink=True)


def cut(target, cutter):
    _apply(target, cutter, "DIFFERENCE")


def join(target, part):
    _apply(target, part, "UNION")


# --- 本体ブランク --------------------------------------------------------
body = add_box("pixel7a_stand", (STAND_W, STAND_D, STAND_H), (0.0, 0.0, STAND_H / 2))

# --- 斜面を切り出す（h > 0 側を落とす） ----------------------------------
cut(body, add_box("cut_slope", (BIG, BIG, BIG), sp(SLOPE_LEN / 2, BIG / 2), A))

# --- スマホスロット（天面の差し込み口から下端の受けまで） ----------------
slot_cut_len = SLOT_W + SLOT_ENTRY
cut(body, add_box("cut_slot", (SLOT_L, slot_cut_len, SLOT_T),
                  sp(STOPPER + slot_cut_len / 2, -(FRONT_SKIN + SLOT_T / 2)), A))

# --- カメラ窓（外皮を貫通。カメラバーがここから顔を出す） ----------------
win_x = SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2
cut(body, add_box("cut_camwin", (CAM_WIN_L, WIN_S_LEN, 0.010),
                  sp(WIN_S_CENTER, -0.003, win_x), A))

# --- 差し込み口のテーパー（外皮側だけ斜めに逃がす） ----------------------
phi = math.atan2(TAPER_D, TAPER_LEN)
ta = A + phi   # 斜面より立てる。s が増えるほど外皮の内面が外へ退く
tdy, tdz = math.cos(ta), math.sin(ta)      # テーパー面に沿う方向
tny, tnz = -math.sin(ta), math.cos(ta)     # テーパー面の外向き法線
tp = sp(TAPER_S0, -FRONT_SKIN)
thalf = 0.030
# テーパー面から内側へ TAPER_D だけの層を抜く（外皮の外面は削らない）
cut(body, add_box("cut_taper", (2 * STAND_W, 2 * thalf, TAPER_D),
                  (0.0,
                   tp[1] + thalf * tdy - (TAPER_D / 2) * tny,
                   tp[2] + thalf * tdz - (TAPER_D / 2) * tnz), ta))

# --- 指がかり（中央だけ外皮と裏板を落としてスマホ上端を摘まめるようにする） ---
grip_len = 0.040
cut(body, add_box("cut_grip", (GRIP_W, grip_len, 0.020),
                  sp(GRIP_S0 + grip_len / 2, -0.006), A))

# --- 内部の肉抜き（底板は残す） ------------------------------------------
cav_h = -(FRONT_SKIN + SLOT_T + BACK_PLATE)
cav = add_box("cut_cavity", (STAND_W - 2 * SIDE_WALL, STAND_D - 2 * WALL_Y, 0.200),
              (0.0, 0.0, BOTTOM_T + 0.100))
cut(cav, add_box("cut_cavity_lid", (BIG, BIG, BIG), sp(SLOPE_LEN / 2, cav_h + BIG / 2), A))
cut(body, cav)

# --- 保持リブ（裏板から突き出してスマホ上部を外皮側へ押す。0 なら作らない） ---
if RIB_H > 0:
    join(body, add_box("rib_hold", (SLOT_L - 2 * RIB_SIDE_GAP, RIB_BW, RIB_H + RIB_EMBED),
                       sp(RIB_S, -(FRONT_SKIN + SLOT_T) + (RIB_H - RIB_EMBED) / 2), A))

# --- 側壁リブ（長辺方向のガタ止め。0 なら作らない） ----------------------
if SIDE_RIB_H > 0:
    side_rib_len = SIDE_RIB_S1 - SIDE_RIB_S0
    for sx in (-1.0, 1.0):
        join(body, add_box("rib_side", (RIB_EMBED + SIDE_RIB_H, side_rib_len, SLOT_T - 0.004),
                           sp(SIDE_RIB_S0 + side_rib_len / 2, -(FRONT_SKIN + SLOT_T / 2),
                              sx * (SLOT_L / 2 + (RIB_EMBED - SIDE_RIB_H) / 2)), A))

# --- USB-C / スピーカーの逃げ（リブより後に抜いて塞がないようにする） ----
cut(body, add_box("cut_usb", (0.020, USB_W, 0.012),
                  sp(USB_S, -(FRONT_SKIN + 0.006), -(STAND_W / 2 - SIDE_WALL)), A))

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body

export_stl("pixel7a-stand")
