"""モデルの静止姿勢の三角形を投影し、参考画像ごとのカメラを IoU が上がる方向へ探す。

py -3.11 models/robot-hand-soft/fit_camera.py <rest.npz> [view ...]
結果は cameras.json。カメラはこのファイルが正本で、描画もここを読む。
"""
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import metrics as MT

CAM_JSON = os.path.join(HERE, "cameras.json")
FIT_SCALE = 0.5
KEYS = ["az", "pitch", "roll", "tx", "tz", "dist", "f"]
STEPS = {"az": 2.0, "pitch": 1.0, "roll": 0.5, "tx": 3.0, "tz": 3.0, "dist": 20.0, "f": 40.0}
INIT = {
    "front":   {"az": 0.0,   "pitch": 0.0, "roll": 0.0, "tx": -7.2, "tz": 119.0, "dist": 400.0, "f": 1780.0},
    "rear":    {"az": 180.0, "pitch": 0.0, "roll": 0.0, "tx": -7.2, "tz": 119.0, "dist": 400.0, "f": 1780.0},
    "oblique": {"az": 145.0, "pitch": 0.0, "roll": 0.0, "tx": -7.2, "tz": 119.0, "dist": 400.0, "f": 1780.0},
}


def camera_axes(c):
    a = np.radians(c["az"])
    p = np.radians(c["pitch"])
    r = np.radians(c["roll"])
    F = np.array([-np.sin(a) * np.cos(p), np.cos(a) * np.cos(p), -np.sin(p)])
    Rt = np.cross(F, [0, 0, 1.0])
    Rt /= np.linalg.norm(Rt)
    Up = np.cross(Rt, F)
    Rt2 = Rt * np.cos(r) + Up * np.sin(r)
    Up2 = -Rt * np.sin(r) + Up * np.cos(r)
    return F, Rt2, Up2


def project(tris, c, size):
    """tris: (N,3,3) mm。カメラは注視点 (tx, 0, tz) から dist 手前。tx はカメラの右方向の平行移動。"""
    F, Rt, Up = camera_axes(c)
    Rt0 = np.cross(F, [0, 0, 1.0])
    Rt0 /= np.linalg.norm(Rt0)
    T = Rt0 * c["tx"] + np.array([0, 0, c["tz"]])
    C = T - F * c["dist"]
    q = tris - C
    z = q @ F
    x = q @ Rt
    y = q @ Up
    s = size / MT.SIZE
    return np.stack([size / 2 + s * c["f"] * x / z, size / 2 - s * c["f"] * y / z], -1)


def raster(tris, c, size):
    pj = project(tris, c, size)
    img = np.zeros((size, size), np.uint8)
    pts = np.round(pj * 16).astype(np.int32)
    for t in pts:
        cv2.fillConvexPoly(img, t, 1, lineType=cv2.LINE_8, shift=4)
    return img.astype(bool)


def fit(tris, ref, c, rounds=5):
    size = int(MT.SIZE * FIT_SCALE)
    best = dict(c)
    bs = MT.iou(raster(tris, best, size), ref)
    steps = dict(STEPS)
    for rd in range(rounds):
        moved = True
        while moved:
            moved = False
            for k in KEYS:
                for sg in (1, -1):
                    while True:
                        t = dict(best)
                        t[k] += sg * steps[k]
                        s = MT.iou(raster(tris, t, size), ref)
                        if s > bs + 1e-5:
                            bs, best = s, t
                            moved = True
                        else:
                            break
        print(f"  round {rd}: iou={bs:.4f}", {k: round(best[k], 2) for k in KEYS}, flush=True)
        steps = {k: v * 0.5 for k, v in steps.items()}
    return best, bs


def main():
    data = np.load(sys.argv[1])
    views = sys.argv[2:] or ["front", "rear", "oblique"]
    tris = np.concatenate([data[k] for k in data.files]) * 1000.0
    print("三角形", len(tris))
    cams = json.load(open(CAM_JSON, encoding="utf-8")) if os.path.exists(CAM_JSON) else {}
    size = int(MT.SIZE * FIT_SCALE)
    for v in views:
        ref = MT.hand_mask(MT.load_rgb(os.path.join(MT.REF_DIR, MT.REFS[v])))
        ref_s = cv2.resize(ref.astype(np.uint8), (size, size), interpolation=cv2.INTER_AREA) > 0
        print(v)
        best, s = fit(tris, ref_s, cams.get(v, INIT[v]))
        cams[v] = {k: float(best[k]) for k in KEYS}
    with open(CAM_JSON + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        json.dump(cams, f, indent=1)
    os.replace(CAM_JSON + ".tmp", CAM_JSON)


if __name__ == "__main__":
    main()
