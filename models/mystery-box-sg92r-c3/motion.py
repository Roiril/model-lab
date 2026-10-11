"""C3の運動学。Blenderを使わないため検証と表示生成から共有できる。"""
from __future__ import annotations

import math

import params as P


def cam_theta_deg(servo_deg: float) -> float:
    return P.CAM_HOME_DEG + (servo_deg - P.SERVO_HOME_DEG)


def carrier_height(index: int, servo_deg: float) -> float:
    theta = math.radians(cam_theta_deg(servo_deg) - P.CAM_PHASE_DEG[index])
    return max(0.0, P.CAM_E * (math.cos(theta) - 0.4))


def quintic(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return u * u * u * (10.0 + u * (-15.0 + 6.0 * u))


def servo_command(t: float, opening: bool = True) -> float:
    u = quintic(t / P.MOTION_DURATION_S)
    if not opening:
        u = 1.0 - u
    return P.SERVO_HOME_DEG + (P.SERVO_END_DEG - P.SERVO_HOME_DEG) * u


def column_matrix(tx=0.0, ty=0.0, tz=0.0):
    return [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            tx, ty, tz, 1.0]


def rotate_x_matrix(deg: float, cy: float, cz: float):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    # 列優先。T(c) R T(-c)。単位はbuild STLと同じmm。
    ty = cy - c * cy + s * cz
    tz = cz - s * cy - c * cz
    return [1.0, 0.0, 0.0, 0.0,
            0.0, c, s, 0.0,
            0.0, -s, c, 0.0,
            0.0, ty, tz, 1.0]


def frames():
    result = []
    start = int(round(P.SERVO_HOME_DEG))
    end = int(round(P.SERVO_END_DEG))
    for servo in range(start, end + 1):
        delta = servo - P.SERVO_HOME_DEG
        transforms = {
            "drive_gear": rotate_x_matrix(-delta, P.SERVO_AXIS_Y * 1000, P.SERVO_AXIS_Z * 1000),
            "ref_horn": rotate_x_matrix(-delta, P.SERVO_AXIS_Y * 1000, P.SERVO_AXIS_Z * 1000),
            "camshaft": rotate_x_matrix(delta, P.CAM_AXIS_Y * 1000, P.CAM_AXIS_Z * 1000),
            "left_spacer": rotate_x_matrix(delta, P.CAM_AXIS_Y * 1000, P.CAM_AXIS_Z * 1000),
            "cam_gear": rotate_x_matrix(delta, P.CAM_AXIS_Y * 1000, P.CAM_AXIS_Z * 1000),
        }
        for i in range(P.GRID_N):
            transforms[f"cam_{i}"] = rotate_x_matrix(
                delta, P.CAM_AXIS_Y * 1000, P.CAM_AXIS_Z * 1000
            )
            transforms[f"carrier_{i}"] = column_matrix(tz=carrier_height(i, servo) * 1000)
        result.append({"servo_deg": float(servo), "transforms": transforms})
    return result
