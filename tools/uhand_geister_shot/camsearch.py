# -*- coding: utf-8 -*-
"""場面（posesearch.py の scene.json）を固定し、カメラの仰角と方位を格子で探す。

"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python tools/uhand_geister_shot/camsearch.py --
    --scene scene.json --ref-hand ref_hand.npy --ref-ghost ref_ghost.npy --out cams.json --work DIR

候補ごとに:
  1. 距離と画面上の位置（レンズのシフト）を、手の外接枠が参照の外接枠に合うよう 3 回詰める
  2. 手と駒のシルエットを描き、手の IoU・駒の見えている割合・駒の中心のずれを測る
硬い条件: 駒の見えている割合 0.9 以上。満たす候補を手の IoU の順に並べる。
上位は Workbench の陰影つきの絵も描く（DIR/top_<順位>.png）。焦点距離は 60mm で固定。
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

import scene as SC

W, H = 960, 560
SW, SH = 240, 140
LENS = 60.0


def arg(name, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(name) + 1] if name in a else default


def downsample(mask):
    m = np.fliplr(mask).astype(np.float32)      # 参照は左手。右手の模型に合わせて反転
    return m.reshape(SH, H // SH, SW, W // SW).mean(axis=(1, 3)) > 0.5


def box(m):
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return None
    return np.array([xs.min(), xs.max() + 1, ys.min(), ys.max() + 1], dtype=float)


def iou(a, b):
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 0.0


cfg = json.load(open(arg("--scene"), encoding="utf-8"))["best"]
S = SC.Scene()
S.set_hand(cfg["dofs"], cfg["pitch"], cfg["roll"])
S.cx, S.cy = cfg["c"]
S.put_ghost()
for o in S.uh:
    o.color = (1, 0, 0, 1)
for o in S.gm:
    o.color = (0, 0, 1, 1)
hv = np.concatenate(list(S.verts.values()))
center = Vector((float(hv[:, 0].mean()), float(hv[:, 1].mean()), float(hv[:, 2].mean())))

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sc.display.render_aa = "OFF"
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.file_format = "PNG"
work = arg("--work")
os.makedirs(work, exist_ok=True)
cd = bpy.data.cameras.new("cam")
cd.lens, cd.sensor_width, cd.sensor_fit = LENS, 36.0, "HORIZONTAL"
cam = bpy.data.objects.new("cam", cd)
sc.collection.objects.link(cam)
sc.camera = cam

ref_h = downsample(np.load(arg("--ref-hand")))
ref_g = downsample(np.load(arg("--ref-ghost")))
RB = box(ref_h)
RG = box(ref_g)


def flat_mode():
    sh.light, sh.color_type = "FLAT", "OBJECT"
    sh.background_type, sh.background_color = "VIEWPORT", (0, 0, 0)
    sc.render.resolution_x, sc.render.resolution_y = SW, SH


def render_masks(path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(path, check_existing=False)
    px = np.array(im.pixels[:], dtype=np.float32).reshape(SH, SW, 4)[::-1]
    bpy.data.images.remove(im)
    return (px[..., 0] > 0.5) & (px[..., 2] < 0.5), (px[..., 2] > 0.5) & (px[..., 0] < 0.5)


def set_cam(el, az, dist, sx, sy):
    e, a = math.radians(el), math.radians(az)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    cam.location = center + d * dist
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.shift_x, cd.shift_y = sx, sy
    S.put_ghost(cam_pos=cam.location)


HV = hv[::7]          # 外接枠の計算に使う手の点（間引き）
# --frame-all: 手と駒を合わせた外接枠を、参照の手と駒を合わせた枠に合わせる。
# 手を床から持ち上げると駒が手より下へ出て、手だけで合わせると駒の下が画面の外に切れる（2026-11-26）
FRAME_ALL = "--" in sys.argv and "--frame-all" in sys.argv[sys.argv.index("--") + 1:]
if FRAME_ALL:
    gv = np.array([(o.matrix_world @ v.co)[:] for o in S.gm for v in o.data.vertices])   # 駒は軸まわりに回るだけなので枠は変わらない
    HV = np.concatenate([HV, gv[::7]])
    RB = np.array([min(RB[0], RG[0]), max(RB[1], RG[1]), min(RB[2], RG[2]), max(RB[3], RG[3])])


def proj_box():
    """手の点をカメラの式で投影した外接枠（SW x SH の画素。画面の外にはみ出しても測れる）。"""
    M = np.array(cam.matrix_world.inverted())
    p = HV @ M[:3, :3].T + M[:3, 3]
    k = cd.lens / cd.sensor_width
    nx = k * p[:, 0] / -p[:, 2] - cd.shift_x
    ny = k * p[:, 1] / -p[:, 2] - cd.shift_y
    x = (nx + 0.5) * SW
    y = SH / 2 - ny * SW
    return np.array([x.min(), x.max(), y.min(), y.max()])


def frame(el, az):
    """外接枠を参照に合わせる距離とシフトを詰め、測った値を返す。"""
    dist, sx, sy = 0.5, 0.0, 0.0
    tmp = os.path.join(work, "_m.png")
    rw, rh = RB[1] - RB[0], RB[3] - RB[2]
    rcx, rcy = (RB[0] + RB[1]) / 2, (RB[2] + RB[3]) / 2
    for _ in range(8):
        set_cam(el, az, dist, sx, sy)
        b = proj_box()
        w, hh = b[1] - b[0], b[3] - b[2]
        s = max(w / rw, hh / rh)          # 枠が参照の枠に収まる大きさ（縦横比が違えば片方は余る）
        dist *= s
        set_cam(el, az, dist, sx, sy)
        b = proj_box()
        cx, cy = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2
        sx -= (rcx - cx) / SW
        sy += (rcy - cy) / SW
    set_cam(el, az, dist, sx, sy)
    h, g = render_masks(tmp)
    for o in S.uh:
        o.hide_render = True
    _, g_only = render_masks(tmp)
    for o in S.uh:
        o.hide_render = False
    vis = float(g.sum() / g_only.sum()) if g_only.sum() else 0.0
    gb = box(g_only)
    gdx = gdy = gh = None
    if gb is not None:
        gdx = float(((gb[0] + gb[1]) - (RG[0] + RG[1])) / 2 * (W / SW))
        gdy = float(((gb[2] + gb[3]) - (RG[2] + RG[3])) / 2 * (W / SW))
        gh = float((gb[3] - gb[2]) * (W / SW))
    b = box(h)
    return dict(el=el, az=az, dist=dist, shift_x=sx, shift_y=sy, iou_hand=iou(h, ref_h), ghost_visible=vis,
                ghost_dx_px=gdx, ghost_dy_px=gdy, ghost_h_px=gh,
                hand_box=[float(v * W / SW) for v in b], cam_pos=list(cam.location), look=list(center))


def rank(r):
    """手の IoU から、駒の中心のずれ 100px ごとに 0.15 を引く。"""
    return r["iou_hand"] - 0.15 * math.hypot(r["ghost_dx_px"], r["ghost_dy_px"]) / 100


flat_mode()
res = []
EL = [int(v) for v in arg("--el", "40,45,50,55,60,65").split(",")]
for el in EL:
    for az in range(0, 360, 10):
        r = frame(el, az)
        if r and r["ghost_dx_px"] is not None:
            r["rank"] = rank(r)
            res.append(r)
    best = max((r for r in res if r["ghost_visible"] >= 0.9), key=lambda r: r["rank"], default=None)
    print(f"[cam] 仰角 {el} まで {len(res)} 候補 / 最良 {best and (best['el'], best['az'], round(best['rank'], 3))}", flush=True)

ok = sorted((r for r in res if r["ghost_visible"] >= 0.9), key=lambda r: -r["rank"])
ng = len(res) - len(ok)
print(f"[cam] 駒が 9 割見える候補 {len(ok)} / 全 {len(res)}（落とした {ng}）")
print(f"[cam] 参照の駒の高さ {float((RG[3] - RG[2]) * W / SW):.0f} px")
for k, r in enumerate(ok[:10]):
    print(f"[cam] {k}: 仰角 {r['el']} 方位 {r['az']} 順位値 {r['rank']:.3f} 手 IoU {r['iou_hand']:.3f} 駒の見え {r['ghost_visible']:.2f} "
          f"駒のずれ ({r['ghost_dx_px']:.0f}, {r['ghost_dy_px']:.0f}) px 駒の高さ {r['ghost_h_px']:.0f} px")

# 上位 8 つを陰影つきで描く（目で選ぶため）
sh.light, sh.color_type = "STUDIO", "MATERIAL"
sh.background_type, sh.background_color = "VIEWPORT", (0.78, 0.78, 0.78)
sh.show_cavity = True
sc.display.render_aa = "8"
sc.render.resolution_x, sc.render.resolution_y = 480, 280
for k, r in enumerate(ok[:8]):
    set_cam(r["el"], r["az"], r["dist"], r["shift_x"], r["shift_y"])
    sc.render.filepath = os.path.join(work, f"top_{k}.png")
    bpy.ops.render.render(write_still=True)

out = arg("--out")
tmp = out + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    # all は駒の見えで落とした角度も含む（周りの角度から撮り比べるとき用）
    json.dump({"scene": cfg, "ok": ok, "rejected": ng, "all": res}, f, ensure_ascii=False, indent=1)
os.replace(tmp, out)
print("[cam]", out)
