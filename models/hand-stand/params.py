# ロボットハンド台座 — 寸法・定数（単位: m）

# ロボットハンド底面フットプリント（実測）
HAND_W = 0.0545   # 54.5mm
HAND_D = 0.0275   # 27.5mm

# はめ込みポケット
FIT_CLR    = 0.0003   # 0.3mm per side（スナップフィット）
POCKET_DEPTH = 0.012  # 12mm — ハンドを差し込んで保持する深さ

# ポケット内寸（クリアランス込み）
POCKET_IW = HAND_W + 2 * FIT_CLR   # 55.1mm
POCKET_ID = HAND_D + 2 * FIT_CLR   # 28.1mm

# ポケットを囲む壁
WALL  = 0.003    # 3mm 側壁
FLOOR = 0.003    # 3mm ポケット床（この下にベースプレート）

# カップ（壁で囲んだ部分）の外寸
CUP_W = POCKET_IW + 2 * WALL   # 61.1mm
CUP_D = POCKET_ID + 2 * WALL   # 34.1mm
CUP_H = FLOOR + POCKET_DEPTH    # 15mm（床3 + ポケット12）

# ベースプレート（転倒防止の広い土台）
BASE_MARGIN = 0.015   # カップ外周から各辺 +15mm 張り出し
BASE_W = CUP_W + 2 * BASE_MARGIN   # 91.1mm
BASE_D = CUP_D + 2 * BASE_MARGIN   # 64.1mm
BASE_T = 0.004    # 4mm 厚（重心を低く保つ薄めの板）

# 面取り（角・縁を落として印刷&取り回しを楽に）
EDGE_BEVEL = 0.0015   # 1.5mm

# ケーブル逃げ溝（-Y 側の壁を切り欠く）
CABLE_W     = 0.010   # 10mm 幅
CABLE_DEPTH = 0.008   # 8mm 深さ（壁上端から下方向へ）
