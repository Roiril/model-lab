"""M 字ジョイント 2 つが直角に出会う角の、床側の部品 3 つの寸法定義。

    pipe_foot_corner_a   … M 字 A の脚 2 本 + 5 本目の柱を受ける板（pipe-foot-pair と同じ形）
    pipe_foot_corner_b   … M 字 B の脚 2 本を受ける板（3 本目なし）
    pipe_foot_corner_tie … 角の脚 2 本のソケットに上からかぶせる添え板（片側は長穴）

形は lib/pair_base.build()。1 体の L 字板は作らない: 角の脚の間隔は内側エルボの差し込み
（pipe-corner）で決まり、そのとき L 字の全長は CORNER_OFF + 160 + 2×25 ≥ 280 で
造形板 252 に入らない（2026-09-13 設計批評）。

上から見た配置（すべて mm。角の節点が原点、M 字 A の脚は x 軸上の負側、B の脚は y 軸上の負側）:
    A の脚 (-CORNER_OFF, 0), (-CORNER_OFF-160, 0)   B の脚 (0, -CORNER_OFF), (0, -CORNER_OFF-160)
    5 本目 (-FIFTH_OFF, -FIFTH_OFF) = 2 つの中央レールの延長線の交点。両方の中央レールが
    ここで柱の側面ソケット（パイプ面から 50、市販継手）に差さって止まる
    2 つの M 字は平らな面を角へ向ける。内側エルボ（R25、差し込み 30）の口が両方の面に
    突き当たり、CORNER_OFF = 19.7 + 25 + 30 = 74.7。外側エルボ（R185）は同心で目地 1.5
    板 A と板 B は床で結合しない（角の過剰拘束を床で逃がす）。板どうしの最接近は約 12
    添え板は角のソケット 2 つ（対角 105.6）にかぶせてひれの上（z=48）に乗り、
    平面のせん断だけを止める。片側を長穴にして寸法の食い違いを吸う

造形板 256（使えるのは 252）: 板 A は 244 x 238.7、板 B は 244 x 84、添え板は 150.7 x 45.1
印刷はこの向きのまま。底面が丸ごと着き、上へ行くほど細るだけなので無支持。
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


PAIR = _load("pipe_foot_pair_params", "pipe-foot-pair")
CORNER = _load("pipe_corner_params", "pipe-corner")

MM = PAIR.MM
SPAN = PAIR.SPAN                         # 160.0 M 字の脚の芯間
PLATE_R = PAIR.PLATE_R                   # 42.0 板の輪郭の半径

# --- 配置（正本は pipe-corner。ここでは読むだけ）---
CORNER_OFF = CORNER.CORNER_OFF           # 74.7 角の脚の軸 → 相手の脚列の軸線
FIFTH_OFF = CORNER_OFF + SPAN / 2        # 154.7 5 本目の軸 → 各脚列の軸線（中央レールの交点）
TIE_L = CORNER_OFF * math.sqrt(2.0)      # 105.6 角の脚 2 本の軸間（対角）

# 板 A（脚 2 本 + 5 本目）が造形板に入ること。板 B は 244 x 84 で問わない
BED = 252.0
assert SPAN + 2 * PLATE_R <= BED, "板 A の幅が造形板に入らない"
assert FIFTH_OFF + 2 * PLATE_R <= BED, "板 A の奥行きが造形板に入らない"

# 5 本目の側面ソケット（パイプ面から SIDE_JOINT_L）の先が M 字の平らな面に当たらないこと
CENTER_FREE = FIFTH_OFF - PAIR.PIPE_OD / 2 - PAIR.SIDE_JOINT_L - PAIR.JOINT_END   # 66.0 裸のパイプ
assert CENTER_FREE >= PAIR.JOINT_CLEAR, "側面ソケットの先が M 字の面に当たる"

# --- 添え板 ---
TIE_RING_ID = 2 * PAIR.BOSS_R + 0.5      # 37.1 ソケットの外径 36.6 に片側 0.25（pipe-foot-spacer と同じ）
TIE_RING_WALL = 4.0
TIE_RING_R = TIE_RING_ID / 2 + TIE_RING_WALL   # 22.55 → 板の幅 45.1
TIE_T = 5.0                              # 板厚
TIE_SLOT = 1.5                           # 片側の穴を板の長手に ±1.5 伸ばす（長穴）
TIE_CHAMFER = 1.0                        # 穴の口の面取り（上からかぶせる時のリード）
TIE_Z = PAIR.FIN_TOP_Z                   # 48.0 ひれの頂点に乗る高さ（参考）
