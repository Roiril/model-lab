"""M 字ジョイントの脚 2 本を床で受けるベース。

    ./run.sh models/pipe-foot-pair/model.py
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import bmesh
from mathutils import Matrix, Vector
from blender_utils import clear_scene, EXPORTS_DIR
from params import *

# 角丸を作るために下へ伸ばしておき、最後に z=0 で切る。
# こうすると底面は平らなまま、その上だけが丸まる。
Z_BUILD_BOT = -BASE_ROUND


# ---------------------------------------------------------------- helpers

def _activate(ob):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    return ob


def _finish(name, bm, matrix=None):
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if matrix is not None:
        ob.matrix_world = matrix
    return ob


def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def revolve(name, profile, matrix=None, seg=SEG):
    """profile: [(z, r)] r>0、z は単調増加。軸は Z。"""
    bm = bmesh.new()
    rings = []
    for a, r in profile:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg) * MM,
                                    r * math.sin(2 * math.pi * i / seg) * MM,
                                    a * MM)) for i in range(seg)])
    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return _finish(name, bm, matrix)


def cyl(name, r, z0, z1, cx=0.0, cy=0.0, seg=SEG):
    return revolve(name, [(z0, r), (z1, r)],
                   Matrix.Translation(Vector((cx, cy, 0.0)) * MM), seg)


def prism(name, poly, z0, z1, matrix=None):
    """poly: [(x, y)]（mm）を z0→z1（mm）に押し出してから matrix で置く。"""
    bm = bmesh.new()
    lo = [bm.verts.new((x * MM, y * MM, z0 * MM)) for x, y in poly]
    hi = [bm.verts.new((x * MM, y * MM, z1 * MM)) for x, y in poly]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    return _finish(name, bm, matrix)


def wall(name, xs, z_bot, z_top, y0, y1):
    """x を並べ、下端 z_bot(x) と上端 z_top(x) のあいだを埋めた縦板。

    ⚠⚠ 凹んだ輪郭を prism() の n-gon の蓋で作ってはいけない。三角化が凹みを
    またいで膜を張り、弧の内側が塞がって板になる（Blender 5.1 で実測）。
    しかも体積も非多様体エッジ数も正しいままなので、数値では気づけない。
    蓋も四角形の帯で作れば、そもそも凹みが問題にならない。
    """
    bm = bmesh.new()
    lo0 = [bm.verts.new((x * MM, y0 * MM, z_bot(x) * MM)) for x in xs]
    hi0 = [bm.verts.new((x * MM, y0 * MM, z_top(x) * MM)) for x in xs]
    lo1 = [bm.verts.new((x * MM, y1 * MM, z_bot(x) * MM)) for x in xs]
    hi1 = [bm.verts.new((x * MM, y1 * MM, z_top(x) * MM)) for x in xs]
    for i in range(len(xs) - 1):
        bm.faces.new([lo0[i], lo0[i + 1], hi0[i + 1], hi0[i]])
        bm.faces.new([lo1[i], lo1[i + 1], hi1[i + 1], hi1[i]])
        bm.faces.new([lo0[i], lo1[i], lo1[i + 1], lo0[i + 1]])
        bm.faces.new([hi0[i], hi1[i], hi1[i + 1], hi0[i + 1]])
    bm.faces.new([lo0[0], hi0[0], hi1[0], lo1[0]])
    bm.faces.new([lo0[-1], hi0[-1], hi1[-1], lo1[-1]])
    return _finish(name, bm)


def box(name, size, matrix):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts[:], vec=Vector(size))
    return _finish(name, bm, matrix)


def clean(ob, dist=1e-5):
    """boolean が残す極短エッジを掃除する。放置すると Bevel が発散する。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return ob


