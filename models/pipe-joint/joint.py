"""28mm パイプ用 5方向ジョイントの形状生成。

+X を上にして一体で 3D プリントする前提の非対称形状。
build_joint() はシーンをクリアしない。BlenderMCP で開きっぱなしの
シーンへ差し込めるように、生成物は指定コレクションへ入れる。
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

from params import (
    MM, PIPE_OD, BORE_D, HUB_D, LEG_HUB_D, BODY_T, SLEEVE_END_R, RAIL_LEAD,
    BASE_ROUND, WEB_EDGE_R,
    FILLET_R, FILLET_ANGLE, X_TOP, X_BOT, X_PRISM,
    LEG_TOP_D, LEG_BOT_D, LEG_TOP_Z, LEG_X, TEARDROP_TOP,
    LEG_BORE_D, LEG_RELIEF_D, LEG_RELIEF_Z0, LEG_RELIEF_Z1, LEG_LEAD,
    SIDE_Y, SIDE_Z, SLOPE_DEG,
    STRUT_T, STRUT_AXIS_R, STRUT_FOOT_Z, STRUT_TOP_EXT,
    WEB_X_TOP,
    TIE_H, TIE_Z_TOP, TIE_Z_BOT, TIE_Y,
    SEG, SLEEVE_END_SEG, FILLET_SEG, REF_RAIL_L, REF_LEG_L,
)

# ---------------------------------------------------------------- helpers

def get_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    return col


def _activate(ob):
    """ops 系は選択状態を見るので必ず通す。"""
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def _finish(name, bm, col, matrix=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if matrix is not None:
        ob.matrix_world = matrix
    return ob


def revolve(name, profile, col, matrix=None, seg=SEG):
    """profile: [(axial, radius)] radius>0、axial は単調増加。ローカル軸は Z。"""
    bm = bmesh.new()
    rings = []
    for a, r in profile:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg),
                                    r * math.sin(2 * math.pi * i / seg), a))
                      for i in range(seg)])
    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return _finish(name, bm, col, matrix)


def prism(name, poly, z0, z1, col, matrix=None):
    """poly: [(x, y)] を反時計回りで。z0→z1 に押し出した柱を作る。"""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in poly]
    hi = [bm.verts.new((x, y, z1)) for x, y in poly]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    return _finish(name, bm, col, matrix)


def box(name, size, matrix, col):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts[:], vec=Vector(size))
    return _finish(name, bm, col, matrix)


def loft(name, polys, zs, col):
    """同じ頂点数の (x, y) 多角形（mm）を z（mm）ごとに置いて帯で結ぶ。断面が z で変わる柱。"""
    bm = bmesh.new()
    rings = [[bm.verts.new((x * MM, y * MM, z * MM)) for x, y in poly] for poly, z in zip(polys, zs)]
    n = len(polys[0])
    for lo, hi in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return _finish(name, bm, col)


def boolean(target, cutter, op="UNION", solver="MANIFOLD"):
    # EXACT は細かいメッシュに止まり穴を空けると結果が空になることがある
    # （Blender 5.1 で実測）。MANIFOLD なら通る。
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = solver
    _activate(target)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def clean(ob, dist=1e-6):
    """boolean が残す極短エッジ・重複頂点を掃除する。
    これをやらないと直後の Bevel が発散して座標が 1e26 になる（Blender 5.1 で実測）。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges[:])
    # 辺が 2 本しか無く一直線に並ぶ頂点を消す。Blender の中では多様体でも、STL の三角化が
    # 両側の面で食い違って面積 0 の三角形が残る（lib/foot_core.clean と同じ対策）
    straight = []
    for v in bm.verts:
        if len(v.link_edges) == 2:
            a, b = (e.other_vert(v).co - v.co for e in v.link_edges)
            if a.length > 0 and b.length > 0 and a.normalized().dot(b.normalized()) < -0.9999:
                straight.append(v)
    if straight:
        bmesh.ops.dissolve_verts(bm, verts=straight)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return ob


