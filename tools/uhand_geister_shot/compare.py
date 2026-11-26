# -*- coding: utf-8 -*-
"""描いた絵を左右反転して参照と並べ、シルエットの IoU を測る。

py -3.11 tools/uhand_geister_shot/compare.py --ref ref.png --ref-hand ref_hand.npy --ref-ghost ref_ghost.npy
    --shot shot.png --sil sil.png --out DIR

DIR/final.png       反転した描画（参照と同じ向き。左手に見える）
DIR/side.jpg        参照と描画の横並び
DIR/overlay.png     シルエットの重ね（緑 = 参照の手 / 赤 = 描画の手 / 黄 = 一致 / 青 = 参照の駒 / 白 = 駒の一致）
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def iou(a, b):
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 0.0


def main():
    out = arg("--out")
    os.makedirs(out, exist_ok=True)
    paths = [arg(k) for k in ("--ref", "--ref-hand", "--ref-ghost", "--shot", "--sil")]
    missing = [p for p in paths if not p or not os.path.exists(p)]
    if missing:
        raise SystemExit(f"無いファイル: {missing}")
    ref = Image.open(paths[0]).convert("RGB")
    W, H = ref.size
    rh, rg = np.load(paths[1]), np.load(paths[2])
    shot = ImageOps.mirror(Image.open(paths[3]).convert("RGB"))
    shot.save(os.path.join(out, "final.png"))
    sil = np.asarray(ImageOps.mirror(Image.open(paths[4]).convert("RGB")).resize((W, H), Image.NEAREST)).astype(int)
    sh = (sil[..., 0] > 127) & (sil[..., 2] < 127)
    sg = (sil[..., 2] > 127) & (sil[..., 0] < 127)
    ih, ig = iou(sh, rh), iou(sg, rg)
    # 駒の中心と大きさ
    def box(m):
        ys, xs = np.nonzero(m)
        return xs.min(), xs.max(), ys.min(), ys.max()
    gb, rb = box(sg), box(rg)
    print(f"[cmp] 手 IoU {ih:.3f} / 駒 IoU {ig:.3f}")
    print(f"[cmp] 駒の枠 参照 x{rb[0]}-{rb[1]} y{rb[2]}-{rb[3]} / 描画 x{gb[0]}-{gb[1]} y{gb[2]}-{gb[3]}")
    ov = np.zeros((H, W, 3), np.uint8)
    ov[rh, 1] = 150
    ov[sh, 0] = 255
    ov[rg] = (0, 0, 255)
    ov[sg & rg] = (255, 255, 255)
    oi = Image.fromarray(ov)
    ImageDraw.Draw(oi).text((8, 8), f"hand IoU {ih:.3f}  ghost IoU {ig:.3f}", fill=(255, 255, 255))
    oi.save(os.path.join(out, "overlay.png"))
    sw = shot.resize((W, H), Image.LANCZOS)
    side = Image.new("RGB", (W * 2, H), (255, 255, 255))
    side.paste(ref, (0, 0))
    side.paste(sw, (W, 0))
    d = ImageDraw.Draw(side)
    d.text((8, 8), "reference", fill=(200, 0, 0))
    d.text((W + 8, 8), f"render  hand IoU {ih:.3f} / ghost IoU {ig:.3f}", fill=(200, 0, 0))
    side.save(os.path.join(out, "side.jpg"), quality=90)
    print("[cmp]", os.path.join(out, "side.jpg"))


main()
