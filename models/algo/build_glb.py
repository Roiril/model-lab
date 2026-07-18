# -*- coding: utf-8 -*-
"""アルゴ (algo) カードの GLB ビルダー（Blender 5.1 / bpy）。

gen_textures.py が出力した outlines.json と tex/*.png を読み、
角丸長方形の薄板メッシュ（表=数字テクスチャ / 側面・裏=地色ソリッド）を生成し、

  - 各カード単体 GLB   exports/algo/glb/<name>.glb        （Unity 取り込み用）
  - 全部入りシーン GLB  exports/algo/algo.glb              （俯瞰／ギャラリー用）

を書き出す。テクスチャは GLB に埋め込む。
"""
import bpy, bmesh, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "algo"))
TEX = os.path.join(OUT, "tex")
GLB = os.path.join(OUT, "glb")
os.makedirs(GLB, exist_ok=True)

with open(os.path.join(OUT, "outlines.json"), encoding="utf-8") as f:
    MAN = json.load(f)

W = MAN["card_w_mm"] * 0.001
H = MAN["card_h_mm"] * 0.001
TH = MAN["thick_mm"] * 0.001
OUTLINE = MAN["outline"]   # 正規化 [-0.5,0.5]×[-0.5,0.5]


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
    bsdf.inputs["Roughness"].default_value = 0.72
    bsdf.inputs["Metallic"].default_value = 0.0
    return m


def tex_mat(name, png):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.68
    bsdf.inputs["Metallic"].default_value = 0.0
    tx = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(os.path.join(TEX, png))
    tx.image = img
    nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def make_card(name, info):
    """角丸長方形を押し出した薄板。トップ面に数字テクスチャ、側面/裏は地色ソリッド。"""
    v2d = [(x * W, y * H) for x, y in OUTLINE]

    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)

    bm = bmesh.new()
    top = [bm.verts.new((x, y, TH)) for x, y in v2d]
    bot = [bm.verts.new((x, y, 0.0)) for x, y in v2d]
    bm.verts.ensure_lookup_table()
    f_top = bm.faces.new(top)
    f_bot = bm.faces.new(list(reversed(bot)))
    n = len(v2d)
    sides = []
    for i in range(n):
        j = (i + 1) % n
        sides.append(bm.faces.new([bot[i], bot[j], top[j], top[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # UV: トップ面はカード外形 → テクスチャ全面 [0,1]。
    uvl = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for loop in f.loops:
            co = loop.vert.co
            loop[uvl].uv = (co.x / W + 0.5, co.y / H + 0.5)

    # マテリアル: トップ=数字テクスチャ, 側面/裏=地色
    ob.data.materials.append(tex_mat(name + "_top", info["tex"]))
    ob.data.materials.append(solid_mat(name + "_side", info["side_color"]))
    f_top.material_index = 0
    for s in sides:
        s.material_index = 1
    f_bot.material_index = 1

    f_top.smooth = False
    f_bot.smooth = False
    for s in sides:
        s.smooth = True
    bm.to_mesh(me)
    bm.free()
    return ob


def export_single(ob, name):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    loc = ob.location.copy()
    ob.location = (0, 0, 0)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(GLB, name + ".glb"),
        export_format="GLB", use_selection=True,
        export_apply=True, export_yup=True,
    )
    ob.location = loc


# ----------------------------------------------------------------- ビルド
clear()
objs = {}
for name, info in MAN["cards"].items():
    objs[name] = make_card(name, info)

# 単体 GLB
for name, ob in objs.items():
    export_single(ob, name)

# ----------------------------------------------------------------- 俯瞰レイアウト
# 白カード（上段）・黒カード（下段）を 0〜11 で横並び。
GX = W + 0.008          # 横間隔（カード幅 + 8mm）
GY = H + 0.012          # 段間隔（カード高 + 12mm）
x0 = -GX * (len(MAN["cards"]) / 2 - 1) / 2   # 12 枚幅を中央寄せ
for i in range(12):
    objs[f"white_{i}"].location = (x0 + i * GX, GY / 2, 0.0)
    objs[f"black_{i}"].location = (x0 + i * GX, -GY / 2, 0.0)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT, "algo.glb"),
    export_format="GLB", use_selection=True,
    export_apply=True, export_yup=True,
)

print("DONE: cards=%d  glb_dir=%s" % (len(objs), GLB))