def bevel(ob, width, segments, angle_deg):
    mod = ob.modifiers.new("bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle_deg)
    mod.miter_outer = "MITER_ARC"
    mod.use_clamp_overlap = True
    _activate(ob)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


ROT_Z_TO_X = Matrix.Rotation(math.radians(90), 4, "Y")


def frame(origin=(0, 0, 0), rot=None):
    m = Matrix.Translation(Vector(origin) * MM)
    return m @ rot if rot is not None else m


def leg_frame(sy):
    """脚の座標系。原点＝左右レールの軸、ローカル +Z＝上。SLOPE_DEG だけ倒す。"""
    return (Matrix.Translation(Vector((0.0, sy, SIDE_Z)) * MM)
            @ Matrix.Rotation(math.radians(SLOPE_DEG), 4, "Y"))


RAILS = ((0.0, 0.0), (SIDE_Y, SIDE_Z), (-SIDE_Y, SIDE_Z))


# ---------------------------------------------------------------- build

def sleeve_profile():
    """満径の筒。両端の外角だけ接線の連続する円弧で丸める。"""
    r_hub = HUB_D / 2
    pts = [(X_BOT, r_hub - BASE_ROUND)]
    for i in range(1, SLEEVE_END_SEG + 1):
        a = -math.pi / 2 + math.pi * i / (2 * SLEEVE_END_SEG)
        pts.append((X_BOT + BASE_ROUND + BASE_ROUND * math.sin(a),
                    r_hub - BASE_ROUND + BASE_ROUND * math.cos(a)))
    pts.append((X_TOP - SLEEVE_END_R, r_hub))
    for i in range(1, SLEEVE_END_SEG + 1):
        a = math.pi * i / (2 * SLEEVE_END_SEG)
        pts.append((X_TOP - SLEEVE_END_R + SLEEVE_END_R * math.sin(a),
                    r_hub - SLEEVE_END_R + SLEEVE_END_R * math.cos(a)))
    return [(a * MM, r * MM) for a, r in pts]


def column_poly(sy):
    """脚ソケットの XY 断面。-X の角を袖と揃え、+X は半円。"""
    r = LEG_HUB_D / 2
    pts = [(X_BOT, sy - r + BASE_ROUND)]
    for i in range(1, SLEEVE_END_SEG + 1):
        a = math.pi + math.pi * i / (2 * SLEEVE_END_SEG)
        pts.append((X_BOT + BASE_ROUND + BASE_ROUND * math.cos(a),
                    sy - r + BASE_ROUND + BASE_ROUND * math.sin(a)))
    n = SEG // 2
    for i in range(n + 1):                       # -90° → +90°（+X 側の半円）
        a = -math.pi / 2 + math.pi * i / n
        pts.append((LEG_X + r * math.cos(a), sy + r * math.sin(a)))
    for i in range(1, SLEEVE_END_SEG + 1):
        a = math.pi / 2 + math.pi * i / (2 * SLEEVE_END_SEG)
        pts.append((X_BOT + BASE_ROUND + BASE_ROUND * math.cos(a),
                    sy + r - BASE_ROUND + BASE_ROUND * math.sin(a)))
    return pts


def teardrop_poly(sy, r):
    """脚穴の XY 断面（半径 r）。円＋45度の屋根。屋根は TEARDROP_TOP で切る。"""
    apex = LEG_X + r * math.sqrt(2.0)
    hw = apex - TEARDROP_TOP
    pts = []
    n = 72
    for i in range(n + 1):                       # θ=45° から 315° へ（+X 側を空ける）
        a = math.radians(45.0 + 270.0 * i / n)
        pts.append((LEG_X + r * math.cos(a), sy + r * math.sin(a)))
    pts.append((TEARDROP_TOP, sy - hw))
    pts.append((TEARDROP_TOP, sy + hw))
    return pts


def strut_axis():
    """+Y 側の斜材の中心線。向き (dy, dz) と下端 (fy, fz) を返す。-Y 側は y を反転する。

    左右レールの軸から下ろし、中央レールの軸を STRUT_AXIS_R だけ外して振る。
    そのまま下の弦の厚みの真ん中まで伸ばすので、谷が弦の上の節点になる。
    """
    span = math.hypot(SIDE_Y, SIDE_Z)
    by, bz = -SIDE_Y / span, -SIDE_Z / span          # 左右レール軸 → 中央レール軸
    a = math.asin(STRUT_AXIS_R / span)               # 中央を外すぶんの振り角
    ca, sa = math.cos(a), math.sin(a)
    dy, dz = by * ca - bz * sa, by * sa + bz * ca    # +Y 側を通る向きへ振る
    t = (SIDE_Z - STRUT_FOOT_Z) / -dz
    return (dy, dz), (SIDE_Y + dy * t, SIDE_Z + dz * t)


def build_joint(col_name="joint"):
    col = get_collection(col_name)
    parts = []

    # レールを掴むスリーブ 3 本（軸 = X）
    prof = sleeve_profile()
    for i, (y, z) in enumerate(RAILS):
        parts.append(revolve("sleeve_%d" % i, prof, col, frame((0, y, z), ROT_Z_TO_X)))

    # 脚のソケット（XY 断面を Z 方向へ押し出した柱）
    for sy in (SIDE_Y, -SIDE_Y):
        poly = [(x * MM, y * MM) for x, y in column_poly(sy)]
        parts.append(prism("column_%s" % ("p" if sy > 0 else "n"), poly,
                           (SIDE_Z - LEG_BOT_D) * MM, SIDE_Z * MM, col))

    # M の下の弦：左右の柱の下端に全幅で 1 本渡す。脚穴・中央レール穴はあとから開ける。
    # ⚠ 斜材より先に積む。斜材の下端の面が弦の肉の中に入った状態で union するため
    web_d = WEB_X_TOP - X_BOT
    cx = (X_BOT + WEB_X_TOP) / 2
    tie = box("tie",
              (web_d * MM, 2 * TIE_Y * MM, TIE_H * MM),
              Matrix.Translation(Vector((cx, 0.0,
                                         (TIE_Z_TOP + TIE_Z_BOT) / 2)) * MM), col)
    bevel(tie, WEB_EDGE_R * MM, FILLET_SEG, FILLET_ANGLE)
    parts.append(tie)

    # 斜材：左右スリーブ → 下の弦。X は弦と同じ奥行き（底面から WEB_D）
    # 上端は左右レールの軸より外へ、下端は弦の厚みの真ん中まで伸ばす。
    # どちらの端面も既にある肉の中で終わるので、union が端どうしの接触にならない
    (dy, dz), (fy, fz) = strut_axis()
    for sy in (SIDE_Y, -SIDE_Y):
        s = 1.0 if sy > 0 else -1.0
        d = Vector((0.0, dy * s, dz))
        perp = Vector((0.0, -d.z, d.y))
        top = Vector((cx, sy, SIDE_Z)) - d * STRUT_TOP_EXT
        foot = Vector((cx, fy * s, fz))
        rot = Matrix(((1.0, d.x, perp.x), (0.0, d.y, perp.y), (0.0, d.z, perp.z))).to_4x4()
        strut = box("strut_%s" % ("p" if sy > 0 else "n"),
                    (web_d * MM, (top - foot).length * MM, STRUT_T * MM),
                    Matrix.Translation((top + foot) * 0.5 * MM) @ rot, col)
        bevel(strut, WEB_EDGE_R * MM, FILLET_SEG, FILLET_ANGLE)
        parts.append(strut)

    body = parts[0]
    body.name = "pipe_joint"
    for p in parts[1:]:
        boolean(body, p, "UNION")
    return body, col


def finish_body(body, col):
    # 接合部に R
    clean(body)
    bevel(body, FILLET_R * MM, FILLET_SEG, FILLET_ANGLE)

    # レール 3 本（貫通）
    r = BORE_D / 2
    for i, (y, z) in enumerate(RAILS):
        cut = revolve("bore_%d" % i, [(-300 * MM, r * MM), (300 * MM, r * MM)],
                      col, frame((0, y, z), ROT_Z_TO_X))
        boolean(body, cut, "DIFFERENCE")
        lead = revolve("bore_lead_%d" % i,
                       [((X_TOP - RAIL_LEAD) * MM, r * MM),
                        ((X_TOP + RAIL_LEAD) * MM, (r + 2 * RAIL_LEAD) * MM)],
                       col, frame((0, y, z), ROT_Z_TO_X))
        boolean(body, lead, "DIFFERENCE")

    # 脚 2 本（下から差し込む止まり穴。天井はティアドロップ）。
    # 半径は z で変える: 弦の底の口に 45° のリード → 当たる帯 → 逃がし（45° で移る）→ 座面側の帯
    rb, rr = LEG_BORE_D / 2, LEG_RELIEF_D / 2
    d = rr - rb
    z_lead = TIE_Z_BOT + LEG_LEAD
    # ⚠ 輪を部品の面（弦の底 TIE_Z_BOT）に載せない。載せると交線が既存の頂点と重なって
    #   面積 0 の三角形が残る。円錐は面の 1mm 下から始めて面を斜めに横切らせる
    stations = [(SIDE_Z - LEG_BOT_D - 40, rb + LEG_LEAD + 1.0), (TIE_Z_BOT - 1.0, rb + LEG_LEAD + 1.0),
                (z_lead, rb),
                (LEG_RELIEF_Z0 - d, rb), (LEG_RELIEF_Z0, rr),
                (LEG_RELIEF_Z1, rr), (LEG_RELIEF_Z1 + d, rb), (LEG_TOP_Z, rb)]
    for sy in (SIDE_Y, -SIDE_Y):
        cut = loft("bore_leg", [teardrop_poly(sy, r) for _, r in stations],
                   [z for z, _ in stations], col)
        boolean(body, cut, "DIFFERENCE")

    from rail_coupling import add_upper_bead
    side = Vector((0.0, 1.0, 0.0))
    up = Vector((0.0, 0.0, 1.0))
    for i, sy in enumerate((-SIDE_Y, SIDE_Y)):
        def frame_at(x, rail_y=sy):
            return Vector((x, rail_y, SIDE_Z)) * MM, side, up
        add_upper_bead(body, 'rail_bead_%d' % i, frame_at, X_BOT + 6.0,
                       col, boolean, HUB_D / 2)

    # 仕上げの掃除は 1e-6 で。⚠ 2e-5 にすると、斜材・弦・平らな面が集まる角にある
    # 0.03mm の辺（正しい形）まで溶かして面が壊れ、STL に非多様体が 3〜6 本出る
    # （2026-09-13 実測。1e-6 と掃除なしはどちらも 0）
    clean(body, dist=1e-6)
    # STLと3MFで同じ三角形を使う。極小の面は書き出す前に整理する。
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-8)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    assert all(e.is_manifold for e in bm.edges), 'joint mesh must be closed'
    bm.to_mesh(body.data)
    bm.free()

    _activate(body)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_flat()
    return body


def build_ref_pipes(col_name="ref_pipes"):
    """実寸の参照パイプ。印刷対象ではない。"""
    col = get_collection(col_name)
    r = PIPE_OD / 2
    rail = [(-REF_RAIL_L / 2 * MM, r * MM), (REF_RAIL_L / 2 * MM, r * MM)]
    for i, (y, z) in enumerate(RAILS):
        revolve("rail_%d" % i, rail, col, frame((0, y, z), ROT_Z_TO_X), seg=48)
    leg = [((-LEG_TOP_D - REF_LEG_L) * MM, r * MM), (-LEG_TOP_D * MM, r * MM)]
    for sy in (SIDE_Y, -SIDE_Y):
        m = leg_frame(sy) @ Matrix.Translation(Vector((LEG_X, 0, 0)) * MM)
        revolve("leg_%s" % ("p" if sy > 0 else "n"), leg, col, m, seg=48)
    return col


def build_all(ref=True):
    body, col = build_joint()
    finish_body(body, col)
    if ref:
        build_ref_pipes()
    return body
