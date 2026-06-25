"""horn — サーボホーンの実体ダミー（UI実測値から描く）。

params.py（mm）から namespace を作り add_horn_dummy に渡す。
形が実物に合ったら、その値を servo_core.HORN に焼き込めば全モデルの受けが追従する。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

from types import SimpleNamespace

import bpy  # noqa: F401
from blender_utils import clear_scene, export_stl
from servo_core import add_horn_dummy
from params import *

clear_scene()

MM = 0.001
TYPES = ["cross", "single", "round"]
prof = SimpleNamespace(
    TYPE=TYPES[max(0, min(2, int(round(HORN_TYPE))))],
    ARM_SPAN_X=ARM_SPAN_X * MM, ARM_SPAN_Y=ARM_SPAN_Y * MM,
    ARM_W=ARM_W * MM, HUB_DIA=HUB_DIA * MM,
    THICKNESS=THICKNESS * MM, ROUND_DIA=ROUND_DIA * MM, SCREW_DIA=SCREW_DIA * MM,
)

add_horn_dummy(prof=prof, name="horn", base_z=0.0)

export_stl("horn")
