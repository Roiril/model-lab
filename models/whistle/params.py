"""whistle パラメータ（ヘルムホルツ共鳴器）。単位: m

ヘルムホルツ共鳴周波数:
    f = (c / 2π) * sqrt(A / (V * L'))
        c  = 音速 ≒ 343 m/s
        A  = ネック断面積
        V  = キャビティ容積
        L' = ネック実効長 (= L + 1.7 * r_neck, 端面補正)
"""

import math

# キャビティ（内側の空洞）
CAVITY_R = 0.015        # 15mm 球の内半径
WALL     = 0.002        # 2mm 肉厚

# ネック（吹き口チューブ）
NECK_R   = 0.003        # 3mm 内半径
NECK_L   = 0.010        # 10mm 長さ
NECK_WALL = 0.002       # 2mm ネック外壁

# 底面フラット化（印刷時ベッドに置けるように）
BASE_FLAT_Z = -0.013    # この高さより下をカット

# 設計周波数（参考計算）
_V  = (4.0 / 3.0) * math.pi * CAVITY_R ** 3
_A  = math.pi * NECK_R ** 2
_Lp = NECK_L + 1.7 * NECK_R
DESIGN_FREQ = (343.0 / (2.0 * math.pi)) * math.sqrt(_A / (_V * _Lp))