def boolean(target, cutter, op="UNION", solver="MANIFOLD"):
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = solver
    _activate(target)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def bevel(ob, width, segments, angle_deg):
    mod = ob.modifiers.new("bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle_deg)
    mod.miter_outer = "MITER_ARC"
    mod.use_clamp_overlap = True
    _activate(ob)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


# ---------------------------------------------------------------- profiles

def socket_profile():
    """底 → 台座 → ソケット → 口元を 1 本の回転体で作る [(z, r)]。

    pipe-foot の core_profile と同じ。板の側は下で作り直すので、
    ここの円板（DISC_R）は板の中に埋まる。
    """
    pts = [(Z_BUILD_BOT, DISC_R), (PLATE_T, DISC_R), (HUB_T, CONE_BASE_R)]
    for i in range(1, CONE_SEG + 1):
        t = i / CONE_SEG
        z = HUB_T + (SEAT_Z - HUB_T) * t
        pts.append((z, BOSS_R + (CONE_BASE_R - BOSS_R) * (1.0 - smoothstep(t))))
    pts.append((BOSS_TOP - MOUTH_TAPER, BOSS_R))
    for i in range(1, CONE_SEG + 1):
        t = i / CONE_SEG
        pts.append((BOSS_TOP - MOUTH_TAPER + MOUTH_TAPER * t,
                    BOSS_R + (TIP_R - BOSS_R) * smoothstep(t)))
    out = [pts[0]]
    for p in pts[1:]:
        if p[0] - out[-1][0] > 1e-9:
            out.append(p)
    return out


def plate_poly(r, seg=SEG):
    """x = ±SPAN/2 に置いた半径 r の円 2 つの凸包。反時計回り。"""
    s = SPAN / 2
    n = seg // 2
    pts = []
    for i in range(n + 1):                       # 右の半円 -90° → +90°
        a = -math.pi / 2 + math.pi * i / n
        pts.append((s + r * math.cos(a), r * math.sin(a)))
    for i in range(n + 1):                       # 左の半円 +90° → +270°
        a = math.pi / 2 + math.pi * i / n
        pts.append((-s + r * math.cos(a), r * math.sin(a)))
    return pts


def spine_top(x):
    """背骨の上端。中央で傾きが 0 になる二次曲線。

    smoothstep にすると中央が平らな帯になり、板を立てただけに見える。
    曲げを受けるのは根元だけなので、中央は低くてよい。
    """
    t = abs(x) / (SPAN / 2)
    return SPINE_MID_Z + (SPINE_TOP_Z - SPINE_MID_Z) * t * t


def spine_xs():
    """背骨を刻む x。両端はソケットの軸まで伸ばし、肉の中で終わらせる。"""
    x0 = SPAN / 2
    return [-x0 + 2 * x0 * i / SPINE_SEG for i in range(SPINE_SEG + 1)]


def fin_poly():
    """横のひれの断面 [(r, z)]。外端は 3mm の高さを残して尖らせない。

    ⚠ 外端は板の上面から FIN_OUT_H だけ立てる。ここが 3mm だと 2.5mm の bevel が
    clamp され、外端・側面・板の 3 面が集まる角に 0.03mm の三角形が残る（実測）。
    下端は板へ 1mm 沈める。面一に乗せると非多様体が 3 から 6 に増えた。
    """
    return [(0.0, PLATE_T - SPINE_LAP), (FIN_OUT_R, PLATE_T - SPINE_LAP),
            (FIN_OUT_R, PLATE_T + FIN_OUT_H), (BOSS_R, FIN_TOP_Z), (0.0, FIN_TOP_Z)]


# ---------------------------------------------------------------- build

def build():
    sx = SPAN / 2

    # 床に着く板（ソケット 2 つを包む長丸）
    body = prism("pipe_foot_pair", plate_poly(PLATE_R), Z_BUILD_BOT, PLATE_T)

    # ソケット 2 本
    prof = socket_profile()
    for k, x in enumerate((-sx, sx)):
        boolean(body, revolve("socket%d" % k, prof,
                              Matrix.Translation(Vector((x, 0, 0)) * MM)), "UNION")

    # 背骨
    boolean(body, wall("spine", spine_xs(), lambda x: PLATE_T - SPINE_LAP, spine_top,
                       -SPINE_T / 2, SPINE_T / 2), "UNION")

    # 横のひれ 4 枚（ソケットごとに ±Y）
    poly = fin_poly()
    for k, x in enumerate((-sx, sx)):
        for j, ang in enumerate((90.0, -90.0)):
            m = (Matrix.Translation(Vector((x, 0, 0)) * MM)
                 @ Matrix.Rotation(math.radians(ang), 4, "Z")
                 @ Matrix.Rotation(math.radians(90), 4, "X"))
            boolean(body, prism("fin%d%d" % (k, j), poly, -FIN_T / 2, FIN_T / 2, m),
                    "UNION")

    # 接合部に R
    clean(body)
    bevel(body, FILLET_R * MM, FILLET_SEG, FILLET_ANGLE)

    # 底を平らに切る（角丸を残したまま接地面を確保）
    boolean(body, box("cut_base", (600 * MM, 400 * MM, 100 * MM),
                      Matrix.Translation(Vector((0, 0, -50.0)) * MM)), "DIFFERENCE")

    # 両端を M 字ジョイントの外形に合わせて平らに切る。
    # 切る面はソケットの外周に接するので、筒はそのまま残って端の面だけが削れる
    for s in (1.0, -1.0):
        boolean(body, box("cut_end", (200 * MM, 400 * MM, 400 * MM),
                          Matrix.Translation(Vector((s * (HALF_W + 100), 0, 100)) * MM)),
                "DIFFERENCE")

    # パイプの穴（座面まで）
    for k, x in enumerate((-sx, sx)):
        boolean(body, cyl("bore%d" % k, BORE_D / 2, SEAT_Z, BOSS_TOP + 10, x, 0.0),
                "DIFFERENCE")

    # 穴あけが残す極小のスリバーを潰す。0.02mm は最小の造形物（口元の肉厚 1.0mm）の
    # 1/50 なので意図した形には触らない。
    # ⚠ 0.1mm まで粗くすると bevel の刻みまで潰れて、非多様体が 3 から 15 に増える
    clean(body, dist=2e-5)

    _activate(body)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_flat()
    return body


clear_scene()
body = build()

os.makedirs(EXPORTS_DIR, exist_ok=True)
stl = os.path.join(EXPORTS_DIR, "pipe_foot_pair.stl")
_activate(body)
bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True,
                      global_scale=1000.0, ascii_format=False)
print("Exported:", stl)
print("bbox mm:", [round(v * 1000, 2) for v in body.dimensions])
