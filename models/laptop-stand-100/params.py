"""100 mm高の一体型ノートPCスタンド用寸法。"""

MODEL_NAME = "laptop-stand-100"
CATEGORY = "ノートPCスタンド"
# CATEGORY: ノートPCスタンド

LAPTOP_WIDTH = 0.400  # 400 mm
LAPTOP_DEPTH = 0.330  # 330 mm
LAPTOP_BASE_THICKNESS = 0.025  # 25 mm（参考表示）
LOAD_MASS_KG = 4.0  # kg

BODY_HEIGHT = 0.098  # 98 mm
FRAME_DEPTH = 0.245  # 245 mm
UPPER_WIDTH = 0.030  # 30 mm
TOP_FILLET = 0.002  # 2 mm
TOP_ROUND = 0.012  # 12 mm
TOP_BEAM = 0.018  # 18 mm（検証用参照値）
BOTTOM_BEAM = 0.012  # 12 mm（内縁丸め後の最小下梁）
END_COLUMN = 0.019  # 19 mm（検証用参照値）
RAIL_CENTER = 0.160  # 160 mm（左右中心間は320 mm）
FLOW_HEIGHT = 0.025  # 25 mm

FOOT_WIDTH = 0.100  # 100 mm
FOOT_DEPTH = 0.275  # 275 mm
FOOT_ROUND = 0.030  # 30 mm
BOTTOM_CHAMFER = 0.001  # 1 mm

HOLE_CENTERS = (0.064, 0.181)  # 64 mm、181 mm
HOLE_WIDTH = 0.090  # 90 mm
HOLE_FLOOR = 0.014  # 14 mm（内縁丸め後の最小下梁は約12 mm）
HOLE_PEAK = 0.078  # 78 mm
HOLE_ROOF_SLOPE = 1.05  # 45度を超える屋根勾配
HOLE_CROWN_R = 0.006  # 6 mm
HOLE_FLOOR_R = 0.008  # 8 mm
HOLE_SHOULDER_R = 0.005  # 5 mm
HOLE_EDGE_R = 0.002  # 2 mm

PAD_THICKNESS = 0.001  # 1 mm
PAD_WIDTH = 0.024  # 24 mm
PAD_LENGTH = 0.045  # 45 mm
PAD_FRONT_Y = 0.016  # 16 mm
PAD_REAR_Y = 0.184  # 184 mm
BASE_PAD_WIDTH = 0.092  # 92 mm
BASE_PAD_LENGTH = 0.035  # 35 mm
BASE_PAD_FRONT_Y = 0.003  # 3 mm
BASE_PAD_REAR_Y = 0.207  # 207 mm

LOFT_PROFILE_POINTS = 132  # 円弧端点を含む外形1周の点数
FLOW_STEPS = 64  # z=1..96 mmの段数下限
TOP_FILLET_STEPS = 16  # 最上部フィレットの分割数
CLEANUP_DISTANCE = 0.0000001  # 0.0001 mm

try:
    from param_override import apply_overrides
    apply_overrides(globals())
except ImportError:
    pass

# Override後に再導出する寸法。
TOP_WIDTH = UPPER_WIDTH - 2.0 * TOP_FILLET
FRAME_WIDTH = TOP_WIDTH
TOP_DEPTH = FRAME_DEPTH
FLOW_TOP_Z = BODY_HEIGHT - TOP_FILLET
FLOW_UPPER_DEPTH = TOP_DEPTH + 2.0 * TOP_FILLET
FLOW_UPPER_ROUND = TOP_ROUND + TOP_FILLET
HOLE_HALF_WIDTH = HOLE_WIDTH / 2.0
HOLE_THEORETICAL_PEAK = HOLE_PEAK + HOLE_CROWN_R * (
    (1.0 + HOLE_ROOF_SLOPE ** 2) ** 0.5 - 1.0
)


def validate():
    import math
    values = (
        LAPTOP_WIDTH, LAPTOP_DEPTH, LAPTOP_BASE_THICKNESS, LOAD_MASS_KG,
        BODY_HEIGHT, FRAME_DEPTH, FRAME_WIDTH, UPPER_WIDTH, TOP_FILLET,
        TOP_BEAM, BOTTOM_BEAM, END_COLUMN, RAIL_CENTER, FLOW_HEIGHT, TOP_ROUND,
        FOOT_WIDTH, FOOT_DEPTH, FOOT_ROUND, BOTTOM_CHAMFER, HOLE_WIDTH,
        HOLE_FLOOR, HOLE_PEAK, HOLE_ROOF_SLOPE, HOLE_CROWN_R,
        HOLE_FLOOR_R, HOLE_SHOULDER_R, HOLE_EDGE_R, PAD_THICKNESS,
        PAD_WIDTH, PAD_LENGTH, BASE_PAD_WIDTH, BASE_PAD_LENGTH,
        CLEANUP_DISTANCE,
    )
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("Dimensions and loads must be finite positive numbers")
    if len(HOLE_CENTERS) != 2 or any(not math.isfinite(value) for value in HOLE_CENTERS):
        raise ValueError("Exactly two finite opening centers are required")
    if RAIL_CENTER <= FOOT_WIDTH / 2.0:
        raise ValueError("Left and right bodies must remain separate")
    if TOP_WIDTH < PAD_WIDTH or TOP_ROUND >= TOP_WIDTH / 2.0:
        raise ValueError("The top must accommodate the protective pads and rounded ends")
    if BOTTOM_CHAMFER + 2.6 * FLOW_HEIGHT >= FLOW_TOP_Z:
        raise ValueError("The base curve must meet the upper section below its top fillet")
    if HOLE_CENTERS[0] - HOLE_HALF_WIDTH < 0 or HOLE_CENTERS[1] + HOLE_HALF_WIDTH > FRAME_DEPTH:
        raise ValueError("Openings must remain inside the body depth")
    if HOLE_CENTERS[1] - HOLE_HALF_WIDTH - (HOLE_CENTERS[0] + HOLE_HALF_WIDTH) < 0.027 - 1e-9:
        raise ValueError("The center column must remain at least 27 mm wide")
    if HOLE_FLOOR - HOLE_EDGE_R < BOTTOM_BEAM - 1e-9:
        raise ValueError("The rounded opening must retain the minimum lower beam")
    if BODY_HEIGHT - (HOLE_PEAK + HOLE_EDGE_R) < TOP_BEAM - 1e-9:
        raise ValueError("The rounded opening must retain the minimum top beam")
    if FOOT_ROUND * 2.0 >= min(FOOT_WIDTH, FOOT_DEPTH):
        raise ValueError("Foot corner radius is too large")
    if not isinstance(LOFT_PROFILE_POINTS, int) or LOFT_PROFILE_POINTS != 132:
        raise ValueError("Loft profiles must contain exactly 132 points")
    if not isinstance(FLOW_STEPS, int) or FLOW_STEPS < 64:
        raise ValueError("Flow loft must use at least 64 steps")
    if not isinstance(TOP_FILLET_STEPS, int) or TOP_FILLET_STEPS < 16:
        raise ValueError("Top fillet must use at least 16 steps")


validate()
