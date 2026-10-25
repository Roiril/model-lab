"""SO-101 の組み立て姿勢。関節角は mycobot-lab のシミュレータ（:8025）と同じ向き・同じ 0 点。

角度は度。長さは m（model-lab の共通の単位）。
"""

SHOULDER_PAN = 0.0  # 肩の旋回 [deg]
SHOULDER_LIFT = -35.0  # 肩の上下 [deg]
ELBOW_FLEX = 45.0  # 肘 [deg]
WRIST_FLEX = -15.0  # 手首の曲げ [deg]
WRIST_ROLL = 0.0  # 手首の回転 [deg]
GRIPPER = 0.0  # グリッパの開き [deg]

# 先端のロボットハンド（hand_mount.py）。FBX が hand_src/ に無いときは元のグリッパのまま
HAND = 1  # ロボットハンドを付ける（1）/ 元のグリッパ（0）
HAND_SIDE = "Right"
HAND_SCALE = 0.058  # FBX の 1 単位の長さ [m]。手首の円盤が 52 mm になり、箱の幅とそろう
BOX_HEIGHT = 0.040  # 配線の箱の高さ [m]。中の高さ 37.6 mm = 8Servos Unit 10.5 + 差したコネクタ 14 + 線の曲がり 13

try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
