"""
wobbler: ねじれコブ塔。FDMサポート無しで自立する"ギリギリ変な形"。

設計意図:
- 底面(z=0)と頂面(z=HEIGHT)は完全な平面でキャップ、ベッド密着OK
- 任意の zスライスで、外側輪郭のローカル dr/dz が 45° 以内
- コブ・花弁・ねじれを重ねて異形感を最大化
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
    HEIGHT, R_BASE, R_TOP,
    LOBE_COUNT, LOBE_AMP,
    TWIST_TURNS,
    BUMP_FREQ, BUMP_AMP,
    RIPPLE_FREQ_J, RIPPLE_AMP,
    N_STEPS, N_CROSS,
    MAX_OVERHANG_SLOPE,
)

clear_scene()


def radius(z, angle):
    """z (0..HEIGHT) と周方向角 angle から外半径を返す。"""
    u = z / HEIGHT  # 0..1

    # 基本テーパー（下→上に細くなる）
    r_base = R_BASE * (1.0 - u) + R_TOP * u

    # 軸方向コブ: 上に行くほど振幅を減衰（頂点で破綻しないよう）
    bump = BUMP_AMP * (1.0 - u) * math.sin(2 * math.pi * BUMP_FREQ * u)

    # 花弁（ねじれ付き）
    twist = 2 * math.pi * TWIST_TURNS * u
    lobe = LOBE_AMP * math.cos(LOBE_COUNT * angle + twist)

    # 周方向リップル
    ripple = RIPPLE_AMP * math.sin(RIPPLE_FREQ_J * angle + 4 * math.pi * u)

    r = r_base * (1.0 + bump + lobe * (1.0 - 0.3 * u) + ripple)
    return max(r, 0.0015)  # 1.5mm 下限


# --- オーバーハング事前チェック（数値微分で検証） ---
def check_overhang():
    dz = HEIGHT / N_STEPS
    worst = 0.0
    for i in range(N_STEPS):
        z0 = i * dz
        z1 = z0 + dz
        for j in range(N_CROSS):
            a = j * 2 * math.pi / N_CROSS
            r0 = radius(z0, a)
            r1 = radius(z1, a)
            slope = (r1 - r0) / dz  # 正: 広がる（=オーバーハング側）
            if slope > worst:
                worst = slope
    return worst


worst_slope = check_overhang()
print(f"[wobbler] worst dr/dz = {worst_slope:.3f} (limit {MAX_OVERHANG_SLOPE})")
if worst_slope > MAX_OVERHANG_SLOPE:
    print(f"[wobbler] WARNING: overhang exceeds safe limit")


# --- 側面メッシュ生成 ---
verts = []
for i in range(N_STEPS + 1):
    z = i * HEIGHT / N_STEPS
    for j in range(N_CROSS):
        a = j * 2 * math.pi / N_CROSS
        r = radius(z, a)
        verts.append(Vector((r * math.cos(a), r * math.sin(a), z)))

# キャップ中心頂点
bottom_center_idx = len(verts)
verts.append(Vector((0.0, 0.0, 0.0)))
top_center_idx = len(verts)
verts.append(Vector((0.0, 0.0, HEIGHT)))

mesh = bpy.data.meshes.new("wobbler")
bm = bmesh.new()
bm_verts = [bm.verts.new(v) for v in verts]
bm.verts.ensure_lookup_table()

# 側面クワッド
for i in range(N_STEPS):
    for j in range(N_CROSS):
        j2 = (j + 1) % N_CROSS
        v0 = bm_verts[i * N_CROSS + j]
        v1 = bm_verts[i * N_CROSS + j2]
        v2 = bm_verts[(i + 1) * N_CROSS + j2]
        v3 = bm_verts[(i + 1) * N_CROSS + j]
        # 外向きCCW: 下→上、j→j2 で外から見て反時計
        bm.faces.new([v0, v3, v2, v1])

# ボトムキャップ（下から見てCCW = 上から見てCW → [center, j2, j]）
bc = bm_verts[bottom_center_idx]
for j in range(N_CROSS):
    j2 = (j + 1) % N_CROSS
    v0 = bm_verts[j]
    v1 = bm_verts[j2]
    bm.faces.new([bc, v1, v0])

# トップキャップ（上から見てCCW = [center, j, j2]）
tc = bm_verts[top_center_idx]
base_top = N_STEPS * N_CROSS
for j in range(N_CROSS):
    j2 = (j + 1) % N_CROSS
    v0 = bm_verts[base_top + j]
    v1 = bm_verts[base_top + j2]
    bm.faces.new([tc, v0, v1])

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("wobbler", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

export_stl("wobbler")
