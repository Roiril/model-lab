"""28mm パイプ用 90 度コーナー（手すり）の形状生成。

外側は中央ポールを避ける凸な曲線と広い平底。内側は円弧と従来の平底。
内径と接続位置は既存品と共通。両端の一体の筒をM字の円形受けへ差す。
"""
import math
from bisect import bisect_left

import bpy
import bmesh
from mathutils import Vector

from params import (
    MM, BORE_D, HUB_R, Z_BASE, BORE_ROOF_HALF, BORE_ROOF_TOP,
    ROOF_SKIN_LIFT, BORE_MOUTH_L,
    STR_SEG, PROF_SEG, ARC_SEG_MIN,
    EDGE_R, R_INNER, R_OUTER, OUTER_BULGE, OUTER_HANDLE,
    OUTER_BOTTOM_SLOPE, OUTER_BED_INSET, REVEAL,
)
from rail_coupling import (SPIGOT_R, SPIGOT_LEAD, ENGAGEMENT,
                           COLLAR_R, COLLAR_HOLD, COLLAR_BLEND)

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

def outer_curve(R, t):
    """端の位置・接線・曲率0を保った、凸な5次Bezier曲線。単位mm。"""
    a = OUTER_HANDLE * R
    b = (32 * (R + OUTER_BULGE) / math.sqrt(2) - 16 * R - 5 * a) / 10
    points = ((0, R), (a, R), (b, R), (R, b), (R, a), (R, 0))
    assert 0 < a < b < R
    def bezier(ps):
        n = len(ps) - 1
        return tuple(sum(math.comb(n, i) * (1-t)**(n-i) * t**i * p[k]
                         for i, p in enumerate(ps)) for k in (0, 1))
    derivative = [(5 * (q[0]-p[0]), 5 * (q[1]-p[1])) for p, q in zip(points, points[1:])]
    return bezier(points), bezier(derivative)


def make_path(R, straight):
    """芯線。原点＝円弧の中心。
    腕A: (-straight, R) → (0, R) を +X へ / 円弧: 90°→0° / 腕B: (R, 0) → (R, -straight)。"""
    arc_len = math.pi / 2 * R
    outer = abs(R - R_OUTER) < 1e-6
    if outer:
        # 距離sは曲線上でもmm。補間用の累積長を作り、等距離で断面を置く。
        samples = 2048
        points = [outer_curve(R, i / samples)[0] for i in range(samples + 1)]
        lengths = [0.0]
        for a, b in zip(points, points[1:]):
            lengths.append(lengths[-1] + math.dist(a, b))
        arc_len = lengths[-1]
    total = straight + arc_len + straight

    def at(s):
        if s <= straight:
            p = Vector(((s - straight) * MM, R * MM, 0.0))
            t = Vector((1.0, 0.0, 0.0))
        elif s <= straight + arc_len:
            if outer:
                distance = s - straight
                i = max(1, min(samples, bisect_left(lengths, distance)))
                u = (i - 1 + (distance-lengths[i-1]) / (lengths[i]-lengths[i-1])) / samples
                point, derivative = outer_curve(R, u)
                p = Vector((point[0] * MM, point[1] * MM, 0))
                t = Vector((*derivative, 0)).normalized()
            else:
                a = math.pi / 2 - (s - straight) / R
                p = Vector((R * math.cos(a) * MM, R * math.sin(a) * MM, 0.0))
                t = Vector((math.sin(a), -math.cos(a), 0.0))
        else:
            p = Vector((R * MM, -(s - straight - arc_len) * MM, 0.0))
            t = Vector((0.0, -1.0, 0.0))
        return p, t.cross(ZU).normalized(), ZU

    seg = max(ARC_SEG_MIN, int(arc_len / 2)) if outer else max(ARC_SEG_MIN, int(R / 2))
    if outer and seg % 2:
        seg += 1                    # 最もポールへ近い中点も必ず含める
    ss = [straight * i / STR_SEG for i in range(STR_SEG + 1)]
    ss += [straight + arc_len * i / seg for i in range(1, seg + 1)]
    ss += [straight + arc_len + straight * i / STR_SEG for i in range(1, STR_SEG + 1)]
    return at, ss, total


