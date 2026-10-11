"""C4-2。寸法はm。SG92Rは確定した正本を読み込む。"""
import importlib.util as _ilu
from pathlib import Path as _Path

_spec = _ilu.spec_from_file_location("sg92r_c42", _Path(__file__).resolve().parents[1] / "sg92r-photo" / "params.py")
SG = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(SG)

MODEL_ID = "mystery-box-sg92r-c4-2"
CUBE = 0.110  # 110mm角
WALL = 0.0024  # 外装2.4mm
FRAME_T = 0.0032  # 荷重を受ける板3.2mm
HEX_PITCH = 0.016  # 六角中心の間隔16mm
HEX_OPEN_FLAT = 0.0140  # 開口対辺14mm
HEX_CAP_FLAT = 0.0133  # 六角面対辺13.3mm、片側0.35mm
HEX_HOLE_FLAT = 0.0093  # 貫通穴対辺9.3mm、面の壁2mm
HEX_CAP_T = 0.0032  # 可動面3.2mm
GROUPS = ("center", "upper_left", "upper_right", "lower_pair")
GROUP_LABELS = ("中央", "左上", "右上", "下側の二か所")
CELL_QR = {
    "center": ((0, 0),),
    "upper_left": ((-1, 0), (-1, 1), (-2, 2)),
    "upper_right": ((1, 0), (0, 1), (0, 2)),
    "lower_pair": ((-1, -1), (0, -1), (0, -2), (2, -1), (1, -1), (2, -2)),
    "fixed": ((-2, 0), (2, 0), (-2, 1), (1, 1), (-1, 2), (1, -2)),
}  # 19セル。左右の可動群と下側二か所を鏡映対称にする
SELECT_DEG = (90.0, 50.0, 130.0, 165.0)
PATTERNS = (("flat", "平面", 15.0), ("upper_left", "左上", 50.0),
            ("center", "中央", 90.0), ("upper_right", "右上", 130.0),
            ("lower_pair", "下側の二か所", 165.0))
