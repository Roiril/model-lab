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
STEM_OUTER_FLAT = 0.0097  # 柱を六角面の内側へ切り揃え、開口とは片側0.75mm離す
HOLE_CLEAR_Z0 = 0.0675  # 連結板の下部2.8mmを残して六角穴を再貫通させる
HOLE_CLEAR_Z1 = 0.0764  # 可動面上面を0.4mm越えて六角穴を確実に開ける
CELL_CLEARANCE = 0.00035  # 開口と可動面の片側隙間0.35mm

# 3群と偏心円カム
CAM_X = (0.0030, 0.0139, 0.0263)  # 中央は右保持肩を避け、内環・外環は従来位置を保つ
CAM_E = (0.003, 0.002, 0.001)  # 偏心3/2/1mm
CAM_R = 0.010  # 偏心と軸穴を差し引いても荷重部を3mm残す円カム半径10mm
CAM_T = 0.0042  # 内環・外環の軸方向厚4.2mm
CENTER_CAM_T = 0.0042  # 中央カムも4.2mm。左側0.6mmだけ保持肩を逃がす
CENTER_CAM_RELIEF_R = 0.0048  # 半径4.5mmのホーン受け保持肩と0.3mm離す
CENTER_CAM_RELIEF_X1 = 0.0015  # 逃げ後も連続したカム面を3.6mm残す
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
CENTER_CAP_PRINT_SUPPORT = (0.00175, 0.0041)  # 中央六角面の外周側を受ける1.2mm柱の中心
CENTER_CAP_PRINT_SUPPORT_D = 0.0012  # 印刷時の短い片持ちだけを分割する最小径
CARRIER_OUTER_PRINT_SUPPORT_PRODUCT_Z = 0.0086  # 外環裏面の最初の押出高さ
CARRIER_OUTER_PRINT_SUPPORT_LAYER_H = 0.0002  # delivery設定の層高
CARRIER_OUTER_PRINT_SUPPORT_GAP = 0.0002  # 支持塔上面と製品下面の材料面間隔
CARRIER_OUTER_PRINT_SUPPORT_X_HALF = 0.00155  # 3本の閉曲線を線幅ぶん覆う塔半幅
CARRIER_OUTER_PRINT_SUPPORT_Y = (-0.03205, -0.02465)  # print座標の最外閉曲線と線幅の範囲
CARRIER_OUTER_PRINT_SUPPORT_BASE_X_HALF = 0.0018  # 拡幅した塔を受けるベッド接地台半幅
CARRIER_OUTER_PRINT_SUPPORT_BASE_Y = (-0.0322, -0.0278)  # 製品外形を避けるベッド接地台のY範囲
CARRIER_OUTER_PRINT_SUPPORT_BASE_T = 0.0004  # 2層の折り取り台
CARRIER_OUTER_PRINT_SUPPORT_RAMP_Z0 = 0.0024  # 製品外形の上0.2mmから45度で広げる
CARRIER_CENTER_PRINT_SUPPORT_PRODUCT_Z = 0.0114  # 中央従動柱の最初の押出高さ
CARRIER_CENTER_PRINT_SUPPORT_GAP = 0.0002  # 支持塔と従動柱の材料面間隔
CARRIER_CENTER_PRINT_SUPPORT_LAYER_H = 0.0002  # delivery設定の層高
HOUSING_DETENT_PRINT_SUPPORT_PRODUCT_Z = 0.0448  # 板ばね先端の最初の押出高さ
HOUSING_DETENT_PRINT_SUPPORT_GAP = 0.0002  # 横穴内の折り取り柱との材料面間隔
HOUSING_DETENT_PRINT_SUPPORT_LAYER_H = 0.0002  # delivery設定の層高
COUPLER_SECOND_PRINT_SUPPORT_PRODUCT_Z = 0.0056  # ホーン受け閉環の最初の押出高さ
FOLLOWER_POST_OFFSET_X = 0.0037  # カム面と隣群の柱から外した柱中心
CENTER_FOLLOWER_POST_OFFSET_X = 0.0023  # 中央柱右端を内環webから0.3mm離す
CENTER_FOLLOWER_PAD_X1 = 0.0076  # 中央パッド右端も内環webより0.3mm内側
CENTER_GUIDE_X = 0.0003  # ホーン受け外周から中央案内を0.2mm離す

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
COUPLER_X0 = -0.0053  # 最悪の軸方向移動後もホーン腕を1.4mm以上覆う
HORN_POCKET_X1 = -0.00265  # 保持溝まで1.25mmの連続盲底を残す
COUPLER_X1 = 0.0012  # 右保持肩の終端。六角pegと主軸ソケットの位置基準
HORN_HOME_DEG = -80.0
COUPLER_PRINT_FLAT = 0.0012  # 外周肉厚1.2mmを残して横軸印刷面を広げる
COUPLER_PRINT_SUPPORT_T = 0.0006  # 六角差込下面へ届く除去式支持の幅0.6mm
COUPLER_PRINT_SUPPORT_GAP = 0.0002  # 嵌合面へ癒着させないZ間隔0.2mm
COUPLER_PRINT_LAYER_H = 0.0002  # 配布プレートの積層高さ。支持上面から差込初層下面を求める

