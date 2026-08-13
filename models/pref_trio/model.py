"""静岡・石川・イタリアの3つを横一列・同サイズで1つのSTLにまとめる。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

import bpy
from blender_utils import clear_scene, export_stl
from pref_utils import build_pref

SIZE = 0.060
THICK = 0.008
GAP = 0.010
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..")

GEO = [
    ("pref_shizuoka", "g_shizuoka"),
    ("pref_ishikawa", "g_ishikawa"),
    ("world_italy", "g_italy"),
]

clear_scene()
objs = []
for folder, name in GEO:
    outline = os.path.join(MODELS_DIR, folder, "outline.json")
    objs.append(build_pref(outline, name, SIZE, THICK))


def bbox(o):
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    return min(xs), max(xs), min(ys), max(ys)


cursor = 0.0
for o in objs:
    xmin, xmax, ymin, ymax = bbox(o)
    w = xmax - xmin
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    o.location.x += cursor + w / 2 - cx
    o.location.y += -cy
    cursor += w + GAP
    o.select_set(True)

print(f"[pref_trio] 3 objects, width = {(cursor-GAP)*1000:.1f} mm")
export_stl("pref_trio")
