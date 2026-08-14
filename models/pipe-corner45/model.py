"""28mm パイプの入隅（縦柱＋水平レール）に付ける Pixel 7a ホルダー。

向きは Blender の板（Cube.005、回転 0/45/45）から取った。カメラは水平から 45° 下、
平面でも 45° 振れる。壁の入隅版（pixel7a-corner45）と同じ姿勢を、両面テープではなく
パイプ 2 本を掴んで出す。

原点は 2 本の軸の交点（角）。
    x … 外向き   y … レールに沿って奥   z … 上（縦柱は z<0 側）
    h … 視線 / s … スロットを上る向き / L … スマホの長辺

掴み方:
    水平レールに割りリング 1 個、縦柱に割りリング 1 個。それぞれ M4×2 で締める。
    直交する 2 本を掴むので摩擦に頼らない。腕が 2 本になって三角形を作るのも効く。

継手・パイプの逃げ:
    継手とパイプが占める円柱を腕とリングから彫る。ポケットは彫らない（彫るとスロットに
    穴が開くため）。当たっていないかはビルド時の印字で見る。

部品:
    pipe-corner45.stl       … 本体（ポケット＋腕 2 本＋リング 2 個）
    pipe-corner45-strap.stl … 帯。2 個刷る
    pipe-corner45-asm.stl   … 組んだ状態（確認用）

必要なもの: M4 ボルト 25mm 4 本、M4 ナット 4 個。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bmesh
import bpy
from mathutils import Matrix, Vector
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()

DL = math.radians(CAM_DEPRESSION)
PS = math.radians(YAW_DEG)
CD, SDl = math.cos(DL), math.sin(DL)
CP, SP = math.cos(PS), math.sin(PS)

HV = Vector((CD * CP, CD * SP, -SDl))     # 視線
SV = Vector((SDl * CP, SDl * SP, CD))     # スロープ
LV = Vector((-SP, CP, 0.0))               # 長辺
YA = Vector((0.0, 1.0, 0.0))              # レール軸
ZA = Vector((0.0, 0.0, 1.0))              # 柱軸

# スマホ中心（ワールド）
C_PH = HV * H_PH + SV * S_PH + LV * L_PH
S_C = STOPPER + PHONE_W / 2
H_C = -(FRONT_SKIN + CLR_T / 2 + PHONE_T / 2)


def rot_from(cx, cy, cz):
    return Matrix(((cx[0], cy[0], cz[0]),
                   (cx[1], cy[1], cz[1]),
                   (cx[2], cy[2], cz[2]))).to_euler()


POCKET_ROT = rot_from(-LV, SV, -HV)


def sp(s, h, t=0.0):
    """ポケット座標 (s, h, t) をワールドへ。t は長辺方向（-L 側が奥）。"""
    return C_PH + SV * (s - S_C) + HV * (h - H_C) - LV * t


def add_box(name, size, loc, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.name, o.scale = name, size
    bpy.ops.object.transform_apply(scale=True)
    return o


def add_cyl(name, r, depth, loc, rot=(0.0, 0.0, 0.0), verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    return o


def _apply(target, other, op):
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation, m.object, m.solver = op, other, "EXACT"
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(other, do_unlink=True)


def cut(t, o):
    _apply(t, o, "DIFFERENCE")


def mesh_from_loops(name, lo, hi):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    a = [bm.verts.new(p) for p in lo]
    b = [bm.verts.new(p) for p in hi]
    bm.faces.new(a)
    bm.faces.new(b[::-1])
    n = len(lo)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([a[i], b[i], b[j], a[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    return o


def arc(r, a0, a1, n=48):
    return [(r * math.cos(a0 + (a1 - a0) * i / n),
             r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def clamp_profile(r_out, r_in, hc, ear_h1):
    """割りリングの片側（h >= hc）＋両側の耳。(s, h) の閉じた輪郭。"""
    e0, e1 = EAR_R - EAR_W / 2, EAR_R + EAR_W / 2
    si = math.sqrt(max(r_in * r_in - hc * hc, 0.0))
    a_in = math.atan2(hc, si)
    a_ear = math.atan2(math.sqrt(max(r_out * r_out - e0 * e0, 0.0)), e0)
    pts = [(si, hc), (e1, hc), (e1, ear_h1), (e0, ear_h1)]
    pts += arc(r_out, a_ear, math.pi - a_ear)
    pts += [(-e0, ear_h1), (-e1, ear_h1), (-e1, hc), (-si, hc)]
    pts += arc(r_in, math.pi - a_in, a_in)
    return pts


# =========================================================================
# 1) ポケット
# =========================================================================
PROF = [(0.0, 0.0), (SLOPE_LEN, 0.0), (SLOPE_LEN, -SHELL_TOTAL), (0.0, -SHELL_TOTAL)]
pocket = mesh_from_loops("pipe_corner45_pocket",
                         [sp(s, h, -MOUNT_W / 2) for (s, h) in PROF],
                         [sp(s, h, MOUNT_W / 2) for (s, h) in PROF])

slot_cut_len = SLOT_W + SLOT_ENTRY
cut(pocket, add_box("cut_slot", (SLOT_L, slot_cut_len, SLOT_T),
                    sp(STOPPER + slot_cut_len / 2, -(FRONT_SKIN + SLOT_T / 2)),
                    POCKET_ROT))

win_t = SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2
cut(pocket, add_box("cut_camwin", (CAM_WIN_L, WIN_S_LEN, 0.010),
                    sp(WIN_S_CENTER, -0.003, win_t), POCKET_ROT))

# 差し込み口のテーパー: s を phi だけ h 側へ倒した面で外皮の内側を逃がす
phi = math.atan2(TAPER_D, TAPER_LEN)
tdir = (SV * math.cos(phi) + HV * math.sin(phi)).normalized()
tn = (HV * math.cos(phi) - SV * math.sin(phi)).normalized()
tp = sp(TAPER_S0, -FRONT_SKIN)
th = 0.030
cut(pocket, add_box("cut_taper", (2 * MOUNT_W, 2 * th, TAPER_CUT),
                    tp + tdir * th + tn * (TAPER_CUT / 2),
                    rot_from(-LV, tdir, -tn)))

grip_len = 0.040
cut(pocket, add_box("cut_grip", (GRIP_W, grip_len, 0.020),
                    sp(GRIP_S0 + grip_len / 2, -0.006), POCKET_ROT))

usb_t0 = -(MOUNT_W / 2 + 0.005)
usb_t1 = -(SLOT_L / 2 - USB_INTO)
cut(pocket, add_box("cut_usb", (usb_t1 - usb_t0, USB_W, USB_T),
                    sp(USB_S, -SHELL_TOTAL / 2, (usb_t0 + usb_t1) / 2), POCKET_ROT))

latches = []
for sx in (1, -1):
    r = LATCH_H * 1.8
    latches.append(add_cyl("pipe_corner45_latch_%d" % (sx > 0), r, LATCH_L,
                           sp(SLOPE_LEN - LATCH_S, -FRONT_SKIN + (r - LATCH_H),
                              sx * LATCH_X),
                           rot_from(SV, -HV, -LV), verts=24))

# =========================================================================
# 2) リング 2 個と帯
# =========================================================================
nut_r = NUT_AF / math.sqrt(3.0)
NUT_OVER = 0.0002
nut_depth = NUT_T + NUT_OVER
nut_h = CLAMP_GAP + EAR_T + NUT_OVER - nut_depth / 2
EAR_H1 = CLAMP_GAP + EAR_T
H_BACK = H_PH + (-SHELL_TOTAL - H_C)      # ポケット裏面の h 座標


def ring_basis(axis):
    """軸に直交する面内で、視線に一番近い向き e1 と、それに直交する e2。"""
    e1 = (HV - axis * HV.dot(axis)).normalized()
    return e1, axis.cross(e1)


def build_clamp(name, axis, at, r_in):
    """割りリング（本体側）を作る。at は軸上の位置ベクトル。"""
    e1, e2 = ring_basis(axis)
    prof = clamp_profile(RING_R, r_in, CLAMP_GAP, EAR_H1)
    lo = [at + e2 * s + e1 * h - axis * (RING_W / 2) for (s, h) in prof]
    hi = [at + e2 * s + e1 * h + axis * (RING_W / 2) for (s, h) in prof]
    ring = mesh_from_loops(name, lo, hi)
    strap_prof = clamp_profile(BORE_D / 2 + STRAP_ARC, r_in, CLAMP_GAP, EAR_H1)
    strap = mesh_from_loops(name.replace("ring", "strap"),
                            [at - e2 * s - e1 * h - axis * (RING_W / 2)
                             for (s, h) in strap_prof],
                            [at - e2 * s - e1 * h + axis * (RING_W / 2)
                             for (s, h) in strap_prof])
    rot = rot_from(e2, axis, e1)
    for sx in (1, -1):
        c0 = at + e2 * (sx * EAR_R)
        cut(ring, add_cyl("screw", SCREW_D / 2, 0.060, c0, rot))
        cut(strap, add_cyl("screw", SCREW_D / 2, 0.060, c0, rot))
        cut(ring, add_cyl("nut", nut_r, nut_depth, c0 + e1 * nut_h, rot, verts=6))
        cut(ring, add_box("nut_slot", (RING_W, NUT_SLOT_W, nut_depth),
                          c0 + e1 * nut_h + axis * (RING_W / 2),
                          rot_from(axis, e2, e1)))
    return ring, strap, e1, e2


Y_RAIL = JOINT_RAIL + JOINT_GAP + RING_W / 2
Z_POST = -(JOINT_POST + JOINT_GAP + RING_W / 2)

ring_rail, strap_rail, e1r, e2r = build_clamp(
    "pipe_corner45_ring_rail", YA, YA * Y_RAIL, BORE_D / 2)
ring_post, strap_post, e1p, e2p = build_clamp(
    "pipe_corner45_ring_post", ZA, ZA * Z_POST, BORE_D / 2 + POST_EXTRA)

# =========================================================================
# 3) 腕（リング → ポケット）。軸と視線を含む面に沿う板
# =========================================================================
def build_web(name, axis, at, width):
    """リングからポケットへ渡す腕。板の面はリングの軸と「リング→スマホ」を含む。

    面が軸を含まないと、腕は軸方向へ登れない。柱側はポケットが 33mm 上にあるので、
    軸に直交する板にしたら 0mm3 しか重ならなかった（交差体積で実測）。
    面が軸を含めば、リングの肉を軸方向に貫き、そのままポケットまで登れる。
    """
    v = C_PH - at
    d = (v - axis * v.dot(axis)).normalized()      # 軸に直交する成分（外向き）
    th = d.cross(axis)                             # 板の厚み方向
    reach = 0.300
    a_lo = min(-(RING_W / 2 + 0.004), v.dot(axis) - 0.008)
    a_hi = max(RING_W / 2 + 0.004, v.dot(axis) + 0.008)
    mid = (at + d * (RING_R - 0.004 + reach / 2) + axis * ((a_lo + a_hi) / 2))
    web = add_box(name, (reach, a_hi - a_lo, WEB_T), mid, rot_from(d, axis, th))
    # ポケット裏面より先へは出さない。裏板は 3mm なので食い込みは 2mm まで
    cut(web, add_box("lid", (0.4, 0.4, 0.4),
                     C_PH + HV * (-SHELL_TOTAL - H_C + WEB_BITE + 0.2), POCKET_ROT))
    return web


web_rail = build_web("pipe_corner45_web_rail", YA, YA * Y_RAIL, WEB_Y)
web_post = build_web("pipe_corner45_web_post", ZA, ZA * Z_POST, WEB_Z)

_v = C_PH - YA * Y_RAIL
_dr = (_v - YA * _v.dot(YA)).normalized()
for sx in (1, -1):
    cut(web_rail, add_cyl("tether", TETHER_D / 2, WEB_T + 0.01,
                          YA * Y_RAIL + _dr * (RING_R + 0.030)
                          + YA * (_v.dot(YA) / 2 + sx * 0.013),
                          rot_from(_dr, YA, _dr.cross(YA))))

# =========================================================================
# 3.5) 橋（2 つのリングを直接つなぐ L 字の板）
# =========================================================================
# 手で作った形（Cube.006）の要点はこれ。2 本のパイプを形で拘束する板を渡すと、
# 締め付けの摩擦に頼らずに回転が止まる。板の面は 2 つのリング中心の両方を含み、
# かつ外（+x）へ逃げられる向きに取る。継手の円柱で彫れば、角の内側が斜めに
# 落ちて、手打ちの形と同じ逃げになる。
_a1, _a2 = YA * Y_RAIL, ZA * Z_POST
_d1 = (_a2 - _a1).normalized()               # レールのリング → 柱のリング
_d2 = Vector((1.0, 0.0, 0.0))                # 外向き
_span = (_a2 - _a1).length + 2 * RING_R
_x0, _x1 = -RING_R, BRIDGE_X
bridge = add_box("pipe_corner45_bridge", (_span, _x1 - _x0, WEB_T),
                 (_a1 + _a2) / 2 + _d2 * ((_x0 + _x1) / 2),
                 rot_from(_d1, _d2, _d1.cross(_d2)))

# =========================================================================
# 4) パイプと継手の逃げ（腕とリングから彫る。ポケットは彫らない）
# =========================================================================
LONG = 0.700
for part in (web_rail, web_post, ring_rail, ring_post, bridge):
    cut(part, add_cyl("rail_pipe", BORE_D / 2, LONG, (0.0, LONG / 2 - 0.001, 0.0),
                      (math.pi / 2, 0.0, 0.0), verts=64))
    cut(part, add_cyl("post_pipe", BORE_D / 2 + POST_EXTRA, LONG,
                      (0.0, 0.0, -LONG / 2 + 0.001), verts=64))
    cut(part, add_cyl("joint_rail", JOINT_R + JOINT_GAP, 2 * JOINT_RAIL,
                      (0.0, 0.0, 0.0), (math.pi / 2, 0.0, 0.0), verts=64))
    cut(part, add_cyl("joint_post", JOINT_R + JOINT_GAP, 2 * JOINT_POST,
                      (0.0, 0.0, 0.0), verts=64))

# =========================================================================
# 5) 検証
# =========================================================================
def clearances(p):
    """(継手すきま, レール軸からの距離, 柱軸からの距離)"""
    rr = math.hypot(p[0], p[2])
    dy = max(-p[1], p[1] - JOINT_RAIL)
    a = (rr - JOINT_R) if dy <= 0 else math.hypot(dy, max(rr - JOINT_R, 0.0))
    rp = math.hypot(p[0], p[1])
    dz = max(p[2], -JOINT_POST - p[2])
    b = (rp - JOINT_R) if dz <= 0 else math.hypot(dz, max(rp - JOINT_R, 0.0))
    return min(a, b), rr, rp


bad = 0
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    b = bmesh.new()
    b.from_mesh(o.data)
    bmesh.ops.dissolve_degenerate(b, dist=1e-6, edges=b.edges[:])
    n = sum(1 for e in b.edges if not e.is_manifold)
    b.to_mesh(o.data)
    b.free()
    bad += n
    mw = o.matrix_world
    vals = [clearances(mw @ v.co) for v in o.data.vertices]
    print("part %-28s nm=%d verts=%4d 継手%+7.2f レール軸%7.2f 柱軸%7.2f"
          % (o.name, n, len(o.data.vertices),
             min(v[0] for v in vals) * 1000, min(v[1] for v in vals) * 1000,
             min(v[2] for v in vals) * 1000))

# --- 部品どうしが本当に体積を共有しているか（重ねて一体化させる前提なので命） ---
def shared_volume(a, b):
    """a と b の交差体積 (mm3)。0 なら繋がっていない。"""
    dup = a.copy()
    dup.data = a.data.copy()
    bpy.context.collection.objects.link(dup)
    bpy.ops.object.select_all(action="DESELECT")
    dup.select_set(True)
    bpy.context.view_layer.objects.active = dup
    m = dup.modifiers.new("x", "BOOLEAN")
    m.operation, m.object, m.solver = "INTERSECT", b, "EXACT"
    bpy.ops.object.modifier_apply(modifier=m.name)
    v = 0.0
    mw = dup.matrix_world
    me = dup.data
    me.calc_loop_triangles()
    for t in me.loop_triangles:
        p0, p1, p2 = (mw @ me.vertices[i].co for i in t.vertices)
        v += p0.dot(p1.cross(p2)) / 6.0
    bpy.data.objects.remove(dup, do_unlink=True)
    return abs(v) * 1e9


# 腕は必ずリングとポケットの両方に食い込んでいなければならない。
# リングとポケットは直接は触れない（腕が渡す）ので、ここには入れない。
for a, b in ((web_rail, ring_rail), (web_rail, pocket),
             (web_post, ring_post), (web_post, pocket),
             (bridge, ring_rail), (bridge, ring_post)):
    v = shared_volume(a, b)
    print("重なり %-12s x %-12s = %8.1f mm3%s"
          % (a.name.replace("pipe_corner45_", ""), b.name.replace("pipe_corner45_", ""),
             v, "" if v > 100.0 else "   ← 繋がっていない"))

pj, pr, pp = 1e9, 1e9, 1e9
for s in (STOPPER, STOPPER + PHONE_W):
    for h in (-(FRONT_SKIN + CLR_T / 2), -(FRONT_SKIN + CLR_T / 2 + PHONE_T)):
        for t in (-PHONE_L / 2, PHONE_L / 2):
            a, r1, r2 = clearances(sp(s, h, t))
            pj, pr, pp = min(pj, a), min(pr, r1), min(pp, r2)
print("---")
print("非多様体の合計: %d" % bad)
print("リング: レール y=%.1fmm / 柱 z=%.1fmm" % (Y_RAIL * 1000, Z_POST * 1000))
print("スマホ中心: レール軸から %.1fmm / 柱軸から %.1fmm"
      % (math.hypot(C_PH.x, C_PH.z) * 1000, math.hypot(C_PH.x, C_PH.y) * 1000))
print("実機のすきま: 継手 %+.2fmm / レール %+.2fmm / 柱 %+.2fmm%s"
      % (pj * 1000, (pr - PIPE_OD / 2) * 1000, (pp - PIPE_OD / 2) * 1000,
         "" if min(pj, pr - PIPE_OD / 2, pp - PIPE_OD / 2) > 0
         else "  ← H_PH を増やすこと"))
print("俯角 %.0f° / 振り %.0f°" % (CAM_DEPRESSION, YAW_DEG))

body = [pocket, web_rail, web_post, ring_rail, ring_post, bridge] + latches


def export_upright(name, parts, rot):
    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    piv = bpy.context.object
    for o in parts:
        o.parent = piv
    piv.rotation_euler = rot
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ v.co for o in parts for v in o.data.vertices]
    piv.location = (-(min(p.x for p in pts) + max(p.x for p in pts)) / 2,
                    -(min(p.y for p in pts) + max(p.y for p in pts)) / 2,
                    -min(p.z for p in pts))
    bpy.context.view_layer.update()
    export_stl(name, only=parts)
    piv.rotation_euler = (0.0, 0.0, 0.0)
    piv.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    for o in parts:
        o.parent = None
    bpy.data.objects.remove(piv, do_unlink=True)


# スロットの空洞を縦のスリットにする向き（長辺 L を立てる）
UP = rot_from(-HV, SV.cross(-HV), SV) if False else \
    Matrix(((LV.x, HV.x, SV.x), (LV.y, HV.y, SV.y), (LV.z, HV.z, SV.z))).inverted().to_euler()
export_upright("pipe-corner45", body, UP)
export_upright("pipe-corner45-strap", [strap_rail], UP)
export_stl("pipe-corner45-asm")
