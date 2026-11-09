"""写真と、同じカメラで描いたレンダーを 1 枚に並べる。

py -3.11 models/hiwonder-uhand/overlay.py <render_dir> <out_dir>

- render_views.py --fit で描いた servo / front / back を、写真（servo と back は左右反転）と並べる
- 左から 写真 / レンダー / 写真の上にレンダーの輪郭（赤）
- 目印点（points/<view>.json）の写真上の位置を緑、レンダーで同じ点が来るはずの位置を写真側にも重ねる
- 写真やレンダーが 1 枚でも欠けたら組まずに止める
"""
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWS = ("servo", "front", "back")


def load(path):
    if not os.path.exists(path):
        sys.exit(f"無い: {path}")
    return cv2.imread(path, cv2.IMREAD_COLOR)


def label(img, text):
    cv2.rectangle(img, (0, 0), (img.shape[1], 34), (255, 255, 255), -1)
    cv2.putText(img, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
    return img


def main():
    rdir, odir = sys.argv[1], sys.argv[2]
    os.makedirs(odir, exist_ok=True)
    for v in VIEWS:
        pts = json.load(open(os.path.join(HERE, "points", f"{v}.json"), encoding="utf-8"))
        photo = load(os.path.join(HERE, "ref", f"ref_{v}.png"))
        if pts.get("mirror"):
            photo = cv2.flip(photo, 1)
        rend = load(os.path.join(rdir, f"{v}.png"))
        if rend.shape[:2] != photo.shape[:2]:
            sys.exit(f"{v}: 大きさが違う 写真 {photo.shape[:2]} レンダー {rend.shape[:2]}")
        edges = cv2.Canny(cv2.GaussianBlur(cv2.cvtColor(rend, cv2.COLOR_BGR2GRAY), (3, 3), 0), 40, 110)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8))
        ov = (photo * 0.75 + 255 * 0.25).astype(np.uint8)
        ov[edges > 0] = (0, 0, 230)
        for name, _, (u, v_) in pts["points"]:
            cv2.circle(ov, (int(u), int(v_)), 5, (0, 170, 0), 2)
        row = np.hstack([label(photo.copy(), f"{v}: photo"), label(rend.copy(), "render (same camera)"),
                         label(ov, "photo + render edges (red), landmarks (green)")])
        cv2.imwrite(os.path.join(odir, f"overlay_{v}.png"), row)
        print("[overlay]", os.path.join(odir, f"overlay_{v}.png"))


main()
