"""写真とレンダーの黒い部分の輪郭（シルエット）を抜き出し、位置と倍率を合わせて重ねる。

py -3.11 models/hiwonder-uhand/silhouette.py <render.png> <ref.png> <out.png>

- 写真: 明るい背景に黒い部品。輝度 < PHOTO_T を部品とみなす（銀色の部品は落ちる）
- レンダー: 白い背景。輝度 < RENDER_T を部品とみなす（レンダーも同じ閾値帯で銀色が落ちるよう揃える）
- 倍率と平行移動を総当たりで探して IoU が最大になる重ね方を出す
- 出力: 赤 = 写真だけ、青 = レンダーだけ、黒 = 両方。左上に IoU を焼く
- 写真の左端の配線と下端の台座は IGNORE で採点から外す
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PHOTO_T = 80
RENDER_T = 80
H = 220            # 探索用に縮める高さ
# 採点から外す写真上の範囲（0..1 の比率）。左端の配線、下端の台座、右端の人の指
IGNORE = [(0.0, 0.62, 0.12, 0.80), (0.0, 0.93, 1.0, 1.0), (0.93, 0.0, 1.0, 0.6)]


def mask(path, t, blur=0):
    im = Image.open(path).convert("L")
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im) < t


def bbox(m):
    ys, xs = np.nonzero(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def resize(m, w, h):
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)) > 127


def main():
    rp, pp, out = sys.argv[1:4]
    P = mask(pp, PHOTO_T, blur=1)
    R = mask(rp, RENDER_T)
    ph, pw = P.shape
    s0 = H / ph
    Ps = resize(P, round(pw * s0), H)
    ign = np.zeros_like(Ps)
    for x0, y0, x1, y1 in IGNORE:
        ign[round(y0 * H):round(y1 * H), round(x0 * Ps.shape[1]):round(x1 * Ps.shape[1])] = True
    # レンダーの黒の外接矩形の高さを写真の黒の外接矩形の高さに合わせた倍率を中心に探す
    rx0, ry0, rx1, ry1 = bbox(R)
    px0, py0, px1, py1 = bbox(Ps & ~ign)
    base = (py1 - py0) / (ry1 - ry0)
    best = (-1, None)
    for k in np.linspace(0.85, 1.15, 13):
        sc = base * k
        Rs = resize(R, max(1, round(R.shape[1] * sc)), max(1, round(R.shape[0] * sc)))
        bx0, by0, bx1, by1 = bbox(Rs)
        for dy in range(-12, 13, 2):
            for dx in range(-14, 15, 2):
                ox, oy = px0 - bx0 + dx, py0 - by0 + dy
                C = np.zeros_like(Ps)
                ys, xs = np.nonzero(Rs)
                ys2, xs2 = ys + oy, xs + ox
                ok = (ys2 >= 0) & (ys2 < C.shape[0]) & (xs2 >= 0) & (xs2 < C.shape[1])
                C[ys2[ok], xs2[ok]] = True
                a, b = Ps & ~ign, C & ~ign
                iou = (a & b).sum() / max(1, (a | b).sum())
                if iou > best[0]:
                    best = (iou, C, k, dx, dy)
    iou, C, k, dx, dy = best
    a, b = Ps, C
    img = np.full(a.shape + (3,), 255, np.uint8)
    img[a & ~b] = (230, 40, 40)
    img[b & ~a] = (40, 120, 230)
    img[a & b] = (30, 30, 30)
    img[ign & ~(a | b)] = (225, 225, 225)
    o = Image.fromarray(img).resize((Ps.shape[1] * 3, H * 3), Image.NEAREST)
    d = ImageDraw.Draw(o)
    d.text((6, 6), f"IoU {iou:.3f}  red=photo only  blue=render only  black=both  (scale x{k:.2f} dx{dx} dy{dy})",
           fill=(0, 0, 0))
    o.save(out)
    print(f"IoU={iou:.3f} scale={k:.2f} dx={dx} dy={dy} -> {out}")


main()
