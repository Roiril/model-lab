"""100 mm高の流線型ノートPCスタンド用寸法。"""

MODEL_NAME = "laptop-stand-100"
CATEGORY = "ノートPCスタンド"
# CATEGORY: ノートPCスタンド

LAPTOP_WIDTH = 0.400  # 400 mm
LAPTOP_DEPTH = 0.330  # 330 mm
LAPTOP_BASE_THICKNESS = 0.025  # 25 mm（参考表示）
LOAD_MASS_KG = 4.0  # kg

BODY_HEIGHT = 0.098  # 98 mm
FRAME_DEPTH = 0.245  # 245 mm
UPPER_WIDTH = 0.034  # 34 mm
FRAME_WIDTH = 0.026  # 26 mm（上面丸め後の保守的な平面幅）
TOP_BEAM = 0.020  # 20 mm
TOP_END_RADIUS = 0.012  # 12 mm
TOP_EDGE_RADIUS = 0.0015  # 1.5 mm
RAIL_CENTER = 0.160  # 160 mm（左右中心間は320 mm）

FOOT_WIDTH = 0.100  # 100 mm
FOOT_DEPTH = 0.275  # 275 mm
FOOT_FRONT_Y = -0.015  # -15 mm
FOOT_ROUND = 0.030  # 30 mm
FOOT_HEIGHT = 0.019  # 19 mm（上面を丸い稜線へ絞る）
BOTTOM_BEAM = 0.010  # 10 mm（丸い足の中に残す保守的な芯厚）
FOOT_EDGE_RADIUS = 0.0001  # 0.1 mm（底面XY輪郭のR30を保つ）
FOOT_PROFILE = (
    (-0.0008, 0.100, 0.275),  # Z / 幅 / 奥行。底面を0.8 mm突き出す
    (0.001, 0.100, 0.275),
    (0.003, 0.099, 0.274),
    (0.006, 0.096, 0.273),
    (0.010, 0.089, 0.270),
    (0.014, 0.074, 0.258),
    (0.017, 0.048, 0.242),
    (0.019, 0.014, 0.219),
)  # 全寸法m。幅広の底面から丸い稜線へ連続的に絞る

# 側面(Y, Z)のCubic Bezier中心線。点順は上梁から底部。
S_CURVE_POINTS = (
    (0.130, 0.084),  # 130, 84 mm
    (0.043, 0.053),  # 43, 53 mm
    (0.198, 0.047),  # 198, 47 mm
    (0.224, 0.013),  # 224, 13 mm
)
REAR_CURVE_POINTS = (
    (0.026, 0.084),  # 26, 84 mm
    (0.072, 0.060),  # 72, 60 mm
    (0.000, 0.037),  # 0, 37 mm
    (0.024, 0.013),  # 24, 13 mm
)
S_SIDE_RADIUS = 0.015  # 15 mm
S_X_RADIUS = 0.018  # 18 mm
REAR_SIDE_RADIUS = 0.011  # 11 mm
REAR_X_RADIUS = 0.017  # 17 mm
S_ROOT_X_RADIUS = 0.038  # 38 mm
REAR_ROOT_X_RADIUS = 0.031  # 31 mm
S_ROOT_SIDE_RADIUS = 0.017  # 17 mm
REAR_ROOT_SIDE_RADIUS = 0.015  # 15 mm

CURVE_STEPS = 64
RING_STEPS = 64
REMESH_VOXEL = 0.0006  # 0.6 mm（融合後に曲面を平滑化）
SMOOTH_ITERATIONS = 180
SMOOTH_FACTOR = 0.65
CLIP_OVERLAP = 0.0008  # 0.8 mm
CLEANUP_DISTANCE = 0.000001  # 0.001 mm

PAD_THICKNESS = 0.001  # 1 mm
PAD_WIDTH = 0.024  # 24 mm
PAD_LENGTH = 0.045  # 45 mm
PAD_FRONT_Y = 0.016  # 16 mm
PAD_REAR_Y = 0.184  # 184 mm
BASE_PAD_WIDTH = 0.092  # 92 mm
BASE_PAD_LENGTH = 0.035  # 35 mm
BASE_PAD_FRONT_Y = 0.003  # 3 mm
BASE_PAD_REAR_Y = 0.207  # 207 mm

