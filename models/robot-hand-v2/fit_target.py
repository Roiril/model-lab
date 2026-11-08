"""目標の画像（target-a）の目印の点に合うカメラを最小二乗で求めて cameras.json の "target" に書く。

blender --background --python models/robot-hand-v2/fit_target.py
目印は目標の画像（1254px）から手で読んだ点。左右は甲側から見た向き（親指が右）。
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import numpy as np
from mathutils import Vector

import params as P
import studio as ST

# (名前, 3D [mm], 目標の画像の px)
F = P.FINGERS
LANDMARKS = [
    ("小指の先", (F["pinky"]["tip"][0], 0.0, F["pinky"]["tip"][1]), (250, 228)),
    ("薬指の先", (F["ring"]["tip"][0], 0.0, F["ring"]["tip"][1]), (430, 78)),
    ("中指の先", (F["middle"]["tip"][0], 0.0, F["middle"]["tip"][1]), (595, 32)),
    ("人差し指の先", (F["index"]["tip"][0], 0.0, F["index"]["tip"][1]), (760, 110)),
    ("親指の先", (P.THUMB["tip"][0], 0.0, P.THUMB["tip"][1]), (1035, 598)),
    ("手のひらの下の中央", (P.WRIST_X, P.PALM_DEPTH / 2, P.PALM_BOTTOM_Z), (615, 935)),
    ("前腕の甲側の縁", (P.WRIST_X, P.FOREARM_R, P.WRIST_A + P.FOREARM_RIM), (625, 1035)),
    ("前腕の左の輪郭", (P.WRIST_X + P.FOREARM_R, 0.0, P.WRIST_A - 40), (466, 1150)),
    ("前腕の右の輪郭", (P.WRIST_X - P.FOREARM_R, 0.0, P.WRIST_A - 40), (790, 1150)),
]


def project(c, p):
    Fw, Rt, Up, _ = ST.camera_axes(c)
    C = ST.camera_pos(c)
    q = Vector(p) * P.MM - C
    z = q.dot(Fw)
    return 627 + c["f"] * q.dot(Rt) / z, 627 - c["f"] * q.dot(Up) / z


def err(c):
    e = 0.0
    for _, p, (u, v) in LANDMARKS:
        pu, pv = project(c, p)
        e += (pu - u) ** 2 + (pv - v) ** 2
    return e


def fit():
    c = {"az": 178.0, "pitch": 8.0, "roll": 0.0, "tx": 0.0, "tz": 140.0, "dist": 420.0, "f": 1600.0}
    steps = {"az": 2.0, "pitch": 2.0, "roll": 1.0, "tx": 8.0, "tz": 8.0, "f": 100.0}
    for _ in range(400):
        moved = False
        for k, s in steps.items():
            for d in (s, -s):
                t = dict(c)
                t[k] += d
                if err(t) < err(c):
                    c, moved = t, True
        if not moved:
            steps = {k: v / 2 for k, v in steps.items()}
            if max(steps.values()) < 1e-3:
                break
    return c


if __name__ == "__main__":
    c = fit()
    print("カメラ", {k: round(v, 2) for k, v in c.items()})
    for name, p, (u, v) in LANDMARKS:
        pu, pv = project(c, p)
        print(f"  {name}: 目標 ({u},{v}) モデル ({pu:.0f},{pv:.0f}) 差 {math.hypot(pu-u, pv-v):.0f}px")
    path = os.path.join(HERE, "cameras.json")
    cams = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    cams["target"] = c
    with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        json.dump(cams, f, ensure_ascii=False, indent=1)
    os.replace(path + ".tmp", path)
