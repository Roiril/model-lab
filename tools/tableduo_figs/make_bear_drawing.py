# -*- coding: utf-8 -*-
"""「あと6画のくま」のパッドに載せる絵を作る。まる役（赤）のだ円 1 つと丸 2 つ、線役（緑）の直線 2 本と折れ線 1 本の 6 画。

py -3.11 tools/tableduo_figs/make_bear_drawing.py OUT.png
"""
import math
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

PX = 8  # 1mm あたりの画素（描いてから半分に縮める）
W, H = 210 * PX, 297 * PX
RED, GREEN = (226, 96, 88), (38, 150, 138)
rng = random.Random(6)
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)


def stroke(pts, col, width_mm=4.4):
    w = int(width_mm * PX)
    pts = [(x * PX, y * PX) for x, y in pts]
    d.line(pts, fill=col + (255,), width=w, joint="curve")
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=col + (255,))


def loop(cx, cy, rx, ry, start=-100, over=22, wob=0.035):
    """手で描いた丸。少しゆがませ、終わりを始まりより少し行き過ぎさせる。"""
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    pts = []
    n = 90
    for i in range(n + 1):
        a = math.radians(start + (360 + over) * i / n)
        k = 1 + wob * math.sin(2 * a + ph[0]) + wob * 0.6 * math.sin(3 * a + ph[1]) - 0.03 * i / n
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


def line(a, b, bow=0.0):
    pts = []
    for i in range(21):
        t = i / 20
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t + bow * math.sin(math.pi * t)
        pts.append((x, y))
    return pts


# 画像の上がパッドの奥。人の席から見て正立する
stroke(loop(105, 160, 52, 44), RED)            # 顔（だ円）
stroke(loop(62, 108, 19, 19, start=40), RED)   # 左耳
stroke(loop(148, 108, 19, 19, start=160), RED)  # 右耳
stroke(line((80, 150), (94, 151), bow=-1.5), GREEN)    # 左目
stroke(line((116, 151), (130, 149), bow=-1.5), GREEN)  # 右目
stroke(line((93, 176), (105, 186)) + line((105, 186), (118, 175)), GREEN)  # 口（1 折）
im = im.resize((W // 2, H // 2), Image.LANCZOS)
im.save(sys.argv[1])
print("wrote", sys.argv[1], im.size)
