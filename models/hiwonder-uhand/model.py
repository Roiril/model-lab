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
        alu=_grain(_mat("uh_alu", (0.028, 0.033, 0.046), 0.72, metal=0.3), scale=1500.0, strength=0.25),
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


def joint(name, pos, x_out, x_in, M, washer=True):
    """指の関節の軸。x_out 側（-X、カメラ側）にねじ頭と黒いブッシュ、x_in 側にナット。"""
    p = Vector(pos)
    out = Vector((x_out, p.y, p.z))
    inn = Vector((x_in, p.y, p.z))
    sgn = -1 if x_out < x_in else 1
    if washer:
        cyl(name + "_bush", out, out + Vector((sgn * 1.6, 0, 0)), 3.6, M["bushing"], bevel=0.3)
        screw(name + "_head", out + Vector((sgn * 1.6, 0, 0)), (sgn, 0, 0), M, r=2.3)
    else:
        screw(name + "_head", out, (sgn, 0, 0), M, r=2.3)
    nut(name + "_nut", inn, (-sgn, 0, 0), M, r=2.4, h=1.6)


# ======================================================================
# 部品
# ======================================================================
def front_plates(M):
    # 指の付け根を受ける紺色の板。指の後ろに立ち、上端は指ごとの段付き。ねじの上下に縦長の小窓
    xl, xr = P.BLUE_X
    tops, steps = P.PLATE_TOP, P.PLATE_STEPS
    edges = [xl] + steps + [xr]
    up = [(xl + 17, P.BLUE_BOTTOM), (xl, P.BLUE_LITTLE_BOTTOM)]   # 小指側の下は斜めに落とす（サーボの写真で板の外に何も無い）
    for k in range(4):
        x0, x1, zt = edges[k], edges[k + 1], tops[k]
        up += [(x0, zt - 3), (x0 + 3, zt)] if k == 0 else [(x0, tops[k - 1]), (x0, zt)]
        up += [(x1 - 5, zt), (x1, zt - 5)] if k == 3 else [(x1, zt)]
    up += [(xr, P.BLUE_BOTTOM)]
    holes = []
    for x, z in P.UPPER_SCREWS:
        for z0, z1 in ((z + 4.5, z + 11.5), (z - 12.0, z - 5.0)):
            holes.append(rrect(x - 1.3, z0, x + 1.3, z1, 0.4, 2))
    holes = [h for h in holes if all(_inside(q, up) for q in h)]
    xz_plate("upper_plate", up, P.UPPER_PLATE_Y, P.ACRYLIC_T, M["blue"], holes)
    for i, (x, z) in enumerate(P.UPPER_SCREWS):
        screw(f"up_screw{i}", (x, P.UPPER_PLATE_Y, z), (0, -1, 0), M, r=2.2)

    # 手前のサーボ板。サーボの窓、親指サーボの切り欠き、左右の耳の穴
    W, H = P.SERVO_FACE
    holes = [rrect(x - W / 2 - 0.6, z - H / 2 - 0.6, x + W / 2 + 0.6, z + H / 2 + 0.6, 1.0, 2)
             for x, z in P.FINGER_SERVOS]
    holes += [circle(c, 3.3, 24) for c in P.LOWER_EAR_HOLES]
    sx, sz = P.THUMB_SERVO_SHAFT
    holes.append(circle((sx, sz), 7.5, 28))   # 親指サーボの出力軸とホーンの逃げ
    xz_plate("lower_plate", fillet(P.LOWER_PLATE, 2.5), P.LOWER_PLATE_Y, P.ACRYLIC_T + 1, M["acrylic"], holes)
    ys = P.LOWER_PLATE_Y
    for i, (x, z) in enumerate(P.LOWER_EAR_SCREWS):
        screw(f"lp_ear_screw{i}", (x, ys, z), (0, -1, 0), M, r=2.8)
    for i, (x, z) in enumerate(P.LOWER_SCREWS):
        screw(f"lp_screw{i}", (x, ys, z), (0, -1, 0), M, r=2.5)


