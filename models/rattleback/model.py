"""
rattleback: 一方向にのみ滑らかに回る半楕円体。

構成:
- 本体: 長軸 A・短軸 B・深さ C の半楕円体 (底面側のみ、z≤0 の凸面)
- 上面: z=0 の平面でキャップ
- 上面に直径方向の対角位置に 2 つの円柱コブを配置 → 慣性主軸を 〜10° 回転

物理的性質:
- 曲率主軸: 幾何的には x,y 軸と一致。
- 慣性主軸: コブの対角配置により幾何軸から傾く。
- この食い違いがスピン→振動→逆転のエネルギー変換を起こす。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
import bmesh
from mathutils import Vector
from blender_utils import clear_scene, export_stl
from params import (
    A, B, C,
    BUMP_R, BUMP_H, BUMP_OFFSET_X, BUMP_OFFSET_Y,
    N_LON, N_LAT,
)

clear_scene()

# --- 半楕円体の底面メッシュを手動生成（z=-C*cos(θ), θ∈[0, π/2]） ---
mesh = bpy.data.meshes.new("rattleback_body")
bm = bmesh.new()

# 緯度 lat: 0 (赤道=上端, z=0) → π/2 (南極, z=-C)
# 経度 lon: 0..2π
lat_verts = []  # lat_verts[i][j] = 頂点
for i in range(N_LAT + 1):
    lat = i * (math.pi / 2) / N_LAT
    cos_lat = math.cos(lat)
    sin_lat = math.sin(lat)
    row = []
    for j in range(N_LON):
        lon = j * 2 * math.pi / N_LON
        x = A * cos_lat * math.cos(lon)
        y = B * cos_lat * math.sin(lon)
        z = -C * sin_lat
        row.append(bm.verts.new((x, y, z)))
    lat_verts.append(row)

# 南極の 1 点に収束させる
south_pole = bm.verts.new((0.0, 0.0, -C))

# 側面クワッド
for i in range(N_LAT):
    for j in range(N_LON):
        j2 = (j + 1) % N_LON
        v0 = lat_verts[i][j]
        v1 = lat_verts[i][j2]
        v2 = lat_verts[i + 1][j2]
        v3 = lat_verts[i + 1][j]
        bm.faces.new([v0, v1, v2, v3])

# 南極キャップ（N_LAT 番目の輪を南極点へ）
for j in range(N_LON):
    j2 = (j + 1) % N_LON
    v0 = lat_verts[N_LAT][j]
    v1 = lat_verts[N_LAT][j2]
    bm.faces.new([v0, v1, south_pole])

# 上面キャップ（赤道 z=0 を塞ぐ）: 中心点を打って扇状に
top_center = bm.verts.new((0.0, 0.0, 0.0))
for j in range(N_LON):
    j2 = (j + 1) % N_LON
    v0 = lat_verts[0][j]
    v1 = lat_verts[0][j2]
    bm.faces.new([top_center, v1, v0])

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()

body = bpy.data.objects.new("rattleback", mesh)
bpy.context.collection.objects.link(body)
bpy.context.view_layer.objects.active = body
body.select_set(True)


# --- 対角コブ 2 個を union ---
bump_positions = [
    (+BUMP_OFFSET_X, +BUMP_OFFSET_Y),
    (-BUMP_OFFSET_X, -BUMP_OFFSET_Y),
]

for (bx, by) in bump_positions:
    # 円柱を生成（底を上面より少し下げて食い込ませる）
    bpy.ops.mesh.primitive_cylinder_add(
        radius=BUMP_R,
        depth=BUMP_H + 0.001,
        vertices=48,
        location=(bx, by, BUMP_H / 2 - 0.0005),
    )
    bump = bpy.context.active_object
    bump.name = "bump"

    bpy.context.view_layer.objects.active = body
    mod = body.modifiers.new("add_bump", "BOOLEAN")
    mod.operation = "UNION"
    mod.object = bump
    mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier="add_bump")
    bpy.data.objects.remove(bump, do_unlink=True)

bpy.context.view_layer.objects.active = body
body.select_set(True)

# 設計軸ずれ角度（参考値）: 2 コブで対角配置したときの推定傾き
tilt_deg = math.degrees(math.atan2(BUMP_OFFSET_Y, BUMP_OFFSET_X))
print(f"[rattleback] bbox = {A*2*1000:.0f}x{B*2*1000:.0f}x{C*1000:.0f}mm (+bump {BUMP_H*1000:.0f}mm)")
print(f"[rattleback] bump diagonal ≒ {tilt_deg:.1f}° (inertia axis rotation hint)")

export_stl("rattleback")
