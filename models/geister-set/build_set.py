# -*- coding: utf-8 -*-
"""ガイスター一式（盤 + コマ16体）を開始配置で1つの GLB にまとめる（Blender 5.1 / bpy）。

既に書き出し済みのアセット GLB を読み込んで配置するだけ（造形コードは各モデル側が正）:

  exports/geister/geister.glb            盤（390×390mm）
  exports/geister-ghost/ghost_blue.glb   青コマ（単体）
  exports/geister-ghost/ghost_red.glb    赤コマ（単体）

実ゲームの開始配置に倣い、中央4列 × 各プレイヤー手前2段 = 8マスに配置。
手前側=青8体（目は奥＝相手向き, マーカーは手前）、奥側=赤8体（180°回転）。
コマはメッシュ共有のリンク複製なので、16体でも軽量。

  → exports/geister-set/geister-set.glb

実行: ./run.sh models/geister-set/build_set.py
"""
import bpy, os, math, mathutils

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
EXP = os.path.join(ROOT, "exports")
OUT = os.path.join(EXP, "geister-set")
os.makedirs(OUT, exist_ok=True)

CELL = 0.390 / 6           # 65mm 角マス
BOARD_TOP = 0.002          # 盤の上面 z


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for d in list(blk):
            blk.remove(d)


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def flatten(objs, name):
    """読み込んだ複数オブジェクトを world 座標に焼き、1メッシュへ結合して返す。"""
    meshes = [o for o in objs if o.type == "MESH"]
    others = [o for o in objs if o.type != "MESH"]
    # 親（gltf import の空ルート等）の変換をメッシュへ焼いてから独立させる
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if any(o.parent for o in meshes):
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    # 残った空オブジェクトを掃除（結合で消えたメッシュ参照は触らない）
    for o in others:
        try:
            bpy.data.objects.remove(o, do_unlink=True)
        except (ReferenceError, RuntimeError):
            pass
    return obj


clear()

# --- 盤 ---
board = flatten(import_glb(os.path.join(EXP, "geister", "geister.glb")), "board")

# --- コマの素体（各色1体だけ実体・以降はリンク複製） ---
blue = flatten(import_glb(os.path.join(EXP, "geister-ghost", "ghost_blue.glb")), "blue_proto")
red = flatten(import_glb(os.path.join(EXP, "geister-ghost", "ghost_red.glb")), "red_proto")

# 赤（奥プレイヤー）は 180°回してから焼き込む（顔が手前=相手向き、マーカーは奥）。
# ※ bpy.ops の回転はバックグラウンドで効かないことがあるためメッシュを直接変換する。
red.data.transform(mathutils.Matrix.Rotation(math.pi, 4, "Z"))

blue.hide_set(True)
red.hide_set(True)

# 開始配置: 中央4列（x = ±0.5, ±1.5 マス）× 各陣2段
XCOLS = [c * CELL for c in (-1.5, -0.5, 0.5, 1.5)]
NEAR_YS = [-2.5 * CELL, -1.5 * CELL]    # 手前プレイヤー（青）
FAR_YS = [2.5 * CELL, 1.5 * CELL]       # 奥プレイヤー（赤）

placed = [board]


def place(proto, x, y):
    o = proto.copy()                     # リンク複製（メッシュ共有）
    o.hide_set(False)
    bpy.context.collection.objects.link(o)
    o.location = (x, y, BOARD_TOP)        # 底 z=0 を盤上面へ
    placed.append(o)


for y in NEAR_YS:                        # 手前=青（マーカーが手前=自陣向き）
    for x in XCOLS:
        place(blue, x, y)
for y in FAR_YS:                         # 奥=赤（素体で180°済み。顔が手前）
    for x in XCOLS:
        place(red, x, y)

# --- 書き出し ---
bpy.ops.object.select_all(action="DESELECT")
for o in placed:
    o.select_set(True)
bpy.context.view_layer.objects.active = board
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT, "geister-set.glb"),
    export_format="GLB", use_selection=True,
    export_apply=True, export_yup=True, export_image_format="JPEG")
print("DONE: geister-set.glb  盤 + 青8 + 赤8  ->  %s" % OUT)
