"""住人の箱 C4 の寸法。単位はすべて m。

座標は X=カム軸、Y=奥行、Z=上。閉じた箱は
X,Y=[-38,38]mm、Z=[0,76]mm。SG92R の寸法は正本を直接読む。
"""

import importlib.util as _ilu
import os as _os

_spec = _ilu.spec_from_file_location(
    "sg92r_photo_params",
    _os.path.join(_os.path.dirname(__file__), "..", "sg92r-photo", "params.py"),
)
SG = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(SG)

MODEL_ID = "mystery-box-sg92r-c4"

# 外装と格子
CUBE = 0.076  # 76mm
WALL = 0.0024  # 2.4mm
TOP_T = 0.002  # 2mm
BOTTOM_T = 0.0024  # 2.4mm
BOTTOM_GAP = 0.0003  # 片側0.3mm
HEX_OPEN_FLAT = 0.0112  # 六角開口の対辺11.2mm
HEX_CAP_FLAT = 0.0105  # 可動面の対辺10.5mm、片側0.35mm隙間
HEX_HOLE_FLAT = 0.0068  # 可動面中央の貫通六角穴6.8mm
HEX_PITCH = 0.0124  # 隣接中心12.4mm
HEX_CAP_T = 0.0022  # 2.2mm
HEX_HOME_TOP = 0.076  # 閉位置で外装天面と面一
WEB_T = 0.003  # 荷重を受ける連結板3mm
WEB_Z0 = 0.0647  # 最大ストローク時も天板下面を0.39mm越えない
WEB_W = 0.003  # 環状連結と案内の幅3mm
STEM_D = 0.0032  # 六角面を支える柱3.2mm
CELL_CLEARANCE = 0.00035  # 開口と可動面の片側隙間0.35mm

# 3群と偏心円カム
CAM_X = (0.0, 0.0124, 0.0248)  # 中心・内環・外環の従動位置
CAM_E = (0.003, 0.002, 0.001)  # 偏心3/2/1mm
CAM_R = 0.010  # 偏心と軸穴を差し引いても荷重部を3mm残す円カム半径10mm
CAM_T = 0.0042  # 軸方向厚4.2mm
CAM_AXIS_Z = 0.040  # カム軸高さ40mm
CAM_SHAFT_R = 0.00365  # 対辺6.3mm六角軸の頂点を包む回転半径3.65mm
CAM_SHAFT_FLAT = 0.0063  # 横向き印刷する主軸の対辺6.3mm
CAM_BORE_FLAT = 0.00665  # 六角穴の対辺6.65mm、片側0.175mm
CAM_HUB_R = 0.0051  # 軸方向位置決めだけを担い、六角穴頂点の外側に1.2mm残す
SHAFT_JOINT_FLAT = 0.0036  # ホーン受け側の六角差込3.6mm
SHAFT_JOINT_SOCKET_FLAT = 0.0039  # 差込穴3.9mm、片側0.15mm
SHAFT_JOINT_L = 0.008  # 差込長8mm
CAM_THETA_MIN_DEG = -80.0
CAM_THETA_MAX_DEG = 80.0
SERVO_MIN_DEG = 10.0
SERVO_MAX_DEG = 170.0
HOME_SERVO_DEG = 10.0
MOVE_TIME_S = 1.5
FOLLOWER_PAD_X = 0.012  # 中央群の片側二本柱も受ける従動パッド幅12mm
FOLLOWER_PAD_Y = 0.008  # 偏心3mmでも接点を端から1mm内側に保つ
FOLLOWER_PAD_T = 0.003  # 荷重を受ける従動パッド3mm
FOLLOWER_POST_T = 0.003  # 荷重を受ける柱3mm
FOLLOWER_POST_OFFSET_X = 0.0046  # カム面から外した柱中心

