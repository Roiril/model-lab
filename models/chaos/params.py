"""
chaos: トレフォイル結び目をベースにした"極限まで変な形"モデル。
単位はすべてメートル（Blender内部単位）。mm値は併記。
"""

# トレフォイル全体のスケール
# bboxは概ね (6*KNOT_SCALE) x (6*KNOT_SCALE) x (2*KNOT_SCALE + チューブ外径)
KNOT_SCALE = 0.010  # 10mm 基準 → 結び目本体 ~60 x 60 x 20mm

# チューブ断面の基準半径
TUBE_R = 0.0065  # 6.5mm → 断面最小でも直径 ~9mm 確保

# 断面ねじれ数（結び目1周あたりの回転数）
TWIST_TURNS = 3

# 断面のスパイク（星型）数
SPIKE_COUNT = 5

# スパイクの出し入れをモジュレートする周波数（結び目1周あたり）
SPIKE_MORPH_FREQ = 2

# 表面の追加うねり
SURFACE_WAVE_FREQ_T = 7   # 軸方向
SURFACE_WAVE_FREQ_J = 2   # 周方向
SURFACE_WAVE_AMP = 0.15   # TUBE_R 比

# メッシュ解像度
N_STEPS = 360   # 軸方向セグメント
N_CROSS = 24    # 断面頂点数

# プリント向けメタ情報
MIN_FEATURE_MM = 4.0  # 断面最小直径の想定下限
