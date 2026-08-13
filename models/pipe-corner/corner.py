"""28mm パイプ用 90 度コーナー（手すり）の形状生成。

U ターン（models/pipe-uturn）と同じ断面・同じ作り方で、円弧だけ 90 度にしたもの。
半径を変えれば内側・中央・外側のどれにも使える。
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

from params import (
    MM, PIPE_OD, BORE_D, HUB_R, TIP_R, MOUTH_TAPER, Z_BASE, BOT_CHAMFER,
    STRAIGHT, TD_TOP, STR_SEG, PROF_SEG, ARC_SEG_MIN,
)

ZU = Vector((0.0, 0.0, 1.0))


# ---------------------------------------------------------------- helpers

def get_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def _activate(ob):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def _finish(name, bm, col):
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def sweep(name, stations, profiles, col):
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

def make_path(R):
    """芯線。原点＝円弧の中心。
    腕A: (-STRAIGHT, R) → (0, R) を +X へ / 円弧: 90°→0° / 腕B: (R, 0) → (R, -STRAIGHT)。"""
    arc_len = math.pi / 2 * R
    total = STRAIGHT + arc_len + STRAIGHT

    def at(s):
        if s <= STRAIGHT:
            p = Vector(((s - STRAIGHT) * MM, R * MM, 0.0))
            t = Vector((1.0, 0.0, 0.0))
        elif s <= STRAIGHT + arc_len:
            a = math.pi / 2 - (s - STRAIGHT) / R          # 90° → 0°
            p = Vector((R * math.cos(a) * MM, R * math.sin(a) * MM, 0.0))
            t = Vector((math.sin(a), -math.cos(a), 0.0))  # 時計回りの接線
        else:
            p = Vector((R * MM, -(s - STRAIGHT - arc_len) * MM, 0.0))
            t = Vector((0.0, -1.0, 0.0))
        return p, t.cross(ZU).normalized(), ZU

    seg = max(ARC_SEG_MIN, int(R / 2))
    ss = [STRAIGHT * i / STR_SEG for i in range(STR_SEG + 1)]
    ss += [STRAIGHT + arc_len * i / seg for i in range(1, seg + 1)]
    ss += [STRAIGHT + arc_len + STRAIGHT * i / STR_SEG for i in range(1, STR_SEG + 1)]
    return at, ss, total


# ---------------------------------------------------------------- profiles

def rho(s, total):
    d = max(min(s, total - s), 0.0)
    if d >= MOUTH_TAPER:
        return HUB_R
    return TIP_R + (HUB_R - TIP_R) * smoothstep(d / MOUTH_TAPER)


def rail_profile(r):
    pts = []
    for i in range(PROF_SEG + 1):
        a = math.pi * i / PROF_SEG
        pts.append((r * math.cos(a), r * math.sin(a)))
    c = min(BOT_CHAMFER, r - 1.0)
    pts += [(-r, -(Z_BASE - c)), (-(r - c), -Z_BASE), (r - c, -Z_BASE), (r, -(Z_BASE - c))]
    return pts


def bore_profile(t):
    """t=1 でティアドロップ、t=0 でただの円。口元では屋根を引っ込める。"""
    r = BORE_D / 2
    n = 64
    pts = [(r * math.cos(math.radians(135.0 + 270.0 * i / n)),
            r * math.sin(math.radians(135.0 + 270.0 * i / n))) for i in range(n + 1)]
    hw = r * math.sqrt(2.0) - TD_TOP
    for a_deg, roof in ((75.0, (hw, TD_TOP)), (105.0, (-hw, TD_TOP))):
        a = math.radians(a_deg)
        c = (r * math.cos(a), r * math.sin(a))
        pts.append((c[0] + (roof[0] - c[0]) * t, c[1] + (roof[1] - c[1]) * t))
    return pts


def bore_t(s, total):
    d = max(min(s, total - s), 0.0)
    ss = smoothstep(min(d, MOUTH_TAPER) / MOUTH_TAPER)
    return max(0.0, min(1.0, (ss - 0.15) / 0.55))


# ---------------------------------------------------------------- build

def build_corner(R, name, col_name="corner"):
    col = get_collection(col_name)
    at, ss, total = make_path(R)

    body = sweep(name, [at(s) for s in ss], [rail_profile(rho(s, total)) for s in ss], col)

    ss2 = [-20.0] + ss + [total + 20.0]
    boolean(body, sweep(name + "_bore", [at(s) for s in ss2],
                        [bore_profile(bore_t(s, total)) for s in ss2], col), "DIFFERENCE")
    _activate(body)
    bpy.ops.object.shade_flat()
    return body
