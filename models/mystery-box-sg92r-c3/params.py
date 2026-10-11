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
CARRIER_BEAM_W = 0.0066  # 6.6mm。カムの最悪位置と歯車左右0.3mm隙間を両立
CARRIER_BEAM_X_WIDTHS = (0.0066, 0.0066, 0.0056, 0.0066, 0.0066)
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
GEAR_BACKLASH = 0.00008  # 各歯車0.08mm、かみ合う2枚の歯厚減少は合計0.16mm
GEAR_THICK = 0.0046  # 4.6mm
GEAR_CENTER_DISTANCE = 0.0302  # 30.2mm
CAM_AXIS_X = 0.0
CAM_AXIS_Y = 0.0
CAM_AXIS_Z = SERVO_AXIS_Z + GEAR_CENTER_DISTANCE  # 53.7mm
GEAR_X = 0.0053  # 歯幅4.6mmをX=3.0..7.6mmへ置く

# 円カムと列キャリア。
CAM_R = 0.007  # 7mm
CAM_E = 0.005  # 5mm
CAM_T = 0.003  # 3mm
CAM_SPACER_D = 0.0126  # 軸方向保持ハブ12.6mm。六角穴頂点の外側に3mm以上残す
CAM_SPACER_GAP = 0.0002  # 隣接部品と内壁へ各0.2mm
CAM_INSERT_CLEARANCE = 0.00025  # 天面棚の挿入溝とハブの片側隙間0.25mm
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
SHAFT_MAIN_X = 0.03860  # キャップ厚1.2mmと主軸肩の両端公称隙間0.3mmを両立。カム積層の総遊びとは別
SHAFT_TIP_X = 0.0397  # ±39.7mm
SHAFT_TIP_D = 0.0036  # 3.6mm
CAP_BORE_D = 0.0040  # 片側0.2mm
CAP_THRUST_COLLAR_D = 0.0126  # 軸方向保持カラー外径12.6mm
CAP_THRUST_COLLAR_BORE_D = 0.0062  # 六角軸頂点へ片側0.213mm逃げる穴径6.2mm
CAP_THRUST_COLLAR_INNER_X = 0.03695  # カラー最内端。積層端36.8mmへ0.15mm隙間
CAP_THRUST_COLLAR_OVERLAP = 0.0002  # キャップ前面との一体化重なり0.2mm
AXIAL_PLAY = 0.0003  # 主軸肩の両端公称隙間0.3mm。カム積層の総遊びとは別
CAP_BODY_R = 0.00775  # 1.2mm角腕を一体で支える外側キャップ半径
CAP_BODY_CLEARANCE = 0.00025  # 本体と外装の半径隙間0.25mm
CAP_FACE_INSET = 0.00005  # 外装外面との同一面を避ける0.05mm
CAP_STEM_R = 0.00715  # 端ハブ半径6.3mmから腕内面へ0.25mm
CAP_LUG_R = 0.0090  # 壁内面へ掛ける3mm角爪の中心半径
CAP_LUG_W = 0.0030  # バヨネット爪の回転方向幅3mm
CAP_LUG_T = 0.0012  # バヨネット爪のX方向厚1.2mm
CAP_STEM_W = 0.0012  # 内側爪と外側キャップをつなぐ腕1.2mm
CAP_BAYONET_CLEARANCE = 0.00025  # 爪の回転包絡と挿入溝の片側隙間0.25mm
CAP_DETENT_ANGLE_DEG = 45.0
CAP_DETENT_ARM_L = 0.008  # 板ばね自由長8mm
CAP_DETENT_ARM_T = 0.0012  # 局所最小厚1.2mm
CAP_DETENT_INTERFERENCE = 0.00015  # 回転中の押し量0.15mm
CAP_DETENT_NOTCH_DEPTH = 0.0003  # 保持位置の凹み0.3mm
CAP_DETENT_NOTCH_W = 0.0034  # 回転方向の凹み幅3.4mm
CAP_PRINT_SUPPORT_FIN_T = 0.00045  # キャップ爪下面へ付ける除去式フィン幅0.45mm
CAP_PRINT_SUPPORT_CONTACT_W = 0.00050  # 爪下面の除去接点幅0.50mm
CAP_PRINT_SUPPORT_ROOT_OVERLAP = 0.00030  # キャップ本体への重なり0.30mm
CAP_PRINT_SUPPORT_LUG_OVERLAP = 0.00015  # 爪下面への重なり0.15mm

