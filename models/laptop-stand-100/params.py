"""100 mm高の水平ノートPCスタンド用寸法。"""

MODEL_NAME = "laptop-stand-100"
CATEGORY = "ノートPCスタンド"
# CATEGORY: ノートPCスタンド

LAPTOP_WIDTH = 0.400  # 400 mm
LAPTOP_DEPTH = 0.330  # 330 mm
LAPTOP_BASE_THICKNESS = 0.025  # 25 mm（参考表示）
LOAD_MASS_KG = 4.0  # kg

BODY_HEIGHT = 0.094  # 94 mm
FRAME_DEPTH = 0.245  # 245 mm
FRAME_WIDTH = 0.026  # 26 mm
TOP_BEAM = 0.016  # 16 mm
BOTTOM_BEAM = 0.007  # 7 mm
BASE_THICKNESS = BOTTOM_BEAM  # 7 mm（底梁厚の参照名）
END_COLUMN = 0.018  # 18 mm
OUTER_R = 0.012  # 12 mm
INNER_R = 0.020  # 20 mm
SIDE_CHAMFER = 0.0008  # 0.8 mm
RAIL_CENTER = 0.160  # 160 mm（左右中心間は320 mm）
PAD_THICKNESS = 0.001  # 1 mm
PAD_WIDTH = 0.024  # 24 mm
PAD_LENGTH = 0.045  # 45 mm
PAD_FRONT_Y = 0.016  # 16 mm
PAD_REAR_Y = 0.184  # 184 mm

FOOT_WIDTH = 0.100  # 100 mm
FOOT_DEPTH = 0.275  # 275 mm
FOOT_HEIGHT = 0.022  # 22 mm
FOOT_FLOOR = 0.004  # 4 mm
FOOT_ROUND = 0.030  # 30 mm
FOOT_TOP_WIDTH = 0.034  # 34 mm
FOOT_TOP_DEPTH = 0.260  # 260 mm
FOOT_TOP_ROUND = 0.008  # 8 mm
FOOT_CHAMFER = 0.001  # 1 mm
FOOT_LOFT_STEPS = 32
FIT_CLEARANCE = 0.00025  # 0.25 mm per side
ENTRY_CHAMFER = 0.0005  # 0.5 mm
BASE_PAD_WIDTH = 0.092  # 92 mm
BASE_PAD_LENGTH = 0.035  # 35 mm
BASE_PAD_FRONT_Y = 0.003  # 3 mm
BASE_PAD_REAR_Y = 0.207  # 207 mm

ROUND_SEGMENTS = 128  # 円1周あたりの分割数
CLEANUP_DISTANCE = 0.0000001  # 0.0001 mm

try:
    from param_override import apply_overrides
    apply_overrides(globals())
except ImportError:
    pass

# Override後に再導出する寸法。
BASE_THICKNESS = BOTTOM_BEAM
SLOT_WIDTH = FRAME_WIDTH + 2.0 * FIT_CLEARANCE
SLOT_DEPTH = FRAME_DEPTH + 2.0 * FIT_CLEARANCE
FOOT_BOTTOM_WIDTH = FOOT_WIDTH - 2.0 * FOOT_CHAMFER
FOOT_BOTTOM_DEPTH = FOOT_DEPTH - 2.0 * FOOT_CHAMFER
FOOT_BOTTOM_ROUND = FOOT_ROUND - FOOT_CHAMFER
FRAME_ASSEMBLY_Z = FOOT_FLOOR + PAD_THICKNESS


def validate():
    import math
    values = (
        LAPTOP_WIDTH, LAPTOP_DEPTH, LAPTOP_BASE_THICKNESS, LOAD_MASS_KG,
        BODY_HEIGHT, FRAME_DEPTH, FRAME_WIDTH, TOP_BEAM, BOTTOM_BEAM,
        END_COLUMN, OUTER_R, INNER_R, SIDE_CHAMFER, RAIL_CENTER,
        PAD_THICKNESS, PAD_WIDTH, PAD_LENGTH, FOOT_WIDTH, FOOT_DEPTH,
        FOOT_HEIGHT, FOOT_FLOOR, FOOT_ROUND, FOOT_TOP_WIDTH,
        FOOT_TOP_DEPTH, FOOT_TOP_ROUND, FOOT_CHAMFER, FIT_CLEARANCE,
        ENTRY_CHAMFER, BASE_PAD_WIDTH, BASE_PAD_LENGTH, CLEANUP_DISTANCE,
    )
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("Dimensions and loads must be finite positive numbers")
    if min(TOP_BEAM, BOTTOM_BEAM, END_COLUMN) <= 2.0 * SIDE_CHAMFER:
        raise ValueError("Sections must be thicker than the side chamfers")
    if RAIL_CENTER <= max(FRAME_WIDTH, FOOT_WIDTH) / 2.0:
        raise ValueError("Left and right parts must remain separate")
    if PAD_WIDTH > FRAME_WIDTH - 2.0 * SIDE_CHAMFER:
        raise ValueError("Top pad exceeds the flat frame surface")
    if BASE_PAD_WIDTH > FOOT_BOTTOM_WIDTH or BASE_PAD_LENGTH > FOOT_BOTTOM_DEPTH:
        raise ValueError("Base pad exceeds the foot underside")
    if PAD_FRONT_Y < OUTER_R or PAD_REAR_Y + PAD_LENGTH > FRAME_DEPTH - OUTER_R:
        raise ValueError("Top pads must remain on the flat frame surface")
    if BASE_PAD_FRONT_Y < 0 or BASE_PAD_REAR_Y + BASE_PAD_LENGTH > FOOT_BOTTOM_DEPTH:
        raise ValueError("Base pads must remain on the foot underside")
    if not (FOOT_FLOOR < FOOT_HEIGHT - ENTRY_CHAMFER):
        raise ValueError("Foot floor and entry chamfer leave no slot height")
    if SLOT_WIDTH >= FOOT_TOP_WIDTH or SLOT_DEPTH >= FOOT_TOP_DEPTH:
        raise ValueError("Slot must leave walls at the foot top")
    if FOOT_ROUND * 2.0 >= min(FOOT_WIDTH, FOOT_DEPTH):
        raise ValueError("Foot corner radius is too large")
    if FOOT_TOP_ROUND * 2.0 >= min(FOOT_TOP_WIDTH, FOOT_TOP_DEPTH):
        raise ValueError("Foot top radius is too large")
    if FOOT_BOTTOM_ROUND <= 0:
        raise ValueError("Foot underside corner radius must remain positive")
    if BODY_HEIGHT <= TOP_BEAM + BOTTOM_BEAM + 2.0 * INNER_R:
        raise ValueError("Frame height cannot contain the beams and inner corner radii")
    if FOOT_HEIGHT - FOOT_FLOOR <= 0 or BOTTOM_BEAM >= FOOT_HEIGHT - FOOT_FLOOR:
        raise ValueError("Foot slot must provide positive frame engagement")
    if not isinstance(FOOT_LOFT_STEPS, int) or FOOT_LOFT_STEPS < 32:
        raise ValueError("FOOT_LOFT_STEPS must be at least 32")
    if not isinstance(ROUND_SEGMENTS, int) or ROUND_SEGMENTS < 32 or ROUND_SEGMENTS % 4:
        raise ValueError("ROUND_SEGMENTS must be a multiple of four of at least 32")


validate()