def servo(name, cx, cz, M, horiz=False):
    W, H = P.SERVO_FACE
    if horiz:
        W, H = H, W
    yf = P.LOWER_PLATE_Y - P.SERVO_PROUD
    D = P.SERVO_DEPTH
    box(name, (cx, yf + D / 2, cz), (W, D, H), M["servo"], bevel=1.0)
    # 底面のねじ 4 本
    for sx in (-1, 1):
        for sz in (-1, 1):
            screw(f"{name}_s{sx}{sz}", (cx + sx * (W / 2 - 2.6), yf, cz + sz * (H / 2 - 2.6)), (0, -1, 0), M, r=1.5)
    # 底面の浮き彫り（丸と弧）。ごく浅い
    u, v = (1, 0, 0), (0, 0, 1)
    if horiz:
        u, v = (0, 0, -1), (1, 0, 0)
    org = (cx, yf - 0.25, cz)
    Mb = basis(u, v, org)
    # 写真の刻印: 上に四角で囲んだ X 字、中央に凹んだ穴、下に弧
    plate(name + "_frame", [(-6, 9), (6, 9), (6, 18), (-6, 18)], 0.4, Mb, M["servo"],
          [[(-5.1, 9.9), (5.1, 9.9), (5.1, 17.1), (-5.1, 17.1)]], bevel=0.05)
    for k, (a, b) in enumerate((((-4.2, 10.6), (4.2, 16.4)), ((-4.2, 16.4), (4.2, 10.6)))):
        plate(f"{name}_x{k}", ribbon([a, b], 0.55), 0.4, Mb, M["servo"], bevel=0.05)
    cyl(name + "_hole", (cx, yf + 0.6, cz), (cx, yf - 0.05, cz), 1.6, M["dark"], n=16)
    arc = [(4.5 * math.cos(math.radians(a)), -8 + 2.5 * math.sin(math.radians(a))) for a in range(200, 341, 10)]
    plate(name + "_arc", ribbon(arc, 0.45), 0.4, Mb, M["servo"], bevel=0.05)


def servos(M):
    for i, (x, z) in enumerate(P.FINGER_SERVOS):
        servo(f"servo{i}", x, z, M)
    t = P.THUMB_SERVO_BODY
    cx, cz = (t["x0"] + t["x1"]) / 2, (t["z0"] + t["z1"]) / 2
    before = set(COLL.objects)
    box("thumb_servo", (cx, (t["y0"] + t["y1"]) / 2, cz), (t["x1"] - t["x0"], t["y1"] - t["y0"], t["z1"] - t["z0"]),
        M["servo"], bevel=1.0)
    # 取り付け耳
    box("thumb_servo_ear", (cx, t["y0"] + 4, cz), (t["x1"] - t["x0"] + 12, 2.5, 9), M["servo"], bevel=0.5)
    # ホーン（白いナイロン）
    sx, sz = P.THUMB_SERVO_SHAFT
    hx, hz = P.HORN_TIP
    yh = t["y0"] - 2.5
    cyl("horn_spline", (sx, t["y0"], sz), (sx, yh, sz), 3.2, M["nylon"])
    Mh = basis((1, 0, 0), (0, 0, 1), (0, yh - 1.2, 0))
    arm = ribbon([(sx, sz), (hx, hz)], [4.8, 3.2])
    holes = [circle((sx + (hx - sx) * f, sz + (hz - sz) * f), 1.0, 12) for f in (0.40, 0.52, 0.64, 0.76, 0.88)]
    cyl("horn_disc", (sx, yh - 0.5, sz), (sx, yh - 2.6, sz), 6.8, M["nylon"], n=32, bevel=0.4)
    plate("horn_arm", arm, 2.4, Mh, M["nylon"], holes, bevel=0.5)
    screw("horn_screw", (sx, yh - 2.7, sz), (0, -1, 0), M, r=2.4)
    # 写真ではサーボごと斜めに付いている。出力軸（Y 軸に平行）まわりに傾ける
    c = Vector((sx, 0, sz)) * MM
    Rt = Matrix.Translation(c) @ Matrix.Rotation(math.radians(-P.THUMB_SERVO_TILT), 4, "Y") @ Matrix.Translation(-c)
    bpy.context.view_layer.update()
    for ob in set(COLL.objects) - before:
        ob.matrix_world = Rt @ ob.matrix_world
    # 押し棒（黒）とボールリンク
    a = (Rt @ (Vector((hx, yh - 4.5, hz)) * MM)) / MM
    b = Vector((74.0, -36.0, 58.0))
    cyl("push_rod", a, b, 1.6, M["servo"], n=12)
    for k, p in enumerate((a, b)):
        cyl(f"ball_link{k}", p + Vector((0, 2.5, 0)), p - Vector((0, 2.5, 0)), 4.0, M["servo"], bevel=0.5)
        screw(f"ball_screw{k}", p - Vector((0, 2.5, 0)), (0, -1, 0), M, r=1.8)


