# -*- coding: utf-8 -*-
"""バンディド (Bandido) カードの GLB ビルダー（Blender 5.1 / bpy）。

gen_textures.py が出力した outlines.json と tex/*.png を読み、
角丸長方形の薄板メッシュ（表=カード面テクスチャ / 裏=共通 ura / 側面=地色ソリッド）
を生成し、

  - 各カード単体 GLB   exports/bandido/glb/<name>.glb
  - 全部入りシーン GLB  exports/bandido/bandido.glb   （8列x4段の俯瞰ギャラリー）

を書き出す。テクスチャは GLB に埋め込む。裏面 ura は単一 image データブロックを
共有し、一括 GLB では 1 枚だけ埋め込まれる（glTF エクスポータが重複排除する）。
"""
import bpy, bmesh, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import copies_of

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "bandido"))
TEX = os.path.join(OUT, "tex")
GLB = os.path.join(OUT, "glb")
os.makedirs(GLB, exist_ok=True)

with open(os.path.join(OUT, "outlines.json"), encoding="utf-8") as f:
    MAN = json.load(f)

W = MAN["card_w_mm"] * 0.001
H = MAN["card_h_mm"] * 0.001
TH = MAN["thick_mm"] * 0.001
OUTLINE = MAN["outline"]          # 正規化 [-0.5,0.5]x[-0.5,0.5]
BACK_TEX = MAN["back_tex"]


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
    bsdf.inputs["Roughness"].default_value = 0.74
    bsdf.inputs["Metallic"].default_value = 0.0
    return m


_img_cache = {}
def load_img(png):
    if png not in _img_cache:
        _img_cache[png] = bpy.data.images.load(os.path.join(TEX, png))
    return _img_cache[png]


def tex_mat(name, png):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.66
    bsdf.inputs["Metallic"].default_value = 0.0
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = load_img(png)
    nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
    return m


# 裏面(ura)マテリアルは全カード共有（image データブロックも 1 つ）
_back_mat = None
def back_mat():
    global _back_mat
    if _back_mat is None:
        _back_mat = tex_mat("back_ura", BACK_TEX)
    return _back_mat


def make_card(name, info):
    """角丸長方形の薄板。表=面テクスチャ / 裏=ura / 側面=地色。"""
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

    uvl = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for loop in f.loops:
            co = loop.vert.co
            if f is f_bot:
                # 裏面: 長辺(Y)軸で表を裏返した見えになるよう U を反転
                loop[uvl].uv = (0.5 - co.x / W, 0.5 + co.y / H)
            else:
                loop[uvl].uv = (co.x / W + 0.5, co.y / H + 0.5)

    # マテリアル: 0=表テクスチャ, 1=側面地色, 2=裏 ura
    ob.data.materials.append(tex_mat(name + "_top", info["tex"]))
    ob.data.materials.append(solid_mat(name + "_side", info["side_color"]))
    ob.data.materials.append(back_mat())
    f_top.material_index = 0
    for s in sides:
        s.material_index = 1
    f_bot.material_index = 2

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
        export_image_format="JPEG", export_jpeg_quality=90,
    )
    ob.location = loc


# ----------------------------------------------------------------- ビルド
clear()
names = list(MAN["cards"].keys())
objs = {n: make_card(n, MAN["cards"][n]) for n in names}

# 単体 GLB
for n in names:
    export_single(objs[n], n)

# ----------------------------------------------------------------- 俯瞰レイアウト
# 実物のデッキ構成で並べる: g*=各2枚, l*=各3枚, bandy=1枚。
# 追加分はリンク複製（メッシュ/マテリアルを共有 → GLB は画像を重複排除）。
instances = []
for n in names:
    instances.append(objs[n])
    for _ in range(copies_of(n) - 1):
        dup = objs[n].copy()                 # data をリンク共有した複製
        bpy.context.collection.objects.link(dup)
        instances.append(dup)

COLS = 10
GX = W + 0.006
GY = H + 0.008
rows = (len(instances) + COLS - 1) // COLS
x0 = -GX * (COLS - 1) / 2
y0 = GY * (rows - 1) / 2
for i, ob in enumerate(instances):
    r, c = divmod(i, COLS)
    ob.location = (x0 + c * GX, y0 - r * GY, 0.0)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT, "bandido.glb"),
    export_format="GLB", use_selection=True,
    export_apply=True, export_yup=True,
    export_image_format="JPEG", export_jpeg_quality=90,
)

print("DONE: kinds=%d  deck=%d  rows=%dx%d  glb_dir=%s" %
      (len(names), len(instances), rows, COLS, GLB))
