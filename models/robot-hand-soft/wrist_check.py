"""手首の太さを横と正面で測る。py -3.11 で動かす。

py -3.11 models/robot-hand-soft/wrist_check.py <side.png>

side_view.py が撮る直交投影の 2 枚（<side.png> と <side>-front.png）を使う。
- 手のひらの下端: 手のひらの下端より PALM_ABOVE 上の高さ
- 手首: 前腕の口の縁の上面から「手のひらの下端」の測定位置までを 0.25mm ごとに見た、いちばん細い所
- 前腕の付け根: 前腕の殻の上端より ARM_BELOW 下の高さ
判定: 手首のいちばん細い所 >= 0.8 × (手のひらの下端と前腕の付け根の太い方)。横と正面の両方。
太さは、その高さの列（横）または行（正面）で、手の画素が続くいちばん長い区間。GAP_PX 以下の明るい切れ目はまたぐ。
計器の校正: 幅の分かっている帯を描いた合成画像を測る。
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P

THRESH = 150
CLOSE_PX = 5             # 1mm（4px）以下の部品のすき間は、縦横どちらの向きでも閉じてから測る
PALM_BOTTOM_Z = 49.3     # 手のひらの下端の高さ [mm]（外形の最も下の点）
PALM_ABOVE = 9.0
ARM_BELOW = 10.0
RATIO = 0.8


def mask_of(path):
    g = np.array(Image.open(path).convert("L")).astype(int)
    m = (g < THRESH).astype(np.uint8)
    h, w = m.shape
    ff = np.pad(1 - m, 1, constant_values=1).astype(np.uint8)
    seed = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, seed, (0, 0), 2)
    m = (ff[1:-1, 1:-1] != 2).astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((CLOSE_PX, CLOSE_PX), np.uint8)) > 0


def longest_run(line):
    idx = np.where(line)[0]
    if len(idx) == 0:
        return 0
    best, start, prev = 0, idx[0], idx[0]
    for i in idx[1:]:
        if i - prev > 1:
            best = max(best, prev - start + 1)
            start = i
        prev = i
    return max(best, prev - start + 1)


def _band(gap):
    img = np.full((200, 400), 220, np.uint8)
    img[50:150, 100:300] = 20
    img[:, 180:180 + gap] = 220       # 縦の切れ目
    img[98:98 + gap, :] = 220         # 横の切れ目
    tmp = os.path.join(HERE, "_wrist_cal.png")
    Image.fromarray(img).save(tmp)
    m = mask_of(tmp)
    os.remove(tmp)
    return longest_run(m[120]), longest_run(m[:, 140])


def calibrate():
    """幅 200px・高さ 100px の帯。4px の切れ目は閉じて 200/100、6px の切れ目は閉じない（200 / 100 より短く出る）。"""
    w4, h4 = _band(4)
    w6, h6 = _band(6)
    ok = w4 == 200 and h4 == 100 and w6 < 200 and h6 < 100
    return ok, f"校正: 4px の切れ目つきの帯を 幅 {w4} / 高さ {h4}px（期待 200 / 100）、6px なら 幅 {w6} / 高さ {h6}px（切れ目で分かれるはず）"


def main():
    side = sys.argv[1]
    front = side.replace(".png", "-front.png")
    sm, fm = mask_of(side), mask_of(front)
    smeta = json.load(open(side + ".json", encoding="utf-8"))
    fmeta = json.load(open(front + ".json", encoding="utf-8"))
    ppm = smeta["px_per_mm"]

    def side_t(z):      # 横: 列 u の太さ [mm]
        u = int(round(smeta["size"][0] / 2 + (z - smeta["center_z_mm"]) * ppm))
        return longest_run(sm[:, u]) / ppm

    def front_t(z):     # 正面: 行 v の幅 [mm]
        v = int(round(fmeta["size"][1] / 2 - (z - fmeta["center_z_mm"]) * ppm))
        return longest_run(fm[v]) / ppm

    f_top = P.CUP_TOP
    c_bot = P.ARM_TOP
    z_palm = PALM_BOTTOM_Z + PALM_ABOVE
    z_arm = c_bot - ARM_BELOW
    zs = np.arange(f_top, z_palm + 0.01, 0.25)
    ok, msg = calibrate()
    log = [msg]
    res = {}
    for name, fn in (("横（奥行き）", side_t), ("正面（幅）", front_t)):
        palm, arm = fn(z_palm), fn(z_arm)
        prof = [(float(z), fn(z)) for z in zs]
        zmin, tmin = min(prof, key=lambda q: q[1])
        need = RATIO * max(palm, arm)
        good = tmin >= need
        ok &= good
        log.append(f"{name}: 手のひらの下端 {palm:.1f}mm（z={z_palm:.1f}）/ 手首のいちばん細い所 {tmin:.1f}mm（z={zmin:.1f}）"
                   f" / 前腕の付け根 {arm:.1f}mm（z={z_arm:.1f}）→ 比 {tmin / max(palm, arm):.2f}（下限 {RATIO}）" + ("" if good else " ← 細すぎる"))
        res[name] = {"palm": palm, "wrist_min": tmin, "wrist_min_z": zmin, "arm": arm, "ratio": tmin / max(palm, arm),
                     "profile": [(round(z, 2), round(t, 2)) for z, t in prof[::4]]}
    print("\n".join(log))
    with open(side.replace(".png", "-wrist.json"), "w", encoding="utf-8") as fp:
        json.dump({"log": log, "result": res}, fp, ensure_ascii=False, indent=1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
