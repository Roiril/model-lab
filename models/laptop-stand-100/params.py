"""100 mm高の水平ノートPCスタンド用寸法。"""

MODEL_NAME = "laptop-stand-100"
CATEGORY = "ノートPCスタンド"
# CATEGORY: ノートPCスタンド

LAPTOP_WIDTH = 0.400  # 400 mm
LAPTOP_DEPTH = 0.330  # 330 mm
LAPTOP_BASE_THICKNESS = 0.025  # 25 mm（参考表示）
LOAD_MASS_KG = 4.0  # kg

BODY_HEIGHT = 0.098  # 98 mm
FRAME_DEPTH = 0.245  # 245 mm
FRAME_WIDTH = 0.026  # 26 mm
TOP_BEAM = 0.016  # 16 mm
BOTTOM_BEAM = 0.007  # 7 mm
BASE_THICKNESS = BOTTOM_BEAM  # 7 mm（底梁厚の参照名）
END_COLUMN = 0.018  # 18 mm
OUTER_R = 0.005  # 5 mm
INNER_R = 0.008  # 8 mm
SIDE_CHAMFER = 0.0008  # 0.8 mm
RAIL_CENTER = 0.160  # 160 mm（左右中心間は320 mm）
PAD_THICKNESS = 0.001  # 1 mm
PAD_WIDTH = 0.024  # 24 mm
PAD_LENGTH = 0.045  # 45 mm
PAD_FRONT_Y = 0.008  # 8 mm（前パッドはY=8..53 mm）
PAD_REAR_Y = 0.192  # 192 mm（後パッドはY=192..237 mm）

ROUND_SEGMENTS = 128  # 円1周あたりの分割数
CLEANUP_DISTANCE = 0.0000001  # 0.0001 mm

try:
    from param_override import apply_overrides
    apply_overrides(globals())
except ImportError:
    pass

BASE_THICKNESS = BOTTOM_BEAM


def validate():
    import math
    values = (LAPTOP_WIDTH, LAPTOP_DEPTH, LAPTOP_BASE_THICKNESS, LOAD_MASS_KG,
              BODY_HEIGHT, FRAME_DEPTH, FRAME_WIDTH, TOP_BEAM, BOTTOM_BEAM,
              END_COLUMN, OUTER_R, INNER_R, SIDE_CHAMFER, RAIL_CENTER,
              PAD_THICKNESS, PAD_WIDTH, PAD_LENGTH, CLEANUP_DISTANCE)
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError('Dimensions and loads must be finite positive numbers')
    if min(TOP_BEAM, BOTTOM_BEAM, END_COLUMN) <= 2 * SIDE_CHAMFER:
        raise ValueError('Sections must be thicker than the side chamfers')
    if RAIL_CENTER <= FRAME_WIDTH / 2:
        raise ValueError('Left and right frames must remain separate')
    if not isinstance(ROUND_SEGMENTS, int) or ROUND_SEGMENTS < 32 or ROUND_SEGMENTS % 4:
        raise ValueError('ROUND_SEGMENTS must be a multiple of four of at least 32')


validate()
