"""書き出したSTLが印刷に使えるか確かめる（./run.sh models/laptop-stand-flow/verify.py）。"""
import os

import bmesh
import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def check(path, expect_parts):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=path)
    obj = bpy.context.object
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    non_manifold = [e for e in bm.edges if not e.is_manifold]
    # 連結成分
    seen, parts = set(), 0
    for v in bm.verts:
        if v in seen:
            continue
        parts += 1
        stack = [v]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(e.other_vert(cur) for e in cur.link_edges)
    volume = bm.calc_volume(signed=True)
    zs = [v.co.z for v in bm.verts]
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    name = os.path.basename(path)
    print(f"{name}: verts={len(bm.verts)} faces={len(bm.faces)} non_manifold_edges={len(non_manifold)} "
          f"parts={parts}(expect {expect_parts}) volume={volume / 1000.0:.1f}cm3 (signed, must be >0)")
    print(f"  bbox mm: X {min(xs):.1f}..{max(xs):.1f}  Y {min(ys):.1f}..{max(ys):.1f}  Z {min(zs):.1f}..{max(zs):.1f}")
    ok = not non_manifold and parts == expect_parts and volume > 0 and abs(min(zs)) < 0.05
    print("  RESULT:", "OK" if ok else "NG")
    bm.free()


check(os.path.join(ROOT, "exports", "laptop-stand-flow-unit.stl"), 1)
check(os.path.join(ROOT, "exports", "laptop-stand-flow.stl"), 2)
