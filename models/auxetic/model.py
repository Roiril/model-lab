"""
auxetic: 再入射六角格子プレート。

構成:
- 平板 (PLATE_W x PLATE_H x PLATE_T) を用意。
- 蝶ネクタイ形の穴 (再入射六角) を NX x NY の格子状にブーリアン差分。
- 穴と穴の間に細いブリッジが残り、これが張力下で「ねじれ」ることで
  横方向にも広がる = 負のポアソン比挙動が現れる。

物理的性質:
- 普通の材料（ゴム・プラ）は引っ張ると横に細くなるが、この構造は逆に太くなる。
- PLA で印刷しても、ブリッジ部が薄いため弾性的にねじれる。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import bmesh
from blender_utils import clear_scene, export_stl
from params import PLATE_W, PLATE_H, PLATE_T, NX, NY, CELL_DX, CELL_DY, BOW_W, BOW_H, BOW_w

clear_scene()


def make_bowtie_cutter(cx, cy, W, H, w, z0, z1, name="cut"):
    """再入射六角（蝶ネクタイ）形のプリズムを作る。"""
    v2d = [
        (-W / 2 + cx, +H / 2 + cy),   # 0: TL
        (-w / 2 + cx,  0     + cy),   # 1: WL (ウエスト左)
        (-W / 2 + cx, -H / 2 + cy),   # 2: BL
        (+W / 2 + cx, -H / 2 + cy),   # 3: BR
        (+w / 2 + cx,  0     + cy),   # 4: WR (ウエスト右)
        (+W / 2 + cx, +H / 2 + cy),   # 5: TR
    ]
    # 凹多角形なので手動で三角形化（4 三角形）
    tris = [(0, 1, 5), (1, 4, 5), (1, 2, 4), (2, 3, 4)]

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in v2d]
    top = [bm.verts.new((x, y, z1)) for x, y in v2d]

    # 底面: -Z 法線 (頂点順を反転)
    for a, b, c in tris:
        bm.faces.new([bot[a], bot[c], bot[b]])
    # 上面: +Z 法線
    for a, b, c in tris:
        bm.faces.new([top[a], top[b], top[c]])
    # 側面: 多角形の辺を上下でつなぐクワッド
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
    for a, b in edges:
        bm.faces.new([bot[a], bot[b], top[b], top[a]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ベースプレート
bpy.ops.mesh.primitive_cube_add(size=1)
plate = bpy.context.active_object
plate.name = "auxetic"
plate.scale = (PLATE_W / 2, PLATE_H / 2, PLATE_T / 2)
bpy.ops.object.transform_apply(scale=True)

# 全カッターを一度の boolean でまとめて差分（高速化）
bpy.context.view_layer.objects.active = plate
cutters = []
for i in range(NX):
    for j in range(NY):
        cx = (i - (NX - 1) / 2) * CELL_DX
        cy = (j - (NY - 1) / 2) * CELL_DY
        cutter = make_bowtie_cutter(
            cx, cy, BOW_W, BOW_H, BOW_w,
            -PLATE_T,   # 余裕をもって貫通
            +PLATE_T,
            name=f"bow_{i}_{j}",
        )
        cutters.append(cutter)

# 全てを一つのオブジェクトに join してから boolean すると速い
bpy.ops.object.select_all(action="DESELECT")
for c in cutters:
    c.select_set(True)
cutters[0].select_set(True)
bpy.context.view_layer.objects.active = cutters[0]
bpy.ops.object.join()
all_cutters = bpy.context.active_object

bpy.context.view_layer.objects.active = plate
plate.select_set(True)
mod = plate.modifiers.new("cut", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = all_cutters
mod.solver = "EXACT"
bpy.ops.object.modifier_apply(modifier="cut")
bpy.data.objects.remove(all_cutters, do_unlink=True)

bpy.context.view_layer.objects.active = plate
plate.select_set(True)

# 最小ブリッジ幅（情報出力）
bridge_x = CELL_DX - BOW_W   # 横方向の最薄部
bridge_y = CELL_DY - BOW_H   # 縦方向の最薄部
print(f"[auxetic] plate = {PLATE_W*1000:.0f}x{PLATE_H*1000:.0f}x{PLATE_T*1000:.1f}mm")
print(f"[auxetic] cells = {NX}x{NY}, bridge = {bridge_x*1000:.1f}x{bridge_y*1000:.1f}mm")

export_stl("auxetic")
