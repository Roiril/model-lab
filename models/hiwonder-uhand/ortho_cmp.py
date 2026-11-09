"""寸法図（2026-11-10 074006）に ortho.py の正射影を重ねる。

py -3.11 models/hiwonder-uhand/ortho_cmp.py <dwg.png> <render_dir> <out.png> [--mmpx 0.16]
図の縮尺は 174mm の寸法線（y=3 から y=276）から 0.6374 mm/px。
図は正面（x < 230）と側面（x >= 230）に分けて、それぞれレンダーの輪郭と重なりが最大になる位置へずらす。
ずらしたあとの縮尺は固定（合わせるのは位置だけ）。
出力: 左が正面、右が側面。灰色がレンダー、赤が図の線。上に、ずらした量と図から読んだ全高を焼く。
"""
import sys

import numpy as np
from PIL import Image, ImageDraw

DWG_MMPX = 174.0 / (276 - 3)
SPLIT = 230   # 図の正面と側面の境目 [px]
ROWS = (0, 262)   # 図のうちハンド本体の行（下の台座の箱は除く）


def main():
    dwg, rdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
    a = sys.argv
    mmpx = float(a[a.index("--mmpx") + 1]) if "--mmpx" in a else 0.16
    g = Image.open(dwg).convert("L")
    k = DWG_MMPX / mmpx
    panels = []
    for name, (x0, x1) in (("dwg_front", (0, SPLIT)), ("dwg_side", (SPLIT, 430))):
        part = g.crop((x0, ROWS[0], x1, ROWS[1]))
        part = part.resize((round(part.width * k), round(part.height * k)), Image.LANCZOS)
        lines = np.array(part) < 150
        rgba = Image.open(f"{rdir}/{name}.png").convert("RGBA")
        sil = np.array(rgba)[..., 3] > 128
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        bg.alpha_composite(rgba)
        r = np.array(bg.convert("L"))
        # レンダーの縁（輪郭と内部の線）を太らせ、図の線との重なりを数える
        edge = (r < 120)
        from PIL import ImageFilter
        edge_d = np.array(Image.fromarray((edge * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 0
        sil_d = np.array(Image.fromarray((sil * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
        ys, xs = np.nonzero(lines)
        ys_all, xs_all = ys, xs
        ys, xs = ys[::7], xs[::7]
        best = None
        H, W = r.shape
        for dy in range(-60, H - part.height + 60, 8):
            for dx in range(-60, W - part.width + 60, 8):
                yy, xx = ys + dy, xs + dx
                ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
                s = sil_d[yy[ok], xx[ok]].sum() + 0.5 * edge_d[yy[ok], xx[ok]].sum() - 0.5 * (~ok).sum()
                if best is None or s > best[0]:
                    best = (s, dx, dy)
        _, dx, dy = best
        ys, xs = ys_all, xs_all
        for ddy in range(dy - 8, dy + 9, 2):
            for ddx in range(dx - 8, dx + 9, 2):
                yy, xx = ys + ddy, xs + ddx
                ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
                s = sil_d[yy[ok], xx[ok]].sum() + 0.5 * edge_d[yy[ok], xx[ok]].sum() - 0.5 * (~ok).sum()
                if s > best[0]:
                    best = (s, ddx, ddy)
        _, dx, dy = best
        rgb = np.stack([r] * 3, -1).astype(float)
        rgb = np.where(sil[..., None], rgb * 0.8 + 30, 255.0)   # レンダーは薄い灰の面と黒い線
        yy, xx = ys + dy, xs + dx
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
        rgb[yy[ok], xx[ok]] = rgb[yy[ok], xx[ok]] * 0.25 + np.array((230, 0, 0)) * 0.75
        ys0, ys1 = max(0, dy - 20), min(H, dy + part.height + 20)
        xs0, xs1 = max(0, dx - 20), min(W, dx + part.width + 20)
        im = Image.fromarray(rgb.astype(np.uint8))
        sil = sil  # 重なり率は切り抜く前に数える
        hit = sil[yy[ok], xx[ok]].mean()
        ImageDraw.Draw(im).text((8, 8), f"{name}  drawing lines inside render silhouette: {hit:.0%}  shift=({dx},{dy})px",
                                fill=(0, 0, 160))
        panels.append(im.crop((xs0, ys0, xs1, ys1)))
        print(name, "hit", round(float(hit), 3), "shift", dx, dy)
    W = sum(p.width for p in panels)
    sheet = Image.new("RGB", (W, max(p.height for p in panels)), "white")
    x = 0
    for p in panels:
        sheet.paste(p, (x, 0))
        x += p.width
    sheet.save(out)
    print(out)


main()
