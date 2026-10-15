"""Dimensions in metres. The approved SG92R source is imported, never copied."""
import importlib.util
from pathlib import Path

_source = Path(__file__).resolve().parents[1] / 'sg92r-photo' / 'params.py'
_spec = importlib.util.spec_from_file_location('flag_box_sg92r', _source)
SG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SG)

EDGE = 0.068  # 68mm, closed cube
WALL = 0.003  # 3mm
AXIS_Z = 0.048  # 48mm
AXIS_Y = -0.008  # -8mm; leaves 35mm for the flag within the cube
SERVO_ORIGIN_X = -0.016  # -16mm
FIT = 0.00025  # 0.25mm per side, printed SG92R ear-slot value
HORN_FIT = 0.00025  # 0.25mm per side
ROTOR_RADIUS = 0.020  # 20mm
ROTOR_FRONT_X = 0.0225  # 22.5mm
FLAG_X0 = 0.0075  # 7.5mm; flag width 15mm
FLAG_Y0 = 0.000  # 0mm
FLAG_Y1 = 0.035  # 35mm from the pivot, absolute end at +27mm
FLAG_T = 0.003  # 3mm
SNAP_T = 0.0012  # 1.2mm, exception: elastic release arms
SNAP_LENGTH = 0.00575  # 5.75mm, free length of each removable key arm
SNAP_DEFLECTION = 0.0003  # 0.3mm, each arm
MOVE_SECONDS = 2.0
SERVO_LOW_DEG = 45.0
SERVO_HIGH_DEG = 135.0
PLA_DENSITY = 1240.0  # kg/m3
STALL_TORQUE_NM = 0.245

def mm(value):
    return value * 1000.0
