"""eye — 頭の球くぼみに接着する目玉ボール。

くぼみ半径と同じ真球。底を少し平らにして造形プレートに置いて印刷する。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy  # noqa: F401
from blender_utils import clear_scene, export_stl
from servo_core import add_eye_ball
from params import *

clear_scene()

MM = 0.001
add_eye_ball(EYE_DIA * MM, flat_h=FLAT_H * MM, name="eye")

export_stl("eye")
