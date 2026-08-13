"""13モデルを横一列・等間隔・同サイズで1つのSTLにまとめる。

各モデルの長辺を SIZE に統一し、X方向に GAP 間隔で並べる。
底面 z=0、各オブジェクトの中心を Y=0 に揃える。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

import bpy
from blender_utils import clear_scene, export_stl
from kanji_utils import build_kanji
from pref_utils import build_pref

SIZE = 0.060       # 全モデル共通の長辺 60mm
THICK = 0.008      # 厚み 8mm
GAP = 0.010        # オブジェクト間の隙間 10mm

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..")

KANJI = [
    ("耳", "k_mimi"), ("田", "k_ta"), ("本", "k_hon"), ("車", "k_kuruma"),
    ("生", "k_sei"), ("女", "k_onna"), ("男", "k_otoko"),
]
GEO = [
    ("pref_shizuoka", "g_shizuoka"), ("pref_ishikawa", "g_ishikawa"),
    ("pref_gifu", "g_gifu"), ("world_chile", "g_chile"),
    ("world_italy", "g_italy"), ("world_vatican", "g_vatican"),
]

clear_scene()

objs = []
for ch, name in KANJI:
    objs.append(build_kanji(ch, name, SIZE, THICK))
for folder, name in GEO:
    outline = os.path.join(MODELS_DIR, folder, "outline.json")
    objs.append(build_pref(outline, name, SIZE, THICK))


def bbox(o):
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    return min(xs), max(xs), min(ys), max(ys)


ROWS = 2
per_row = -(-len(objs) // ROWS)   # 切り上げ → 上段7・下段6
row_pitch = SIZE + GAP            # 行間（同サイズなので SIZE 基準で十分）

max_w = 0.0
for r in range(ROWS):
    chunk = objs[r * per_row:(r + 1) * per_row]
    cursor = 0.0
    for o in chunk:
        xmin, xmax, ymin, ymax = bbox(o)
        w = xmax - xmin
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        o.location.x += cursor + w / 2 - cx     # 左端を cursor に
        # 上の行ほど Y を大きく（r=0 が上段）
        o.location.y += (ROWS - 1 - r) * row_pitch - cy
        cursor += w + GAP
    max_w = max(max_w, cursor - GAP)

# 全体を選択して export（全オブジェクト出力）
for o in objs:
    o.select_set(True)

print(f"[all_lineup] {len(objs)} objects, {ROWS} rows, "
      f"width = {max_w*1000:.1f} mm, height = {(ROWS*row_pitch-GAP)*1000:.1f} mm")
export_stl("all_lineup")