# 鉛直案内。対向する案内で片側荷重のこじれを抑える
GUIDE_CLEARANCE = 0.00035  # 片側0.35mm
GUIDE_LUG = 0.003  # 可動側の角柱3mm
GUIDE_WALL = 0.003  # 固定側案内壁3mm
GUIDE_Z0 = 0.0605  # 独立案内枠の下面60.5mm。カム軸受け掃引上端より上
GUIDE_Z1 = 0.0642  # C形案内上端64.45mm。最大位置でも2.94mmかかる
GUIDE_LUG_Z0 = 0.0556  # 可動案内柱下端55.6mm。最大位置でも案内内に2.94mm残る
GUIDE_FRAME_T = 0.003  # 平面印刷する案内支持枠3mm
GUIDE_FRAME_RAIL = 0.003  # 外周と接続腕の幅3mm

# SG92R。正本座標(Xs,Ys,Zs)を(X,Y,Z)=(Zs+SERVO_X0, Xs, Ys+SERVO_Z)へ写す
SERVO_X0 = -0.035  # 本体底面X=-35mm、左内壁との隙間0.6mm
SERVO_Y_OFFSET = 0.0  # 正本の出力軸をカム軸Y=0へ合わせる
SERVO_Z = 0.040  # 出力軸中心Z=40mm
SERVO_CLR = 0.00035  # 本体保持の片側隙間0.35mm
SERVO_TRAY_T = 0.0024  # 保持台2.4mm
SERVO_CLIP_T = 0.0025  # 着脱クリップ2.5mm
SERVO_CLIP_HOOK = 0.001  # 爪のかかり1mm
SERVO_CLIP_FLEX_L = 0.018  # しなる脚の長さ18mm
WIRE_EXIT_W = 0.008  # コネクタが通る幅8mm
WIRE_EXIT_H = 0.0045  # コネクタが通る高さ4.5mm

# ホーン受け。SG正本の非対称外形を使い、口だけ広げる
HORN_CLEARANCE = 0.00015  # 片側0.15mm、仮値
HORN_MOUTH_EXTRA = 0.0002  # 入口だけ片側0.2mm追加
HORN_POCKET_EXTRA = 0.0001  # 腕厚へ0.1mm追加
COUPLER_X0 = -0.0047  # ホーン腕下面より0.2mm左
COUPLER_X1 = -0.0024  # 中心カム手前の軸本体との接続端
HORN_HOME_DEG = -80.0

# 軸の両持ち。左はSG92R出力軸、右は印刷した受けで支える
BEARING_X = (0.0332,)
BEARING_T = 0.0044  # 回転ポケットを除いて主軸を支える有効幅3mm
BEARING_CLEARANCE = 0.0003  # 回転隙間片側0.3mm
BEARING_OUT_R = 0.00695  # 回転穴の外側に3mmを残す支持部外半径6.95mm
KEEPER_T = 0.0024  # 下から嵌める保持部2.4mm
KEEPER_GAP = 0.0002  # 軸受け支持板と保持具本体の軸方向隙間0.2mm
KEEPER_RAIL_Y = -0.015  # 保持爪の指掛かり位置
KEEPER_DETENT_ANGLE_DEG = 45.0  # 保持位置で板ばねと凹みが合う角度
KEEPER_DETENT_ARM_L = 0.008  # 板ばねの自由長8mm
KEEPER_DETENT_ARM_T = 0.0012  # 局所最小厚1.2mm
KEEPER_DETENT_INTERFERENCE = 0.00015  # 回転中の押し量0.15mm
KEEPER_DETENT_NOTCH_DEPTH = 0.0003  # 保持具外周の凹み深さ0.3mm
KEEPER_DETENT_NOTCH_W = 0.0026  # 板ばね先端の角も収める回転方向の凹み幅2.6mm

# 底板の工具不要スナップ
BOTTOM_LIP = 0.003  # 周囲の差し込み幅3mm
BOTTOM_TAB_T = 0.0018  # しなる爪1.8mm
BOTTOM_TAB_L = 0.014  # 自由長14mm
BOTTOM_TAB_HOOK = 0.0007  # かかり0.7mm

# 物理
PLA_DENSITY = 1240.0  # kg/m3
SERVO_STALL_TORQUE = 0.245  # N m、2.5kgf cm @4.8V
GUIDE_FRICTION_MU = 0.30  # 乾いたPLA同士の保守的な仮値
GRAVITY = 9.80665  # m/s2
