"""D2: C2の寸法図候補SG92R機構を80mmの鋭角箱へ収める。単位:m。"""
import importlib.util
import os


_path = os.path.join(os.path.dirname(__file__), "..", "mystery-box-sg92r-c2", "params.py")
_spec = importlib.util.spec_from_file_location("mystery_box_c2_params", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
globals().update({name: getattr(_base, name) for name in dir(_base) if name.isupper()})

CUBE = 0.080
WALL = 0.003
FLOOR = 0.003
LID_T = 0.003
EDGE_R = 0.0
HINGE_Y = -0.013
HINGE_Z = 0.074
SHAFT_Y = 0.009
SHAFT_Z = 0.0306
MODEL_ID = "mystery-box-sg92r-d2"
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

ROOF_LEG_Y0 = -0.007
ROOF_LEG_Y1 = -0.003
ROOF_LEG_X = 0.035
ROOF_FRONT_Y = -0.005
FIN_ROOT_Y = HINGE_Y + 0.023
FIN_BACK_Y = HINGE_Y - 0.001
ASSEMBLY_LID_BACK_DEG = 75.0
B_REL_Z = -0.0213
