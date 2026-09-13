"""M 字ジョイントの脚 2 本と、その横に立つ 3 本目の脚を、床で 1 枚の板に
まとめて受けるベースの寸法定義。

pipe-foot（フランジ足）と pipe-foot-spacer（芯間合わせ板）を 1 部品にしたもの。
ねじ止めをやめたので、ねじ穴・そのまわりのふくらみ・ねじ側のリブは無い。
2026-09-11 に 3 本目のソケットを足した。3 本目は中央レールを受ける柱で、位置は
M 字の本体の面から側面ソケット 50 が収まる所（THIRD_OFF、2026-09-13 に決め直し）。

すべて mm。ローカル座標: 底面の中心が原点、+Z が上。
ソケットは x = ±SPAN/2（M 字の脚 2 本）と (0, THIRD_OFF)（3 本目）。
使うときはこの X 軸が M 字ジョイントの Y 軸（脚が並ぶ向き）に重なり、
+Y が M 字の平らな面の側（中央レールが抜けて来る側）になる。

相手から引き継ぐ寸法:
    芯間   = M 字ジョイントの脚ソケットと同じ 160mm
    ソケット = pipe-foot と同じ（座面 30mm・差し込み 55mm・口元の絞り 12mm）

板は 3 つのソケットを包む凸包（角の丸い三角形）。全幅 244mm・奥行き 173mm。
角用（pipe-foot-corner）は同じ形づくり（pair_base.py）で 3 本目を 5 本目の位置に置く。
M 字ジョイントの外形（196.6mm）に合わせて両端を平らに切ることもできるが、
接地面を優先して長丸のまま（2026-09-05 ユーザー判断）。造形板 256mm に対して
片側 6mm しか余らないので、ブリムは付けられない。

印刷はこの向きのまま。底面が丸ごと着き、外形は上へ行くほど細るだけなので無支持。
"""
import importlib.util
import math
import os


