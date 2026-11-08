"""静止画を描く。目標と同じ構図（target）、横（side）、手首の寄り（wrist）、正面・真後ろ・斜め後ろ。

blender --background --python models/robot-hand-v2/render_views.py -- [--views target,side,wrist,front,rear,oblique]
    [--out DIR] [--res 1254] [--samples 96] [--pose wrist=20,wrist_dev=8]
target は cameras.json（fit_target.py が書く）。他は部品の外接箱から画角を決める。前腕は画面の下の外へ出す。
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

import model as HM
import params as P
import studio as ST

RENDER_DIR = r"G:\マイドライブ\shubie\renders\robot-hand-v2"
# 視点: (方位, 見下ろす角度, 画面に入れる部品, 余白の割合, 上下の位置の補正)
VIEWS = {
    "front": (0.0, 6.0, "hand", 0.06),
    "rear": (180.0, 6.0, "hand", 0.06),
    "oblique": (140.0, 14.0, "hand", 0.06),
    "side": (90.0, 0.0, "hand_wrist", 0.05),
    "wrist": (125.0, 12.0, "wrist", 0.10),
}
WRIST_PARTS = ("wrist_yoke", "wrist_hub", "forearm_lip")


def part_points(objs, which):
    bpy.context.view_layer.update()
    pts = []
    for name, ob in objs.items():
        if name == "forearm":
            continue
        if which == "wrist" and name not in WRIST_PARTS:
            continue
        mw = ob.matrix_world
        me = ob.data
        pts += [mw @ v.co for v in list(me.vertices)[::7]]
    if which in ("hand_wrist", "wrist"):
        # 前腕の口のまわりまで入れる
        A = P.WRIST_A * P.MM
        r = P.FOREARM_R * P.MM
        for i in range(24):
            a = 2 * math.pi * i / 24
            pts.append(Vector((P.WRIST_X * P.MM + r * math.cos(a), r * math.sin(a), A - (0.012 if which == "wrist" else 0.0))))
    return pts


def fit_camera(pts, az, pitch, margin, dist=520.0, res=1254):
    c = {"az": az, "pitch": pitch, "roll": 0.0, "tx": 0.0, "tz": 100.0, "dist": dist, "f": 1500.0}
    for _ in range(8):
        F, Rt, Up, _ = ST.camera_axes(c)
        C = ST.camera_pos(c)
        xs = [(p - C).dot(Rt) / (p - C).dot(F) for p in pts]
        ys = [(p - C).dot(Up) / (p - C).dot(F) for p in pts]
        c["tx"] += (min(xs) + max(xs)) / 2 * c["dist"]
        c["tz"] += (min(ys) + max(ys)) / 2 * c["dist"]
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    c["f"] = res * (1 - 2 * margin) / span
    return c


def place(st, c, light_key):
    ST.place_view(st, {"v": c}, "v", row=627, light_key=light_key)
    # 壁は手の 35cm 後ろ。カメラに正対させる
    F, Rt, Up, _ = ST.camera_axes(c)
    C = ST.camera_pos(c)
    st["wall"].matrix_world = (Matrix.Translation(C + F * (c["dist"] * P.MM + 0.35))
                               @ Matrix((Rt, Up, -F)).transposed().to_4x4())


def set_pose(joints, spec):
    for item in filter(None, spec.split(",")):
        k, v = item.split("=")
        ob, axis, base = joints[k]
        ob.rotation_euler[axis] = base[axis] + math.radians(float(v))


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    res = int(ST._arg("--res", 1254))
    samples = int(ST._arg("--samples", 96))
    out = ST._arg("--out", RENDER_DIR)
    views = ST._arg("--views", "target,side,wrist,front,rear,oblique").split(",")
    suffix = ST._arg("--suffix", "")
    os.makedirs(out, exist_ok=True)
    st = ST.setup_scene(res, samples)
    objs, _, joints = HM.build_hand()
    set_pose(joints, ST._arg("--pose", ""))
    cams = ST.load_cameras()
    for v in views:
        if v == "target":
            c = cams["target"]
        else:
            az, pitch, which, margin = VIEWS[v]
            c = fit_camera(part_points(objs, which), az, pitch, margin)
        place(st, c, v if v in ST.LIGHT_ENERGY else "rear")
        ST.render_still(os.path.join(out, f"model-{v}{suffix}.png"))
        print("描画:", v, {k: round(x, 1) for k, x in c.items()}, flush=True)
