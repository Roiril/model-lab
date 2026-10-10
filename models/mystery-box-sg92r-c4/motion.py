"""C4の運動表。形、検証、表示はこの式を共用する。"""

from __future__ import annotations

import json
import math
import os

import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
MM = 1000.0


def cam_theta_deg(servo_deg: float) -> float:
    return servo_deg - 90.0


def lift_m(group: int, servo_deg: float) -> float:
    """閉位置からの鉛直変位。groupは0=中心、1=内環、2=外環。"""
    theta = math.radians(cam_theta_deg(servo_deg))
    low = math.sin(math.radians(P.CAM_THETA_MIN_DEG))
    return P.CAM_E[group] * (math.sin(theta) - low)


def quintic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 10.0 * t**3 - 15.0 * t**4 + 6.0 * t**5


def servo_command_deg(elapsed_s: float, opening: bool = True) -> float:
    u = quintic(elapsed_s / P.MOVE_TIME_S)
    if not opening:
        u = 1.0 - u
    return P.SERVO_MIN_DEG + (P.SERVO_MAX_DEG - P.SERVO_MIN_DEG) * u


def identity():
    return [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]


def translate_z(mm_value: float):
    out = identity()
    out[14] = mm_value
    return out


def rotate_x_about_axis(delta_deg: float):
    a = math.radians(delta_deg)
    c, s = math.cos(a), math.sin(a)
    z0 = P.CAM_AXIS_Z * MM
    return [1.0, 0.0, 0.0, 0.0,
            0.0, c, s, 0.0,
            0.0, -s, c, 0.0,
            0.0, s * z0, (1.0 - c) * z0, 1.0]


def transforms(servo_deg: float):
    delta = cam_theta_deg(servo_deg) - P.CAM_THETA_MIN_DEG
    cam = rotate_x_about_axis(delta)
    return {
        "camshaft": cam,
        "horn_coupler": cam,
        "cam_center": cam,
        "cam_inner": cam,
        "cam_outer": cam,
        "servo_horn": cam,
        "carrier_center": translate_z(lift_m(0, servo_deg) * MM),
        "carrier_inner": translate_z(lift_m(1, servo_deg) * MM),
        "carrier_outer": translate_z(lift_m(2, servo_deg) * MM),
    }


def motion_document():
    frames = []
    for degree in range(int(P.SERVO_MIN_DEG), int(P.SERVO_MAX_DEG) + 1):
        frames.append({"servo_deg": degree, "transforms": transforms(float(degree))})
    return {
        "home_servo_deg": P.HOME_SERVO_DEG,
        "duration_s": P.MOVE_TIME_S,
        "easing": "quintic_smoothstep",
        "frames": frames,
    }


def write_motion():
    os.makedirs(BUILD, exist_ok=True)
    path = os.path.join(BUILD, "motion.json")
    with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(motion_document(), fh, ensure_ascii=False, separators=(",", ":"))
    os.replace(path + ".tmp", path)
    return path


if __name__ == "__main__":
    print(write_motion())
