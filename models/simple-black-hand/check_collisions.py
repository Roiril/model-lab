"""部品同士が貫通していないかを、開いた手から握りまでの姿勢で調べる。

blender --background --python models/simple-black-hand/check_collisions.py
各姿勢で部品ごとに BVH を作り、三角形同士の交差を数える。交差があれば exit 1。
除外: 指の根元の節と親指の根元は手のひらへ入り込む（固定。手のひらの開口の暗がりも同じ）。
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bpy
from mathutils.bvhtree import BVHTree

import model as HM
import params as P
from blender_utils import clear_scene


def set_pose(joints, t):
    """t=0 で開いた手、t=1 で握り（params の FIST_*）。"""
    for name, ang in P.FIST_FINGER.items():
        for j, v in ang.items():
            ob, ax, base = joints[f"{name}_{j}"]
            r = list(base)
            r[ax] += math.radians(v * t)
            ob.rotation_euler = r
    for j, v in P.FIST_THUMB.items():
        ob, ax, base = joints[f"thumb_{j}"]
        r = list(base)
        r[ax] += math.radians(v * t)
        ob.rotation_euler = r


def excluded(a, b):
    pair = {a, b}
    if "palm" in pair or "palm_shade" in pair:
        other = (pair - {"palm", "palm_shade"} or {"palm"}).pop()
        return other.endswith("_root") or other in ("thumb_shade", "palm", "palm_shade")
    return "thumb_shade" in pair and "thumb_root" in pair


def main():
    clear_scene()
    objs, _, joints = HM.build_hand()
    names = sorted(objs)
    bad = 0
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        set_pose(joints, t)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        trees = {}
        for n in names:
            ob = objs[n]
            me = ob.data
            mw = ob.matrix_world
            trees[n] = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [p.vertices[:] for p in me.polygons])
        hits = []
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if excluded(a, b):
                    continue
                k = len(trees[a].overlap(trees[b]))
                if k:
                    hits.append((a, b, k))
        print(f"[collide] t={t:.2f} 交差 {len(hits)} 組", hits)
        bad += len(hits)
    print("[collide] 合計", bad)
    sys.exit(1 if bad else 0)


main()
