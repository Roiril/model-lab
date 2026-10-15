"""The blank module has no actuator or moving parts during operation."""
import numpy as np


def transforms(servo_deg, interface, common_params):
    return {part: np.eye(4) for part in ("panel", "key_l", "key_r")}
