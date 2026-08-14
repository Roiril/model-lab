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
def build_saddle(coll, fK, fC, arm_len, name="M_saddle"):
    """パイプを抱く半分 + 腕 + パッド。合わせ面より先（ポケット側）は落とす。"""
    half = P.SPLIT_GAP / 2
    x_mate = P.X_BACK - P.BOSS_T                 # C 座標での合わせ面
    body = _cyl(name, fK, (0, 0, 0), P.RING_R, P.RING_W, "Z", coll)

    for s in (+1, -1):                            # 耳
        yc = s * (P.EAR_Y0 + P.EAR_Y1) / 2
        _csg(body, _box("_ear", fK, (P.EAR_T / 2, yc, 0),
                        (P.EAR_T, P.EAR_Y1 - P.EAR_Y0, P.RING_W), coll), "UNION")

    over = 0.020                                  # 合わせ面が斜めなので長めに出して切る
    _csg(body, _box("_arm", fK, ((arm_len + over) / 2, 0, 0),
                    (arm_len + over, P.ARM_H, P.ARM_W), coll), "UNION")
    # パッドは合わせ面より 0.5mm 出しておいて、あとで面で切る。面一で置くと切る材料が
    # 無い退化した boolean になる。
    _csg(body, _box("_pad", fC, (x_mate - P.PAD_T / 2 + 0.00025, 0, 0),
                    (P.PAD_T + 0.0005, P.PAD_Y, P.PAD_Z), coll), "UNION")
    _csg(body, _box("_mate", fC, (x_mate + 0.100, 0, 0), (0.200, 0.400, 0.400), coll))

    _csg(body, _cyl("_bore", fK, (0, 0, 0), P.BORE_R, P.RING_W + 0.020, "Z", coll))
    _csg(body, _box("_split", fK, (half - 0.100, 0, 0), (0.200, 0.400, 0.400), coll))

    for s in (+1, -1):                            # 耳のボルト穴とナット座
        _csg(body, _cyl("_bh", fK, (0, s * P.BOLT_Y, 0), P.BOLT_R, 0.060, "X", coll))
        _csg(body, _hex("_nut", fK, (P.EAR_T - P.NUT_T / 2 + 0.0004, s * P.BOLT_Y, 0),
                        P.NUT_AF, P.NUT_T + 0.0008, "X", coll))

    for s in (+1, -1):                            # パッドのボルト穴と座ぐり
        _csg(body, _cyl("_pb", fC, (x_mate - P.PAD_T / 2, s * P.PAD_BOLT_Y, 0),
                        P.BOLT_R, 0.060, "X", coll))
        _csg(body, _cyl("_pcb", fC, (x_mate - P.PAD_T - 0.0005 + P.CB_D / 2,
                                     s * P.PAD_BOLT_Y, 0),
                        P.CB_R, P.CB_D + 0.001, "X", coll))
    return body


def build_strap(coll, fK, name="M_strap"):
    """反対側の半分。頭は座ぐりへ落とす。"""
    half = P.SPLIT_GAP / 2
    body = _cyl(name, fK, (0, 0, 0), P.RING_R, P.RING_W, "Z", coll)
    for s in (+1, -1):
        yc = s * (P.EAR_Y0 + P.EAR_Y1) / 2
        _csg(body, _box("_ear", fK, (-P.EAR_T / 2, yc, 0),
                        (P.EAR_T, P.EAR_Y1 - P.EAR_Y0, P.RING_W), coll), "UNION")
    _csg(body, _cyl("_bore", fK, (0, 0, 0), P.BORE_R, P.RING_W + 0.020, "Z", coll))
    _csg(body, _box("_split", fK, (0.100 - half, 0, 0), (0.200, 0.400, 0.400), coll))
    for s in (+1, -1):
        _csg(body, _cyl("_bh", fK, (0, s * P.BOLT_Y, 0), P.BOLT_R, 0.060, "X", coll))
        _csg(body, _cyl("_cb", fK, (-P.EAR_T - 0.0005 + P.CB_D / 2, s * P.BOLT_Y, 0),
                        P.CB_R, P.CB_D + 0.001, "X", coll))
    return body


def build_cradle(coll, fC, name="M_cradle"):
    """スマホのポケット。前は枠。差し込み口は +z。"""
    xc = (P.X_BACK + P.X_FRONT) / 2
    zc = (P.Z_BOT + P.Z_TOP) / 2
    body = _box(name, fC, (xc, 0, zc),
                (P.X_FRONT - P.X_BACK, P.SHELL_Y, P.Z_TOP - P.Z_BOT), coll)
    # ボスは殻へ 1mm 食い込ませる。面一で突き当てると合わせ面が内部の壁として残る。
    _csg(body, _box("_boss", fC, (P.X_BACK - P.BOSS_T / 2 + 0.0005, 0, 0),
                    (P.BOSS_T + 0.001, P.BOSS_Y, P.BOSS_Z), coll), "UNION")

    top = P.Z_TOP + 0.060                          # スロットは上へ抜く
    z0 = -P.SLOT_W / 2
    _csg(body, _box("_slot", fC, (0, 0, (z0 + top) / 2),
                    (P.SLOT_T, P.SLOT_L, top - z0), coll))

    wz0 = z0 + P.BORDER                            # 前の窓（上端は開けたまま）
    _csg(body, _box("_win", fC, (P.X_FRONT, 0, (wz0 + top) / 2),
                    (0.020, P.SLOT_L - 2 * P.BORDER, top - wz0), coll))

    ubot = P.Z_BOT - 0.005                         # 底の USB 切り欠き
    utop = z0 + 0.0005                             # スロットの床と面一にしない
    _csg(body, _box("_usb", fC, (0, 0, (ubot + utop) / 2), (0.040, P.USB_W, utop - ubot), coll))

    _csg(body, _cyl("_teth", fC, (P.X_BACK - P.BOSS_T / 2, 0, 0.0130),
                    P.TETHER_R, P.BOSS_Y + 0.020, "Y", coll))

    # ボルト穴・ナット座・ナットを差し込む溝。この 3 つはどの面も他と一致させない。
    # 一致させると切る材料の無い boolean になり、殻の裏に三角形が 1 枚残る。
    for s in (+1, -1):
        y = s * P.PAD_BOLT_Y
        # 止まり穴にする。裏板まで抜くと、長いねじがスロットへ顔を出してスマホに当たる。
        # 穴はナット座より 1.8mm 深い。ここが浅いと M4×16 が底を突いて締まらない。
        # 裏板は残り 1.7mm。
        x_hole = P.X_BACK + 0.0013
        x_out = P.X_BACK - P.BOSS_T - 0.002
        _csg(body, _cyl("_cb_h", fC, ((x_hole + x_out) / 2, y, 0),
                        P.BOLT_R, x_hole - x_out, "X", coll))
        nut0, nut1 = P.X_BACK - 0.0005 - P.NUT_T - 0.0004, P.X_BACK - 0.0005
        _csg(body, _hex("_cnut", fC, ((nut0 + nut1) / 2, y, 0),
                        P.NUT_AF, nut1 - nut0, "X", coll))
        # 溝はナット座より 0.2mm 深く・0.6mm 浅く終え、幅は六角の二面幅より 0.4mm 広い。
        # y はナットの座に少しだけ食い込ませる（座の内側 6mm が残るので回り止めは効く）
        sl0, sl1 = nut0 - 0.0002, nut1 - 0.0006
        y0, y1 = y + s * 0.002, s * (P.BOSS_Y / 2 + 0.010)
        _csg(body, _box("_cslot", fC, ((sl0 + sl1) / 2, (y0 + y1) / 2, 0),
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
