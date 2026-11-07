"""全コマの部品同士の貫通量を測る。

blender --background --python models/robot-hand-soft/check_collisions.py -- [--out <json>] [--calibrate-only]

方法: 部品ごとに局所座標の格子で「殻の内側の点の、殻の面までの距離」を求める（列ごとの光線で内外を判定）。
各コマで相手の部品の表面点を局所座標へ移し、格子を線形補間して深さを読む。A→B と B→A の大きい方が貫通量。
格子の間隔が読み取りの下限になる。
除外: 指の根元の節と手のひら（固定で、根元が手のひらへ ROOT_BELOW_PALM 入り込む）。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import animate as AN
import model as HM
import params as P
import studio as ST

PITCH = 0.0006      # 格子 [m]（0.6mm）
PITCH_BIG = 0.0008  # 手のひらと台座
SAMPLE_AREA = 0.25e-6   # 表面点 1 個あたりの面積 [m2]


class Part:
    def __init__(self, name, subs, pitch):
        self.name = name
        self.subs = subs
        allv = np.array([p for v, _ in subs for p in v])
        self.lo = allv.min(0) - 2 * pitch
        self.hi = allv.max(0) + 2 * pitch
        self.center = (self.lo + self.hi) / 2
        self.radius = float(np.linalg.norm(self.hi - self.center))
        self.pitch = pitch
        self._grid()
        self._points()

    def _grid(self):
        p = self.pitch
        nx, ny, nz = np.ceil((self.hi - self.lo) / p).astype(int) + 1
        self.n = (nx, ny, nz)
        depth = np.zeros((nx, ny, nz), np.float32)
        for v, f in self.subs:
            bvh = BVHTree.FromPolygons(v, f, all_triangles=False)
            va = np.array(v)
            i0 = np.maximum(np.floor((va.min(0) - self.lo) / p).astype(int), 0)
            i1 = np.minimum(np.ceil((va.max(0) - self.lo) / p).astype(int), np.array(self.n) - 1)
            ymin = self.lo[1] - p
            for ix in range(i0[0], i1[0] + 1):
                x = self.lo[0] + ix * p
                for iz in range(i0[2], i1[2] + 1):
                    z = self.lo[2] + iz * p
                    # 列に沿って面との交点を集める
                    hits = []
                    pos = Vector((x + 1.3e-6, ymin, z + 0.7e-6))
                    d = Vector((0, 1, 0))
                    for _ in range(40):
                        loc, _n, _i, dist = bvh.ray_cast(pos, d)
                        if loc is None:
                            break
                        hits.append(loc.y)
                        pos = Vector((pos.x, loc.y + 1e-7, pos.z))
                    if len(hits) < 2:
                        continue
                    for a, b in zip(hits[0::2], hits[1::2]):
                        j0 = int(np.ceil((a - self.lo[1]) / p))
                        j1 = int(np.floor((b - self.lo[1]) / p))
                        for iy in range(max(j0, 0), min(j1, self.n[1] - 1) + 1):
                            q = Vector((x, self.lo[1] + iy * p, z))
                            near = bvh.find_nearest(q)
                            if near[0] is not None:
                                depth[ix, iy, iz] = max(depth[ix, iy, iz], near[3])
        self.depth = depth

    def _points(self):
        rng = np.random.default_rng(abs(hash(self.name)) % (2 ** 31))
        pts = []
        for v, f in self.subs:
            va = np.array(v)
            tri = []
            for q in f:
                for k in range(1, len(q) - 1):
                    tri.append((q[0], q[k], q[k + 1]))
            tri = np.array(tri)
            a, b, c = va[tri[:, 0]], va[tri[:, 1]], va[tri[:, 2]]
            area = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2
            n = max(int(area.sum() / SAMPLE_AREA), 50)
            idx = rng.choice(len(tri), n, p=area / area.sum())
            u, w = rng.random((2, n))
            flip = u + w > 1
            u[flip], w[flip] = 1 - u[flip], 1 - w[flip]
            pts.append(a[idx] + (b[idx] - a[idx]) * u[:, None] + (c[idx] - a[idx]) * w[:, None])
            pts.append(va)
        self.points = np.vstack(pts)

    def sample(self, q):
        """局所座標の点の深さ（線形補間）。外は 0。"""
        g = (q - self.lo) / self.pitch
        i = np.floor(g).astype(int)
        keep = ((i >= 0).all(1)) & (i[:, 0] < self.n[0] - 1) & (i[:, 1] < self.n[1] - 1) & (i[:, 2] < self.n[2] - 1)
        if not keep.any():
            return 0.0
        i = i[keep]
        f = g[keep] - i
        D = self.depth
        out = 0.0
        vals = np.zeros(len(i), np.float32)
        for dx in (0, 1):
            wx = f[:, 0] if dx else 1 - f[:, 0]
            for dy in (0, 1):
                wy = f[:, 1] if dy else 1 - f[:, 1]
                for dz in (0, 1):
                    wz = f[:, 2] if dz else 1 - f[:, 2]
                    vals += wx * wy * wz * D[i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz]
        return float(vals.max())


def excluded(a, b):
    pair = {a, b}
    if pair in ({"palm", "palm_shade"}, {"thumb_root", "thumb_shade"}):
        return True   # 同じ剛体の暗い板。親の中へ入り込んでいる
    if "palm" in pair:
        other = (pair - {"palm"}).pop() if len(pair) == 2 else ""
        if other.endswith("_root") and not other.startswith("thumb"):
            return True
    return False


def pair_depth(A, B, Ma, Mb):
    Mba = np.linalg.inv(Mb) @ Ma
    Mab = np.linalg.inv(Mba)
    d1 = B.sample((Mba[:3, :3] @ A.points.T).T + Mba[:3, 3])
    d2 = A.sample((Mab[:3, :3] @ B.points.T).T + Mab[:3, 3])
    return max(d1, d2)


def world_mats(objs):
    bpy.context.view_layer.update()
    return {k: np.array(o.matrix_world) for k, o in objs.items()}


def scan(parts, objs, frames, sc, names=None):
    names = names or list(parts)
    pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:] if not excluded(a, b)]
    worst = {}
    per_frame = {}
    for fr in frames:
        sc.frame_set(fr)
        M = world_mats(objs)
        cent = {k: M[k][:3, :3] @ parts[k].center + M[k][:3, 3] for k in names}
        mx = 0.0
        for a, b in pairs:
            if np.linalg.norm(cent[a] - cent[b]) > parts[a].radius + parts[b].radius:
                continue
            d = pair_depth(parts[a], parts[b], M[a], M[b])
            if d > 0:
                key = f"{a} / {b}"
                if d > worst.get(key, (0,))[0]:
                    worst[key] = (d, fr)
            mx = max(mx, d)
        per_frame[fr] = mx
    return worst, per_frame


def calibrate(log):
    """既知の量で計器を確かめる: 2.00mm 重なった箱、0.50mm 離れた箱、指を手のひらへ押し込んだ姿勢。"""
    a = [HM.rbox(0, 20, 0, 20, 0, 20, 0.0, seg=1)]
    mm = P.MM
    box = lambda s: [([(x * mm, y * mm, z * mm) for x, y, z in v], f) for v, f in s]
    A = Part("calA", box(a), PITCH)
    B = Part("calB", box(a), PITCH)
    I = np.eye(4)
    res = {}
    for label, off, expect in (("2.00mm 重なる", 18.0, 2.0), ("0.50mm 離れる", 20.5, 0.0), ("4.00mm 重なる", 16.0, 4.0)):
        Mb = I.copy()
        Mb[0, 3] = off * mm
        d = pair_depth(A, B, I, Mb) * 1000
        res[label] = d
        log.append(f"校正 箱 {label}: 測定 {d:.2f}mm（期待 {expect:.2f}mm）")
    ok = abs(res["2.00mm 重なる"] - 2) < 0.7 and res["0.50mm 離れる"] < 0.05 and abs(res["4.00mm 重なる"] - 4) < 0.7
    return ok


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    objs, subs, joints = HM.build_hand()
    log = []
    cal = calibrate(log)
    log.append("校正 箱 " + ("合格" if cal else "不合格"))
    print("\n".join(log), flush=True)
    parts = {}
    for k, s in subs.items():
        parts[k] = Part(k, s, PITCH_BIG if k in ("palm", "base") else PITCH)
    print("格子を作った", {k: int((p.depth > 0).sum()) for k, p in parts.items()}, flush=True)
    # 姿勢で確かめる: 指を手の甲側へ 60 度（通常の範囲外）。手のひらに当たらないはず / 親指を手のひらへ押し込む
    sc.frame_set(1)
    ob, ax, base = joints["index_j3"]
    # 悪い姿勢の校正: 親指の根元を 40 度振ると開口の縁に当たるはず
    ob2, ax2, base2 = joints["thumb_cmc"]
    keep = tuple(ob2.rotation_euler)
    ob2.rotation_euler[ax2] = base2[ax2] + np.radians(55)
    M = world_mats(objs)
    bad = pair_depth(parts["thumb_seg1"], parts["palm"], M["thumb_seg1"], M["palm"]) * 1000
    ob2.rotation_euler = keep
    log.append(f"校正 姿勢: 親指を開口の外へ 55 度振る → 親指と手のひらの貫通 {bad:.2f}mm（0 より大きいはず）")
    M = world_mats(objs)
    fs, fe = AN.apply_keys(joints)
    frames = list(range(fs, fe + 1))
    worst, per_frame = scan(parts, objs, frames, sc)
    ordered = sorted(worst.items(), key=lambda kv: -kv[1][0])
    maxd = ordered[0][1][0] * 1000 if ordered else 0.0
    log.append(f"全 {len(frames)} コマの最大貫通 {maxd:.2f}mm（格子 {PITCH*1000:.1f}mm、手のひらと台座は {PITCH_BIG*1000:.1f}mm）")
    for k, (d, fr) in ordered[:12]:
        log.append(f"  {k}: {d*1000:.2f}mm（コマ {fr}）")
    log.append("除外: 指 4 本の根元の節と手のひら（固定。根元が %.1fmm 入り込む）/ 手のひらと開口の奥の暗い輪 / 親指の根元と裏の暗い円板（どちらも同じ剛体）" % P.ROOT_BELOW_PALM)
    text = "\n".join(log)
    print(text, flush=True)
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out + ".tmp", "w", encoding="utf-8", newline="\n") as f:
            json.dump({"log": log, "max_mm": maxd, "pairs": {k: [round(d * 1000, 3), fr] for k, (d, fr) in ordered},
                       "per_frame_mm": {str(k): round(v * 1000, 3) for k, v in per_frame.items()}}, f, ensure_ascii=False, indent=0)
        os.replace(out + ".tmp", out)


if __name__ == "__main__":
    main()
