"""住人の箱 C3。寸法は m。コメントは mm。"""
import importlib.util
import math
import os

_spec = importlib.util.spec_from_file_location(
    "sg92r_photo_params",
    os.path.join(os.path.dirname(__file__), "..", "sg92r-photo", "params.py"),
)
SG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SG)

MODEL_ID = "mystery-box-sg92r-c3"

# 外観。ホーンの全角度包絡と3mm床を両立するため、目標70mmから80mmへ広げた。
CUBE_W = 0.080  # 80mm
CUBE_D = 0.080  # 80mm
CUBE_H = 0.080  # 80mm
WALL = 0.003  # 3mm
FLOOR = 0.003  # 3mm

# 5x5天面格子。
GRID_N = 5
TILE = 0.0104  # 10.4mm
PITCH = 0.0112  # 11.2mm
TILE_GAP = PITCH - TILE  # 0.8mm
TILE_T = 0.003  # 3mm
CARRIER_BEAM_W = 0.006  # 6mm。歯車面の左右に0.6mm以上残す
CARRIER_BEAM_T = 0.003  # 3mm
GUIDE_TONGUE_W = 0.006  # 6mm
GUIDE_TONGUE_D = 0.0028  # 2.8mm
GUIDE_CLEARANCE = 0.0003  # 片側0.3mm
GUIDE_Y = 0.031  # 前後31mm
GUIDE_BAR_D = 0.004  # 4mm
GUIDE_BAR_H = 0.004  # 4mm
GUIDE_RIB_W = 0.002  # 分割されたガイド区間を床から支える2mmリブ

# サーボ軸とカム軸。30歯module 1の1:1伝達。
SERVO_AXIS_X = 0.0
SERVO_AXIS_Y = 0.0
SERVO_AXIS_Z = 0.0235  # 23.5mm。ホーン包絡の下面を床より0.5mm上に置く
GEAR_MODULE = 0.001  # module 1mm
GEAR_TEETH = 30
GEAR_PRESSURE_DEG = 20.0
GEAR_BACKLASH = 0.00018  # 円周方向0.18mm
GEAR_THICK = 0.004  # 4mm
GEAR_CENTER_DISTANCE = 0.0302  # 30.2mm
CAM_AXIS_X = 0.0
CAM_AXIS_Y = 0.0
CAM_AXIS_Z = SERVO_AXIS_Z + GEAR_CENTER_DISTANCE  # 53.7mm
GEAR_X = 0.0056  # 列0と+11.2mm列の間

# 円カムと列キャリア。
CAM_R = 0.007  # 7mm
CAM_E = 0.005  # 5mm
CAM_T = 0.003  # 3mm
CAM_PHASE_DEG = (145.0, 105.0, 65.0, 105.0, 145.0)
FOLLOWER_STOP_Z = CAM_AXIS_Z + CAM_R + 0.4 * CAM_E  # 軸+9mm
CARRIER_TOP_Z = CUBE_H
CARRIER_BEAM_Z0 = FOLLOWER_STOP_Z
CARRIER_BEAM_Z1 = CARRIER_BEAM_Z0 + CARRIER_BEAM_T
TILE_Z0 = CARRIER_TOP_Z - TILE_T

# 角度。15degで全列flush、165degで外列が最大3mm。
SERVO_HOME_DEG = 15.0
SERVO_END_DEG = 165.0
CAM_HOME_DEG = -5.0
CAM_END_DEG = 145.0
MOTION_DURATION_S = 2.0
MOTION_STEP_DEG = 1.0

# 分割カム軸。中央は六角、壁内は丸軸受け、端は着脱キャップ用。
SHAFT_AF = 0.0050  # 六角対辺5mm
SHAFT_BORE_AF = 0.0054  # 片側約0.2mm
JOURNAL_AF = SHAFT_AF  # 軸受け区間も六角対辺5mm。平面印刷する
JOURNAL_CORNER_D = JOURNAL_AF / math.cos(math.pi / 6)
BEARING_D = 0.0062  # 六角頂点から片側約0.21mm
SHAFT_MAIN_X = 0.0388  # ±38.8mm
SHAFT_TIP_X = 0.0397  # ±39.7mm
SHAFT_TIP_D = 0.0036  # 3.6mm
CAP_BORE_D = 0.0040  # 片側0.2mm
AXIAL_PLAY = 0.0003  # 0.3mm

# ホーン受け。正本寸法はSGを直接参照し、ここには隙間と外壁だけを置く。
HORN_CLEARANCE = 0.00020  # 片側0.20mm
HORN_RECEIVER_WALL = 0.0020  # 2mm
HORN_RECEIVER_X0 = 0.0000
HORN_RECEIVER_X1 = 0.0030
DRIVE_GEAR_X0 = GEAR_X - GEAR_THICK / 2
DRIVE_GEAR_X1 = GEAR_X + GEAR_THICK / 2

# サーボ保持と配線。
SERVO_CLEARANCE = 0.00035  # 片側0.35mm
CLIP_T = 0.003  # 荷重部3mm
CLIP_INTERFERENCE = 0.0001  # サーボY側を片側0.1mmで挟む
WIRE_EXIT_W = 0.008  # コネクタ8mm
WIRE_EXIT_H = 0.004  # 4mm

# 材料・物理。
PLA_DENSITY = 1240.0  # kg/m3
SERVO_STALL_TORQUE = 0.245  # N m @4.8V
FRICTION_COEFF = 0.30
