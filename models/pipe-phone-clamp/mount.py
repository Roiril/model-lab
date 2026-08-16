# Φ28 パイプ用 Pixel 7a ホルダーの形（bpy）。単位: m
#
# 生成は 2 つの座標系（params.py 参照）でだけ行い、ワールドへは行列 1 個で持っていく。
# ワールドで直に組むと 45°×45° の二重回転が全ての数値に混ざり、どこが間違っているのか
# 分からなくなる。腕だけが 2 つの座標系をまたぐので、腕は K で伸ばして C の平面で切る。
import math

import bpy
import bmesh
from mathutils import Vector, Matrix

import params as P


# =========================================================================
# 下ごしらえ
# =========================================================================
def _obj(name, bm, coll):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def _bake(ob):
    """モディファイアを焼く。bpy.ops を使わないのでコンテキストに依存しない。"""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    bpy.data.meshes.remove(old)


def _csg(target, cutter, op="DIFFERENCE"):
    m = target.modifiers.new("b", "BOOLEAN")
    m.operation = op
    m.solver = "EXACT"
    m.object = cutter
    _bake(target)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def _box(name, frame, center, size, coll):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.transform(frame @ Matrix.Translation(Vector(center)))
    return _obj(name, bm, coll)


_AXIS_ROT = {
    "Z": Matrix.Identity(4),
    "X": Matrix.Rotation(math.pi / 2, 4, "Y"),
    "Y": Matrix.Rotation(-math.pi / 2, 4, "X"),
}


def _prism(name, frame, center, r, depth, axis, coll, seg=64):
    bm = bmesh.new()
    kw = dict(cap_ends=True, cap_tris=False, segments=seg, depth=depth)
    try:
        bmesh.ops.create_cone(bm, radius1=r, radius2=r, **kw)
    except TypeError:                       # 3.x 系は名前が diameter だが中身は半径
        bmesh.ops.create_cone(bm, diameter1=r, diameter2=r, **kw)
    bm.transform(frame @ Matrix.Translation(Vector(center)) @ _AXIS_ROT[axis])
    return _obj(name, bm, coll)


def _cyl(name, frame, center, r, depth, axis, coll):
    return _prism(name, frame, center, r, depth, axis, coll, seg=64)


def _hex(name, frame, center, af, depth, axis, coll):
    return _prism(name, frame, center, af * 0.5 / math.cos(math.pi / 6), depth, axis, coll, seg=6)


