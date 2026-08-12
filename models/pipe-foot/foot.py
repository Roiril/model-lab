"""28mm パイプの脚を床に固定するベースの形状生成。

底面をベッドに置いた向きのまま無サポートで刷れる。
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

from params import (
    MM, PIPE_OD, BORE_D, BOSS_R, SEAT_Z, BOSS_TOP, MOUTH_TAPER, TIP_R,
    FLANGE_T, HUB_T, DISC_R, LOBE_R, BOLT_R, SCREW_D, SCREW_CHAMFER, CONE_BASE_R,
    RIB_T, RIB_OUT_R, RIB_TOP_Z,
    FILLET_R, FILLET_ANGLE, FILLET_SEG, BASE_ROUND, SEG, CONE_SEG, REF_LEN,
)

Z_BUILD_BOT = -BASE_ROUND     # 面取り分だけ下に伸ばして最後に切る


# ---------------------------------------------------------------- helpers

def get_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    return col


def _activate(ob):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def _finish(name, bm, col, matrix=None):
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if matrix is not None:
        ob.matrix_world = matrix
    return ob


def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def revolve(name, profile, col, matrix=None, seg=SEG):
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
    return _finish(name, bm, col, matrix)


def cyl(name, r, z0, z1, col, cx=0.0, cy=0.0, seg=SEG):
    return revolve(name, [(z0, r), (z1, r)], col,
                   Matrix.Translation(Vector((cx, cy, 0.0)) * MM), seg)


def prism(name, poly, z0, z1, col, matrix=None):
    """poly: [(x, y)]（メートル）。z0→z1 に押し出してから matrix で置く。"""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in poly]
    hi = [bm.verts.new((x, y, z1)) for x, y in poly]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    return _finish(name, bm, col, matrix)


def box(name, size, matrix, col):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts[:], vec=Vector(size))
    return _finish(name, bm, col, matrix)


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


BOLT_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ---------------------------------------------------------------- build

def core_profile():
    """底面 → ソケット口元までを 1 本の回転体で作るプロファイル [(z, r)]。

    フランジは外周 FLANGE_T、中央 HUB_T の段付き。段は上向きの円錐なので無支持。
    台座は smoothstep で絞る。口元はさらに TIP_R まで落として段差を小さくする。
    """
    pts = [(Z_BUILD_BOT, DISC_R), (FLANGE_T, DISC_R), (HUB_T, CONE_BASE_R)]
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


def rib_poly():
    """リブの断面 [(r, z)]。外端は 3mm の高さを残して尖らせない。"""
    return [(0.0, FLANGE_T), (RIB_OUT_R, FLANGE_T), (RIB_OUT_R, FLANGE_T + 3.0),
            (BOSS_R, RIB_TOP_Z), (0.0, RIB_TOP_Z)]


def build_foot(col_name="foot"):
    col = get_collection(col_name)

    # フランジ（段付き）＋台座＋ソケットを 1 本の回転体で
    body = revolve("pipe_foot", core_profile(), col)

    # ねじ穴まわりのふくらみ 4 方向
    for k, (dx, dy) in enumerate(BOLT_DIRS):
        boolean(body, cyl("lobe%d" % k, LOBE_R, Z_BUILD_BOT, FLANGE_T, col,
                          BOLT_R * dx, BOLT_R * dy, seg=48), "UNION")

    # 補強リブ 4 枚（ねじの方向に合わせる）
    poly = [(x * MM, y * MM) for x, y in rib_poly()]
    for k, (dx, dy) in enumerate(BOLT_DIRS):
        ang = math.atan2(dy, dx)
        m = (Matrix.Rotation(ang, 4, "Z")
             @ Matrix.Rotation(math.radians(90), 4, "X"))
        boolean(body, prism("rib%d" % k, poly, -RIB_T / 2 * MM, RIB_T / 2 * MM, col, m),
                "UNION")

    # 接合部に R
    clean(body)
    bevel(body, FILLET_R * MM, FILLET_SEG, FILLET_ANGLE)

    # 底を平らに切る
    boolean(body, box("cut_base", (400 * MM, 400 * MM, 100 * MM),
                      Matrix.Translation(Vector((0, 0, -50.0)) * MM), col),
            "DIFFERENCE")

    # パイプの穴（座面まで）
    boolean(body, cyl("bore", BORE_D / 2, SEAT_Z, BOSS_TOP + 10, col), "DIFFERENCE")

    # ねじ穴 4 本（口に面取り）
    r = SCREW_D / 2
    c = SCREW_CHAMFER
    for k, (dx, dy) in enumerate(BOLT_DIRS):
        prof = [(-5.0, r), (FLANGE_T - c, r), (FLANGE_T, r + c), (FLANGE_T + 5.0, r + c)]
        boolean(body, revolve("screw%d" % k, prof, col,
                              Matrix.Translation(Vector((BOLT_R * dx, BOLT_R * dy, 0)) * MM),
                              seg=48), "DIFFERENCE")

    _activate(body)
    bpy.ops.object.shade_flat()
    return body, col


def build_ref_pipe(col_name="foot_ref"):
    col = get_collection(col_name)
    cyl("ref_leg", PIPE_OD / 2, SEAT_Z, SEAT_Z + REF_LEN, col, seg=48)
    return col


def build_all(ref=True):
    body, col = build_foot()
    if ref:
        build_ref_pipe()
    return body
