"""F1 common dimensions. Length constants are metres; module meshes use mm."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = HERE.name
_spec = importlib.util.spec_from_file_location("f1_sg92r_reference", ROOT / "models/sg92r-photo/params.py")
SG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SG)


def mm(value):
    return float(value) * 1000.0


CUBE = 0.100  # 100mm
PANEL = 0.092  # 92mm
PANEL_T = 0.002  # 2mm
APERTURE = 0.0926  # 92.6mm
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
FRAME_EDGE = 0.0037  # 3.7mm cosmetic border
FRAME_JOINT_CLEARANCE = 0.00025  # 0.25mm
FRAME_SNAP_L = 0.018  # 18mm
FRAME_SNAP_T = 0.0016  # 1.6mm
FRAME_SNAP_DEFLECT = 0.0006  # 0.6mm
