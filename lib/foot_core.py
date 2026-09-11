"""パイプの脚を床で受けるベース（pipe-foot-pair / pipe-foot-corner）で共有する形づくりの部品。

寸法はここに持たない。ソケットの輪郭やひれの断面は、呼ぶ側の params を引数で受ける。
単位はモデル側と同じく mm で受け、Blender へ渡すときに MM を掛ける。

boolean は MANIFOLD solver。EXACT より速く、面一の接触が無ければ壊れない。
そのぶん、面どうしの接触・同一平面は呼ぶ側が避けること（板へ 1mm 沈める等）。
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

MM = 0.001


# ---------------------------------------------------------------- basics

def activate(ob):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    return ob


def finish(name, bm, matrix=None):
    """bmesh をオブジェクトにしてシーンへ置く。n-gon は三角形にし、法線を外向きに揃える。"""
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


def translate(x, y, z=0.0):
    return Matrix.Translation(Vector((x, y, z)) * MM)


# ---------------------------------------------------------------- primitives

def revolve(name, profile, matrix=None, seg=96):
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
    return finish(name, bm, matrix)


def cyl(name, r, z0, z1, cx=0.0, cy=0.0, seg=96):
    return revolve(name, [(z0, r), (z1, r)], translate(cx, cy), seg)


def prism(name, poly, z0, z1, matrix=None):
    """poly: [(x, y)]（mm）を z0→z1（mm）に押し出してから matrix で置く。

    ⚠⚠ 凹んだ輪郭に使わない。n-gon の蓋を三角化すると凹みをまたいで膜が張り、
    へこみが塞がって板になる（Blender 5.1 で実測）。体積も非多様体エッジ数も
    正しいままなので、数値では気づけない。凹む形は wall_net() のように
    四角形の帯で組む。
    """
    bm = bmesh.new()
    lo = [bm.verts.new((x * MM, y * MM, z0 * MM)) for x, y in poly]
    hi = [bm.verts.new((x * MM, y * MM, z1 * MM)) for x, y in poly]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    return finish(name, bm, matrix)


def box(name, size, matrix):
    """size: (x, y, z) は Blender 単位（m）。"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts[:], vec=Vector(size))
    return finish(name, bm, matrix)


def box_mm(name, x0, x1, y0, y1, z0, z1):
    """mm の範囲で置く箱。切り落とし用。"""
    return box(name, ((x1 - x0) * MM, (y1 - y0) * MM, (z1 - z0) * MM),
               translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


# ---------------------------------------------------------------- operations

def clean(ob, dist=1e-5):
    """boolean が残す極短エッジを掃除する。放置すると Bevel が発散する。

    ⚠ 辺が 2 本しか無く、その 2 本が一直線に並ぶ頂点も消す。Blender の中では多様体でも、
    STL に書くときの三角化が両側の面で食い違い（片方はその頂点を飛ばして三角形を作る）、
    面積 0 の三角形が 3 面に挟まれた辺として残る。pipe-foot-corner の A2 のひれと台座の
    継ぎ目で実測（ずれ 0.0004mm。Blender 側の非多様体は 0、STL を読み戻すと 3）。
    """
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges[:])
    straight = []
    for v in bm.verts:
        if len(v.link_edges) == 2:
            a, b = (e.other_vert(v).co - v.co for e in v.link_edges)
            if a.length > 0 and b.length > 0 and a.normalized().dot(b.normalized()) < -0.9999:
                straight.append(v)
    if straight:
        print(f"[clean] {ob.name}: 直線上の頂点 {len(straight)} 個を消した")
        bmesh.ops.dissolve_verts(bm, verts=straight)
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
    activate(target)
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
    activate(ob)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


# ---------------------------------------------------------------- outlines

def _normal_angle(p, q):
    """反時計回りの多角形の辺 p→q の、外向き法線の角度。"""
    return math.atan2(-(q[0] - p[0]), q[1] - p[1])