# 軸の両持ち。左はSG92R出力軸、右は印刷した受けで支える
BEARING_X = (0.0332,)
BEARING_T = 0.0044  # 回転ポケットを除いて主軸を支える有効幅3mm
BEARING_CLEARANCE = 0.0003  # 回転隙間片側0.3mm
BEARING_OUT_R = 0.00695  # 回転穴の外側に3mmを残す支持部外半径6.95mm
BEARING_PRINT_GUSSET = 0.0038  # 右壁から軸受け下面へ伸ばす45度支持の高さと長さ
CAM_SHAFT_X1 = 0.0350  # keeper内面35.3mmとの軸方向遊び0.3mm
KEEPER_T = 0.0024  # 下から嵌める保持部2.4mm
KEEPER_GAP = 0.0002  # 軸受け支持板と保持具本体の軸方向隙間0.2mm
KEEPER_RAIL_Y = -0.015  # 保持爪の指掛かり位置
KEEPER_DETENT_ANGLE_DEG = 45.0  # 保持位置で板ばねと凹みが合う角度
KEEPER_DETENT_ARM_L = 0.008  # 板ばねの自由長8mm
KEEPER_DETENT_ARM_T = 0.0012  # 局所最小厚1.2mm
KEEPER_DETENT_INTERFERENCE = 0.00015  # 回転中の押し量0.15mm
KEEPER_DETENT_NOTCH_DEPTH = 0.0003  # 保持具外周の凹み深さ0.3mm
KEEPER_DETENT_NOTCH_W = 0.0026  # 板ばね先端の角も収める回転方向の凹み幅2.6mm

# ホーン受けと主軸を軸方向に捕える静止二股ヨーク
JOINT_COUPLER_GROOVE_X0 = -0.0014  # 1.2mm盲底より右の中実部だけに設ける保持溝
JOINT_COUPLER_GROOVE_X1 = 0.0  # 溝幅1.4mm
JOINT_COUPLER_GROOVE_R = 0.0033  # 六角peg頂点から1.22mm以上残す
JOINT_COUPLER_SHOULDER_X0 = -0.0026  # 連続盲底の内側0.05mmで円形肩を重ねる
JOINT_COUPLER_SHOULDER_X1 = 0.0012  # 溝の右へ1.2mmの保持肩を残す
JOINT_COUPLER_SHOULDER_R = 0.0045  # 中央カムの局所逃げとの半径方向隙間0.3mm
JOINT_KEEPER_LEFT_X0 = -0.0013  # 保持溝の左右へ0.1mm軸方向隙間
JOINT_KEEPER_LEFT_X1 = -0.0001  # 左フォーク厚1.2mm
JOINT_SHAFT_GROOVE_X0 = 0.0099  # 9.4mm盲穴端より0.5mm右の中実部
JOINT_SHAFT_GROOVE_X1 = 0.0113  # 軸溝幅1.4mm
JOINT_SHAFT_GROOVE_D = 0.0054  # 中実軸の円形溝径5.4mm
JOINT_KEEPER_RIGHT_X0 = 0.0100  # 軸溝と片側0.1mm隙間
JOINT_KEEPER_RIGHT_X1 = 0.0112  # 右フォーク厚1.2mm
JOINT_KEEPER_LEFT_SLOT_R = 0.0039  # 回転する6.3mm六角軸の包絡へ0.25mm以上
JOINT_KEEPER_RIGHT_SLOT_R = 0.0029  # φ5.4mm軸溝へ半径0.2mm隙間
JOINT_KEEPER_PANEL_Z0 = 0.0027  # 底板上面から0.3mm上。底板で下方を止める
JOINT_KEEPER_PANEL_Z1 = 0.0204  # ホーン受け腕の下面21.68mmから1.28mm下

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
