"""28mm パイプ用 90 度コーナー（手すり）の形状生成。

円形の握りを45度の接線と平底へつなぐ。両端にはM字の受けへ入る短い舌を付ける。
内径と芯線は既存品と共通。舌の下面だけ局所サポートを使う。
"""
import math

import bpy
import bmesh
from mathutils import Vector

from params import (
    MM, BORE_D, HUB_R, Z_BASE, TD_TOP, BORE_MOUTH_L,
    STR_SEG, PROF_SEG, ARC_SEG_MIN,
    EDGE_R, R_INNER,
)
from rail_coupling import (INNER_R as KEY_INNER_R, OUTER_R as KEY_OUTER_R,
                           HALF_H as KEY_HALF_H, ROUND as KEY_ROUND,
                           INNER_L as KEY_INNER_L, OUTER_L as KEY_OUTER_L)

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

def make_path(R, straight):
    """芯線。原点＝円弧の中心。
    腕A: (-straight, R) → (0, R) を +X へ / 円弧: 90°→0° / 腕B: (R, 0) → (R, -straight)。"""
    arc_len = math.pi / 2 * R
    total = straight + arc_len + straight

    def at(s):
        if s <= straight:
            p = Vector(((s - straight) * MM, R * MM, 0.0))
            t = Vector((1.0, 0.0, 0.0))
        elif s <= straight + arc_len:
            a = math.pi / 2 - (s - straight) / R          # 90° → 0°
            p = Vector((R * math.cos(a) * MM, R * math.sin(a) * MM, 0.0))
            t = Vector((math.sin(a), -math.cos(a), 0.0))  # 時計回りの接線
        else:
            p = Vector((R * MM, -(s - straight - arc_len) * MM, 0.0))
            t = Vector((0.0, -1.0, 0.0))
        return p, t.cross(ZU).normalized(), ZU

    seg = max(ARC_SEG_MIN, int(R / 2))
    ss = [straight * i / STR_SEG for i in range(STR_SEG + 1)]
    ss += [straight + arc_len * i / seg for i in range(1, seg + 1)]
    ss += [straight + arc_len + straight * i / STR_SEG for i in range(1, STR_SEG + 1)]
    return at, ss, total


# ---------------------------------------------------------------- profiles

def rail_profile(r):
    """円形の側面から45度の接線で平底へ移る。最大幅・高さは維持する。"""
    pts = []
    n = round(PROF_SEG * 1.25)
    for i in range(n + 1):
        a = math.radians(225) * i / n
        pts.append((r * math.cos(a), r * math.sin(a)))
    # 45度面と底面が作る角に、両面へ接する小円弧を置く。
    corner = r * math.sqrt(2) - Z_BASE
    setback = EDGE_R * math.tan(math.pi / 8)
    for sign in (-1, 1):
        cx = sign * (corner - setback)
        cz = -Z_BASE + EDGE_R
        angles = (225, 270) if sign == -1 else (270, 315)
        for i in range(7):
            a = math.radians(angles[0] + (angles[1] - angles[0]) * i / 6)
            pts.append((cx + EDGE_R * math.cos(a), cz + EDGE_R * math.sin(a)))
    for i in range(PROF_SEG // 4 + 1):
        a = math.radians(315 + 45 * i / (PROF_SEG // 4))
        if i < PROF_SEG // 4:
            pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def add_keys(body, R, straight, col):
    """同じパイプを通したまま、M字の脇の受けへ入る2本の短い舌。"""
    length = KEY_INNER_L if abs(R - R_INNER) < 1e-6 else KEY_OUTER_L
    radial = (KEY_INNER_R + KEY_OUTER_R) / 2
    for end in range(2):
        for sign in (-1, 1):
            # 根元は0.8mm食い込ませる。穴を削った後なので内径は変わらない。
            center = (-(straight + (length - .8) / 2), R - sign * radial, 0)
            dims = (length + .8, KEY_OUTER_R - KEY_INNER_R, KEY_HALF_H * 2)
            if end:
                center = (center[1], center[0], center[2])
                dims = (dims[1], dims[0], dims[2])
            bpy.ops.mesh.primitive_cube_add(size=1, location=Vector(center) * MM)
            key = bpy.context.object
            key.name = 'location_key'
            key.dimensions = Vector(dims) * MM
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bevel = key.modifiers.new('soft_key_edges', 'BEVEL')
            bevel.width = KEY_ROUND * MM
            bevel.segments = 4
            bpy.ops.object.modifier_apply(modifier=bevel.name)
            boolean(body, key, 'UNION', solver='EXACT')
    return body


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
    ss = smoothstep(min(d, BORE_MOUTH_L) / BORE_MOUTH_L)
    return max(0.0, min(1.0, (ss - 0.15) / 0.55))


# ---------------------------------------------------------------- build

def build_corner(R, straight, name, col_name="corner"):
    col = get_collection(col_name)
    at, ss, total = make_path(R, straight)

    body = sweep(name, [at(s) for s in ss], [rail_profile(HUB_R) for _ in ss], col)
    _activate(body)
    mod = body.modifiers.new('mouth_outer_round', 'BEVEL')
    mod.width = EDGE_R * MM
    mod.segments = 4
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(35)
    bpy.ops.object.modifier_apply(modifier=mod.name)

    ss2 = [-20.0] + ss + [total + 20.0]
    boolean(body, sweep(name + "_bore", [at(s) for s in ss2],
                        [bore_profile(bore_t(s, total)) for s in ss2], col), "DIFFERENCE")
    add_keys(body, R, straight, col)
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-8)
    straight_vertices = []
    for v in bm.verts:
        if len(v.link_edges) == 2:
            a, b = (e.other_vert(v).co - v.co for e in v.link_edges)
            if a.length and b.length and a.normalized().dot(b.normalized()) < -.999999:
                straight_vertices.append(v)
    if straight_vertices:
        bmesh.ops.dissolve_verts(bm, verts=straight_vertices)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    assert all(e.is_manifold for e in bm.edges), 'corner mesh must be closed'
    bm.to_mesh(body.data)
    bm.free()
    _activate(body)
    bpy.ops.object.shade_flat()
    return body
