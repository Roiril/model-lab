"""mm 単位で Blender の印刷部品を組み立てる 2D / 3D 形状道具。"""
import math

import bmesh
import bpy
from mathutils import Matrix


def circle(c, r, n=64, a0=0.0, a1=360.0, closed=True):
    m = n if closed else n + 1
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(m)]


def hull(points):
    pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def ccw(poly):
    return poly if area(poly) > 0 else poly[::-1]


def triangulate(poly):
    """耳切り。凹んだ輪郭を n-gon で閉じず、蓋を三角形で作る。"""
    poly = ccw(poly)
    idx = list(range(len(poly)))
    tris = []

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def inside(p, a, b, c):
        return cross(a, b, p) >= -1e-12 and cross(b, c, p) >= -1e-12 and cross(c, a, p) >= -1e-12
    guard = 0
    while len(idx) > 3 and guard < 100000:
        guard += 1
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if cross(a, b, c) <= 1e-12:
                continue
            if any(inside(poly[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            raise RuntimeError("triangulation failed")
    tris.append(tuple(idx))
    return poly, tris


def teardrop(c, r, cap, up=1.0, n=48):
    """横穴の輪郭。刷るときの上側に 45° の尖りを付け、cap mm 下で平らに切る。"""
    pts = []
    for i in range(n + 1):
        a = math.radians(45 + 270 * i / n)
        pts.append((r * math.cos(a + math.pi / 2), r * math.sin(a + math.pi / 2)))
    top = r + cap
    half = r * math.sqrt(2) - top
    poly = pts + [(half, top), (-half, top)]
    poly = [(x, y * up) for x, y in poly]
    return [(c[0] + x, c[1] + y) for x, y in ccw(poly)]


def link_obj(bm, name):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def prism(poly, axis, a0, a1, name="prism"):
    """2D 輪郭を軸方向に押し出す。axis='x': (y,z) / 'y': (x,z) / 'z': (x,y)。"""
    poly, tris = triangulate(poly)

    def p3(p, t):
        if axis == "x":
            return (t, p[0], p[1])
        if axis == "y":
            return (p[0], t, p[1])
        return (p[0], p[1], t)
    bm = bmesh.new()
    lo = [bm.verts.new(p3(p, a0)) for p in poly]
    hi = [bm.verts.new(p3(p, a1)) for p in poly]
    for a, b, c in tris:
        bm.faces.new((lo[c], lo[b], lo[a]))
        bm.faces.new((hi[a], hi[b], hi[c]))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link_obj(bm, name)


def box(x0, x1, y0, y1, z0, z1, name="box"):
    return prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "z", z0, z1, name)


def cyl_x(c, r, x0, x1, n=64, name="cyl"):
    return prism(circle(c, r, n), "x", x0, x1, name)


def hull3d(points, name="hull"):
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link_obj(bm, name)


def loft_rings(rings, name):
    """同じ点数の輪（z, [(x,y)...]）を下から順に繋いだ立体。"""
    bm = bmesh.new()
    vs = [[bm.verts.new((p[0], p[1], z)) for p in ring] for z, ring in rings]
    bm.faces.new(vs[0][::-1])
    bm.faces.new(vs[-1])
    for a, b in zip(vs[:-1], vs[1:]):
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link_obj(bm, name)


def clean(ob, dist=1e-4):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def boolean(target, other, op):
    mod = target.modifiers.new("b", "BOOLEAN")
    mod.operation = op
    mod.solver = "EXACT"
    mod.object = other
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(other, do_unlink=True)
    clean(target)
    return target


def union(target, *others):
    for other in others:
        boolean(target, other, "UNION")
    return target


def cut(target, *others):
    for other in others:
        boolean(target, other, "DIFFERENCE")
    return target


def intersect(target, other):
    return boolean(target, other, "INTERSECT")


def nonmanifold(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    n = sum(1 for edge in bm.edges if not edge.is_manifold)
    bm.free()
    return n


def nonmanifold_where(ob, k=4):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    out = [[round(c, 2) for c in (edge.verts[0].co + edge.verts[1].co) / 2]
           for edge in bm.edges if not edge.is_manifold][:k]
    bm.free()
    return out


def volume(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    value = bm.calc_volume(signed=False)
    bm.free()
    return value


def transform(ob, mat):
    ob.data.transform(mat)
    ob.data.update()


def rot_x_about(deg, cy, cz):
    """X 軸（y=cy, z=cz を通る）まわりの回転。+deg で +Y が +Z へ回る。"""
    return (Matrix.Translation((0, cy, cz)) @ Matrix.Rotation(math.radians(deg), 4, "X")
            @ Matrix.Translation((0, -cy, -cz)))


def rrect(half, rho, n=10):
    """中心が原点の角丸正方形の輪郭。"""
    pts = []
    for cx, cy, angle in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        for k in range(n + 1):
            t = math.radians(angle + 90 * k / n)
            pts.append((cx * (half - rho) + rho * math.cos(t), cy * (half - rho) + rho * math.sin(t)))
    return pts
