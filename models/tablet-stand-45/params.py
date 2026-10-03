"""Redmi Pad SE 11 インチ裸本体用スタンドの固定寸法。長さの単位は m。"""

MODEL_NAME = "tablet-stand-45"
# CATEGORY: タブレットスタンド

TABLET_WIDTH = 0.25553  # 255.53mm
TABLET_HEIGHT = 0.16708  # 167.08mm
TABLET_THICKNESS = 0.00736  # 7.36mm
TABLET_MASS_KG = 0.478  # 478g
BACK_PAD = 0.0008  # 0.8mm
FLOOR_PAD = 0.0008  # 0.8mm
FEET_PAD = 0.001  # 1mm

WIDTH = 0.180  # 横幅 180mm
DEPTH = 0.210  # 奥行き 210mm
ANGLE_DEG = 45.0  # 傾き 45度

SEAT_Y = 0.017  # 下端の前後位置 17mm
SEAT_Z = 0.012  # 下端の高さ 12mm
SUPPORT_LENGTH = 0.154  # 背面を支える長さ 154mm
RIB_WIDTH = 0.018  # 左右リブ幅 18mm
RIB_CENTER = (WIDTH - RIB_WIDTH) / 2.0  # 左右中心 X = +/-81mm
DECK_THICKNESS = 0.005  # 背面の支えの法線方向厚さ 5mm
BASE_THICKNESS = 0.004  # 底の厚さ 4mm
REAR_THICKNESS = 0.006  # 後ろの支えの法線方向厚さ 6mm

GROOVE_WIDTH = 0.0092  # 受け口 9.2mm（本体 7.36 + 背面パッド 0.8 + 余裕 1.04mm）
LIP_HEIGHT = 0.006  # 画面方向への落下止め投影高さ 6mm
LIP_THICKNESS = 0.0032  # 落下止めの Y 方向厚さ 3.2mm

INNER_CORNER_R = 0.0008  # 受け口の内側の丸み 0.8mm
LIP_OUTER_R = 0.0012  # 落下止め外側の丸み 1.2mm
SUPPORT_TOP_R = 0.003  # 支え上端の丸み 3mm
LOWER_OUTER_R = 0.004  # 脚の前後の丸み 4mm
HOLE_FLOOR_CORNER_R = 0.007  # 穴の床側の丸み 7mm
HOLE_TOP_R = 0.0008  # 穴頂部の丸み 0.8mm
SIDE_CHAMFER = 0.0006  # X 端面の縁を落とす幅 0.6mm
ROUND_SEGMENTS = 12 * 12

BAR_WIDTH = 0.174  # 横棒幅 174mm
BAR_Y_FRONT = 0.004  # 前横棒の開始位置 4mm
BAR_DEPTH_FRONT = 0.012  # 前横棒の奥行き 12mm
BAR_Y_REAR = 0.198  # 後横棒の開始位置 198mm
BAR_DEPTH_REAR = 0.010  # 後横棒の奥行き 10mm
BAR_HEIGHT = 0.004  # 横棒高さ 4mm
BAR_CORNER_R = 0.0008  # 横棒の丸み 0.8mm


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
        "FEET_PAD": FEET_PAD,
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
        "SIDE_CHAMFER": SIDE_CHAMFER,
        "BAR_WIDTH": BAR_WIDTH,
        "BAR_Y_FRONT": BAR_Y_FRONT,
        "BAR_DEPTH_FRONT": BAR_DEPTH_FRONT,
        "BAR_Y_REAR": BAR_Y_REAR,
        "BAR_DEPTH_REAR": BAR_DEPTH_REAR,
        "BAR_HEIGHT": BAR_HEIGHT,
        "BAR_CORNER_R": BAR_CORNER_R,
    }
    for name, value in lengths.items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{name} must be a positive number")
    if not 30.0 <= ANGLE_DEG <= 70.0:
        raise ValueError("ANGLE_DEG must be between 30 and 70 degrees")
    if not isinstance(ROUND_SEGMENTS, int) or ROUND_SEGMENTS < 32:
        raise ValueError("ROUND_SEGMENTS must be an integer of at least 32")
    if abs(RIB_CENTER - (WIDTH - RIB_WIDTH) / 2.0) > 1e-9:
        raise ValueError("RIB_CENTER must place the ribs against the outside edges")
    rib_inner_edge = RIB_CENTER - RIB_WIDTH / 2.0
    if BAR_WIDTH / 2.0 <= rib_inner_edge:
        raise ValueError("crossbars must overlap both ribs")
    if BAR_Y_FRONT + BAR_DEPTH_FRONT >= SEAT_Y:
        raise ValueError("front crossbar must remain ahead of the tablet seat")
    if BAR_Y_REAR + BAR_DEPTH_REAR > DEPTH:
        raise ValueError("rear crossbar must remain within the stand depth")
    if BAR_HEIGHT != BASE_THICKNESS:
        raise ValueError("crossbars and rib floors must share the print surface")
    if GROOVE_WIDTH <= TABLET_THICKNESS + BACK_PAD:
        raise ValueError("groove must include tablet, pad, and clearance")
    if min(BASE_THICKNESS, DECK_THICKNESS, REAR_THICKNESS, LIP_THICKNESS) < 0.0032:
        raise ValueError("structural sections are too thin")


validate()
