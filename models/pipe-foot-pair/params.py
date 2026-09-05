"""M 字ジョイントの脚 2 本を、床で 1 枚の板にまとめて受けるベースの寸法定義。

pipe-foot（フランジ足）と pipe-foot-spacer（芯間合わせ板）を 1 部品にしたもの。
ねじ止めをやめたので、ねじ穴・そのまわりのふくらみ・ねじ側のリブは無い。

すべて mm。ローカル座標: 底面の中心が原点、+Z が上、ソケットは x = ±SPAN/2。
使うときはこの X 軸が M 字ジョイントの Y 軸（脚が並ぶ向き）に重なる。

相手から引き継ぐ寸法:
    芯間   = M 字ジョイントの脚ソケットと同じ 160mm
    全幅   = M 字ジョイントの外形と同じ 196.6mm（両端を平らに切って出す）
    ソケット = pipe-foot と同じ（座面 30mm・差し込み 55mm・口元の絞り 12mm）

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

# --- 芯間と全幅 ---
SPAN = 2 * J.SIDE_Y                    # 160.0 脚パイプの芯間
HALF_W = J.SIDE_Y + J.LEG_HUB_D / 2    # 98.3 M 字ジョイントの外形の半分

# ⚠ 両端を切る面は、ソケットの外周にちょうど接する。M 字ジョイントの脚の柱と
#   このソケットが同じ肉厚 4.0mm で同じパイプを咥えているから成り立っている。
#   どちらかの肉厚を変えると接線でなくなり、端の面に段差か浅い交差が出る。
assert abs(HALF_W - (SPAN / 2 + BOSS_R)) < 1e-9, \
    "端の面がソケットに接していない。M 字ジョイントの柱とソケットの肉厚を揃える"

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
FIN_OUT_R = F.RIB_OUT_R          # 33.0 外端
FIN_OUT_H = 5.0                  # 外端を板の上面から立てる高さ。FILLET_R の 2 倍を確保する
FIN_TOP_Z = F.RIB_TOP_Z          # 48.0 ソケット側の付け根の高さ

assert FIN_OUT_R < PLATE_R, "ひれが板からはみ出す"

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
