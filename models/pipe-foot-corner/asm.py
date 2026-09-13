"""角一式を組んだ状態の確認用 STL（板 2 枚 + 添え板の版）。

    ./run.sh models/pipe-foot-corner/asm.py  →  exports/pipe_foot_corner_asm.stl

組み方の本体は lib/corner_asm.py。ここでは床側の部品の置き方だけ渡す。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

from blender_utils import clear_scene, EXPORTS_DIR
import corner_asm
from params import PAIR, CORNER, CORNER_OFF, TIE_Z

MC = CORNER_OFF + PAIR.SPAN / 2

clear_scene()
corner_asm.build_asm(PAIR, CORNER, EXPORTS_DIR, "pipe_foot_corner_asm", [
    # 板 A: ローカルは脚が x=±80、3 本目が (0, +FIFTH_OFF)。180° 回して中心を (-MC, 0) へ
    ("pipe_foot_corner_a.stl", 180, -MC, 0.0, 0.0),
    # 板 B: ローカルは脚が x=±80。90° 回して中心を (0, -MC) へ
    ("pipe_foot_corner_b.stl", 90, 0.0, -MC, 0.0),
    # 添え板: ローカルは穴が (0,0) と (TIE_L, 0)。A1 から B1 へ -45°。ひれの上 z=TIE_Z に乗る
    ("pipe_foot_corner_tie.stl", -45, -CORNER_OFF, 0.0, TIE_Z),
])