def back_and_sides(M):
    b = P.BACK_PLATE
    xz_plate("back_plate", rrect(b["x0"], b["z0"], b["x1"], b["z1"], b["r"], 6), P.PALM_BACK_Y, P.ALU_T, M["alu"])
    yb = P.PALM_BACK_Y + P.ALU_T
    for i, (x, z) in enumerate(P.BACK_SCREWS_SMALL):
        screw(f"bp_screw{i}", (x, yb, z), (0, 1, 0), M, r=2.6, head="button")
    for i, (x, z) in enumerate(P.BACK_SCREWS_BIG):
        screw(f"bp_big{i}", (x, yb, z), (0, 1, 0), M, r=3.8, head="button")
    s = P.SIDE_WALL
    xl, xr = P.PALM_X
    n = P.SIDE_WALL_LITTLE_NOTCH
    little = [(n["y"], s["z0"]), (s["y1"], s["z0"]), (s["y1"], s["z1"]), (s["y0"], s["z1"]), (s["y0"], n["z"]),
              (n["y"], n["z"] - 6)]
    for k, x in enumerate((xl + ALU_T() / 2, xr - ALU_T() / 2)):
        Ms = basis((0, 1, 0), (0, 0, 1), (x, 0, 0))
        outline = little if k == 0 else rrect(s["y0"], s["z0"], s["y1"], s["z1"], 2, 4)
        plate(f"side_wall{k}", outline, ALU_T(), Ms, M["alu"])   # 側板は甲と同じ艶消しのアルミ
    # 内側の詰め物（すき間から白い背景が見えないように）
    lx = [x for x, _ in P.LOWER_PLATE]   # 手前のサーボ板より外へ出さない
    box("palm_core", ((min(lx) + max(lx)) / 2, -6, 72), (max(lx) - min(lx) - 4, 24, 100), M["dark"], bevel=0)


def wrist(M):
    f = P.FOOT
    Mf = basis((1, 0, 0), (0, 1, 0), (0, 0, f["z"] + f["t"] / 2))
    foot = circle((0, f["y"]), 30.0, 64)   # 写真の台座は円盤
    plate("foot", foot, f["t"], Mf, M["acrylic"], [circle((0, f["y"]), f["hole_r"], 20),
                                                  circle((-21, f["y"]), 2.0, 12), circle((21, f["y"]), 2.0, 12)])
    w = P.WRIST_BRACKET
    for k, y in enumerate((w["y_front"], w["y_back"])):
        xz_plate(f"wrist_plate{k}", rrect(w["x0"], w["z0"], w["x1"], w["z1"] + 4, 3), y, ALU_T(), M["alu"])
    box("wrist_block", (0, (w["y_front"] + w["y_back"]) / 2, (w["z0"] + w["z1"]) / 2 + 2),
        (w["x1"] - w["x0"] - 4, w["y_back"] - w["y_front"], w["z1"] - w["z0"] + 4), M["servo"], bevel=1)
    # 手首の U 字金具。手のひらの下端から後ろへ水平に伸び、背面に大穴と 4 つの小穴
    if P.WRIST_U_SHOW:
        u = P.WRIST_U
        wm = P.WRIST_MOUNT
        xz_plate("wrist_mount", rrect(u["x0"], u["z0"], u["x1"], wm["z1"], 6), wm["y"], u["y0"] - wm["y"], M["alu"])
        for i, (dx, z) in enumerate(((8, wm["z1"] - 7), (-8, wm["z1"] - 7))):
            screw(f"wrist_mount_screw{i}", ((u["x0"] + u["x1"]) / 2 + dx, u["y0"], z), (0, 1, 0), M, r=2.4, head="button")
        for k, x in enumerate((u["x0"], u["x1"] - P.ALU_T)):
            Mu = basis((0, 1, 0), (0, 0, 1), (x + P.ALU_T / 2, 0, 0))
            holes = [circle((u["hy"], u["hz"]), 6.0, 28)] + [circle((u["hy"] + dy, u["hz"] + dz), 1.4, 12)
                                                               for dy, dz in ((8, 8), (-8, 8), (8, -8), (-8, -8))]
            plate(f"wrist_u_side{k}", fillet([(u["y0"], u["z0"]), (u["y1"], u["z0"]), (u["y1"], u["z1"]), (u["y0"], u["z1"])], 10),
                  P.ALU_T, Mu, M["alu"], holes)
        cx = (u["x0"] + u["x1"]) / 2
        web_holes = [circle((cx, u["hz"]), 7.0, 32)] + [circle((cx + dx, u["hz"] + dz), 1.5, 12)
                                                       for dx, dz in ((9, 9), (-9, 9), (9, -9), (-9, -9))]
        xz_plate("wrist_u_web", rrect(u["x0"], u["z0"], u["x1"], u["z1"], 11), u["y1"] - P.ALU_T, P.ALU_T, M["alu"], web_holes)
        cyl("wrist_u_shaft", (cx, u["y1"] - 3, u["hz"]), (cx, u["y1"] - 0.6, u["hz"]), 5.0, M["servo"], n=32, bevel=0.4)
        cyl("wrist_u_hub", (u["x0"] - 3, u["hy"], u["hz"]), (u["x1"] + 3, u["hy"], u["hz"]), 5.2, M["servo"])
        box("wrist_servo", (cx, (u["y0"] + u["y1"]) / 2 - 1, u["hz"]), (u["x1"] - u["x0"] - 2 * P.ALU_T - 1, 20, 38),
            M["servo"], bevel=7.0)
    screw("wrist_screw0", (-15, w["y_front"], 0), (0, -1, 0), M, r=2.0)
    screw("wrist_screw1", (15, w["y_front"], 0), (0, -1, 0), M, r=2.0)


