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
    MM, PIPE_OD, BORE_D, HUB_D, LEG_HUB_D, BODY_T, TAPER_L, TIP_D, BASE_ROUND,
    FILLET_R, FILLET_ANGLE, X_TOP, X_BOT, X_PRISM,
    LEG_TOP_D, LEG_BOT_D, LEG_TOP_Z, LEG_X, TEARDROP_TOP,
    SIDE_Y, SIDE_Z, SLOPE_DEG, STRUT_T,
    TIE_T, TIE_Z_TOP, TIE_Z_BOT, TIE_Y,
    SEG, TAPER_SEG, FILLET_SEG, REF_RAIL_L, REF_LEG_L,
)

# ベベルする前は底を BASE_ROUND ぶん下へ伸ばしておき、最後に X_BOT で切る。
# こうすると底面は平らなまま、その上だけが丸まる。
X_BUILD_BOT = X_BOT - BASE_ROUND


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


def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


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
    """-X 端は満径のまま、+X 端だけ TIP_D まで落とす非対称プロファイル。"""
    r_hub, r_tip = HUB_D / 2, TIP_D / 2
    pts = [(X_BUILD_BOT, r_hub), (X_PRISM, r_hub)]
    for i in range(1, TAPER_SEG + 1):
        t = i / TAPER_SEG
        pts.append((X_PRISM + TAPER_L * t, r_hub + (r_tip - r_hub) * smoothstep(t)))
    return [(a * MM, r * MM) for a, r in pts]


def column_poly(sy):
    """脚ソケットの XY 断面。下は角、上は半円（＝スリーブと同径でつながる）。"""
    r = LEG_HUB_D / 2
    pts = [(X_BUILD_BOT, sy - r)]
    n = SEG // 2
    for i in range(n + 1):                       # -90° → +90°（+X 側の半円）
        a = -math.pi / 2 + math.pi * i / n
        pts.append((LEG_X + r * math.cos(a), sy + r * math.sin(a)))
    pts.append((X_BUILD_BOT, sy + r))
    return pts


def teardrop_poly(sy):
    """脚穴の XY 断面。円＋45度の屋根。屋根は TEARDROP_TOP で切る。"""
    r = BORE_D / 2
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

    # 斜材：中央スリーブ ↔ 左右スリーブ。X は X_BUILD_BOT..X_PRISM
    for sy in (SIDE_Y, -SIDE_Y):
        d = Vector((0.0, sy, SIDE_Z)).normalized()
        perp = Vector((0.0, -d.z, d.y))
        span = math.hypot(sy, SIDE_Z)
        cx = (X_BUILD_BOT + X_PRISM) / 2
        mid = Vector((cx, sy * 0.5, SIDE_Z * 0.5)) * MM
        rot = Matrix(((1.0, d.x, perp.x), (0.0, d.y, perp.y), (0.0, d.z, perp.z))).to_4x4()
        parts.append(box("strut_%s" % ("p" if sy > 0 else "n"),
                         ((X_PRISM - X_BUILD_BOT) * MM, (span + 12.0) * MM, STRUT_T * MM),
                         Matrix.Translation(mid) @ rot, col))

    # M の下の弦：左右の柱の下端に全幅で 1 本渡す。脚穴・中央レール穴はあとから開ける
    parts.append(box("tie",
                     ((X_PRISM - X_BUILD_BOT) * MM, 2 * TIE_Y * MM, TIE_T * MM),
                     Matrix.Translation(Vector(((X_BUILD_BOT + X_PRISM) / 2, 0.0,
                                                (TIE_Z_TOP + TIE_Z_BOT) / 2)) * MM), col))

    body = parts[0]
    body.name = "pipe_joint"
    for p in parts[1:]:
        boolean(body, p, "UNION")
    return body, col


def finish_body(body, col):
    # 接合部に R
    clean(body)
    bevel(body, FILLET_R * MM, FILLET_SEG, FILLET_ANGLE)

    # 底を平らに切る（角丸を残したまま接地面を確保）
    cut = box("cut_base", (200 * MM, 400 * MM, 400 * MM),
              Matrix.Translation(Vector((X_BOT - 100, 0, SIDE_Z / 2)) * MM), col)
    boolean(body, cut, "DIFFERENCE")

    # レール 3 本（貫通）
    r = BORE_D / 2
    for i, (y, z) in enumerate(RAILS):
        cut = revolve("bore_%d" % i, [(-300 * MM, r * MM), (300 * MM, r * MM)],
                      col, frame((0, y, z), ROT_Z_TO_X))
        boolean(body, cut, "DIFFERENCE")

    # 脚 2 本（下から差し込む止まり穴。天井はティアドロップ）
    for sy in (SIDE_Y, -SIDE_Y):
        poly = [(x * MM, y * MM) for x, y in teardrop_poly(sy)]
        cut = prism("bore_leg", poly, (SIDE_Z - LEG_BOT_D - 40) * MM, LEG_TOP_Z * MM, col)
        boolean(body, cut, "DIFFERENCE")

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
