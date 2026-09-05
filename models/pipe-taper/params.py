"""M 字ジョイントの平らな側へ足す、パイプ用のすり鉢リング。

ジョイントは +X 側だけが襟からパイプ面まで落ちる非対称形で、造形板に伏せる
-X 側は平らに切り落としてある。この部品を反対側から差してその面へ突き当てると、
どちらの側からもパイプ面まで滑らかに落ちる。

寸法は pipe-joint の params.py から取る。合わせ面の径まで向こうに追従するので、
ジョイントの襟や角丸をいじってもここは直さなくてよい。

印刷は太い側を下にして立てる。上すぼまりなので支持材は要らない。
"""
import importlib.util
import os

_path = os.path.join(os.path.dirname(__file__), os.pardir, "pipe-joint", "params.py")
_spec = importlib.util.spec_from_file_location("pipe_joint_params", _path)
J = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(J)

MM = J.MM

# --- ジョイントから引き継ぐ寸法 ---
PIPE_OD = J.PIPE_OD          # 28.0 実パイプ外径
CLEAR = J.CLEAR              # 0.30 片側クリアランス（ジョイントと同じはめ合い）
BORE_D = J.BORE_D            # 28.6 内径
HUB_D = J.HUB_D              # 36.6 太い側の外径。ジョイントの襟と同径
TIP_D = J.TIP_D              # 29.4 細い側の外径。パイプ面から 0.7mm
TAPER_L = J.TAPER_L          # 16.0 すり鉢の長さ
BASE_ROUND = J.BASE_ROUND    # 1.5 底の角丸（ジョイントと同じ作り方で切る）
FILLET_R = J.FILLET_R        # 3.0
FILLET_ANGLE = J.FILLET_ANGLE
SEG = J.SEG
TAPER_SEG = J.TAPER_SEG

# --- この部品だけの寸法 ---
# 合わせ面からすり鉢が始まるまでの真っ直ぐな部分。
# ⚠ FILLET_R より短くすると底の角丸が clamp されて半径が変わり、
#   ジョイントの合わせ面と径が合わなくなる（そこに段差が出る）。
COLLAR_L = FILLET_R          # 3.0

LEN = COLLAR_L + TAPER_L     # 19.0 切ったあとの全長
Z_BUILD_BOT = -BASE_ROUND    # -1.5 角丸を作るために下へ伸ばしておく高さ

assert COLLAR_L >= FILLET_R, "真っ直ぐな部分が角丸より短い。合わせ面の径がずれる"
