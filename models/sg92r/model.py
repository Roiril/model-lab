"""sg92r — SG92R 実寸ダミー（実測値入力UIから直接描く）。

params.py の各寸法（UIで実測上書き可）から namespace を作り、add_servo_dummy に渡す。
本体底が z=0 に来るように立てて出力する。
ここで形を実物に合わせ込んだら、その値を servo_core.SG92R に焼き込んで全体へ反映する。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

from types import SimpleNamespace

import bpy  # noqa: F401
from blender_utils import clear_scene, export_stl
from servo_core import add_servo_dummy
from params import *

clear_scene()

# params は mm。ここで m に変換する
MM = 0.001
bl, bw, bh = BODY_L * MM, BODY_W * MM, BODY_H * MM
fl, fw, ft = FLANGE_L * MM, FLANGE_W * MM, FLANGE_T * MM
ffb = FLANGE_FROM_BOTTOM * MM
boss_h, shaft_h = BOSS_H * MM, SHAFT_H * MM
sac = boss_h + shaft_h  # ケース上面〜軸先端 = 2円柱の合計

# UI実測値（m換算）から派生値込みのプロファイルを構築
prof = SimpleNamespace(
    BODY_L=bl, BODY_W=bw, BODY_H=bh,
    SHAFT_OFFSET=SHAFT_OFFSET * MM,
    FLANGE_L=fl, FLANGE_W=fw, FLANGE_T=ft,
    FLANGE_FROM_BOTTOM=ffb,
    SCREW_SPACING=SCREW_SPACING * MM,
    TAB_HOLE_DIA=TAB_HOLE_DIA * MM,
    BOSS_DIA=BOSS_DIA * MM, BOSS_H=boss_h,
    SHAFT_DIA=SHAFT_DIA * MM, SHAFT_H=shaft_h,
    SHAFT_ABOVE_CASE=sac,
    NUB_ABOVE_DECK=bh - ffb,
    SHAFT_ABOVE_DECK=(bh - ffb) + sac,
)

# 本体底を z=0 に（flange_top_z=None で自動）
add_servo_dummy(flange_top_z=None, name="sg92r", clr=DUMMY_CLR * MM, prof=prof)

export_stl("sg92r")
