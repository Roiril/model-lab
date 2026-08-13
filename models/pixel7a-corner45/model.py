"""Pixel 7a 入隅マウント — 部屋の角に貼り、二等分線の斜め下 40° へカメラを向ける。

角を挟む 2 枚の壁を x=0 と y=0 に置く。部屋の中は x>0, y>0。
角からの距離を測る軸を 2 本使う。

    u … 二等分線（部屋の奥へ向かう）   v … 幅方向（角をまたぐ弦）

壁はこの座標で u = v（y=0 の壁）と u = -v（x=0 の壁）の 2 面になる。部屋の中は
u > |v| なので、幅 MOUNT_W のポケットは u >= MOUNT_W/2 まで前へ出さないと角へめり込む。
その手前に残る三角形は部屋側から見て死んでいる空間なので、何も置かない。

ポケットの左右に中空の三角柱（ウィング）を 1 本ずつ付け、その外面を壁へ当てて
両面テープの貼付面にする。ウィングは角の側ではなくポケットの外側へ張り出す。
角の側へ回すと、ポケットが前へ倒れている分だけ上へ行くほど壁から離れ、そこを
埋める箱が必要になる。外側なら壁とポケット側壁が 45° で交わるので、その谷を
そのまま殻で塞げばよい。
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

A = math.radians(TILT_DEG)
CA, SA = math.cos(A), math.sin(A)
R2 = math.sqrt(2.0)
BIG = 0.4

# ポケットのローカル原点。s=0, h=0（外皮の下端）が z=0 に来るように置く。
U_ORG = U_BACK + SHELL_TOTAL * SA
H_W = SLOPE_LEN * SA          # 60.2mm 外皮の上端の高さ＝ウィングの高さ
ROT = (A, 0.0, -math.pi / 4)  # ワールドへ：X 回りに倒してから Z 回りに -45°


def world(u, v, z):
    """(u, v, z) をワールド座標へ。"""
    return ((u + v) / R2, (u - v) / R2, z)


def sp(s, h, t=0.0):
    """ポケット座標 (s, h, t) をワールド座標へ。t は幅方向＝v。"""
    return world(U_ORG + s * CA + h * SA, t, s * SA - h * CA)


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


def make_mesh(name, verts, faces):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in verts]
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    return o


# =========================================================================
# 1) ポケット — (u, z) 平面の輪郭を幅方向へ押し出す
# =========================================================================
# 後ろ下は垂直に落として平らな底を作る。ここが印刷の 1 層目になる。
PROFILE = [
    (U_BACK, 0.0),                                        # 底の後端
    (U_ORG, 0.0),                                         # 外皮の下端（s=0, h=0）
    (U_ORG + SLOPE_LEN * CA, SLOPE_LEN * SA),             # 外皮の先端（s=L, h=0）
    (U_ORG + SLOPE_LEN * CA - SHELL_TOTAL * SA,
     SLOPE_LEN * SA + SHELL_TOTAL * CA),                  # 裏板の先端（s=L, h=-T）
    (U_BACK, SHELL_TOTAL * CA),                           # 裏板の下端（s=0, h=-T）
]
HALF = MOUNT_W / 2
_n = len(PROFILE)
_v = [world(u, -HALF, z) for (u, z) in PROFILE] + [world(u, HALF, z) for (u, z) in PROFILE]
_f = [tuple(range(_n)), tuple(range(2 * _n - 1, _n - 1, -1))]
_f += [(i, _n + i, _n + (i + 1) % _n, (i + 1) % _n) for i in range(_n)]
body = make_mesh("pixel7a_c45_pocket", _v, _f)

# --- スマホスロット（差し込み口から下端の受けまで） ---
slot_cut_len = SLOT_W + SLOT_ENTRY
cut(body, add_box("cut_slot", (SLOT_L, slot_cut_len, SLOT_T),
                  sp(STOPPER + slot_cut_len / 2, -(FRONT_SKIN + SLOT_T / 2)), ROT))

# --- カメラ窓（外皮を貫通。カメラバーがここから顔を出す） ---
win_t = SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2
cut(body, add_box("cut_camwin", (CAM_WIN_L, WIN_S_LEN, 0.010),
                  sp(WIN_S_CENTER, -0.003, win_t), ROT))

# --- 差し込み口のテーパー（外皮側だけスロットへ逃がす） ---
phi = math.atan2(TAPER_D, TAPER_LEN)
ta = A - phi
tp_u = U_ORG + TAPER_S0 * CA + (-FRONT_SKIN) * SA
tp_z = TAPER_S0 * SA + FRONT_SKIN * CA
th = 0.030
cu = tp_u + th * math.cos(ta) - (TAPER_CUT / 2) * math.sin(ta)
cz = tp_z + th * math.sin(ta) + (TAPER_CUT / 2) * math.cos(ta)
cut(body, add_box("cut_taper", (2 * MOUNT_W, 2 * th, TAPER_CUT),
                  world(cu, 0.0, cz), (ta, 0.0, -math.pi / 4)))

# --- 指がかり（中央だけ外皮と裏板を落としてスマホ上端を摘まむ） ---
grip_len = 0.040
cut(body, add_box("cut_grip", (GRIP_W, grip_len, 0.020),
                  sp(GRIP_S0 + grip_len / 2, -0.006), ROT))


# =========================================================================
# 2) ウィング（中空の三角柱。外面が壁＝貼付面）
# =========================================================================
def offset_poly(pts, t):
    """凸多角形（CCW）を内側へ t だけオフセットする。"""
    lines = []
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L          # CCW の内向き法線
        lines.append((x0 + nx * t, y0 + ny * t, dx, dy))
    out = []
    for i in range(n):
        x0, y0, dx0, dy0 = lines[i - 1]
        x1, y1, dx1, dy1 = lines[i]
        den = dx0 * dy1 - dy0 * dx1
        s = ((x1 - x0) * dy1 - (y1 - y0) * dx1) / den
        out.append((x0 + dx0 * s, y0 + dy0 * s))
    return out


a = HALF - WING_BITE        # 側壁ぎわの面の v（ポケットへ 2mm 食い込む）
r = a + WING_REAR           # 後端を落とす位置の u


def wing_poly(q):
    """前端を u = q に置いたウィング断面（u, v）。CCW。"""
    return [
        (r, a),                  # 側壁ぎわの後端
        (q, a),                  # 側壁ぎわの前端
        (q, WING_VMAX),          # 前面の外端
        (WING_VMAX, WING_VMAX),  # 壁の上の外端
        (r, r),                  # 壁の上の後端
    ]


# 高さの取り方。外皮の上端（H_W）まではポケットの前面に沿って前へ倒れながら太り、
# そこから上はポケットが無いので前端を絞って細い鰭にする。上へ伸ばすほど、前へ
# 倒れようとする力を受け止める腕が長くなる。壁に当たる面の幅は上まで変わらない。
LEVELS = [(0.0, U_ORG + PAD_OVER),
          (H_W, U_ORG + H_W / math.tan(A) + PAD_OVER),
          (WING_H, r + WING_TOP_D)]

wings = []
for sign in (1.0, -1.0):
    polys = [wing_poly(q) for (_, q) in LEVELS]
    n = len(polys[0])
    verts, faces = [], []
    for (z, _), p in zip(LEVELS, polys):
        verts += [world(u, sign * v, z) for (u, v) in p]
        verts += [world(u, sign * v, z) for (u, v) in offset_poly(p, WING_T)]
    for k in range(len(LEVELS) - 1):
        O0, I0 = k * 2 * n, k * 2 * n + n
        O1, I1 = (k + 1) * 2 * n, (k + 1) * 2 * n + n
        for i in range(n):
            j = (i + 1) % n
            faces.append((O0 + i, O0 + j, O1 + j, O1 + i))   # 外側
            faces.append((I0 + j, I0 + i, I1 + i, I1 + j))   # 内側
    top = (len(LEVELS) - 1) * 2 * n
    for i in range(n):
        j = (i + 1) % n
        faces.append((j, i, n + i, n + j))                   # 下端の縁
        faces.append((top + i, top + j, top + n + j, top + n + i))   # 上端の縁
    wings.append(make_mesh("pixel7a_c45_wing_%s" % ("l" if sign > 0 else "r"),
                           verts, faces))

# --- 貼付面を角の側へ伸ばす帯（壁の上をまっすぐ後ろへ。幅は増えない） ---
tab_x1 = r * R2 + PAD_LAP        # ウィングの壁面と重ねる
tab_x0 = r * R2 - PAD_TAB
tab_len = tab_x1 - tab_x0
wings.append(add_box("pixel7a_c45_pad_l", (tab_len, PAD_TAB_T, WING_H),
                     ((tab_x0 + tab_x1) / 2, PAD_TAB_T / 2, WING_H / 2)))
wings.append(add_box("pixel7a_c45_pad_r", (PAD_TAB_T, tab_len, WING_H),
                     (PAD_TAB_T / 2, (tab_x0 + tab_x1) / 2, WING_H / 2)))

# --- USB-C / スピーカーの逃げ（側壁とウィングを貫く） ---
usb_t0 = -(HALF + WING_T + 0.006)
usb_t1 = -(SLOT_L / 2 - USB_INTO)
for target in [body] + wings:
    cut(target, add_box("cut_usb", (usb_t1 - usb_t0, USB_W, USB_T),
                        sp(USB_S, -SHELL_TOTAL / 2, (usb_t0 + usb_t1) / 2), ROT))

# =========================================================================
# 3) 検証 — 壁を突き抜けていないか、各パーツが閉じているか
# =========================================================================
worst = 1e9
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    b = bmesh.new()
    b.from_mesh(o.data)
    bmesh.ops.dissolve_degenerate(b, dist=1e-6, edges=b.edges[:])
    n_bad = sum(1 for e in b.edges if not e.is_manifold)
    b.to_mesh(o.data)
    b.free()
    # 壁の内側にいるか（x >= 0 かつ y >= 0）。負なら壁へめり込んでいる。
    mw = o.matrix_world
    m = min(min((mw @ v.co).x, (mw @ v.co).y) for v in o.data.vertices)
    worst = min(worst, m)
    print("part %-24s non_manifold=%d verts=%3d wall_clr=%+6.2fmm"
          % (o.name, n_bad, len(o.data.vertices), m * 1000))

print("---")
print("角からの張り出し u: %.1fmm / 全幅 v: %.1fmm / 高さ %.1fmm"
      % ((U_ORG + SLOPE_LEN * CA + PAD_OVER) * 1000, 2 * WING_VMAX * 1000,
         (SLOPE_LEN * SA + SHELL_TOTAL * CA) * 1000))
print("壁からの最小クリアランス: %+.2fmm（負なら壁を突き抜けている）" % (worst * 1000))
print("カメラ俯角 %.0f° / 壁に対する振り 45°" % CAM_DEPRESSION)

export_stl("pixel7a-corner45")