SERVO_MIN_DEG = 15.0
SERVO_MAX_DEG = 165.0
HOME_SERVO_DEG = 15.0
ASSEMBLY_SERVO_DEG = 90.0
MOVE_TIME_S = 3.0  # 全角度を動かす最短時間3秒
DENT_DEPTH = 0.004  # 選択された場所が4mm沈む
DENT_DWELL_DEG = 6.0  # 底の平坦部分は中心から各6度
DENT_HALF_WIDTH_DEG = 30.0  # 谷の半幅30度、斜面24度
CAM_RADII = (0.033, 0.037, 0.041, 0.045)  # 独立トラック半径33/37/41/45mm
CAM_TRACK_W = 0.0036  # トラック幅3.6mm
CAM_OUTER_R = 0.049  # 円盤外径98mm
CAM_BASE_T = 0.0032  # 円盤の基板3.2mm
CAM_BASE_Z = 0.0441  # 円盤の下面44.1mm
FOLLOWER_ANGLES_DEG = (0.0, 120.0, 60.0, 270.0)
FOLLOWER_RADIAL_W = 0.0020  # 接点の径方向幅2.0mm、端まで各0.8mm
FOLLOWER_ARC_L = 0.0024  # 周方向長さ2.4mm。斜めの足を3.6mm角案内へ通す
FOLLOWER_T = 0.0048  # 接点の上下厚4.8mm。案内棒下端を谷外平面から0.6mm離す
GUIDE_CLR = 0.00020  # 案内の片側隙間0.20mm
GUIDE_MIN_ENGAGEMENT = 0.008  # 両端で8mm以上案内に残す
GUIDE_LUG = 0.0032  # 可動角柱の一辺3.2mm
GUIDE_WALL = 0.0016  # 静止案内の壁1.6mm
GUIDE_INNER_R = 0.020  # 内側案内中心半径20mm、固定六角穴から0.7mm以上離す
GUIDE_Z0 = 0.072  # 静止案内の下面72mm
GUIDE_Z1 = 0.091  # 静止案内の上面91mm
GUIDE_LEDGE_INNER = 0.0470  # 案内枠の四隅支持内端47mm
GUIDE_LEDGE_OUTER = 0.0528  # 外壁へ0.2mm重ねる支持外端52.8mm
GUIDE_LEDGE_Z0 = 0.0728  # 四隅支持下面72.8mm
GUIDE_LEDGE_Z1 = 0.0760  # 案内枠下面へ直接接する支持上面76mm
GUIDE_XY_STOP_INNER = 0.0504  # 案内枠端との片側隙間0.2mm
GUIDE_XY_STOP_Z0 = 0.0757  # 対角二隅のL字案内下面
GUIDE_XY_STOP_Z1 = 0.0802  # L字案内上面
GUIDE_XY_STOP_CHAMFER = 0.0004  # 上端導入面の後退量0.4mm
GUIDE_TOP_POST_INNER = 0.0470  # 天板側の上抜け止め柱内端
GUIDE_TOP_POST_OUTER = 0.0500  # 上抜け止め柱外端
GUIDE_TOP_POST_Z0 = 0.0795  # 案内枠上面との隙間0.3mm
CARRIER_WEB_Z0 = 0.098  # 上段の隠し梁下面98mm
MOVING_WEB_Z0 = 0.1036  # 非中央3群の梁下面103.6mm、下降時99.6mm
CENTER_ARM_Z0 = 0.0961  # 中央群の梁下面96.1mm、下降時も案内上面から1.1mm離す
FOLLOWER_HOME_Z = 0.0513  # 平面姿勢のカム接触面51.3mm
AXIAL_CLR = 0.0003  # 円盤/ホーン受け抜け止めの遊び0.3mm
KEEPER_TAB_T = 0.0012  # 円盤止め輪の爪厚1.2mm
KEEPER_TAB_FREE_L = 0.007  # 止め輪下面47.6mmから爪上面40.6mmまで7mm
KEEPER_TAB_DEFLECTION = 0.0005  # 組立時の撓み0.5mm、ひずみ1.836735%
KEEPER_INNER_R = 0.0472  # 円盤平坦フランジだけを捕える内半径47.2mm
KEEPER_OUTER_R = 0.0512  # 斜め四方向の着脱爪を止め輪へ重ねる外半径51.2mm
KEEPER_TAB_INNER = 0.0507  # 支持環外半径50.5mmとの隙間0.2mm
KEEPER_HOOK_INNER = 0.0500  # 支持環への掛かり0.5mm
KEEPER_HOOK_Z0 = 0.0394  # 爪下面39.4mm
KEEPER_HOOK_Z1 = 0.0406  # 支持環下面40.9mmから下方0.3mm
KEEPER_ANGLES_DEG = (45, 135, 225, 315)  # 四方の支持柱を避ける
EXTERIOR_TAB_T = 0.0012  # 底板/天板の着脱爪厚1.2mm
EXTERIOR_TAB_CLR = 0.0002  # 閉位置の爪と内壁の隙間0.2mm
EXTERIOR_HOOK_DEFLECTION = 0.0005  # 内壁を通るための最大撓み0.5mm
BOTTOM_HOOK_Z0 = 0.0112  # 底板上面3.2mmから最短自由長8mm
BOTTOM_HOOK_Z1 = 0.0132  # 爪掛かり上面13.2mm
BOTTOM_TAB_Z1 = 0.0140  # 底板の着脱爪上端14mm
BOTTOM_POCKET_Z0 = 0.0110  # 爪との下方遊び0.2mm
BOTTOM_POCKET_Z1 = 0.0140  # 取付ポケット上端14mm
BOTTOM_LATCH_ANGLES_DEG = (90, 270)  # 配線出口と別の二面へ置く
FACE_POCKET_Z0 = 0.0962  # 天板爪下面96.5mmへの下方余裕0.3mm
FACE_POCKET_Z1 = 0.0985  # 天板爪上面へ直接接する上方保持面
CAM_RADIAL_BEARING_R = 0.010  # 円盤中央boss外半径10mm
CAM_RADIAL_BEARING_INNER_R = 0.0102  # 径方向受け内半径、片側0.2mm隙間
CAM_RADIAL_BEARING_OUTER_R = 0.012  # 径方向受け外半径12mm
CAM_RADIAL_BEARING_Z0 = 0.0478  # 径方向受け下面
CAM_RADIAL_BEARING_Z1 = 0.0527  # 径方向受け上面
CAM_RADIAL_BEARING_CHAMFER = 0.0005  # 下面内周の導入面0.5mm
KEY_TOP_STOP_R = 0.0122  # 駆動キー頭の上抜け止め円板半径12.2mm
SERVO_Z0 = 0.004  # 正本本体底面4mm
SERVO_CLR = 0.00035  # 本体保持の片側隙間0.35mm
SERVO_X_STOP_T = 0.0024  # 底板に一体化した本体X両端止め壁2.4mm
SERVO_X_STOP_Z1 = 0.0072  # 配線中心Z9mmを避ける端壁上端7.2mm
HORN_CLR = 0.00015  # 正本ホーンポケット片側0.15mm、試し刷りで確認
KEY_FLAT = 0.010  # 正逆を伝える角形キーの幅10mm
KEY_SOCKET_FLAT = 0.0102  # 穴10.2mm、片側0.1mm、試し刷りで確認
COUPLER_KEY_BOSS_R = 0.0086  # 角穴の角から1.39mm残す中央座半径8.6mm
COUPLER_Z0 = 0.0343  # ホーン受け下面34.3mm
COUPLER_Z1 = 0.0405  # ホーン受け上面40.5mm
HORN_POCKET_Z1 = 0.03615  # ホーンポケット盲底下面36.15mm
KEY_SOCKET_Z0 = 0.03735  # 角キー盲穴底37.35mm、ホーン側へ1.2mm残す
DRIVE_KEY_Z0 = 0.03755  # 角キー下面、盲穴底から0.2mm離す
DRIVE_KEY_Z1 = 0.0507  # 上端頭へ0.2mm重ねて一体化
KEY_HEAD_D = 0.017  # 円盤からの上抜けを止める円形頭17mm
KEY_HEAD_Z0 = 0.0505  # 円盤boss上面との隙間0.2mm
KEY_HEAD_Z1 = 0.0517  # 上側静止止め面との隙間0.3mm
KEY_TOP_STOP_Z0 = 0.052  # 案内枠側の上抜け止め下面
KEY_TOP_STOP_Z1 = 0.0552  # 上抜け止め厚3.2mm
WIRE_EXIT_W = 0.008  # コネクタ出口幅8mm
WIRE_EXIT_H = 0.0045  # コネクタ出口高さ4.5mm
PLA_DENSITY = 1240.0  # kg/m3
SERVO_STALL_TORQUE = 0.245  # Nm、製造元2.5kgf cm @4.8V
GUIDE_FRICTION_MU = 0.30  # 乾燥した印刷面の摩擦仮値
GRAVITY = 9.80665  # m/s2
