"""M 字ジョイント 2 つが直角に出会う角で、脚 4 本と 5 本目の脚を 1 枚の板で受けるベース。

pipe-foot-pair（脚 2 本 + 3 本目）を 2 つ直角に置き、角で 1 体にしたもの。
別々の板だと角の脚どうしが 84mm より近づけない。1 体にして角の脚を寄せる
（2026-09-11 ユーザーのスケッチ「近づけるために一体化」）。

すべて mm。ローカル座標: 底面が z=0、+Z が上。刷る向きのまま。
    角の節点 = 原点。そこから -X へ伸びる脚列と -Y へ伸びる脚列
    X 列の脚: (-CORNER_OFF, 0) と (-CORNER_OFF - SPAN, 0)   ← M 字ジョイント A
    Y 列の脚: (0, -CORNER_OFF) と (0, -CORNER_OFF - SPAN)   ← M 字ジョイント B
    5 本目  : (-FIFTH_OFF, -FIFTH_OFF)。両方の脚列のパイプ外面から FIFTH_GAP の隙間
ユーザーのスケッチ（角が右下、列が上と左へ伸びる）を反時計回りに 90° 回した向き。
造形板の手前左（除外域 18 x 28mm）に、板の無い側（斜辺の外）が来るようにするため。

角の脚の寄せ方（CORNER_OFF）:
    M 字ジョイントの本体は脚の軸から、閉じた端の側へ 19.7、レールが入る側へ 34.3
    はみ出す（pipe-joint: BODY_T 54 / LEG_X -7.3）。2 つのジョイントの閉じた端を
    角に向けて置く前提で、本体どうしの隙間が CORNER_OFF - 19.7 - 18.3 = 4mm になる 42 にした。
    レールが角の側から入る向きで使うなら 53 以上が要る（そのときは FIFTH との干渉も見直す）。

造形板に収める:
    脚列の長さは SPAN + CORNER_OFF = 202。板を軸から PLATE_R = 42 まで出すと 286 になり
    X1C の 256 に入らない。外側（角の外側と列の遠い端）だけ軸から EDGE_CUT = 25 で
    平らに切って 252 に収める。切った面はソケットの台座（r 26）を 5mm ほどかすめる。
    造形板の縁まで 2mm。ブリムは付けられない。
"""
import importlib.util
import os


