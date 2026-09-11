"""M 字ジョイントの脚 2 本と、その横の 3 本目の脚を床で受けるベース。

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


def _normal_angle(p, q):
    """反時計回りの多角形の辺 p→q の、外向き法線の角度。"""
    return math.atan2(-(q[0] - p[0]), q[1] - p[1])


def hull_poly(centers, r, seg=SEG):
    """半径 r の円を centers（反時計回り）に置いたときの凸包。反時計回りの点列。

    各円の上では、入ってくる辺の法線から出ていく辺の法線までの弧を描き、
    弧どうしは共通外接線でつながる。円が 2 つなら長丸になる。
    """
    n = len(centers)
    pts = []
    for i in range(n):
        p = centers[i]
        a0 = _normal_angle(centers[i - 1], p)
        a1 = _normal_angle(p, centers[(i + 1) % n])
        while a1 <= a0:
            a1 += 2 * math.pi
        k = max(1, round(seg * (a1 - a0) / (2 * math.pi)))
        for j in range(k + 1):
            a = a0 + (a1 - a0) * j / k
            pts.append((p[0] + r * math.cos(a), p[1] + r * math.sin(a)))
    return pts


def spine_top(x):
    """主材の上端。中央で傾きが 0 になる二次曲線。

    smoothstep にすると中央が平らな帯になり、板を立てただけに見える。
    曲げを受けるのは根元だけなので、中央は低くてよい。
    """
    t = abs(x) / (SPAN / 2)
    return SPINE_MID_Z + (SPINE_TOP_Z - SPINE_MID_Z) * t * t


def branch_top(y):
    """枝の上端。主材の側面から出る所の高さを起点に、同じ二次曲線で上がる。"""
    y0 = SPINE_T / 2
    z0 = spine_top(y0)
    t = (y - y0) / (THIRD_OFF - y0)
    return z0 + (SPINE_TOP_Z - z0) * t * t


def t_spine():
    """背骨。X 方向の主材と、3 本目のソケットへ伸びる枝を 1 つのメッシュで作る。

    枝を別体にして boolean で足すと、主材の上面（中央で 14mm）と枝の上面が
    ほぼ同じ高さで交わり、0.1mm 以下の段や薄片が出て bevel が荒れる。
    主材の x に ±SPINE_T/2 を含めてそのあいだに点を置かず、+Y の側面のその
    四角形を抜いて、枝の付け根をその 4 頂点に直接つなぐ。

    ⚠⚠ 凹んだ輪郭を prism() の n-gon の蓋で作ってはいけない。三角化が凹みを
    またいで膜を張り、弧の内側が塞がって板になる（Blender 5.1 で実測）。
    しかも体積も非多様体エッジ数も正しいままなので、数値では気づけない。
    蓋も四角形の帯で作れば、そもそも凹みが問題にならない。
    """
    sx = SPAN / 2
    ht = SPINE_T / 2
    zb = PLATE_T - SPINE_LAP
    n = SPINE_SEG // 2
    bm = bmesh.new()

    def V(x, y, z):
        return bm.verts.new((x * MM, y * MM, z * MM))

    # 主材。両端はソケットの軸まで伸ばし、肉の中で終わらせる
    xs = ([-sx + (sx - ht) * i / n for i in range(n + 1)]
          + [ht + (sx - ht) * i / n for i in range(n + 1)])
    k = n                                      # xs[k] = -ht, xs[k+1] = +ht
    lo0 = [V(x, -ht, zb) for x in xs]
    hi0 = [V(x, -ht, spine_top(x)) for x in xs]
    lo1 = [V(x, ht, zb) for x in xs]
    hi1 = [V(x, ht, spine_top(x)) for x in xs]
    for i in range(len(xs) - 1):
        bm.faces.new([lo0[i], lo0[i + 1], hi0[i + 1], hi0[i]])
        if i != k:                             # 枝の付け根は抜く
            bm.faces.new([lo1[i], lo1[i + 1], hi1[i + 1], hi1[i]])
        bm.faces.new([lo0[i], lo1[i], lo1[i + 1], lo0[i + 1]])
        bm.faces.new([hi0[i], hi1[i], hi1[i + 1], hi0[i + 1]])
    bm.faces.new([lo0[0], hi0[0], hi1[0], lo1[0]])
    bm.faces.new([lo0[-1], hi0[-1], hi1[-1], lo1[-1]])

    # 枝。付け根の 4 頂点は主材のもの。先端は 3 本目のソケットの軸まで
    ys = [ht + (THIRD_OFF - ht) * j / BRANCH_SEG for j in range(BRANCH_SEG + 1)]
    la = [lo1[k]] + [V(-ht, y, zb) for y in ys[1:]]
    ha = [hi1[k]] + [V(-ht, y, branch_top(y)) for y in ys[1:]]
    lb = [lo1[k + 1]] + [V(ht, y, zb) for y in ys[1:]]
    hb = [hi1[k + 1]] + [V(ht, y, branch_top(y)) for y in ys[1:]]
    for j in range(BRANCH_SEG):
        bm.faces.new([la[j], la[j + 1], ha[j + 1], ha[j]])
        bm.faces.new([lb[j], lb[j + 1], hb[j + 1], hb[j]])
        bm.faces.new([la[j], lb[j], lb[j + 1], la[j + 1]])
        bm.faces.new([ha[j], hb[j], hb[j + 1], ha[j + 1]])
    bm.faces.new([la[-1], ha[-1], hb[-1], lb[-1]])
    return _finish("spine", bm)


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
    # ソケットの軸と、そのひれの向き。ひれは背骨と直交する側に出す
    sockets = [((-sx, 0.0), (90.0, -90.0)),
               ((sx, 0.0), (90.0, -90.0)),
               (THIRD, (0.0, 180.0))]

    # 床に着く板（ソケット 3 つを包む凸包。反時計回りに並べる）
    body = prism("pipe_foot_pair", hull_poly([c for c, _ in sockets], PLATE_R),
                 Z_BUILD_BOT, PLATE_T)

    # ソケット 3 本
    prof = socket_profile()
    for k, (c, _) in enumerate(sockets):
        boolean(body, revolve("socket%d" % k, prof,
                              Matrix.Translation(Vector((c[0], c[1], 0)) * MM)), "UNION")

    # 背骨（主材 + 枝）
    boolean(body, t_spine(), "UNION")

    # 横のひれ 6 枚（ソケットごとに 2 枚）
    poly = fin_poly()
    for k, (c, angs) in enumerate(sockets):
        for j, ang in enumerate(angs):
            m = (Matrix.Translation(Vector((c[0], c[1], 0)) * MM)
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

    # パイプの穴（座面まで）
    for k, (c, _) in enumerate(sockets):
        boolean(body, cyl("bore%d" % k, BORE_D / 2, SEAT_Z, BOSS_TOP + 10, c[0], c[1]),
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
