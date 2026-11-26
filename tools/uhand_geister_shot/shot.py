# -*- coding: utf-8 -*-
"""場面（posesearch.py）とカメラ（camsearch.py）を受け取り、Cycles で 1 枚を描く。

"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python tools/uhand_geister_shot/shot.py --
    --cams cams.json [--pick 0] --out shot.png [--size 1920x1120] [--samples 256] [--sil sil.png]

描くのは右手の模型。参照（左手）と同じ向きで見るには compare.py が左右反転する。
--sil を渡すと、同じカメラで手 = 赤・駒 = 青のシルエットも描く（compare.py が IoU を測る）。
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import scene as SC


def arg(name, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(name) + 1] if name in a else default


def bsdf_of(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


C = json.load(open(arg("--cams"), encoding="utf-8"))
cfg = C["scene"]
cam_cfg = C["ok"][int(arg("--pick", "0"))]
print(f"[shot] 姿勢 {cfg['dofs']} pitch {cfg['pitch']} roll {cfg['roll']} / カメラ 仰角 {cam_cfg['el']} 方位 {cam_cfg['az']}")

S = SC.Scene()
S.set_hand(cfg["dofs"], cfg["pitch"], cfg["roll"])
S.cx, S.cy = cfg["c"]
cam_pos = Vector(cam_cfg["cam_pos"])
S.put_ghost(cam_pos=cam_pos)

# ---------------------------------------------------------------- 接触の確かめ（面どうしの当たり判定）
dg = bpy.context.evaluated_depsgraph_get()


def tree(ob, shrink=0.0):
    ev = ob.evaluated_get(dg)
    M = ev.matrix_world
    vs = [M @ v.co for v in ev.data.vertices]
    if shrink:
        c = Vector((S.cx, S.cy, 0))
        vs = [c + Vector((v.x - c.x, v.y - c.y, 0)) * (1 - shrink) + Vector((0, 0, v.z)) for v in vs]
    return BVHTree.FromPolygons(vs, [tuple(p.vertices) for p in ev.data.polygons])


hand_t = {o.name: tree(o) for o in S.uh}
g_full = [tree(o) for o in S.gm]
g_in = [tree(o, 0.08) for o in S.gm]          # 半径を 8% 細らせた駒（約 1mm 内側）
touch = sorted({k for k, t in hand_t.items() if any(g.overlap(t) for g in g_full)})
deep = sorted({k for k, t in hand_t.items() if any(g.overlap(t) for g in g_in)})
print(f"[shot] 駒の表面に触れる部品 {touch} / 1mm より深く食い込む部品 {deep or 'なし'}")
cl = S.clearances((S.cx, S.cy))
print(f"[shot] 頂点で測った隙間: 親指 {cl['uh_thumb_tip'][0] * 1000:.2f}mm（高さ {cl['uh_thumb_tip'][1] * 1000:.0f}mm）"
      f" 人差し指 {cl['uh_index_tip'][0] * 1000:.2f}mm（高さ {cl['uh_index_tip'][1] * 1000:.0f}mm）")

# ---------------------------------------------------------------- 材質（実物の写真では黒は濃い灰に写る）
LIFT = float(arg("--lift", "1.6"))
SPEC = float(arg("--spec", "0.5"))       # 黒い面の鏡面反射の強さ（Principled の Specular IOR Level。既定 0.5）
for name, rgb, rough in (("uh_acrylic", (0.016, 0.017, 0.020), 0.25), ("uh_servo", (0.020, 0.021, 0.024), 0.42),
                         ("uh_alu", (0.030, 0.031, 0.035), 0.5), ("uh_dark", (0.008, 0.008, 0.009), 0.45),
                         ("uh_bushing", (0.02, 0.02, 0.022), 0.25)):
    m = bpy.data.materials.get(name)
    if m is not None:
        b = bsdf_of(m)
        b.inputs["Base Color"].default_value = (*[c * LIFT for c in rgb], 1)
        b.inputs["Roughness"].default_value = rough
        for nm in ("Specular IOR Level", "Specular"):
            if nm in b.inputs:
                b.inputs[nm].default_value = SPEC
                break
for name in ("uh_steel", "uh_link"):
    m = bpy.data.materials.get(name)
    if m is not None:
        b = bsdf_of(m)
        b.inputs["Metallic"].default_value = 0.9
        b.inputs["Base Color"].default_value = (0.72, 0.73, 0.76, 1)
        b.inputs["Roughness"].default_value = 0.28
for o in S.gm:
    for sl in o.material_slots:
        if sl.material:
            bsdf_of(sl.material).inputs["Roughness"].default_value = 0.55

# ---------------------------------------------------------------- 床・光・背景（参照の地は sRGB 200 の灰）
sc = bpy.context.scene
BG = float(arg("--bg", "0.58"))
fm = bpy.data.materials.new("floor")
fm.use_nodes = True
fb = bsdf_of(fm)
fb.inputs["Base Color"].default_value = (BG, BG, BG, 1)
fb.inputs["Roughness"].default_value = 0.8
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
plane = bpy.context.active_object
plane.data.materials.append(fm)
w = bpy.data.worlds.new("w")
w.use_nodes = True
bgn = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
bgn.inputs[0].default_value = (BG, BG, BG, 1)
bgn.inputs[1].default_value = float(arg("--world", "0.6"))
sc.world = w

center = Vector(cam_cfg["look"])
view = (center - cam_pos).normalized()
right = view.cross(Vector((0, 0, 1))).normalized()
back = Vector((view.x, view.y, 0)).normalized()


def light(name, off, energy, size):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy, ld.size = energy, size
    lo = bpy.data.objects.new(name, ld)
    lo.location = center + off
    lo.rotation_euler = (center - lo.location).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(lo)


K = float(arg("--light", "0.15"))
# 参照は画面の左上から光が来る。右手で描いて反転するので、ここでは画面の右上から当てる
light("key", right * 0.3 + back * 0.15 + Vector((0, 0, 0.75)), 140 * K, 0.9)
light("fill", -right * 0.5 - back * 0.55 + Vector((0, 0, 0.35)), 45 * K, 0.8)
light("rim", right * 0.5 + back * 0.45 + Vector((0, 0, 0.3)), 35 * K, 0.6)

# ---------------------------------------------------------------- カメラ（camsearch.py と同じ置き方）
cd = bpy.data.cameras.new("cam")
cd.lens, cd.sensor_width, cd.sensor_fit = 60.0, 36.0, "HORIZONTAL"
cd.shift_x, cd.shift_y = cam_cfg["shift_x"], cam_cfg["shift_y"]
cam = bpy.data.objects.new("cam", cd)
sc.collection.objects.link(cam)
sc.camera = cam
cam.location = cam_pos
cam.rotation_euler = (center - cam_pos).to_track_quat("-Z", "Y").to_euler()

wd, ht = (int(v) for v in arg("--size", "1920x1120").split("x"))
sc.render.resolution_x, sc.render.resolution_y = wd, ht
sc.render.image_settings.file_format = "PNG"
sc.render.engine = "CYCLES"
sc.cycles.samples = int(arg("--samples", "256"))
sc.cycles.use_denoising = True
prefs = bpy.context.preferences.addons["cycles"].preferences
used = "CPU"
for kind in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = kind
        prefs.get_devices()
        gpus = [dv for dv in prefs.devices if dv.type == kind]
        if gpus:
            for dv in prefs.devices:
                dv.use = dv.type == kind
            sc.cycles.device = "GPU"
            used = f"{kind} {gpus[0].name}"
            break
    except TypeError:
        pass
print(f"[render] cycles {sc.cycles.samples} spp gpu={used}")
VT = arg("--view", "AgX")
try:
    sc.view_settings.view_transform = VT
except TypeError as e:
    raise SystemExit(f"[render] 表示変換 {VT!r} は無い: {e}")
LOOK = arg("--look")
if LOOK:
    try:
        sc.view_settings.look = LOOK
    except TypeError as e:
        raise SystemExit(f"[render] look {LOOK!r} は無い: {e}")
print(f"[render] 表示変換 {sc.view_settings.view_transform} / look {sc.view_settings.look}")
sc.view_settings.exposure = float(arg("--exposure", "0"))
out = arg("--out")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("[render]", out)

sil = arg("--sil")
if sil:
    plane.hide_render = True
    for o in S.uh:
        o.color = (1, 0, 0, 1)
    for o in S.gm:
        o.color = (0, 0, 1, 1)
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light, sh.color_type = "FLAT", "OBJECT"
    sh.background_type, sh.background_color = "VIEWPORT", (0, 0, 0)
    sc.display.render_aa = "OFF"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0
    sc.render.resolution_x, sc.render.resolution_y = 960, 560
    sc.render.filepath = sil
    bpy.ops.render.render(write_still=True)
    print("[render]", sil)
