# -*- coding: utf-8 -*-
"""卓上ゲームの図（実験環境の全景・各ゲームの写真）で共通に使う部品。

卓と椅子の形、木の材質、ゲームの配置（table-duo-vr の TableDuoSceneSetup.cs を移したもの）、光とカメラと Cycles の設定。
Unity の (x, y, z) は Blender の (x, z, y) に読み替える。人の席は -Y、手の席は +Y。
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.normpath(os.path.join(HERE, "..", ".."))
PROJ = os.path.normpath(os.path.join(ML, "..", ".."))
TP = os.path.join(PROJ, "Unity", "table-duo-vr", "Assets", "TableDuo", "ThirdParty")
GLTF_YAW = 180.0  # glTFast は X を反転して取り込む。Blender の取り込みとは Z まわりに 180 度違う

TOP = 0.75
HX, HY = 0.65, 0.35
SLAB = 0.034


def arg(name, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(name) + 1] if name in a else default


def flag(name):
    return "--" in sys.argv and name in sys.argv[sys.argv.index("--") + 1:]


def vec(name, default):
    return Vector(tuple(float(v) for v in arg(name, default).split(",")))


def bsdf_of(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def set_in(b, names, value):
    for nm in names:
        if nm in b.inputs:
            b.inputs[nm].default_value = value
            return


def world_bounds(objs):
    bpy.context.view_layer.update()
    mn = Vector((1e9,) * 3)
    mx = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn = Vector(map(min, mn, w))
            mx = Vector(map(max, mx, w))
    return mn, mx


def meshes_of(root):
    return [o for o in root.children_recursive if o.type == "MESH"]


# ---------------------------------------------------------------- GLB を卓に置く
GAME_OBJS = []


def glb(game, name, pos_xy, top, yaw=0.0, scale=1.0, face_down=False, tilt=None):
    """PlaceModelRealScale と同じ。外接箱の中心を pos、底面を top に合わせる。"""
    path = os.path.join(TP, game, "glb", name + ".glb")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(game + "_" + name, None)
    bpy.context.scene.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    rot = Matrix.Rotation(math.radians(-yaw + GLTF_YAW), 4, "Z")
    if face_down:
        rot = rot @ Matrix.Rotation(math.pi, 4, "X")
    if tilt is not None:
        rot = tilt @ rot
    root.matrix_world = rot @ Matrix.Scale(scale, 4)
    mn, mx = world_bounds(meshes_of(root))
    c = (mn + mx) / 2
    root.matrix_world = Matrix.Translation(Vector((pos_xy[0] - c.x, pos_xy[1] - c.y, top - mn.z))) @ root.matrix_world
    GAME_OBJS.extend(meshes_of(root))
    return root


def top_of(root):
    return world_bounds(meshes_of(root))[1].z


# ---------------------------------------------------------------- 材質
def flat_mat(name, rgb, rough=0.9, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = bsdf_of(m)
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    return m


def wood_mat(name="td_wood", light=(0.62, 0.50, 0.385), dark=(0.47, 0.36, 0.265), rough=0.40, coat=0.18,
             grain=1.0):
    """明るい木。木目は長辺（X）に沿って流れる。色の差は小さくして、駒より目立たせない。"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = bsdf_of(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.55, 9.0, 9.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = 3.2
    n1.inputs["Detail"].default_value = 9.0
    n1.inputs["Roughness"].default_value = 0.62
    n1.inputs["Distortion"].default_value = 1.3
    nt.links.new(mp.outputs[0], n1.inputs["Vector"])
    mp2 = nt.nodes.new("ShaderNodeMapping")
    mp2.inputs["Scale"].default_value = (1.2, 95.0, 95.0)
    nt.links.new(tc.outputs["Object"], mp2.inputs["Vector"])
    n2 = nt.nodes.new("ShaderNodeTexNoise")  # 細かい導管の筋
    n2.inputs["Scale"].default_value = 2.0
    n2.inputs["Detail"].default_value = 4.0
    nt.links.new(mp2.outputs[0], n2.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (*light, 1)
    nt.links.new(n1.outputs["Fac"], ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.inputs["Fac"].default_value = 0.22 * grain
    nt.links.new(ramp.outputs["Color"], mix.inputs["Color1"])
    nt.links.new(n2.outputs["Fac"], mix.inputs["Color2"])
    base = nt.nodes.new("ShaderNodeMixRGB")  # 木目の強さ（0 で無地）
    base.inputs["Fac"].default_value = min(1.0, grain)
    base.inputs["Color1"].default_value = (*[(a + c) / 2 for a, c in zip(light, dark)], 1)
    nt.links.new(mix.outputs["Color"], base.inputs["Color2"])
    nt.links.new(base.outputs["Color"], b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = rough - 0.05
    rr.inputs["To Max"].default_value = rough + 0.08
    nt.links.new(n2.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.06 * grain
    bump.inputs["Distance"].default_value = 0.002
    nt.links.new(n2.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    set_in(b, ("Coat Weight", "Coat"), coat)
    set_in(b, ("Coat Roughness",), 0.10)
    return m


# ---------------------------------------------------------------- 形
def rbox(name, loc, size, mat, bevel=0.004, seg=4):
    """角を丸めた箱。"""
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    if bevel > 0:
        bv = o.modifiers.new("bevel", "BEVEL")
        bv.width = bevel
        bv.segments = seg
        bv.limit_method = "ANGLE"
        wn = o.modifiers.new("wn", "WEIGHTED_NORMAL")
        wn.keep_sharp = False
        for p in o.data.polygons:
            p.use_smooth = True
    o.data.materials.append(mat)
    return o


def build_table(mat, leg_mat=None, legs=True, cx=0.0, cy=0.0, hx=HX, hy=HY, top=TOP):
    leg_mat = leg_mat or mat
    objs = [rbox("td_top", (cx, cy, top - SLAB / 2), (hx * 2, hy * 2, SLAB), mat, bevel=0.007, seg=5)]
    if legs:
        inset, lw = 0.055, 0.052
        for sx in (-1, 1):
            for sy in (-1, 1):
                objs.append(rbox("td_leg", (cx + sx * (hx - inset), cy + sy * (hy - inset), (top - SLAB) / 2),
                                 (lw, lw, top - SLAB), leg_mat, bevel=0.005))
        ah = 0.07
        for sy in (-1, 1):
            objs.append(rbox("td_apron", (cx, cy + sy * (hy - inset), top - SLAB - ah / 2),
                             ((hx - inset) * 2 - lw, 0.022, ah), leg_mat, bevel=0.002))
        for sx in (-1, 1):
            objs.append(rbox("td_apron", (cx + sx * (hx - inset), cy, top - SLAB - ah / 2),
                             (0.022, (hy - inset) * 2 - lw, ah), leg_mat, bevel=0.002))
    return objs


def build_chair(mat, pos_xy, seat=0.47, yaw=0.0, back=True):
    """座面と 4 本の脚と背。yaw=0 で +Y を向く。"""
    x, y = pos_xy
    w, d, t = 0.43, 0.42, 0.030
    parts = [rbox("ch_seat", (0, 0, seat - t / 2), (w, d, t), mat, bevel=0.008, seg=5)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = seat - t if sy > 0 or not back else seat - t
            parts.append(rbox("ch_leg", (sx * (w / 2 - 0.03), sy * (d / 2 - 0.03), h / 2), (0.034, 0.034, h), mat,
                              bevel=0.004))
    if back:
        bh = 0.40
        for sx in (-1, 1):
            parts.append(rbox("ch_post", (sx * (w / 2 - 0.03), -(d / 2 - 0.03), seat + bh / 2 - 0.01),
                              (0.034, 0.030, bh), mat, bevel=0.004))
        parts.append(rbox("ch_back", (0, -(d / 2 - 0.03), seat + bh - 0.085), (w - 0.06, 0.020, 0.15), mat,
                          bevel=0.006))
    root = bpy.data.objects.new("chair", None)
    bpy.context.scene.collection.objects.link(root)
    for p in parts:
        p.parent = root
    root.matrix_world = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    return root, parts


# ---------------------------------------------------------------- 光・カメラ・描画
def light(name, kind, loc, energy, size=1.0, target=(0, 0, TOP), color=(1, 1, 1), size_y=None, spot=None,
          spread=None, blend=1.0):
    sc = bpy.context.scene
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == "AREA":
        ld.size = size
        if size_y:
            ld.shape = "RECTANGLE"
            ld.size_y = size_y
        if spread is not None:
            ld.spread = math.radians(spread)
    if kind == "SPOT":
        ld.spot_size = math.radians(spot or 40)
        ld.spot_blend = blend
        ld.shadow_soft_size = size
    lo = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return lo


def only(lo, objs, name):
    """この光を objs だけに当てる。"""
    col = bpy.data.collections.new(name)
    for o in objs:
        col.objects.link(o)
    lo.light_linking.receiver_collection = col


def world(rgb, strength):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (*rgb, 1)
    bg.inputs[1].default_value = strength
    return w


def camera(loc, look, lens, fstop=0.0, focus=None, ortho=None, sensor=36.0):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cd.sensor_width = sensor
    loc, look = Vector(loc), Vector(look)
    cam.location = loc
    cam.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    else:
        cd.lens = lens
    if fstop > 0:
        cd.dof.use_dof = True
        cd.dof.focus_distance = (Vector(focus if focus is not None else look) - loc).length
        cd.dof.aperture_fstop = fstop
        cd.dof.aperture_blades = 9
    return cam


def setup_render(tag, size, samples=256, engine="cycles", exposure=0.0, look="AgX - Base Contrast", bounces=8):
    sc = bpy.context.scene
    if engine == "cycles":
        sc.render.engine = "CYCLES"
        prefs = bpy.context.preferences.addons["cycles"].preferences
        dev = "CPU"
        for kind in ("OPTIX", "CUDA", "HIP", "ONEAPI"):
            try:
                prefs.compute_device_type = kind
                prefs.get_devices()
                gpus = [d for d in prefs.devices if d.type == kind]
                if gpus:
                    for d in prefs.devices:
                        d.use = d.type == kind
                    dev = "GPU"
                    print(f"[{tag}] cycles device", kind, [d.name for d in gpus])
                    break
            except Exception:
                pass
        sc.cycles.device = dev
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = bounces
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.adaptive_threshold = 0.01
        try:
            sc.cycles.denoiser = "OPTIX" if dev == "GPU" else "OPENIMAGEDENOISE"
            sc.cycles.denoiser = "OPENIMAGEDENOISE"
        except TypeError:
            pass
    else:
        for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                sc.render.engine = eng
                break
            except TypeError:
                pass
        sc.eevee.taa_render_samples = min(samples, 64)
        for attr in ("use_shadows", "use_gtao", "use_raytracing"):
            try:
                setattr(sc.eevee, attr, True)
            except Exception:
                pass
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = look
    except TypeError as e:
        print(f"[{tag}] view", e)
    sc.view_settings.exposure = exposure
    w, h = (int(v) for v in size.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"


def render(tag, out):
    sc = bpy.context.scene
    out = os.path.abspath(out)  # 相対のまま渡すと Blender がドライブの根から解釈する
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print(f"[{tag}] wrote", out)


# ---------------------------------------------------------------- ゲームの配置
def serpentine(cx, z_start, z_end, usable_half_x, count, step):
    """SampleSerpentine の移植。戻り値は (x, y) の列。"""
    per_row = 8
    rows = math.ceil(count / per_row)

    def pitch(rows):
        return min(0.10, (z_start - z_end) / (rows - 1)) if rows > 1 else 0.10

    row_pitch = pitch(rows)
    turn_r = row_pitch * 0.5
    row_half = (per_row - 1) * step * 0.5
    while row_half + turn_r > usable_half_x and per_row > 4:
        per_row -= 1
        rows = math.ceil(count / per_row)
        row_pitch = pitch(rows)
        turn_r = row_pitch * 0.5
        row_half = (per_row - 1) * step * 0.5
    poly = []
    for r in range(rows):
        z = z_start - r * row_pitch
        ltr = r % 2 == 0
        xa = -row_half if ltr else row_half
        xb = -xa
        for i in range(33):
            poly.append((xa + (xb - xa) * i / 32, z))
        if r == rows - 1:
            break
        sgn = 1 if ltr else -1
        for i in range(1, 24):
            a = math.pi * 0.5 - math.pi * (i / 24)
            poly.append((xb + sgn * turn_r * math.cos(a), z - turn_r + turn_r * math.sin(a)))
    pts = [(cx + poly[0][0], poly[0][1])]
    last = poly[0]
    for i in range(1, len(poly)):
        if len(pts) >= count:
            break
        a, b = poly[i - 1], poly[i]
        seg = math.dist(a, b)
        sub = max(1, math.ceil(seg / 0.004))
        for s in range(1, sub + 1):
            if len(pts) >= count:
                break
            t = s / sub
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            if math.dist(last, p) >= step:
                pts.append((cx + p[0], p[1]))
                last = p
    return pts


def place_dsa(top=TOP, cx=0.0, cy=0.0, hx=HX, hy=HY, edge=0.07, staged=True):
    """海底探検。staged なら、遊んでいる途中の形にする（駒が道の上にいて、取られた所に裏トークンが入る）。"""
    G = "DeepSeaAdventure"
    CHIP = 1.6
    chain = []
    for lvl in (["tri_0", "tri_1", "tri_2", "tri_3"], ["sq_4", "sq_5", "sq_6", "sq_7"],
                ["pen_8", "pen_9", "pen_10", "pen_11"], ["hex_12", "hex_13", "hex_14", "hex_15"]):
        chain += lvl + lvl
    pts = serpentine(cx, cy + (hy - edge) - 0.18, cy - (hy - edge) + 0.05, hx - edge - 0.05, len(chain), 0.070)
    taken = {5: None, 11: None} if staged else {}
    for i, name in enumerate(chain):
        if i < len(pts) - 1:
            d = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        else:
            d = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        yaw = 0.0 if i == 0 else 180 + math.degrees(math.atan2(d[0], d[1]))
        if i in taken:
            glb(G, "back_circle", pts[i], top, scale=CHIP)
            taken[i] = name
        else:
            glb(G, name, pts[i], top, yaw=yaw, scale=CHIP, face_down=True)
    board_y = pts[0][1] + 0.022 + 0.008 + 0.043
    glb(G, "submarine_board", (pts[0][0], board_y), top, yaw=180)
    for s in range(2):
        x = cx - (hx - edge - 0.05) + s * 0.075
        y0 = cy - (hy - edge - 0.06)
        z = top
        for k in range(9 if staged else 10):
            r = glb(G, "back_circle", (x, y0), z, scale=CHIP)
            mn, mx = world_bounds(meshes_of(r))
            z += max(0.004, mx.z - mn.z)
    side_x = cx + (hx - edge - 0.06)
    if staged:
        glb(G, "meeple_purple", (pts[7][0] + 0.004, pts[7][1] - 0.004), top + 0.0065, yaw=20, scale=1.6)
        glb(G, "meeple_red", (pts[13][0], pts[13][1] + 0.003), top + 0.0065, yaw=-30, scale=1.6)
        # 取ったチップは、取った人の手前に伏せて置く
        glb(G, taken[5], (cx + 0.34, cy - hy + 0.085), top, yaw=12, scale=CHIP, face_down=True)
        glb(G, taken[11], (cx - 0.05, cy + hy - 0.075), top, yaw=200, scale=CHIP, face_down=True)
        glb(G, "die", (side_x - 0.115, cy + 0.035), top, yaw=18, scale=1.5)
        glb(G, "die", (side_x - 0.060, cy - 0.020), top, yaw=62, scale=1.5)
    else:
        glb(G, "meeple_purple", (side_x - 0.09, board_y), top, scale=1.6)
        glb(G, "meeple_red", (side_x - 0.02, board_y), top, scale=1.6)
        glb(G, "die", (side_x - 0.09, board_y - 0.09), top, scale=1.5)
        glb(G, "die", (side_x - 0.02, board_y - 0.09), top, yaw=35, scale=1.5)
    glb(G, "air_marker", (side_x + 0.02, board_y), top, scale=CHIP * 0.8)
    return pts


def place_algo(top=TOP, cx=0.0, cy=0.0, staged=True):
    """アルゴ。山札 16 枚と、各席の手前に手札 4 枚。staged なら当てられた札を表にする。"""
    G = "Algo"
    S = 1.3
    rng = random.Random(20260718)
    names = [f"white_{v}" for v in range(12)] + [f"black_{v}" for v in range(12)]
    rng.shuffle(names)

    def key(n):
        c, v = n.split("_")
        return int(v) * 2 + (1 if c == "white" else 0)

    near = sorted(names[:4], key=key)
    far = sorted(names[4:8], key=key)
    deck = names[8:]
    open_near = {1, 2} if staged else set()
    open_far = {0} if staged else set()
    for i, n in enumerate(near):
        op = i in open_near  # 表の札は、持ち主から読める向きにする
        glb(G, n, (cx + (i - 1.5) * 0.065, cy - 0.24), top, yaw=180 if op else 0, scale=S, face_down=not op)
    for i, n in enumerate(far):  # 手の席から見て左から小さい順
        op = i in open_far
        glb(G, n, (cx - (i - 1.5) * 0.065, cy + 0.24), top, yaw=0 if op else 180, scale=S, face_down=not op)
    n_deck = 14 if staged else 16
    for i in range(n_deck):
        j = (rng.random() - 0.5) * (5.0 if staged else 0.0)
        glb(G, deck[i], (cx - 0.12 + (rng.random() - 0.5) * 0.002, cy + (rng.random() - 0.5) * 0.002),
            top + i * 0.0030, yaw=90 + j, scale=S, face_down=True)
    if staged:  # 山から引いた札を、当てにいく側が手元に伏せて持つ
        glb(G, deck[14], (cx + 0.045, cy - 0.105), top, yaw=-14, scale=S, face_down=True)


def place_geister(top=TOP, cx=0.0, cy=0.0, staged=True, captured_off=False):
    """ガイスター。盤と、各席 8 体の駒。staged なら数手進んだ形にして、取られた駒を盤の外に置く。"""
    G = "Geister"
    board = glb(G, "geister", (cx, cy), top, yaw=0)
    mn, mx = world_bounds(meshes_of(board))
    btop = mx.z + 0.0005
    pitch = (mx.x - mn.x) / 6
    cols = (-1.5, -0.5, 0.5, 1.5)
    moves ={(0, 5): (-0.5, -0.5), (0, 7): (2.5, -1.5), (1, 4): (-1.5, 0.5)} if staged else {}
    captured = {(1, 6): (cx + 0.5 * pitch, cy - 3 * pitch - 0.055, 205.0),
                (0, 4): (cx - 0.6 * pitch, cy + 3 * pitch + 0.055, 20.0)} if staged else {}
    if captured_off:  # 集合写真では盤の前後に場所が無いので、取られた駒は置かない
        captured = {k: None for k in captured}
    for seat in range(2):
        yaw = 180.0 if seat == 0 else 0.0
        for i in range(8):
            col, row = i % 4, i // 4
            x = cx + cols[col] * pitch
            y = cy + (-1 if seat == 0 else 1) * (2.5 - row) * pitch
            blue = ((col + row + seat) % 2) == 0
            z, yw = btop, yaw
            if (seat, i) in moves:
                gx, gy = moves[(seat, i)]
                x, y = cx + gx * pitch, cy + gy * pitch
            if (seat, i) in captured:
                if captured[(seat, i)] is None:
                    continue
                x, y, yw = captured[(seat, i)]
                z = top
            glb(G, "ghost_blue" if blue else "ghost_red", (x, y), z, yaw=yw, scale=1.6)
    return pitch


def place_bandido(top=TOP, cx=0.0, cy=0.0, hx=HX, staged=True, laid=None, deck_x=None, deck_y=0.0):
    """バンディド。中央に開始札、各席の手前に表向きの手札 3 枚、+X の端に裏向きの山札。"""
    G = "Bandido"
    S = 0.8
    p = 0.044 * S
    rng = random.Random(20260722)
    laid = laid or []
    used = {n for n, *_ in laid}
    g = [f"g{i}" for i in range(1, 25) if f"g{i}" not in used]
    l = [f"l{i}" for i in range(1, 8) if f"l{i}" not in used]
    rng.shuffle(g)
    rng.shuffle(l)
    glb(G, "bandy", (cx, cy), top, yaw=90, scale=S)
    step = p + 0.0098
    hand0 = [l.pop(), g.pop(), g.pop()]
    hand1 = [g.pop(), g.pop(), g.pop()]
    for i, n in enumerate(hand0):
        glb(G, n, (cx + (i - 1) * step, cy - 0.24), top, yaw=0, scale=S)
    for i, n in enumerate(hand1):
        glb(G, n, (cx + (i - 1) * step, cy + 0.24), top, yaw=180, scale=S)
    rest = g + l
    rng.shuffle(rest)
    for name, gx, gy, yaw in laid:  # 置いた札（格子の単位は短辺 p）
        glb(G, name, (cx + gx * p, cy + gy * p), top, yaw=yaw, scale=S)
    dx = deck_x if deck_x is not None else hx - 0.07
    for i, n in enumerate(rest):
        j = (rng.random() - 0.5) * (4.0 if staged else 0.0)
        glb(G, n, (cx + dx, cy + deck_y), top + i * 0.0016, yaw=j, scale=S, face_down=True)


def place_bear(top=TOP, cx=0.0, cy=0.0, drawing=None):
    """あと6画のくま。中央に描画パッド、+X にお題カード 12 枚、各席の手前に役割カードとトークンとペン。"""
    G = "SixStrokesBear"
    T, M = 1.6, 1.3
    pad = glb(G, "drawing_pad", (cx, cy), top, yaw=0)
    rows = (("prompt_01_sleepy", "prompt_02_cold", "prompt_03_hungry", "prompt_04_surprised"),
            ("prompt_05_waiting", "prompt_06_troubled", "prompt_07_attention", "prompt_08_joy"),
            ("prompt_09_hiding", "prompt_10_brave", "prompt_11_awkward", "prompt_12_make_up"))
    for r, row in enumerate(rows):
        for c, n in enumerate(row):
            glb(G, n, (cx + 0.33 + (c - 1.5) * 0.11, cy + (r - 1) * 0.09), top, yaw=270)
    s0, s1 = cy - 0.26, cy + 0.26
    glb(G, "role_circle", (cx - 0.16, s0), top, yaw=0)
    glb(G, "stroke_circle", (cx - 0.02, s0), top, yaw=0, scale=T)
    glb(G, "stroke_circle", (cx + 0.05, s0), top, yaw=0, scale=T)
    glb(G, "stroke_oval", (cx + 0.12, s0), top, yaw=0, scale=T)
    mk0 = glb(G, "marker_circle", (cx + 0.28, s0), top, yaw=90, scale=M)
    glb(G, "role_segment", (cx + 0.16, s1), top, yaw=180)
    glb(G, "stroke_straight", (cx + 0.02, s1), top, yaw=180, scale=T)
    glb(G, "stroke_straight", (cx - 0.05, s1), top, yaw=180, scale=T)
    glb(G, "stroke_bend", (cx - 0.12, s1), top, yaw=180, scale=T)
    mk1 = glb(G, "marker_segment", (cx - 0.28, s1), top, yaw=90, scale=M)
    glb(G, "timer_3min", (cx - 0.20, cy), top, yaw=0)
    glb(G, "achievement_card", (cx - 0.40, cy - 0.14), top, yaw=0)
    for z in (-0.07, 0.0, 0.07):
        glb(G, "achievement_token", (cx - 0.52, cy + z), top, yaw=0, scale=T)
    glb(G, "rule_card", (cx - 0.40, cy + 0.14), top, yaw=90)
    # 消しゴム（本体とスリーブ）
    eb = rbox("bear_eraser", (cx - 0.20, cy - 0.12, top + 0.011), (0.060, 0.032, 0.022),
              flat_mat("eraser_body", (1.0, 1.0, 0.97), 0.6), bevel=0.003)
    es = rbox("bear_eraser_sleeve", (cx - 0.20, cy - 0.12, top + 0.012), (0.026, 0.034, 0.024),
              flat_mat("eraser_sleeve", (0.020, 0.056, 0.069), 0.5), bevel=0.0015)
    GAME_OBJS.extend([eb, es])
    if drawing:
        _paint(pad, (cx, cy), drawing)
    return pad, mk0, mk1


def place_all(top=TOP, drawing=None):
    """5 つのゲームを 1 つの卓に集める（集合写真用。実際の配置ではない）。
    奥の列は左から あと6画のくま・ガイスター・海底探検、手前の列は左から くまのトークン・アルゴ・バンディド。"""
    rng = random.Random(11)
    # --- あと6画のくま（左）
    B = "SixStrokesBear"
    pad = glb(B, "drawing_pad", (-0.47, 0.10), top, yaw=0)
    if drawing:
        _paint(pad, (-0.47, 0.10), drawing)
    glb(B, "timer_3min", (-0.315, 0.235), top, yaw=25)
    glb(B, "marker_circle", (-0.455, -0.095), top, yaw=96, scale=1.3)
    glb(B, "marker_segment", (-0.315, -0.175), top, yaw=14, scale=1.3)
    for n, x, y in (("stroke_circle", -0.590, -0.170), ("stroke_circle", -0.510, -0.165), ("stroke_oval", -0.430, -0.172),
                    ("stroke_straight", -0.555, -0.262), ("stroke_straight", -0.475, -0.268), ("stroke_bend", -0.395, -0.260)):
        glb(B, n, (x, y), top, yaw=rng.uniform(-10, 10), scale=1.6)
    glb(B, "prompt_08_joy", (-0.312, 0.085), top, yaw=262)
    glb(B, "prompt_03_hungry", (-0.305, 0.012), top + 0.0006, yaw=281)
    # --- ガイスター（中央の奥）
    place_geister(top=top, cx=-0.065, cy=0.125, staged=True, captured_off=True)
    # --- 海底探検（右の奥）
    D = "DeepSeaAdventure"
    glb(D, "submarine_board", (0.305, 0.275), top, yaw=180)
    chain = ["tri_0", "tri_1", "tri_2", "tri_3", "tri_0", "sq_4", "sq_5", "sq_6", "sq_7", "sq_4",
             "pen_8", "pen_9", "pen_10", "pen_11", "hex_12", "hex_13", "hex_14"]
    pts = [(0.445 + 0.068 * i, 0.275 - 0.012 * i) for i in range(3)]
    pts += [(0.60 - 0.068 * i, 0.165 + 0.004 * i) for i in range(6)]
    pts += [(0.225 + 0.068 * i, 0.075 - 0.004 * i) for i in range(6)]
    pts += [(0.585 - 0.068 * i, -0.02) for i in range(2)]
    for i, (n, pt) in enumerate(zip(chain, pts)):
        if i == 7:
            glb(D, "back_circle", pt, top, scale=1.6)
        else:
            glb(D, n, pt, top, yaw=rng.uniform(0, 360), scale=1.6, face_down=True)
    glb(D, "meeple_red", pts[5], top + 0.0065, yaw=30, scale=1.6)
    glb(D, "meeple_purple", pts[10], top + 0.0065, yaw=-20, scale=1.6)
    glb(D, "die", (0.475, -0.070), top, yaw=20, scale=1.5)
    glb(D, "die", (0.520, -0.100), top, yaw=65, scale=1.5)
    # --- アルゴ（手前の中央）
    A = "Algo"
    for i, (n, op) in enumerate((("black_2", False), ("white_4", True), ("white_6", True), ("black_9", False))):
        glb(A, n, (-0.2 + i * 0.066, -0.245), top, yaw=180 if op else 0, scale=1.3, face_down=not op)
    deck = ["white_1", "black_7", "white_10", "black_0", "white_3", "black_11", "white_8", "black_5"]
    for i, n in enumerate(deck):
        glb(A, n, (0.09 + rng.uniform(-0.001, 0.001), -0.215), top + i * 0.0030, yaw=90 + rng.uniform(-3, 3), scale=1.3,
            face_down=True)
    # --- バンディド（手前の右）
    G = "Bandido"
    p = 0.044 * 0.8
    bx, by = 0.335, -0.195
    glb(G, "bandy", (bx, by), top, yaw=90, scale=0.8)
    for n, gx, gy, yaw in (("g20", 2, 0, 90), ("g11", -0.5, 1.5, 0), ("g4", 0.5, 1.5, 0), ("g24", -0.5, -1.5, 0)):
        glb(G, n, (bx + gx * p, by + gy * p), top, yaw=yaw, scale=0.8)
    names = [f"g{i}" for i in range(1, 25) if i not in (20, 11, 4, 24)]
    for i, n in enumerate(names[:14]):
        glb(G, n, (0.555, -0.215), top + i * 0.0016, yaw=8 + rng.uniform(-2.5, 2.5), scale=0.8, face_down=True)
    glb(G, "l2", (0.49, -0.30), top, yaw=75, scale=0.8)


def _paint(pad, xy, drawing):
    """パッドの上に、描きかけの絵（透明の地に線だけの画像）を載せる。"""
    ptop = top_of(pad)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(xy[0], xy[1], ptop + 0.0003))
    q = bpy.context.active_object
    q.name = "bear_paint"
    q.scale = (0.210, 0.297, 1)
    m = bpy.data.materials.new("bear_paint")
    m.use_nodes = True
    b = bsdf_of(m)
    ti = m.node_tree.nodes.new("ShaderNodeTexImage")
    ti.image = bpy.data.images.load(drawing, check_existing=True)
    m.node_tree.links.new(ti.outputs["Color"], b.inputs["Base Color"])
    m.node_tree.links.new(ti.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.55
    q.data.materials.append(m)
    q.visible_shadow = False
    GAME_OBJS.append(q)


PLACERS = {"all": place_all, "dsa": place_dsa, "algo": place_algo, "geister": place_geister, "bandido": place_bandido,
           "bear": place_bear}
