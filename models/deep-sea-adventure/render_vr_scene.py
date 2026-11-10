# -*- coding: utf-8 -*-
"""VR の卓で、人（Remy）と uHand が海底探検を囲む場面を描く。

卓・椅子・駒の配置は table-duo-vr の TableDuoSceneSetup.cs（PlaceDeepSeaAdventure / SampleSerpentine /
PlaceBlankStacks）をそのまま移した。Unity の (x, y, z) は Blender の (x, z, y) に読み替える。

blender --background --python models/deep-sea-adventure/render_vr_scene.py -- [--out PATH] [--size 1600x900]
    [--top]   卓を真上から撮る（配置の確認用）
    [--samples N]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ML, "models", "hiwonder-uhand"))

import bpy
from mathutils import Matrix, Vector

import anim_build as AB
import anim_lib

PROJ = os.path.normpath(os.path.join(ML, "..", ".."))
TD = os.path.join(PROJ, "Unity", "table-duo-vr", "Assets")
DSA = os.path.join(TD, "TableDuo", "ThirdParty", "DeepSeaAdventure", "glb")
KENNEY = os.path.join(PROJ, "Unity", "table-duo-vr", "Assets", "ThirdParty", "Kenney", "Furniture")
REMY = os.path.join(PROJ, "Unity", "fixed-cam-vr", "Assets", "ThirdParty", "Mixamo", "Remy.fbx")
REMY_TEX = os.path.join(PROJ, "Unity", "fixed-cam-vr", "Assets", "Editor", "VirtualWalkAssets")

# glTFast は glTF の X を反転して取り込む。Blender の glTF 取り込みとは Z 軸まわりに 180 度違う
GLTF_YAW = 180.0


def arg(name, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(name) + 1] if name in a else default


def flag(name):
    return "--" in sys.argv and name in sys.argv[sys.argv.index("--") + 1:]


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


def import_root(importer, path):
    """取り込んだ物を 1 つの空の親にまとめて返す。"""
    before = set(bpy.data.objects)
    importer(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(os.path.basename(path), None)
    bpy.context.scene.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    return root, new


def meshes_of(root):
    return [o for o in root.children_recursive if o.type == "MESH"]


def place(root, pos_xy, top, yaw=0.0, scale=1.0, face_down=False):
    """PlaceModelRealScale と同じ。外接箱の中心を pos、底面を top に合わせる。"""
    rot = Matrix.Rotation(math.radians(-yaw + GLTF_YAW), 4, "Z")
    if face_down:
        rot = rot @ Matrix.Rotation(math.pi, 4, "X")
    root.matrix_world = rot @ Matrix.Scale(scale, 4)
    mn, mx = world_bounds(meshes_of(root))
    c = (mn + mx) / 2
    root.matrix_world = Matrix.Translation(Vector((pos_xy[0] - c.x, pos_xy[1] - c.y, top - mn.z))) @ root.matrix_world


def glb(name, *a, **k):
    root, _ = import_root(bpy.ops.import_scene.gltf, os.path.join(DSA, name + ".glb"))
    place(root, *a, **k)
    return root


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


# ---------------------------------------------------------------- uHand
arm_h, rest_h = AB.rig()
_pose = dict(anim_lib.load_poses()["point"])
if arg("--pose"):  # 例: --pose index=0,middle=0.45
    _pose.update({k: float(v) for k, v in (kv.split("=") for kv in arg("--pose").split(","))})
AB.apply_pose(arm_h, rest_h, _pose)
bpy.context.view_layer.update()
uh_objs = [o for o in bpy.data.objects if o.name.startswith("uh_")]

# ---------------------------------------------------------------- 卓と椅子（Kenney）
TABLE_TOP = 0.75


def load_ascii_fbx(path):
    """Kenney の ASCII FBX（メッシュ 1 個・材質 1 個）を読む。Blender の取り込みは ASCII を受け付けない。"""
    import re
    txt = open(path, encoding="utf-8", errors="replace").read()

    def arr(key):
        m = re.search(key + r": \*\d+ \{\s*a: ([^}]*)\}", txt)
        return [float(v) for v in m.group(1).replace("\n", "").split(",") if v.strip()]

    v = arr("Vertices")
    idx = [int(x) for x in arr("PolygonVertexIndex")]
    verts = [(v[i], -v[i + 2], v[i + 1]) for i in range(0, len(v), 3)]  # FBX の Y 上 → Blender の Z 上
    faces, cur = [], []
    for k in idx:
        if k < 0:
            cur.append(-k - 1)
            faces.append(cur)
            cur = []
        else:
            cur.append(k)
    col = re.findall(r'"DiffuseColor", "Color", "", "A",([\d.]+),([\d.]+),([\d.]+)', txt)[-1]
    name = os.path.splitext(os.path.basename(path))[0]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    mat = bpy.data.materials.new(name + "_mat")
    mat.use_nodes = True
    b = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*[float(c) for c in col], 1)
    b.inputs["Roughness"].default_value = 0.65
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    root = bpy.data.objects.new(name + "_root", None)
    sc_ = bpy.context.scene.collection
    sc_.objects.link(ob)
    sc_.objects.link(root)
    ob.parent = root
    return root


def fit_height(path, pos_xy, yaw, target_h, max_w, stretch=False):
    root = load_ascii_fbx(path)
    root.matrix_world = Matrix.Rotation(math.radians(-yaw), 4, "Z")
    mn, mx = world_bounds(meshes_of(root))
    size = mx - mn
    s = target_h / size.z
    if max(size.x, size.y) * s > max_w:
        s = max_w / max(size.x, size.y)
    sz = target_h / size.z if stretch else s
    root.matrix_world = Matrix.Diagonal((s, s, sz, 1)) @ root.matrix_world
    mn, mx = world_bounds(meshes_of(root))
    c = (mn + mx) / 2
    root.matrix_world = Matrix.Translation(Vector((pos_xy[0] - c.x, pos_xy[1] - c.y, -mn.z))) @ root.matrix_world
    return root


table = fit_height(os.path.join(KENNEY, "table.fbx"), (0, 0), 0, TABLE_TOP, 1.3, stretch=True)
tmn, tmx = world_bounds(meshes_of(table))
if (tmx - tmn).y > (tmx - tmn).x:  # 長辺を X（人と手を結ぶ線に直交）へ
    table.matrix_world = Matrix.Rotation(math.pi / 2, 4, "Z") @ table.matrix_world
    tmn, tmx = world_bounds(meshes_of(table))
top = tmx.z
cx, cy = (tmn.x + tmx.x) / 2, (tmn.y + tmx.y) / 2
hx, hy = (tmx.x - tmn.x) / 2, (tmx.y - tmn.y) / 2
EDGE = 0.07
print(f"[scene] table top={top:.3f} half=({hx:.3f},{hy:.3f})")
chair0 = fit_height(os.path.join(KENNEY, "chair.fbx"), (0, -0.61), 0, 0.85, 0.55)
chair1 = fit_height(os.path.join(KENNEY, "chair.fbx"), (0, 0.61), 180, 0.85, 0.55)

# ---------------------------------------------------------------- 海底探検（PlaceDeepSeaAdventure）
CHIP = 1.6
chain = []
for lvl in (["tri_0", "tri_1", "tri_2", "tri_3"], ["sq_4", "sq_5", "sq_6", "sq_7"],
            ["pen_8", "pen_9", "pen_10", "pen_11"], ["hex_12", "hex_13", "hex_14", "hex_15"]):
    chain += lvl + lvl
step = 0.070
z_start = cy + (hy - EDGE) - 0.18
z_end = cy - (hy - EDGE) + 0.05
pts = serpentine(cx, z_start, z_end, hx - EDGE - 0.05, len(chain), step)
for i, name in enumerate(chain):
    if i < len(pts) - 1:
        d = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
    else:
        d = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
    yaw = 0.0 if i == 0 else 180 + math.degrees(math.atan2(d[0], d[1]))
    glb(name, pts[i], top, yaw=yaw, scale=CHIP, face_down=True)

board_y = pts[0][1] + 0.022 + 0.008 + 0.043
glb("submarine_board", (pts[0][0], board_y), top, yaw=180)

# 裏トークン 20 枚を 2 山（人の側の左）
for s in range(2):
    x = cx - (hx - EDGE - 0.05) + s * 0.075
    y0 = cy - (hy - EDGE - 0.06)
    z = top
    for k in range(10):
        r = glb("back_circle", (x, y0), z, scale=CHIP)
        mn, mx = world_bounds(meshes_of(r))
        z += max(0.004, mx.z - mn.z)

side_x = cx + (hx - EDGE - 0.06)
glb("meeple_purple", (side_x - 0.09, board_y), top, scale=1.6)
glb("meeple_red", (side_x - 0.02, board_y), top, scale=1.6)
glb("die", (side_x - 0.09, board_y - 0.09), top, scale=1.5)
glb("die", (side_x - 0.02, board_y - 0.09), top, yaw=35, scale=1.5)
glb("air_marker", (side_x + 0.02, board_y), top, scale=CHIP * 0.8)

# ---------------------------------------------------------------- uHand を指差しで置く
TARGET_CHIP = int(arg("--chip", "13"))
tx, ty = pts[TARGET_CHIP]
tmn_c, tmx_c = world_bounds([o for o in bpy.data.objects if o.type == "MESH"
                             and math.dist((o.matrix_world.translation.x, o.matrix_world.translation.y), (tx, ty)) < 0.05
                             and o.matrix_world.translation.z < top + 0.02])
chip_top = top + 0.004

dg = bpy.context.evaluated_depsgraph_get()
pb = arm_h.pose.bones
f0 = ((arm_h.matrix_world @ pb["index_tip"].tail) - (arm_h.matrix_world @ pb["index_prox"].head)).normalized()
tip_ob = bpy.data.objects["uh_index_tip"]
ev = tip_ob.evaluated_get(dg)
tip = max((ev.matrix_world @ v.co for v in ev.data.vertices), key=lambda p: p.dot(f0))


def frame(f, n):
    f = f.normalized()
    n = (n - f * n.dot(f)).normalized()
    return Matrix((f, n, f.cross(n))).transposed()


ft = Vector(tuple(float(v) for v in arg("--hand-dir", "-0.45,-0.35,-0.82").split(","))).normalized()
nt = Vector(tuple(float(v) for v in arg("--palm", "-0.2,-0.6,-0.8").split(",")))
R = (frame(ft, nt) @ frame(f0, Vector((0, -1, 0))).inverted()).to_4x4()
HAND_SCALE = float(arg("--hand-scale", "1.0"))
M = R @ Matrix.Scale(HAND_SCALE, 4)
goal = Vector((tx, ty, chip_top + 0.0008))
arm_h.matrix_world = Matrix.Translation(goal - (M @ tip)) @ M @ arm_h.matrix_world
bpy.context.view_layer.update()
_low = min(((o.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world @ v.co).z, o.name)
           for o in uh_objs for v in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
           if o.name != "uh_index_tip")
print(f"[uhand] tip z={goal.z - top:+.4f} / 指先以外の最下点 {_low[0] - top:+.4f} m ({_low[1]})")

# ---------------------------------------------------------------- Remy を座らせる
remy, remy_new = import_root(bpy.ops.import_scene.fbx, REMY)
arm_r = next(o for o in remy_new if o.type == "ARMATURE")
arm_r.animation_data_clear()  # FBX のアクション（T ポーズ）が描画時に姿勢を上書きする
remy.matrix_world = Matrix.Rotation(math.pi, 4, "Z")  # +Y（卓）を向く

# 身長を 1.75m にそろえる（FBX の単位の解釈に依らないよう、骨の頭頂と足で測る）
bpy.context.view_layer.update()
_top = (arm_r.matrix_world @ arm_r.pose.bones["mixamorig:HeadTop_End"].head).z
_toe = (arm_r.matrix_world @ arm_r.pose.bones["mixamorig:LeftToeBase"].head).z
remy.matrix_world = Matrix.Scale(1.75 / (_top - _toe), 4) @ remy.matrix_world
print(f"[remy] rest height {_top - _toe:.3f} -> 1.75")

remy_mats = {s.material for o in remy_new if o.type == "MESH" for s in o.material_slots if s.material}
for m in remy_mats:
    if not m.node_tree:
        continue
    nt_ = m.node_tree
    tex = next((n for n in nt_.nodes if n.type == "TEX_IMAGE" and n.image
                and "Diffuse" in os.path.basename(n.image.filepath)), None)
    op = next((n for n in nt_.nodes if n.type == "TEX_IMAGE" and n.image
               and "Opacity" in os.path.basename(n.image.filepath)), None)
    paths = {}
    for n_, key in ((tex, "d"), (op, "o")):
        if n_ is not None:
            p = os.path.join(REMY_TEX, os.path.basename(n_.image.filepath.replace("\\", "/")))
            if os.path.exists(p):
                paths[key] = p
    nt_.nodes.clear()
    out = nt_.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt_.nodes.new("ShaderNodeBsdfPrincipled")
    nt_.links.new(bsdf.outputs[0], out.inputs[0])
    bsdf.inputs["Roughness"].default_value = 0.7
    if "d" in paths:
        ti = nt_.nodes.new("ShaderNodeTexImage")
        ti.image = bpy.data.images.load(paths["d"], check_existing=True)
        nt_.links.new(ti.outputs[0], bsdf.inputs["Base Color"])
    if "o" in paths:
        to = nt_.nodes.new("ShaderNodeTexImage")
        to.image = bpy.data.images.load(paths["o"], check_existing=True)
        to.image.colorspace_settings.name = "Non-Color"
        nt_.links.new(to.outputs[0], bsdf.inputs["Alpha"])
    print("[remy] material", m.name, sorted(paths))


def aim(name, d):
    bpy.context.view_layer.update()
    p = arm_r.pose.bones["mixamorig:" + name]
    d_a = (arm_r.matrix_world.to_quaternion().inverted() @ Vector(d)).normalized()
    cur = p.matrix.copy()
    q = cur.col[1].xyz.normalized().rotation_difference(d_a)
    m = (q.to_matrix() @ cur.to_3x3()).to_4x4()
    m.translation = cur.translation
    p.matrix = m


def twist(name, deg):
    bpy.context.view_layer.update()
    p = arm_r.pose.bones["mixamorig:" + name]
    cur = p.matrix.copy()
    q = Matrix.Rotation(math.radians(deg), 3, (arm_r.matrix_world.to_quaternion().inverted() @ Vector((0, 0, 1))))
    m = (q @ cur.to_3x3()).to_4x4()
    m.translation = cur.translation
    p.matrix = m


for nm, d in (("Spine", (0, 0.10, 1)), ("Spine1", (0, 0.14, 1)), ("Spine2", (0, 0.16, 1)),
              ("Neck", (0, 0.25, 1)), ("Head", (0.05, 0.45, 1)),
              ("LeftUpLeg", (-0.12, 1, -0.05)), ("RightUpLeg", (0.12, 1, -0.05)),
              ("LeftLeg", (-0.05, 0.12, -1)), ("RightLeg", (0.05, 0.12, -1)),
              ("LeftFoot", (-0.05, 0.85, -0.55)), ("RightFoot", (0.05, 0.85, -0.55)),
              ("LeftArm", (-0.12, 0.32, -0.94)), ("RightArm", (0.12, 0.32, -0.94)),
              ("LeftForeArm", (0.40, 1, 0.36)), ("RightForeArm", (-0.40, 1, 0.36)),
              ("LeftHand", (0.2, 1, -0.12)), ("RightHand", (-0.2, 1, -0.12))):
    aim(nm, d)
twist("Head", float(arg("--head-turn", "-12")))
bpy.context.view_layer.update()

# 腰を椅子の座面へ
hips = arm_r.matrix_world @ arm_r.pose.bones["mixamorig:Hips"].head
cmn, cmx = world_bounds(meshes_of(chair0))
SEAT_H = float(arg("--seat", "0.50"))
remy.matrix_world = Matrix.Translation(Vector((0 - hips.x, -0.60 - hips.y, SEAT_H - hips.z))) @ remy.matrix_world
bpy.context.view_layer.update()
print("[remy] hips ->", tuple(round(v, 3) for v in arm_r.matrix_world @ arm_r.pose.bones["mixamorig:Hips"].head),
      "wrist L", tuple(round(v, 3) for v in arm_r.matrix_world @ arm_r.pose.bones["mixamorig:LeftHand"].head))

# ---------------------------------------------------------------- 部屋・光・カメラ
def flat_mat(name, rgb, rough=0.9):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    return m


def box(name, loc, size, mat):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(mat)
    return o


def render_default():
    """元の構図（人の肩越し）で部屋・光・カメラを置いて描く。"""
    ROOM = 6.0
    box("floor", (0, 0, -0.01), (ROOM, ROOM, 0.02), flat_mat("floor", (0.25, 0.27, 0.30)))
    wall = flat_mat("wall", (0.63, 0.61, 0.58))
    box("wall_n", (0, ROOM / 2, 1.5), (ROOM, 0.02, 3), wall)
    box("wall_e", (ROOM / 2, 0, 1.5), (0.02, ROOM, 3), wall)
    box("wall_w", (-ROOM / 2, 0, 1.5), (0.02, ROOM, 3), wall)
    box("wall_s", (0, -ROOM / 2, 1.5), (ROOM, 0.02, 3), wall)

    sc = bpy.context.scene
    world = bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.62, 0.62, 0.64, 1)
    bg.inputs[1].default_value = 0.25


    def light(name, kind, loc, energy, size=1.0, target=(0, 0, 0.75)):
        ld = bpy.data.lights.new(name, kind)
        ld.energy = energy
        if kind == "AREA":
            ld.size = size
        lo = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return lo


    light("key", "AREA", (0.6, -0.4, 2.4), 150, 1.4)
    light("fill", "AREA", (-1.6, -1.2, 1.8), 50, 2.0)
    light("rim", "AREA", (0.2, 1.6, 1.9), 45, 1.5)

    cam_d = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    if flag("--top"):
        cam_d.type = "ORTHO"
        cam_d.ortho_scale = 1.5
        cam.location = (cx, cy, 3)
        cam.rotation_euler = (0, 0, 0)
    else:
        cam_d.lens = float(arg("--lens", "32"))
        loc = Vector(tuple(float(v) for v in arg("--cam", "0.62,-1.05,1.32").split(",")))
        look = Vector(tuple(float(v) for v in arg("--look", "-0.05,0.08,0.80").split(",")))
        cam.location = loc
        cam.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()

    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    try:
        sc.eevee.taa_render_samples = int(arg("--samples", "64"))
    except Exception:
        pass
    for attr in ("use_shadows", "use_gtao", "use_raytracing"):
        try:
            setattr(sc.eevee, attr, True)
        except Exception:
            pass
    try:
        sc.view_settings.view_transform = "AgX"
    except TypeError:
        pass
    w, h = (int(v) for v in arg("--size", "1600x900").split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.film_transparent = False
    out = arg("--out", os.path.join(ML, "exports", "deep-sea", "vr-scene.png"))
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("[scene] wrote", out)


if __name__ == "__main__":
    render_default()