def _load(name, model):
    path = os.path.join(os.path.dirname(__file__), os.pardir, model, "params.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PAIR = _load("pipe_foot_pair_params", "pipe-foot-pair")

MM = PAIR.MM

# --- パイプとソケット（pipe-foot-pair と同じ）---
PIPE_OD = PAIR.PIPE_OD           # 28.0
BORE_D = PAIR.BORE_D             # 28.6
BOSS_R = PAIR.BOSS_R             # 18.3 ソケット外径 36.6
SEAT_Z = PAIR.SEAT_Z             # 30.0 パイプの下端の高さ
BOSS_TOP = PAIR.BOSS_TOP         # 85.0 全高
MOUTH_TAPER = PAIR.MOUTH_TAPER   # 12.0
TIP_R = PAIR.TIP_R               # 15.3
HUB_T = PAIR.HUB_T               # 8.0
DISC_R = PAIR.DISC_R             # 34.0
CONE_BASE_R = PAIR.CONE_BASE_R   # 26.0

# --- 脚の配置 ---
SPAN = PAIR.SPAN                 # 160.0 M 字ジョイントの脚の芯間
CORNER_OFF = 42.0                # 角の脚の軸から、もう一方の列の軸線までの距離
FIFTH_GAP = PAIR.THIRD_GAP       # 55.0 5 本目とそれぞれの列のパイプ外面どうしの隙間
FIFTH_OFF = FIFTH_GAP + PIPE_OD  # 83.0 5 本目の軸から、それぞれの列の軸線までの距離

A1 = (-CORNER_OFF, 0.0)                  # X 列、角に近い脚
A2 = (-CORNER_OFF - SPAN, 0.0)           # X 列、遠い脚
B1 = (0.0, -CORNER_OFF)                  # Y 列、角に近い脚
B2 = (0.0, -CORNER_OFF - SPAN)           # Y 列、遠い脚
FIFTH = (-FIFTH_OFF, -FIFTH_OFF)         # 5 本目

# 角の脚 2 本の軸間の下限。ジョイント本体は脚の軸から閉じた端まで JOINT_END、
# 脚の並ぶ向きには BOSS_R はみ出す。閉じた端を角に向けたとき、本体どうしの隙間が 3mm 以上
JOINT_END = 19.7
assert CORNER_OFF >= JOINT_END + BOSS_R + 3.0, "角の脚が近すぎて M 字ジョイントの本体どうしが当たる"
# 5 本目のパイプ（r 14）が、閉じた端を角に向けたジョイント本体（軸線から JOINT_END まで）に当たらない
assert FIFTH_OFF - PIPE_OD / 2 > JOINT_END + 3.0, "5 本目のパイプが M 字ジョイントの本体に当たる"

# --- 床に着く板 ---
PLATE_R = PAIR.PLATE_R           # 42.0 ソケット軸からの半径（凸包の丸み）
PLATE_T = PAIR.PLATE_T           # 5.0 縁の板厚
EDGE_CUT = 25.0                  # 外側の縁を軸から何 mm で平らに切るか
BED = 256.0                      # X1C の造形板
BED_MARGIN = 2.0                 # 縁に残す余白

EXTENT = SPAN + CORNER_OFF + 2 * EDGE_CUT       # 252.0 部品の全幅（= 奥行き）
assert EXTENT <= BED - 2 * BED_MARGIN, f"造形板に入らない: {EXTENT}"
assert EDGE_CUT > BOSS_R + 2.0, "切り落としがソケットの筒に掛かる"

# --- 背骨（脚列を通す縦板）と枝 ---
SPINE_T = PAIR.SPINE_T           # 8.0
SPINE_TOP_Z = PAIR.SPINE_TOP_Z   # 48.0 ソケット側の付け根の高さ
SPINE_MID_Z = PAIR.SPINE_MID_Z   # 14.0 脚 2 本の中央での高さ
SPINE_LAP = PAIR.SPINE_LAP       # 1.0 板へ食い込ませる量
SPINE_SEG = PAIR.SPINE_SEG       # 48 脚 2 本のあいだの分割数
BRANCH_SEG = PAIR.BRANCH_SEG     # 24 枝の分割数
# 脚から角までは、脚 2 本のあいだと同じ曲率のまま角で最も低くなる弧。
# 角に近い脚 2 本の根元が集まる所なので、角は低くしない（CORNER_OFF 42 で 38.6）
SPINE_CURV = (SPINE_TOP_Z - SPINE_MID_Z) / (SPAN / 2) ** 2   # 0.0053 /mm
CORNER_Z = SPINE_TOP_Z - SPINE_CURV * CORNER_OFF ** 2         # 38.6 角での高さ

# --- 横のひれ ---
# 外側（切り落とす側）には出せない。板が平らな所で終われないため（pipe-foot-pair の注意書き）
FIN_T = PAIR.FIN_T               # 6.0
FIN_OUT_R = PAIR.FIN_OUT_R       # 36.0
FIN_OUT_H = PAIR.FIN_OUT_H       # 5.0
FIN_TOP_Z = PAIR.FIN_TOP_Z       # 48.0

# --- 仕上げ ---
FILLET_R = PAIR.FILLET_R         # 2.5
FILLET_ANGLE = PAIR.FILLET_ANGLE
FILLET_SEG = PAIR.FILLET_SEG
BASE_ROUND = PAIR.BASE_ROUND     # 1.5

# --- メッシュ品質 ---
SEG = PAIR.SEG                   # 96
CONE_SEG = PAIR.CONE_SEG         # 24
