"""動き・組み立て・印刷の検証（Blender の Python で走らせる。bpy の部品は使わず STL を直に読む）。

    "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python models/mystery-box-sg92r-c2/verify.py

入力: model.py が build/ に出した組んだ姿勢の STL（mm）と刷る姿勢の STL。
出力: build/verify_report.json
判定は数で行う。計器は先に「当たるはず」「当たらないはず」の両方で校正してから使う。
"""
import json
import math
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.stdout.reconfigure(encoding="utf-8")

from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import linkage as K  # noqa: E402
import params as P  # noqa: E402

BUILD = os.path.join(HERE, "build")
MM = 1000.0
HY, HZ = K.H
OY, OZ = K.O
from printmech.mesh import Mesh, clearance, inside  # noqa: E402


def contact(a, b, depth=True, step=1):
    """三角形の交差と、包絡の外を除外した食い込み。"""
    ba, bb = a.bvh(), b.bvh()
    pairs = ba.overlap(bb)
    if not pairs and not depth:
        return dict(hits=0, depth=0.0)
    maximum = 0.0
    contained_samples = 0
    # 交差する面の頂点を調べる。箱の全頂点を毎工程で光線判定する必要はない。
    candidate_faces = [set(), set()]
    for ia, ib in pairs:
        candidate_faces[0].add(ia)
        candidate_faces[1].add(ib)
    for index, (mesh, other, tree) in enumerate(((a, b, bb), (b, a, ba))):
        samples = []
        if pairs:
            # 頂点だけでは、全頂点が相手の外にある薄板同士の十字交差を見落とす。
            # 交差した三角形の辺中点と重心側の面内点も調べる。
            for face_index in sorted(candidate_faces[index]):
                p, q, r = (mesh.v[vi] for vi in mesh.t[face_index])
                for i in range(3):
                    for j in range(3 - i):
                        samples.append((p * (2 - i - j) + q * i + r * j) / 2)
                samples.append((p + q + r) / 3)
        else:
            samples = [mesh.v[vi] for vi in range(0, len(mesh.v), step)]
        for v in samples:
            nearest = tree.find_nearest(v)
            if nearest[0] is None:
                continue
            is_inside = other.contains(v, tree)
            if is_inside:
                contained_samples += 1
                maximum = max(maximum, nearest[3])
    # 面交差がないのに単独頂点だけが内側になる値は、光線が角を通るときの偶奇誤差。
    # 完全内包なら閉じた連結成分の全頂点が内側になるため、複数点で裏を取る。
    if not pairs and contained_samples < 3:
        maximum = 0.0
    return dict(hits=len(pairs), depth=round(maximum, 3), contained_samples=contained_samples)


def component_count(mesh):
    by_vertex = {i: set() for i in range(len(mesh.v))}
    for tri in mesh.t:
        for i, vertex in enumerate(tri):
            by_vertex[vertex].update((tri[(i + 1) % 3], tri[(i + 2) % 3]))
    remaining = set(by_vertex)
    count = 0
    while remaining:
        count += 1
        pending = [remaining.pop()]
        while pending:
            vertex = pending.pop()
            linked = by_vertex[vertex] & remaining
            remaining.difference_update(linked)
            pending.extend(linked)
    return count


def flat_plane(mesh, axis, target, center_ok):
    candidates = []
    for tri in mesh.t:
        points = [mesh.v[index] for index in tri]
        values = [point[axis] for point in points]
        if max(values) - min(values) > 0.002:
            continue
        center = sum(points, Vector()) / 3
        if center_ok(center):
            candidates.append(sum(values) / 3)
    if not candidates:
        raise ValueError(f"{mesh.name}: 基準面を検出できません axis={axis} target={target}")
    return min(candidates, key=lambda value: abs(value - target))


def calibrate_flat_plane():
    mesh = Mesh(
        [Vector((0, 0, 7)), Vector((4, 0, 7)), Vector((0, 4, 7)),
         Vector((10, 3, 0)), Vector((14, 3, 0)), Vector((10, 3, 4))],
        [(0, 1, 2), (3, 4, 5)], "datum_calibration")
    z_plane = flat_plane(mesh, 2, 7, lambda p: p.x < 5)
    y_plane = flat_plane(mesh, 1, 3, lambda p: p.x > 5)
    miss_raises = False
    try:
        flat_plane(mesh, 2, 0, lambda p: False)
    except ValueError:
        miss_raises = True
    return dict(z_plane_mm=round(z_plane, 4), y_plane_mm=round(y_plane, 4),
                missing_plane_rejected=miss_raises,
                ok=abs(z_plane - 7) < 0.001 and abs(y_plane - 3) < 0.001 and miss_raises)


