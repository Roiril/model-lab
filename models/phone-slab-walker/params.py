"""スマホ板ロボットの寸法（mm）。座標: X 右、Y 前（画面の向き）、Z 上。足裏が z=0、腰の軸は y=0。

既製部品の出どころ:
- STS3215: mycobot-lab/src/robots/so101/sim/assets/sts3215_03a_v1.stl を自前で解析した値（ledger の basis 参照）
- Pixel 7a: models/pixel7a-stand/params.py を import する（書き写さない）
- Arduino Leonardo R3: 公式の外形と取付穴
"""
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "pixel7a_params", os.path.join(_here, "..", "pixel7a-stand", "params.py"))
_pixel = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pixel)

# --- スマホ（正本は m 単位） ---
PHONE_L = _pixel.PHONE_L * 1000
PHONE_W = _pixel.PHONE_W * 1000
PHONE_T = _pixel.PHONE_T * 1000
SLOT_L = _pixel.SLOT_L * 1000
SLOT_W = _pixel.SLOT_W * 1000
SLOT_T = _pixel.SLOT_T * 1000

# --- STS3215（サーボ座標: 出力軸が +Zs、軸は Xs=12.5, Ys=0） ---
SERVO_L = 45.4          # Xs 方向
SERVO_D = 24.8          # Ys 方向
SERVO_SHAFT_XS = 12.5
SERVO_ZS_REAR = -19.4   # 後ろのふた（コネクタ面）
SERVO_ZS_CAP = -14.4    # 本体と後ろのふたの境
SERVO_ZS_TOP = 16.2     # ホーンが座る面
SERVO_ZS_HORN = 18.7    # ホーンの外面
SERVO_ZS_TIP = 20.2     # スプラインの先
SERVO_CAP_XS = (-22.4, 15.5)
HORN_R = 10.0
HORN_HOLE_R = 1.25      # 穴の径（φ2.5）
HORN_HOLE_OFFSET = 4.95 # 軸から Ys / Xs 方向に ±4.95（PCD 14）
SPLINE_R = 2.7
CONNECTOR_XS = -1.55    # コネクタ 3 ピンの列の位置
CONNECTOR_YS = (1.2, 9.2)
CONNECTOR_LEN = 11.0    # 刺さったコネクタと線の曲げの逃げ（仮値。試し刷りで確かめる）

# --- 形を決める値 ---
CLEARANCE = 3.0         # 中央板が脚より短い量。sim_gait.py の比較で決める
CAP_FLOOR = 4.0         # 足の床
CHAMBER = 36.0          # スマホの下、USB プラグの置き場
STOP_WALL = 3.0         # スマホの上の壁
POCKET_FIT = 0.3        # サーボの穴の片側の隙間
SERVO_GAP = 13.0        # サーボの尻どうしの隙間（コネクタの置き場）
CABLE_HALF = 6.7        # サーボの線を下へ通す口の半幅
PILLAR_Y1 = -1.0        # 尻の間の柱の前の端（床から立つ）
Y_FRONT = 16.0
Y_REAR = -18.0
LIP_T = 2.0             # スマホの前の縁
DIVIDER_T = 2.0         # スマホとマイコンの仕切り
REAR_WALL = 2.0
SIDE_WALL = 3.0
LEG_W = 26.0
LEG_GAP = 0.6           # 中央板と脚の隙間
BOSS_GAP = 0.1          # 脚の座面とホーンの隙間
FOOT_D = 60.0           # 足裏の前後長さ（y ±30）
SOLE_CHAMFER = 1.5
BOLT_SHANK_R = 1.25
BOLT_HOLE_R = 1.6
BOLT_HEAD_R = 2.8
BOLT_HEAD_H = 2.4
BOLT_WELL_R = 3.6
BOLT_SEAT_T = 3.5
SWING_DEG = 45.0        # ファームの LIMIT_DEG と揃える
SWING_STEP = 2.5

