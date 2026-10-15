"""Pure 1:1 external gear motion; closed baked coordinates in millimetres."""
import math
import numpy as np
from . import params as P

O = np.array((P.SERVO_V,P.SERVO_D))*1000
H = np.array((P.HINGE_V,P.HINGE_D))*1000
LINE_DEG = math.degrees(math.atan2(*(O-H)[::-1]))
INPUT_PHASE_DEG = 2*LINE_DEG + 180/P.TEETH - P.SECTOR_TEETH_DEG[0]


def rot_x(degrees,pivot):
    a=math.radians(degrees)
    m=np.eye(4)
    m[1:3,1:3]=((math.cos(a),-math.sin(a)),(math.sin(a),math.cos(a)))
    p=np.array((0.,*pivot))
    m[:3,3]=p-m[:3,:3]@p
    return m


def transforms(servo_deg,interface=None,common_params=None):
    theta=float(servo_deg)-P.CLOSED_SERVO_DEG
    if not -1e-8 <= theta <= 60+1e-8:
        raise ValueError('sector_flag requires servo 60..120 degrees')
    out={pid:np.eye(4) for pid in P.PART_IDS}
    for pid in ('horn','input_gear'):
        out[pid]=rot_x(theta,O)
    for pid in ('sector_gear','flag','flag_cover'):
        out[pid]=rot_x(-theta,H)
    return out


def trajectory(t):
    s=min(1.,max(0.,float(t)/P.MOVE_SECONDS))
    return P.CLOSED_SERVO_DEG + 60*(10*s**3-15*s**4+6*s**5)


def diagnostics():
    rp=P.PITCH_RADIUS*1000
    rb=rp*math.cos(math.radians(P.PRESSURE_ANGLE_DEG))
    ra=P.TIP_RADIUS*1000
    inv=lambda a: math.tan(a)-a
    half=(math.pi*rp/P.TEETH-P.BACKLASH*1000/2)/(2*rp)
    top=half+inv(math.radians(P.PRESSURE_ANGLE_DEG))-inv(math.acos(rb/ra))
    return dict(centre_distance_mm=float(np.linalg.norm(O-H)),hinge_v_mm=float(H[0]),
                closed_servo_deg=60,open_servo_deg=120,assembly_flag_deg=30,
                tip_width_mm=2*ra*math.sin(top),
                contact_ratio=(2*math.sqrt(ra*ra-rb*rb)-27*math.sin(math.radians(20))) /
                              (math.pi*P.MODULE*1000*math.cos(math.radians(20))),
                nominal_backlash_deg=math.degrees(P.BACKLASH/P.PITCH_RADIUS),
                max_speed_deg_s=60*1.875/P.MOVE_SECONDS,
                max_acceleration_deg_s2=60*(10/math.sqrt(3))/P.MOVE_SECONDS**2)
