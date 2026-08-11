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


def add_box(name, size, loc, tilt=False):
    rot = (A, 0.0, 0.0) if tilt else (0.0, 0.0, 0.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return o


def add_cyl(name, r, depth, loc):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=depth, location=loc, rotation=(A, 0.0, 0.0), vertices=64)
    o = bpy.context.object
    o.name = name
    return o


def cut(target, cutter):
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    m = target.modifiers.new("cut", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = cutter
    m.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


# --- 本体ブランク --------------------------------------------------------
body = add_box("pixel7a_stand", (STAND_W, STAND_D, STAND_H), (0.0, 0.0, STAND_H / 2))

# --- 斜面を切り出す（h > 0 側を落とす） ----------------------------------
cut(body, add_box("cut_slope", (BIG, BIG, BIG), sp(SLOPE_LEN / 2, BIG / 2), tilt=True))

# --- スマホスロット（天面の差し込み口から下端の受けまで） ----------------
slot_cut_len = SLOT_W + SLOT_ENTRY
cut(body, add_box("cut_slot", (SLOT_L, slot_cut_len, SLOT_T),
                  sp(STOPPER + slot_cut_len / 2, -(FRONT_SKIN + SLOT_T / 2)), tilt=True))

# --- カメラ窓（外皮を貫通。カメラバーがここから顔を出す） ----------------
win_x = SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2
cut(body, add_box("cut_camwin", (CAM_WIN_L, WIN_S_LEN, 0.020),
                  sp(WIN_S_CENTER, 0.0, win_x), tilt=True))

# --- 内部の肉抜き（底面開口・中央にリブを残す） --------------------------
cav_h = -(FRONT_SKIN + SLOT_T + BACK_PLATE)
for sign in (-1.0, 1.0):
    x_in = sign * RIB_W / 2
    x_out = sign * (STAND_W / 2 - SIDE_WALL)
    cav = add_box("cut_cavity", (abs(x_out - x_in), STAND_D - 2 * WALL_Y, 0.200),
                  ((x_in + x_out) / 2, 0.0, 0.080))
    cut(cav, add_box("cut_cavity_lid", (BIG, BIG, BIG), sp(SLOPE_LEN / 2, cav_h + BIG / 2), tilt=True))
    cut(body, cav)

# --- 指穴（裏板を貫通。ここを押してスマホを抜く） ------------------------
for x in (-FINGER_X, FINGER_X):
    cut(body, add_cyl("cut_finger", FINGER_R, FINGER_DEPTH,
                      sp(FINGER_S, cav_h + FINGER_DEPTH / 2 - 0.004, x)))

# --- USB-C / スピーカーの逃げ（スマホ下端側の側壁を切り欠く） ------------
cut(body, add_box("cut_usb", (0.020, USB_W, 0.012),
                  sp(USB_S, -(FRONT_SKIN + 0.006), -(STAND_W / 2 - SIDE_WALL)), tilt=True))

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body

export_stl("pixel7a-stand")
