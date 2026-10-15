"""One-to-one direct drive; geometry and verification share these transforms."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'lib'))
import numpy as np
from printmech.contract import rotation
from params import AXIS_Z, AXIS_Y, mm, SERVO_LOW_DEG

def transforms(servo_deg, ids):
    turn = rotation((1, 0, 0), servo_deg - SERVO_LOW_DEG, (0, mm(AXIS_Y), mm(AXIS_Z)))
    return {p: turn.copy() if p in ('horn', 'flag', 'bearing_button') else np.eye(4) for p in ids}