def _bevel(ob, width, segments=2, angle_deg=40.0):
    m = ob.modifiers.new("bev", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(angle_deg)
    _bake(ob)


# =========================================================================
# 座標系
# =========================================================================
def frames(phone_center, euler_deg, pipe_point, pipe_dir):
    """C（ポケット）・K（クランプ）の 4x4 と腕の長さを返す。

    K の原点はパイプ軸上で、パッドの合わせ面の中心にいちばん近い点。こう取ると
    腕がパイプと直角になり、印刷したとき腕が造形板と平行に伸びる。
    """
    rot = (Matrix.Rotation(math.radians(euler_deg[2]), 4, "Z")
           @ Matrix.Rotation(math.radians(euler_deg[1]), 4, "Y")
           @ Matrix.Rotation(math.radians(euler_deg[0]), 4, "X"))
    mx = (rot @ Vector((1, 0, 0))).normalized()   # カメラの視線（前）
    my = (rot @ Vector((0, 1, 0))).normalized()   # スマホの長辺
    mz = (rot @ Vector((0, 0, 1))).normalized()   # スロットを上る向き
    o = Vector(phone_center)
    C = Matrix(((mx.x, my.x, mz.x, o.x),
                (mx.y, my.y, mz.y, o.y),
                (mx.z, my.z, mz.z, o.z),
                (0.0, 0.0, 0.0, 1.0)))

    pad_c = C @ Vector((P.X_BACK - P.BOSS_T, 0.0, 0.0))    # 合わせ面の中心
    p0 = Vector(pipe_point)
    d = Vector(pipe_dir).normalized()
    axis_pt = p0 + d * (pad_c - p0).dot(d)
    kx = (pad_c - axis_pt).normalized()
    kz = d
    ky = kz.cross(kx)
    K = Matrix(((kx.x, ky.x, kz.x, axis_pt.x),
                (kx.y, ky.y, kz.y, axis_pt.y),
                (kx.z, ky.z, kz.z, axis_pt.z),
                (0.0, 0.0, 0.0, 1.0)))
    return C, K, (pad_c - axis_pt).length


# =========================================================================
# 部品
# =========================================================================
# =========================================================================
# 角のジョイントを兼ねる本体（レールと柱を 1 つの部品で掴む）
# =========================================================================
def _roof(name, frame, r, length, sign, coll):
    """ボアの天井を 45° の切妻に落とすカッター。

    分割面を造形板へ伏せると、半円の樋の天井（頂点まわり ±45°）だけが宙に浮く。
    そこを切妻に落とすと支持材が要らなくなる。パイプは残った 4 本の帯（±45°/±135°）
    で挟まれるので、掴む力はむしろ V ブロックに近くなって位置も決まる。
    """
    k = r * 0.70710678
    tri = [(sign * k, +k), (sign * k, -k), (sign * r * 1.41421356, 0.0)]
    bm = bmesh.new()
    h = length / 2
    vs = [(bm.verts.new((x, y, -h)), bm.verts.new((x, y, +h))) for (x, y) in tri]
    bm.faces.new([vs[0][0], vs[1][0], vs[2][0]])
    bm.faces.new([vs[0][1], vs[1][1], vs[2][1]])
    for i in range(3):
        a, b = vs[i], vs[(i + 1) % 3]
        bm.faces.new([a[0], b[0], b[1], a[1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.transform(frame)
    return _obj(name, bm, coll)


def corner_frames(fC):
    """レール側 fR と柱側 fQ。frame-z はそのパイプの軸、frame-x は「印刷したときの
    真上」をその軸と直角な面へ射影した向き（＝ボアの切妻を向ける向き）。"""
    up = (fC.to_3x3() @ Vector((0, 0, 1))).normalized()      # 印刷時の上 = Mz

    def mk(o, axis):
        z = Vector(axis).normalized()
        x = (up - z * up.dot(z)).normalized()
        y = z.cross(x)
        return Matrix(((x.x, y.x, z.x, o[0]),
                       (x.y, y.y, z.y, o[1]),
                       (x.z, y.z, z.z, o[2]),
                       (0.0, 0.0, 0.0, 1.0)))
    return (mk((P.CORNER_X, P.RAIL_RING_Y, P.RAIL_Z), (0, 1, 0)),
            mk((P.CORNER_X, P.CORNER_Y, P.POST_RING_Z), (0, 0, 1)))


def _arm_frame(a, b):
    """a→b を x 軸に持つ座標系（z はできるだけ世界の上を向ける）。"""
    ux = (b - a).normalized()
    uz = (Vector((0, 0, 1)) - ux * ux.z).normalized()
    uy = uz.cross(ux)
    m = (a + b) / 2
    return Matrix(((ux.x, uy.x, uz.x, m.x),
                   (ux.y, uy.y, uz.y, m.y),
                   (ux.z, uy.z, uz.z, m.z),
                   (0.0, 0.0, 0.0, 1.0))), (b - a).length


def _tri_z(name, frame, tri_xy, length, coll):
    """frame の x-y 平面に置いた三角形を、z 方向へ length 押し出した角柱。"""
    bm = bmesh.new()
    h = length / 2
    vs = [(bm.verts.new((x, y, -h)), bm.verts.new((x, y, +h))) for (x, y) in tri_xy]
    bm.faces.new([vs[0][0], vs[1][0], vs[2][0]])
    bm.faces.new([vs[0][1], vs[1][1], vs[2][1]])
    for i in range(3):
        a, b = vs[i], vs[(i + 1) % 3]
        bm.faces.new([a[0], b[0], b[1], a[1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.transform(frame)
    return _obj(name, bm, coll)


def build_one(coll, fR, fQ, fC, name="M_mount"):
    """全部 1 部品。閉じたリング 2 個 + 角の肉 + 腕 + ポケット。ねじは使わない。

    リングは口を開けない（差し込みで組む）ので、撓ませる必要が無く肉を厚く取れる。
    ボアの天井だけ 45 度の切妻に落としてあるので、深い筒の中に支持材が入らない。
    """
    r_out = P.CLIP_BORE_R + P.CLIP_WALL
    body = _cyl(name, fR, (0, 0, 0), r_out, P.CLIP_W, "Z", coll)
    _csg(body, _cyl("_c2", fQ, (0, 0, 0), r_out, P.CLIP_W, "Z", coll), "UNION")

    I = Matrix.Identity(4)
    _csg(body, _box("_web", I, (P.CORNER_X, (P.WEB_Y0 + P.WEB_Y1) / 2,
                                (P.WEB_Z0 + P.WEB_Z1) / 2),
                    (2 * r_out, P.WEB_Y1 - P.WEB_Y0, P.WEB_Z1 - P.WEB_Z0), coll), "UNION")

    # 腕。ポケットの背中のボスの中まで差し込んで一体にする
    tip = fC @ Vector((P.X_BACK - P.BOSS_T / 2, 0.0, 0.0))
    root = Vector((P.CORNER_X, (P.WEB_Y0 + P.WEB_Y1) / 2, (P.WEB_Z0 + P.WEB_Z1) / 2))
    fA, alen = _arm_frame(root, tip)
    _csg(body, _box("_arm", fA, (0, 0, 0), (alen, P.ARM_W, P.ARM_H), coll), "UNION")

    _csg(body, build_cradle(coll, fC, bolts=False, name="_pocket"), "UNION")

    # 腕はボス（10mm）より厚いので、そのままだとスロットへ 3.7cm3 はみ出す。
    # union のあとでスロットだけ引き直して、中を空にする
    cut_len = P.SLOT_W + P.SLOT_ENTRY
    _csg(body, _box("_reslot", fC, (0, 0, P.STOPPER + cut_len / 2 - P.S_MID),
                    (P.SLOT_T, P.SLOT_L, cut_len), coll))

    for f in (fR, fQ):                              # ボアと、その天井の切妻
        _csg(body, _cyl("_bore", f, (0, 0, 0), P.CLIP_BORE_R, 0.300, "Z", coll))
        _csg(body, _roof("_roof", f, P.CLIP_BORE_R, 0.300, +1, coll))
    return body


def build_cradle(coll, fC, brace=False, bolts=True, name="M_cradle"):
    """スマホのポケット。前は枠。差し込み口は +z。"""
    xc = (P.X_BACK + P.X_FRONT) / 2
    zc = (P.Z_BOT + P.Z_TOP) / 2
    body = _box(name, fC, (xc, 0, zc),
                (P.X_FRONT - P.X_BACK, P.SHELL_Y, P.Z_TOP - P.Z_BOT), coll)
    # ボスは殻へ 1mm 食い込ませる。面一で突き当てると合わせ面が内部の壁として残る。
    # 下端は殻の底より 0.5mm 上で止める。底を面一に揃えると、その合わせ目が
    # union の縫い目として残る（実測 158 本の非多様体エッジ）。
    bz0 = P.Z_BOT + 0.0005
    _csg(body, _box("_boss", fC, (P.X_BACK - P.BOSS_T / 2 + 0.0005, 0, (bz0 + P.BOSS_Z_TOP) / 2),
                    (P.BOSS_T + 0.001, P.BOSS_Y, P.BOSS_Z_TOP - bz0), coll), "UNION")

    # --- ここから差し込み側。models/pixel7a-stand と同じ形・同じ寸法 ------------
    def z_of(s):                                   # 斜面座標 s → C-z
        return s - P.S_MID

    cut_len = P.SLOT_W + P.SLOT_ENTRY              # スロット（上へ抜く）
    _csg(body, _box("_slot", fC, (0, 0, z_of(P.STOPPER + cut_len / 2)),
                    (P.SLOT_T, P.SLOT_L, cut_len), coll))

    win_y = P.SLOT_L / 2 - P.CAM_EDGE_RIM - P.CAM_WIN_L / 2   # カメラ窓
    _csg(body, _box("_camwin", fC,
                    (P.X_FRONT - 0.003, win_y, z_of((P.WIN_S_MIN + P.WIN_S_MAX) / 2)),
                    (0.010, P.CAM_WIN_L, P.WIN_S_MAX - P.WIN_S_MIN), coll))

    # 差し込み口のテーパー。斜面より phi だけ立てた面を引き、その内側 TAPER_D を抜く
    phi = math.atan2(P.TAPER_D, P.TAPER_LEN)
    # 起点をスロット側へ 0.2mm 逃がし、その分だけ斜面を手前から始める。面がスロットの
    # 面と接したままだと、USB の切り欠きと交わる所に三角形が 1 枚残る（実測 3 本）。
    back = 0.0002
    ft = (fC @ Matrix.Translation((P.SLOT_T / 2 - back, 0.0,
                                   z_of(P.TAPER_S0 - back / math.tan(phi))))
          @ Matrix.Rotation(phi, 4, "Y"))
    # 厚みは TAPER_D ではなく 8mm 取る。TAPER_D ぴったりだと、下面がスロットの面を
    # 浅い角度で横切って薄片ができる。余分はスロットの空洞なので形は変わらない。
    _csg(body, _box("_taper", ft, (-0.004, 0, 0.030),
                    (0.008, 2 * P.SHELL_Y, 0.060), coll))

    glen = 0.040                                   # 指がかり（外皮と裏板を落とす）
    _csg(body, _box("_grip", fC, (P.X_FRONT - 0.006, 0, z_of(P.GRIP_S0 + glen / 2)),
                    (0.020, P.GRIP_W, glen), coll))

    # USB-C / スピーカーの逃げ。スマホ下端は長辺の端に来るので、側壁を切り欠く。
    # 外皮側の面はスロットの面より 0.5mm 手前で止める（面一にすると縫い目が残る）
    ux0, ux1 = P.X_FRONT - 0.0145, P.SLOT_T / 2 - 0.0005
    _csg(body, _box("_usb", fC, ((ux0 + ux1) / 2,
                                 -(P.SHELL_Y / 2 - P.SIDE_WALL), z_of(P.USB_S)),
                    (ux1 - ux0, 0.020, P.USB_W), coll))

    _csg(body, _cyl("_teth", fC, (P.X_BACK - P.BOSS_T / 2, 0, 0.0130),
                    P.TETHER_R, P.BOSS_Y + 0.020, "Y", coll))

    # ボルト穴・ナット座・ナットを差し込む溝。この 3 つはどの面も他と一致させない。
    # 一致させると切る材料の無い boolean になり、殻の裏に三角形が 1 枚残る。
    holes = [(+1, P.PAD_BOLT_Y, 0.0), (-1, -P.PAD_BOLT_Y, 0.0)] if bolts else []
    if brace:                                      # つっかえ棒をボス面へ留める 3 本目
        holes.append((+1, 0.0, P.STRUT_BOSS_Z))
    for s, y, zh in holes:
        # 止まり穴にする。裏板まで抜くと、長いねじがスロットへ顔を出してスマホに当たる。
        # 穴はナット座より 1.8mm 深い。ここが浅いと M4×16 が底を突いて締まらない。
        # 裏板は残り 1.7mm。
        x_hole = P.X_BACK + 0.0013
        x_out = P.X_BACK - P.BOSS_T - 0.002
        _csg(body, _cyl("_cb_h", fC, ((x_hole + x_out) / 2, y, zh),
                        P.BOLT_R, x_hole - x_out, "X", coll))
        nut0, nut1 = P.X_BACK - 0.0005 - P.NUT_T - 0.0004, P.X_BACK - 0.0005
        _csg(body, _hex("_cnut", fC, ((nut0 + nut1) / 2, y, zh),
                        P.NUT_AF, nut1 - nut0, "X", coll))
        # 溝はナット座より 0.2mm 深く・0.6mm 浅く終え、幅は六角の二面幅より 0.4mm 広い。
        # y はナットの座に少しだけ食い込ませる（座の内側 6mm が残るので回り止めは効く）
        sl0, sl1 = nut0 - 0.0002, nut1 - 0.0006
        y0, y1 = y + s * 0.002, s * (P.BOSS_Y / 2 + 0.010)
        _csg(body, _box("_cslot", fC, ((sl0 + sl1) / 2, (y0 + y1) / 2, zh),
                        (sl1 - sl0, abs(y1 - y0), P.NUT_AF + 0.0004), coll))

    if P.BEVEL > 0:
        _bevel(body, P.BEVEL)
    return body


# =========================================================================
# 検査
# =========================================================================
def _shells(bm):
    """面のつながりで殻を数える。2 以上なら内部に壁か浮いた塊がある。

    浮動小数に一切依存しない（世界座標 1m 付近では光線の内外判定が当てにならない）。
    """
    bm.faces.ensure_lookup_table()
    seen = set()
    n = 0
    for f in bm.faces:
        if f.index in seen:
            continue
        n += 1
        stack = [f]
        seen.add(f.index)
        while stack:
            for e in stack.pop().edges:
                for lf in e.link_faces:
                    if lf.index not in seen:
                        seen.add(lf.index)
                        stack.append(lf)
    return n


def stats(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    vol = bm.calc_volume(signed=True)
    nonmani = sum(1 for e in bm.edges if not e.is_manifold)
    loose = sum(1 for v in bm.verts if not v.link_edges)
    shells = _shells(bm)
    bm.free()
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
    mx = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
    return dict(name=ob.name, vol_cm3=vol * 1e6, nonmani=nonmani, loose=loose, shells=shells,
                dim_mm=tuple(round((mx - mn)[i] * 1000, 1) for i in range(3)),
                min_mm=tuple(round(mn[i] * 1000, 1) for i in range(3)),
                max_mm=tuple(round(mx[i] * 1000, 1) for i in range(3)))
