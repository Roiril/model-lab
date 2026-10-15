"""Pure four-bar calculation. mm matrices map the closed baked mesh to each pose."""
import math
import numpy as np
from . import params as P

H = np.array((P.HINGE_V, P.HINGE_D)) * 1000
O = np.array((P.SERVO_V, P.SERVO_D)) * 1000
A_LENGTH = P.CRANK_LENGTH * 1000
B_OFFSET = np.array((P.LID_PIN_V, P.LID_PIN_D)) * 1000
A_CLOSED = O + A_LENGTH * np.array((math.cos(math.radians(P.CLOSED_ALPHA_DEG)), math.sin(math.radians(P.CLOSED_ALPHA_DEG))))
B_CLOSED = H + B_OFFSET
# Preserve exact closure instead of putting the plan's 4-decimal rounding into the mechanism.
LENGTH = float(np.linalg.norm(B_CLOSED - A_CLOSED))


def b_at(theta):
    a = math.radians(-theta)
    return H + np.array(((math.cos(a), -math.sin(a)), (math.sin(a), math.cos(a)))) @ B_OFFSET


def alpha_at(theta):
    b = b_at(theta)
    delta = b - O
    r = float(np.linalg.norm(delta))
    c = (r*r + A_LENGTH*A_LENGTH - LENGTH*LENGTH) / (2*r*A_LENGTH)
    if abs(c) > 1 + 1e-10:
        raise ValueError('four-bar cannot close at this angle')
    return math.degrees(math.atan2(delta[1], delta[0]) + math.acos(max(-1, min(1, c))))


ALPHA_OPEN = alpha_at(P.OPEN_THETA_DEG)
SERVO_OFFSET = 90 - (P.CLOSED_ALPHA_DEG + ALPHA_OPEN) / 2
CLOSED_SERVO = P.CLOSED_ALPHA_DEG + SERVO_OFFSET
OPEN_SERVO = ALPHA_OPEN + SERVO_OFFSET


def pose(servo_deg):
    alpha = float(servo_deg) - SERVO_OFFSET
    if not ALPHA_OPEN-1e-7 <= alpha <= P.CLOSED_ALPHA_DEG+1e-7:
        raise ValueError(f'servo angle {servo_deg} outside [{OPEN_SERVO}, {CLOSED_SERVO}]')
    lo, hi = 0., P.OPEN_THETA_DEG
    for _ in range(52):
        mid = (lo+hi)/2
        if alpha_at(mid) > alpha:
            lo = mid
        else:
            hi = mid
    theta = (lo+hi)/2
    if abs(servo_deg-CLOSED_SERVO) < 1e-7:
        theta = 0.
    if abs(servo_deg-OPEN_SERVO) < 1e-7:
        theta = P.OPEN_THETA_DEG
    a = O + A_LENGTH*np.array((math.cos(math.radians(alpha)), math.sin(math.radians(alpha))))
    b = b_at(theta)
    beta = math.degrees(math.atan2((b-a)[1], (b-a)[0]))
    return {'alpha_deg':alpha, 'theta_deg':theta, 'a_mm':a, 'b_mm':b, 'beta_deg':beta,
            'closure_error_mm':float(abs(np.linalg.norm(b-a)-LENGTH))}


def rot_x(degrees, pivot):
    a = math.radians(degrees)
    m = np.eye(4)
    m[1:3, 1:3] = ((math.cos(a), -math.sin(a)), (math.sin(a), math.cos(a)))
    p = np.array((0., *pivot))
    m[:3, 3] = p - m[:3, :3] @ p
    return m


def transforms(servo_deg, interface=None, common_params=None):
    p = pose(servo_deg)
    out = {pid:np.eye(4) for pid in P.PART_IDS}
    out['horn'] = rot_x(p['alpha_deg']-P.CLOSED_ALPHA_DEG, O)
    out['crank'] = out['horn'].copy()
    out['lid'] = rot_x(-p['theta_deg'], H)
    beta0 = math.degrees(math.atan2(*(B_CLOSED-A_CLOSED)[::-1]))
    out['link'] = rot_x(p['beta_deg']-beta0, A_CLOSED)
    out['link'][1:3, 3] += p['a_mm']-A_CLOSED
    return out


def retention_poses(interface, common_params):
    return [
        {'id':'mid', 'label':'蓋30度', 'servo_deg':alpha_at(30) + SERVO_OFFSET, 'output_deg':30},
        {'id':'open', 'label':'蓋60度', 'servo_deg':OPEN_SERVO, 'output_deg':P.OPEN_THETA_DEG}
    ]


def diagnostics():
    rows = [pose(OPEN_SERVO + i*(CLOSED_SERVO-OPEN_SERVO)/600) for i in range(601)]
    angles = []
    for p in rows:
        b = p['b_mm']-H
        c = p['a_mm']-p['b_mm']
        cos = abs(float(b@c) / np.linalg.norm(b) / np.linalg.norm(c))
        angles.append(math.degrees(math.acos(min(1., cos))))
    return {'closed_servo_deg':CLOSED_SERVO, 'open_servo_deg':OPEN_SERVO,
            'assembly_theta_deg':pose(90)['theta_deg'], 'exact_link_length_mm':LENGTH,
            'max_closure_error_mm':max(r['closure_error_mm'] for r in rows),
            'min_transmission_deg':min(angles)}