def hull_poly(centers, r, seg=96):
    """半径 r の円を centers（凸な順に反時計回り）に置いたときの凸包。反時計回りの点列。

    各円の上では、入ってくる辺の法線から出ていく辺の法線までの弧を描き、
    弧どうしは共通外接線でつながる。円が 2 つなら長丸になる。
    凸包の内側に入る円は渡さない（その円の弧が輪郭に出て自己交差する）。
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


def socket_profile(P, z_bot):
    """底 → 台座 → ソケット → 口元を 1 本の回転体で作る [(z, r)]。

    pipe-foot の core_profile と同じ。板の側は呼ぶ側が作り直すので、
    ここの円板（DISC_R）は板の中に埋まる。P は params モジュール。
    """
    pts = [(z_bot, P.DISC_R), (P.PLATE_T, P.DISC_R), (P.HUB_T, P.CONE_BASE_R)]
    for i in range(1, P.CONE_SEG + 1):
        t = i / P.CONE_SEG
        z = P.HUB_T + (P.SEAT_Z - P.HUB_T) * t
        pts.append((z, P.BOSS_R + (P.CONE_BASE_R - P.BOSS_R) * (1.0 - smoothstep(t))))
    pts.append((P.BOSS_TOP - P.MOUTH_TAPER, P.BOSS_R))
    for i in range(1, P.CONE_SEG + 1):
        t = i / P.CONE_SEG
        pts.append((P.BOSS_TOP - P.MOUTH_TAPER + P.MOUTH_TAPER * t,
                    P.BOSS_R + (P.TIP_R - P.BOSS_R) * smoothstep(t)))
    out = [pts[0]]
    for p in pts[1:]:
        if p[0] - out[-1][0] > 1e-9:
            out.append(p)
    return out


def socket_profile_plain(P, z_bot, foot_r, arc_seg=8):
    """台座（8mm の段と円錐）を持たないソケット [(z, r)]。板から直接、半径 foot_r の
    丸みで筒が立つ。

    板の縁までの余地が無い所（pipe-foot-corner の外側。軸から 25mm で造形板が尽きる）用。
    丸みは回転体の輪郭に入れるので bevel は掛からない（隣り合う面の角が 25° 未満）。
    筒の外径 + foot_r + 板の縁の R が縁までの距離に収まることは呼ぶ側が確かめる。
    """
    r0 = P.BOSS_R + foot_r
    pts = [(z_bot, r0), (P.PLATE_T, r0)]
    for i in range(1, arc_seg + 1):
        a = math.pi / 2 * i / arc_seg
        pts.append((P.PLATE_T + foot_r * (1.0 - math.cos(a)), r0 - foot_r * math.sin(a)))
    pts.append((P.BOSS_TOP - P.MOUTH_TAPER, P.BOSS_R))
    for i in range(1, P.CONE_SEG + 1):
        t = i / P.CONE_SEG
        pts.append((P.BOSS_TOP - P.MOUTH_TAPER + P.MOUTH_TAPER * t,
                    P.BOSS_R + (P.TIP_R - P.BOSS_R) * smoothstep(t)))
    return pts


def arc(center, r, a0_deg, a1_deg, n):
    """center を中心に a0 → a1（度）をたどる点列。両端を含む。"""
    cx, cy = center
    return [(cx + r * math.cos(math.radians(a0_deg + (a1_deg - a0_deg) * i / n)),
             cy + r * math.sin(math.radians(a0_deg + (a1_deg - a0_deg) * i / n)))
            for i in range(n + 1)]


def chain(*pieces):
    """点列を順につなぐ。継ぎ目で同じ点が重なれば 1 つにする。"""
    out = []
    for pc in pieces:
        for p in pc:
            if out and abs(out[-1][0] - p[0]) < 1e-9 and abs(out[-1][1] - p[1]) < 1e-9:
                continue
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-9 and abs(out[0][1] - out[-1][1]) < 1e-9:
        out.pop()
    return out


def fin_poly(P):
    """横のひれの断面 [(r, z)]。外端は FIN_OUT_H の高さを残して尖らせない。

    ⚠ 外端は板の上面から FIN_OUT_H だけ立てる。ここが 3mm だと 2.5mm の bevel が
    clamp され、外端・側面・板の 3 面が集まる角に 0.03mm の三角形が残る（実測）。
    下端は板へ SPINE_LAP 沈める。面一に乗せると非多様体が 3 から 6 に増えた。
    """
    zb = P.PLATE_T - P.SPINE_LAP
    return [(0.0, zb), (P.FIN_OUT_R, zb), (P.FIN_OUT_R, P.PLATE_T + P.FIN_OUT_H),
            (P.BOSS_R, P.FIN_TOP_Z), (0.0, P.FIN_TOP_Z)]


def fin(name, P, cx, cy, ang_deg):
    """ソケット (cx, cy) から ang_deg の向きへ出すひれ。"""
    m = (translate(cx, cy)
         @ Matrix.Rotation(math.radians(ang_deg), 4, "Z")
         @ Matrix.Rotation(math.radians(90), 4, "X"))
    return prism(name, fin_poly(P), -P.FIN_T / 2, P.FIN_T / 2, m)


# ---------------------------------------------------------------- wall network

def wall_net(name, nodes, walls, thick, z_bot):
    """縦板の網（背骨と枝）を 1 つの多様体メッシュで作る。

    枝を別体にして boolean で足すと、主材の上面と枝の上面がほぼ同じ高さで交わって
    0.1mm 以下の段や薄片が出る。板どうしが出会う点には thick 角の芯を置き、
    板はその芯の面の 4 頂点に直接つなぐ。芯の面のうち板が付かないものは蓋になる。

    nodes: {key: (x, y)}  板どうしが出会う点
    walls: [dict(axis="x"|"y", c=<直交座標>, a=<端>, b=<端>, top=fn, seg=int)]
        a は軸座標の小さい側の端、b は大きい側。端は ("node", key) か ("free", s)。
        自由端は蓋で閉じる（ソケットの肉の中で終わらせる前提）。
        top(s, side) は軸座標 s、側 side（-1 / +1）での上端の高さ。
    芯の上面の高さは、その頂点を含む板の top を全部評価した最大値。
    """
    ht = thick / 2
    bm = bmesh.new()

    def V(x, y, z):
        return bm.verts.new((x * MM, y * MM, z * MM))

    # 芯のどの面に板が付くか。"+x" は芯の +x 側の面
    attached = {k: {} for k in nodes}
    for w in walls:
        for end, low in ((w["a"], True), (w["b"], False)):
            if end[0] == "node":
                face = ("+" if low else "-") + w["axis"]
                assert face not in attached[end[1]], f"{name}: {end[1]} の {face} に板が 2 枚"
                attached[end[1]][face] = w

    def top_at(w, x, y):
        if w["axis"] == "x":
            return w["top"](x, 1 if y > w["c"] else -1)
        return w["top"](y, 1 if x > w["c"] else -1)

    # 芯: corner (sx, sy) → (下, 上)。上の高さは、その角を含む面に付く板の top の最大値。
    # 角を含まない面の板まで見ると、枝の二次曲線を芯の反対側へ外挿した値が混ざる
    core = {}
    for key, (nx, ny) in nodes.items():
        assert attached[key], f"{name}: 節点 {key} に板が 1 枚も付いていない"
        for sx in (-1, 1):
            for sy in (-1, 1):
                x, y = nx + sx * ht, ny + sy * ht
                faces = [("+" if sx > 0 else "-") + "x", ("+" if sy > 0 else "-") + "y"]
                ws = [attached[key][f] for f in faces if f in attached[key]]
                if not ws:                      # 板が付かない角。隣の角と同じ高さにする
                    ws = list(attached[key].values())
                z = max(top_at(w, x, y) for w in ws)
                core[key, sx, sy] = (V(x, y, z_bot), V(x, y, z))
        c = lambda sx, sy: core[key, sx, sy]
        bm.faces.new([c(-1, -1)[1], c(1, -1)[1], c(1, 1)[1], c(-1, 1)[1]])
        bm.faces.new([c(-1, -1)[0], c(-1, 1)[0], c(1, 1)[0], c(1, -1)[0]])
        caps = {"+x": (c(1, -1), c(1, 1)), "-x": (c(-1, -1), c(-1, 1)),
                "+y": (c(-1, 1), c(1, 1)), "-y": (c(-1, -1), c(1, -1))}
        for face, (p, q) in caps.items():
            if face not in attached[key]:
                bm.faces.new([p[0], p[1], q[1], q[0]])

    def face_ring(key, face):
        """芯の面の 4 頂点を [(下-, 上-), (下+, 上+)] の並びで返す。side は直交方向の符号。"""
        s = 1 if face[0] == "+" else -1
        if face[1] == "x":
            return [core[key, s, -1], core[key, s, 1]]
        return [core[key, -1, s], core[key, 1, s]]

    for w in walls:
        axis, c, top = w["axis"], w["c"], w["top"]

        def ring_at(s):
            out = []
            for side in (-1, 1):
                x, y = (s, c + side * ht) if axis == "x" else (c + side * ht, s)
                out.append((V(x, y, z_bot), V(x, y, top(s, side))))
            return out

        ends = []
        for end, low in ((w["a"], True), (w["b"], False)):
            if end[0] == "node":
                nx, ny = nodes[end[1]]
                s_node = nx if axis == "x" else ny
                ends.append((s_node + (ht if low else -ht), face_ring(end[1], ("+" if low else "-") + axis)))
            else:
                ends.append((end[1], None))
        (s0, r0), (s1, r1) = ends
        assert s1 > s0, f"{name}: 板の向きが逆（{s0} → {s1}）"
        n = w.get("seg", 24)
        rings = [r0 if r0 is not None else ring_at(s0)]
        for i in range(1, n):
            rings.append(ring_at(s0 + (s1 - s0) * i / n))
        rings.append(r1 if r1 is not None else ring_at(s1))
        for r, rn in zip(rings, rings[1:]):
            bm.faces.new([r[0][0], rn[0][0], rn[0][1], r[0][1]])
            bm.faces.new([r[1][0], rn[1][0], rn[1][1], r[1][1]])
            bm.faces.new([r[0][0], r[1][0], rn[1][0], rn[0][0]])
            bm.faces.new([r[0][1], r[1][1], rn[1][1], rn[0][1]])
        for r, free in ((rings[0], r0 is None), (rings[-1], r1 is None)):
            if free:
                bm.faces.new([r[0][0], r[0][1], r[1][1], r[1][0]])

    ob = finish(name, bm)
    assert non_manifold(ob) == 0, f"{name}: 板の網に非多様体エッジがある"
    return ob


def non_manifold(ob):
    """非多様体エッジの数。0 でなければ boolean へ渡してはいけない。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    n = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return n
