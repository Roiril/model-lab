# -*- coding: utf-8 -*-
"""ガイスター盤の GLB ビルダー（Blender 5.1 / bpy）。

gen_texture.py が出力した exports/geister/tex/board.jpg を読み、
正方形の薄板メッシュ（表=盤面写真テクスチャ / 側面・裏=黒ソリッド）を生成して

  exports/geister/geister.glb   （テクスチャ埋め込み・Unity 取り込み用）

を書き出す。algo（models/algo/build_glb.py）と同じライン。
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy, bmesh
from params import BOARD_W, BOARD_D, BOARD_T, SIDE_COLOR

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "geister"))
TEX = os.path.join(OUT, "tex")


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for d in list(blk):
            blk.remove(d)


def srgb_to_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def solid_mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    r, g, b = [srgb_to_lin(x) for x in rgb[:3]]
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.75
    bsdf.inputs["Metallic"].default_value = 0.0
    return m


def tex_mat(name, path):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.62
    bsdf.inputs["Metallic"].default_value = 0.0
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(path)
    nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def make_board():
    """正方形を押し出した薄板。トップ面に盤面写真、側面/裏は黒ソリッド。"""
    hw, hd = BOARD_W / 2, BOARD_D / 2
    v2d = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]

    me = bpy.data.meshes.new("geister_board")
    ob = bpy.data.objects.new("geister_board", me)
    bpy.context.collection.objects.link(ob)

    bm = bmesh.new()
    top = [bm.verts.new((x, y, BOARD_T)) for x, y in v2d]
    bot = [bm.verts.new((x, y, 0.0)) for x, y in v2d]
    f_top = bm.faces.new(top)
    f_bot = bm.faces.new(list(reversed(bot)))
    sides = []
    for i in range(4):
        j = (i + 1) % 4
        sides.append(bm.faces.new([bot[i], bot[j], top[j], top[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # UV: トップ面 = 盤外形 → テクスチャ全面 [0,1]
    uvl = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for loop in f.loops:
            co = loop.vert.co
            loop[uvl].uv = (co.x / BOARD_W + 0.5, co.y / BOARD_D + 0.5)

    ob.data.materials.append(tex_mat("board_top", os.path.join(TEX, "board.jpg")))
    ob.data.materials.append(solid_mat("board_side", SIDE_COLOR))
    f_top.material_index = 0
    f_bot.material_index = 1
    for s in sides:
        s.material_index = 1
    for f in bm.faces:
        f.smooth = False

    bm.to_mesh(me)
    bm.free()
    return ob


clear()
ob = make_board()
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = ob
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT, "geister.glb"),
    export_format="GLB", use_selection=True,
    export_apply=True, export_yup=True,
    export_image_format="JPEG",
)
print("DONE: %s  (%.0f x %.0f x %.1f mm)" % (
    os.path.join(OUT, "geister.glb"),
    BOARD_W * 1000, BOARD_D * 1000, BOARD_T * 1000))
