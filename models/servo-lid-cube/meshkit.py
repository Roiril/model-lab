"""STL を直に読むメッシュと、当たり・隙間の判定（verify.py と print_review.py が使う）。Blender の Python で動く。"""
import math
import os
import struct

from mathutils import Vector
from mathutils.bvhtree import BVHTree

RAY_DIR = Vector((0.2113, 0.3547, 0.9108)).normalized()


# ---------------------------------------------------------------------------
# メッシュ
# ---------------------------------------------------------------------------

class Mesh:
    def __init__(self, verts, tris, name):
        self.v = verts
        self.t = tris
        self.name = name

    @staticmethod
    def load(path, name=None):
        raw = open(path, "rb").read()
        n = struct.unpack("<I", raw[80:84])[0]
        idx, verts, tris = {}, [], []
        for i in range(n):
            o = 84 + 50 * i + 12
            f = struct.unpack("<9f", raw[o:o + 36])
            tri = []
            for k in range(3):
                key = (round(f[3 * k], 4), round(f[3 * k + 1], 4), round(f[3 * k + 2], 4))
                if key not in idx:
                    idx[key] = len(verts)
                    verts.append(Vector(key))
                tri.append(idx[key])
            if len(set(tri)) == 3:
                tris.append(tuple(tri))
        return Mesh(verts, tris, name or os.path.basename(path))

    def moved(self, mat, name=None):
        return Mesh([mat @ v for v in self.v], self.t, name or self.name)

    def bvh(self):
        return BVHTree.FromPolygons(self.v, self.t, epsilon=0.0)

    def mass_props(self):
        """体積・重心・慣性テンソル（密度 1、mm 単位）。四面体分解。"""
        vol = 0.0
        c = Vector((0, 0, 0))
        ii = [[0.0] * 3 for _ in range(3)]
        for a, b, d in self.t:
            p, q, r = self.v[a], self.v[b], self.v[d]
            v6 = p.dot(q.cross(r))
            vol += v6 / 6
            c += (p + q + r) * (v6 / 24)
        c /= vol
        # 慣性（重心まわり）: 二次モーメントを四面体ごとに
        sxx = syy = szz = sxy = sxz = syz = 0.0
        for a, b, d in self.t:
            p, q, r = self.v[a] - c, self.v[b] - c, self.v[d] - c
            v6 = p.dot(q.cross(r))
            def m2(i, j):
                return v6 / 120 * (2 * (p[i] * p[j] + q[i] * q[j] + r[i] * r[j])
                                   + p[i] * q[j] + q[i] * p[j] + p[i] * r[j] + r[i] * p[j]
                                   + q[i] * r[j] + r[i] * q[j])
            sxx += m2(0, 0); syy += m2(1, 1); szz += m2(2, 2)
            sxy += m2(0, 1); sxz += m2(0, 2); syz += m2(1, 2)
        ixx = syy + szz
        return dict(volume=vol, com=tuple(c), ixx_com=ixx, second=(sxx, syy, szz, sxy, sxz, syz))


def inside(bvh, p):
    count, o = 0, p.copy()
    for _ in range(80):
        hit = bvh.ray_cast(o, RAY_DIR)
        if hit[0] is None:
            break
        count += 1
        o = hit[0] + RAY_DIR * 1e-4
    return count % 2 == 1


def contact(a, b, depth=True, step=1):
    """a と b の干渉。面の交差の数と、相手の内側に入った頂点の最大の深さ（mm）。"""
    ba, bb = a.bvh(), b.bvh()
    pairs = ba.overlap(bb)
    if not pairs and not depth:
        return dict(hits=0, depth=0.0)
    d = 0.0
    if pairs or depth:
        for m, bv in ((a, bb), (b, ba)):
            for v in m.v[::step]:
                if inside(bv, v):
                    loc = bv.find_nearest(v)
                    if loc[0] is not None:
                        d = max(d, loc[3])
    return dict(hits=len(pairs), depth=round(d, 3))


def clearance(a, b, step=1, cap=30.0):
    """頂点から相手の面までの最小距離（mm）。当たっていなければ隙間の目安。"""
    bb, ba = b.bvh(), a.bvh()
    best = cap
    for m, bv in ((a, bb), (b, ba)):
        for v in m.v[::step]:
            loc = bv.find_nearest(v, best)
            if loc[0] is not None and loc[3] < best:
                best = loc[3]
    return round(best, 3)
