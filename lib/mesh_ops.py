"""平板構造のモデルを組むための共通ヘルパー。

輪郭を多角形で作って押し出す（prism_*）ことを基本にする。箱と円柱の UNION は
円柱が箱の面に接して長さ 0 のエッジを残し、そのまま次の boolean に入ると
EXACT が「エラーを出さずに」壊れた結果を返す（CLAUDE.md / servo-robot-design 参照）。

boolean のたびに clean() を通すこと。union() / cut() は中で呼んでいる。
"""

import math

import bpy
import bmesh


# ------------------------------------------------------------
# 基本
# ------------------------------------------------------------

def activate(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    return o


def place(o, mat):
    """行列で置き直して適用する。"""
    o.matrix_world = mat @ o.matrix_world
    activate(o)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o


def clean(ob, dist=1e-5):
    """boolean が残す重複頂点・ゼロ長エッジを掃除する。

    これを挟まないと non-manifold のまま次の boolean に入り、EXACT がまるごと
    誤った結果（穴がふさがる・材料が生える）を返すことがある。
    """
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return ob


def boolean(target, cutter, op="DIFFERENCE"):
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    activate(target)
    bpy.ops.object.modifier_apply(modifier="bool")
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def union(a, b):
    boolean(a, b, op="UNION")
    return clean(a)


def cut(a, b):
    boolean(a, b)
    return clean(a)


def non_manifold(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    n = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return n


# ------------------------------------------------------------
# プリミティブ
# ------------------------------------------------------------

def box_range(x0, x1, y0, y1, z0, z1, name):
    bpy.ops.mesh.primitive_cube_add(size=2, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.name = name
    o.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
    activate(o)
    bpy.ops.object.transform_apply(scale=True)
    return o


def cyl_x(r, x0, x1, y, z, name, verts=96):
    """X 軸に沿った円柱。"""
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=abs(x1 - x0), vertices=verts,
                                        location=(0, 0, 0), rotation=(0, math.pi / 2, 0))
    o = bpy.context.active_object
    o.location = ((x0 + x1) / 2, y, z)
    activate(o)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    o.name = name
    return o


def cone_x(r0, r1, x0, x1, y, z, name, verts=64):
    """X 軸に沿った円錐台（-X 端が r0、+X 端が r1）。"""
    bpy.ops.mesh.primitive_cone_add(radius1=r0, radius2=r1, depth=abs(x1 - x0), vertices=verts,
                                    location=(0, 0, 0), rotation=(0, math.pi / 2, 0))
    o = bpy.context.active_object
    o.location = ((x0 + x1) / 2, y, z)
    activate(o)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    o.name = name
    return o


def prism_x(name, poly, x0, x1):
    """(y, z) の閉じた多角形を X 方向へ押し出す。boolean を使わないので確実に多様体。"""
    return _prism(name, [(x0, y, z) for y, z in poly], [(x1, y, z) for y, z in poly])


def prism_z(name, poly, z0, z1):
    """(x, y) の閉じた多角形を Z 方向へ押し出す。"""
    return _prism(name, [(x, y, z0) for x, y in poly], [(x, y, z1) for x, y in poly])


def _prism(name, lo_pts, hi_pts):
    bm = bmesh.new()
    lo = [bm.verts.new(p) for p in lo_pts]
    hi = [bm.verts.new(p) for p in hi_pts]
    n = len(lo_pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ------------------------------------------------------------
# 2D 輪郭
# ------------------------------------------------------------

def hull2_poly(c0, r0, c1, r1, seg=48):
    """2 つの円の凸包の輪郭。半径が違ってよい（テーパした桁になる）。

    円 2 つを UNION すると接線でゼロ長エッジが出るので、輪郭を直に作る。
    """
    (x0, y0), (x1, y1) = c0, c1
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy)
    if d < 1e-9:
        c, r = (c0, max(r0, r1))
        return [(c[0] + r * math.cos(2 * math.pi * i / seg),
                 c[1] + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    if d <= abs(r1 - r0):                      # 片方がもう片方を含む
        c, r = (c0, r0) if r0 > r1 else (c1, r1)
        return [(c[0] + r * math.cos(2 * math.pi * i / seg),
                 c[1] + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]

    base = math.atan2(dy, dx)
    # 外接接線の接点角。半径差ぶんだけ接点が回る
    a = math.acos(max(-1.0, min(1.0, (r0 - r1) / d)))
    pts = []
    for i in range(seg + 1):                   # 円 0 の外側の弧
        t = base + a + (2 * math.pi - 2 * a) * i / seg
        pts.append((x0 + r0 * math.cos(t), y0 + r0 * math.sin(t)))
    for i in range(seg + 1):                   # 円 1 の外側の弧
        t = base - a + (2 * a) * i / seg
        pts.append((x1 + r1 * math.cos(t), y1 + r1 * math.sin(t)))
    return pts


def arc_centers(c0, r_path, a0, a1, n):
    """(a0→a1) の円弧上に n 個の点を等間隔で置く。曲がった桁の節点に使う。"""
    return [(c0[0] + r_path * math.cos(a0 + (a1 - a0) * i / (n - 1)),
             c0[1] + r_path * math.sin(a0 + (a1 - a0) * i / (n - 1))) for i in range(n)]


def _arc(c, r, a0, a1, seg):
    """c を中心に a0 → a1 を反時計回りにたどる点列。"""
    d = (a1 - a0) % (2 * math.pi)
    n = max(2, int(seg * d / (2 * math.pi)) + 2)
    return [(c[0] + r * math.cos(a0 + d * i / (n - 1)),
             c[1] + r * math.sin(a0 + d * i / (n - 1))) for i in range(n)]


def _pt(node, a):
    (cy, cz), r = node
    return (cy + r * math.cos(a), cz + r * math.sin(a))


def _isect(p0, p1, q0, q1):
    """2 直線の交点。平行なら None。"""
    dx1, dy1 = p1[0] - p0[0], p1[1] - p0[1]
    dx2, dy2 = q1[0] - q0[0], q1[1] - q0[1]
    den = dx1 * dy2 - dy1 * dx2
    if abs(den) < 1e-12:
        return None
    t = ((q0[0] - p0[0]) * dy2 - (q0[1] - p0[1]) * dx2) / den
    return (p0[0] + t * dx1, p0[1] + t * dy1)


def _side(nodes, angs, ccw, seg):
    """片側の輪郭を、経路の向きにたどって返す。

    曲がりの外側は円弧でつなぐ。内側は 2 本の接線が交わるので交点を 1 点だけ置く。
    ⚠ ここで接点を 2 つとも置くと輪郭が後戻りして自己交差する。桁がくびれている
    （半径が途中で小さくなる）と必ず起きて、boolean が壊れた結果を返す。
    """
    m = len(angs)
    A = [_pt(nodes[i], angs[i]) for i in range(m)]
    B = [_pt(nodes[i + 1], angs[i]) for i in range(m)]
    out = [A[0]]
    for i in range(1, m):
        d = (angs[i] - angs[i - 1]) % (2 * math.pi)
        outward = (d <= math.pi) if ccw else (d >= math.pi)
        if outward:
            if ccw:
                out += _arc(nodes[i][0], nodes[i][1], angs[i - 1], angs[i], seg)
            else:
                out += list(reversed(_arc(nodes[i][0], nodes[i][1], angs[i], angs[i - 1], seg)))
        else:
            p = _isect(A[i - 1], B[i - 1], A[i], B[i])
            out.append(p if p is not None else B[i - 1])
    out.append(B[m - 1])
    return out


def chain_poly(nodes, seg=64):
    """節点 [(c, r), ...] を数珠つなぎにした形の輪郭を、1 本の多角形として返す。

    節ごとの凸包を UNION でつなぐと、隣り合う節が同じ円の面で接して
    non-manifold のもとになる（前腕で 649 本出た）。輪郭を直に作れば
    prism_x が 1 発で多様体を作る。
    """
    n = len(nodes)
    if n == 1:
        (cy, cz), r = nodes[0]
        return [(cy + r * math.cos(2 * math.pi * i / seg),
                 cz + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]

    base, alpha = [], []
    for (ca, ra), (cb, rb) in zip(nodes, nodes[1:]):
        d = math.hypot(cb[0] - ca[0], cb[1] - ca[1])
        base.append(math.atan2(cb[1] - ca[1], cb[0] - ca[0]))
        alpha.append(math.acos(max(-1.0, min(1.0, (ra - rb) / d))) if d > 1e-12 else math.pi / 2)
    right = [b - a for b, a in zip(base, alpha)]
    left = [b + a for b, a in zip(base, alpha)]

    pts = _side(nodes, right, True, seg)
    pts += _arc(nodes[-1][0], nodes[-1][1], right[-1], left[-1], seg)[1:]      # 先端
    pts += list(reversed(_side(nodes, left, False, seg)))[1:]
    pts += _arc(nodes[0][0], nodes[0][1], left[0], right[0], seg)[1:-1]        # 根元

    out = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-7:
            out.append(p)
    if len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < 1e-7:
        out.pop()
    return out


def poly_self_intersects(poly):
    """輪郭が自分自身と交わっていないか確かめる（boolean へ渡す前の検算）。"""
    n = len(poly)

    def seg_cross(a, b, c, d):
        def o(p, q, r):
            v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
            return 0 if abs(v) < 1e-15 else (1 if v > 0 else -1)
        return (o(a, b, c) != o(a, b, d)) and (o(c, d, a) != o(c, d, b))

    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if seg_cross(a, b, poly[j], poly[(j + 1) % n]):
                return True
    return False


def chain_plate(name, nodes, x0, x1, seg=64):
    """節点を数珠つなぎにした平板。輪郭 1 本を押し出すので必ず多様体。

    自己交差した輪郭を押し出すと、メッシュ自体は non-manifold 0 に見えるのに
    その後の boolean が壊れた結果（体積がほぼ消える）を返す。ここで先に弾く。
    """
    poly = chain_poly(nodes, seg)
    if poly_self_intersects(poly):
        raise ValueError(f"{name}: 輪郭が自己交差している。節点の半径か曲がりを見直すこと "
                         f"（節点 {[(round(c[0]*1000,1), round(c[1]*1000,1), round(r*1000,1)) for c, r in nodes]}）")
    return prism_x(name, poly, x0, x1)


def chain_hull(name, nodes, x0, x1, seg=40):
    """（旧）節点ごとの凸包を UNION でつなぐ。chain_plate を使うこと。"""
    part = None
    for (ca, ra), (cb, rb) in zip(nodes, nodes[1:]):
        seg_ob = prism_x(f"{name}_s", hull2_poly(ca, ra, cb, rb, seg), x0, x1)
        part = seg_ob if part is None else union(part, seg_ob)
    part.name = name
    return clean(part)
