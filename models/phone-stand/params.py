"""アーム式スマホスタンド（装飾用・固定ポーズ）パラメータ。単位: m"""
import math

# --- 机クランプ（C字） ---
CLAMP_W = 0.040          # 横幅 40mm
CLAMP_H = 0.060          # 開口高さ 60mm
CLAMP_T = 0.008          # 厚み 8mm
CLAMP_DEPTH = 0.035      # 奥行き 35mm
CLAMP_OPENING = 0.030    # 机厚相当の開口 30mm
CLAMP_SCREW_R = 0.006    # 締め付けネジ半径
CLAMP_SCREW_L = 0.045    # ネジ長

# --- 垂直支柱 ---
POST_R = 0.008           # 半径 8mm
POST_H = 0.080           # 高さ 80mm

# --- アーム共通 ---
ARM_R = 0.006            # アーム棒の半径 6mm
ARM_LEN = 0.130          # 各アームの長さ 130mm
JOINT_R = 0.012          # 関節（円盤）半径
JOINT_T = 0.010          # 関節厚

# --- バネ（コイル） ---
SPRING_R = 0.010         # コイル半径
SPRING_WIRE_R = 0.0012   # 線材半径 1.2mm
SPRING_TURNS = 14        # 巻き数
SPRING_LEN_RATIO = 0.75  # アーム長に対する比率

# --- アームのポーズ（各関節の角度、ラジアン） ---
# 画像を参考にジグザグ
ARM1_ANGLE = math.radians(60)   # 支柱から上前方へ
ARM2_ANGLE = math.radians(-110) # 折り返して下前方へ
ARM3_ANGLE = math.radians(70)   # 再度上へ

# --- スマホホルダー ---
HOLDER_W = 0.085          # 横幅（スマホ幅+余裕）
HOLDER_H = 0.012          # プレート厚（前後）
HOLDER_PLATE_T = 0.004    # プレート厚み
GRIP_W = 0.010            # 爪の幅
GRIP_H = 0.018            # 爪の高さ
HOLDER_TILT = math.radians(-15)  # 少し上向き

# --- 装着するスマホ ---
PHONE_W = 0.075          # 75mm
PHONE_H = 0.150          # 150mm
PHONE_T = 0.008          # 8mm
PHONE_CORNER_R = 0.010   # 角丸 10mm
