"""Redmi Pad SE 11 インチ用スタンドを生成する。

側面の輪郭（profile.py）を X 方向へ並べた輪で押し出す。左右の端の数 mm では輪郭を
内側へずらして縁を丸める（机に接する辺はずらさないので、下の縁は直角のまま）。
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bpy
import bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

from blender_utils import clear_scene, export_stl
import params as P
import stand_profile as prof

MM = 0.001


def _cap_triangles(poly2d):
    cap = [Vector((a, b, 0.0)) for a, b in poly2d]
    return tessellate_polygon([cap])


def loft(name, rings, scale=MM):
    """rings: [(x, [(y, z), ...]), ...] 同じ点数の輪を X 順に繋いだ閉じたメッシュ。"""
    count = len(rings[0][1])
    bm = bmesh.new()
    loops = [[bm.verts.new((x * scale, y * scale, z * scale)) for y, z in pts] for x, pts in rings]
    for a, b in zip(loops, loops[1:]):
        for i in range(count):
            j = (i + 1) % count
            bm.faces.new((a[i], a[j], b[j], b[i]))
    for loop, pts, flip in ((loops[0], rings[0][1], True), (loops[-1], rings[-1][1], False)):
        for tri in _cap_triangles(pts):
            ids = list(reversed(tri)) if flip else list(tri)
            bm.faces.new([loop[i] for i in ids])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def clean(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-7)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()


def metrics(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    tiny = sum(1 for f in bm.faces if f.calc_area() < 1e-12)
    volume = bm.calc_volume(signed=True)
    seen, comps = set(), 0
    for v in bm.verts:
        if v.index in seen:
            continue
        comps += 1
        stack = [v]
        while stack:
            cur = stack.pop()
            if cur.index in seen:
                continue
            seen.add(cur.index)
            stack.extend(e.other_vert(cur) for e in cur.link_edges)
    bm.free()
    xs = [v.co for v in obj.data.vertices]
    lo = [min(c[i] for c in xs) for i in range(3)]
    hi = [max(c[i] for c in xs) for i in range(3)]
    return dict(non_manifold=non_manifold, zero_area=tiny, components=comps,
                volume_cm3=volume * 1e6, size_mm=[(hi[i] - lo[i]) * 1000 for i in range(3)],
                min_mm=[v * 1000 for v in lo], max_mm=[v * 1000 for v in hi])


def taper(obj):
    """高さに比例して左右をすぼめる。頂部で TOP_WIDTH_MM になる。"""
    height = max(v.co.z for v in obj.data.vertices)
    k = (1.0 - P.TOP_WIDTH_MM / P.WIDTH_MM) / height
    for v in obj.data.vertices:
        v.co.x *= 1.0 - k * v.co.z
    obj.data.update()


def build():
    base = prof.outline()
    rings = [(x, prof.offset(base, d)) for x, d in prof.side_rings()]
    stand = loft("Redmi Pad stand", rings)
    taper(stand)
    clean(stand)
    for poly in stand.data.polygons:
        poly.use_smooth = False
    return stand


def main():
    clear_scene()
    stand = build()
    m = metrics(stand)
    print("STAND_METRICS", m)
    if m["non_manifold"] or m["components"] != 1 or m["zero_area"]:
        raise RuntimeError(f"bad mesh: {m}")
    export_stl(P.MODEL_NAME, only=[stand])
    os.makedirs(os.path.join(HERE, "../../exports", P.MODEL_NAME), exist_ok=True)
    export_stl(f"{P.MODEL_NAME}/print", only=[stand])


main()
