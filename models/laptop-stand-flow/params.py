"""参考画像（design/reference.png）を忠実に再現した、S字のノートPCスタンド。単位: m

形の寸法は参考画像の側面図から読み取った比率で決めている（trace.py / profile.py）。
画像1px = 0.75mm で読んだ大きさ（足の全長 約247mm、高さ約140mm）が SIZE_FACTOR = 1.0。
全体を相似に拡縮するときは SIZE_FACTOR だけを変える。
"""

MODEL_NAME = "laptop-stand-flow"
CATEGORY = "ノートPCスタンド"
# CATEGORY: ノートPCスタンド

SIZE_FACTOR = 1.0  # 1.0 で足の全長 約247mm・高さ約140mm。0.9 なら約222mm・126mm
PAIR_SPACING = 0.200  # 左右の脚の中心間 200mm

# レール板（ノートPCが載る面）
PLANK_HALF_WIDTH = 0.012  # 幅24mm
PLANK_EDGE_RADIUS = 0.0020  # 2mm
PLANK_END_RADIUS = 0.010  # 平面の角R 10mm
PLANK_THICKNESS = 0.0075  # 7.5mm
LIP_DROP = 0.0055  # 前端の返しの出っ張り 5.5mm
LIP_LENGTH = 0.022  # 前端の返しの長さ 22mm

# 断面の丸み: 1 で楕円、大きいほど角張る
SECTION_POWER = 2.0

# 柱の上面（レール板の座）を板の下面より高くして、板に食い込ませる量。歪みを掛けても板と柱が離れない
SEAT_RAISE = 0.0035  # 3.5mm

# 接地面の下へ延長して切り落とす量（平らな底面をつくる）
GROUND_OVERSHOOT = 0.0045

# 立体化の解像度
GRID = 0.0006  # 0.6mm
SMOOTH_ITERATIONS = 30

# 参考画像のカメラから見た輪郭を目標に寄せる、小さな歪み（fit/view_warp.npz があるとき）
USE_VIEW_WARP = True
