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


HAND_CUT = {"front": 940, "oblique": 925, "rear": 940}
MAX_ROLL = 0.3        # 机の縁が傾かない範囲 [deg]
TOP_MARGIN = 0.022    # 上端の余白の下限
HAND_FLOOR = {"front": 0.90, "oblique": 0.853, "rear": 0.90}


def score(tris, ref, c, view, size):
    """手だけの IoU を下限つきで守りながら、台座を含む全体の IoU を上げる。"""
    m = raster(tris, c, size)
    cut = HAND_CUT[view] * size // MT.SIZE
    hand = MT.iou(ref[:cut], m[:cut])
    whole = MT.iou(ref, m)
    ys = np.where(m.any(1))[0]
    s = 0.5 * hand + 0.5 * whole
    s -= 5 * max(HAND_FLOOR[view] - hand, 0)
    s -= 5 * max(TOP_MARGIN - ys.min() / size, 0)
    s -= 0.2 * max(abs(c["roll"]) - MAX_ROLL, 0)
    # 手の範囲の中心がずれないようにする（指の長さの差は両端へ分ける）
    xs = np.where(m[:cut].any(0))[0]
    xr = np.where(ref[:cut].any(0))[0]
    s -= 2 * max(abs((xs.min() + xs.max()) - (xr.min() + xr.max())) / (2 * size) - 0.008, 0)
    return s


def fit(tris, ref, c, view, rounds=4):
    size = int(MT.SIZE * FIT_SCALE)
    best = dict(c)
    bs = score(tris, ref, best, view, size)
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
                        x = score(tris, ref, t, view, size)
                        if x > bs + 1e-5:
                            bs, best = x, t
                            moved = True
                        else:
                            break
        print(f"  round {rd}: score={bs:.4f}", {k: round(best[k], 2) for k in KEYS}, flush=True)
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
        c0 = dict(cams.get(v, INIT[v]))
        c0["roll"] = max(min(c0["roll"], MAX_ROLL), -MAX_ROLL)
        seeds = [dict(c0, az=a) for a in (c0["az"], 142.0, 147.0)] if v == "oblique" else [c0]
        results = [fit(tris, ref_s, q, v) for q in seeds]
        best, s = max(results, key=lambda r: r[1])
        cams[v] = {k: float(best[k]) for k in KEYS}
    with open(CAM_JSON + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        json.dump(cams, f, indent=1)
    os.replace(CAM_JSON + ".tmp", CAM_JSON)


if __name__ == "__main__":
    main()
