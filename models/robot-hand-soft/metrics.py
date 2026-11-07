"""手の輪郭を画像から取る計器と IoU。py -3.11 で動かす（Blender は使わない）。

同じ関数を参考画像とモデルの描画の両方へ通す。校正は compare.py の calibrate()。
"""
import numpy as np
import cv2
from PIL import Image

REF_DIR = r"G:\マイドライブ\shubie\design-study\2026-11-07-robot-hand\final"
RENDER_DIR = r"G:\マイドライブ\shubie\renders\robot-hand-soft"
REFS = {
    "front": "robot-hand-noscrew.png",
    "oblique": "robot-hand-rear-oblique.png",
    "rear": "robot-hand-rear.png",
}
SIZE = 1254
# 彩度の低い暗い画素 = 手。壁は明るく、机は彩度が高いので落ちる。
V_MAX = 105
S_MAX = 0.28


def load_rgb(path):
    return np.array(Image.open(path).convert("RGB"))


def hand_mask(rgb):
    """背景を除いた手の輪郭。内側のハイライトは穴埋めで塞ぐ。"""
    a = rgb.astype(float)
    v = a.max(2)
    s = (v - a.min(2)) / np.maximum(v, 1)
    m = ((v < V_MAX) & (s < S_MAX)).astype(np.uint8)
    # 外とつながった背景だけを背景とする
    h, w = m.shape
    ff = (1 - m).astype(np.uint8)
    pad = np.pad(ff, 1, constant_values=1)
    seed = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(pad, seed, (0, 0), 2)
    bg = pad[1:-1, 1:-1] == 2
    return ~bg


def iou(a, b):
    i = np.logical_and(a, b).sum()
    u = np.logical_or(a, b).sum()
    return float(i) / max(float(u), 1.0)
