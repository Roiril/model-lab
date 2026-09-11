"""M 字ジョイントの脚 2 本と、その横の 3 本目の脚を床で受けるベース。

    ./run.sh models/pipe-foot-pair/model.py

形づくりの部品（回転体・押し出し・boolean・板の網）は lib/foot_core.py。
pipe-foot-corner と共有している。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, EXPORTS_DIR
import foot_core as fc
import params as P
from params import *

# 角丸を作るために下へ伸ばしておき、最後に z=0 で切る。
# こうすると底面は平らなまま、その上だけが丸まる。
Z_BUILD_BOT = -BASE_ROUND


# ---------------------------------------------------------------- profiles

def spine_top(x):
    """主材の上端。中央で傾きが 0 になる二次曲線。

    smoothstep にすると中央が平らな帯になり、板を立てただけに見える。
    曲げを受けるのは根元だけなので、中央は低くてよい。
    """
    t = abs(x) / (SPAN / 2)
    return SPINE_MID_Z + (SPINE_TOP_Z - SPINE_MID_Z) * t * t


def branch_top(y, side):
    """枝の上端。主材の側面から出る所の高さを起点に、同じ二次曲線で上がる。"""
    y0 = SPINE_T / 2
    z0 = spine_top(y0)
    t = (y - y0) / (THIRD_OFF - y0)
    return z0 + (SPINE_TOP_Z - z0) * t * t


def t_spine():
    """背骨。X 方向の主材と、3 本目のソケットへ伸びる枝を 1 つのメッシュで作る（T 字）。

    枝を別体にして boolean で足すと、主材の上面（中央で 14mm）と枝の上面が
    ほぼ同じ高さで交わり、0.1mm 以下の段や薄片が出て bevel が荒れる。
    中央に SPINE_T 角の芯を置き、主材の左右と枝をその芯の面につなぐ（wall_net）。
    両端はソケットの軸まで伸ばし、肉の中で終わらせる。
    """
    sx = SPAN / 2
    n = SPINE_SEG // 2
    main = lambda s, side: spine_top(s)
    return fc.wall_net("spine", {"J": (0.0, 0.0)}, [
        dict(axis="x", c=0.0, a=("free", -sx), b=("node", "J"), top=main, seg=n),
        dict(axis="x", c=0.0, a=("node", "J"), b=("free", sx), top=main, seg=n),
        dict(axis="y", c=0.0, a=("node", "J"), b=("free", THIRD_OFF), top=branch_top,
             seg=BRANCH_SEG),
    ], SPINE_T, PLATE_T - SPINE_LAP)


# ---------------------------------------------------------------- build

def build():
    sx = SPAN / 2
    # ソケットの軸と、そのひれの向き。ひれは背骨と直交する側に出す
    sockets = [((-sx, 0.0), (90.0, -90.0)),
               ((sx, 0.0), (90.0, -90.0)),
               (THIRD, (0.0, 180.0))]

    # 床に着く板（ソケット 3 つを包む凸包。反時計回りに並べる）
    body = fc.prism("pipe_foot_pair", fc.hull_poly([c for c, _ in sockets], PLATE_R, SEG),
                    Z_BUILD_BOT, PLATE_T)

    # ソケット 3 本
    prof = fc.socket_profile(P, Z_BUILD_BOT)
    for k, (c, _) in enumerate(sockets):
        fc.boolean(body, fc.revolve("socket%d" % k, prof, fc.translate(*c), SEG), "UNION")

    # 背骨（主材 + 枝）
    fc.boolean(body, t_spine(), "UNION")

    # 横のひれ 6 枚（ソケットごとに 2 枚）
    for k, (c, angs) in enumerate(sockets):
        for j, ang in enumerate(angs):
            fc.boolean(body, fc.fin("fin%d%d" % (k, j), P, c[0], c[1], ang), "UNION")

    # 接合部に R
    fc.clean(body)
    fc.bevel(body, FILLET_R * MM, FILLET_SEG, FILLET_ANGLE)

    # 底を平らに切る（角丸を残したまま接地面を確保）
    fc.boolean(body, fc.box_mm("cut_base", -300, 300, -200, 200, -100, 0), "DIFFERENCE")

    # パイプの穴（座面まで）
    for k, (c, _) in enumerate(sockets):
        fc.boolean(body, fc.cyl("bore%d" % k, BORE_D / 2, SEAT_Z, BOSS_TOP + 10, c[0], c[1], SEG),
                   "DIFFERENCE")

    # 穴あけが残す極小のスリバーを潰す。0.02mm は最小の造形物（口元の肉厚 1.0mm）の
    # 1/50 なので意図した形には触らない。
    # ⚠ 0.1mm まで粗くすると bevel の刻みまで潰れて、非多様体が 3 から 15 に増える
    fc.clean(body, dist=2e-5)

    fc.activate(body)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_flat()
    return body


clear_scene()
body = build()

os.makedirs(EXPORTS_DIR, exist_ok=True)
stl = os.path.join(EXPORTS_DIR, "pipe_foot_pair.stl")
fc.activate(body)
bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True,
                      global_scale=1000.0, ascii_format=False)
print("Exported:", stl)
print("bbox mm:", [round(v * 1000, 2) for v in body.dimensions])
