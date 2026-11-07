"""GLB を読み戻し、元の階層と同じ姿勢で動くかを確かめる。

blender --background --python models/robot-hand-soft/verify_glb.py -- <file.glb>
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bpy
from mathutils import Vector

import animate as AN
import model as HM
import params as P

CHECK_FRAMES = [1, 40, 62, 98, 150, 175, 200, 245, 275, 301]
CHECK_PARTS = ["index_tip", "middle_tip", "ring_tip", "pinky_tip", "thumb_tip", "palm"]


def read_json(path):
    with open(path, "rb") as f:
        head = f.read(12)
        assert head[:4] == b"glTF"
        n, kind = struct.unpack("<I4s", f.read(8))
        assert kind == b"JSON"
        return json.loads(f.read(n).decode("utf-8"))


def positions(objs, frames):
    sc = bpy.context.scene
    out = {}
    for fr in frames:
        sc.frame_set(fr)
        bpy.context.view_layer.update()
        out[fr] = {k: objs[k].matrix_world.translation.copy() for k in CHECK_PARTS}
    return out


def main():
    path = sys.argv[sys.argv.index("--") + 1]
    g = read_json(path)
    print("GLB 大きさ", os.path.getsize(path), "ノード", len(g["nodes"]), "メッシュ", len(g["meshes"]),
          "アニメーション", len(g.get("animations", [])), "チャンネル", sum(len(a["channels"]) for a in g.get("animations", [])))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    objs, _, joints = HM.build_hand()
    AN.apply_keys(joints)
    sc.frame_end = 301
    src = positions(objs, CHECK_FRAMES)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = P.FPS  # 読み戻しの時刻→コマの換算に使われる
    bpy.ops.import_scene.gltf(filepath=path)
    sc = bpy.context.scene
    accs = g["accessors"]
    times = [accs[smp["input"]] for smp in g["animations"][0]["samplers"]]
    print("時刻 %.3f〜%.3f 秒" % (min(t["min"][0] for t in times), max(t["max"][0] for t in times)))
    assert len(g.get("animations", [])) == 1, "クリップは 1 本のはず"
    imp = {o.name: o for o in bpy.data.objects}
    missing = [k for k in CHECK_PARTS if k not in imp]
    assert not missing, missing
    dst = positions(imp, CHECK_FRAMES)
    worst = 0.0
    for fr in CHECK_FRAMES:
        for k in CHECK_PARTS:
            worst = max(worst, (src[fr][k] - dst[fr][k]).length)
    moved = max((dst[fr]["index_tip"] - dst[1]["index_tip"]).length for fr in CHECK_FRAMES) * 1000
    loop = max((dst[301][k] - dst[1][k]).length for k in CHECK_PARTS) * 1000
    print(f"元との差 最大 {worst*1000:.3f}mm / 人差し指の先の動き {moved:.1f}mm / コマ 1 と 301 の差 {loop:.3f}mm")
    sys.exit(0 if worst < 1e-4 and moved > 30 and loop < 0.01 else 1)


if __name__ == "__main__":
    main()
