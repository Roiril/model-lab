"""Hiwonder uHand の見た目の再現（表示用。印刷用ではない）。

./run.sh models/hiwonder-uhand/model.py で exports/hiwonder-uhand.stl を書く。
render_views.py は build() を呼んで写真と同じ角度で描く。
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bpy
from mathutils import Matrix, Vector

import params as P

MM = P.MM


# ======================================================================
# 材質
# ======================================================================
def _mat(name, color, rough, metal=0.0, coat=0.0, spec=0.5):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for key in ("Coat Weight", "Clearcoat"):
        if key in b.inputs:
            b.inputs[key].default_value = coat
            break
    for key in ("Specular IOR Level", "Specular"):
        if key in b.inputs:
            b.inputs[key].default_value = spec
            break
    m.diffuse_color = (*color, 1)
    return m


def _grain(m, scale=900.0, strength=0.06):
    """艶消しアルミの細かな粒（バンプ）。"""
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 2.0
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def materials():
    return dict(
        acrylic=_mat("uh_acrylic", (0.006, 0.006, 0.007), 0.13, coat=0.0, spec=0.5),
        servo=_mat("uh_servo", (0.008, 0.008, 0.009), 0.5),
        # 甲の板と側板: 黒の艶消し焼付塗装（2026-11-10 074343 / 074156 の写真）
        alu=_grain(_mat("uh_alu", (0.014, 0.014, 0.016), 0.7, metal=0.2), scale=1500.0, strength=0.2),
        steel=_mat("uh_steel", (0.45, 0.45, 0.47), 0.3, metal=0.55),
        link=_mat("uh_link", (0.42, 0.42, 0.44), 0.32, metal=0.5),
        dark=_mat("uh_dark", (0.002, 0.002, 0.002), 0.5),
        bushing=_mat("uh_bushing", (0.01, 0.01, 0.011), 0.25),
        nylon=_mat("uh_nylon", (0.86, 0.86, 0.84), 0.45),
        brass=_mat("uh_brass", (0.8, 0.58, 0.22), 0.25, metal=1.0),
        blue=_mat("uh_blue", (0.022, 0.045, 0.14), 0.12, coat=0.6),
        label=_mat("uh_label", (0.9, 0.9, 0.9), 0.5),
    )


# ======================================================================
# 2D の形
# ======================================================================
def circle(c, r, n=24):
    return [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def rrect(x0, y0, x1, y1, r, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def fillet(poly, r, n=4):
    """多角形の角を半径 r で丸める（各角で辺の長さの 4 割を上限）。"""
    out = []
    k = len(poly)
    for i in range(k):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % k])
        d0, d1 = (p0 - p1), (p2 - p1)
        l0, l1 = d0.length, d1.length
        d0.normalize(); d1.normalize()
        ang = math.acos(max(-1, min(1, d0.dot(d1))))
        if ang < 1e-3 or abs(ang - math.pi) < 1e-3:
            out.append(tuple(p1)); continue
        t = min(r / math.tan(ang / 2), 0.4 * l0, 0.4 * l1)
        a, b = p1 + d0 * t, p1 + d1 * t
        for j in range(n + 1):  # 二次ベジェで近似
            s = j / n
            q = a * (1 - s) ** 2 + p1 * 2 * s * (1 - s) + b * s * s
            out.append((q.x, q.y))
    return out


def ribbon(center, half):
    """中心線 center（点列）に沿う太さ half（点ごと）の帯。両端は半円。"""
    pts = [Vector(c) for c in center]
    n = len(pts)
    if not isinstance(half, (list, tuple)):
        half = [half] * n
    left, right = [], []
    for i in range(n):
        d = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = Vector((-d.y, d.x))
        left.append(pts[i] + nrm * half[i])
        right.append(pts[i] - nrm * half[i])
    out = [tuple(p) for p in left]
    d = (pts[-1] - pts[-2]).normalized()
    nrm = Vector((-d.y, d.x))
    for j in range(1, 8):
        a = math.pi * j / 8
        v = pts[-1] + nrm * half[-1] * math.cos(a) + d * half[-1] * math.sin(a)
        out.append(tuple(v))
    out += [tuple(p) for p in reversed(right)]
    d = (pts[0] - pts[1]).normalized()
    nrm = Vector((-d.y, d.x))
    for j in range(1, 8):
        a = math.pi * j / 8
        v = pts[0] + nrm * half[0] * math.cos(a) + d * half[0] * math.sin(a)
        out.append(tuple(v))
    return out


def arc_pts(a, b, sag, n=12):
    """a から b への弧（中点で sag だけ左へ膨らむ）。"""
    a, b = Vector(a), Vector(b)
    d = b - a
    nrm = Vector((-d.y, d.x)).normalized()
    return [tuple(a + d * (i / n) + nrm * sag * 4 * (i / n) * (1 - i / n)) for i in range(n + 1)]


# ======================================================================
# 3D 化
# ======================================================================
COLL = None


def _link(ob):
    COLL.objects.link(ob)
    return ob


def basis(u, v, origin):
    u, v = Vector(u).normalized(), Vector(v).normalized()
    n = u.cross(v)
    M = Matrix.Identity(4)
    for i in range(3):
        M[i][0], M[i][1], M[i][2], M[i][3] = u[i], v[i], n[i], origin[i]
    return M


def _inside(pt, poly):
    x, y = pt
    c = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def plate(name, outline, t, M, mat, holes=(), bevel=0.35):
    """平面内の輪郭（mm）を厚み t（mm、+n 側と -n 側に半分ずつ）で押し出す。M は mm 系の基底。"""
    # 穴が輪郭からはみ出すと 2D カーブの面が張れず、縁の線だけが残る（2026-11-10 にサーボ板で起きた）
    for h in holes:
        bad = [q for q in h if not _inside(tuple(q), [tuple(v) for v in outline])]
        if bad:
            raise ValueError(f"{name}: 穴が輪郭の外に出ている {bad[0]}")
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    b = min(bevel, t * 0.3)
    cu.extrude = max(t / 2 - b, 0.01) * MM
    cu.bevel_depth = b * MM
    cu.bevel_resolution = 2
    for loop in [outline, *holes]:
        sp = cu.splines.new("POLY")
        sp.points.add(len(loop) - 1)
        for i, (x, y) in enumerate(loop):
            sp.points[i].co = (x * MM, y * MM, 0, 1)
        sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(mat)
    M2 = M.copy()
    for i in range(3):
        M2[i][3] *= MM
    ob.matrix_world = M2
    return _link(ob)


def xz_plate(name, outline, y_front, t, mat, holes=(), bevel=0.35):
    """XZ 面の板。y_front（手前 = -Y 側の面）から +Y へ厚み t。"""
    return plate(name, outline, t, basis((1, 0, 0), (0, 0, 1), (0, y_front + t / 2, 0)), mat, holes, bevel)


def box(name, c, s, mat, bevel=0.6):
    bpy.ops.mesh.primitive_cube_add(size=1, location=[v * MM for v in c])
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = [v * MM for v in s]
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        m = ob.modifiers.new("bv", "BEVEL")
        m.width = bevel * MM
        m.segments = 2
    ob.data.materials.append(mat)
    _move(ob)
    return ob


def cyl(name, a, b, r, mat, n=24, bevel=0.0):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=n, radius=r * MM, depth=d.length * MM,
                                        location=((a + b) / 2) * MM)
    ob = bpy.context.active_object
    ob.name = name
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    if bevel:
        m = ob.modifiers.new("bv", "BEVEL")
        m.width = bevel * MM
        m.segments = 2
    ob.data.materials.append(mat)
    _move(ob)
    return ob


def _move(ob):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    COLL.objects.link(ob)


def screw(name, pos, normal, M, r=2.5, head="pan"):
    """ねじの頭。pos は面上の点、normal は外向き。head="pan" は十字の溝つき、"button" は溝の見えない丸い頭。"""
    pos, normal = Vector(pos), Vector(normal).normalized()
    h = r * (0.5 if head == "button" else 0.26)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=r * MM,
                                         location=pos * MM)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (1, 1, h / r)
    ob.rotation_euler = normal.to_track_quat("Z", "Y").to_euler()
    ob.data.materials.append(M["steel"])
    _move(ob)
    if head == "button":   # 甲の写真のねじは丸い頭で溝が見えない
        return ob
    # 十字の溝
    q = normal.to_track_quat("Z", "Y")
    for k in range(2):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(pos + normal * h * 0.85) * MM)
        c = bpy.context.active_object
        c.name = name + f"_x{k}"
        c.scale = ((r * 1.15 if k == 0 else r * 0.32) * MM, (r * 0.32 if k == 0 else r * 1.15) * MM, h * 0.7 * MM)
        c.rotation_euler = (q @ Matrix.Rotation(math.radians(45), 4, "Z").to_quaternion()).to_euler()
        c.data.materials.append(M["dark"])
        _move(c)
    return ob


def nut(name, pos, normal, M, r=2.8, h=2.0):
    pos, normal = Vector(pos), Vector(normal).normalized()
    cyl(name, pos, pos + normal * h, r, M["steel"], n=6, bevel=0.2)


# ======================================================================
# 部品
# ======================================================================
def yz(x):
    """YZ 面の板の基底。面内座標は (y, z)、厚みは x を中心に振り分ける。"""
    return basis((0, 1, 0), (0, 0, 1), (x, 0, 0))


def xcyl(name, x0, x1, p, r, mat, n=24, bevel=0.0):
    """X 軸に平行な円柱。p は面内の (y, z)。"""
    return cyl(name, (x0, p[0], p[1]), (x1, p[0], p[1]), r, mat, n=n, bevel=bevel)


def palm_plate(M):
    """手のひらの板。上端は指ごとの段、親指側に翼。指ごとに 2 列の窓とねじ、1 列目の上に S 字の板の受け。"""
    outline = fillet(P.PALM_OUTLINE, 1.5)
    holes, insets = [], []
    for xa, s in zip(P.FINGER_X, P.STEP_Z):
        xb = xa + P.COL_B
        for x0, z0, x1, z1, tab in ((xa + 0.6, s - 17.2, xa + 3.6, s - 12.2, False),
                                    (xb - 1.6, s - 7.8, xb + 1.6, s - 2.3, True),
                                    (xb - 1.5, s - 18.8, xb + 1.5, s - 13.3, False)):
            h = rrect(x0, z0, x1, z1, 0.4, 2)
            if all(_inside(q, outline) for q in h):
                holes.append(h)
                if tab:
                    insets.append(((x0 + x1) / 2, (z0 + z1) / 2, x1 - x0 - 0.5, z1 - z0 - 0.8))
    y0 = P.PALM_Y[0]
    xz_plate("palm_plate", outline, y0, P.ACRYLIC_T, M["acrylic"], holes)
    for k, (x, z, w, h) in enumerate(insets):     # 窓に差さった指の台の爪
        box(f"palm_tab{k}", (x, 0.2, z), (w, P.ACRYLIC_T + 1.0, h), M["servo"], bevel=0.2)
    for i, (xa, s) in enumerate(zip(P.FINGER_X, P.STEP_Z)):
        screw(f"palm_sa{i}", (xa + 1.0, y0, s - 10.0), (0, -1, 0), M, r=1.5)
        screw(f"palm_sb{i}", (xa + P.COL_B, y0, s - 10.0), (0, -1, 0), M, r=1.5)
        # S 字の板の受け（板の手前の黒い台と、横向きの軸）
        hy, hz = P.HOOK_PIVOT[0], s + P.HOOK_PIVOT[1]
        box(f"hook_block{i}", (xa, (y0 - 9.0) / 2, s - 5.3), (4.5, 9.0 + y0, 5.6), M["servo"], bevel=0.5)
        xcyl(f"hook_bush{i}", xa - 2.0, xa + 3.6, (hy, hz), 2.3, M["bushing"], bevel=0.3)
        screw(f"hook_screw{i}", (xa + P.LAYER_S - P.LINK_T / 2, hy, hz), (-1, 0, 0), M, r=1.7)
    for i, (x, z) in enumerate(P.PALM_SCREWS):
        screw(f"palm_screw{i}", (x, y0, z), (0, -1, 0), M, r=1.6)


def servo_plate(M):
    """手前のサーボ板。指のサーボ 4 個の窓があり、下は親指のサーボをよけて斜めに切れている。"""
    W, H = P.SERVO_FACE
    holes = [rrect(x - W / 2 - 0.3, z - H / 2 - 0.3, x + W / 2 + 0.3, z + H / 2 + 0.3, 0.6, 2)
             for x, z in P.FINGER_SERVOS]
    ys = P.SERVO_PLATE_Y
    xz_plate("servo_plate", fillet(P.SERVO_PLATE, 1.5), ys, P.ACRYLIC_T, M["acrylic"], holes)
    for i, (x, z, r) in enumerate(P.SERVO_PLATE_SCREWS):
        screw(f"sp_screw{i}", (x, ys, z), (0, -1, 0), M, r=r)
        cyl(f"sp_post{i}", (x, ys + P.ACRYLIC_T, z), (x, P.PALM_Y[0], z), 2.0, M["bushing"], n=6)


def servo(name, cx, cz, M):
    W, H = P.SERVO_FACE
    yf = P.SERVO_PLATE_Y - P.SERVO_PROUD
    D = P.SERVO_DEPTH
    box(name, (cx, yf + D / 2, cz), (W, D, H), M["servo"], bevel=0.5)
    for sx in (-1, 1):
        for sz in (-1, 1):
            screw(f"{name}_s{sx}{sz}", (cx + sx * (W / 2 - 1.5), yf, cz + sz * (H / 2 - 1.5)), (0, -1, 0), M, r=0.85)
    # 底面の浮き彫り: 上に四角で囲んだ X 字、中央に穴、下に弧
    Mb = basis((1, 0, 0), (0, 0, 1), (cx, yf - 0.12, cz))
    plate(name + "_frame", [(-3, 4.3), (3, 4.3), (3, 8.8), (-3, 8.8)], 0.25, Mb, M["servo"],
          [[(-2.5, 4.8), (2.5, 4.8), (2.5, 8.3), (-2.5, 8.3)]], bevel=0.03)
    for k, (a, b) in enumerate((((-2.1, 5.2), (2.1, 7.9)), ((-2.1, 7.9), (2.1, 5.2)))):
        plate(f"{name}_x{k}", ribbon([a, b], 0.28), 0.25, Mb, M["servo"], bevel=0.03)
    cyl(name + "_hole", (cx, yf + 0.4, cz), (cx, yf - 0.03, cz), 0.8, M["dark"], n=16)
    arc = [(2.3 * math.cos(math.radians(a)), -4 + 1.3 * math.sin(math.radians(a))) for a in range(200, 341, 10)]
    plate(name + "_arc", ribbon(arc, 0.24), 0.25, Mb, M["servo"], bevel=0.03)


def thumb_frame():
    """親指の板の面の基底。e1 は面内で右下がり、e2 は手のひら側、n は板の上面から下向き。"""
    t = math.radians(P.THUMB_TILT)
    e1 = Vector((math.cos(t), 0, -math.sin(t)))
    e2 = Vector((0, -1, 0))
    return e1, e2, e1.cross(e2), Vector(P.THUMB_ORIGIN)


def thumb_pt(a, b, h=0.0):
    e1, e2, n, o = thumb_frame()
    return o + e1 * a + e2 * b + n * h


def thumb_ab(p):
    """実座標の点を親指の面内座標 (a, b, h) に直す。"""
    e1, e2, n, o = thumb_frame()
    d = Vector(p) - o
    return d.dot(e1), d.dot(e2), d.dot(n)


def thumb_strut_bottom():
    d = math.radians(P.THUMB_DIR)
    a = P.THUMB_PIVOT_A + P.THUMB_STRUT * math.cos(d)
    b = P.THUMB_STRUT * math.sin(d)
    return a, b


def servos(M):
    for i, (x, z) in enumerate(P.FINGER_SERVOS):
        servo(f"servo{i}", x, z, M)
    # 親指のサーボ。寝かせて斜めに付く。上面（出力軸のある面）が手のひら側を向く
    sx, sz = P.THUMB_SERVO_SHAFT
    t = math.radians(P.THUMB_SERVO_TILT)
    u, w = Vector((math.cos(t), math.sin(t))), Vector((-math.sin(t), math.cos(t)))
    s0 = Vector((sx, sz))

    def rect(a0, a1, hw):
        return [tuple(s0 + u * a + w * b) for a, b in ((a0, -hw), (a1, -hw), (a1, hw), (a0, hw))]

    yt = P.THUMB_SERVO_TOP_Y
    D = P.SERVO_DEPTH
    Mxz = lambda y: basis((1, 0, 0), (0, 0, 1), (0, y, 0))
    plate("thumb_servo", fillet(rect(*P.THUMB_SERVO_ALONG, 6.0), 0.8), D, Mxz(yt + D / 2), M["servo"], bevel=0.5)
    plate("thumb_servo_ear", fillet(rect(*P.THUMB_SERVO_EARS, 6.0), 1.5), 2.5, Mxz(yt + 5.5), M["servo"], bevel=0.4)
    for k, a in enumerate((P.THUMB_SERVO_EARS[0] + 2.3, P.THUMB_SERVO_EARS[1] - 2.6)):
        q = s0 + u * a
        screw(f"thumb_servo_s{k}", (q.x, yt + 4.25, q.y), (0, -1, 0), M, r=1.5)
    # ホーン（白いナイロン）。軸から右上へ腕が伸び、先に押し棒の受けが付く
    hx, hz = P.HORN_TIP
    yh = P.HORN_Y
    cyl("horn_boss", (sx, yt, sz), (sx, yh + 1.0, sz), 3.0, M["nylon"], n=24)
    holes = [circle((sx + (hx - sx) * f, sz + (hz - sz) * f), 0.55, 10) for f in (0.36, 0.5, 0.64)]
    plate("horn_arm", ribbon([(sx, sz), (hx, hz)], [3.6, 2.7]), 2.0, Mxz(yh), M["nylon"], holes, bevel=0.4)
    plate("horn_stub", ribbon([(sx, sz), (sx + 5.6, sz - 2.3)], [3.6, 3.0]), 2.0, Mxz(yh), M["nylon"],
          [circle((sx + 5.6, sz - 2.3), 1.2, 14)], bevel=0.4)
    cyl("horn_washer", (sx, yh - 1.0, sz), (sx, yh - 1.5, sz), 2.6, M["steel"], n=24)
    screw("horn_screw", (sx, yh - 1.5, sz), (0, -1, 0), M, r=1.7)
    cyl("rod_end0", (hx, yh - 1.0, hz), (hx, yh - 4.6, hz), 3.3, M["servo"], n=24, bevel=0.5)
    screw("rod_end0_s", (hx, yh - 4.6, hz), (0, -1, 0), M, r=1.6)
    # 押し棒: ホーンの先から親指の下の真鍮の柱の下端へ
    a, b = thumb_strut_bottom()
    end = thumb_pt(a, b, P.THUMB_LAYERS["lower"][1] + 9.5)
    cyl("push_rod", (hx, yh - 2.8, hz), end, 1.1, M["servo"], n=12)


def edge_wall(name, a, b, y0, y1, M):
    """甲の板の縁 a→b（xz）から手のひら側へ折れた板。板の内側は a→b の左手（輪郭は反時計回り）。"""
    t = P.METAL_T
    a3, b3 = Vector((a[0], 0, a[1])), Vector((b[0], 0, b[1]))
    w = (b3 - a3).normalized()
    n_in = Vector((-w.z, 0, w.x))
    L = (b3 - a3).length
    o = a3 + n_in * (t / 2)
    plate(name, rrect(y0, 0, y1, L, 1.2, 3), t, basis((0, 1, 0), tuple(w), tuple(o)), M["alu"])
    c0, c1 = a3 + n_in * t, b3 + n_in * t
    cyl(name + "_fold", (c0.x, y1 - t, c0.z), (c1.x, y1 - t, c1.z), t, M["alu"], n=16)


def along(a, b, d):
    """a から b へ向かって d だけ進んだ点。"""
    a, b = Vector(a), Vector(b)
    return tuple(a + (b - a).normalized() * d)


def metal_cover(M):
    """甲の板金。甲の板と、縁から手のひら側へ折れた左右の側板、上辺と面取りの縁。
    親指側の縁は鉛直、小指側の縁は上へ向けて外に開く（写真 04 を、下辺を水平にして読んだ）。"""
    y0, y1 = P.BACK_Y
    xz_plate("back_plate", fillet(P.BACK_OUTLINE, 3.5), y0, P.METAL_T, M["alu"])
    for i, (x, z) in enumerate(P.BACK_SCREWS_SMALL):
        screw(f"bp_screw{i}", (x, y1, z), (0, 1, 0), M, r=1.4, head="button")
    for i, (x, z) in enumerate(P.BACK_SCREWS_BIG):
        screw(f"bp_big{i}", (x, y1, z), (0, 1, 0), M, r=2.0, head="button")
    edge_wall("wall_thumb", along(P.BACK_BT, P.BACK_TT, 4.0), P.BACK_TT, P.SIDE_WALL_Y0, y1, M)
    edge_wall("wall_little", P.BACK_TL, along(P.BACK_BL, P.BACK_TL, 4.0), P.SIDE_WALL_Y0, y1, M)
    edge_wall("lip_chamfer", P.BACK_TT, P.BACK_PEAK, y1 - P.TOP_LIP, y1, M)
    edge_wall("lip_top", P.BACK_PEAK, P.BACK_TL, y1 - P.TOP_LIP, y1, M)
    # 板の間の柱（甲のねじ 4 本が手のひらの板まで通る）
    for i, (x, z) in enumerate(P.BACK_SCREWS_SMALL):
        cyl(f"post{i}", (x, P.PALM_Y[1], z), (x, y0, z), 2.2, M["bushing"], n=6)
    # 内側の詰め物（すき間から背景が抜けないように）
    box("palm_core", (-1.5, 13.5, 47.0), (40.0, 21.0, 44.0), M["dark"], bevel=0)


def wrist(M):
    """手首。甲の板の内側に重なる L 字の金具。縦の板が甲の板の下から舌のように出て、前へ折れて丸いフランジに載る。"""
    x0, x1 = P.WRIST_X
    t = P.METAL_T
    zb, zt = P.WRIST_H_Z
    yv = P.BACK_Y[0] - t
    xz_plate("wrist_v", rrect(x0, zb, x1, P.WRIST_TOP_Z, 1.2), yv, t, M["alu"])
    Mh = basis((1, 0, 0), (0, 1, 0), (0, 0, (zb + zt) / 2))
    plate("wrist_h", rrect(x0, P.WRIST_FRONT_Y, x1, yv + t, 2.0), zt - zb, Mh, M["alu"])
    cyl("wrist_bend", (x0 + 0.3, yv + t - (zt - zb), zt), (x1 - 0.3, yv + t - (zt - zb), zt), zt - zb, M["alu"], n=20)
    f = P.WRIST_FLANGE
    cyl("wrist_flange", (f["x"], f["y"], zb), (f["x"], f["y"], f["z0"]), f["r"], M["servo"], n=48, bevel=0.3)
    cyl("wrist_hub", (f["x"], f["y"], f["z0"]), (f["x"], f["y"], 0.0), f["hub_r"], M["steel"], n=32, bevel=0.2)
    for i, a in enumerate((0, 90, 180, 270)):
        a = math.radians(a)
        screw(f"wrist_screw{i}", (f["x"] + 7.0 * math.cos(a), f["y"] + 7.0 * math.sin(a), zt), (0, 0, 1), M, r=1.5)


# ---- 指 ---------------------------------------------------------------
def paddle_outline(sh):
    """末節の板。付け根が広く、先へ細くなる木の葉形（側面図の人差し指）。"""
    cy, cz = P.F_TIP_C
    r = P.F_TIP_R
    cap = [(cy + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a))) for a in range(45, 186, 15)]
    pts = [(11.4, 138.8), (10.2, 143.0), *cap, (-15.2, 155.0), (-13.7, 150.5), (-11.2, 146.2),
           (-8.3, 142.5), (-6.5, 139.9), (5.0, 136.9), (8.3, 136.6), (10.7, 137.6)]
    return [sh(p) for p in pts]


def finger(i, M):
    """指 1 本。面内座標 (y, z) は側面図の人差し指の読み。指ごとに z をずらし、付け根の軸まわりに扇に開く。
    手のひらの板の後ろに付け根の軸があり、基節が板の上端をまたいで前へ傾く。
    板の層（小指側から）: S 字の銀の板、中節の板、基節と末節の板、銀の連結板。"""
    nm = ("little", "ring", "middle", "index")[i]
    xa, dz, s = P.FINGER_X[i], P.FINGER_DZ[i], P.STEP_Z[i]
    t = P.FINGER_T
    blk, slv = M["acrylic"], M["link"]

    def sh(p):
        return (p[0], p[1] + dz)

    mcp, pip, dip, mid = sh(P.F_MCP), sh(P.F_PIP), sh(P.F_DIP), sh(P.F_MID)
    pa, pd, pg = sh(P.F_A), sh(P.F_D), sh(P.F_G)
    xm, xc, xl = xa + P.LAYER_MID, xa + P.LAYER_CORE, xa + P.LAYER_LINK
    before = set(COLL.objects)

    # 基節（付け根の軸から最初の関節まで）と、連結板の下端を受ける張り出し
    plate(f"{nm}_prox", ribbon([mcp, sh((12.0, 100.0)), pip], [4.5, 5.5, 6.3]), t, yz(xc), blk, bevel=0.3)
    plate(f"{nm}_prox_lug", ribbon([pip, pa], [4.0, 3.2]), t, yz(xc), blk, bevel=0.3)
    # 中節（2 つの関節をつなぐ骨の形の板）と、下の尾
    plate(f"{nm}_mid", ribbon([dip, mid, pip], [4.3, 3.5, 4.3]), t, yz(xm), blk, bevel=0.3)
    plate(f"{nm}_mid_tail", ribbon([pip, pg], [4.3, 3.0]), t, yz(xm), blk, bevel=0.3)
    # 末節
    plate(f"{nm}_tip", paddle_outline(sh), t, yz(xc), blk, bevel=0.4)
    # 銀の連結板（親指側の面。基節の張り出しから末節の付け根へ、甲の側へ少し反る）
    ap = arc_pts(pa, pd, -1.2)
    plate(f"{nm}_link", ribbon(ap, 2.0), P.LINK_T, yz(xl), slv, bevel=0.25)
    for e, q in enumerate((pa, pd)):
        plate(f"{nm}_link_e{e}", circle(q, 3.0, 20), P.LINK_T, yz(xl), slv, bevel=0.25)
        screw(f"{nm}_link_s{e}", (xl + P.LINK_T / 2, q[0], q[1]), (1, 0, 0), M, r=1.9)

    # 小指側の面の金具: 2 つの関節に大きい座金とねじ、中ほどに小ねじ
    xf = xm - t / 2
    for k, q in enumerate((dip, pip)):
        xcyl(f"{nm}_washer{k}", xf, xf - 0.7, q, 3.3, M["steel"], bevel=0.15)
        screw(f"{nm}_jscrew{k}", (xf - 0.7, q[0], q[1]), (-1, 0, 0), M, r=1.9, head="button")
    screw(f"{nm}_midscrew", (xf, mid[0], mid[1]), (-1, 0, 0), M, r=1.5, head="button")
    nut(f"{nm}_midnut", (xm + t / 2, mid[0], mid[1]), (1, 0, 0), M, r=1.9, h=1.8)
    # 親指側の面: 最初の関節から黒い筒が出て、先が銀色
    xr = xc + t / 2
    xcyl(f"{nm}_pip_spacer", xr, xr + 3.5, pip, 2.6, M["bushing"], bevel=0.3)
    xcyl(f"{nm}_pip_cap", xr + 3.5, xr + 4.3, pip, 1.7, M["steel"], bevel=0.2)
    xcyl(f"{nm}_dip_pin", xr, xr + 0.5, dip, 1.0, M["steel"])
    # 付け根の軸とナット
    xcyl(f"{nm}_mcp_bolt", xm - t / 2 - 0.5, xr + 2.0, mcp, 1.2, M["steel"])
    nut(f"{nm}_mcp_nut", (xr, mcp[0], mcp[1]), (1, 0, 0), M, r=2.6, h=1.9)
    # 引き棒（サーボから基節の上端へ）と下端のナット
    rb, rt = sh(P.F_ROD_BOTTOM), sh(P.F_ROD_TOP)
    cyl(f"{nm}_rod", (xc, rb[0], rb[1]), (xc, rt[0], rt[1]), 0.7, M["steel"], n=10)
    xcyl(f"{nm}_rod_end", xc - 1.8, xc + 1.8, rb, 3.0, M["bushing"], bevel=0.3)
    nut(f"{nm}_rod_nut", (xc + 1.8, rb[0], rb[1]), (1, 0, 0), M, r=2.2, h=1.6)

    # 付け根の軸まわりに扇に開く
    c = Vector((xa, mcp[0], mcp[1])) * MM
    R = Matrix.Translation(c) @ Matrix.Rotation(math.radians(P.FINGER_FAN[i]), 4, "Y") @ Matrix.Translation(-c)
    bpy.context.view_layer.update()
    for ob in set(COLL.objects) - before:
        ob.matrix_world = R @ ob.matrix_world

    # 付け根の台（手のひらの板の後ろで軸を支える）。板に固定なので回さない
    plate(f"{nm}_base", ribbon([(4.5, s - 1.5), mcp], [4.0, 4.6]), t, yz(xm), M["servo"], bevel=0.3)
    # S 字の銀の板: 手のひらの板の手前の軸から板の上端をまたぎ、中節の尾へ上がる
    g = (R @ (Vector((xm, pg[0], pg[1])) * MM)) / MM
    hy, hz = P.HOOK_PIVOT[0], s + P.HOOK_PIVOT[1]
    top = s + 6.3
    path = [(hy, hz), (hy + 0.3, s + 0.8), (-4.6, s + 4.7), (-0.8, top), (2.6, top + 1.4),
            (4.4, (top + 1.4 + g.z) / 2), (g.y, g.z)]
    xs = xa + P.LAYER_S
    plate(f"{nm}_slink", ribbon(path, 1.9), P.LINK_T, yz(xs), slv, bevel=0.25)
    for e, q in enumerate((path[0], path[-1])):
        plate(f"{nm}_slink_e{e}", circle(q, 2.8, 20), P.LINK_T, yz(xs), slv, bevel=0.25)
    screw(f"{nm}_slink_s", (xs - P.LINK_T / 2, g.y, g.z), (-1, 0, 0), M, r=1.7)


def fingers(M):
    for i in range(4):
        finger(i, M)


def thumb(M):
    """親指。基節は上下 2 枚の板、末節は 1 枚でその間に挟まる。板は右下がりに傾き、正面からは縁だけが見える。
    上に銀のクランク（翼の裏から親指へ渡る）、下に真鍮の柱と押し棒。"""
    e1, e2, n, o = thumb_frame()
    L = P.THUMB_LAYERS

    def Mt(layer):
        h0, h1 = layer
        return basis(tuple(e1), tuple(e2), tuple(o + n * ((h0 + h1) / 2))), h1 - h0

    d = math.radians(P.THUMB_DIR)
    du = Vector((math.cos(d), math.sin(d)))
    pv = Vector((P.THUMB_PIVOT_A, 0.0))
    jt = pv + du * P.THUMB_PROX_LEN
    up = -n

    # 基節の上下の板
    Mu, tu = Mt(L["upper"])
    plate("thumb_upper", ribbon([tuple(pv - du * 2), tuple(pv + du * 24), tuple(jt)], [6.0, 6.0, 5.2]), tu, Mu,
          M["acrylic"], bevel=0.3)
    Ml, tl = Mt(L["lower"])
    plate("thumb_lower", ribbon([tuple(pv - du * 5), tuple(pv + du * 20), tuple(pv + du * 40)], [6.0, 6.0, 5.0]), tl, Ml,
          M["acrylic"], bevel=0.3)
    # 付け根の黒い詰め物と縦軸
    Mm, tm = Mt(L["mid"])
    plate("thumb_root", ribbon([tuple(pv - du * 2), tuple(pv + du * 14)], 5.0), tm, Mm, M["servo"], bevel=0.3)
    cyl("thumb_pivot", thumb_pt(pv.x, pv.y, -1.2), thumb_pt(pv.x, pv.y, L["lower"][1] + 1.2), 3.2, M["bushing"], n=24, bevel=0.3)
    # 末節（1 枚。関節の手前から始まり、先は丸く、穴が 1 つ）
    dm_a = math.radians(P.THUMB_TIP_DIR)
    dm = Vector((math.cos(dm_a), math.sin(dm_a)))
    tip_c = jt + dm * P.THUMB_TIP_LEN
    hole = circle(tuple(tip_c), 1.3, 14)
    plate("thumb_distal", ribbon([tuple(jt - du * 16), tuple(jt - du * 4), tuple(jt + dm * 6), tuple(tip_c)],
                                 [5.2, 5.2, 4.6, 3.9]), tm, Mm, M["acrylic"], [hole], bevel=0.3)
    # 上の板のねじ: 付け根寄りと中ほどに小ねじ、中央と関節に座金つき
    for k, (dist, big) in enumerate(((7.9, False), (28.3, True), (39.9, False), (P.THUMB_PROX_LEN, True))):
        q = pv + du * dist
        top = thumb_pt(q.x, q.y, 0.0)
        if big:
            cyl(f"thumb_w{k}", top, top + up * 0.7, 3.3, M["steel"], n=24, bevel=0.15)
            screw(f"thumb_s{k}", top + up * 0.7, up, M, r=1.9)
        else:
            screw(f"thumb_s{k}", top, up, M, r=1.5)
        if dist <= 40:
            nut(f"thumb_n{k}", thumb_pt(q.x, q.y, L["lower"][1]), n, M, r=1.9, h=1.6)
    # 真鍮の柱と、下端の押し棒の受け
    a, b = thumb_strut_bottom()
    h0 = L["lower"][1]
    cyl("thumb_strut", thumb_pt(a, b, h0), thumb_pt(a, b, h0 + 8.0), 1.5, M["brass"], n=16)
    cyl("rod_end1", thumb_pt(a, b, h0 + 7.5), thumb_pt(a, b, h0 + 11.0), 2.8, M["servo"], n=24, bevel=0.4)
    screw("rod_end1_s", thumb_pt(a, b, h0 + 11.0), n, M, r=1.5)
    # 銀のクランク: 翼の裏の柱から親指の手のひら側の張り出しへ渡る
    fa, fb, fh = thumb_ab(P.THUMB_CRANK_F)
    ta, tb, th = thumb_ab(P.THUMB_CRANK_T)
    hc = min(fh, th, -P.LINK_T / 2 - 0.2)
    Mc = basis(tuple(e1), tuple(e2), tuple(o + n * hc))
    path = [(fa, fb), (fa + (ta - fa) * 0.15, fb + (tb - fb) * 0.35), (fa + (ta - fa) * 0.85, fb + (tb - fb) * 0.65), (ta, tb)]
    plate("thumb_crank", ribbon(path, 2.6), P.LINK_T, Mc, M["link"], bevel=0.25)
    for k, q in enumerate(((fa, fb), (ta, tb))):
        plate(f"thumb_crank_e{k}", circle(q, 3.3, 20), P.LINK_T, Mc, M["link"], bevel=0.25)
        screw(f"thumb_crank_s{k}", thumb_pt(q[0], q[1], hc - P.LINK_T / 2), up, M, r=1.7)
    # 親指側の受け（上の板から手のひら側へ出る黒い張り出し）
    on_axis = pv + du * ((ta - pv.x) / du.x)
    plate("thumb_crank_tab", ribbon([tuple(on_axis), (ta, tb)], [4.0, 3.3]), tu, Mu, M["acrylic"], bevel=0.3)
    # 固定側の柱（翼の裏から）
    f = Vector(P.THUMB_CRANK_F)
    cyl("thumb_crank_post", (f.x, P.PALM_Y[1], f.z), tuple(f), 2.2, M["bushing"], n=6)


# ======================================================================
def build():
    global COLL
    COLL = bpy.data.collections.new("uhand")
    bpy.context.scene.collection.children.link(COLL)
    M = materials()
    palm_plate(M)
    servo_plate(M)
    servos(M)
    metal_cover(M)
    wrist(M)
    fingers(M)
    thumb(M)
    return COLL


def to_meshes():
    """曲線の板をメッシュに直す（STL 用）。"""
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in list(COLL.objects):
        if ob.type == "CURVE":
            me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
            mo = bpy.data.objects.new(ob.name, me)
            mo.matrix_world = ob.matrix_world
            COLL.objects.link(mo)
            bpy.data.objects.remove(ob, do_unlink=True)


if __name__ == "__main__" and not os.environ.get("UHAND_NO_EXPORT"):
    from blender_utils import clear_scene, export_stl
    clear_scene()
    build()
    to_meshes()
    export_stl("hiwonder-uhand")
    # 色つきの GLB
    for ob in bpy.data.objects:
        ob.select_set(ob.name in COLL.objects)
    bpy.ops.export_scene.gltf(filepath=os.path.join(os.path.dirname(__file__), "../../exports/hiwonder-uhand.glb"),
                              export_format="GLB", use_selection=True, export_apply=True)
