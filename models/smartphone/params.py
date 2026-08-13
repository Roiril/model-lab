"""Smartphone model parameters (units: meters)."""

# 本体外形（一般的なスマホサイズ）
WIDTH  = 0.075   # 75mm
DEPTH  = 0.150   # 150mm
HEIGHT = 0.008   # 8mm 厚み
CORNER_R = 0.010 # 10mm 角丸半径

# 画面（フチを残してくぼみ）
SCREEN_MARGIN = 0.004   # 4mm ベゼル
SCREEN_DEPTH  = 0.0005  # 0.5mm くぼみ

# カメラバンプ（背面）
CAM_BUMP_W = 0.025      # 25mm
CAM_BUMP_H = 0.025      # 25mm
CAM_BUMP_T = 0.0015     # 1.5mm 出っ張り
CAM_BUMP_R = 0.004      # 4mm 角丸
CAM_OFFSET_X = 0.018    # 中心からのオフセット
CAM_OFFSET_Y = 0.050    # 上端寄り

# 個別レンズ（カメラバンプ上の円柱）
LENS_R       = 0.005    # 5mm 半径
LENS_T       = 0.0008   # 0.8mm 出っ張り
LENS_SPACING = 0.011    # レンズ間距離