def servo_fit(parts, coupon):
    """実際のSTLから座面と長手基準面を読み、寸法図の仮定と試片を照合する。"""
    body = parts["box"]
    clip = parts["clip"]
    seat_expected = OZ - P.SG.BODY_W * MM / 2
    near_offset_expected = (P.SG.BODY_CENTER_X + P.SG.BODY_L / 2) * MM
    near_expected = OY - near_offset_expected
    far_expected = OY - (P.SG.BODY_CENTER_X - P.SG.BODY_L / 2) * MM
    far_gap = P.SERVO_FAR_END_GAP * MM
    far_wall = far_expected + far_gap
    seat_filter = lambda p: (-31.5 < p.x < P.PED_X1 * MM - 0.5
                             and near_expected + 1 < p.y < far_expected - 1
                             and P.FLOOR * MM < p.z < OZ)
    near_filter = lambda p: (p.x < P.END_WALL_X1 * MM - 0.2
                             and seat_expected + 0.2 < p.z < OZ + P.SG.BODY_W * MM / 2 - 0.2)
    seat_actual = flat_plane(body, 2, seat_expected, seat_filter)
    near_actual = flat_plane(body, 1, near_expected, near_filter)
    coupon_seat = flat_plane(coupon, 2, seat_expected, seat_filter)
    coupon_near = flat_plane(coupon, 1, near_expected, near_filter)

    tip_z0 = seat_expected + P.SERVO_SPRING_TIP_ABOVE_SEAT * MM
    tip_z1 = tip_z0 + P.SERVO_SPRING_TIP_H * MM
    tip_vertices = [v for v in clip.v
                    if P.CLIP_X0 * MM - 0.01 <= v.x <= P.CLIP_X1 * MM + 0.01
                    and tip_z0 - 0.01 <= v.z <= tip_z1 + 0.01
                    and v.y > near_expected]
    if not tip_vertices:
        raise ValueError("clip: サーボ長手押さえの先端を検出できません")
    spring_tip_y = min(v.y for v in tip_vertices)
    intent_actual = far_expected - spring_tip_y
    root_z = OZ + P.SG.BODY_W * MM / 2 + P.CLIP_TOP_GAP * MM
    tip_mid_z = (tip_z0 + tip_z1) / 2
    free_length = root_z - tip_mid_z
    spring_t = P.SERVO_SPRING_T * MM
    strain = 1.5 * spring_t * intent_actual / free_length ** 2
    strain_limit = 0.02
    deflection_at_limit = strain_limit * free_length ** 2 / (1.5 * spring_t)
    leaf_outer = far_wall + spring_t
    front_leg_inner = (P.PED_Y1 + P.CLIP_SIDE_GAP) * MM
    positive_length_error = min(deflection_at_limit - intent_actual,
                                front_leg_inner - leaf_outer)
    axis_tol = P.SERVO_DATUM_AXIS_TOL * MM
    body_datums = dict(
        seat_z_mm=round(seat_actual, 4),
        shaft_z_from_seat_mm=round(OZ - seat_actual, 4),
        shaft_z_expected_mm=round(P.SG.BODY_W * MM / 2, 4),
        shaft_z_error_mm=round(OZ - seat_actual - P.SG.BODY_W * MM / 2, 4),
        near_plane_y_mm=round(near_actual, 4),
        shaft_y_from_near_plane_mm=round(OY - near_actual, 4),
        shaft_y_expected_mm=round(near_offset_expected, 4),
        shaft_y_error_mm=round(OY - near_actual - near_offset_expected, 4),
    )
    coupon_datums = dict(
        components=component_count(coupon),
        seat_z_mm=round(coupon_seat, 4),
        near_plane_y_mm=round(coupon_near, 4),
        seat_matches_body_mm=round(coupon_seat - seat_actual, 4),
        near_plane_matches_body_mm=round(coupon_near - near_actual, 4),
    )
    initial_contact = contact(clip, parts["ref_body"])
    spring = dict(
        thickness_mm=round(spring_t, 4),
        intent_design_mm=round(P.SERVO_SPRING_INTENT * MM, 4),
        intent_mesh_mm=round(intent_actual, 4),
        free_length_mm=round(free_length, 4),
        nominal_strain_pct=round(strain * 100, 4),
        strain_limit_pct=round(strain_limit * 100, 2),
        initial_contact=initial_contact,
        insertion_check="assembly.E_clip_press（上からの全経路）",
        method="梁下面を根元固定とする片持ち近似。先端の公称食い込みをたわみ量とした。",
    )
    allowance = dict(
        body_width_error_abs_max_mm=round(axis_tol * 2, 4),
        shaft_to_near_end_error_abs_max_mm=round(axis_tol, 4),
        body_length_error_range_mm=[round(-intent_actual, 4), round(positive_length_error, 4)],
        condition="実測幅の差の半分と軸寄り端寸法の差が各軸誤差内で、長さ差が範囲内なら形状で吸収できる。試片で確認する。",
    )
    numerical_tol = 0.003
    minimum_wall = min(P.WALL, P.FLOOR, P.SERVO_SPRING_T) * MM
    ok = (abs(body_datums["shaft_z_error_mm"]) <= numerical_tol
          and abs(body_datums["shaft_y_error_mm"]) <= numerical_tol
          and coupon_datums["components"] == 1
          and abs(coupon_datums["seat_matches_body_mm"]) <= numerical_tol
          and abs(coupon_datums["near_plane_matches_body_mm"]) <= numerical_tol
          and abs(intent_actual - P.SERVO_SPRING_INTENT * MM) <= numerical_tol
          and initial_contact["hits"] > 0 and 0.08 <= initial_contact["depth"] <= 0.16
          and strain < strain_limit and minimum_wall >= 1.2 - numerical_tol
          and P.SG.REFERENCE_PREFIX == "sg92r-photo-c2-drawing-trial")
    return dict(
        profile=P.SERVO_DIMENSION_PROFILE,
        body_datums=body_datums,
        coupon_datums=coupon_datums,
        spring=spring,
        drawing_error_allowance=allowance,
        minimum_wall_mm=round(minimum_wall, 4),
        minimum_wall_design_mm=round(minimum_wall, 4),
        physical_fit_pending=not P.SERVO_DIMENSION_PROFILE["physical_fit_confirmed"],
        ok=ok,
    )


def rot_x(deg, cy, cz):
    return (Matrix.Translation((0, cy, cz)) @ Matrix.Rotation(math.radians(deg), 4, "X")
            @ Matrix.Translation((0, -cy, -cz)))


def link_matrix(alpha, theta):
    pa0, pb0 = K.pin_a(K.ALPHA0), K.pin_b(0.0)
    pa1, pb1 = K.pin_a(alpha), K.pin_b(theta)
    d = math.degrees(math.atan2(pb1[1] - pa1[1], pb1[0] - pa1[0]) - math.atan2(pb0[1] - pa0[1], pb0[0] - pa0[0]))
    return Matrix.Translation((0, pa1[0] - pa0[0], pa1[1] - pa0[1])) @ rot_x(d, pa0[0], pa0[1])


def pose(parts, theta, alpha=None, link_extra=None):
    """蓋角 θ の姿勢の可動部品（lid / crank / horn / link）を返す。"""
    if alpha is None:
        s = K.sweep(theta, max(8, int(theta / 2) + 2)) if theta > 0 else [(0.0, K.ALPHA0)]
        alpha = s[-1][1]
    out = dict(lid=parts["lid"].moved(rot_x(theta, HY, HZ)),
               crank=parts["crank"].moved(rot_x(alpha - K.ALPHA0, OY, OZ)),
               horn=parts["ref_horn"].moved(rot_x(alpha - K.ALPHA0, OY, OZ)))
    lm = link_matrix(alpha, theta)
    if link_extra is not None:
        lm = link_extra @ lm
    out["link"] = parts["link"].moved(lm)
    return out, alpha


