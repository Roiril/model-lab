"""28mm パイプ用 5方向ジョイントの形状生成。

build_joint() はシーンをクリアしない。BlenderMCP で開きっぱなしの
シーンへ差し込めるように、生成物は指定コレクションへ入れる。
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

from params import (
    MM, BORE_D, HUB_D, END_D, SIDE_Y, SIDE_Z, SLEEVE_L, TAPER_L,
    LEG_TOP_D, LEG_BOT_D, SLOPE_DEG, STRUT_W, STRUT_T, SEG, TAPER_SEG,
    PIPE_OD, REF_RAIL_L, REF_LEG_L,
)


# ---------------------------------------------------------------- helpers

def get_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    return col


def _finish(name, bm, col):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def revolve(name, profile, col, matrix=None, seg=SEG):
    """profile: [(axial, radius)] radius>0、axial は単調増加。ローカル軸は Z。"""
    bm = bmesh.new()
    rings = []
    for a, r in profile:
        ring = [
            bm.verts.new((r * math.cos(2 * math.pi * i / seg),
                          r * math.sin(2 * math.pi * i / seg),
                          a))
            for i in range(seg)
        ]
        rings.append(ring)
    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    ob = _finish(name, bm, col)
    if matrix is not None:
        ob.matrix_world = matrix
    return ob


def taper_profile(length, taper, r_hub, r_end):
    """両端が r_end、中央が r_hub の S 字テーパ profile を返す（軸は -length/2 .. +length/2）。"""
    half = length / 2.0
    pts = []
    for i in range(TAPER_SEG + 1):
        t = i / TAPER_SEG
        pts.append((-half + taper * t, r_end + (r_hub - r_end) * smoothstep(t)))
    for i in range(TAPER_SEG + 1):
        t = i / TAPER_SEG
        pts.append((half - taper + taper * t, r_hub + (r_end - r_hub) * smoothstep(t)))
    # 重複する軸位置を除去
    out = [pts[0]]
    for p in pts[1:]:
        if p[0] - out[-1][0] > 1e-9:
            out.append(p)
    return out


def box(name, size, matrix, col):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts, vec=Vector(size))
    ob = _finish(name, bm, col)
    ob.matrix_world = matrix
    return ob


def boolean(target, cutter, op="UNION", solver="MANIFOLD"):
    # EXACT は voxel remesh 後の十数万ポリのメッシュに止まり穴を空けると
    # 結果が空になる（Blender 5.1 で実測）。MANIFOLD なら通る。
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = solver
    _activate(target)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def frame(origin=(0, 0, 0), rot=None):
    m = Matrix.Translation(Vector(origin) * MM)
    if rot is not None:
        m = m @ rot
    return m


# ---------------------------------------------------------------- build

# ローカル Z を +X へ向ける回転（レール軸はワールド X）
ROT_Z_TO_X = Matrix.Rotation(math.radians(90), 4, "Y")


def leg_frame(sy):
    """脚の座標系。原点＝左右レールの軸、ローカル +Z＝脚が伸びる向きの逆（上）。
    SLOPE_DEG だけ Y 軸まわりに倒す。"""
    return (Matrix.Translation(Vector((0.0, sy, SIDE_Z)) * MM)
            @ Matrix.Rotation(math.radians(SLOPE_DEG), 4, "Y"))


def build_joint(col_name="joint"):
    col = get_collection(col_name)

    r_hub, r_end, r_bore = HUB_D / 2, END_D / 2, BORE_D / 2

    # --- レールを掴むスリーブ 3 本（軸 = X）---
    prof = [(a * MM, r * MM) for a, r in taper_profile(SLEEVE_L, TAPER_L, r_hub, r_end)]
    parts = [
        revolve("sleeve_c", prof, col, frame((0, 0, 0), ROT_Z_TO_X)),
        revolve("sleeve_p", prof, col, frame((0, SIDE_Y, SIDE_Z), ROT_Z_TO_X)),
        revolve("sleeve_n", prof, col, frame((0, -SIDE_Y, SIDE_Z), ROT_Z_TO_X)),
    ]

    # --- 脚のソケット（レール軸から下に伸ばす。開口端だけ絞る）---
    cprof = []
    for i in range(TAPER_SEG + 1):
        t = i / TAPER_SEG
        cprof.append(((-LEG_BOT_D + TAPER_L * t) * MM,
                      (r_end + (r_hub - r_end) * smoothstep(t)) * MM))
    cprof.append((0.0, r_hub * MM))
    for sy in (SIDE_Y, -SIDE_Y):
        parts.append(revolve("column_%s" % ("p" if sy > 0 else "n"), cprof, col,
                             leg_frame(sy)))

    # --- 斜材：中央スリーブ ↔ 左右スリーブ ---
    for sy in (SIDE_Y, -SIDE_Y):
        d = Vector((0.0, sy, SIDE_Z)).normalized()
        perp = Vector((0.0, -d.z, d.y))  # ex × d（右手系を保つ）
        span = math.hypot(sy, SIDE_Z)
        mid = Vector((0.0, sy, SIDE_Z)) * 0.5 * MM
        rot = Matrix((
            (1.0, d.x, perp.x),
            (0.0, d.y, perp.y),
            (0.0, d.z, perp.z),
        )).to_4x4()
        m = Matrix.Translation(mid) @ rot
        parts.append(box("strut_%s" % ("p" if sy > 0 else "n"),
                         (STRUT_W * MM, (span + 12.0) * MM, STRUT_T * MM), m, col))

    # --- 合体 ---
    body = parts[0]
    body.name = "pipe_joint"
    for p in parts[1:]:
        boolean(body, p, "UNION")

    return body, col


def _activate(ob):
    """ops 系は選択状態を見るので必ず通す。"""
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def _voxel_remesh(ob, voxel):
    ob.data.remesh_voxel_size = voxel
    ob.data.remesh_voxel_adaptivity = 0.0
    _activate(ob)
    if bpy.ops.object.voxel_remesh() != {"FINISHED"}:
        raise RuntimeError("voxel_remesh failed")


def _displace(ob, dist):
    mod = ob.modifiers.new("disp", "DISPLACE")
    mod.direction = "NORMAL"
    mod.mid_level = 0.0
    mod.strength = dist
    _activate(ob)
    bpy.ops.object.modifier_apply(modifier=mod.name)


def _smooth(ob, factor, iters):
    if iters <= 0:
        return
    mod = ob.modifiers.new("smooth", "SMOOTH")
    mod.factor = factor
    mod.iterations = iters
    _activate(ob)
    bpy.ops.object.modifier_apply(modifier=mod.name)


def fillet_closing(ob, radius, voxel, steps=4, polish=2):
    """モルフォロジーのクロージング（膨張→収縮）で凹エッジだけに R を付ける。
    凸のシルエットはほぼ保たれるので、接合部の谷だけが滑らかになる。

    一気に R だけ法線方向へ動かすと自己交差が大きくなって縫い目がギザつくので、
    R/steps ずつ動かして毎回 voxel remesh で交差を解消する。"""
    _voxel_remesh(ob, voxel)
    for sign in (1.0, -1.0):
        for _ in range(steps):
            _smooth(ob, 0.5, 1)
            _displace(ob, sign * radius / steps)
            _voxel_remesh(ob, voxel)
    _smooth(ob, 0.5, polish)
    return ob


def cut_bores(body, col):
    r_bore = BORE_D / 2

    # レール 3 本（貫通）
    long_prof = [(-300 * MM, r_bore * MM), (300 * MM, r_bore * MM)]
    for name, y, z in (("bore_c", 0, 0), ("bore_p", SIDE_Y, SIDE_Z), ("bore_n", -SIDE_Y, SIDE_Z)):
        cut = revolve(name, long_prof, col, frame((0, y, z), ROT_Z_TO_X))
        boolean(body, cut, "DIFFERENCE")

    # 脚 2 本（下から差し込む止まり穴。上端＝座面）
    leg_prof = [((-LEG_BOT_D - 60) * MM, r_bore * MM), (-LEG_TOP_D * MM, r_bore * MM)]
    for sy in (SIDE_Y, -SIDE_Y):
        cut = revolve("bore_leg", leg_prof, col, leg_frame(sy))
        boolean(body, cut, "DIFFERENCE")

    return body


def build_ref_pipes(col_name="ref_pipes"):
    """実寸の参照パイプ。印刷対象ではない。"""
    col = get_collection(col_name)
    r = PIPE_OD / 2
    rail = [(-REF_RAIL_L / 2 * MM, r * MM), (REF_RAIL_L / 2 * MM, r * MM)]
    revolve("rail_c", rail, col, frame((0, 0, 0), ROT_Z_TO_X), seg=48)
    revolve("rail_p", rail, col, frame((0, SIDE_Y, SIDE_Z), ROT_Z_TO_X), seg=48)
    revolve("rail_n", rail, col, frame((0, -SIDE_Y, SIDE_Z), ROT_Z_TO_X), seg=48)
    leg = [((-LEG_TOP_D - REF_LEG_L) * MM, r * MM), (-LEG_TOP_D * MM, r * MM)]
    revolve("leg_p", leg, col, leg_frame(SIDE_Y), seg=48)
    revolve("leg_n", leg, col, leg_frame(-SIDE_Y), seg=48)
    return col


def build_all(fillet_r=4.0, voxel=0.5, ref=True):
    body, col = build_joint()
    if fillet_r:
        fillet_closing(body, fillet_r * MM, voxel * MM)
    cut_bores(body, col)
    _activate(body)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    if ref:
        build_ref_pipes()
    return body
