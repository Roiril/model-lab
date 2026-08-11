"""28mm パイプ用 180 度ヘアピン（手すり）の形状生成。

芯線に沿って断面をスイープするだけで作る。断面は上へ行くほど細るので、
寝かせたまま無サポートで刷れる。中を通す穴だけ天井をティアドロップにする。
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

from params import (
    MM, PIPE_OD, BORE_D, HUB_R, TIP_R, MOUTH_TAPER, Z_BASE, BOT_CHAMFER,
    R, STRAIGHT, TD_TOP, ARC_SEG, STR_SEG, PROF_SEG, REF_LEN,
)

ARC_LEN = math.pi * R
TOTAL_LEN = 2 * STRAIGHT + ARC_LEN
ZU = Vector((0.0, 0.0, 1.0))


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
    if ngons:
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


def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def sweep(name, stations, profiles, col):
    """stations: [(origin, u, v)]、profiles: 各 station の [(a, b)]（点数は共通）。"""
    bm = bmesh.new()
    rings = []
    for (o, u, v), prof in zip(stations, profiles):
        rings.append([bm.verts.new(o + u * (a * MM) + v * (b * MM)) for a, b in prof])
    n = len(profiles[0])
    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return _finish(name, bm, col)


def boolean(target, cutter, op="DIFFERENCE", solver="MANIFOLD"):
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = solver
    _activate(target)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


# ---------------------------------------------------------------- path

def station_at(s):
    """芯線上の距離 s の位置と断面の向き。s<0 / s>TOTAL_LEN は直線部の延長。"""
    if s <= STRAIGHT:
        p = Vector(((STRAIGHT - s) * MM, R * MM, 0.0))
        t = Vector((-1.0, 0.0, 0.0))
    elif s <= STRAIGHT + ARC_LEN:
        a = math.pi / 2 + (s - STRAIGHT) / R
        p = Vector((R * math.cos(a) * MM, R * math.sin(a) * MM, 0.0))
        t = Vector((-math.sin(a), math.cos(a), 0.0))
    else:
        p = Vector(((s - STRAIGHT - ARC_LEN) * MM, -R * MM, 0.0))
        t = Vector((1.0, 0.0, 0.0))
    return p, t.cross(ZU).normalized(), ZU


def s_list(pad=0.0):
    """口元の変化を拾えるように、直線部は細かく刻む。"""
    out = []
    n = STR_SEG
    for i in range(n + 1):
        out.append(-pad + (STRAIGHT + pad) * i / n)
    for i in range(1, ARC_SEG + 1):
        out.append(STRAIGHT + ARC_LEN * i / ARC_SEG)
    for i in range(1, n + 1):
        out.append(STRAIGHT + ARC_LEN + (STRAIGHT + pad) * i / n)
    return out


# ---------------------------------------------------------------- profiles

def rho(s):
    """外形の半径。両端の口元だけ TIP_R まで絞る。"""
    d = max(min(s, TOTAL_LEN - s), 0.0)
    if d >= MOUTH_TAPER:
        return HUB_R
    return TIP_R + (HUB_R - TIP_R) * smoothstep(d / MOUTH_TAPER)


def rail_profile(r):
    """上半分は半円、横は垂直、下は 45 度面取りの平ら。反時計回り。"""
    pts = []
    for i in range(PROF_SEG + 1):            # φ=0 → 180（上の半円）
        a = math.pi * i / PROF_SEG
        pts.append((r * math.cos(a), r * math.sin(a)))
    c = min(BOT_CHAMFER, r - 1.0)
    pts.append((-r, -(Z_BASE - c)))
    pts.append((-(r - c), -Z_BASE))
    pts.append((r - c, -Z_BASE))
    pts.append((r, -(Z_BASE - c)))
    return pts


def teardrop_profile():
    """穴の断面。円＋45 度の屋根。屋根は TD_TOP で切る。"""
    r = BORE_D / 2
    hw = r * math.sqrt(2.0) - TD_TOP
    pts = []
    n = 64
    for i in range(n + 1):                   # 135° → 405°（上を空ける）
        a = math.radians(135.0 + 270.0 * i / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    pts.append((hw, TD_TOP))
    pts.append((-hw, TD_TOP))
    return pts


# ---------------------------------------------------------------- build

def build_uturn(col_name="uturn"):
    col = get_collection(col_name)

    ss = s_list()
    st = [station_at(s) for s in ss]
    body = sweep("pipe_uturn", st, [rail_profile(rho(s)) for s in ss], col)

    ss2 = s_list(pad=20.0)
    st2 = [station_at(s) for s in ss2]
    td = teardrop_profile()
    boolean(body, sweep("bore", st2, [td] * len(ss2), col), "DIFFERENCE")

    _activate(body)
    bpy.ops.object.shade_flat()
    return body, col


def build_ref_pipes(col_name="uturn_ref"):
    col = get_collection(col_name)
    r = PIPE_OD / 2
    prof = [(r * math.cos(2 * math.pi * i / 48), r * math.sin(2 * math.pi * i / 48))
            for i in range(48)]
    for sy in (R, -R):
        st = [(Vector((STRAIGHT * MM, sy * MM, 0.0)), Vector((0.0, 1.0, 0.0)), ZU),
              (Vector(((STRAIGHT + REF_LEN) * MM, sy * MM, 0.0)), Vector((0.0, 1.0, 0.0)), ZU)]
        sweep("ref_%s" % ("p" if sy > 0 else "n"), st, [prof, prof], col)
    return col


def build_all(ref=True):
    body, col = build_uturn()
    if ref:
        build_ref_pipes()
    return body
