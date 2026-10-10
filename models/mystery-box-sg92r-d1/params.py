"""D1: C1の実物確認済みSG92R機構を80mmの鋭角箱へ収める。単位:m。"""
import importlib.util
import os


def _load(name, folder):
    path = os.path.join(os.path.dirname(__file__), "..", folder, "params.py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_base = _load("mystery_box_c1_params", "mystery-box-sg92r-c1")
_fallback = _load("mystery_box_c2_params", "mystery-box-sg92r-c2")
globals().update({name: getattr(_base, name) for name in dir(_base) if name.isupper()})
for _name in dir(_fallback):
    if _name.isupper() and _name not in globals():
        globals()[_name] = getattr(_fallback, _name)

SG.REFERENCE_PREFIX = "sg92r-photo"
SERVO_DIMENSION_PROFILE = {"id": "approved", "physicalFitConfirmed": True}

CUBE = 0.080
WALL = 0.003
FLOOR = 0.003
LID_T = 0.003
EDGE_R = 0.0
HINGE_Y = -0.030
HINGE_Z = 0.074
SHAFT_Y = 0.003
SHAFT_Z = 0.0306
MODEL_ID = "mystery-box-sg92r-d1"
CLIP_X1 = -0.01785

HINGE_EAR_R = 0.0045
ROOF_KNUCKLE_CLEAR_R = 0.0048
LID_KNUCKLE_HALF_X = 0.0186
ROOF_EAR_X0 = 0.019
ROOF_EAR_X1 = 0.027
LID_SUPPORT_X_W = 0.004
LID_ARM_HALF_W = 0.0018
ROOF_SEAM_R = 0.0166
LID_SEAM_R = 0.0170
PIN_END_X = 0.0288
PIN_HEAD_X0 = 0.0270
PIN_HEAD_R = 0.0037
HINGE_HOLE_LID_D = 0.0054
HINGE_TIP_D = 0.0056
HINGE_TIP_L = 0.0012
HINGE_SPLIT_L = 0.007

ROOF_LEG_Y0 = -0.024
ROOF_LEG_Y1 = -0.020
ROOF_LEG_X = 0.035
ROOF_FRONT_Y = -0.022
FIN_ROOT_Y = HINGE_Y + 0.023
FIN_BACK_Y = HINGE_Y - 0.001
ASSEMBLY_LID_BACK_DEG = 75.0
B_REL_Z = -0.0213
