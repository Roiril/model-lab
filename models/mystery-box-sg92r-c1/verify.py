"""動き・組み立て・印刷の検証（Blender の Python で走らせる。bpy の部品は使わず STL を直に読む）。

    "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python models/mystery-box-sg92r-c1/verify.py

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
    # 交差する面の頂点を調べる。箱の全頂点を毎工程で光線判定する必要はない。
    candidates = [set(), set()]
    for ia, ib in pairs:
        candidates[0].update(a.t[ia])
        candidates[1].update(b.t[ib])
    for index, (mesh, other, tree) in enumerate(((a, b, bb), (b, a, ba))):
        ids = sorted(candidates[index]) if pairs else range(0, len(mesh.v), step)
        for vi in ids:
            v = mesh.v[vi]
            if other.contains(v, tree):
                nearest = tree.find_nearest(v)
                if nearest[0] is not None:
                    maximum = max(maximum, nearest[3])
    return dict(hits=len(pairs), depth=round(maximum, 3))

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
    ok = (c_hit["hits"] > 0 and c_hit["depth"] > 0.3 and res["must_not_hit_clip_vs_lid"]["hits"] == 0
          and abs(res["clearance_crank_vs_box_design_0.3"] - 0.3) < 0.05)
    res["ok"] = ok
    return res


# ---------------------------------------------------------------------------
# 2. 動き（0〜65°）の干渉
# ---------------------------------------------------------------------------

STATIC = ("box", "pin", "clip", "ref_body", "ref_wire", "speaker_clip", "ref_speaker")
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
                    # θ=0 で蓋が箱の縁に載っているのは設計どおりの接触
                    if th == 0 and {a, b} == {"lid", "box"}:
                        c = contact(mv[a], mb)
                        if c["depth"] < 0.02:
                            row.setdefault("contacts", []).append(f"{a}-{b} 面で接触（深さ {c['depth']}）")
                            continue
                    c = contact(mv[a], mb)
                    row["hits"].append(dict(pair=f"{a}-{b}", **c))
        rows.append(row)
    return rows


def motion_clearances(parts, thetas):
    """可動部品と周りとの最小隙間（mm）を角度ごとに。"""
    out = {}
    pairs = [("lid", "box"), ("crank", "box"), ("crank", "ref_body"), ("link", "box"), ("link", "lid"),
             ("link", "crank"), ("crank", "lid"), ("horn", "box"), ("link", "ref_body"), ("lid", "clip")]
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
    lid0 = parts["lid"].moved(rot_x(P.ASSEMBLY_LID_BACK_DEG, HY, HZ))
    # A. 蝶番ピンを右側面から差す（蓋は閉じた位置）
    mats = [(t, Matrix.Translation((t, 0, 0))) for t in [78 - i * 1.0 for i in range(79)]]
    res["A_hinge_pin_insert"] = dict(
        worst=path_check({"pin": parts["pin"]}, {"box": parts["box"], "lid": lid0}, mats),
        note="蓋は125°。先端5.3mmと左の貫通穴5.2mmの片側0.05mmだけを圧入する")

    # B. ホーンを付けたサーボに、クランクを +X 側から押し込む（箱の外）
    mats = [(t, Matrix.Translation((t, 0, 0))) for t in [8 - i * 0.25 for i in range(32)] + [0.02]]
    res["B_crank_onto_horn"] = dict(worst=path_check({"crank": parts["crank"]},
                                                     {"horn": parts["ref_horn"], "body": parts["ref_body"]}, mats))

    # C. リンクをピン A に（鍵溝の角度で差し、回して止める）
    a0 = K.ALPHA0
    rel0 = K.relative_link_crank(0.0, a0)
    key = P.BAYONET_KEY_DEG
    pa = K.pin_a(a0)
    to_key = rot_x(key - rel0, pa[0], pa[1])
    mats = [(t, Matrix.Translation((t, 0, 0)) @ to_key) for t in [8 - i * 0.25 for i in range(33)]]
    res["C1_link_push_at_key"] = dict(worst=path_check({"link": parts["link"]}, {"crank": parts["crank"]}, mats))
    mats = [(ang, rot_x(ang - rel0, pa[0], pa[1])) for ang in [key - i * 5.0 for i in range(int((key - rel0) / 5) + 1)] + [rel0]]
    res["C2_link_turn_to_operating"] = dict(worst=path_check({"link": parts["link"]}, {"crank": parts["crank"]}, mats),
                                            from_deg=key, to_deg=round(rel0, 1))
    # 爪には45度の斜面がある。引く距離を連続に調べ、抜ける前に爪へ当たることを確認する。
    lock = []
    for th in (0.0, K.THETA_OPEN / 2, K.THETA_OPEN):
        s = K.sweep(th, 40) if th > 0 else [(0.0, a0)]
        al = s[-1][1]
        rel = K.relative_link_crank(th, al)
        rotation = rot_x(rel - rel0, pa[0], pa[1])
        path = []
        for pull in [i * 0.25 for i in range(31)]:
            c = contact(parts["link"].moved(Matrix.Translation((pull, 0, 0)) @ rotation), parts["crank"])
            path.append(dict(pull_mm=pull, **c))
        at2 = next(r for r in path if r['pull_mm'] == 2.0)
        first = next((r['pull_mm'] for r in path if r['hits'] > 0), None)
        lock.append(dict(theta=th, rel=round(rel, 1), pulled_2mm_hits=at2['hits'], depth=at2['depth'],
                         first_contact_mm=first, path=path))
    key_path = []
    for pull in [i * 0.25 for i in range(31)]:
        c = contact(parts['link'].moved(Matrix.Translation((pull, 0, 0)) @ to_key), parts['crank'])
        key_path.append(dict(pull_mm=pull, **c))
    res['C3_bayonet_lock'] = dict(operating=lock, pull_check_mm=2.0, at_key_path=key_path,
                                 ok=all(r['first_contact_mm'] is not None and r['first_contact_mm'] < 2 for r in lock)
                                 and all(r['hits'] == 0 for r in key_path))

    # D. サーボ一式（本体・配線・ホーン・クランク・リンク）を上から箱へ下ろす。蓋は開けて倒しておく
    th_mid = K.THETA_OPEN / 2
    mv, alpha_mid = pose(parts, th_mid)
    back = P.ASSEMBLY_LID_BACK_DEG
    lid_back = parts["lid"].moved(rot_x(back, HY, HZ))
    sub = dict(body=parts["ref_body"], wire=parts["ref_wire"], horn=mv["horn"], crank=mv["crank"],
               link=mv["link"])
    mats = [(t, Matrix.Translation((0, 0, t))) for t in [70 - i * 1.0 for i in range(70)] + [0.3, 0.1, 0.0]]
    res["D_servo_unit_lower"] = dict(
        worst=path_check(sub, {"box": parts["box"],
                              "speaker_clip": parts["speaker_clip"], "speaker": parts["ref_speaker"]}, mats),
        crank_alpha=round(alpha_mid, 1),
        note="サーボを 90° にしてホーンを付けた状態（クランクは動作範囲の中央）。配線は 8mm の固い棒で近似")

    # E. 押さえクリップを上から押し込む
    sub_final = dict(body=parts["ref_body"], wire=parts["ref_wire"], crank=mv["crank"], horn=mv["horn"])
    mats = [(t, Matrix.Translation((0, 0, t))) for t in [25 - i * 0.25 for i in range(101)]]
    res["E_clip_press"] = dict(worst=path_check({"clip": parts["clip"]}, dict(box=parts["box"], **sub_final), mats),
                               note="爪が台の角を乗り越えるときの食い込み＝脚のたわみ量")
    # C1ではサーボを先に入れ、125°の蓋を後から上入れする。
    mats_lid = [(t, Matrix.Translation((0, 0, t))) for t in [40 - i * 0.5 for i in range(81)]]
    res["G_lid_place_after_servo"] = dict(worst=path_check({"lid": lid_back},
        dict(box=parts["box"], clip=parts["clip"], link=mv["link"],
             speaker=parts["ref_speaker"], speaker_clip=parts["speaker_clip"], **sub_final), mats_lid))

    # F. 蓋を下ろしながら、リンクの B 端を -X に逃がしておき、合ったところで離して耳の穴に入れる
    pb = K.pin_b(th_mid)
    pa_m = K.pin_a(alpha_mid)
    ax = Vector((0, pb[0] - pa_m[0], pb[1] - pa_m[1])).normalized()
    perp = Vector((0, -ax.z, ax.y))  # リンクに直角（YZ 面内）
    lab = math.hypot(pb[0] - pa_m[0], pb[1] - pa_m[1])
    defl = P.FIN_T * MM + 0.4
    ang = math.degrees(math.atan(defl / lab))
    bend = Matrix.Translation((0, pa_m[0], pa_m[1])) @ Matrix.Rotation(math.radians(ang), 4, perp) \
        @ Matrix.Translation((0, -pa_m[0], -pa_m[1]))
    # 向きの確認（B 端が -X に動くこと）
    probe = bend @ Vector((0, pb[0], pb[1]))
    if probe.x > 0:
        bend = Matrix.Translation((0, pa_m[0], pa_m[1])) @ Matrix.Rotation(math.radians(-ang), 4, perp) \
            @ Matrix.Translation((0, -pa_m[0], -pa_m[1]))
    link_bent = bent_link(mv['link'], pa_m, pb, defl)
    hits = {}
    for th in [back - i * 2.5 for i in range(int((back - th_mid) / 2.5) + 1)] + [th_mid]:
        lid = parts["lid"].moved(rot_x(th, HY, HZ))
        c = lid.bvh().overlap(link_bent.bvh())
        if c:
            hits[str(round(th, 1))] = contact(lid, link_bent)
    res["F_lid_down_with_link_bent"] = dict(hits=hits, bend_deg=round(ang, 2), b_end_shift_mm=round(defl, 2))
    res['F_bent_link_fixed_parts'] = {}
    for name in ('box', 'crank', 'horn', 'ref_body', 'ref_wire'):
        other = mv[name] if name in mv else parts[name]
        c = contact(link_bent, other, depth=False)
        if c['hits']:
            res['F_bent_link_fixed_parts'][name] = contact(link_bent, other)
    # 離す: たわみを戻す途中で耳と当たらないか（最後は穴に入る）
    rel_hits = {}
    lid_mid = parts["lid"].moved(rot_x(th_mid, HY, HZ))
    for k in range(11):
        f = k / 10
        bm = Matrix.Translation((0, pa_m[0], pa_m[1])) @ Matrix.Rotation(math.radians(math.copysign(ang, 1) * (1 - f) * (1 if probe.x <= 0 else -1)), 4, perp) \
            @ Matrix.Translation((0, -pa_m[0], -pa_m[1]))
        c = contact(lid_mid, bent_link(mv['link'], pa_m, pb, defl * (1 - f)))
        if c["hits"]:
            rel_hits[str(f)] = c
    res["F_release_into_fin"] = dict(hits=rel_hits,
                                     note="途中で当たるのはピン B の面取りが耳の穴の縁に乗る区間。最後（1.0）が 0 なら入る")
    # リンクのたわみのひずみ（片持ち、A を根元）
    t_link = P.LINK_T * MM
    free_span = lab - (P.LINK_A_BOSS_R + P.LINK_B_BOSS_R) * MM
    strain = 1.5 * t_link * defl / free_span ** 2
    res["F_link_bend_strain_pct"] = round(strain * 100, 2)
    res['F_link_free_span_mm'] = round(free_span, 3)
    res['F_link_bend_method'] = 'A端を拘束。両端の丸を除く27.75mmを曲げられる長さとした保守的な近似。材料試験や有限要素解析は未実施'
    clip_span = OZ + P.SG.BODY_W * MM / 2 + P.CLIP_TOP_GAP * MM - (P.HOOK_Z + P.HOOK_H) * MM
    res['clip_snap_strain_pct'] = round(100 * 1.5 * P.CLIP_LEG_T * MM * 0.9 / clip_span ** 2, 2)
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
    res['I_pin_push_out'] = dict(worst=path_check({'pin': parts['pin']}, {'box': parts['box'], 'lid': lid_back},
        [(t, Matrix.Translation((t, 0, 0))) for t in (0, 0.5, 1, 2, 3)]),
        right_tip_protrusion_mm=round(parts['pin'].bounds()[1][0] + 3 - P.CUBE * MM / 2, 2))
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
    names = ["box", "lid", "crank", "link", "pin", "clip", "speaker_clip", "ref_speaker", "ref_body", "ref_horn", "ref_wire"]
    parts = {n: Mesh.load(os.path.join(BUILD, f"{n}.stl"), n) for n in names}
    report = {}
    report["calibration"] = calibrate(parts)
    print("calibration", report["calibration"], flush=True)
    thetas = [i * 2.5 for i in range(int(K.THETA_OPEN / 2.5) + 1)]
    report["motion"] = motion(parts, thetas)
    report["motion_summary"] = dict(
        steps=len(thetas), theta_max=thetas[-1],
        poses_with_hits=[r["theta"] for r in report["motion"] if r["hits"]],
        contacts=[c for r in report["motion"] for c in r.get("contacts", [])])
    print("motion", report["motion_summary"], flush=True)
    report["motion_clearance_mm"] = motion_clearances(parts, thetas)
    print("clearance", report["motion_clearance_mm"], flush=True)
    report["lid_free_open_limit_deg"] = free_open_limit(parts)
    report["static_closed"] = {}
    mv, _ = pose(parts, 0.0)
    allp = dict(parts)
    allp.update(dict(lid=mv["lid"], crank=mv["crank"], link=mv["link"]))
    keys = ["box", "lid", "crank", "link", "pin", "clip", "speaker_clip", "ref_speaker", "ref_body", "ref_wire"]
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if {a, b} in ({"ref_body", "ref_wire"},):
                continue
            c = contact(allp[a], allp[b], depth=False)
            if c["hits"]:
                report["static_closed"][f"{a}-{b}"] = contact(allp[a], allp[b])
    print("static", report["static_closed"])
    report["assembly"] = assembly(parts)
    print("assembly", json.dumps(report["assembly"], ensure_ascii=False)[:3000])
    # 質量特性（中実 PLA）
    rho = P.PLA_DENSITY / 1e9  # kg/mm3
    mp = {}
    for n in ("lid", "crank", "link", "box", "clip", "pin", "speaker_clip"):
        m = parts[n].mass_props()
        mp[n] = dict(volume_mm3=round(m["volume"], 1), mass_g=round(m["volume"] * rho * 1000, 2),
                     com_mm=[round(x, 2) for x in m["com"]], ixx_com_mm5=m["ixx_com"])
    report["mass"] = mp
    # 刷る姿勢
    report["overhang_calibration"] = calib_overhang()
    print("overhang calib", report["overhang_calibration"])
    report["overhang"] = {}
    for n in ("box", "lid", "crank", "link", "pin", "clip", "speaker_clip"):
        m = Mesh.load(os.path.join(BUILD, f"print_{n}.stl"), n)
        report["overhang"][n] = overhang_report(m)
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
