# -*- coding: utf-8 -*-
"""盤面写真から正方形テクスチャを生成する（PIL。Blender 不要）。

board_photo.jpg（実物を真上から撮影）の周囲に写り込んだ黒布背景を
輝度しきい値で切り落とし、正方形にリサイズして exports/geister/tex/ に出す。

実行: python models/geister/gen_texture.py
"""
import os
import numpy as np
from PIL import Image

from params import CROP_THR, TEX_SIZE

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "geister"))
TEX = os.path.join(OUT, "tex")
os.makedirs(TEX, exist_ok=True)

im = Image.open(os.path.join(HERE, "board_photo.jpg")).convert("RGB")
a = np.asarray(im.convert("L")).astype(np.float32)
h, w = a.shape

# 行/列の平均輝度が盤面レベルに上がる位置で切り出し（背景の黒布を除去）
rows = a.mean(axis=1)
cols = a.mean(axis=0)
top = next(i for i in range(h) if rows[i] > CROP_THR)
bot = next(i for i in range(h - 1, -1, -1) if rows[i] > CROP_THR)
left = next(i for i in range(w) if cols[i] > CROP_THR)
right = next(i for i in range(w - 1, -1, -1) if cols[i] > CROP_THR)

im = im.crop((left, top, right + 1, bot + 1))
im = im.resize((TEX_SIZE, TEX_SIZE), Image.LANCZOS)
path = os.path.join(TEX, "board.jpg")
im.save(path, quality=90)
print("crop=(%d,%d,%d,%d) -> %dx%d  %s" % (left, top, right, bot, TEX_SIZE, TEX_SIZE, path))
