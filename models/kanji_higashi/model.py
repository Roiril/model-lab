import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

from blender_utils import clear_scene, export_stl
from kanji_utils import build_kanji, log_bbox
from params import CHAR, TARGET_SIZE, THICKNESS

clear_scene()
obj = build_kanji(CHAR, "kanji_higashi", TARGET_SIZE, THICKNESS)
log_bbox(obj, "kanji_higashi")
export_stl("kanji_higashi")
