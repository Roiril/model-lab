# -*- coding: utf-8 -*-
"""参照画像から、手と駒のシルエット（960x560 の bool 配列）を作る。

py -3.11 tools/uhand_geister_shot/ref_masks.py --ref ref.png --out DIR [--crop 0,0,960,560]
    DIR/ref_hand.npy / DIR/ref_ghost.npy / DIR/ref_mask.png（赤 = 手、青 = 駒）

手: 暗い画素（輝度 120 未満）から配線の橙を除き、x < 190 のコネクタを外して閉じる。
駒: 枠 (640..740, 405..560) の中で、背景（sRGB 200 の灰）と手のどちらでもない画素。
参照が別の画像なら、閾値と枠をその画像に合わせて直す。
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def close(m, k):
    im = Image.fromarray((m * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))) > 127


def main():
    out = arg("--out")
    os.makedirs(out, exist_ok=True)
    im = Image.open(arg("--ref")).convert("RGB")
    crop = arg("--crop")
    if crop:
        im = im.crop(tuple(int(v) for v in crop.split(",")))
    if im.size != (960, 560):
        raise SystemExit(f"参照は 960x560 で渡す（今は {im.size}）")
    a = np.asarray(im).astype(int)
    lum = a.mean(axis=2)
    hand = (lum < 120) & ~(a[..., 0] - a[..., 2] > 60)
    hand[:, :190] = False
    hand = close(hand, 7)
    nb = np.abs(a - 200).max(axis=2) > 6
    ghost = np.zeros_like(hand)
    ghost[405:560, 640:740] = nb[405:560, 640:740] & ~hand[405:560, 640:740]
    ghost = close(ghost, 5)
    np.save(os.path.join(out, "ref_hand.npy"), hand)
    np.save(os.path.join(out, "ref_ghost.npy"), ghost)
    m = np.zeros(a.shape, np.uint8)
    m[hand] = (255, 0, 0)
    m[ghost] = (0, 128, 255)
    Image.fromarray(m).save(os.path.join(out, "ref_mask.png"))
    if crop:
        im.save(os.path.join(out, "ref.png"))
    print(f"[mask] 手 {int(hand.sum())} 画素 / 駒 {int(ghost.sum())} 画素 → {out}")


main()
