import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

from blender_utils import clear_scene, export_stl
from pref_utils import build_pref, log_bbox
from params import TARGET_SIZE, THICKNESS

clear_scene()
outline = os.path.join(os.path.dirname(__file__), "outline.json")
obj = build_pref(outline, "pref_ishikawa", TARGET_SIZE, THICKNESS)
log_bbox(obj, "pref_ishikawa")
export_stl("pref_ishikawa")