def _load(name, model):
    path = os.path.join(os.path.dirname(__file__), os.pardir, model, "params.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


J = _load("pipe_joint_params", "pipe-joint")
F = _load("pipe_foot_params", "pipe-foot")

MM = F.MM

# --- パイプとソケット（pipe-foot からそのまま）---
PIPE_OD = F.PIPE_OD              # 28.0
CLEAR = F.CLEAR                  # 0.30
BORE_D = F.BORE_D                # 28.6
WALL = F.WALL                    # 4.0
BOSS_R = F.BOSS_R                # 18.3 ソケット外径 36.6
SEAT_Z = F.SEAT_Z                # 30.0 パイプの下端の高さ
SOCKET_DEPTH = F.SOCKET_DEPTH    # 55.0 差し込み長
BOSS_TOP = F.BOSS_TOP            # 85.0 全高
# 口元は外側を絞らず、内側を漏斗にする（2026-09-13）。外側を 1.0mm の壁まで絞ると
# 穴の口に面取りが入らない。脚を上から落とすときの位置合わせは、この漏斗が受け持つ
MOUTH_TAPER = 0.0                # 外側の絞りなし（筒は上まで 36.6）
TIP_R = BOSS_R                   # 18.3
FUNNEL_L = 6.0                   # 漏斗の深さ
FUNNEL_DR = 2.5                  # 口で穴の半径がこれだけ広がる（⌀28.6 → ⌀33.6。壁は 1.5 残る）
assert BOSS_R - (BORE_D / 2 + FUNNEL_DR) >= 1.2, "漏斗の口で壁が薄すぎる"
HUB_T = F.HUB_T                  # 8.0 ソケットまわりの板厚
DISC_R = F.DISC_R                # 34.0 板厚を 8mm から 5mm へ落とす半径
CONE_BASE_R = F.CONE_BASE_R      # 26.0 台座の根元の半径

# --- 芯間 ---
SPAN = 2 * J.SIDE_Y                    # 160.0 脚パイプの芯間。M 字ジョイントの脚と同じ

# --- 3 本目の柱（中央レールを受ける）---
# 2 本の脚の芯を結ぶ線の中点から、横（+Y）へ THIRD_OFF の所に軸を置く。
# 中央レールは M 字ジョイントの平らな面を抜けて、3 本目のパイプ側面に付く
# 横向きソケット（市販継手、パイプ面から SIDE_JOINT_L）に差さって止まる。
# ユーザーの当初指示は「パイプ外面どうし最低 55」（2026-09-11）だったが、M 字の本体は
# 脚パイプの面より JOINT_END - 14 = 5.7 外へ出るので、55 だとソケットの先が本体に
# 0.7 食い込む。位置は「本体の面 + ソケット + 隙間」から決める（2026-09-13）。
# 部品を Z まわりに 180° 回せば -Y 側になるので、向きは組むときに選べる。
JOINT_END = J.LEG_X - J.X_BOT    # 19.7 M 字の本体が脚の軸から平らな面まで出る量
SIDE_JOINT_L = 50.0              # 3 本目の側面ソケットの長さ（パイプ面から。ユーザー指定）
JOINT_CLEAR = 5.0                # ソケットの先と M 字の面のあいだに残す隙間
THIRD_OFF = JOINT_END + SIDE_JOINT_L + PIPE_OD / 2 + JOINT_CLEAR   # 88.7 軸線からの距離
THIRD_GAP = THIRD_OFF - PIPE_OD  # 60.7 パイプ外面どうしの隙間（参考。55 より広い）
THIRD = (0.0, THIRD_OFF)         # 軸の位置 (x, y)

assert THIRD_OFF - PIPE_OD / 2 - SIDE_JOINT_L > JOINT_END, "側面ソケットの先が M 字の本体に食い込む"

# --- 床に着く板 ---
# 輪郭はソケット 3 つを包む凸包（角の丸い三角形）。ねじ穴のふくらみが無くなったぶん、
# 半径を足を単体で使っていたときの 34 から広げて接地面を稼ぐ。
PLATE_R = 42.0                   # ソケット軸からの半径
PLATE_T = F.FLANGE_T             # 5.0 縁の板厚

assert PLATE_R > DISC_R, "板が足の座より小さい。段が消える"

# --- 背骨（ソケットを繋ぐ縦板）---
# 5mm の板だけだと台座の根元で曲げ応力が材料の強度を超える（pipe-foot で確認済み）。
# 単体の足では内向きのリブ 2 枚だったものが、2 個つながったことで 1 本の通し材になる。
# 上端はソケットの高さから中央へ向かって下がる弧。曲げを受けるのは根元だけなので、
# 中央は低くてよい。低くするほど部品が軽く見える。
# 3 本目のソケットへは、主材の中央から枝を 1 本出す（T 字）。枝の上端も同じ弧。
SPINE_T = 8.0                    # 厚み
SPINE_TOP_Z = F.RIB_TOP_Z        # 48.0 ソケット側の付け根の高さ
SPINE_MID_Z = 14.0               # 中央での高さ。曲げを受けるのは根元だけなので中央は低くてよい
SPINE_LAP = 1.0                  # 板へ食い込ませる量（面どうしの接触を作らない）
SPINE_SEG = 48                   # 主材の弧の分割数（片側 24）
BRANCH_SEG = 24                  # 枝の弧の分割数

# --- 横のひれ（ソケットの左右）---
# 背骨と直交する向きの曲げを受ける。形は pipe-foot のリブと同じ。
FIN_T = F.RIB_T                  # 6.0
# ⚠⚠ 外端は板が平らな所（r > DISC_R）で終わらせる。単体の足と同じ 33 にすると、
#   板厚が 8 → 5mm へ落ちる段（r = 26..34）の途中で終わり、bevel がそこに
#   穴を開ける（面が 1 枚しかつながらないエッジが 6 本。Blender 5.1 で実測）。
#   端を切る boolean を入れていたあいだは、その boolean がメッシュを作り直すので
#   穴が塞がって見えていた。丸いまま出すことにして初めて表に出た。
FIN_OUT_R = 36.0                 # 外端。段の外、板の縁から 6mm 内側
FIN_OUT_H = 5.0                  # 外端を板の上面から立てる高さ。FILLET_R の 2 倍を確保する
FIN_TOP_Z = F.RIB_TOP_Z          # 48.0 ソケット側の付け根の高さ

assert DISC_R < FIN_OUT_R < PLATE_R - 2 * F.FILLET_R, \
    "ひれの外端が段の上か、板の縁の丸みに掛かっている"

# --- 仕上げ ---
FILLET_R = F.FILLET_R            # 2.5
FILLET_ANGLE = F.FILLET_ANGLE    # 25.0
FILLET_SEG = F.FILLET_SEG
BASE_ROUND = F.BASE_ROUND        # 1.5 底の角丸（後で平らに切る分）

# --- メッシュ品質 ---
SEG = F.SEG                      # 96
CONE_SEG = F.CONE_SEG            # 24

# --- 参照パイプ（フィット確認用。印刷対象ではない）---
REF_LEN = 200.0