def ALU_T():
    return P.ALU_T


# ---- 指 ---------------------------------------------------------------
def axis_joint(name, c, ax, h_out, M, washer=True, r_bush=5.3, r_head=2.6):
    """軸 ax（単位ベクトル、カメラ側へ向く）の関節。c は軸の中心、h_out は中心から外面まで。"""
    c, ax = Vector(c), Vector(ax).normalized()
    out = c + ax * h_out
    inn = c - ax * h_out
    if washer:
        cyl(name + "_bush", out, out + ax * 1.6, r_bush, M["bushing"], n=24, bevel=0.5)
        out = out + ax * 1.6
        cyl(name + "_washer", out, out + ax * 0.9, r_head * 1.45, M["steel"], n=24, bevel=0.2)
        out = out + ax * 0.9
    screw(name + "_head", out, ax, M, r=r_head)
    nut(name + "_nut", inn, -ax, M, r=2.6, h=1.8)


def finger(name, fx, fz, lens, angs, M, fan=0.0):
    """指。面内座標 (p, q): p = 手のひら側へ、q = 上。指の板の面は鉛直軸まわりに FINGER_YAW だけ回す。"""
    y0 = P.FINGER_ROOT_Y
    t, g = P.FINGER_PLATE_T, P.FINGER_GAP
    yaw = math.radians(P.FINGER_YAW)
    R = Matrix.Rotation(math.radians(fan), 3, "Y") @ Matrix.Rotation(yaw, 3, "Z")
    ex = R @ Vector((1, 0, 0))          # 板の厚み方向（軸の向き）
    ep = R @ Vector((0, -1, 0))         # 曲がる向き
    ez = R @ Vector((0, 0, 1))
    O = Vector((fx, y0, fz)) - ez * fz   # 付け根の関節 (fx, y0, fz) を中心に扇に開く
    h = g / 2 + t                        # 軸の中心から板の外面まで
    pivots, dirs = [], []
    p0 = Vector((0.0, fz))
    phi = 0.0
    for L, a in zip(lens, angs):
        phi += math.radians(a)
        d = Vector((math.sin(phi), math.cos(phi)))
        pivots.append(p0.copy()); dirs.append(d)
        p0 = p0 + d * L

    def w2(seg, pp, qq):
        d = dirs[seg]
        n = Vector((d.y, -d.x))
        return pivots[seg] + n * pp + d * qq

    def to3(v2, dx=0.0):
        return O + ex * dx + ep * v2.x + ez * v2.y

    def frame(dx):
        return basis(tuple(ep), tuple(ez), tuple(O + ex * dx))  # n = ep × ez = -ex

    def seg_plates(nm, outline2, inner=False):
        """outer: 2 枚の板で挟む節。inner: 1 枚の板（外の節の間に入る）。関節で段差が見える。"""
        if inner:
            plate(f"{nm}_0", outline2, 2 * t + g - 3.0, frame(0.0), M["acrylic"], bevel=0.3)
        else:
            for k, dx in enumerate((-(g / 2 + t / 2), g / 2 + t / 2)):
                plate(f"{nm}_{k}", outline2, t, frame(dx), M["acrylic"], bevel=0.25)

    W = P.FINGER_W / 2
    base = ribbon([(0, fz - 20), (0, fz)], [W + 1.0, W + 0.5])
    seg_plates(f"{name}_base", base)
    for s in range(2):
        L = lens[s]
        c2 = [tuple(w2(s, -1.5 * math.sin(math.pi * i / 2), q)) for i, q in enumerate((0, L * 0.5, L))]
        seg_plates(f"{name}_seg{s}", ribbon(c2, [W + 0.5, W, W]) if s == 1 else ribbon(c2, [W, W, W - 0.5]),
                   inner=(s == 0))
    curl = math.radians(P.TIP_CURL)
    L = lens[2]
    pts, halfs = [], []
    n = 12
    cur = Vector((0.0, 0.0))
    for i in range(n + 1):
        pts.append(tuple(w2(2, cur.x, cur.y)))
        halfs.append(W * (0.86 - 0.3 * (i / n) ** 4))
        ang = curl * (i / n) ** 1.3
        cur = cur + Vector((math.sin(ang), math.cos(ang))) * (L / n)
    seg_plates(f"{name}_tip", ribbon(pts, halfs), inner=True)

    for s in range(3):
        a3 = to3(pivots[s])
        b3 = to3(pivots[s] + dirs[s] * lens[s] * (0.75 if s == 2 else 1.0))
        cyl(f"{name}_core{s}", a3, b3, 4.5, M["dark"], n=12)

    # 関節（カメラ側 = -ex 側にねじ頭）
    for s in range(3):
        axis_joint(f"{name}_j{s}", to3(pivots[s]), -ex, h, M)
    for s in range(2):
        axis_joint(f"{name}_m{s}", to3(w2(s, 0, lens[s] * 0.5)), -ex, h, M, washer=False, r_head=2.3)
    # 指先の止めねじ
    axis_joint(f"{name}_tipscrew", to3(w2(2, 1.5, L * 0.45)), -ex, h, M, washer=False, r_head=2.0)

    # 銀色のリンク（手の甲側 = -p 側、カメラ側の外面の外）
    dl = -(h + 1.6 + P.LINK_T / 2 + 0.3)   # カメラ側の外面（ブッシュの外）
    Ml = frame(dl)
    links = [
        (w2(0, -5.0, lens[0] * 0.55), w2(1, -5.0, 10.0), 1.5),
        (w2(1, -5.0, lens[1] * 0.55), w2(2, -5.0, 10.0), 1.5),
    ]
    for k, (a, b, sag) in enumerate(links):
        ap = arc_pts(a, b, sag)
        hw = [P.LINK_W / 2 * (1.0 - 0.35 * math.sin(math.pi * i / (len(ap) - 1))) for i in range(len(ap))]
        plate(f"{name}_link{k}", ribbon(ap, hw), P.LINK_T, Ml, M["link"], bevel=0.3)
        for e, pnt in enumerate((a, b)):   # 端は丸く広げる
            plate(f"{name}_link{k}_e{e}", circle(tuple(pnt), P.LINK_W / 2 + 1.0, 20), P.LINK_T, Ml, M["link"], bevel=0.3)
        for e, pnt in enumerate((a, b)):
            screw(f"{name}_link{k}_s{e}", to3(pnt, dl - P.LINK_T / 2), -ex, M, r=2.8)
    s_pts = [(-5.0, fz + 4), (-8.0, fz - 8), (-3.0, fz - 18), (-1.0, fz - 30)]
    plate(f"{name}_slink", ribbon(s_pts, P.LINK_W / 2), P.LINK_T, Ml, M["link"], bevel=0.3)
    plate(f"{name}_slink_e", circle(s_pts[-1], P.LINK_W / 2 + 1.0, 20), P.LINK_T, Ml, M["link"], bevel=0.3)
    screw(f"{name}_slink_s", to3(Vector(s_pts[-1]), dl - P.LINK_T / 2), -ex, M, r=2.6)
    # 板の手前の黒いナット受け
    box(f"{name}_slink_blk", tuple((to3(Vector(s_pts[-1]), dl * 0.5)) ), (7, 6, 7), M["servo"], bevel=0.8)


