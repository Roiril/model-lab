"""Pixel 7a 壁掛けマウント — 壁に貼り、スマホを伏せて収めてカメラだけ斜め下 40° へ向ける。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bmesh
import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()

# --- スロットのローカル座標系 --------------------------------------------
# 壁面は y=0、本体は y>0 側にある。
# s: スロットを上る方向（壁ぎわの下端から手前上へ）
# h: スマホ背面の外向き法線＝カメラの視線（斜め下・手前）。h=0 が外皮の外表面で、
#    h が負の側にスロットと裏板が積み重なる。
A = math.radians(TILT_DEG)
UY, UZ = math.cos(A), math.sin(A)
NY, NZ = math.sin(A), -math.cos(A)
ORG_Y = SHELL_TOTAL * math.sin(A)   # s=0, h=-SHELL_TOTAL がちょうど壁面に乗る位置
ORG_Z = 0.0
BIG = 0.4


def sp(s, h, x=0.0):
    """スロット座標 (s, h) をワールド座標へ。"""
    return (x, ORG_Y + s * UY + h * NY, ORG_Z + s * UZ + h * NZ)


def yz(s, h):
    p = sp(s, h)
    return (p[1], p[2])


def add_box(name, size, loc, rot_x=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=(rot_x, 0.0, 0.0))
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return o


def extrude_profile(name, pts, x0, x1):
    """Y-Z 平面の多角形を X 方向に押し出して閉じた立体にする。"""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    lo = [bm.verts.new((x0, y, z)) for (y, z) in pts]
    hi = [bm.verts.new((x1, y, z)) for (y, z) in pts]
    bm.faces.new(lo)
    bm.faces.new(hi[::-1])
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], hi[i], hi[j], lo[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
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


# --- 外形（側面の輪郭を X 方向へ押し出す） -------------------------------
# 壁面 z=0..PLATE_H が貼付面。底面は水平、そこから外皮が 50° で立ち上がる。
PROFILE = [
    (0.0, 0.0),                    # 壁ぎわの底
    (ORG_Y, 0.0),                  # 底面の手前端＝外皮の起点
    yz(SLOPE_LEN, 0.0),            # 外皮の先端（いちばん手前）
    yz(SLOPE_LEN, -SHELL_TOTAL),   # 裏板の先端
    (0.0, PLATE_H),                # 背板の上端
]
body = extrude_profile("pixel7a_wallmount", PROFILE, -MOUNT_W / 2, MOUNT_W / 2)

# --- スマホスロット（差し込み口から下端の受けまで） ----------------------
slot_cut_len = SLOT_W + SLOT_ENTRY
cut(body, add_box("cut_slot", (SLOT_L, slot_cut_len, SLOT_T),
                  sp(STOPPER + slot_cut_len / 2, -(FRONT_SKIN + SLOT_T / 2)), A))

# --- カメラ窓（外皮を貫通。カメラバーがここから顔を出す） ----------------
win_x = SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2
cut(body, add_box("cut_camwin", (CAM_WIN_L, WIN_S_LEN, 0.010),
                  sp(WIN_S_CENTER, -0.003, win_x), A))

# --- 差し込み口のテーパー（外皮側だけ h の外へ逃がす） -------------------
phi = math.atan2(TAPER_D, TAPER_LEN)
ta = A - phi   # s が増えるほど外皮の内面が h の外へ退く
tdy, tdz = math.cos(ta), math.sin(ta)
tny, tnz = math.sin(ta), -math.cos(ta)
tp = sp(TAPER_S0, -FRONT_SKIN)
thalf = 0.030
cut(body, add_box("cut_taper", (2 * MOUNT_W, 2 * thalf, TAPER_D),
                  (0.0,
                   tp[1] + thalf * tdy + (TAPER_D / 2) * tny,
                   tp[2] + thalf * tdz + (TAPER_D / 2) * tnz), ta))

# --- 指がかり（中央だけ外皮と裏板を落としてスマホ上端を摘まめるようにする） ---
grip_len = 0.040
cut(body, add_box("cut_grip", (GRIP_W, grip_len, 0.020),
                  sp(GRIP_S0 + grip_len / 2, -0.006), A))

# 指がかりの開口に中央ガセットが橋のように残るので、その区間だけ落とす。
cut(body, add_box("cut_grip_gusset", (GUSSET_W + 0.004, grip_len, 0.041),
                  sp(GRIP_S0 + grip_len / 2, -0.0345), A))

# --- USB-C / スピーカーの逃げ（スマホ下端側の側壁だけを切り欠く） --------
# 外皮・裏板とは面一にせず、厚み方向はスロットの内側で止める（coplanar を避ける）。
usb_x0 = -(MOUNT_W / 2 + 0.005)
usb_x1 = -(SLOT_L / 2 - 0.0005)
cut(body, add_box("cut_usb", (usb_x1 - usb_x0, USB_W, USB_T),
                  sp(USB_S, -SHELL_TOTAL / 2, (usb_x0 + usb_x1) / 2), A))

# --- 背板とスロット部の間を肉抜き（左右の側壁と中央のガセットは残す） ----
# 裏板の外面より内側（h < -SHELL_TOTAL）かつ背板より手前（y > PLATE_T）を抜く。
for x0, x1 in ((-MOUNT_W / 2 + SIDE_WALL, -GUSSET_W / 2),
               (GUSSET_W / 2, MOUNT_W / 2 - SIDE_WALL)):
    cav = add_box("cut_cavity", (x1 - x0, 0.300, 0.300),
                  ((x0 + x1) / 2, PLATE_T + 0.150, 0.150))
    cut(cav, add_box("cut_cavity_lid", (BIG, BIG, BIG),
                     sp(SLOPE_LEN / 2, -SHELL_TOTAL + BIG / 2), A))
    cut(body, cav)

# --- 面積ゼロの縮退面を掃除する（テーパーが外皮の先端をほぼ一点で切るため出る） ---
_bm = bmesh.new()
_bm.from_mesh(body.data)
bmesh.ops.dissolve_degenerate(_bm, dist=1e-6, edges=_bm.edges[:])
_bm.to_mesh(body.data)
_bm.free()

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body

export_stl("pixel7a-wallmount")
