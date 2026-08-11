"""28mm パイプ用 180 度ヘアピンの形状生成。

外形は Z 方向の押し出し（プリズム）、中の穴は芯線に沿ってスイープした
ティアドロップ断面。寝かせたまま無サポートで刷れる。
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

from params import (
    MM, PIPE_OD, BORE_D, HUB_D, WALL, BODY_H, BAND_W, R, STRAIGHT, TD_TOP,
    FILLET_R, FILLET_ANGLE, FILLET_SEG, BASE_ROUND, ARC_SEG, PROF_SEG, REF_LEN,
)

Z_TOP = BODY_H / 2
Z_BOT = -BODY_H / 2
Z_BUILD_BOT = Z_BOT - BASE_ROUND   # 面取り分だけ下に伸ばして最後に切る


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
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def _finish(name, bm, col, matrix=None):
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:            # 凹の n-gon は boolean が嫌がるので割っておく
        bmesh.ops.triangulate(bm, faces=ngons)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if matrix is not None:
        ob.matrix_world = matrix
    return ob


def prism(name, poly, z0, z1, col, matrix=None):
    """poly: [(x, y)]。z0→z1 に押し出す。"""
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


def sweep(name, stations, profile, col, matrix=None):
    """stations: [(origin, u, v)]。profile: [(a, b)] を u,v 平面に置いて連ねる。"""
    bm = bmesh.new()
    rings = []
    for o, u, v in stations:
        rings.append([bm.verts.new(o + u * a + v * b) for a, b in profile])
    n = len(profile)
    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return _finish(name, bm, col, matrix)


def box(name, size, matrix, col):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts[:], vec=Vector(size))
    return _finish(name, bm, col, matrix)


def clean(ob, dist=1e-6):
    """boolean が残す極短エッジを掃除する。放置すると Bevel が発散する。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return ob


def boolean(target, cutter, op="DIFFERENCE", solver="MANIFOLD"):
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = solver
    _activate(target)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


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


# ---------------------------------------------------------------- geometry

def band_outline(x_mouth, half_w):
    """U の帯の 2D 輪郭（XY）。反時計回り。"""
    ro, ri = R + half_w, R - half_w
    pts = [(x_mouth, ri), (0.0, ri)]
    for i in range(ARC_SEG + 1):                       # 内側の弧 90°→270°
        a = math.pi / 2 + math.pi * i / ARC_SEG
        pts.append((ri * math.cos(a), ri * math.sin(a)))
    pts += [(x_mouth, -ri), (x_mouth, -ro), (0.0, -ro)]
    for i in range(ARC_SEG + 1):                       # 外側の弧 270°→90°
        a = 3 * math.pi / 2 - math.pi * i / ARC_SEG
        pts.append((ro * math.cos(a), ro * math.sin(a)))
    pts.append((x_mouth, ro))
    # 重複点を落とす
    out = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - out[-1][0]) > 1e-9 or abs(p[1] - out[-1][1]) > 1e-9:
            out.append(p)
    return out


def centerline(extra):
    """芯線の station 列。extra だけ両端を伸ばす。"""
    st = []
    zu = Vector((0.0, 0.0, 1.0))

    def add(p, t):
        u = t.cross(zu).normalized()      # 断面の水平方向
        st.append((p, u, zu))

    # +Y 側の直線（+X → 原点方向）
    n = 8
    for i in range(n + 1):
        x = (STRAIGHT + extra) * (1.0 - i / n)
        add(Vector((x, R, 0.0)), Vector((-1.0, 0.0, 0.0)))
    # 円弧 90° → 270°
    for i in range(1, ARC_SEG + 1):
        a = math.pi / 2 + math.pi * i / ARC_SEG
        p = Vector((R * math.cos(a), R * math.sin(a), 0.0))
        t = Vector((-math.sin(a), math.cos(a), 0.0))
        add(p, t)
    # -Y 側の直線
    for i in range(1, n + 1):
        x = (STRAIGHT + extra) * i / n
        add(Vector((x, -R, 0.0)), Vector((1.0, 0.0, 0.0)))
    return st


def teardrop_profile():
    """穴の断面。円＋45 度の屋根。屋根は TD_TOP で切る。"""
    r = BORE_D / 2
    apex = r * math.sqrt(2.0)
    hw = apex - TD_TOP
    pts = []
    for i in range(PROF_SEG + 1):                 # 135° → 405°（上を空ける）
        a = math.radians(135.0 + 270.0 * i / PROF_SEG)
        pts.append((r * math.cos(a), r * math.sin(a)))
    pts.append((hw, TD_TOP))
    pts.append((-hw, TD_TOP))
    return pts


def build_uturn(col_name="uturn"):
    col = get_collection(col_name)

    poly = [(x * MM, y * MM) for x, y in band_outline(STRAIGHT, BAND_W / 2)]
    body = prism("pipe_uturn", poly, Z_BUILD_BOT * MM, Z_TOP * MM, col)

    # 縦エッジに R
    clean(body)
    bevel(body, FILLET_R * MM, FILLET_SEG, FILLET_ANGLE)

    # 底を平らに切り直す（角丸を残したまま接地面を確保）
    cut = box("cut_base", (600 * MM, 600 * MM, 200 * MM),
              Matrix.Translation(Vector((0, 0, Z_BOT - 100)) * MM), col)
    boolean(body, cut, "DIFFERENCE")

    # 中を通す穴（ティアドロップ断面のスイープ）
    st = [(o * MM, u, v) for o, u, v in centerline(20.0)]
    prof = [(a * MM, b * MM) for a, b in teardrop_profile()]
    boolean(body, sweep("bore", st, prof, col), "DIFFERENCE")

    _activate(body)
    bpy.ops.object.shade_flat()
    return body, col


def build_ref_pipes(col_name="uturn_ref"):
    col = get_collection(col_name)
    r = PIPE_OD / 2
    prof = [(r * math.cos(2 * math.pi * i / 48) * MM,
             r * math.sin(2 * math.pi * i / 48) * MM) for i in range(48)]
    zu = Vector((0.0, 0.0, 1.0))
    for sy in (R, -R):
        st = [(Vector((STRAIGHT * MM, sy * MM, 0.0)), Vector((0.0, 1.0, 0.0)), zu),
              (Vector(((STRAIGHT + REF_LEN) * MM, sy * MM, 0.0)), Vector((0.0, 1.0, 0.0)), zu)]
        sweep("ref_%s" % ("p" if sy > 0 else "n"), st, prof, col)
    return col


def build_all(ref=True):
    body, col = build_uturn()
    if ref:
        build_ref_pipes()
    return body
