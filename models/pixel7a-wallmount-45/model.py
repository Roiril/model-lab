"""Pixel 7a 壁掛けマウント 横 45° 振り

正面版（pixel7a-wallmount）のスロット部を垂直軸まわりに YAW_DEG だけ回したもの。
壁面 y=0 と背板の向きは変えていない。カメラは壁の正面から YAW_DEG 振れた方向の、
斜め下 (90 - TILT_DEG)° を向く。

回すと水平方向に対角線分だけ広がり、背板とスロット部の間が大きく離れる。そこは
縦のガセットで渡す。ガセットを Boolean で母材へ融合させると、斜めのブロックと
垂直な板の交差が原因でメッシュが壊れる（実測: 非多様体 270 本）。そこで
スロット部・背板・ガセットを互いに BITE だけ食い込ませた別々の閉じた立体として
書き出す。スライサーは重なったシェルを 1 つの実体として扱うので、印刷結果は同じ。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bmesh
import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()

# --- 座標系 --------------------------------------------------------------
# s: スロットを上る方向 / h: スマホ背面の外向き法線（カメラの視線）
A = math.radians(TILT_DEG)
YAW = math.radians(YAW_DEG)
UY, UZ = math.cos(A), math.sin(A)
NY, NZ = math.sin(A), -math.cos(A)
CY, SY = math.cos(YAW), math.sin(YAW)
LOCAL_ORG_Y = SHELL_TOTAL * math.sin(A)
BIG = 0.4
ROT = (A, 0.0, YAW)
OFFSET_Y = (MOUNT_W / 2) * abs(SY) + PLATE_T


def sp(s, h, x=0.0):
    """スロット座標 (s, h, x) をワールド座標へ。"""
    ly = LOCAL_ORG_Y + s * UY + h * NY
    lz = s * UZ + h * NZ
    return (x * CY - ly * SY, x * SY + ly * CY + OFFSET_Y, lz)


def add_box(name, size, loc, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return o


def cut(target, cutter):
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = cutter
    m.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def back_of_slot(bite):
    """スロット部の裏面より背板側だけを残すためのカッター。"""
    return add_box("lid", (BIG, BIG, BIG),
                   sp(SLOPE_LEN / 2, -SHELL_TOTAL + bite + BIG / 2), ROT)


# =========================================================================
# 1) スロット部
# =========================================================================
body = add_box("pixel7a_wm45_slot", (MOUNT_W, SLOPE_LEN, SHELL_TOTAL),
               sp(SLOPE_LEN / 2, -SHELL_TOTAL / 2), ROT)

slot_cut_len = SLOT_W + SLOT_ENTRY
cut(body, add_box("cut_slot", (SLOT_L, slot_cut_len, SLOT_T),
                  sp(STOPPER + slot_cut_len / 2, -(FRONT_SKIN + SLOT_T / 2)), ROT))

win_x = SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2
cut(body, add_box("cut_camwin", (CAM_WIN_L, WIN_S_LEN, 0.010),
                  sp(WIN_S_CENTER, -0.003, win_x), ROT))

# 差し込み口のテーパー（外皮の内面をスロット側へ逃がす）
phi = math.atan2(TAPER_D, TAPER_LEN)
ta = A - phi
tdy, tdz = math.cos(ta), math.sin(ta)
tny, tnz = math.sin(ta), -math.cos(ta)
tly = LOCAL_ORG_Y + TAPER_S0 * UY + (-FRONT_SKIN) * NY
tlz = TAPER_S0 * UZ + (-FRONT_SKIN) * NZ
th = 0.030
cly = tly + th * tdy - (TAPER_CUT / 2) * tny
clz = tlz + th * tdz - (TAPER_CUT / 2) * tnz
cut(body, add_box("cut_taper", (2 * MOUNT_W, 2 * th, TAPER_CUT),
                  (-cly * SY, cly * CY + OFFSET_Y, clz), (ta, 0.0, YAW)))

cut(body, add_box("cut_grip", (GRIP_W, 0.040, 0.020),
                  sp(GRIP_S0 + 0.020, -0.006), ROT))

usb_x0 = -(MOUNT_W / 2 + 0.005)
usb_x1 = -(SLOT_L / 2 - USB_INTO)
cut(body, add_box("cut_usb", (usb_x1 - usb_x0, USB_W, USB_T),
                  sp(USB_S, -SHELL_TOTAL / 2, (usb_x0 + usb_x1) / 2), ROT))

# =========================================================================
# 2) 背板（壁に貼る。向きは正面版のまま）
# =========================================================================
corners = [sp(s, h, x)
           for s in (0.0, SLOPE_LEN) for h in (0.0, -SHELL_TOTAL)
           for x in (-MOUNT_W / 2, MOUNT_W / 2)]
PLATE_X0 = min(c[0] for c in corners) - PLATE_MARGIN
PLATE_X1 = max(c[0] for c in corners) + PLATE_MARGIN
plate_w = PLATE_X1 - PLATE_X0
Y_MAX = max(c[1] for c in corners)

# 背板もガセットも上下の帯だけにする（全高にすると材料が倍以上になる）
BANDS = ((0.0, BAND_H), (PLATE_H - BAND_H, PLATE_H))

for j, (z0, z1) in enumerate(BANDS):
    add_box("pixel7a_wm45_plate_%d" % j, (plate_w, PLATE_T, z1 - z0),
            ((PLATE_X0 + PLATE_X1) / 2, PLATE_T / 2, (z0 + z1) / 2))

# =========================================================================
# 3) ガセット（背板とスロット部を渡す縦の板。両側へ BITE 食い込ませる）
# =========================================================================
made = 0
for i in range(GUSSET_N):
    xg = PLATE_X0 + plate_w * (i + 0.5) / GUSSET_N
    y0 = PLATE_T - GUSSET_BITE          # 背板の中から始める
    for j, (z0, z1) in enumerate(BANDS):
        gus = add_box("pixel7a_wm45_gusset_%d_%d" % (i, j),
                      (GUSSET_T, Y_MAX - y0, z1 - z0),
                      (xg, y0 + (Y_MAX - y0) / 2, (z0 + z1) / 2))
        cut(gus, back_of_slot(GUSSET_BITE))   # スロット部の裏板へ BITE 食い込ませる
        if len(gus.data.vertices) == 0 or gus.dimensions.y < GUSSET_MIN:
            bpy.data.objects.remove(gus, do_unlink=True)
            continue
        made += 1

print("gussets: %d / %d" % (made, GUSSET_N))
print("plate x: %.2f .. %.2f mm, Y_MAX: %.2f mm"
      % (PLATE_X0 * 1000, PLATE_X1 * 1000, Y_MAX * 1000))

# --- 各パーツを掃除して報告 ----------------------------------------------
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    b = bmesh.new()
    b.from_mesh(o.data)
    bmesh.ops.dissolve_degenerate(b, dist=1e-6, edges=b.edges[:])
    n = sum(1 for e in b.edges if not e.is_manifold)
    b.to_mesh(o.data)
    b.free()
    print("part %-28s non_manifold=%d verts=%d" % (o.name, n, len(o.data.vertices)))

export_stl("pixel7a-wallmount-45")