try:
    from param_override import apply_overrides
    apply_overrides(globals())
except ImportError:
    pass


def validate():
    import math

    positive = (
        LAPTOP_WIDTH, LAPTOP_DEPTH, LAPTOP_BASE_THICKNESS, LOAD_MASS_KG,
        BODY_HEIGHT, FRAME_DEPTH, UPPER_WIDTH, FRAME_WIDTH, TOP_BEAM,
        TOP_END_RADIUS, TOP_EDGE_RADIUS, RAIL_CENTER, FOOT_WIDTH, FOOT_DEPTH,
        FOOT_ROUND, FOOT_HEIGHT, BOTTOM_BEAM, FOOT_EDGE_RADIUS, S_SIDE_RADIUS, S_X_RADIUS,
        REAR_SIDE_RADIUS, REAR_X_RADIUS, S_ROOT_X_RADIUS, REAR_ROOT_X_RADIUS,
        S_ROOT_SIDE_RADIUS, REAR_ROOT_SIDE_RADIUS, REMESH_VOXEL,
        SMOOTH_FACTOR, CLIP_OVERLAP, CLEANUP_DISTANCE, PAD_THICKNESS,
        PAD_WIDTH, PAD_LENGTH, BASE_PAD_WIDTH, BASE_PAD_LENGTH,
    )
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0
           for value in positive):
        raise ValueError("Dimensions and loads must be finite positive numbers")
    for name, points in (("S_CURVE_POINTS", S_CURVE_POINTS),
                         ("REAR_CURVE_POINTS", REAR_CURVE_POINTS)):
        if len(points) != 4 or any(len(point) != 2 for point in points):
            raise ValueError(f"{name} must contain four Y/Z points")
        if any(not math.isfinite(value) for point in points for value in point):
            raise ValueError(f"{name} must contain finite coordinates")
    if RAIL_CENTER <= FOOT_WIDTH / 2.0:
        raise ValueError("Left and right bodies must remain separate")
    if UPPER_WIDTH < PAD_WIDTH or FRAME_WIDTH < PAD_WIDTH:
        raise ValueError("The top must retain at least the pad width as a flat contact")
    if TOP_BEAM >= BODY_HEIGHT or FOOT_HEIGHT >= BODY_HEIGHT:
        raise ValueError("Top and foot thicknesses must fit within the body height")
    if abs(FOOT_FRONT_Y + FOOT_DEPTH - (FRAME_DEPTH + 0.015)) > 1e-9:
        raise ValueError("Foot must span Y=-15..260 mm")
    if FOOT_ROUND * 2.0 >= FOOT_WIDTH:
        raise ValueError("Foot corner radius is too large")
    if (len(FOOT_PROFILE) < 3 or
            any(len(section) != 3 for section in FOOT_PROFILE) or
            any(not math.isfinite(value) for section in FOOT_PROFILE for value in section) or
            any(width <= 0 or depth <= 0 for _, width, depth in FOOT_PROFILE) or
            any(a[0] >= b[0] for a, b in zip(FOOT_PROFILE, FOOT_PROFILE[1:]))):
        raise ValueError("Foot profiles must be finite ordered Z/width/depth sections")
    if abs(FOOT_PROFILE[-1][0] - FOOT_HEIGHT) > 1e-9:
        raise ValueError("The foot profile must end at the specified foot height")
    if not isinstance(CURVE_STEPS, int) or CURVE_STEPS < 64:
        raise ValueError("Curve sweeps must use at least 64 steps")
    if not isinstance(RING_STEPS, int) or RING_STEPS < 32:
        raise ValueError("Sweep rings must use at least 32 steps")
    if not isinstance(SMOOTH_ITERATIONS, int) or SMOOTH_ITERATIONS < 0:
        raise ValueError("Smooth iterations must be a non-negative integer")


validate()