def horn_orientation(parts):
    """非対称な参照ホーンを逆向きに付けた場合のクランク食い込みを調べる。"""
    crank = parts["crank"]
    horn = parts["ref_horn"]
    calibration_hit = contact(
        crank, horn.moved(Matrix.Translation((1.0, 0, 0))))
    calibration_miss = contact(
        crank, horn.moved(Matrix.Translation((100.0, 0, 0))))
    calibration_ok = (calibration_hit["depth"] > 0.3
                      and calibration_miss["hits"] == 0)

    correct_contact = contact(crank, horn)
    correct_ok = correct_contact["depth"] <= 0.02
    setup_theta = P.ASSEMBLY_LID_BACK_DEG
    setup_moving, setup_alpha = pose(parts, setup_theta)
    setup_contact = contact(setup_moving["crank"], setup_moving["horn"])
    reversed_horn = horn.moved(rot_x(180.0, OY, OZ))
    reversed_same_center_contact = contact(crank, reversed_horn)
    reversed_same_center_rejected = reversed_same_center_contact["depth"] > 0.1

    left_mm = abs(P.SG.HORN_LEFT_X * MM)
    right_mm = P.SG.HORN_RIGHT_X * MM
    length_difference = left_mm - right_mm
    signed_shift = (P.SG.HORN_LEFT_X + P.SG.HORN_RIGHT_X) * MM
    alpha = math.radians(K.ALPHA0)
    long_arm_direction = Vector((0, math.cos(alpha), math.sin(alpha)))
    displacement = long_arm_direction * signed_shift
    outline_aligned = reversed_horn.moved(Matrix.Translation(displacement))
    outline_aligned_contact = contact(crank, outline_aligned)
    outline_aligned_rejected = outline_aligned_contact["depth"] > 0.1

    overall_ok = (calibration_ok and correct_ok
                  and reversed_same_center_rejected and outline_aligned_rejected)
    return dict(
        left_mm=round(left_mm, 3),
        right_mm=round(right_mm, 3),
        length_difference_mm=round(length_difference, 3),
        calibration=dict(
            horn_plus_x_1mm=calibration_hit,
            horn_plus_x_100mm=calibration_miss,
            ok=calibration_ok,
        ),
        correct=dict(correct_contact, contact=correct_contact, ok=correct_ok),
        setup_angle=dict(bvh_contact=setup_contact,
                         theta_deg=round(setup_theta, 3), alpha_deg=round(setup_alpha, 3),
                         rigid_pair_transform=True, requires_boolean_exact=True,
                         note="クランクとホーンは同じ剛体変換。合否はboolean_report.horn_crank_setup_mm3で判定"),
        reversed_same_center=dict(
            reversed_same_center_contact,
            contact=reversed_same_center_contact,
            rejected=reversed_same_center_rejected,
        ),
        reversed_outline_aligned=dict(
            outline_aligned_contact,
            contact=outline_aligned_contact,
            shift_mm=round(signed_shift, 3),
            axis_displacement_mm=round(displacement.length, 3),
            rejected=outline_aligned_rejected,
        ),
        note="名目形状。実物の弾性と印刷誤差は未確認",
        ok=overall_ok,
        overall_ok=overall_ok,
    )


def print_horn_orientation(result):
    print("horn orientation", dict(
        calibration=result["calibration"]["ok"],
        correct_depth_mm=result["correct"]["depth"],
        setup_angle_deg=result["setup_angle"]["theta_deg"],
        setup_angle_bvh_depth_mm=result["setup_angle"]["bvh_contact"]["depth"],
        reversed_same_center_depth_mm=result["reversed_same_center"]["depth"],
        reversed_outline_aligned_depth_mm=result["reversed_outline_aligned"]["depth"],
        ok=result["overall_ok"],
    ), flush=True)