# ホーン受け。正本寸法はSGを直接参照し、ここには隙間と外壁だけを置く。
HORN_CLEARANCE = 0.00020  # 片側0.20mm
HORN_RECEIVER_WALL = 0.0020  # 2mm
HORN_RECEIVER_OPEN_X = SG.HORN_HUB_BOTTOM_Z - SG.HORN_ARM_BOTTOM_Z - HORN_CLEARANCE
HORN_BLIND_X0 = SG.HORN_ARM_T + HORN_CLEARANCE  # ホーン+X面から0.2mm
HORN_BLIND_T = 0.0020  # 盲底2mm
HORN_BOSS_D = 0.0120  # 中心ボス12mm
DRIVE_GEAR_X0 = GEAR_X - GEAR_THICK / 2
DRIVE_GEAR_X1 = GEAR_X + GEAR_THICK / 2
DRIVE_SUPPORT_ROOT_R = GEAR_MODULE * (GEAR_TEETH / 2 - 1.25)  # 歯底半径13.75mm
DRIVE_SUPPORT_LOFT = 0.00225  # 歯先16mmから歯底半径へ45°以下で縮める
DRIVE_SUPPORT_CONE = DRIVE_SUPPORT_ROOT_R - 0.0030  # 歯底半径からジャーナルへ45°
DRIVE_SUPPORT_ROOT_X = DRIVE_GEAR_X1 + DRIVE_SUPPORT_LOFT
DRIVE_JOURNAL_X0 = DRIVE_SUPPORT_ROOT_X + DRIVE_SUPPORT_CONE  # 20.6mm
DRIVE_JOURNAL_D = 0.0060  # +X側ジャーナル6mm
DRIVE_JOURNAL_SPAN = 0.00330  # 歯車面と端肩の間3.30mm
DRIVE_JOURNAL_X1 = DRIVE_JOURNAL_X0 + DRIVE_JOURNAL_SPAN  # 23.9mm
DRIVE_BEARING_W = 0.0030  # U字座の有効幅3mm
DRIVE_BEARING_RADIAL_CLEARANCE = 0.00025  # 片側0.25mm
DRIVE_SHOULDER_D = 0.0080  # 端肩8mm
DRIVE_SHOULDER_T = 0.0015  # 端肩厚1.5mm
DRIVE_SHOULDER_X1 = DRIVE_JOURNAL_X1 + DRIVE_SHOULDER_T  # 25.4mm
DRIVE_BEARING_WALL = 0.0030  # U字座の荷重部3mm
DRIVE_CLIP_GAP = 0.00025  # 上クリップとジャーナル上面の隙間0.25mm
DRIVE_CLIP_T = 0.0012  # しなる脚の厚さ1.2mm
DRIVE_CLIP_HOOK = 0.0006  # U字座へ掛かる爪0.6mm

# サーボ保持と配線。
SERVO_CLEARANCE = 0.00035  # 片側0.35mm
CLIP_T = 0.003  # 荷重部3mm
CLIP_INTERFERENCE = 0.0001  # サーボY側を片側0.1mmで挟む
WIRE_EXIT_W = 0.008  # コネクタ8mm
WIRE_EXIT_H = 0.0045  # 4.5mm

# 材料・物理。
PLA_DENSITY = 1240.0  # kg/m3
SERVO_STALL_TORQUE = 0.245  # N m @4.8V
FRICTION_COEFF = 0.30
