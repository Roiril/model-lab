# -*- coding: utf-8 -*-
"""ガイスターおばけコマの GLB ビルダー（Blender 5.1 / bpy）。

弾丸型の楕円ロフト本体（白）＋ 正面の目2つ（暗色の凹み）＋ 裏の丸マーカー（赤/青）
＋ 裏の縦ひだ（溝）＋ なみなみ裾 を生成し、

  exports/geister-ghost/ghost_blue.glb
  exports/geister-ghost/ghost_red.glb
  exports/geister-ghost/geister-ghost.glb   （青・赤 並べた俯瞰）

を書き出す（テクスチャなし・単色マテリアル、Unity 取り込み用）。

実行: ./run.sh models/geister-ghost/build_glb.py
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy, bmesh
import numpy as np
from params import *

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "geister-ghost"))
os.makedirs(OUT, exist_ok=True)

# 段階検証用トグル（True で裏のひだ・なみなみ裾を追加）
DO_FLUTES = True

def _rel_at(t):
    """正面 half幅の RX_BASE 比を数式で返す（滑らかな1本曲線）。
    t<=SHOULDER_T: ベル状に広がる裾（底=1.0 → 肩=SHOULDER_REL）
    t> SHOULDER_T: 丸くブラントなドーム頭（肩=SHOULDER_REL → 頭頂=0）
    """
    if t <= SHOULDER_T:
        u = t / SHOULDER_T                      # 0=底, 1=肩
        base = SHOULDER_REL + (1.0 - SHOULDER_REL) * (1.0 - u) ** BODY_FLARE_POW
        foot = FLARE_FOOT * math.exp(-(t / FOOT_WIDTH) ** 2)  # 最下部のスカート広がり
        return base + foot
    u = (t - SHOULDER_T) / (1.0 - SHOULDER_T)   # 0=肩, 1=頭頂
    return SHOULDER_REL * max(0.0, 1.0 - u ** DOME_POW) ** 0.5


# 数式プロファイルを密にサンプルして補間テーブル化
_PT = np.linspace(0.0, 1.0, 400)
_PR = np.array([_rel_at(t) for t in _PT])


def rx_at(t):
    return float(np.interp(t, _PT, _PR)) * RX_BASE


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for d in list(blk):
            blk.remove(d)


def srgb_to_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def solid_mat(name, rgb, rough=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    r, g, b = [srgb_to_lin(x) for x in rgb[:3]]
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 0.0
    return m


def boolean(target, cutter, op="DIFFERENCE"):
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def add_cylinder(r, depth, loc, rot):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=depth,
                                        location=loc, rotation=rot)
    return bpy.context.object


# ---------------------------------------------------------------- 本体ロフト
def make_body():
    me = bpy.data.meshes.new("ghost")
    ob = bpy.data.objects.new("ghost", me)
    bpy.context.collection.objects.link(ob)
    bm = bmesh.new()

    ts = np.linspace(0.0, 1.0, N_Z)
    rings = []
    for ti in ts[:-1]:                       # 最上段は apex に置換
        rx = rx_at(ti)
        ry = rx * DEPTH_RATIO
        z = HEIGHT * ti
        ring = []
        for k in range(N_THETA):
            a = 2 * math.pi * k / N_THETA
            ring.append(bm.verts.new((rx * math.cos(a), ry * math.sin(a), z)))
        rings.append(ring)
    apex = bm.verts.new((0.0, 0.0, HEIGHT))
    bm.verts.ensure_lookup_table()

    # 側面 quad
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(N_THETA):
            j = (k + 1) % N_THETA
            bm.faces.new([r0[k], r0[j], r1[j], r1[k]])
    # 頭頂 fan
    top = rings[-1]
    for k in range(N_THETA):
        j = (k + 1) % N_THETA
        bm.faces.new([top[k], top[j], apex])
    # 底 n-gon
    bm.faces.new(list(reversed(rings[0])))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    return ob


def y_front_at(x, t):
    """高さ t・左右 x での正面(+Y)表面の y 座標。"""
    rx = rx_at(t)
    ry = rx * DEPTH_RATIO
    q = max(0.0, 1.0 - (x / rx) ** 2)
    return ry * math.sqrt(q)


# ---------------------------------------------------------------- 目
def cut_eyes(body):
    dark_discs = []
    for sx in (-1, 1):
        x = sx * EYE_DX
        z = HEIGHT * EYE_T
        ysurf = y_front_at(x, EYE_T)
        # 掘り込み: Y 軸沿いのシリンダーを正面から差し込む
        cyl = add_cylinder(EYE_R, EYE_DEPTH * 2 + 0.004,
                            (x, ysurf + EYE_DEPTH * 1.0, z),
                            (math.radians(90), 0, 0))
        boolean(body, cyl, "DIFFERENCE")
        # 穴底に暗色ディスク（暗く見せる）
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32, radius=EYE_R * 0.92, depth=0.0006,
            location=(x, ysurf - EYE_DEPTH + 0.0009, z),
            rotation=(math.radians(90), 0, 0))
        dark_discs.append(bpy.context.object)
    # 2枚を結合
    bpy.ops.object.select_all(action="DESELECT")
    for d in dark_discs:
        d.select_set(True)
    bpy.context.view_layer.objects.active = dark_discs[0]
    bpy.ops.object.join()
    eyes = bpy.context.object
    eyes.name = "eyes"
    eyes.data.materials.append(solid_mat("eye_dark", EYE_DARK, rough=0.6))
    return eyes


# ---------------------------------------------------------------- 裏ひだ・裾
def cut_flutes(body):
    # 溝: 裏(-Y)側の下半分〜底面まで縦の半円溝を彫る。
    # 上端は球で丸めて滑らかにフェードさせ（硬い棚を作らない）、
    # 下端は底面(z=0)を貫いて裾まで届かせる（底面自体は平ら、裏の縁だけ溝でなみなみ）。
    xs = np.linspace(-RX_BASE * 0.62, RX_BASE * 0.62, FLUTE_N)
    ztop = HEIGHT * FLUTE_TOP
    zbot = -0.010
    for x in xs:
        ysurf = -y_front_at(x, 0.35)              # 裏面は -Y
        y = ysurf - FLUTE_R * 0.55
        # カッターは結合せず個別に引く（結合すると自己交差で EXACT が壊れる）。
        cyl = add_cylinder(FLUTE_R, ztop - zbot, (x, y, (ztop + zbot) / 2), (0, 0, 0))
        boolean(body, cyl, "DIFFERENCE")
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=32, ring_count=16, radius=FLUTE_R, location=(x, y, ztop))
        boolean(body, bpy.context.object, "DIFFERENCE")   # 上端を球で丸める


# ---------------------------------------------------------------- マーカー
def make_marker(body, rgb):
    """裏面に平らな座ぐりを彫り、その底に色ディスクを埋め込む（出っ張らせない）。"""
    z = HEIGHT * MARK_T
    ysurf = -y_front_at(0.0, MARK_T)      # 裏面中央（-Y, 負値）。外側 = -Y 方向
    # 座ぐり: 底面 y = ysurf + MARK_POCKET（胴側へ 0.6mm）から外へ貫くシリンダーで平らに削る
    extra = 0.004
    cyl = add_cylinder(MARK_R, MARK_POCKET + extra,
                       (0.0, ysurf + MARK_POCKET / 2 - extra / 2, z),
                       (math.radians(90), 0, 0))
    boolean(body, cyl, "DIFFERENCE")
    # 色ディスク: 外面を表面より 0.3mm 内側に（埋め込み）
    disc_t = 0.0007
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=MARK_R * 0.94, depth=disc_t,
        location=(0.0, ysurf + MARK_INSET + disc_t / 2, z),
        rotation=(math.radians(90), 0, 0))
    mk = bpy.context.object
    mk.name = "marker"
    mk.data.materials.append(solid_mat("marker", rgb, rough=0.35))
    return mk


# ---------------------------------------------------------------- ビルド1体
def build_ghost(variant_rgb):
    body = make_body()
    body.data.materials.append(solid_mat("body_white", BODY_WHITE, rough=0.55))
    eyes = cut_eyes(body)
    if DO_FLUTES:
        cut_flutes(body)
    marker = make_marker(body, variant_rgb)
    return [body, eyes, marker]


def export(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True,
        export_apply=True, export_yup=True)


# ================================================================= main
# 単体（各色）
for name, rgb in VARIANTS.items():
    clear()
    objs = build_ghost(rgb)
    export(objs, os.path.join(OUT, f"ghost_{name}.glb"))
    print(f"  ghost_{name}.glb")

# 俯瞰（青・赤 並べる）
clear()
allobjs = []
gap = RX_BASE * 3.4
for i, (name, rgb) in enumerate(VARIANTS.items()):
    objs = build_ghost(rgb)
    dx = (i - (len(VARIANTS) - 1) / 2) * gap
    for o in objs:
        o.location.x += dx
    allobjs += objs
export(allobjs, os.path.join(OUT, "geister-ghost.glb"))
print("DONE: height=%.0fmm width=%.0fmm  ->  %s" % (
    HEIGHT * 1000, RX_BASE * 2000, OUT))
