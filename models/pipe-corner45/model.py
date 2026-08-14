"""28mm パイプの入隅（縦柱＋水平レール）に付ける Pixel 7a ホルダー。

壁の入隅版（pixel7a-corner45）を、両面テープではなくパイプ 2 本を掴む形に置き換えた。
壁の版は首を 45° 振っていたが、こちらは振らない。スマホの長辺は水平レールと平行で、
カメラはレールの半径方向・外向きに 45° 下を向く。

原点は 2 本の軸の交点（角）。
    x … 外向き   y … レールに沿って奥   z … 上（縦柱は z<0 側）
    h = ( cos45, 0, -sin45) カメラの視線
    s = ( sin45, 0,  cos45) スロットを上る向き。差し込み口は上

掴み方:
    水平レールに割りリング 1 個、縦柱に割りリング 1 個。それぞれ M4×2 で締める。
    直交する 2 本を掴むので摩擦に頼らない。レール側が縦軸まわりの回転を止め、
    柱側がレール軸まわりの回転を止める。

継手・パイプの逃げ:
    位置決めで気をつけるのではなく、継手とパイプが占める円柱を全部品から彫る。
    実測して JOINT_* を直せば、当たる部品は自動で削れる。

部品:
    pipe-corner45.stl       … 本体（ポケット＋板 2 枚＋リング 2 個）
    pipe-corner45-strap.stl … 帯。レール用・柱用で同じものを 2 個刷る
    pipe-corner45-asm.stl   … 組んだ状態（確認用）

必要なもの: M4 ボルト 25mm 4 本、M4 ナット 4 個。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bmesh
import bpy
from mathutils import Matrix
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()

D = math.radians(CAM_DEPRESSION)
CD, SD = math.cos(D), math.sin(D)
HV = (CD, 0.0, -SD)     # h: カメラの視線
SV = (SD, 0.0, CD)      # s: スロットを上る向き
BIG = 0.4

# ポケットのローカル軸 → ワールド。幅方向 t は -y（USB 側を奥に持ってくる）
POCKET_ROT = Matrix(((0.0, SD, -CD), (-1.0, 0.0, 0.0), (0.0, CD, SD))).to_euler()

Y_RAIL = JOINT_RAIL + JOINT_GAP + RING_W / 2      # レールのリング位置
Z_POST = -(JOINT_POST + JOINT_GAP + RING_W / 2)   # 柱のリング位置


def hs(a, b, y=0.0):
    """(h, s, y) 座標をワールドへ。"""
    return (a * HV[0] + b * SV[0], y, a * HV[2] + b * SV[2])


def sp(s, h, t=0.0):
    """ポケット座標 (s, h, t) をワールドへ。"""
    p = hs(P_BACK + SHELL_TOTAL + h, s - SLOPE_LEN / 2)
    return (p[0], Y_PH - t, p[2])


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
    m.operation = op
    m.object = other
    m.solver = "EXACT"
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
pocket = mesh_from_loops(
    "pipe_corner45_pocket",
    [sp(s, h, -MOUNT_W / 2) for (s, h) in PROF],
    [sp(s, h, MOUNT_W / 2) for (s, h) in PROF])

slot_cut_len = SLOT_W + SLOT_ENTRY
cut(pocket, add_box("cut_slot", (SLOT_L, slot_cut_len, SLOT_T),
                    sp(STOPPER + slot_cut_len / 2, -(FRONT_SKIN + SLOT_T / 2)),
                    POCKET_ROT))

win_t = SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2
cut(pocket, add_box("cut_camwin", (CAM_WIN_L, WIN_S_LEN, 0.010),
                    sp(WIN_S_CENTER, -0.003, win_t), POCKET_ROT))

phi = math.atan2(TAPER_D, TAPER_LEN)
tp = sp(TAPER_S0, -FRONT_SKIN)
tdir = (SD * math.cos(phi) + CD * math.sin(phi), 0.0,
        CD * math.cos(phi) - SD * math.sin(phi))     # s を phi だけ h 側へ倒した向き
tn = (tdir[2], 0.0, -tdir[0])                        # その法線（h 側）
th = 0.030
taper_rot = Matrix(((0.0, tdir[0], -tn[0]), (-1.0, 0.0, 0.0),
                    (0.0, tdir[2], -tn[2]))).to_euler()
cut(pocket, add_box("cut_taper", (2 * MOUNT_W, 2 * th, TAPER_CUT),
                    (tp[0] + th * tdir[0] + (TAPER_CUT / 2) * tn[0], tp[1],
                     tp[2] + th * tdir[2] + (TAPER_CUT / 2) * tn[2]), taper_rot))

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
    p = sp(SLOPE_LEN - LATCH_S, -FRONT_SKIN + (r - LATCH_H), sx * LATCH_X)
    latches.append(add_cyl("pipe_corner45_latch_%d" % (sx > 0), r, LATCH_L, p,
                           (math.pi / 2, 0.0, 0.0), verts=24))

# =========================================================================
# 2) リング 2 個と帯
# =========================================================================
nut_r = NUT_AF / math.sqrt(3.0)
NUT_OVER = 0.0002
nut_depth = NUT_T + NUT_OVER
nut_h = CLAMP_GAP + EAR_T + NUT_OVER - nut_depth / 2
EAR_H1 = CLAMP_GAP + EAR_T

# レール用: 断面は (s, h) 平面、y 方向へ押し出す
prof_rail = clamp_profile(RING_R, BORE_D / 2, CLAMP_GAP, EAR_H1)
ring_rail = mesh_from_loops(
    "pipe_corner45_ring_rail",
    [hs(h, s, Y_RAIL - RING_W / 2) for (s, h) in prof_rail],
    [hs(h, s, Y_RAIL + RING_W / 2) for (s, h) in prof_rail])

# 柱用: 断面は (y, x) 平面、z 方向へ押し出す。C は +x 側（ポケットの側）に肉を残す
prof_post = clamp_profile(RING_R, BORE_D / 2 + POST_EXTRA, CLAMP_GAP, EAR_H1)
ring_post = mesh_from_loops(
    "pipe_corner45_ring_post",
    [(h, s, Z_POST - RING_W / 2) for (s, h) in prof_post],
    [(h, s, Z_POST + RING_W / 2) for (s, h) in prof_post])

straps = []
for tag, prof, lo, hi in (
        ("rail", clamp_profile(BORE_D / 2 + STRAP_ARC, BORE_D / 2, CLAMP_GAP, EAR_H1),
         lambda s, h: hs(-h, s, Y_RAIL - RING_W / 2),
         lambda s, h: hs(-h, s, Y_RAIL + RING_W / 2)),
        ("post", clamp_profile(BORE_D / 2 + STRAP_ARC, BORE_D / 2 + POST_EXTRA,
                               CLAMP_GAP, EAR_H1),
         lambda s, h: (-h, s, Z_POST - RING_W / 2),
         lambda s, h: (-h, s, Z_POST + RING_W / 2))):
    straps.append(mesh_from_loops("pipe_corner45_strap_%s" % tag,
                                  [lo(s, h) for (s, h) in prof],
                                  [hi(s, h) for (s, h) in prof]))

# ねじ穴・ナット座
for ring, strap, axis in ((ring_rail, straps[0], "rail"), (ring_post, straps[1], "post")):
    for sx in (1, -1):
        if axis == "rail":
            c0 = hs(0.0, sx * EAR_R, Y_RAIL)
            cn = hs(nut_h, sx * EAR_R, Y_RAIL)
            cs = hs(nut_h, sx * EAR_R, Y_RAIL + RING_W / 2)
            rot = (0.0, math.atan2(HV[0], -HV[2]), 0.0)
            slot = (RING_W, NUT_SLOT_W, nut_depth)
            slot_rot = Matrix(((SV[0], 0.0, HV[0]), (0.0, 1.0, 0.0),
                               (SV[2], 0.0, HV[2]))).to_euler()
            slot_size = (RING_W, NUT_SLOT_W, nut_depth)
            slot_rot = Matrix(((0.0, SV[0], HV[0]), (1.0, 0.0, 0.0),
                               (0.0, SV[2], HV[2]))).to_euler()
        else:
            c0 = (0.0, sx * EAR_R, Z_POST)
            cn = (nut_h, sx * EAR_R, Z_POST)
            cs = (nut_h, sx * EAR_R, Z_POST + RING_W / 2)
            rot = (0.0, math.pi / 2, 0.0)
            slot_size = (RING_W, NUT_SLOT_W, nut_depth)
            slot_rot = Matrix(((0.0, 0.0, 1.0), (0.0, 1.0, 0.0),
                               (-1.0, 0.0, 0.0))).to_euler()
        cut(ring, add_cyl("screw", SCREW_D / 2, 0.060, c0, rot))
        cut(strap, add_cyl("screw", SCREW_D / 2, 0.060, c0, rot))
        cut(ring, add_cyl("nut", nut_r, nut_depth, cn, rot, verts=6))
        cut(ring, add_box("nut_slot", slot_size, cs, slot_rot))

# =========================================================================
# 3) 板（リング → ポケット）
# =========================================================================
# レール側: s=0 の面に沿う板。リングの外周からポケット裏面まで
WEB_ROT = Matrix(((HV[0], 0.0, SV[0]), (0.0, 1.0, 0.0),
                  (HV[2], 0.0, SV[2]))).to_euler()
web_rail = add_box("pipe_corner45_web_rail",
                   (P_BACK + WEB_BITE - (RING_R - WEB_BITE), RING_W + 0.020, WEB_T),
                   hs((RING_R - WEB_BITE + P_BACK + WEB_BITE) / 2, 0.0, Y_RAIL),
                   WEB_ROT)

# 柱側: レール側と同じ向き（法線は s）の板。ポケットの下端ぎわに置くと、柱リングを
# 斜めに串刺しにして繋がる。y に垂直な板にすると、立てて刷ったとき 18cm2 の水平な
# オーバーハングになる（実測）。
S_WEB_POST = -SLOPE_LEN / 2 + 0.002
H_POST0 = 0.034
web_post = add_box("pipe_corner45_web_post",
                   (P_BACK + WEB_BITE - H_POST0, RING_W, WEB_T),
                   hs((H_POST0 + P_BACK + WEB_BITE) / 2, S_WEB_POST, 0.0),
                   WEB_ROT)

for sx in (1, -1):
    cut(web_rail, add_cyl("tether", TETHER_D / 2, WEB_T + 0.01,
                          hs((RING_R + P_BACK) / 2, 0.0, Y_RAIL + sx * 0.016),
                          Matrix(((HV[0], 0.0, SV[0]), (0.0, 1.0, 0.0),
                                  (HV[2], 0.0, SV[2]))).to_euler()))

# =========================================================================
# 4) パイプと継手の逃げ（全部品から彫る）
# =========================================================================
body = [pocket, web_rail, web_post, ring_rail, ring_post] + latches
LONG = 0.600
for part in body:
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
def joint_clear(p):
    dr = math.hypot(p[0], p[2]) - JOINT_R          # レール軸から
    dy = max(-p[1], p[1] - JOINT_RAIL)
    a = dr if dy <= 0 else math.hypot(dy, max(dr, 0.0))
    dr2 = math.hypot(p[0], p[1]) - JOINT_R         # 柱軸から
    dz = max(p[2], -JOINT_POST - p[2])
    b = dr2 if dz <= 0 else math.hypot(dz, max(dr2, 0.0))
    return min(a, b)


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
    pts = [mw @ v.co for v in o.data.vertices]
    jc = min(joint_clear(p) for p in pts)
    rail = min(math.hypot(p.x, p.z) for p in pts)
    post = min(math.hypot(p.x, p.y) for p in pts)
    print("part %-28s nm=%d verts=%4d 継手%+7.2f レール軸%6.2f 柱軸%6.2f"
          % (o.name, n, len(o.data.vertices), jc * 1000, rail * 1000, post * 1000))

worst = 1e9
for s in (STOPPER, STOPPER + PHONE_W):
    for h in (-(FRONT_SKIN + CLR_T / 2), -(FRONT_SKIN + CLR_T / 2 + PHONE_T)):
        for t in (-PHONE_L / 2, PHONE_L / 2):
            worst = min(worst, joint_clear(sp(s, h, t)))
print("---")
print("非多様体の合計: %d" % bad)
print("リング: レール y=%.1fmm / 柱 z=%.1fmm（継手は半径 %.1f、レール %.1f、柱 %.1f と仮定）"
      % (Y_RAIL * 1000, Z_POST * 1000, JOINT_R * 1000, JOINT_RAIL * 1000,
         JOINT_POST * 1000))
print("実機と継手のすきま: %+.2fmm%s"
      % (worst * 1000, "" if worst > 0 else "  ← P_BACK を増やすこと"))


def export_upright(name, parts):
    """ポケットの長辺（y）を立てた向き＝印刷の向きで書き出す。

    寝かせるとスロットの空洞の天井 153 x 74mm がまるごとオーバーハングになる。
    立てればスロットは縦のスリットになり、荷重も積層を剥がす向きに来ない。
    総当たりで測った結果、-y を上にする向きがいちばんサポートが少ない。
    """
    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    piv = bpy.context.object
    for o in parts:
        o.parent = piv
    piv.rotation_euler = (-math.pi / 2, 0.0, 0.0)
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


export_upright("pipe-corner45", body)
export_upright("pipe-corner45-strap", [straps[0]])
export_stl("pipe-corner45-asm")
