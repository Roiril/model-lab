"""Dimensions and independent closed contours. Lengths are metres."""
MODEL_NAME = "laptop-stand-sculpted"
# CATEGORY: ノートPCスタンド
CATEGORY = "ノートPCスタンド"
PAIR_SPACING = 0.200  # 左右の中心間隔 200mm
RAIL_HALF_WIDTH = 0.012  # 上面の半幅 12mm
RAIL_HALF_THICKNESS = 0.0025  # 上面の厚みの半分 2.5mm
RAIL_HEIGHT = 0.145  # PCを置く高さ 145mm
RAIL_START = 0.043  # 上面の後端 43mm
RAIL_END = 0.270000  # 上面の前端 270mm
LIP_HEIGHT = 0.006  # 前端の立ち上がり 6mm
GRID = 0.0005  # 計算間隔 0.5mm
POISSON_SHAPE_SCALE = 0.000010  # 曲面の丸み 10mm²
BODY_HALF_WIDTH = 0.01175  # 胴体の基本半幅 11.75mm
FOOT_EXTRA_HALF_WIDTH = 0.00875  # 足の半幅の追加 8.75mm
SHOULDER_EXTRA_HALF_WIDTH = 0.007  # 肩の半幅の追加 7mm
FOOT_BLEND_HEIGHT = 0.02625  # 足の広がりを移す高さ 26.25mm
REAR_FOOT_RATIO = 0.275  # 後足の広がりの比率 0.275
PROFILE_MID_SHIFT = -0.00825  # 中央の前後補正 -8.25mm
PROFILE_SHOULDER_SHIFT = 0.008  # 肩の前後補正 8mm
PROFILE_WINDOW_SHIFT = -0.00125  # 穴付近の前後補正 -1.25mm
PROFILE_WINDOW_LIFT = 0.004  # 穴付近の高さ補正 4mm
INNER_Y_OFFSET = -0.005  # 穴の前後位置補正 -5mm
INNER_Z_OFFSET = -0.002  # 穴の高さ補正 -2mm

# Periodic cubic B-spline control polygons. Metres.
OUTER = [
    (0.024000, 0.143625),
    (0.031250, 0.131375),
    (0.052000, 0.114125),
    (0.076000, 0.097375),
    (0.096250, 0.074187),
    (0.092500, 0.060000),
    (0.066000, 0.038937),
    (0.019250, 0.021500),
    (-0.024500, 0.002250),
    (-0.024938, -0.006000),
    (0.039375, -0.006000),
    (0.124563, -0.006000),
    (0.219250, -0.006000),
    (0.249500, -0.006000),
    (0.241750, 0.007938),
    (0.201937, 0.030750),
    (0.165312, 0.053437),
    (0.123625, 0.077937),
    (0.086813, 0.101063),
    (0.055000, 0.117000),
    (0.050000, 0.134000),
    (0.077000, 0.140000),
]

INNER = [
    (0.102297, 0.084063),
    (0.102422, 0.082719),
    (0.104109, 0.080687),
    (0.104938, 0.078250),
    (0.103125, 0.073359),
    (0.098688, 0.063188),
    (0.093531, 0.048219),
    (0.092469, 0.033000),
    (0.100078, 0.022109),
    (0.115672, 0.016375),
    (0.132953, 0.014312),
    (0.145734, 0.014875),
    (0.152500, 0.017719),
    (0.154266, 0.022344),
    (0.153328, 0.028844),
    (0.150797, 0.038281),
    (0.143266, 0.050344),
    (0.130437, 0.062594),
    (0.118422, 0.072406),
    (0.110859, 0.078875),
    (0.106641, 0.082563),
    (0.103969, 0.084125),
]

# The viewer supplies overrides through the shared project helper.
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'lib'))
from param_override import apply_overrides
apply_overrides(globals())
