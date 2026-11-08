"""真横から撮る（厚みの比較用）。指さしの姿勢: 人差し指を伸ばし、ほかの 3 本と親指を曲げる。

blender --background --python models/robot-hand-soft/side_view.py -- --out <png> [--res 1600] [--samples 64]

カメラは親指の側（-X）から +X を向く直交投影。画面の上が手の甲（+Y）、右が指先（+Z）。
参考画像は指先が左なので、比較では左右を反転して並べる。
画素と座標の対応と、人差し指の先と関節 j3 の画素を <png>.json に書く。
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bpy
from mathutils import Matrix, Vector

import animate as AN
import model as HM
import params as P
import studio as ST

W, H = 1600, 1000
ORTHO = 0.400        # 画面の幅 [m]
CENTER = (0.0, 0.135)   # 画面の中心 (Y, Z) [m]


# 参考の写真に合わせた指さしの姿勢。人差し指以外は軽く曲げて下へ垂らす
CURL = {"j3": 45.0, "j2": 55.0, "j1": 30.0}


def pointing_pose():
    q = AN.zero_pose()
    for n in ("middle", "ring", "pinky"):
        for j, v in CURL.items():
            q[f"{n}_{j}"] = v
    return AN.with_thumb(q, P.FIST_THUMB)


def main():
    out = ST._arg("--out", None)
    res = int(ST._arg("--res", W))
    samples = int(ST._arg("--samples", 64))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    st = ST.setup_scene(res, samples)
    sc = bpy.context.scene
    sc.render.resolution_x = res
    sc.render.resolution_y = round(res * H / W)
    st["table"].hide_render = True
    st["wall"].hide_render = True
    bg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[1].default_value = 0.85
    objs, _, joints = HM.build_hand()
    for name, v in pointing_pose().items():
        ob, axis, base = joints[name]
        ob.rotation_euler[axis] = base[axis] + math.radians(v)
    bpy.context.view_layer.update()
    cam = st["cam"]
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ORTHO
    cam.data.sensor_fit = "HORIZONTAL"
    fwd, up = Vector((1, 0, 0)), Vector((0, 1, 0))
    rgt = fwd.cross(up)     # = +Z
    m = Matrix((rgt, up, -fwd)).transposed().to_4x4()
    m.translation = Vector((-1.0, CENTER[0], CENTER[1]))
    cam.matrix_world = m
    st["light"].location = Vector((-0.6, 0.5, 0.3))
    st["light"].rotation_euler = (Vector((0, 0, 0.13)) - st["light"].location).to_track_quat("-Z", "Y").to_euler()
    st["light"].data.energy = 6.0

    def pix(p):
        u = sc.render.resolution_x / 2 + (p.z - CENTER[1]) / ORTHO * sc.render.resolution_x
        v = sc.render.resolution_y / 2 - (p.y - CENTER[0]) / ORTHO * sc.render.resolution_x
        return [round(u, 2), round(v, 2)]

    # 人差し指の先の頂点と、関節 j3 での指の断面の中心
    f = P.FINGERS["index"]
    yc_tip = (P.TIP_FRONT + P.SEG_BACK["tip"]) / 2
    tip = objs["index_tip"].matrix_world @ (Vector((0, yc_tip - P.AXIS_Y, f["hinges"][0])) * P.MM)
    mid_y = (P.SEG_FRONT + P.SEG_BACK["seg1"]) / 2
    j3 = objs["index_seg1"].matrix_world @ (Vector((0, mid_y - P.AXIS_Y, 0)) * P.MM)
    meta = {"px_per_mm": sc.render.resolution_x / (ORTHO * 1000), "index_tip": pix(tip), "index_j3": pix(j3),
            "finger_len_mm": f["hinges"][2], "view": "親指の側から（左右反転前）"}
    ST.render_still(out)
    with open(out + ".json", "w", encoding="utf-8") as fp:
        json.dump(meta, fp, ensure_ascii=False, indent=1)
    print("横から:", out, meta)


if __name__ == "__main__":
    main()
