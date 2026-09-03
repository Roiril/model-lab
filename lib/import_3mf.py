"""3mf を Blender に読み込んで、部品を並べた四面図を焼く。

    blender --background --python lib/import_3mf.py -- <file.3mf> <out.png> [モード]

    （既定）    部品を実寸のまま 1 列に並べる
    --sheet     部品ごとに大きさをそろえて格子に置く。小さい部品が潰れない
    --assembled 3mf の build 変換をそのまま使い、造形プレート上の配置で出す

--sheet は部品ごとに倍率が違う。実寸は lib/read_3mf.py の表で読む。

シェーディングはフラット。機械部品にスムーズをかけると角が丸まって見え、
面取りやフィレットの有無を読み違える。
"""

import sys
import os
import zipfile
import xml.etree.ElementTree as ET

import bpy
from mathutils import Vector, Matrix

NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
MM = 0.001

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = argv[0], argv[1]
ASSEMBLED = "--assembled" in argv
SHEET = "--sheet" in argv


def clear():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def build_transforms(z):
    out = {}
    try:
        root = ET.fromstring(z.read("3D/3dmodel.model"))
    except KeyError:
        return out
    build = root.find(NS + "build")
    if build is None:
        return out
    for item in build.findall(NS + "item"):
        t = item.get("transform")
        if not t:
            continue
        v = [float(x) for x in t.split()]
        out[item.get("objectid")] = Matrix((
            (v[0], v[3], v[6], v[9] * MM),
            (v[1], v[4], v[7], v[10] * MM),
            (v[2], v[5], v[8], v[11] * MM),
            (0, 0, 0, 1),
        ))
    return out


def load(z):
    objs = []
    for entry in z.namelist():
        if not entry.endswith(".model"):
            continue
        root = ET.fromstring(z.read(entry))
        for obj in root.iter(NS + "object"):
            mesh = obj.find(NS + "mesh")
            if mesh is None:
                continue
            vs = mesh.find(NS + "vertices")
            ts = mesh.find(NS + "triangles")
            if vs is None or len(vs) == 0:
                continue
            verts = [(float(v.get("x")) * MM, float(v.get("y")) * MM, float(v.get("z")) * MM)
                     for v in vs]
            tris = [(int(t.get("v1")), int(t.get("v2")), int(t.get("v3"))) for t in ts]
            me = bpy.data.meshes.new(f"obj{obj.get('id')}")
            me.from_pydata(verts, [], tris)
            me.validate()
            # フラットシェーディング。角を丸めない
            for poly in me.polygons:
                poly.use_smooth = False
            ob = bpy.data.objects.new(me.name, me)
            bpy.context.collection.objects.link(ob)
            objs.append((obj.get("id"), ob))
    return objs


def dims(ob):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = Vector(min(c[i] for c in cs) for i in range(3))
    mx = Vector(max(c[i] for c in cs) for i in range(3))
    return mn, mx


def scene_bbox(objs):
    mn = Vector((1e9,) * 3)
    mx = Vector((-1e9,) * 3)
    for _, ob in objs:
        a, b = dims(ob)
        mn = Vector(min(mn[i], a[i]) for i in range(3))
        mx = Vector(max(mx[i], b[i]) for i in range(3))
    return mn, mx


clear()
with zipfile.ZipFile(SRC) as z:
    objs = load(z)
    tf = build_transforms(z)

if ASSEMBLED:
    for oid, ob in objs:
        if oid in tf:
            ob.matrix_world = tf[oid]
elif SHEET:
    # 部品ごとに最大寸法をそろえて格子に置く。小さい部品が大きい部品に潰されない
    import math
    cols = math.ceil(math.sqrt(len(objs)))
    cell = 0.030
    for k, (oid, ob) in enumerate(objs):
        mn, mx = dims(ob)
        span = max((mx - mn)[i] for i in range(3)) or 1.0
        s = cell * 0.78 / span
        ob.scale = (s, s, s)
        bpy.context.view_layer.update()
        mn, mx = dims(ob)
        ctr_p = (mn + mx) / 2
        ob.location -= Vector((ctr_p.x, ctr_p.y, mn.z))
        ob.location += Vector(((k % cols) * cell, -(k // cols) * cell, 0))
        print(f"[import]  格子 {k}: obj{oid}  実寸 "
              f"{[round((mx - mn)[i] / s / MM, 2) for i in range(3)]} mm  倍率 {s / MM:.2f}")
else:
    # 各部品を原点に寄せてから X 方向に間隔をあけて並べる
    gap = 0.004
    cursor = 0.0
    placed = []
    for oid, ob in objs:
        mn, mx = dims(ob)
        ob.location -= Vector((mn.x, (mn.y + mx.y) / 2, mn.z))
        placed.append((mx.x - mn.x, ob))
    placed.sort(key=lambda p: -p[0])
    for w, ob in placed:
        ob.location.x += cursor
        cursor += w + gap

bpy.context.view_layer.update()   # matrix_world を反映してから枠を測る
print(f"[import] {len(objs)} parts  assembled={ASSEMBLED}")

mat = bpy.data.materials.new("part")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.72, 0.74, 0.77, 1)
bsdf.inputs["Roughness"].default_value = 0.5
bsdf.inputs["Metallic"].default_value = 0.0
for _, ob in objs:
    ob.data.materials.append(mat)

mn, mx = scene_bbox(objs)
ctr = (mn + mx) / 2
size = max((mx - mn)[i] for i in range(3))
print(f"[import] bbox mm = {[round((mx - mn)[i] / MM, 2) for i in range(3)]}")

for pos, energy in (((1, -1.2, 1.4), 400), ((-1.3, -0.7, 0.5), 150), ((0.2, 1.5, 0.9), 110)):
    ld = bpy.data.lights.new("L", "AREA")
    ld.energy = energy
    ld.size = size * 3
    lo = bpy.data.objects.new("L", ld)
    bpy.context.collection.objects.link(lo)
    lo.location = ctr + Vector(pos) * size * 2.0
    lo.rotation_euler = (ctr - lo.location).to_track_quat("-Z", "Y").to_euler()

sc = bpy.context.scene
engines = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_WORKBENCH"
sc.world = sc.world or bpy.data.worlds.new("W")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.10, 0.10, 0.11, 1)
sc.render.resolution_x = 900
sc.render.resolution_y = 900 if SHEET else 520

cam_d = bpy.data.cameras.new("C")
cam_d.type = "ORTHO"
cam = bpy.data.objects.new("C", cam_d)
bpy.context.collection.objects.link(cam)
sc.camera = cam

if SHEET:
    # 格子は XY 平面に並ぶので、正面図と側面図は重なって読めない
    VIEWS = {"iso": (0.55, -0.55, 1), "top": (0, 0, 1)}
else:
    VIEWS = {"iso": (1, -1, 0.7), "front": (0, -1, 0), "side": (1, 0, 0), "top": (0, 0, 1)}
base, ext = os.path.splitext(OUT)
for name, d in VIEWS.items():
    v = Vector(d).normalized()
    cam.location = ctr + v * size * 4
    cam.rotation_euler = (-v).to_track_quat("-Z", "Y").to_euler()
    cam_d.ortho_scale = size * 1.1
    sc.render.filepath = f"{base}_{name}{ext}"
    bpy.ops.render.render(write_still=True)
    print(f"[import] {sc.render.filepath}")
