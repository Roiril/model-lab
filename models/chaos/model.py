"""
chaos: トレフォイル結び目チューブ。
- 芯: 3葉結び (sin(t)+2sin(2t), cos(t)-2cos(2t), -sin(3t))
- 断面: 5本スパイクの星が、軸に沿って3回ねじれつつモーフィング
- 表面: 追加の正弦波うねり
- フレーム: 上方向(Z)からの投影で作る周期的な法線フレーム
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
    KNOT_SCALE, TUBE_R, TWIST_TURNS, SPIKE_COUNT,
    SPIKE_MORPH_FREQ, SURFACE_WAVE_FREQ_T, SURFACE_WAVE_FREQ_J,
    SURFACE_WAVE_AMP, N_STEPS, N_CROSS,
)

clear_scene()


def trefoil(t):
    s = KNOT_SCALE
    x = (math.sin(t) + 2 * math.sin(2 * t)) * s
    y = (math.cos(t) - 2 * math.cos(2 * t)) * s
    z = -math.sin(3 * t) * s
    return Vector((x, y, z))


def trefoil_tangent(t):
    s = KNOT_SCALE
    dx = (math.cos(t) + 4 * math.cos(2 * t)) * s
    dy = (-math.sin(t) + 4 * math.sin(2 * t)) * s
    dz = -3 * math.cos(3 * t) * s
    return Vector((dx, dy, dz)).normalized()


def frame(t):
    """周期的な(T,N,B)フレーム。Z軸を射影することで t の連続関数になり、
    かつ t=0 と t=2π で必ず一致する（ホロノミーなし）。"""
    T = trefoil_tangent(t)
    up = Vector((0.0, 0.0, 1.0))
    N = up - T * T.dot(up)
    if N.length < 1e-6:
        up = Vector((1.0, 0.0, 0.0))
        N = up - T * T.dot(up)
    N.normalize()
    B = T.cross(N).normalized()
    return T, N, B


def cross_section_radius(t, angle):
    """断面の半径関数。スパイク星 + うねり + モーフ。"""
    # 星型スパイク: cos(SPIKE_COUNT * angle) を [0,1] にマップ
    spike = 0.5 + 0.5 * math.cos(SPIKE_COUNT * angle + TWIST_TURNS * t)
    # スパイクの強さが結び目1周ごとに変動
    spike_strength = 0.5 + 0.35 * math.sin(SPIKE_MORPH_FREQ * t)
    # 表面波
    wave = SURFACE_WAVE_AMP * math.sin(
        SURFACE_WAVE_FREQ_T * t + SURFACE_WAVE_FREQ_J * angle
    )
    base = 0.60 + 0.45 * spike * spike_strength + wave
    return TUBE_R * max(0.45, base)  # 下限クランプで薄肉事故を防ぐ


# --- メッシュ生成 ---
verts = []
for i in range(N_STEPS):
    t = i * 2 * math.pi / N_STEPS
    C = trefoil(t)
    T, N, B = frame(t)
    for j in range(N_CROSS):
        a = j * 2 * math.pi / N_CROSS
        r = cross_section_radius(t, a)
        P = C + N * (math.cos(a) * r) + B * (math.sin(a) * r)
        verts.append(P)

mesh = bpy.data.meshes.new("chaos")
bm = bmesh.new()
bm_verts = [bm.verts.new(v) for v in verts]
bm.verts.ensure_lookup_table()

for i in range(N_STEPS):
    i2 = (i + 1) % N_STEPS
    for j in range(N_CROSS):
        j2 = (j + 1) % N_CROSS
        v0 = bm_verts[i * N_CROSS + j]
        v1 = bm_verts[i * N_CROSS + j2]
        v2 = bm_verts[i2 * N_CROSS + j2]
        v3 = bm_verts[i2 * N_CROSS + j]
        # 外向きCCW: T方向に i→i2、周方向に j→j2 で外側から見て反時計
        bm.faces.new([v0, v3, v2, v1])

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("chaos", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

export_stl("chaos")
