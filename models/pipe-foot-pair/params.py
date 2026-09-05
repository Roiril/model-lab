"""M 字ジョイントの脚 2 本を、床で 1 枚の板にまとめて受けるベースの寸法定義。

pipe-foot（フランジ足）と pipe-foot-spacer（芯間合わせ板）を 1 部品にしたもの。
ねじ止めをやめたので、ねじ穴・そのまわりのふくらみ・ねじ側のリブは無い。

すべて mm。ローカル座標: 底面の中心が原点、+Z が上、ソケットは x = ±SPAN/2。
使うときはこの X 軸が M 字ジョイントの Y 軸（脚が並ぶ向き）に重なる。

相手から引き継ぐ寸法:
    芯間   = M 字ジョイントの脚ソケットと同じ 160mm
    ソケット = pipe-foot と同じ（座面 30mm・差し込み 55mm・口元の絞り 12mm）

全幅は長丸のまま 244mm。M 字ジョイントの外形（196.6mm）に合わせて両端を平らに
切ることもできるが、接地面が 18982 → 16413mm2 へ 14% 減る。接地面を優先した
（2026-09-05 ユーザー判断）。造形板 256mm に対して片側 6mm しか余らないので、
ブリムは付けられない。

印刷はこの向きのまま。底面が丸ごと着き、外形は上へ行くほど細るだけなので無支持。
"""
import importlib.util
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
MOUTH_TAPER = F.MOUTH_TAPER      # 12.0 口元で絞る長さ
TIP_R = F.TIP_R                  # 15.3 口元の外径 30.6
HUB_T = F.HUB_T                  # 8.0 ソケットまわりの板厚
DISC_R = F.DISC_R                # 34.0 板厚を 8mm から 5mm へ落とす半径
CONE_BASE_R = F.CONE_BASE_R      # 26.0 台座の根元の半径

# --- 芯間 ---
SPAN = 2 * J.SIDE_Y                    # 160.0 脚パイプの芯間。M 字ジョイントの脚と同じ

# --- 床に着く板 ---
# 輪郭はソケット 2 つを包む長丸。ねじ穴のふくらみが無くなったぶん、
# 半径を足を単体で使っていたときの 34 から広げて接地面を稼ぐ。
PLATE_R = 42.0                   # ソケット軸からの半径。奥行きは 84mm
PLATE_T = F.FLANGE_T             # 5.0 縁の板厚

assert PLATE_R > DISC_R, "板が足の座より小さい。段が消える"

# --- 背骨（ソケット 2 つを繋ぐ縦板）---
# 5mm の板だけだと台座の根元で曲げ応力が材料の強度を超える（pipe-foot で確認済み）。
# 単体の足では内向きのリブ 2 枚だったものが、2 個つながったことで 1 本の通し材になる。
# 上端はソケットの高さから中央へ向かって下がる弧。曲げを受けるのは根元だけなので、
# 中央は低くてよい。低くするほど部品が軽く見える。
SPINE_T = 8.0                    # 厚み
SPINE_TOP_Z = F.RIB_TOP_Z        # 48.0 ソケット側の付け根の高さ
SPINE_MID_Z = 14.0               # 中央での高さ。曲げを受けるのは根元だけなので中央は低くてよい
SPINE_LAP = 1.0                  # 板へ食い込ませる量（面どうしの接触を作らない）
SPINE_SEG = 48                   # 弧の分割数

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
