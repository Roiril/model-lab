"""角の床側を 1 枚にまとめた板（H2D 向け、284.7 角）。

    ./run.sh models/pipe-foot-corner-one/model.py

形は lib/corner_plate.build_plate()。分割版（pipe-foot-corner-split）も同じ形を 2 枚に切る。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

from blender_utils import clear_scene, EXPORTS_DIR
import corner_plate
import pair_base
import params

clear_scene()
pair_base.export(corner_plate.build_plate(params, "pipe_foot_corner_one"), EXPORTS_DIR, "pipe_foot_corner_one.stl")
