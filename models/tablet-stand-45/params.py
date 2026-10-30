"""Redmi Pad SE 11 インチ裸本体用スタンドの固定寸法。長さの単位は m。"""

MODEL_NAME = "tablet-stand-45"
# CATEGORY: タブレットスタンド

TABLET_WIDTH = 0.25553  # 255.53mm
TABLET_HEIGHT = 0.16708  # 167.08mm
TABLET_THICKNESS = 0.00736  # 7.36mm
TABLET_MASS_KG = 0.478  # 478g
BACK_PAD = 0.0008  # 0.8mm
FLOOR_PAD = 0.0008  # 0.8mm
FEET_PAD = 0.0  # 一体の平らな台座を机へ直接置く

WIDTH = 0.212  # 台座横幅 212mm
DEPTH = 0.220  # 台座奥行き 220mm
BASE_FRONT = -0.006  # 前へ6mm張り出す
BASE_CORNER_R = 0.012  # XY輪郭の角丸12mm。下面は平ら
FRAME_DEPTH = 0.208  # 台座後縁まで6mmを残す
SIDE_MARGIN = 0.008  # 左右の台座張り出し8mm
ANGLE_DEG = 45.0  # 傾き 45度

SEAT_Y = 0.017  # 下端の前後位置 17mm
SEAT_Z = 0.014  # 下端の高さ 14mm
SUPPORT_LENGTH = 0.154  # 背面を支える長さ 154mm
RIB_WIDTH = 0.028  # 左右リブ幅 28mm
RIB_CENTER = (WIDTH - 2 * SIDE_MARGIN - RIB_WIDTH) / 2.0  # +/-84mm
DECK_THICKNESS = 0.020  # 背面の支え20mm以上
BASE_THICKNESS = 0.006  # 全面台座6mm
REAR_THICKNESS = 0.020  # 後ろの支え20mm以上
OPENING_FRONT = 0.060  # 窓の下辺はY=60..180mm
OPENING_REAR = 0.180
OPENING_TOP_Y = 0.120
OPENING_TOP_Z = 0.066  # 窓を高さ66mmで閉じ、上部を連続させる

GROOVE_WIDTH = 0.0092  # 受け口 9.2mm（本体 7.36 + 背面パッド 0.8 + 余裕 1.04mm）
LIP_HEIGHT = 0.006  # 画面方向への落下止め投影高さ 6mm
LIP_THICKNESS = 0.004  # 落下止めのY方向厚さ4mm

INNER_CORNER_R = 0.0008  # 受け口の内側の丸み 0.8mm
LIP_OUTER_R = 0.0012  # 落下止め外側の丸み 1.2mm
SUPPORT_TOP_R = 0.003  # 支え上端の丸み 3mm
LOWER_OUTER_R = 0.004  # 脚の前後の丸み 4mm
HOLE_FLOOR_CORNER_R = 0.007  # 穴の床側の丸み 7mm
HOLE_TOP_R = 0.0008  # 穴頂部の丸み 0.8mm
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
        "TABLET_WIDTH": TABLET_WIDTH,
        "TABLET_HEIGHT": TABLET_HEIGHT,
        "TABLET_THICKNESS": TABLET_THICKNESS,
        "BACK_PAD": BACK_PAD,
        "FLOOR_PAD": FLOOR_PAD,
        "WIDTH": WIDTH,
        "DEPTH": DEPTH,
        "SEAT_Y": SEAT_Y,
        "SEAT_Z": SEAT_Z,
        "SUPPORT_LENGTH": SUPPORT_LENGTH,
        "RIB_WIDTH": RIB_WIDTH,
        "RIB_CENTER": RIB_CENTER,
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
        "HOLE_FLOOR_CORNER_R": HOLE_FLOOR_CORNER_R,
        "HOLE_TOP_R": HOLE_TOP_R,
        "BASE_CORNER_R": BASE_CORNER_R,
        "FRAME_DEPTH": FRAME_DEPTH,
        "SIDE_MARGIN": SIDE_MARGIN,
        "OPENING_FRONT": OPENING_FRONT,
        "OPENING_REAR": OPENING_REAR,
        "OPENING_TOP_Y": OPENING_TOP_Y,
        "OPENING_TOP_Z": OPENING_TOP_Z,
    }
    for name, value in lengths.items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{name} must be a positive number")
    if not 30.0 <= ANGLE_DEG <= 70.0:
        raise ValueError("ANGLE_DEG must be between 30 and 70 degrees")
    if not isinstance(ROUND_SEGMENTS, int) or ROUND_SEGMENTS < 32:
        raise ValueError("ROUND_SEGMENTS must be an integer of at least 32")
    if abs(RIB_CENTER - (WIDTH - 2 * SIDE_MARGIN - RIB_WIDTH) / 2.0) > 1e-9:
        raise ValueError("rib locations must retain the base margins")
    if not BASE_FRONT < 0 < FRAME_DEPTH < BASE_FRONT + DEPTH:
        raise ValueError("frame must fit inside the base")
    rise = OPENING_TOP_Z - BASE_THICKNESS
    if max(OPENING_TOP_Y - OPENING_FRONT, OPENING_REAR - OPENING_TOP_Y) > rise + 1e-9:
        raise ValueError("opening roof must not exceed 45 degrees from vertical")
    if FEET_PAD < 0:
        raise ValueError("feet height cannot be negative")
    if GROOVE_WIDTH <= TABLET_THICKNESS + BACK_PAD:
        raise ValueError("groove must include tablet, pad, and clearance")
    if min(BASE_THICKNESS, DECK_THICKNESS, REAR_THICKNESS, LIP_THICKNESS) < 0.0032:
        raise ValueError("structural sections are too thin")


validate()
