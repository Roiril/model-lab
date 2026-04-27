"""
shadow_trio: 三方向の影がそれぞれ異なる輪郭になる影絵彫刻。

各方向のシルエット (bbox = 2R cube 内):
- +X から見た影 (YZ 平面): 正方形  2R x 2R
- +Y から見た影 (XZ 平面): 円      半径 R
- +Z から見た影 (XY 平面): 二等辺三角形  頂点 (-R,-R), (R,-R), (0,R)

構成:
  V = Cube(2R)  ∩  Cylinder_Y(r=R, h=2R)  ∩  TriPrism_Z(h=2R)
各方向への投影が元のシルエットに一致するため、光を当てた影もそのまま出る。
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

# ---------- 1. 立方体 (X 軸押し出し = YZ 正方形シルエット) ----------
bpy.ops.mesh.primitive_cube_add(size=2 * R, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "base_cube"

# ---------- 2. Y 軸円柱 (XZ 円シルエット) ----------
# 既定軸は Z なので X 軸回りに 90° 回して軸を Y に揃える
bpy.ops.mesh.primitive_cylinder_add(
    radius=R, depth=2 * R * 1.01, vertices=N_CIRCLE, location=(0, 0, 0)
)
cyl = bpy.context.active_object
cyl.name = "cyl_y"
cyl.rotation_euler = (math.pi / 2, 0, 0)
bpy.ops.object.transform_apply(rotation=True)

# ---------- 3. Z 軸三角柱 (XY 三角形シルエット) ----------
# 三角形: (-R,-R), (R,-R), (0,R)。Boolean 面一回避で Z 方向は ±0.5mm 突き出す。
Z_EXT = R + 0.0005
tri_verts = [
    (-R, -R, -Z_EXT), (R, -R, -Z_EXT), (0.0, R, -Z_EXT),
    (-R, -R,  Z_EXT), (R, -R,  Z_EXT), (0.0, R,  Z_EXT),
]

mesh = bpy.data.meshes.new("tri_prism")
bm = bmesh.new()
v = [bm.verts.new(c) for c in tri_verts]
bm.verts.ensure_lookup_table()
# 底面 (z=-Z_EXT)・上面 (z=+Z_EXT) と側面 3 枚
bm.faces.new([v[0], v[1], v[2]])
bm.faces.new([v[5], v[4], v[3]])
bm.faces.new([v[0], v[3], v[4], v[1]])  # y=-R 側
bm.faces.new([v[1], v[4], v[5], v[2]])  # 右斜面
bm.faces.new([v[2], v[5], v[3], v[0]])  # 左斜面
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()

tri = bpy.data.objects.new("tri_prism", mesh)
bpy.context.collection.objects.link(tri)

# ---------- Boolean: cube ∩ cyl ∩ tri ----------
def boolean_intersect(target, tool):
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new("isect", "BOOLEAN")
    mod.operation = "INTERSECT"
    mod.object = tool
    mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier="isect")
    bpy.data.objects.remove(tool, do_unlink=True)

boolean_intersect(cube, cyl)
boolean_intersect(cube, tri)

cube.name = "shadow_trio"
bpy.context.view_layer.objects.active = cube
cube.select_set(True)

# ---------- 外形ログ ----------
xs = [v.co.x for v in cube.data.vertices]
ys = [v.co.y for v in cube.data.vertices]
zs = [v.co.z for v in cube.data.vertices]
bb = (
    (max(xs) - min(xs)) * 1000,
    (max(ys) - min(ys)) * 1000,
    (max(zs) - min(zs)) * 1000,
)
print(
    f"[shadow_trio] R = {R*1000:.1f}mm, "
    f"bbox = {bb[0]:.1f} x {bb[1]:.1f} x {bb[2]:.1f} mm, "
    f"verts = {len(cube.data.vertices)}, faces = {len(cube.data.polygons)}"
)

export_stl("shadow_trio")
