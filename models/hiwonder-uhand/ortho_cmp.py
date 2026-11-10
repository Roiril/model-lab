"""寸法図（ref/uhand参考資料/02）に ortho.py の正射影を重ねる。

py -3.11 models/hiwonder-uhand/ortho_cmp.py <render_dir> <out_dir> [--mmpx 0.1]
図の縮尺と原点は固定（params.py の冒頭と同じ。位置合わせで動かさない）。
出力:
  cmp_front.png / cmp_side.png   左が寸法図、右がモデル
  ovl_front.png / ovl_side.png   寸法図の線（黒）にモデルの面（薄赤）と縁（赤）を重ねたもの
標準出力に、寸法図の線のうちモデルの縁から 1mm 以内にある割合を出す。
"""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
K = 0.3853                 # 寸法図 02 の mm/px
Z0 = 454.5                 # z = 0 の行
ORG = dict(front=146.5, side=497.3)        # x = 0 / y = 0 の列
FRAME = dict(h0=-60.0, h1=100.0, z0=-5.0, z1=180.0)      # ortho.py と同じ
CROP = dict(front=(-45.0, 92.0, 0.0, 178.0), side=(-42.0, 32.0, 0.0, 178.0))   # 見せる範囲 [mm]
PPM = 5.0                  # 出力の px/mm


def main():
    rdir, out = sys.argv[1], sys.argv[2]
    a = sys.argv
    mmpx = float(a[a.index("--mmpx") + 1]) if "--mmpx" in a else 0.1
    os.makedirs(out, exist_ok=True)
    dwg = Image.open(glob.glob(os.path.join(HERE, "ref", "uhand参考資料", "02_*.png"))[0]).convert("L")
    for view in ("front", "side"):
        h0, h1, z0, z1 = CROP[view]
        size = (round((h1 - h0) * PPM), round((z1 - z0) * PPM))
        # 寸法図を同じ範囲・同じ縮尺に切り出す
        box = (ORG[view] + h0 / K, Z0 - z1 / K, ORG[view] + h1 / K, Z0 - z0 / K)
        d = dwg.transform(size, Image.EXTENT, box, Image.BICUBIC, fillcolor=255)
        # モデル
        r = Image.open(os.path.join(rdir, f"dwg_{view}.png")).convert("RGBA")
        bx = ((h0 - FRAME["h0"]) / mmpx, (FRAME["z1"] - z1) / mmpx, (h1 - FRAME["h0"]) / mmpx, (FRAME["z1"] - z0) / mmpx)
        r = r.transform(size, Image.EXTENT, bx, Image.BICUBIC)
        ra = np.asarray(r).astype(float)
        sil = ra[..., 3] > 128
        white = Image.new("RGBA", size, (255, 255, 255, 255))
        white.alpha_composite(r)
        gray = np.asarray(white.convert("L"))
        edge = gray < 215
        lines = np.asarray(d) < 150
        # 寸法図の線がモデルの縁の近く（1mm）にある割合
        near = np.asarray(Image.fromarray((edge * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * round(PPM) + 1))) > 0
        hit = (lines & near).sum() / max(lines.sum(), 1)
        inside = (lines & sil).sum() / max(lines.sum(), 1)
        print(f"{view}: 図の線のうちモデルの縁から 1mm 以内 {hit:.3f} / モデルの面の内側 {inside:.3f}")
        # 重ね
        o = np.full((size[1], size[0], 3), 255.0)
        o[sil] = (255, 225, 225)
        o[edge] = (230, 40, 40)
        o[lines] = o[lines] * 0.15
        Image.fromarray(o.astype(np.uint8)).save(os.path.join(out, f"ovl_{view}.png"))
        pair = Image.new("RGB", (size[0] * 2 + 10, size[1]), (255, 255, 255))
        pair.paste(d.convert("RGB"), (0, 0))
        pair.paste(white.convert("RGB"), (size[0] + 10, 0))
        pair.save(os.path.join(out, f"cmp_{view}.png"))


main()
