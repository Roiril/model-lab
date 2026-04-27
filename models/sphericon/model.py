"""
sphericon: 単一の連続曲面を持つ立体。

構成:
- 正方形断面（対角線が軸）を持つ双錐を、軸を含む平面で半分に切り
  片方を 90° 回したものと接合した形。
- 4 つの半円錐面 (strip 1..4) が、2 本の半円リッジと 4 本の直線スロープで接続される。
- 頂点は 4 つ: (±R, 0, 0), (0, 0, ±R)

物理的性質:
- 平面上で転がすと、重心が直線的に進みつつ全表面がレールに触れる（蛇行転がり）。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
import bmesh
from blender_utils import clear_scene, export_stl
from params import R, SEG

clear_scene()

mesh = bpy.data.meshes.new("sphericon")
bm = bmesh.new()

# 4 頂点（双錐の「角」）
apex_top = bm.verts.new((0.0, 0.0,  R))   # Z 軸双錐の上頂点
apex_bot = bm.verts.new((0.0, 0.0, -R))   # Z 軸双錐の下頂点
apex_px  = bm.verts.new(( R, 0.0, 0.0))   # X 軸双錐の正方頂点
apex_nx  = bm.verts.new((-R, 0.0, 0.0))   # X 軸双錐の負方頂点

# リッジ1: y>=0 半円 (XY 平面の z=0 円の前半分)
#   strip 1 (apex_top) と strip 2 (apex_bot) の共有ベース
ridge_xy = [apex_px]
for j in range(1, SEG):
    theta = j * math.pi / SEG
    ridge_xy.append(bm.verts.new((R * math.cos(theta), R * math.sin(theta), 0.0)))
ridge_xy.append(apex_nx)

# リッジ2: y<=0 半円 (YZ 平面の x=0 円の後半分)
#   strip 3 (apex_px) と strip 4 (apex_nx) の共有ベース
ridge_yz = [apex_top]
for j in range(1, SEG):
    phi = j * math.pi / SEG
    ridge_yz.append(bm.verts.new((0.0, -R * math.sin(phi), R * math.cos(phi))))
ridge_yz.append(apex_bot)

# Strip 1: apex_top から ridge_xy への扇（上側・前方の半円錐）
for j in range(SEG):
    bm.faces.new([apex_top, ridge_xy[j], ridge_xy[j + 1]])

# Strip 2: apex_bot から ridge_xy への扇（下側・前方の半円錐）
for j in range(SEG):
    bm.faces.new([apex_bot, ridge_xy[j + 1], ridge_xy[j]])

# Strip 3: apex_px から ridge_yz への扇（右側・後方の半円錐）
for j in range(SEG):
    bm.faces.new([apex_px, ridge_yz[j + 1], ridge_yz[j]])

# Strip 4: apex_nx から ridge_yz への扇（左側・後方の半円錐）
for j in range(SEG):
    bm.faces.new([apex_nx, ridge_yz[j], ridge_yz[j + 1]])

# 法線を外向きに統一
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("sphericon", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

print(f"[sphericon] R = {R*1000:.1f}mm, bbox = {R*2*1000:.0f}x{R*2*1000:.0f}x{R*2*1000:.0f}mm")

export_stl("sphericon")
