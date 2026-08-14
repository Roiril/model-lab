"""28mm パイプの端に付ける Pixel 7a ホルダー（カメラを斜め下 45° へ）。

パイプ端から差し込む筒にすると、つなぎ目の継手を跨げない。そこで割りリングで抱く。
リングは軸方向に 2 個並べ、それぞれ独立に M4×2 で締める。1 枚の帯で 2 個を同時に
締めると片当たりして、どちらか一方しか効かない。

座標系:
    x … パイプ軸。x=0 がパイプの端、+x が奥（継手から離れる向き）
    s … スロットを上る向き (0, cosA, sinA)。差し込み口は上
    h … カメラの視線 (0, sinA, -cosA)。パイプから見て外向き＋下向き
    A = TILT_DEG = 90 - 俯角

リングと耳は (s, h) 平面の輪郭を x 方向へ押し出して作る。円筒と箱をブーリアンで
足すと、割り面と耳の底面が同一平面になってメッシュが壊れる（実測: 非多様体 349 本）。

継手は「当たらない位置に置く」のではなく、継手が占める円柱を全部品から彫ってある。
実測して JOINT_LEN / JOINT_R を直せば、当たる部品は自動で削れる。

部品（重ね合わせた別々の閉じた立体として書き出す。スライサーは 1 つの実体として扱う）:
    pipe-phone45.stl       … 本体（ポケット＋背骨＋リング下半分＋耳）。パイプ軸を
                             立てた向きで書き出す。寝かせるとスロットの空洞の天井
                             153 x 74mm がまるごとオーバーハングになる
    pipe-phone45-strap.stl … 帯。同じものを 2 個刷る
    pipe-phone45-asm.stl   … 組んだ状態（確認用。印刷には使わない）

必要なもの: M4 ボルト 25mm 4 本、M4 ナット 4 個。ナットは耳の横穴へ差し込む。
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
UY, UZ = math.cos(A), math.sin(A)     # s 方向
NY, NZ = math.sin(A), -math.cos(A)    # h 方向
ROT = (A, 0.0, 0.0)
BIG = 0.4

S0 = SLOPE_LEN / 2                    # ポケットの中心を半径線に載せる
ORG_Y = (D_BACK + SHELL_TOTAL) * NY - S0 * UY
ORG_Z = -(D_BACK + SHELL_TOTAL) * math.cos(A) - S0 * UZ

X_RING1 = JOINT_LEN + JOINT_GAP + RING_W / 2
X_RING2 = X_RING1 + RING_DX
X_MID = (X_RING1 + X_RING2) / 2
X_SPINE0 = X_RING1 - RING_W / 2
X_SPINE1 = X_RING2 + RING_W / 2

EAR_S0 = EAR_R - EAR_W / 2
EAR_S1 = EAR_R + EAR_W / 2


def pipe_pos(x, sc, hc):
    """パイプ軸を原点とする (s, h) をワールドへ。"""
    return (x, sc * UY + hc * NY, sc * UZ + hc * NZ)


def sp(s, h, x=0.0):
    """ポケット座標 (s, h) をワールドへ。"""
    return (x, ORG_Y + s * UY + h * NY, ORG_Z + s * UZ + h * NZ)


def add_box(name, size, loc, rot=ROT):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return o


def add_cyl(name, r, depth, loc, rot=ROT, verts=48):
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


def join(t, o):
    _apply(t, o, "UNION")


def extrude_sh(name, pts, x0, x1):
    """(s, h) 平面の多角形を x 方向へ押し出して閉じた立体にする。"""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    lo = [bm.verts.new(pipe_pos(x0, s, h)) for (s, h) in pts]
    hi = [bm.verts.new(pipe_pos(x1, s, h)) for (s, h) in pts]
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


def arc(r, a0, a1, n=48):
    """半径 r の円弧を (s, h) で返す。角度は s 軸から測る。"""
    return [(r * math.cos(a0 + (a1 - a0) * i / n),
             r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def clamp_profile(r_out, hc, ear_h1):
    """割りリングの片側（h >= hc）＋両側の耳。(s, h) の閉じた輪郭。"""
    ri = BORE_D / 2
    si_in = math.sqrt(max(ri * ri - hc * hc, 0.0))       # 内円が割り面と交わる s
    a_in = math.atan2(hc, si_in)
    h_arc = math.sqrt(max(r_out * r_out - EAR_S0 ** 2, 0.0))  # 外円が耳の内側と交わる h
    a_ear = math.atan2(h_arc, EAR_S0)
    pts = [(si_in, hc), (EAR_S1, hc), (EAR_S1, ear_h1), (EAR_S0, ear_h1)]
    pts += arc(r_out, a_ear, math.pi - a_ear)
    pts += [(-EAR_S0, ear_h1), (-EAR_S1, ear_h1), (-EAR_S1, hc), (-si_in, hc)]
    pts += arc(ri, math.pi - a_in, a_in)
    return pts


# =========================================================================
# 1) ポケット（壁掛け版と同じ断面。パイプ軸方向へ押し出す）
# =========================================================================
POCKET = [(0.0, 0.0), (SLOPE_LEN, 0.0), (SLOPE_LEN, -SHELL_TOTAL), (0.0, -SHELL_TOTAL)]
me = bpy.data.meshes.new("pocket")
_bm = bmesh.new()
_lo = [_bm.verts.new(sp(s, h, X_MID - MOUNT_W / 2)) for (s, h) in POCKET]
_hi = [_bm.verts.new(sp(s, h, X_MID + MOUNT_W / 2)) for (s, h) in POCKET]
_bm.faces.new(_lo)
_bm.faces.new(_hi[::-1])
for i in range(4):
    j = (i + 1) % 4
    _bm.faces.new([_lo[i], _hi[i], _hi[j], _lo[j]])
bmesh.ops.recalc_face_normals(_bm, faces=_bm.faces)
_bm.to_mesh(me)
_bm.free()
pocket = bpy.data.objects.new("pipe_phone45_pocket", me)
bpy.context.collection.objects.link(pocket)

slot_cut_len = SLOT_W + SLOT_ENTRY
cut(pocket, add_box("cut_slot", (SLOT_L, slot_cut_len, SLOT_T),
                    sp(STOPPER + slot_cut_len / 2,
                       -(FRONT_SKIN + SLOT_T / 2), X_MID)))

win_x = SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2
cut(pocket, add_box("cut_camwin", (CAM_WIN_L, WIN_S_LEN, 0.010),
                    sp(WIN_S_CENTER, -0.003, X_MID + win_x)))

phi = math.atan2(TAPER_D, TAPER_LEN)
ta = A - phi
tp = sp(TAPER_S0, -FRONT_SKIN, X_MID)
th = 0.030
cut(pocket, add_box("cut_taper", (2 * MOUNT_W, 2 * th, TAPER_CUT),
                    (X_MID,
                     tp[1] + th * math.cos(ta) - (TAPER_CUT / 2) * math.sin(ta),
                     tp[2] + th * math.sin(ta) + (TAPER_CUT / 2) * math.cos(ta)),
                    (ta, 0.0, 0.0)))

grip_len = 0.040
cut(pocket, add_box("cut_grip", (GRIP_W, grip_len, 0.020),
                    sp(GRIP_S0 + grip_len / 2, -0.006, X_MID)))

usb_x0 = -(MOUNT_W / 2 + 0.005)
usb_x1 = -(SLOT_L / 2 - USB_INTO)
cut(pocket, add_box("cut_usb", (usb_x1 - usb_x0, USB_W, USB_T),
                    sp(USB_S, -SHELL_TOTAL / 2, X_MID + (usb_x0 + usb_x1) / 2)))

# --- 抜け止めの山（外皮の内面から丸棒を出す。軸は肉の中へ沈めて接線を避ける） ---
latches = []
for sx in (1, -1):
    r = LATCH_H * 1.8
    latches.append(add_cyl("pipe_phone45_latch_%d" % (sx > 0), r, LATCH_L,
                           sp(SLOPE_LEN - LATCH_S, -FRONT_SKIN + (r - LATCH_H),
                              X_MID + sx * LATCH_X),
                           (0.0, math.pi / 2, 0.0), verts=24))

# =========================================================================
# 2) 背骨（リングとポケット裏面を渡す板）
# =========================================================================
h0 = RING_R - SPINE_BITE
h1 = D_BACK + SPINE_BITE
# 背骨はポケットの全長に渡す。リングの間だけにすると、立てて刷ったとき背骨の下端が
# 宙に浮いてサポートが要る。伸ばせばポケットと同じ高さから始まり、ポケットの反りも止まる。
spine = add_box("pipe_phone45_spine", (MOUNT_W, SPINE_T, h1 - h0),
                pipe_pos(X_MID, 0.0, (h0 + h1) / 2))
for sx in (1, -1):
    cut(spine, add_cyl("tether", TETHER_D / 2, SPINE_T + 0.01,
                       pipe_pos(X_MID + sx * 0.030, 0.0, (h0 + h1) / 2),
                       (A + math.pi / 2, 0.0, 0.0)))

# =========================================================================
# 3) 割りリング（本体側）と帯
# =========================================================================
nut_r = NUT_AF / math.sqrt(3.0)
# ナット座は耳の上面へ 0.2mm 突き抜けさせる。面一で止めるとカッターと耳の上面が
# 同一平面になり、ブーリアンがメッシュを壊す（実測: 非多様体 114 本）。
NUT_OVER = 0.0002
nut_depth = NUT_T + NUT_OVER
nut_h = CLAMP_GAP + EAR_T + NUT_OVER - nut_depth / 2
rings, straps = [], []
for i, xr in enumerate((X_RING1, X_RING2)):
    ring = extrude_sh("pipe_phone45_ring_%d" % i,
                      clamp_profile(RING_R, CLAMP_GAP, CLAMP_GAP + EAR_T),
                      xr - RING_W / 2, xr + RING_W / 2)
    for sx in (1, -1):
        cut(ring, add_cyl("screw", SCREW_D / 2, 0.060,
                          pipe_pos(xr, sx * EAR_R, 0.0)))
        # ナットは耳の外端に、パイプ軸方向から差し込む（締めるとき回り止めが要らない）
        cut(ring, add_cyl("nut", nut_r, nut_depth,
                          pipe_pos(xr, sx * EAR_R, nut_h), verts=6))
        cut(ring, add_box("nut_slot", (RING_W, NUT_SLOT_W, nut_depth),
                          pipe_pos(xr + RING_W / 2, sx * EAR_R, nut_h)))
    rings.append(ring)

    # 帯は h を反転した同じ輪郭。外半径だけ薄くして先に馴染ませる。
    prof = [(s, -h) for (s, h) in
            clamp_profile(BORE_D / 2 + STRAP_ARC, CLAMP_GAP, CLAMP_GAP + EAR_T)]
    strap = extrude_sh("pipe_phone45_strap_%d" % i, prof,
                       xr - RING_W / 2, xr + RING_W / 2)
    for sx in (1, -1):
        cut(strap, add_cyl("screw", SCREW_D / 2, 0.060,
                           pipe_pos(xr, sx * EAR_R, 0.0)))
    straps.append(strap)

# =========================================================================
# 4) 継手の逃げ（継手の外形＋すきまを、全部品から丸ごと彫る）
# =========================================================================
# 位置決めで気をつけるのではなく、継手が占める円柱を差し引く。継手を実測して
# JOINT_LEN / JOINT_R を直せば、当たる部品は自動で削れる。
X_CLEAR = JOINT_LEN + JOINT_GAP
joint_env_len = X_CLEAR + 0.200
for part in [pocket, spine] + rings:
    cut(part, add_cyl("joint_env", JOINT_R + JOINT_GAP, joint_env_len,
                      (X_CLEAR - joint_env_len / 2, 0.0, 0.0),
                      (0.0, math.pi / 2, 0.0), verts=64))


# =========================================================================
# 5) 検証
# =========================================================================
def report(o):
    b = bmesh.new()
    b.from_mesh(o.data)
    bmesh.ops.dissolve_degenerate(b, dist=1e-6, edges=b.edges[:])
    n = sum(1 for e in b.edges if not e.is_manifold)
    b.to_mesh(o.data)
    b.free()
    mw = o.matrix_world
    pts = [mw @ v.co for v in o.data.vertices]
    clr, worst = 1e9, None
    for p in pts:
        r = math.hypot(p.y, p.z)
        dx = max(-p.x, p.x - JOINT_LEN)
        d = (r - JOINT_R) if dx <= 0 else math.hypot(dx, max(r - JOINT_R, 0.0))
        if d < clr:
            clr, worst = d, p
    bore = min(math.hypot(p.y, p.z) for p in pts)
    print("part %-26s nm=%d verts=%4d  継手すきま=%+7.2fmm @x=%6.1f  軸から最小=%6.2fmm"
          % (o.name, n, len(o.data.vertices), clr * 1000, worst.x * 1000, bore * 1000))
    return n


bad = 0
for o in list(bpy.data.objects):
    if o.type == "MESH":
        bad += report(o)
print("---")
print("非多様体の合計: %d" % bad)
print("リング x = %.1f / %.1f mm（継手は x = 0..%.1fmm、半径 %.1fmm と仮定）"
      % (X_RING1 * 1000, X_RING2 * 1000, JOINT_LEN * 1000, JOINT_R * 1000))
print("ポケット x = %.1f .. %.1f mm / 俯角 %.0f° / パイプ軸からポケット裏面 %.1fmm"
      % ((X_MID - MOUNT_W / 2) * 1000, (X_MID + MOUNT_W / 2) * 1000,
         CAM_DEPRESSION, D_BACK * 1000))

# 継手の逃げは部品を自動で削る。削りすぎてスロットや実機に届いていないかを見る。
worst = 1e9
for s in (STOPPER, STOPPER + PHONE_W):
    for h in (-(FRONT_SKIN + CLR_T / 2), -(FRONT_SKIN + CLR_T / 2 + PHONE_T)):
        for x in (X_MID - PHONE_L / 2, X_MID + PHONE_L / 2):
            p = sp(s, h, x)
            r = math.hypot(p[1], p[2])
            dx = max(-p[0], p[0] - JOINT_LEN)
            worst = min(worst, (r - JOINT_R) if dx <= 0
                        else math.hypot(dx, max(r - JOINT_R, 0.0)))
print("実機と継手のすきま: %+.2fmm%s"
      % (worst * 1000, "" if worst > 0 else "  ← 継手が大きすぎる。D_BACK を増やすこと"))

body_parts = [pocket, spine] + rings + latches


def export_upright(name, parts):
    """パイプ軸を立てた向き（＝印刷の向き）にして書き出す。

    寝かせるとスロットの空洞の天井（153 x 74mm）がまるごと水平のオーバーハングに
    なる。立てればスロットは縦のスリットになり、荷重も積層を剥がす向きに来ない。
    """
    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    piv = bpy.context.object
    for o in parts:
        o.parent = piv
    piv.rotation_euler = (0.0, -math.pi / 2, 0.0)
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
        o.matrix_world = o.matrix_world
    bpy.data.objects.remove(piv, do_unlink=True)


export_upright("pipe-phone45", body_parts)
export_upright("pipe-phone45-strap", [straps[0]])
export_stl("pipe-phone45-asm")
