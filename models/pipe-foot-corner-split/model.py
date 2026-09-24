"""角の床側の板を、パズルの凸凹つきで 2 枚に切る（X1C 向け）。

    ./run.sh models/pipe-foot-corner-split/model.py
    → exports/pipe_foot_corner_split_a.stl / _b.stl

板は lib/corner_plate.build_plate()（pipe-foot-corner-one と同じ形）に「節」（継ぎ目が壁を
横切る所の太い塊）を足して作り、継ぎ目の片側の領域（角柱）との共通部分を取って 2 枚にする。
凸凹はすべて z 方向の押し出しなので、B を A の上から落として組む。
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import bmesh
from blender_utils import clear_scene, EXPORTS_DIR
import foot_core as fc
import pair_base
import corner_plate
from params import (ONE, SEAM_S0, SEAM_X, SEAM_TIE_XY, GAP, TAB_CLEAR, tab_dimensions,
                    KNUCKLE_W, KNUCKLE_L, KNUCKLE_L_TAB, KNUCKLE_UP, TABS,
                    KNUCKLE_RADIUS, KNUCKLE_BLEND, S1_KNUCKLE_L,
                    ENTRY_CHAMFER, TAB_ROOT_R, BED)

FAR = 400.0          # 領域の角柱を板より十分大きく取る
Z_TOP = 300.0
S2 = math.sqrt(2.0)


def seam_frame(seg, pos):
    """継ぎ目上の点 p と、A → B の向き d（継ぎ目の法線）、継ぎ目に沿う向き t。"""
    if seg == "s1":
        p = (pos, pos)
        d = (1.0 / S2, -1.0 / S2)
    else:
        p = (SEAM_X, pos)
        d = (1.0, 0.0)
    return p, d, (-d[1], d[0])


def wall_height_at(seg):
    """継ぎ目が壁を横切る所の、壁の上端の高さ。"""
    if seg == "s1":
        return corner_plate.tie_top(ONE)(ONE.TIE_L / 2, 1)
    return corner_plate.branch_top(ONE)(SEAM_X, 1)


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def knuckle_blocks():
    """継ぎ目を横切る壁の節。丸い平面輪郭と、既存の壁につながる上面。"""
    out = []
    for seg, pos, owner, kind in TABS:
        if kind != "knuckle":
            continue
        p, d, t = seam_frame(seg, pos)
        h = wall_height_at(seg) + KNUCKLE_UP
        recess_l = S1_KNUCKLE_L if seg == "s1" else KNUCKLE_L
        la, lb = ((KNUCKLE_L_TAB, recess_l) if owner == "A" else
                  (recess_l, KNUCKLE_L_TAB))
        bm = bmesh.new()
        rings = []
        # Cross-sections avoid the triangular fan of a non-planar roof.
        # Extra samples on the circular ends preserve tangent continuity.
        r = KNUCKLE_RADIUS
        samples = {-la, lb}
        samples.update(-la + r * (1 - math.cos(math.pi * i / 32)) for i in range(17))
        samples.update(lb - r * (1 - math.cos(math.pi * i / 32)) for i in range(17))
        samples.update(-la + (la + lb) * i / 64 for i in range(65))
        for s in sorted(samples):
            edge = min(s + la, lb - s)
            w = KNUCKLE_W / 2
            if edge < r:
                w -= r - math.sqrt(max(0, r * r - (r - edge) ** 2))
            end_distance = min(s + la, lb - s)
            wall_z = (corner_plate.tie_top(ONE)(ONE.TIE_L / 2 + s, 1)
                      if seg == "s1" else
                      corner_plate.branch_top(ONE)(p[0] + d[0] * s, 1))
            top = wall_z + (h - wall_z) * _smooth(end_distance / KNUCKLE_BLEND)
            rings.append([bm.verts.new(((p[0] + d[0] * s + t[0] * u) * ONE.MM,
                                       (p[1] + d[1] * s + t[1] * u) * ONE.MM,
                                       z * ONE.MM))
                          for u, z in [(-w, -1), (w, -1), (w, top), (-w, top)]])
        for a, b in zip(rings, rings[1:]):
            for i in range(4):
                j = (i + 1) % 4
                bm.faces.new([a[i], a[j], b[j], b[i]])
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
        out.append(fc.finish("knuckle_" + seg, bm))
    return out


def _tab_outline(dim):
    """根元から幅 14 の首を経て、円形の頭へ接線でつながる輪郭。"""
    rx = dim["head_r"]
    ry = dim.get("head_ry", rx)
    neck = dim["neck_w"] / 2
    center = dim["neck_l"]
    narrow = TAB_ROOT_R
    upper = [(-4.0, neck + TAB_ROOT_R)]
    for i in range(25):
        a = math.pi + math.pi / 2 * i / 24
        upper.append((TAB_ROOT_R * (1 + math.cos(a)),
                      neck + TAB_ROOT_R * (1 + math.sin(a))))
    for i in range(1, 25):
        s = narrow + (center - narrow) * i / 24
        upper.append((s, neck + (ry - neck) * _smooth((s - narrow) / (center - narrow))))
    head = [(center + rx * math.cos(math.radians(90 - 180 * i / 48)),
             ry * math.sin(math.radians(90 - 180 * i / 48))) for i in range(1, 49)]
    return upper + head + [(s, -u) for s, u in reversed(upper[:-1])]


def _inset(poly, distance):
    """各辺を法線方向に distance 平行移動し、隣接する直線の交点を取る。"""
    area = sum(x * poly[(i + 1) % len(poly)][1] - y * poly[(i + 1) % len(poly)][0]
               for i, (x, y) in enumerate(poly))
    sign = 1.0 if area > 0 else -1.0
    result = []
    for i, point in enumerate(poly):
        before, after = poly[i - 1], poly[(i + 1) % len(poly)]
        e0 = (point[0] - before[0], point[1] - before[1])
        e1 = (after[0] - point[0], after[1] - point[1])
        n0 = (-sign * e0[1] / math.hypot(*e0), sign * e0[0] / math.hypot(*e0))
        n1 = (-sign * e1[1] / math.hypot(*e1), sign * e1[0] / math.hypot(*e1))
        scale = distance / max(0.1, (1.0 + n0[0] * n1[0] + n0[1] * n1[1]) / 2)
        result.append((point[0] + (n0[0] + n1[0]) * scale / 2,
                       point[1] + (n0[1] + n1[1]) * scale / 2))
    return result


def tab_solids(owner, shrink, tag):
    """owner の凸輪郭。相手の凹は名目寸法、凸は輪郭全体を法線方向に縮める。"""
    out = []
    for i, (seg, pos, o, kind) in enumerate(TABS):
        if o != owner:
            continue
        p, d, t = seam_frame(seg, pos)
        if owner == "B":
            d = (-d[0], -d[1])
        dim = tab_dimensions(seg, kind)
        z_top = (wall_height_at(seg) + KNUCKLE_UP if kind == "knuckle" else ONE.PLATE_T) + 1.0
        outline = _tab_outline(dim)
        if shrink:
            outline = _inset(outline, shrink)
        if tag == "cut":
            # B descends: its socket mouths open at the bottom for A's tall
            # keys; A's plate sockets open at the top for B's plate keys.
            c = ENTRY_CHAMFER
            levels = ([(-1.0, -c), (0.0, -c), (c, 0.0), (z_top, 0.0)]
                      if kind == "knuckle" else
                      [(-1.0, 0.0), (ONE.PLATE_T - c, 0.0),
                       (ONE.PLATE_T, -c), (z_top, -c)])
        else:
            levels = [(-1.0, 0.0), (z_top, 0.0)]
        out.append(tab_loft("%s_tab%d" % (tag, i), outline, levels, p, d, t))
    return out


def tab_loft(name, outline, levels, p, d, t):
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    bm = bmesh.new()
    rings, shapes = [], []
    for z, offset in levels:
        shape = _inset(outline, offset) if offset else outline
        xy = [(p[0] + d[0] * s + t[0] * u, p[1] + d[1] * s + t[1] * u)
              for s, u in shape]
        shapes.append(xy)
        rings.append([bm.verts.new((x * ONE.MM, y * ONE.MM, z * ONE.MM)) for x, y in xy])
    n = len(outline)
    for lo, hi in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    for ring, shape in [(rings[0], shapes[0]), (rings[-1], shapes[-1])]:
        for a, b, c in tessellate_polygon([[Vector((x, y, 0)) for x, y in shape]]):
            bm.faces.new([ring[a], ring[b], ring[c]])
    return fc.finish(name, bm)


def side_poly(side, e):
    """継ぎ目から e だけ side（"A" / "B"）の側へ寄せた境界で、その側を覆う大きな多角形。
    継ぎ目 1 は x - y = 0 の線（A 側は x - y < 0）、継ぎ目 2 は x = SEAM_X の線（A 側は x < SEAM_X）。"""
    s = -1.0 if side == "A" else 1.0
    x2 = SEAM_X + s * e
    k = (x2, x2 - s * e * S2)                   # 2 本の線の交点
    top_t = 60.0                                # S0 の先（板の外）まで継ぎ目 1 を延ばす
    p_top = (SEAM_S0[0] + top_t + s * e / S2, SEAM_S0[1] + top_t - s * e / S2)
    if side == "A":
        return [p_top, (p_top[0], FAR), (-FAR, FAR), (-FAR, -FAR), (x2, -FAR), k]
    return [p_top, k, (x2, -FAR), (FAR, -FAR), (FAR, FAR), (p_top[0], FAR)]


def region(side):
    """side の片が占める領域。継ぎ目から GAP/2 寄せた境界 + 自分の凸（TAB_CLEAR 痩せ）
    - 相手の凹（図面の寸法）。A 側は折れ点で凹むので prism_concave で作る。"""
    reg = fc.prism_concave("region_" + side, side_poly(side, GAP / 2), -1.0, Z_TOP)
    for ob in tab_solids(side, TAB_CLEAR, "own"):
        fc.boolean(reg, ob, "UNION", solver="EXACT")
    other = "B" if side == "A" else "A"
    for ob in tab_solids(other, 0.0, "cut"):
        fc.boolean(reg, ob, "DIFFERENCE", solver="EXACT")
    return reg


def copy_of(ob, name):
    cp = ob.copy()
    cp.data = ob.data.copy()
    cp.name = name
    bpy.context.scene.collection.objects.link(cp)
    return cp


def prepare_export(ob):
    """三角化の後に薄片を除き、STLと3MFに同じ閉じたメッシュを渡す。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.verts.index_update()
    groups = {}
    for face in bm.faces:
        groups.setdefault(tuple(sorted(v.index for v in face.verts)), []).append(face)
    cancel = []
    for faces in groups.values():
        if len(faces) > 1:
            assert len(faces) == 2 and faces[0].normal.dot(faces[1].normal) < -0.999, \
                'Unexpected coincident faces in ' + ob.name
            # Oppositely oriented coincident triangles enclose no material.
            cancel.extend(faces)
    if cancel:
        bmesh.ops.delete(bm, geom=cancel, context='FACES_ONLY')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bmesh.ops.dissolve_degenerate(bm, dist=1e-8, edges=bm.edges[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bad = sum(not e.is_manifold for e in bm.edges)
    assert bad == 0, f'{ob.name}: {bad} nonmanifold edges after triangulation'
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


clear_scene()
plate = corner_plate.build_plate(ONE, "plate", extras=knuckle_blocks())
piece_b = copy_of(plate, "pipe_foot_corner_split_b")
piece_a = plate
piece_a.name = "pipe_foot_corner_split_a"

fc.boolean(piece_a, region("A"), "INTERSECT", solver="EXACT")
fc.boolean(piece_b, region("B"), "INTERSECT", solver="EXACT")
for ob in (piece_a, piece_b):
    pair_base.finish(ONE, ob)
    prepare_export(ob)
    assert max(ob.dimensions.x, ob.dimensions.y) / ONE.MM <= BED, 'Part exceeds print area'

pair_base.export(piece_a, EXPORTS_DIR, "pipe_foot_corner_split_a.stl")
pair_base.export(piece_b, EXPORTS_DIR, "pipe_foot_corner_split_b.stl")

from export_3mf import export_part
export_part(piece_a, EXPORTS_DIR, "pipe-foot-corner-refined-a.3mf")
export_part(piece_b, EXPORTS_DIR, "pipe-foot-corner-refined-b.3mf")
