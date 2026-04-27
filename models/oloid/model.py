"""
oloid: 2 つの直交する同半径円の凸包として定義される立体。

構成:
- 円 A: 中心 (-R/2, 0, 0)、XZ 平面内、半径 R
- 円 B: 中心 (+R/2, 0, 0)、XY 平面内、半径 R
- 各中心は他方の円周上に載る（間隔 = R）。
- 2 円の頂点を全部集めて凸包を取れば oloid が得られる。

物理的性質:
- 平面上で転がすと「全表面」が順番に床に触れる（面全部が接地線を通る）。
- 展開すると単一の連続した展開図になる（developable 曲面）。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
import bmesh
from blender_utils import clear_scene, export_stl
from params import R, N_CIRCLE

clear_scene()

mesh = bpy.data.meshes.new("oloid")
bm = bmesh.new()

# 円 A: XZ 平面 (y=0)、中心 (-R/2, 0, 0)
for i in range(N_CIRCLE):
    a = i * 2.0 * math.pi / N_CIRCLE
    bm.verts.new((-R * 0.5 + R * math.cos(a), 0.0, R * math.sin(a)))

# 円 B: XY 平面 (z=0)、中心 (+R/2, 0, 0)
for i in range(N_CIRCLE):
    b = i * 2.0 * math.pi / N_CIRCLE
    bm.verts.new((R * 0.5 + R * math.cos(b), R * math.sin(b), 0.0))

# 凸包で oloid を生成
bmesh.ops.convex_hull(bm, input=bm.verts)

# 内部の重複頂点・未使用要素を掃除
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("oloid", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# 外形寸法（bbox）
xs = [v.co.x for v in mesh.vertices]
ys = [v.co.y for v in mesh.vertices]
zs = [v.co.z for v in mesh.vertices]
bb = ((max(xs) - min(xs)) * 1000, (max(ys) - min(ys)) * 1000, (max(zs) - min(zs)) * 1000)
print(f"[oloid] R = {R*1000:.1f}mm, bbox = {bb[0]:.1f}x{bb[1]:.1f}x{bb[2]:.1f}mm")

export_stl("oloid")