# スライドの舌（断面は根本が細く先が太い台形）
TONGUE_X = 42.4
TONGUE_BASE = 0.8       # 半幅
TONGUE_TIP = 1.2        # 半幅
TONGUE_H = 1.2
TONGUE_FIT = 0.25       # 溝の片側の隙間

CAV_W = 40.0            # マイコンの部屋の半幅
SHELF_W = 1.4           # 仕切り板の棚の幅
HOOD_H = 3.0            # 頭の庇の高さ
TAB_X = (15.0, 25.0)    # 前枠の上端の爪
TAB_Y = (12.9, 14.6)    # 頭の前の壁を 1.2mm 残す
TAB_RISE = 1.3          # 爪の高さ。前の面は 45°
TAB_FIT = 0.25
PHONE_POST_X = (16.0, 30.0)   # スマホの下の柱（中央は USB プラグが通る）

# 足のふたの爪（弾性）
SNAP_T = 2.5
SNAP_DELTA = 1.0
SNAP_Y = (-10.0, 0.0)
SNAP_WINDOW_Z = (8.7, 12.3)   # z_split からの高さ
SNAP_ROOT_ABOVE_FLOOR = 6.0

# Arduino Leonardo R3（u は USB の短辺から、v は長辺から）
BOARD_L = 68.6
BOARD_W = 53.3
BOARD_T = 1.6
BOARD_HOLES = [(14.0, 2.5), (15.3, 50.7), (66.1, 7.6), (66.1, 35.5)]
BOARD_STANDOFF = 3.0
BOARD_PEG_R = 1.35
BOARD_PEG_H = 6.0
BOARD_TOP_KEEPOUT = 9.5  # ピンソケットとジャック

# --- 導いた値 ---
HALF_W = SERVO_GAP / 2 + (SERVO_ZS_TOP - SERVO_ZS_REAR) + SIDE_WALL   # 中央板の半幅
Z_BOTTOM = CLEARANCE
Z_SPLIT = Z_BOTTOM + 20.0
Z_SLOT0 = Z_BOTTOM + CAP_FLOOR + CHAMBER
Z_SLOT1 = Z_SLOT0 + SLOT_L
Z_STOP1 = Z_SLOT1 + STOP_WALL
SERVO_BELOW = SERVO_SHAFT_XS + SERVO_L / 2
SERVO_ABOVE = SERVO_L / 2 - SERVO_SHAFT_XS
HIP_Z = Z_STOP1 + POCKET_FIT + SERVO_BELOW
Z_POCKET_TOP = HIP_Z + SERVO_ABOVE + POCKET_FIT
Z_TOP = Z_POCKET_TOP + 3.0
Y_SLOT_FRONT = Y_FRONT - LIP_T
Y_SLOT_BACK = Y_SLOT_FRONT - SLOT_T
Y_DIV_BACK = Y_SLOT_BACK - DIVIDER_T
Y_CAV_BACK = Y_REAR + REAR_WALL
Y_POCKET = SERVO_D / 2 + POCKET_FIT
SERVO_X_REAR = SERVO_GAP / 2                    # 右サーボの尻の x
SERVO_X_TOP = SERVO_X_REAR + SERVO_ZS_TOP - SERVO_ZS_REAR
HORN_X0 = SERVO_X_TOP
HORN_X1 = SERVO_X_REAR + SERVO_ZS_HORN - SERVO_ZS_REAR
TIP_X = SERVO_X_REAR + SERVO_ZS_TIP - SERVO_ZS_REAR
LEG_X0 = HALF_W + LEG_GAP
LEG_X1 = LEG_X0 + LEG_W
LEG_SEAT_X = HORN_X1 + BOSS_GAP
BOSS_R = 9.5
HOLE_R = 11.0                                   # 側壁のホーン穴
LEG_TOP = Z_TOP
BOARD_Z0 = Z_SPLIT + 4.0
