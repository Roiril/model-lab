"""SO-101 の組み立て姿勢。関節角は mycobot-lab のシミュレータ（:8025）と同じ向き・同じ 0 点。

角度は度。長さは m（model-lab の共通の単位）。
"""

SHOULDER_PAN = 0.0  # 肩の旋回 [deg]
SHOULDER_LIFT = -35.0  # 肩の上下 [deg]
ELBOW_FLEX = 45.0  # 肘 [deg]
WRIST_FLEX = -15.0  # 手首の曲げ [deg]
WRIST_ROLL = 0.0  # 手首の回転 [deg]
GRIPPER = 0.0  # グリッパの開き [deg]

try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