def calibration_box(name, lo, hi):
    """接触計器の校正に使う、閉じた直方体メッシュ。"""
    vertices = [Vector((x, y, z)) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    triangles = [(0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6),
                 (0, 1, 5), (0, 5, 4), (2, 6, 7), (2, 7, 3),
                 (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5)]
    return Mesh(vertices, triangles, name)


# ---------------------------------------------------------------------------
# 1. 計器の校正
# ---------------------------------------------------------------------------

def calibrate(parts):
    res = {}
    # 当たるはず: リンクを +X に 1mm（蓋の耳との隙間は 0.3mm）
    mv, _ = pose(parts, 0.0)
    shifted = mv["link"].moved(Matrix.Translation((1.0, 0, 0)))
    c_hit = contact(shifted, mv["lid"])
    res["must_hit_link_plus1mm_vs_lid"] = c_hit
    # 当たらないはず: クリップと蓋（遠い）
    res["must_not_hit_clip_vs_lid"] = contact(parts["clip"], mv["lid"])
    # 距離の校正: クランクの +X 面と受けの -X 面は設計 0.3mm
    res["clearance_crank_vs_box_design_0.3"] = clearance(mv["crank"], parts["box"], step=1)
    horizontal = calibration_box("horizontal_plate", (-5, -5, -0.5), (5, 5, 0.5))
    vertical = calibration_box("vertical_plate", (-0.5, -5, -5), (0.5, 5, 5))
    res["must_hit_crossed_thin_plates"] = contact(horizontal, vertical)
    res["must_not_hit_separated_thin_plates"] = contact(
        horizontal, vertical.moved(Matrix.Translation((20, 0, 0))))
    ok = (c_hit["hits"] > 0 and c_hit["depth"] > 0.3 and res["must_not_hit_clip_vs_lid"]["hits"] == 0
          and res["must_hit_crossed_thin_plates"]["hits"] > 0
          and res["must_hit_crossed_thin_plates"]["depth"] > 0.1
          and res["must_not_hit_separated_thin_plates"]["hits"] == 0
          and abs(res["clearance_crank_vs_box_design_0.3"] - 0.3) < 0.05)
    res["ok"] = ok
    return res


# ---------------------------------------------------------------------------
# 2. 動き（0〜65°）の干渉
# ---------------------------------------------------------------------------

STATIC = ("box", "pin", "clip", "ref_body", "ref_wire", "speaker_clip", "ref_speaker", "roof")
MOVING = ("lid", "crank", "link", "horn")
SKIP = {("crank", "horn"), ("horn", "crank"), ("horn", "ref_body"), ("horn", "ref_wire")}


def motion(parts, thetas):
    rows = []
    worst = {}
    for th in thetas:
        mv, alpha = pose(parts, th)
        row = dict(theta=round(th, 2), alpha=round(alpha, 2), hits=[])
        names = list(MOVING)
        for i, a in enumerate(names):
            for b in list(STATIC) + names[i + 1:]:
                if (a, b) in SKIP or (b, a) in SKIP:
                    continue
                mb = parts[b] if b in STATIC else mv[b]
                pairs = mv[a].bvh().overlap(mb.bvh())
                # 面が交差しない完全な内包も調べる。接触面上の点は除く。
                if not pairs:
                    contained = False
                    for ma, other in ((mv[a], mb), (mb, mv[a])):
                        tree = other.bvh()
                        for vi in (0, len(ma.v) // 2, len(ma.v) - 1):
                            point = ma.v[vi]
                            if other.contains(point, tree) and tree.find_nearest(point)[3] > 0.01:
                                contained = True
                                break
                    if contained:
                        row['hits'].append(dict(pair=f'{a}-{b}', contained=True))
                if pairs:
                    c = contact(mv[a], mb)
                    # 閉姿勢の蓋と箱は設計上の着座面。従来の0.02mm丸め許容を維持する。
                    if th == 0 and a == "lid" and b == "box" and c["depth"] < 0.02:
                        row.setdefault("contacts", []).append(
                            dict(pair=f"{a}-{b}", **c, note="閉姿勢の着座面"))
                        continue
                    # STL の三角形が同じ境界面を横切っても、食い込みが無ければ接触として分ける。
                    if c["depth"] <= 0.003:
                        row.setdefault("contacts", []).append(
                            dict(pair=f"{a}-{b}", **c, note="境界面の接触。食い込みなし"))
                        continue
                    row["hits"].append(dict(pair=f"{a}-{b}", **c))
        rows.append(row)
    return rows


def motion_clearances(parts, thetas):
    """可動部品と周りとの最小隙間（mm）を角度ごとに。"""
    out = {}
    pairs = [("lid", "box"), ("crank", "box"), ("crank", "ref_body"), ("link", "box"), ("link", "lid"),
             ("link", "crank"), ("crank", "lid"), ("horn", "box"), ("link", "ref_body"), ("lid", "clip"), ('lid','roof')]
    for a, b in pairs:
        out[f"{a}-{b}"] = []
    for th in thetas:
        mv, _ = pose(parts, th)
        for a, b in pairs:
            ma = mv[a] if a in mv else parts[a]
            mb = mv[b] if b in mv else parts[b]
            out[f"{a}-{b}"].append(clearance(ma, mb, step=2))
    return {k: dict(min=min(v), at_theta=thetas[v.index(min(v))]) for k, v in out.items()}


def free_open_limit(parts):
    """リンクを外した蓋だけで、何度まで箱に当たらず開くか（組み立て中に蓋を倒しておける角度）。"""
    last = 0.0
    for th in range(95, 200, 5):
        lid = parts["lid"].moved(rot_x(th, HY, HZ))
        if lid.bvh().overlap(parts["box"].bvh()) or lid.bvh().overlap(parts["pin"].bvh()):
            break
        last = th
    return last


# ---------------------------------------------------------------------------
# 3. 組み立ての経路
# ---------------------------------------------------------------------------

def path_check(moving, static, mats, skip=()):
    """moving（Mesh の dict）を mats の各行列で動かし、static と当たるか。"""
    worst = {}
    for t, m in mats:
        for kn, mm_ in moving.items():
            mvd = mm_.moved(m)
            for ks, st in static.items():
                if (kn, ks) in skip:
                    continue
                pairs = mvd.bvh().overlap(st.bvh())
                if pairs:
                    c = contact(mvd, st, step=1)
                    key = f"{kn}-{ks}"
                    if c["depth"] > worst.get(key, dict(depth=-1))["depth"]:
                        worst[key] = dict(depth=c["depth"], hits=c["hits"], at=round(t, 2))
    return worst


def bent_link(mesh, pa, pb, displacement):
    """A端を動かさない片持ち梁の近似。両端の丸い部分は曲げない。"""
    direction = Vector((0, pb[0] - pa[0], pb[1] - pa[1])).normalized()
    length = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
    root = P.LINK_A_BOSS_R * MM
    tip = P.LINK_B_BOSS_R * MM
    span = length - root - tip
    amplitude = displacement / (1 + 1.5 * tip / span)
    center_x = (P.SERVO_X0 + P.SG.HORN_TOP_Z + P.CRANK_TOP_T + P.AX_GAP + P.LINK_T / 2) * MM
    origin = Vector((center_x, pa[0], pa[1]))
    verts = []
    for vertex in mesh.v:
        s = (vertex - origin).dot(direction) - root
        q = min(1.0, max(0.0, s / span))
        offset = amplitude * (q * q * (3 - q) / 2 + max(0.0, s - span) * 1.5 / span)
        slope = amplitude * (3 * q - 1.5 * q * q) / span
        angle = math.atan(slope)
        cross = vertex.x - center_x
        position = vertex.copy() + direction * (cross * math.sin(angle))
        position.x = center_x + cross * math.cos(angle) - offset
        verts.append(position)
    return Mesh(verts, mesh.t, mesh.name)


def assembly(parts):
    res = {}
    setup_theta = P.ASSEMBLY_LID_BACK_DEG
    mv_setup, alpha_setup = pose(parts, setup_theta)
    lid_setup = mv_setup["lid"]
    pa_setup, pb_setup = K.pin_a(alpha_setup), K.pin_b(setup_theta)
    link_setup_deg = K.link_angle(setup_theta, alpha_setup)
    key_link_deg = setup_theta + P.B_KEY_DEG - 180.0
    link_at_b_key = mv_setup["link"].moved(
        rot_x(key_link_deg - link_setup_deg, pb_setup[0], pb_setup[1]))

    # B. 箱外で蓋の鍵溝へ B ピンを +X 方向に通す。
    insert_x = [-8.0 + i * 0.25 for i in range(33)]
    res["B_retainer_insert"] = dict(
        worst=path_check({"link": link_at_b_key}, {"lid": lid_setup},
                         [(x, Matrix.Translation((x, 0, 0))) for x in insert_x]),
        from_x_mm=-8.0, to_x_mm=0.0, key_link_deg=round(key_link_deg, 3))

    # 鍵角から組立姿勢へは、B の下側を通る円弧を選ぶ。両方向を actual STL で残す。
    forward = (link_setup_deg - key_link_deg) % 360.0
    deltas = (forward, forward - 360.0)
    turn_candidates = []
    for delta in deltas:
        count = max(1, int(math.ceil(abs(delta) / 2.5)))
        angles = [delta * i / count for i in range(count + 1)]
        worst = path_check({"link": link_at_b_key}, {"lid": lid_setup},
                           [(a, rot_x(a, pb_setup[0], pb_setup[1])) for a in angles])
        a_z = [pb_setup[1] - K.L_LINK * math.sin(math.radians(key_link_deg + a)) for a in angles]
        turn_candidates.append(dict(delta_deg=round(delta, 3), samples=len(angles), worst=worst,
                                    mean_a_z_mm=round(sum(a_z) / len(a_z), 3),
                                    max_a_z_mm=round(max(a_z), 3),
                                    clear=not any(v["depth"] > 0.003 for v in worst.values())))
    clear_turns = [row for row in turn_candidates if row["clear"]]
    chosen_turn = min(clear_turns, key=lambda row: row["mean_a_z_mm"]) if clear_turns else min(
        turn_candidates, key=lambda row: max((v["depth"] for v in row["worst"].values()), default=0.0))
    res["B_retainer_turn"] = dict(
        worst=chosen_turn["worst"], from_link_deg=round(key_link_deg, 3),
        to_link_deg=round(link_setup_deg, 3), chosen_delta_deg=chosen_turn["delta_deg"],
        route="underside", candidates=turn_candidates, ok=chosen_turn["clear"])

    # B の爪は、動作 0〜65°の131姿勢で、ピンが抜ける前に -X 引抜きを止める。
    pulls = [i * 0.25 for i in range(31)]
    operating = []
    for i in range(131):
        theta = i * K.THETA_OPEN / 130
        moving, alpha = pose(parts, theta)
        path = []
        for pull in pulls:
            c = contact(moving["link"].moved(Matrix.Translation((-pull, 0, 0))), moving["lid"])
            path.append(dict(pull_mm=pull, **c))
        first = next((row for row in path if row["hits"] > 0 and row["depth"] > 0.003), None)
        operating.append(dict(theta=round(theta, 3), alpha=round(alpha, 3),
                              first_contact_mm=None if first is None else first["pull_mm"],
                              first_contact_depth_mm=None if first is None else first["depth"],
                              max_depth_mm=max(row["depth"] for row in path), path=path))
    key_path = []
    for pull in pulls:
        c = contact(link_at_b_key.moved(Matrix.Translation((-pull, 0, 0))), lid_setup)
        key_path.append(dict(pull_mm=pull, **c))
    pin_exit = P.FIN_T * MM
    res["B_retainer_lock"] = dict(
        operating=operating, at_key_path=key_path, poses=len(operating), pull_max_mm=pulls[-1],
        pull_step_mm=0.25, pin_exit_mm=round(pin_exit, 3),
        first_contact_max_mm=max((row["first_contact_mm"] for row in operating
                                  if row["first_contact_mm"] is not None), default=None),
        calibration=dict(operating_hit=all(row["first_contact_mm"] is not None for row in operating),
                         key_withdrawal_clear=all(row["depth"] <= 0.003 for row in key_path)),
        ok=(all(row["first_contact_mm"] is not None and row["first_contact_mm"] < pin_exit
                and row["max_depth_mm"] > 0.003 for row in operating)
            and all(row["depth"] <= 0.003 for row in key_path)))

    # A の従来バヨネットも、動作姿勢での保持と鍵角での引抜きを残す。
    a_lock = []
    for theta in (0.0, K.THETA_OPEN / 2, K.THETA_OPEN):
        moving, alpha = pose(parts, theta)
        path = []
        for pull in pulls:
            c = contact(moving["link"].moved(Matrix.Translation((pull, 0, 0))), moving["crank"])
            path.append(dict(pull_mm=pull, **c))
        first = next((row for row in path if row["hits"] > 0 and row["depth"] > 0.003), None)
        a_lock.append(dict(theta=theta, rel=round(K.relative_link_crank(theta, alpha), 3),
                           first_contact_mm=None if first is None else first["pull_mm"], path=path))
    moving0, alpha0 = pose(parts, 0.0)
    pa0 = K.pin_a(alpha0)
    rel0 = K.relative_link_crank(0.0, alpha0)
    link_at_a_key = moving0["link"].moved(rot_x(P.BAYONET_KEY_DEG - rel0, pa0[0], pa0[1]))
    a_key_path = [dict(pull_mm=pull, **contact(
        link_at_a_key.moved(Matrix.Translation((pull, 0, 0))), moving0["crank"])) for pull in pulls]
    res["C3_bayonet_lock"] = dict(
        operating=a_lock, at_key_path=a_key_path,
        ok=all(row["first_contact_mm"] is not None and row["first_contact_mm"] < 2.0 for row in a_lock)
        and all(row["depth"] <= 0.003 for row in a_key_path))

    # C. B を保持した蓋とリンクへ自由クランクを A 鍵角で差し、クランクだけを組立姿勢へ回す。
    alpha_key = link_setup_deg - P.BAYONET_KEY_DEG
    crank_at_key = mv_setup["crank"].moved(
        rot_x(alpha_key - alpha_setup, pa_setup[0], pa_setup[1]))
    res["C_retainer_crank_insert"] = dict(
        worst=path_check({"crank": crank_at_key}, {"link": mv_setup["link"], "lid": lid_setup},
                         [(x, Matrix.Translation((x, 0, 0))) for x in insert_x]),
        from_x_mm=-8.0, to_x_mm=0.0, alpha_key_deg=round(alpha_key, 3))
    turn_count = max(1, int(math.ceil(abs(alpha_setup - alpha_key) / 2.5)))
    crank_turn = [alpha_key + (alpha_setup - alpha_key) * i / turn_count for i in range(turn_count + 1)]
    res["C_retainer_crank_turn"] = dict(
        worst=path_check({"crank": crank_at_key}, {"link": mv_setup["link"], "lid": lid_setup},
                         [(a, rot_x(a - alpha_key, pa_setup[0], pa_setup[1])) for a in crank_turn]),
        from_alpha_deg=round(alpha_key, 3), to_alpha_deg=round(alpha_setup, 3), samples=len(crank_turn))

    # 結合済みの蓋・リンク・クランクを、組立姿勢のホーンへ +X 側からかぶせる。
    assembly95 = {"lid": lid_setup, "link": mv_setup["link"], "crank": mv_setup["crank"]}
    onto_horn_x = [8.0 - i * 0.25 for i in range(33)]
    res["C_retainer_horn_insert"] = dict(
        worst=path_check(assembly95, {"horn": mv_setup["horn"], "body": parts["ref_body"]},
                         [(x, Matrix.Translation((x, 0, 0))) for x in onto_horn_x]),
        from_x_mm=8.0, to_x_mm=0.0,
        intended_contact="crank-horn at x=0 is gated by Boolean EXACT; every other pair remains a BVH gate")

    # D. 組立角の蓋を含むサーボ一式を上から箱へ下ろす。
    sub = dict(body=parts["ref_body"], wire=parts["ref_wire"], horn=mv_setup["horn"],
               crank=mv_setup["crank"], link=mv_setup["link"], lid=lid_setup)
    mats = [(t, Matrix.Translation((0, 0, t))) for t in [70 - i * 1.0 for i in range(70)] + [0.3, 0.1, 0.0]]
    lower_contacts = path_check(sub, {"box": parts["box"], "speaker_clip": parts["speaker_clip"],
                                      "speaker": parts["ref_speaker"]}, mats)
    res["D_servo_unit_lower"] = dict(
        worst={key: value for key, value in lower_contacts.items() if value["depth"] > 0.003},
        contacts={key: dict(value, note="基準面の摺動接触")
                  for key, value in lower_contacts.items() if value["depth"] <= 0.003},
        lid_deg=round(setup_theta, 3), crank_alpha=round(alpha_setup, 3), travel_mm=70,
        note="蓋・リンク・クランク・ホーン・サーボ本体・配線を一式で下降。配線は8mmの固い棒で近似")

    # E. 押さえクリップを上から押し込み、蝶番ピンを右側面から差す。
    sub_final = dict(body=parts["ref_body"], wire=parts["ref_wire"], crank=mv_setup["crank"],
                     horn=mv_setup["horn"], link=mv_setup["link"], lid=lid_setup)
    mats = [(t, Matrix.Translation((0, 0, t))) for t in [25 - i * 0.25 for i in range(101)]]
    res["E_clip_press"] = dict(worst=path_check({"clip": parts["clip"]}, dict(box=parts["box"], **sub_final), mats),
                               note="爪が台の角を乗り越えるときの食い込み＝脚のたわみ量")
    pin_mats = [(t, Matrix.Translation((t, 0, 0))) for t in [78 - i * 1.0 for i in range(79)]]
    res["E_hinge_pin_insert"] = dict(
        worst=path_check({"pin": parts["pin"]}, {"box": parts["box"], "lid": lid_setup}, pin_mats),
        note=f"蓋は{setup_theta:.0f}°。先端5.3mmと左の貫通穴5.2mmの片側0.05mmだけを圧入する")

    # F. 保持済み一式を組立角から32.5°まで運動学どおりに下ろす。
    target_theta = K.THETA_OPEN / 2
    lower_thetas = [setup_theta - i * 0.5 for i in range(int((setup_theta - target_theta) / 0.5) + 1)]
    if lower_thetas[-1] != target_theta:
        lower_thetas.append(target_theta)
    lower_rows = motion(parts, lower_thetas)
    res["F_retained_lid_lower"] = dict(
        from_theta_deg=round(setup_theta, 3), to_theta_deg=round(target_theta, 3),
        samples=len(lower_rows), rows=lower_rows,
        hits=[dict(theta=row["theta"], hits=row["hits"]) for row in lower_rows if row["hits"]],
        ok=not any(row["hits"] for row in lower_rows))

    mv_mid, alpha_mid = pose(parts, target_theta)
    lid_mid = mv_mid["lid"]
    clip_span = OZ + P.SG.BODY_W * MM / 2 + P.CLIP_TOP_GAP * MM - (P.HOOK_Z + P.HOOK_H) * MM
    clip_deflection = res["E_clip_press"]["worst"]["clip-box"]["depth"]
    res['clip_snap_deflection_mm'] = clip_deflection
    res['clip_snap_strain_pct'] = round(100 * 1.5 * P.CLIP_LEG_T * MM * clip_deflection / clip_span ** 2, 2)
    res['hinge_tip_strain_pct'] = round(100 * 1.5 * (P.HINGE_TIP_D - P.HINGE_SPLIT_W) * MM / 2 * 0.05 / (P.HINGE_SPLIT_L * MM) ** 2, 2)
    # H. エキサイターと保持具の上入れ。爪と押し当て以外の食い込みを区別する。
    up = [(t, Matrix.Translation((0, 0, t))) for t in [45 - i * 0.5 for i in range(91)]]
    res['H_speaker_lower'] = dict(worst=path_check({'speaker': parts['ref_speaker']}, {'box': parts['box']}, up))
    res['H_speaker_clip_press'] = dict(worst=path_check({'speaker_clip': parts['speaker_clip']},
        {'box': parts['box'], 'speaker': parts['ref_speaker']}, up))
    res['H_speaker_clip_final'] = contact(parts['speaker_clip'], parts['box'])
    cap_span = P.EXCITER_D * MM - 3.0
    res['H_speaker_clip_strain_pct'] = round(100 * 1.5 * 3.8 * 0.3 / cap_span ** 2, 2)
    res['H_speaker_clip_preload_mm'] = round(P.EXCITER_PRELOAD * MM, 3)
    res['H_speaker_clip_pull_lock'] = contact(parts['speaker_clip'].moved(Matrix.Translation((0, 0, 1))), parts['box'])
    # 取り外しは挿入の逆経路。押し出したピンの右端が側面から2mm出る位置を確認する。
    res['I_pin_push_out'] = dict(worst=path_check({'pin': parts['pin']}, {'box': parts['box'], 'lid': lid_setup},
        [(t, Matrix.Translation((t, 0, 0))) for t in (0, 0.5, 1, 2, 3)]),
        right_tip_protrusion_mm=round(parts['pin'].bounds()[1][0] + 3 - P.CUBE * MM / 2, 2))
    # J. 固定天面を最後に載せる。蓋は中央の32.5°。スナップ以外の衝突を区別する。
    final_static = dict(parts)
    final_static.update(lid=lid_mid, crank=mv_mid['crank'], link=mv_mid['link'], ref_horn=mv_mid['horn'])
    final_static.pop('roof')
    roof_path = [(t, Matrix.Translation((0,0,t))) for t in [45-i*.5 for i in range(91)]]
    res['J_roof_lower'] = dict(worst=path_check({'roof': parts['roof']}, final_static, roof_path),
        travel_mm=45, note='壁の内側へ0.8mm掛かる爪だけを曲げる。固定天面は蝶番の荷重を受けない')
    root_z = P.CUBE*MM-P.LID_T*MM
    rigid_top = max((P.ROOF_LEG_BOTTOM+P.ROOF_HOOK_H)*MM, P.ROOF_RELEASE_TOP_Z*MM)
    flex_length = root_z-rigid_top
    hook_lever = rigid_top-(P.ROOF_LEG_BOTTOM+P.ROOF_HOOK_H-P.ROOF_HOOK)*MM
    res['J_roof_press_strain_pct'] = round(100*1.5*P.ROOF_LEG_T*MM*P.ROOF_PRESS_DELTA*MM/flex_length**2, 2)
    res['J_roof_free_span_mm'] = round(flex_length,3)
    res['J_roof_final'] = {name: contact(parts['roof'], other) for name,other in final_static.items()
                           if parts['roof'].bvh().overlap(other.bvh())}
    # 解除では脚の根元を動かさず、左右の爪を内へ曲げる。
    verts=[]
    for v in parts['roof'].v:
        point=v.copy()
        if v.z < root_z and P.ROOF_LEG_Y0*MM-.01 <= v.y <= P.ROOF_LEG_Y1*MM+.01:
            s=max(0,min(1,(root_z-v.z)/flex_length))
            beyond=max(0,(root_z-v.z)-flex_length)
            delta=P.ROOF_PRESS_DELTA*MM/(1+1.5*hook_lever/flex_length)
            offset=delta*(s*s*(3-s)/2 + beyond*1.5/flex_length)
            point.x -= math.copysign(offset,v.x)
        verts.append(point)
    pressed=Mesh(verts,parts['roof'].t,'roof_pressed')
    hook_points=[p for p,v in zip(verts,parts['roof'].v) if abs(v.x) > 32.7
        and v.z < (P.ROOF_LEG_BOTTOM+P.ROOF_HOOK_H)*MM+.01
        and P.ROOF_LEG_Y0*MM-.01 <= v.y <= P.ROOF_LEG_Y1*MM+.01]
    hook_edge=max(abs(p.x) for p in hook_points)
    res['J_roof_release']=dict(worst=path_check({'roof':pressed},final_static,
        [(t,Matrix.Translation((0,0,t))) for t in [i*.25 for i in range(25)] + [8,12,20,30,45]]),
        delta_mm=round(P.ROOF_PRESS_DELTA*MM,2), travel_mm=45,
        released_hook_max_abs_x_mm=round(hook_edge,3), wall_clearance_mm=round(32-hook_edge,3))
    res['J_roof_release']['blocking']={name:value for name,value in res['J_roof_release']['worst'].items() if value['depth']>.001}
    # 同じ嵌合面を切り出した試験片にも、爪以外の食い込みがない。
    coupon_body=Mesh.load(os.path.join(BUILD,'roof_test_body.stl'),'roof_test_body')
    coupon_roof=Mesh.load(os.path.join(BUILD,'roof_test.stl'),'roof_test')
    res['J_roof_coupon_final']=contact(coupon_body,coupon_roof)
    # 指先の丸い包絡(直径10mm)。正面の開口から両脚へ入る経路。握り力は実物未検証。
    finger_checks={}
    for side in (-1,1):
        samples=[]
        for yy in [20-i*.5 for i in range(82)]:
            center=Vector((side*24.5,yy,45))
            for name,other in final_static.items():
                near=other.bvh().find_nearest(center)
                if other.contains(center) or (near[0] is not None and near[3] < 5-.001):
                    samples.append(dict(y_mm=yy,part=name,distance_mm=round(near[3],3)))
        finger_checks[str(side)]=samples
    res['J_finger_approach']=dict(diameter_mm=10,centers_xz_mm=[[-24.5,45],[24.5,45]],
        y_start_mm=20,y_end_mm=-20.5, obstacles=finger_checks, physical_grip_tested=False)
    finger_press={}
    for side in (-1,1):
        samples=[]
        for i in range(13):
            center=Vector((side*(24.5-P.ROOF_PRESS_DELTA*MM*i/12),-20.5,45))
            for name,other in final_static.items():
                near=other.bvh().find_nearest(center)
                if other.contains(center) or (near[0] is not None and near[3] < 5-.001):
                    samples.append(dict(step=i,part=name,distance_mm=round(near[3],3)))
        finger_press[str(side)]=samples
    res['J_finger_press']=dict(delta_mm=round(P.ROOF_PRESS_DELTA*MM,2),obstacles=finger_press,
        direction='左右の解除つまみを箱の中央へ押す')
    return res


# ---------------------------------------------------------------------------
# 4. 刷る姿勢の宙に浮く面
# ---------------------------------------------------------------------------

def overhang_report(m, layer=0.2, limit_deg=45.0):
    """45° より寝た下向き面を塊に分け、塊ごとに「外側のすぐ下に肉があるか」で支えを判定。"""
    bvh = m.bvh()
    cos_lim = -math.cos(math.radians(limit_deg))
    faces = []
    for i, (a, b, c) in enumerate(m.t):
        p, q, r = m.v[a], m.v[b], m.v[c]
        n = (q - p).cross(r - p)
        area = n.length / 2
        if area < 1e-9:
            continue
        n.normalize()
        zc = (p.z + q.z + r.z) / 3
        if n.z < cos_lim and zc > layer * 1.25:
            faces.append(i)
    # 頂点共有で塊に
    parent = {f: f for f in faces}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    by_vert = {}
    for f in faces:
        for vi in m.t[f]:
            by_vert.setdefault(vi, []).append(f)
    for lst in by_vert.values():
        for f in lst[1:]:
            parent[find(f)] = find(lst[0])
    groups = {}
    for f in faces:
        groups.setdefault(find(f), []).append(f)
    out = []
    for g in groups.values():
        area = 0.0
        zs, pts = [], []
        horiz = True
        for f in g:
            a, b, c = (m.v[i] for i in m.t[f])
            n = (b - a).cross(c - a)
            area += n.length / 2
            nn = n.normalized()
            horiz = horiz and nn.z < -0.985
            zs += [a.z, b.z, c.z]
            pts.append((a + b + c) / 3)
        # 支えの判定: 塊の外周の辺の中点を、面内で外へ 0.4mm、下へ 0.5 層ずらした点が肉の中か
        edge_count = {}
        for f in g:
            t = m.t[f]
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                k = tuple(sorted(e))
                edge_count[k] = edge_count.get(k, 0) + 1
        boundary = [e for e, n in edge_count.items() if n == 1]
        cen = sum(pts, Vector()) / len(pts)
        sup = tot = 0
        for e in boundary:
            mid = (m.v[e[0]] + m.v[e[1]]) / 2
            d = Vector((mid.x - cen.x, mid.y - cen.y, 0))
            if d.length < 1e-6:
                continue
            d.normalize()
            probe = mid + d * 0.4 - Vector((0, 0, layer * 0.5))
            tot += 1
            if inside(bvh, probe):
                sup += 1
        lo = [min(p[i] for p in pts) for i in range(3)]
        hi = [max(p[i] for p in pts) for i in range(3)]
        span = max(hi[0] - lo[0], hi[1] - lo[1])
        out.append(dict(area_mm2=round(area, 2), z=[round(min(zs), 2), round(max(zs), 2)],
                        bbox=[[round(x, 1) for x in lo], [round(x, 1) for x in hi]],
                        horizontal=horiz, supported_edge_ratio=round(sup / tot, 2) if tot else 0.0,
                        span_mm=round(span, 2)))
    out.sort(key=lambda d: -d["area_mm2"])
    return out


def calib_overhang():
    """浮いた板（必ず検出）と横穴の天井（橋渡しで支えあり）で計器を確かめる。"""
    def boxm(x0, x1, y0, y1, z0, z1):
        v = [Vector((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
        t = [(0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6), (0, 1, 5), (0, 5, 4), (2, 6, 7), (2, 7, 3),
             (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5)]
        return v, t
    # 浮いた板: 土台の上 10mm に板（土台とは別の塊）
    v1, t1 = boxm(0, 20, 0, 20, 0, 2)
    v2, t2 = boxm(0, 20, 0, 20, 10, 12)
    floating = Mesh(v1 + v2, t1 + [(a + 8, b + 8, c + 8) for a, b, c in t2], "floating")
    # 橋: 左右の柱に渡した梁（Π 形の 1 つの閉じたメッシュ。下面は両端で柱に支えられる）
    poly = [(0, 0), (4, 0), (4, 10), (16, 10), (16, 0), (20, 0), (20, 12), (0, 12)]
    tri = [(0, 1, 2), (0, 2, 7), (2, 3, 6), (2, 6, 7), (3, 4, 5), (3, 5, 6)]   # 手で分けた凸片
    v = [Vector((x, 0, z)) for x, z in poly] + [Vector((x, 10, z)) for x, z in poly]
    t = [(a, b, c) for a, b, c in tri] + [(c + 8, b + 8, a + 8) for a, b, c in tri]
    for i in range(8):
        j = (i + 1) % 8
        t += [(i, i + 8, j + 8), (i, j + 8, j)]
    bridge = Mesh(v, t, "bridge")
    fl = overhang_report(floating)
    br = overhang_report(bridge)
    return dict(floating_plate=fl[:1], bridge=br[:1],
                ok=bool(fl) and fl[0]["supported_edge_ratio"] < 0.2 and bool(br) and br[0]["supported_edge_ratio"] > 0.2)


# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    if "--horn-orientation-only" in sys.argv:
        parts = {name: Mesh.load(os.path.join(BUILD, f"{name}.stl"), name)
                 for name in ("crank", "ref_horn")}
        result = horn_orientation(parts)
        with open(os.path.join(BUILD, "horn_orientation_report.json"), "w",
                  encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1)
        print_horn_orientation(result)
        if not result["overall_ok"]:
            raise RuntimeError("ホーン逆向き装着の検査に失敗しました")
        return

    names = ["box", "lid", "crank", "link", "pin", "clip", "speaker_clip", "ref_speaker", "ref_body", "ref_horn", "ref_wire", "roof"]
    parts = {n: Mesh.load(os.path.join(BUILD, f"{n}.stl"), n) for n in names}
    servo_coupon = Mesh.load(os.path.join(BUILD, "servo_fit_test.stl"), "servo_fit_test")
    report = {}
    report["calibration"] = calibrate(parts)
    report["calibration"]["flat_plane"] = calibrate_flat_plane()
    report["calibration"]["ok"] = (report["calibration"]["ok"]
                                      and report["calibration"]["flat_plane"]["ok"])
    print("calibration", report["calibration"], flush=True)
    report["horn_orientation"] = horn_orientation(parts)
    print_horn_orientation(report["horn_orientation"])
    if not report["horn_orientation"]["overall_ok"]:
        raise RuntimeError("ホーン逆向き装着の検査に失敗しました")
    report["servo_fit"] = servo_fit(parts, servo_coupon)
    report["servo_fit"]["instrument_calibration_ok"] = report["calibration"]["ok"]
    report["servo_fit"]["ok"] = (report["servo_fit"]["ok"]
                                  and report["servo_fit"]["instrument_calibration_ok"])
    print("servo fit", json.dumps(report["servo_fit"], ensure_ascii=False), flush=True)
    motion_max = max(K.THETA_OPEN, P.ASSEMBLY_LID_BACK_DEG)
    thetas = [i * .5 for i in range(int(motion_max / .5) + 1)]
    report["motion"] = motion(parts, thetas)
    report["motion_summary"] = dict(
        steps=len(thetas), theta_max=thetas[-1], nominal_theta_max=K.THETA_OPEN,
        poses_with_hits=[r["theta"] for r in report["motion"] if r["hits"]],
        contacts=[c for r in report["motion"] for c in r.get("contacts", [])])
    print("motion", report["motion_summary"], flush=True)
    report["motion_clearance_mm"] = motion_clearances(parts, thetas)
    print("clearance", report["motion_clearance_mm"], flush=True)
    report["lid_free_open_limit_deg"] = free_open_limit(parts)
    report["static_closed"] = {}
    report["static_contacts"] = {}
    mv, _ = pose(parts, 0.0)
    allp = dict(parts)
    allp.update(dict(lid=mv["lid"], crank=mv["crank"], link=mv["link"]))
    keys = ["box", "lid", "crank", "link", "pin", "clip", "speaker_clip", "ref_speaker", "ref_body", "ref_wire", "roof"]
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if {a, b} in ({"ref_body", "ref_wire"},):
                continue
            c = contact(allp[a], allp[b], depth=False)
            if c["hits"]:
                detail = contact(allp[a], allp[b])
                if detail["depth"] <= 0.003:
                    report["static_contacts"][f"{a}-{b}"] = dict(
                        detail, note="基準面または着座面の接触。食い込みなし")
                else:
                    report["static_closed"][f"{a}-{b}"] = detail
    print("static", report["static_closed"])
    print("static contacts", report["static_contacts"])
    report["assembly"] = assembly(parts)
    print("assembly", json.dumps(report["assembly"], ensure_ascii=False)[:3000])
    # 質量特性（中実 PLA）
    rho = P.PLA_DENSITY / 1e9  # kg/mm3
    mp = {}
    for n in ("lid", "crank", "link", "box", "clip", "pin", "speaker_clip", "roof"):
        m = parts[n].mass_props()
        mp[n] = dict(volume_mm3=round(m["volume"], 1), mass_g=round(m["volume"] * rho * 1000, 2),
                     com_mm=[round(x, 2) for x in m["com"]], ixx_com_mm5=m["ixx_com"])
    report["mass"] = mp
    # 刷る姿勢
    report["overhang_calibration"] = calib_overhang()
    print("overhang calib", report["overhang_calibration"])
    report["overhang"] = {}
    for n in ("box", "lid", "crank", "link", "pin", "clip", "speaker_clip", "roof"):
        m = Mesh.load(os.path.join(BUILD, f"print_{n}.stl"), n)
        report["overhang"][n] = overhang_report(m)
    report["overhang"]["servo_fit_test"] = overhang_report(
        Mesh.load(os.path.join(BUILD, "print_servo_fit_test.stl"), "servo_fit_test"))
    report["overhang"]["joint_b_test"] = overhang_report(
        Mesh.load(os.path.join(BUILD, "print_joint_b_test.stl"), "joint_b_test"))
    for n, g in report["overhang"].items():
        print("overhang", n, len(g))
        for x in g[:12]:
            print("   ", x["area_mm2"], x["z"], x["supported_edge_ratio"], "H" if x["horizontal"] else "S",
                  x["span_mm"], x["bbox"])
    print("free open limit", report["lid_free_open_limit_deg"])
    report["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(BUILD, "verify_report.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("done", report["elapsed_s"])


if __name__ == '__main__':
    main()