# ---------------------------------------------------------------- profiles

def rail_profile(r, outer=False, roof_lift=0.0):
    """平底と上面のなだらかな厚みを持つ外周断面。"""
    def upper_point(a):
        # 45〜135度だけを接線が続く形で膨らませる。底と側面は変えない。
        lift = 0.0
        if math.pi / 4 < a < 3 * math.pi / 4:
            lift = roof_lift * math.sin(2 * (a - math.pi / 4)) ** 2
        rho = r + lift
        return rho * math.cos(a), rho * math.sin(a)

    if outer:
        slope = math.radians(OUTER_BOTTOM_SLOPE)
        end = math.pi * 1.5 - slope
        n = round(PROF_SEG * end / math.pi)
        pts = [upper_point(end * i / n) for i in range(n + 1)]
        # 側面の円へ接する55度斜面と平底。最後の0.3mmは45度の面取り。
        corner = r * math.sin(slope) - (Z_BASE-r*math.cos(slope))/math.tan(slope)
        rise = OUTER_BED_INSET / (1 - 1/math.tan(slope))
        shoulder = corner + rise / math.tan(slope)
        flat = corner - OUTER_BED_INSET
        pts += [(-shoulder, -Z_BASE + rise), (-flat, -Z_BASE),
                (flat, -Z_BASE), (shoulder, -Z_BASE + rise)]
        start = math.pi * 1.5 + slope
        n = round(PROF_SEG * (2*math.pi-start) / math.pi)
        pts += [(r * math.cos(start + (2*math.pi-start)*i/n),
                 r * math.sin(start + (2*math.pi-start)*i/n)) for i in range(n)]
        return pts
    pts = []
    n = round(PROF_SEG * 1.25)
    for i in range(n + 1):
        a = math.radians(225) * i / n
        pts.append(upper_point(a))
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


def bore_profile(t):
    """t=1 で45度の屋根と6mmの短い橋渡し。口元では円へ戻す。"""
    r = BORE_D / 2
    n = 64
    pts = [(r * math.cos(math.radians(135.0 + 270.0 * i / n)),
            r * math.sin(math.radians(135.0 + 270.0 * i / n))) for i in range(n + 1)]
    for a_deg, roof in ((75.0, (BORE_ROOF_HALF, BORE_ROOF_TOP)),
                        (90.0, (0, BORE_ROOF_TOP)),
                        (105.0, (-BORE_ROOF_HALF, BORE_ROOF_TOP))):
        a = math.radians(a_deg)
        c = (r * math.cos(a), r * math.sin(a))
        pts.append((c[0] + (roof[0] - c[0]) * t, c[1] + (roof[1] - c[1]) * t))
    return pts


def bore_t(s, total):
    d = max(min(s, total - s), 0.0)
    ss = smoothstep(min(d, BORE_MOUTH_L) / BORE_MOUTH_L)
    return max(0.0, min(1.0, (ss - 0.15) / 0.55))


def spigot_profile(r):
    """円形受けに収まる筒。底のみ本体と同じ高さで切り、接地を連続させる。"""
    start = -math.asin(Z_BASE / r)
    angles = [start * (1-i/16) for i in range(16)]
    angles += [math.pi*i/64 for i in range(65)]
    angles += [math.pi-start*i/16 for i in range(1,17)]
    return [(r*math.cos(a), max(-Z_BASE, r*math.sin(a))) for a in angles]


# ---------------------------------------------------------------- build

