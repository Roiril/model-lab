"""四つの独立した円盤カムと扇形平面従動子。"""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import params as P

def quintic(u):
    u = max(0.0, min(1.0, u))
    return u ** 3 * (10.0 + u * (-15.0 + 6.0 * u))

def wrap_deg(a):
    return (a + 180.0) % 360.0 - 180.0

def dent_m(group, degree, footprint=False):
    distance = abs(wrap_deg(degree - P.SELECT_DEG[group]))
    if footprint:
        # 扇形の平面が覆ううち、最も高いカム面に接する。
        distance += math.degrees(P.FOLLOWER_ARC_L / (2.0 * P.CAM_RADII[group]))
    u = (distance - P.DENT_DWELL_DEG) / (P.DENT_HALF_WIDTH_DEG - P.DENT_DWELL_DEG)
    return P.DENT_DEPTH * (1.0 - quintic(u))

def lift_m(group, degree):
    from contact_envelope import lift_mm
    value = lift_mm(group, round(float(degree), 10))
    if abs(value) < 1e-9:
        value = 0.0
    if abs(value + 1000 * P.DENT_DEPTH) < 1e-9:
        value = -1000 * P.DENT_DEPTH
    return value / 1000.0

def cam_height_m(group, local_angle_deg):
    degree = P.HOME_SERVO_DEG + P.FOLLOWER_ANGLES_DEG[group] - local_angle_deg
    return P.CAM_BASE_T + P.DENT_DEPTH - dent_m(group, degree)

def follower_floor_m(group, degree):
    return P.CAM_BASE_Z + P.CAM_BASE_T + P.DENT_DEPTH + lift_m(group, degree)

def identity():
    return [1.,0.,0.,0., 0.,1.,0.,0., 0.,0.,1.,0., 0.,0.,0.,1.]

def transforms(degree):
    a = math.radians(degree - P.HOME_SERVO_DEG)
    c, s = math.cos(a), math.sin(a)
    rotation = [c,s,0.,0., -s,c,0.,0., 0.,0.,1.,0., 0.,0.,0.,1.]
    out = {name: rotation[:] for name in ("cam_disk", "horn_coupler", "drive_key", "servo_horn")}
    for i, group in enumerate(P.GROUPS):
        matrix = identity()
        matrix[14] = 1000.0 * lift_m(i, degree)
        out["carrier_" + group] = matrix
    return out

def motion_document():
    import contact_envelope as envelope
    step_deg = 0.05
    count = round((P.SERVO_MAX_DEG - P.SERVO_MIN_DEG) / step_deg)
    interpolation_tolerance_mm = 0.00002
    frames = {}

    def frame(degree):
        degree = round(degree, 10)
        if degree not in frames:
            frames[degree] = dict(servo_deg=degree, transforms=transforms(degree))
        return frames[degree]

    accepted = []

    def refine(a, b, depth=0):
        left, right = frame(a), frame(b)
        worst = 0.0
        for fraction in (.25, .5, .75):
            degree = round(a + (b - a) * fraction, 10)
            for group_index, group in enumerate(P.GROUPS):
                za = left['transforms']['carrier_' + group][14]
                zb = right['transforms']['carrier_' + group][14]
                actual = envelope.lift_mm(group_index, degree)
                worst = max(worst, abs(za + (zb - za) * fraction - actual))
        if worst <= interpolation_tolerance_mm:
            accepted.append(left)
        else:
            if depth >= 16:
                raise ValueError('contact table interpolation did not converge')
            midpoint = round((a + b) * .5, 10)
            refine(a, midpoint, depth + 1)
            refine(midpoint, b, depth + 1)

    for index in range(count):
        refine(round(P.SERVO_MIN_DEG + index * step_deg, 10),
               round(P.SERVO_MIN_DEG + (index + 1) * step_deg, 10))
    accepted.append(frame(P.SERVO_MAX_DEG))
    return {"home_servo_deg": P.HOME_SERVO_DEG, "duration_s": P.MOVE_TIME_S,
            "easing": "quintic_smoothstep", "patterns": [dict(id=i,label=l,servo_deg=d) for i,l,d in P.PATTERNS],
            "contactEnvelope": {"method": "actual_STL_triangle_intersection_maximum",
                "calibration": envelope.calibration(), "frameStepDeg": step_deg,
                "adaptiveRefinement": {"sampleFractions": [.25, .5, .75],
                    "toleranceMm": interpolation_tolerance_mm, "frameCount": len(accepted),
                    "minimumStepDeg": min(b['servo_deg'] - a['servo_deg']
                                          for a, b in zip(accepted, accepted[1:]))},
                "sourceSha256": {f"models/{P.MODEL_ID}/{name}": digest
                                 for name, digest in envelope.source_hashes().items()}},
            "frames": accepted}

def write_motion():
    target = Path(__file__).parent / "build" / "motion.json"
    target.parent.mkdir(exist_ok=True)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(motion_document(),ensure_ascii=False,separators=(",",":")),encoding="utf-8",newline="\n")
    os.replace(temporary,target)
    return target

if __name__ == "__main__":
    print(write_motion())
