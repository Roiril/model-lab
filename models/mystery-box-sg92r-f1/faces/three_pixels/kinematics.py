"""Table -> periodic pitch curve -> finite-pin swept groove, without bpy.

Uses tangible-pixel-cube's table-driven generation and infeasible-input rejection.
The geometry here is an axial cylindrical cam, not the reference's plate cam.
"""
import json
import math
from pathlib import Path
import numpy as np
from . import params as P


def read_patterns(path=None):
    data = json.loads(Path(path or Path(__file__).with_name('patterns.json')).read_text(encoding='utf-8'))
    if data.get('units') != 'mm' or data.get('pixels') != ['pixel_1', 'pixel_2', 'pixel_3']:
        raise ValueError('patterns: expected millimetres and three named pixels')
    stops = data['stops']
    if [row['servo_deg'] for row in stops] != [60, 90, 120]:
        raise ValueError('patterns: stop angles must be 60, 90, 120 degrees')
    for row in stops:
        if len(row['heights_mm']) != 3 or any(not math.isfinite(h) or not 0 <= h <= P.LIFT_MAX*1000 for h in row['heights_mm']):
            raise ValueError('patterns: heights must be finite and within 0..3 mm')
    if stops[1]['heights_mm'] != [0, 0, 0]:
        raise ValueError('patterns: 90 degree assembly datum must be all zero')
    return data


def q(s):
    return s*s*s*(10+s*(-15+6*s))


def nodes(table=None):
    table = read_patterns() if table is None else table
    return sorted(((angle-(row['servo_deg']-90)) % 360, row['heights_mm'][i])
                  for i, angle in enumerate(P.FOLLOWER_DEG) for row in table['stops'])


def curve(phi_deg, derivative=0, table=None):
    """Periodic lift; derivatives are with respect to radians."""
    ns = nodes(table)
    a = np.asarray(phi_deg, dtype=float) % 360
    out = np.zeros_like(a)
    for i, (left, h0) in enumerate(ns):
        right, h1 = ns[(i+1) % len(ns)]
        length = (right-left) % 360
        delta = (a-left) % 360
        mask = delta < length
        s = np.clip((delta-P.DWELL_HALF_DEG)/(length-2*P.DWELL_HALF_DEG), 0, 1)
        width = math.radians(length-2*P.DWELL_HALF_DEG)
        if derivative == 0:
            value = h0+(h1-h0)*q(s)
        elif derivative == 1:
            value = (h1-h0)*30*s*s*(1-s)*(1-s)/width
        elif derivative == 2:
            value = (h1-h0)*60*s*(1-s)*(1-2*s)/(width*width)
        else:
            raise ValueError('derivative must be 0, 1 or 2')
        out = np.where(mask, value, out)
    return float(out) if out.ndim == 0 else out


def heights(servo_deg, table=None):
    if not P.SERVO_MIN_DEG-1e-8 <= servo_deg <= P.SERVO_MAX_DEG+1e-8:
        raise ValueError('servo angle outside 60..120 degrees')
    return [curve(a-(servo_deg-90), table=table) for a in P.FOLLOWER_DEG]


def rotation(degrees):
    a = math.radians(degrees)
    m = np.eye(4)
    m[:2, :2] = ((math.cos(a), -math.sin(a)), (math.sin(a), math.cos(a)))
    p = np.array((P.AXIS_U*1000, 0., 0.))
    m[:3, 3] = p-m[:3, :3]@p
    return m


def transforms(servo_deg, interface=None, common_params=None):
    out = {pid: np.eye(4) for pid in P.PART_IDS}
    rot = rotation(servo_deg-90)
    for pid in ('horn', 'cam_lower', 'cam_upper', 'cam_key_1', 'cam_key_2'):
        out[pid] = rot.copy()
    for i, h in enumerate(heights(servo_deg), 1):
        out[f'pixel_{i}'][2, 3] = -h
    return out


def groove_bounds(radius_mm, phi_deg, table=None):
    """Envelope of a radius-2.2 finite radial pin; shallow/deep d.

    At (r,phi), tangential offset t places the pin at theta=phi-asin(t/r).
    Its section is sqrt(a²-t²), and r*cos(phi-theta) must be on the pin.
    Golden-section extrema account for finite pin diameter on slopes.
    """
    a = P.GROOVE_WIDTH*500
    phi = np.asarray(phi_deg, dtype=float)
    def z(t, sign):
        theta = phi-np.degrees(np.arcsin(t/radius_mm))
        return P.PIN_D*1000-curve(theta, table=table)+sign*np.sqrt(np.maximum(0, a*a-t*t))
    result=[]
    for sign in (-1, 1):
        lo=np.full_like(phi, -a); hi=np.full_like(phi, a)
        ratio=(math.sqrt(5)-1)/2
        for _ in range(42):
            l=hi-ratio*(hi-lo); r=lo+ratio*(hi-lo)
            take_left=sign*z(l,sign) > sign*z(r,sign)
            hi=np.where(take_left,r,hi); lo=np.where(take_left,lo,l)
        t=(lo+hi)/2
        longitudinal=np.sqrt(radius_mm**2-t*t)
        if np.any(longitudinal < P.PIN_R0*1000) or np.any(longitudinal > P.PIN_R1*1000):
            raise ValueError('groove touches a finite pin end')
        result.append(z(t,sign))
    return result


def diagnostics():
    table=read_patterns()
    angles=np.linspace(60,120,6001)
    phi=np.asarray(P.FOLLOWER_DEG)[:,None]-(angles[None,:]-90)
    slopes=np.abs(curve(phi,1,table))
    slope=float(slopes.max())
    r=min(P.CAM_INNER_RADIUS,P.UPPER_CAM_INNER_RADIUS)*1000
    contact_r=math.sqrt(r*r-(P.GROOVE_WIDTH*500)**2)
    actual=float((P.PIXEL_RESISTANCE_N*slopes.sum(axis=0)/1000/P.EFFICIENCY).max()+P.FRICTION_NM+P.ACCELERATION_NM)
    conservative=3*P.PIXEL_RESISTANCE_N*slope/1000/P.EFFICIENCY+P.FRICTION_NM+P.ACCELERATION_NM
    ph=np.arange(0,360,.025)
    h1=curve(ph,1,table); h2=curve(ph,2,table)
    curvature=np.abs(r*h2)/(r*r+h1*h1)**1.5
    return {'stops':table['stops'], 'max_dh_mm_per_rad':slope,
            'pressure_angle_at_25mm_deg':math.degrees(math.atan(slope/25)),
            'pressure_angle_conservative_deg':math.degrees(math.atan(slope/contact_r)),
            'min_contact_radius_mm':contact_r,
            'normal_offset_curvature_product':float(curvature.max()*P.GROOVE_WIDTH*500),
            'torque_simultaneous_nm':actual, 'torque_conservative_nm':conservative,
            'torque_limit_nm':P.SERVO_STALL_NM/3,
            'max_command_speed_deg_s':60*1.875/P.MOVE_SECONDS,
            'groove_nominal_normal_play_mm':(P.GROOVE_WIDTH-P.PIN_DIAMETER)*1000}
