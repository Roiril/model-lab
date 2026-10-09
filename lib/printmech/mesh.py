"""mm 単位の STL メッシュと、当たり、隙間、質量特性の判定。Blender の Python で動く。"""
import os
import struct

from mathutils import Vector
from mathutils.bvhtree import BVHTree

RAY_DIR = Vector((0.2113, 0.3547, 0.9108)).normalized()


class Mesh:
    def __init__(self, verts, tris, name):
        self.v = verts
        self.t = tris
        self.name = name
        self._bounds = (tuple(min(vertex[axis] for vertex in verts) for axis in range(3)),
                        tuple(max(vertex[axis] for vertex in verts) for axis in range(3)))

    @staticmethod
    def load(path, name=None):
        with open(path, "rb") as fh:
            raw = fh.read()
        n = struct.unpack("<I", raw[80:84])[0]
        idx, verts, tris = {}, [], []
        for i in range(n):
            offset = 84 + 50 * i + 12
            face = struct.unpack("<9f", raw[offset:offset + 36])
            tri = []
            for k in range(3):
                key = (round(face[3 * k], 4), round(face[3 * k + 1], 4), round(face[3 * k + 2], 4))
                if key not in idx:
                    idx[key] = len(verts)
                    verts.append(Vector(key))
                tri.append(idx[key])
            if len(set(tri)) == 3:
                tris.append(tuple(tri))
        return Mesh(verts, tris, name or os.path.basename(path))

    def moved(self, mat, name=None):
        return Mesh([mat @ vertex for vertex in self.v], self.t, name or self.name)

    def bvh(self):
        return BVHTree.FromPolygons(self.v, self.t, epsilon=0.0)

    def bounds(self):
        """軸に平行な外接箱を ``((min xyz), (max xyz))`` で返す。単位は mm。"""
        return self._bounds

    def contains(self, point, bvh=None, tolerance=1e-6):
        """外接箱で明らかな外点を除いてから、点が閉じたメッシュ内かを調べる。"""
        lower, upper = self.bounds()
        if any(point[axis] < lower[axis] - tolerance or point[axis] > upper[axis] + tolerance
               for axis in range(3)):
            return False
        return inside(bvh or self.bvh(), point)

    def mass_props(self):
        """体積・重心・慣性テンソル（密度 1、mm 単位）。四面体分解。"""
        vol = 0.0
        center = Vector((0, 0, 0))
        for a, b, d in self.t:
            p, q, r = self.v[a], self.v[b], self.v[d]
            v6 = p.dot(q.cross(r))
            vol += v6 / 6
            center += (p + q + r) * (v6 / 24)
        center /= vol
        sxx = syy = szz = sxy = sxz = syz = 0.0
        for a, b, d in self.t:
            p, q, r = self.v[a] - center, self.v[b] - center, self.v[d] - center
            v6 = p.dot(q.cross(r))

            def m2(i, j):
                return v6 / 120 * (2 * (p[i] * p[j] + q[i] * q[j] + r[i] * r[j])
                                   + p[i] * q[j] + q[i] * p[j] + p[i] * r[j] + r[i] * p[j]
                                   + q[i] * r[j] + r[i] * q[j])
            sxx += m2(0, 0)
            syy += m2(1, 1)
            szz += m2(2, 2)
            sxy += m2(0, 1)
            sxz += m2(0, 2)
            syz += m2(1, 2)
        ixx = syy + szz
        return dict(volume=vol, com=tuple(center), ixx_com=ixx,
                    second=(sxx, syy, szz, sxy, sxz, syz))


def inside(bvh, point):
    count, origin = 0, point.copy()
    for _ in range(80):
        hit = bvh.ray_cast(origin, RAY_DIR)
        if hit[0] is None:
            break
        count += 1
        origin = hit[0] + RAY_DIR * 1e-4
    return count % 2 == 1


def contact(a, b, depth=True, step=1):
    """a と b の干渉。面の交差数と、内側に入った頂点の最大深さを mm で返す。"""
    ba, bb = a.bvh(), b.bvh()
    pairs = ba.overlap(bb)
    if not pairs and not depth:
        return dict(hits=0, depth=0.0)
    max_depth = 0.0
    if pairs or depth:
        for mesh, bvh in ((a, bb), (b, ba)):
            for vertex in mesh.v[::step]:
                if inside(bvh, vertex):
                    nearest = bvh.find_nearest(vertex)
                    if nearest[0] is not None:
                        max_depth = max(max_depth, nearest[3])
    return dict(hits=len(pairs), depth=round(max_depth, 3))


def clearance(a, b, step=1, cap=30.0):
    """頂点から相手の面までの最小距離を mm で返す。"""
    bb, ba = b.bvh(), a.bvh()
    best = cap
    for mesh, bvh in ((a, bb), (b, ba)):
        for vertex in mesh.v[::step]:
            nearest = bvh.find_nearest(vertex, best)
            if nearest[0] is not None and nearest[3] < best:
                best = nearest[3]
    return round(best, 3)
