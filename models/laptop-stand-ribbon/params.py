"""一体型リボンスタンドの寸法。長さはm。"""

MODEL_NAME = "laptop-stand-ribbon"
# CATEGORY: ノートPCスタンド

LENGTH = 0.280  # 奥行きの基準 280mm
HEIGHT = 0.152  # 高さの基準 152mm
FOOT_WIDTH = 0.084  # 足の幅の基準 84mm
RAIL_WIDTH = 0.024  # 上側の最小幅 24mm
LIP_RISE = 0.009  # 前端の立ち上がり 9mm
LIP_LENGTH = 0.032  # 前端を曲げる長さ 32mm

overhang_limit_deg = 45.0  # 許容する下向き面の限界 45度
design_overhang_deg = 42.0  # 外周と穴天井の設計角度 42度
triangulation_step = 0.002  # 側面内部の三角形間隔 2mm
boundary_step = 0.0015  # 輪郭の最大頂点間隔 1.5mm