def build_corner(R, straight, name, col_name="corner"):
    col = get_collection(col_name)
    at, ss, total = make_path(R, straight)

    outer = abs(R - R_OUTER) < 1e-6
    # 端の肩は厚くし、8mmで元の握り径へ戻す。平底の高さは変えない。
    ss = sorted(set(ss + [d for d in (COLLAR_HOLD, COLLAR_BLEND)]
                    + [total-d for d in (COLLAR_HOLD, COLLAR_BLEND)]))
    def collar_radius(s):
        d = min(s, total-s)
        t = max(0, min(1, (d-COLLAR_HOLD)/(COLLAR_BLEND-COLLAR_HOLD)))
        return HUB_R + (COLLAR_R-HUB_R)*(1-smoothstep(t))
    def upper_lift(s):
        # 差し込み口の丸穴では肩が十分に厚い。屋根が高くなると上面も高くする。
        radius = collar_radius(s)
        return max(0.0, HUB_R + ROOF_SKIN_LIFT - radius) * bore_t(s, total)
    body = sweep(name, [at(s) for s in ss],
                 [rail_profile(collar_radius(s), outer, upper_lift(s)) for s in ss], col)
    _activate(body)
    mod = body.modifiers.new('mouth_outer_round', 'BEVEL')
    mod.width = EDGE_R * MM
    mod.segments = 4
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(35)
    if outer:
        # 平底の面取りを二重に丸めない。口の端面だけを丸める。
        weights = body.data.attributes.new('bevel_weight_edge', 'FLOAT', 'EDGE')
        for edge in body.data.edges:
            coords = [body.data.vertices[i].co for i in edge.vertices]
            mouth = any(all(abs(p[axis] + straight * MM) < 1e-7 for p in coords) for axis in (0, 1))
            above_sole = all(p.z > (-Z_BASE + 1.01) * MM for p in coords)
            weights.data[edge.index].value = float(mouth and above_sole)
        mod.limit_method = 'WEIGHT'
    bpy.ops.object.modifier_apply(modifier=mod.name)

    # 中空化する前に全周の差し込み筒を結合する。根元は肩の内部へ1mm重ねる。
    length = ENGAGEMENT + (REVEAL if outer else 0)
    for end in (0, 1):
        bm = bmesh.new()
        bm.from_mesh(body.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-7)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-8)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(body.data)
        bm.free()
        distances = [-length, -length+SPIGOT_LEAD, 1.0]
        radii = [SPIGOT_R-SPIGOT_LEAD, SPIGOT_R, SPIGOT_R]
        stations = [at(total-d if end else d) for d in distances]
        male = sweep(name+'_spigot', stations, [spigot_profile(r) for r in radii], col)
        # 外カーブの2本目はEXACTが共面の平底を3頂点へ崩す。閉じた入力を確認して切替。
        solver = 'MANIFOLD' if outer and end else 'EXACT'
        if solver == 'MANIFOLD':
            for part in (body, male):
                check = bmesh.new()
                check.from_mesh(part.data)
                assert check.faces and all(e.is_manifold for e in check.edges), 'union input must be closed'
                assert abs(check.calc_volume()) > 1e-9, 'union input must contain volume'
                check.free()
        boolean(body, male, 'UNION', solver=solver)

    ss2 = [-20.0] + ss + [total + 20.0]
    boolean(body, sweep(name + "_bore", [at(s) for s in ss2],
                        [bore_profile(bore_t(s, total)) for s in ss2], col), "DIFFERENCE")
    if outer:
        # 穴の口に残る極小の辺を整理してから突起を結合する。
        bm = bmesh.new()
        bm.from_mesh(body.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-7)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-8)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(body.data)
        bm.free()
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
    non_manifold = [e for e in bm.edges if not e.is_manifold]
    if non_manifold:
        print('[corner] non-manifold', name, len(non_manifold),
              [[tuple(round(c * 1000, 4) for c in v.co) for v in e.verts]
               for e in non_manifold[:12]])
    assert bm.verts and bm.faces and not non_manifold, 'corner mesh must be nonempty and closed'
    bm.to_mesh(body.data)
    bm.free()
    _activate(body)
    bpy.ops.object.shade_flat()
    return body
