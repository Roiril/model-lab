# -*- coding: utf-8 -*-
"""卓の上のボードゲームを 1 つずつ撮る。図1（render_teaser.py）と同じ卓の色・青い背景・光の向きで、物撮りの画にする。

blender --background --python tools/tableduo_figs/fig_games.py -- --game dsa|algo|geister|bandido|bear|all（all は 5 つを 1 つの卓に集めた集合写真）
    [--out PATH] [--size 2100x1400] [--samples N] [--engine cycles|eevee]
    [--top]            配置の確認用に真上から撮る
    [--az deg] [--el deg] [--fill 0..1] [--shift x,y] [--lens mm] [--fstop f] [--focus x,y,z]
    [--drawing PATH]   「あと6画のくま」のパッドに載せる絵
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy
from mathutils import Vector

import tdf_common as C

arg, flag, vec = C.arg, C.flag, C.vec
GAME = arg("--game", "dsa")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------------------------------------------------------------- 卓とゲーム
wood = C.wood_mat(light=(0.27, 0.19, 0.13), dark=(0.175, 0.118, 0.078), rough=0.46, coat=0.10,
                  grain=float(arg("--grain", "1.0")))
table = C.build_table(wood, legs=True)
kw = {}
if GAME in ("bear", "all"):
    kw["drawing"] = arg("--drawing", os.path.join(HERE, "bear_drawing.png"))  # make_bear_drawing.py で作る
if GAME == "bandido":
    # 開始札の左右の出口から道をのばした形。札の名前と向きは絵を見て決めた
    laid = arg("--laid", "g20:2:0:90,g11:-0.5:1.5:0,g4:0.5:1.5:0,g24:-0.5:-1.5:0")
    kw["laid"] = [(n, float(x), float(y), float(w)) for n, x, y, w in
                  (item.split(":") for item in laid.split(","))]
    kw["deck_x"] = float(arg("--deck-x", "0.26"))
    kw["deck_y"] = float(arg("--deck-y", "0.06"))
C.PLACERS[GAME](**kw)
# 札と駒の艶を抑える（光が面で返ると印刷の色が抜ける）
for m in {sl.material for o in C.GAME_OBJS for sl in o.material_slots if sl.material}:
    b_ = C.bsdf_of(m)
    r_ = b_.inputs["Roughness"]
    if not r_.is_linked:
        r_.default_value = max(r_.default_value, float(arg("--min-rough", "0.72")))
gmn, gmx = C.world_bounds(C.GAME_OBJS)
gc = (gmn + gmx) / 2
print(f"[games] {GAME} bounds x {gmn.x:.3f}..{gmx.x:.3f} y {gmn.y:.3f}..{gmx.y:.3f} z ..{gmx.z:.3f} / objs {len(C.GAME_OBJS)}")

# ---------------------------------------------------------------- 部屋（暗い床と、奥の青い壁）
ROOM = 7.0
floor_m = C.flat_mat("floor", (0.022, 0.027, 0.034), 0.22)
wall_m = C.flat_mat("wall", (0.070, 0.095, 0.120), 0.95)
for name, loc, size in (("floor", (0, 0, -0.01), (ROOM, ROOM, 0.02)),
                        ("wall_n", (0, ROOM / 2, 1.5), (ROOM, 0.02, 3)), ("wall_s", (0, -ROOM / 2, 1.5), (ROOM, 0.02, 3)),
                        ("wall_e", (ROOM / 2, 0, 1.5), (0.02, ROOM, 3)), ("wall_w", (-ROOM / 2, 0, 1.5), (0.02, ROOM, 3))):
    C.rbox(name, loc, size, wall_m if name.startswith("wall") else floor_m, bevel=0)
C.world((0.30, 0.42, 0.60), float(arg("--ambient", "0.05")))

# ---------------------------------------------------------------- カメラ
# 人の席の左手前から、卓を斜めに見下ろす。向き（az: 人の席の正面から左へ回る角度）と高さ（el）と寄り（fill）を
# ゲームごとに決め、距離は駒の外接箱が画面に収まるように出す
VIEWS = {
    "all": dict(az=14, el=27, lens=70, fill=1.05, fstop=8.0, shift=(0.0, 0.0), focus=(0.0, -0.10)),
    "dsa": dict(az=32, el=23, lens=85, fill=1.55, fstop=4.0, shift=(-0.16, -0.04), focus=(-0.08, -0.03)),
    "algo": dict(az=40, el=26, lens=85, fill=0.98, fstop=4.5, shift=(0.0, 0.03), focus=(-0.10, -0.02)),
    "geister": dict(az=36, el=21, lens=85, fill=0.95, fstop=5.6, shift=(0.0, 0.02), focus=(0.0, -0.06)),
    "bandido": dict(az=44, el=29, lens=85, fill=1.02, fstop=4.5, shift=(0.0, 0.0), focus=(0.0, 0.0)),
    "bear": dict(az=26, el=28, lens=85, fill=1.45, fstop=4.5, shift=(-0.02, -0.03), focus=(0.0, -0.05)),
}
v = VIEWS[GAME]
K = float(arg("--light", "1.0"))
if flag("--top"):
    C.camera((0, 0, 3), (0, 0.0001, 0.75), 50, ortho=float(arg("--ortho", "1.45")))
    C.light("top", "AREA", (0, 0, 2.6), 60, 2.5)
    C.setup_render("games", arg("--size", "1500x900"), samples=24, engine="eevee")
else:
    az = math.radians(float(arg("--az", v["az"])))
    el = math.radians(float(arg("--el", v["el"])))
    lens = float(arg("--lens", v["lens"]))
    w, h = (int(x) for x in arg("--size", "2100x1400").split("x"))
    d = Vector((-math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))  # 卓からカメラへ
    right = Vector((0, 0, 1)).cross(d).normalized()
    up = d.cross(right)
    sx, sy = (float(x) for x in arg("--shift", "%g,%g" % v["shift"]).split(","))
    look = Vector((gc.x, gc.y, (C.TOP + gmx.z) / 2))
    # 外接箱の 8 隅を画面の横と縦へ射影して、いちばん遠い隅が fill の内側に入る距離を取る
    corners = [Vector((x, y, z)) for x in (gmn.x, gmx.x) for y in (gmn.y, gmx.y) for z in (C.TOP, gmx.z)]
    th, tv = 18.0 / lens, 18.0 / lens * h / w
    fill = float(arg("--fill", v["fill"]))
    dist = 0.0
    for c in corners:
        r = c - look
        dist = max(dist, abs(r.dot(right)) / (th * fill) + r.dot(d), abs(r.dot(up)) / (tv * fill) + r.dot(d))
    look = look + right * sx * dist * th + up * sy * dist * tv
    cam_loc = look + d * dist
    if arg("--cam"):
        cam_loc, look = vec("--cam", "0,0,0"), vec("--look", "0,0,0.75")
    fx, fy = (float(x) for x in arg("--focus", "%g,%g" % v["focus"]).split(","))  # ピントを合わせる卓上の点
    focus = Vector((fx, fy, C.TOP + 0.01))
    C.camera(cam_loc, look, lens, fstop=float(arg("--fstop", v["fstop"])), focus=focus)
    print(f"[games] cam {tuple(round(x, 3) for x in cam_loc)} dist {dist:.3f}")
    WARM, COOL = (1.0, 0.90, 0.78), (0.62, 0.82, 1.0)
    tgt = (gc.x, gc.y, C.TOP)
    # 主光: カメラの左の高い所から横向きに。卓の正反射がカメラへ返らない向きにして、札の絵を白く飛ばさない。
    # 影は右へ落ちる。広がりを絞って、卓の端へ向かって暗く落とす
    key_p = Vector(tgt) - right * 1.25 + Vector((0, 0, 1.25)) - d.xy.to_3d().normalized() * 0.25
    C.light("key", "AREA", key_p, 21 * K * float(arg("--key", "1.0")), 0.55, target=tgt,
            color=WARM, spread=float(arg("--key-spread", "70")))
    # カメラの上から、影を少し起こす大きな面
    C.light("fill", "AREA", cam_loc + Vector((0, 0, 0.6)) + right * 0.5, 3 * K * float(arg("--fillk", "1.0")), 1.8,
            target=tgt, color=(0.88, 0.94, 1.0), spread=120)
    # 右奥の低い所から、細長い青い光。立っている駒と札の縁に線が入る（卓には当てない）
    rim_p = Vector(tgt) + right * 0.95 - d.xy.to_3d().normalized() * 0.95 + Vector((0, 0, 0.42))
    C.only(C.light("rim", "AREA", rim_p, 10 * K * float(arg("--rim", "1.0")), 1.4,
                   target=tgt, color=COOL, size_y=0.14, spread=70), C.GAME_OBJS, "ll_rim")
    # 奥の壁の青い明かり。暗い床に映って、卓の外が青く沈む
    WASH = float(arg("--wash", "0.6"))
    if WASH > 0:
        for i, (px, py, tx, ty) in enumerate(((0.4, 1.3, 0.4, 3.5), (1.3, 0.2, 3.5, 0.2))):
            C.light(f"wash{i}", "SPOT", (px, py, 0.15), 1500 * WASH, 0.3, target=(tx, ty, 1.05),
                    color=(0.30, 0.58, 0.85), spot=120)
    C.setup_render("games", arg("--size", "2100x1400"), samples=int(arg("--samples", "256")),
                   engine=arg("--engine", "cycles"), exposure=float(arg("--exposure", "0")))

C.render("games", arg("--out", os.path.join(C.ML, "exports", "table-duo-figs", f"game-{GAME}.png")))
