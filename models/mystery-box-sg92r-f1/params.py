"""F1 common dimensions. Length constants are metres; module meshes use mm."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = HERE.name
INTERFACE_ID = "resident-face-v2"
_spec = importlib.util.spec_from_file_location("f1_sg92r_reference", ROOT / "models/sg92r-photo/params.py")
SG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SG)


def mm(value):
    return float(value) * 1000.0


CUBE = 0.100  # 100mm
PANEL = 0.0874  # 87.4mm; 6mm frame edge and 0.3mm seam
PANEL_T = 0.002  # 2mm
APERTURE = 0.088  # 88mm
FIT = 0.00025  # 0.25mm per side
POSITION_DIA = 0.004  # 4mm
POSITION_HOLE = 0.0044  # 4.4mm
KEY_ARM_L = 0.018  # 18mm
KEY_ARM_T = 0.0016  # 1.6mm
KEY_ARM_W = 0.005  # 5mm
KEY_DEFLECT = 0.0006  # 0.6mm
KEY_ENGAGE = 0.0024  # 2.4mm
EXTRACTION = 0.040  # 40mm
SERVICE_WIRE = 0.060  # 60mm
TRAY_OUTER = (0.024, 0.024, 0.044)  # 24 x 24 x 44mm
TRAY_INNER = (0.020, 0.020, 0.040)  # 20 x 20 x 40mm
FRAME_EDGE = 0.006  # 6mm cosmetic border
FRAME_JOINT_CLEARANCE = 0.00025  # 0.25mm
FRAME_SNAP_L = 0.018  # 18mm
FRAME_SNAP_T = 0.0016  # 1.6mm
FRAME_SNAP_DEFLECT = 0.0006  # 0.6mm
FRAME_CARRIER_T = 0.003  # 3mm; four separately printed side receivers
WIRING_RESERVED = (0.056, 0.040, 0.011)  # 56 x 40 x 11mm, excluding feet/tray posts
WIRING_RESERVED_CENTER_Z = -0.0415  # -41.5mm
WIRING_FOOT_X = 0.014  # two rigid T-head feet at +/-14mm
WIRING_FOOT_T = 0.00155  # 1.55mm; captured by lower ring and back carrier
