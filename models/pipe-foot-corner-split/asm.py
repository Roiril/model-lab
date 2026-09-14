"""角一式を組んだ状態の確認用 STL（2 枚に切った板の版）。

    ./run.sh models/pipe-foot-corner-split/asm.py  →  exports/pipe_foot_corner_split_asm.stl
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

from blender_utils import clear_scene, EXPORTS_DIR
import corner_asm
from params import PAIR, CORNER

clear_scene()
# 2 枚とも世界座標のまま作ってあるので、そのまま置く
corner_asm.build_asm(PAIR, CORNER, EXPORTS_DIR, "pipe_foot_corner_split_asm", [
    ("pipe_foot_corner_split_a.stl", 0, 0.0, 0.0, 0.0),
    ("pipe_foot_corner_split_b.stl", 0, 0.0, 0.0, 0.0),
])
