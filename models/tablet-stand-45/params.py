"""tablet-stand-45 の固定寸法。長さの単位は m。"""

MODEL_NAME = "tablet-stand-45"
# CATEGORY: タブレットスタンド

WIDTH = 0.228  # 横幅 228mm
DEPTH = 0.240  # 奥行き 240mm
ANGLE_DEG = 45.0  # 傾き 45度

SEAT_Y = 0.034  # 下端の前後位置 34mm
SEAT_Z = 0.020  # 下端の高さ 20mm
SUPPORT_LENGTH = 0.180  # 背面を支える長さ 180mm
DECK_THICKNESS = 0.010  # 背面の支えの厚さ 10mm
BASE_THICKNESS = 0.010  # 底板の厚さ 10mm
REAR_THICKNESS = 0.016  # 後ろの支えの厚さ 16mm

GROOVE_WIDTH = 0.022  # 受け口の幅 22mm
LIP_HEIGHT = 0.009  # 画面に沿った落下止めの高さ 9mm
LIP_THICKNESS = 0.006  # 落下止めの厚さ 6mm

INNER_CORNER_R = 0.0015  # 受け口の内側の丸み 1.5mm
LIP_OUTER_R = 0.00225  # 落下止めの丸み 2.25mm
SUPPORT_TOP_R = 0.008  # 支えの上端の丸み 8mm
LOWER_OUTER_R = 0.0075  # 脚の前後の丸み 7.5mm
HOLE_CORNER_R = 0.015  # 穴の隅の丸み 15mm
SIDE_CHAMFER = 0.0008  # 側面の縁を落とす幅 0.8mm
ROUND_SEGMENTS = 12 * 12


try:
    from param_override import apply_overrides
    apply_overrides(globals())
except ImportError:
    pass


def validate():
    if MODEL_NAME != "tablet-stand-45":
        raise ValueError("MODEL_NAME must remain tablet-stand-45")
    lengths = {
        "WIDTH": WIDTH,
        "DEPTH": DEPTH,
        "SEAT_Y": SEAT_Y,
        "SEAT_Z": SEAT_Z,
        "SUPPORT_LENGTH": SUPPORT_LENGTH,
        "DECK_THICKNESS": DECK_THICKNESS,
        "BASE_THICKNESS": BASE_THICKNESS,
        "REAR_THICKNESS": REAR_THICKNESS,
        "GROOVE_WIDTH": GROOVE_WIDTH,
        "LIP_HEIGHT": LIP_HEIGHT,
        "LIP_THICKNESS": LIP_THICKNESS,
        "INNER_CORNER_R": INNER_CORNER_R,
        "LIP_OUTER_R": LIP_OUTER_R,
        "SUPPORT_TOP_R": SUPPORT_TOP_R,
        "LOWER_OUTER_R": LOWER_OUTER_R,
        "HOLE_CORNER_R": HOLE_CORNER_R,
        "SIDE_CHAMFER": SIDE_CHAMFER,
    }
    for name, value in lengths.items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{name} must be a positive number")
    if not 30.0 <= ANGLE_DEG <= 70.0:
        raise ValueError("ANGLE_DEG must be between 30 and 70 degrees")
    if not isinstance(ROUND_SEGMENTS, int) or ROUND_SEGMENTS < 32:
        raise ValueError("ROUND_SEGMENTS must be an integer of at least 32")
    if WIDTH <= 2 * SIDE_CHAMFER or DEPTH <= SEAT_Y:
        raise ValueError("stand dimensions are too small")
    if BASE_THICKNESS < 0.008 or DECK_THICKNESS < 0.008:
        raise ValueError("base and deck must retain at least 8mm")
    if REAR_THICKNESS < 0.016:
        raise ValueError("rear column must retain at least 16mm")


validate()