POSE = None   # None なら params の曲げ角、リストなら指ごとに差し替える


def fingers(M):
    for i, (nm, fx, fz, lens, angs) in enumerate(P.FINGERS):
        finger(nm, fx, fz, lens, POSE[i] if POSE else angs, M, P.FINGER_FAN[i])


def thumb(M):
    """親指。水平な板 2 枚を真鍮のスペーサーで繋ぐ。"""
    px, py = P.THUMB_PIVOT
    a = math.radians(P.THUMB_DIR)
    d = Vector((math.cos(a), math.sin(a)))
    nrm = Vector((-d.y, d.x))
    L1, L2 = P.THUMB_LEN
    o = Vector((px, py))
    # 付け根の金具（手のひらの横に立つ）
    # 付け根の縦軸の円筒ブッシュ（上下の支持板の間）
    cyl("thumb_root_bush", (px, py, P.THUMB_PLATES_Z[0] - 6), (px, py, P.THUMB_PLATES_Z[1] + 9), 6.5, M["bushing"], n=28, bevel=0.5)
    box("thumb_bracket", (px - 2, py + 2, 68), (8, 16, 32), M["acrylic"], bevel=0.6)
    for zi, z in enumerate(P.THUMB_PLATES_Z):
        Mz = basis((1, 0, 0), (0, 1, 0), (0, 0, z + 1.5))
        # 基節と中節を分ける（関節で 2 mm 空ける）
        mj = o + d * (L1 * 0.5)
        plate(f"thumb_prox{zi}", ribbon([tuple(o), tuple(mj - d * 1.0)], [8.5, 7.0]), 3.0, Mz, M["acrylic"])
        plate(f"thumb_mid{zi}", ribbon([tuple(mj + d * 1.0), tuple(o + d * L1)], [7.5, 6.5]), 3.0, Mz, M["acrylic"])
        # 根元の円弧の切り欠きのある円盤
        plate(f"thumb_root{zi}", fillet([tuple(o + Vector((math.cos(t_), math.sin(t_))) * 11.0)
                                          for t_ in [a + math.pi * (0.35 + 1.3 * i / 15) for i in range(16)]] + [tuple(o)], 2.0, 2),
              3.0, Mz, M["acrylic"])
        # 末節: 手のひら側へ反る
        b = o + d * L1
        pts = []
        cur = b.copy()
        ang = a
        for i in range(9):
            pts.append(tuple(cur))
            ang = a - math.radians(38) * (i / 8) ** 1.3
            cur = cur + Vector((math.cos(ang), math.sin(ang))) * (L2 / 8)
        # 末節は 30% の位置で関節を挟んで 2 つに分ける
        plate(f"thumb_tip{zi}", ribbon(pts[:6], [5.6, 6.0, 6.4, 6.6, 6.6, 6.4]), 3.0, Mz, M["acrylic"])
        plate(f"thumb_tip_end{zi}", ribbon(pts[5:], [5.2, 4.8, 4.3, 3.6]), 3.0, Mz, M["acrylic"])
        plate(f"thumb_knuckle{zi}", circle(pts[5], 8.0, 28), 3.0, Mz, M["acrylic"])
        tip_joint = Vector(pts[5])
    z0, z1 = P.THUMB_PLATES_Z
    # 真鍮のスペーサーと黒いスペーサー
    sp = o + d * (L1 - 6) + nrm * 3
    cyl("thumb_brass", (sp.x, sp.y, z0 + 3), (sp.x, sp.y, z1), 2.2, M["brass"], n=6)
    for k, pnt in enumerate((o, o + d * L1, o + d * L1 * 0.5)):
        cyl(f"thumb_spacer{k}", (pnt.x, pnt.y, z0 + 3), (pnt.x, pnt.y, z1), 3.4, M["bushing"], n=16)
        screw(f"thumb_s{k}", (pnt.x, pnt.y, z1 + 3), (0, 0, 1), M, r=2.4)
        screw(f"thumb_sb{k}", (pnt.x, pnt.y, z0), (0, 0, -1), M, r=2.4)
    screw("thumb_brass_s", (sp.x, sp.y, z1 + 3), (0, 0, 1), M, r=2.0)
    # 押し棒を受けるレバー
    lv = o + d * 18 - nrm * 9
    Mz = basis((1, 0, 0), (0, 1, 0), (0, 0, z0 + 1.5))
    plate("thumb_lever", ribbon([tuple(o), tuple(lv)], [6, 4]), 3.0, Mz, M["acrylic"])
    # 末節の銀リンク
    Mz2 = basis((1, 0, 0), (0, 1, 0), (0, 0, z1 + 3.0 + P.LINK_T / 2))
    la, lb = o + d * 10 + nrm * 6, o + d * (L1 + 12) + nrm * 2
    plate("thumb_link", ribbon(arc_pts(tuple(la), tuple(lb), 2.5), P.LINK_W / 2), P.LINK_T, Mz2, M["link"], bevel=0.3)
    lc = o + d * (L1 + 30) + nrm * (-4)
    la2 = o + d * (L1 * 0.5 + 8) - nrm * 6
    plate("thumb_link2", ribbon(arc_pts(tuple(la2), tuple(lc), -2.5), P.LINK_W / 2), P.LINK_T, Mz2, M["link"], bevel=0.3)
    for k, pnt in enumerate((la, lb, la2, lc)):
        plate(f"thumb_link_e{k}", circle(tuple(pnt), P.LINK_W / 2 + 1.0, 20), P.LINK_T, Mz2, M["link"], bevel=0.3)
        screw(f"thumb_link_s{k}", (pnt.x, pnt.y, z1 + 3.0 + P.LINK_T), (0, 0, 1), M, r=2.4)
    # 関節の黒いブッシュと銀の座金（上面に見える）
    for k, pnt in enumerate((o + d * (L1 * 0.5), o + d * L1, tip_joint)):
        cyl(f"thumb_jb{k}", (pnt.x, pnt.y, z1 + 3.0), (pnt.x, pnt.y, z1 + 5.0), 5.5, M["bushing"], n=24, bevel=0.4)
        cyl(f"thumb_jw{k}", (pnt.x, pnt.y, z1 + 5.0), (pnt.x, pnt.y, z1 + 5.8), 4.0, M["steel"], n=24, bevel=0.2)
        screw(f"thumb_jh{k}", (pnt.x, pnt.y, z1 + 5.8), (0, 0, 1), M, r=3.0)


# ======================================================================
def build():
    global COLL
    COLL = bpy.data.collections.new("uhand")
    bpy.context.scene.collection.children.link(COLL)
    M = materials()
    front_plates(M)
    servos(M)
    back_and_sides(M)
    wrist(M)
    fingers(M)
    before = set(COLL.objects)
    thumb(M)
    # 親指全体を付け根まわりに下へ傾ける
    a = math.radians(P.THUMB_DIR)
    axis = Vector((-math.sin(a), math.cos(a), 0))
    c = Vector((*P.THUMB_PIVOT, sum(P.THUMB_PLATES_Z) / 2)) * MM
    R = Matrix.Translation(c) @ Matrix.Rotation(math.radians(P.THUMB_PITCH), 4, axis) @ Matrix.Translation(-c)
    bpy.context.view_layer.update()   # 直前に scale を入れた物の matrix_world を確定させる
    for ob in set(COLL.objects) - before:
        ob.matrix_world = R @ ob.matrix_world
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
    # 色つきの GLB（viewer/uhand-camera.html で写真と重ねてカメラを合わせる）
    for ob in bpy.data.objects:
        ob.select_set(ob.name in COLL.objects)
    bpy.ops.export_scene.gltf(filepath=os.path.join(os.path.dirname(__file__), "../../exports/hiwonder-uhand.glb"),
                              export_format="GLB", use_selection=True, export_apply=True)
