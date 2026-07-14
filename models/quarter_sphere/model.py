"""
quarter_sphere (8分割版): 直径400mm 中空球の 1/8 = オクタント 1パーツ。

- 外半径200mm / 肉厚3mm の中空シェルを x=0, y=0, z=0 の3平面で8分割。
- 出力は1パーツ（上半球の1/4）。上半球に4個、下半球に4個（同パーツを
  天地反転）印刷し、計8個を接合すると球になる。1パーツ ~200x200x200mm。
- 位置決めは「両合わせ面とも穴」＋別体ダボ（径5mm丸棒）。造形物に出っ張り
  が無いので印刷が崩れない。縦シーム穴は水平ボア、赤道シーム穴は垂直ボア。
- 全パーツ同一形状＆穴位置が回転・反転対称なので、隣接面のダボ穴が必ず一致。

推奨印刷向き: 赤道面(z=0)をベッドに伏せて極を上に。出っ張り無し。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
from blender_utils import clear_scene, export_stl
from params import (
    R_OUT, R_IN, SPHERE_SEG, SPHERE_RING,
    FLANGE_T, FLANGE_DEPTH,
    HOLE_D, HOLE_DEPTH, VHOLE_Z, EHOLE_AZ,
)

clear_scene()


def _activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def boolean(target, cutter, op):
    _activate(target)
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def uv_sphere(radius, name):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius, segments=SPHERE_SEG, ring_count=SPHERE_RING
    )
    o = bpy.context.active_object
    o.name = name
    return o


def box(name, cx, cy, cz, sx, sy, sz):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    _activate(o)
    bpy.ops.object.transform_apply(scale=True)
    return o


def cylinder(name, radius, length, axis, cx, cy, cz):
    """axis='X'|'Y'|'Z'。Z は無回転（垂直ボア）。"""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, vertices=48)
    o = bpy.context.active_object
    o.name = name
    if axis == "Y":
        o.rotation_euler = (math.pi / 2, 0, 0)
    elif axis == "X":
        o.rotation_euler = (0, math.pi / 2, 0)
    o.location = (cx, cy, cz)
    _activate(o)
    bpy.ops.object.transform_apply(rotation=True)
    return o


BIG = 1.0  # カッター用の十分大きい寸法

# --- 1. 中空シェル（全球） ---
shell = uv_sphere(R_OUT, "quarter_sphere")
inner = uv_sphere(R_IN, "inner_cut")
boolean(shell, inner, "DIFFERENCE")

# --- 2. 接合フランジ: 球内面から内側 FLANGE_DEPTH の球殻バンドを、
#        x=0 / y=0 / z=0 の3平面沿いスラブで抜いてリブ化 ---
band = uv_sphere(R_IN + 0.0008, "band")
band_in = uv_sphere(R_IN - FLANGE_DEPTH, "band_in")
boolean(band, band_in, "DIFFERENCE")

# 各スラブは合わせ面を 0.002 はみ出させ、平面に面を作らない（後の平面カットで
# クリーンな合わせ面を生成 / coplanar Boolean を回避）
slab_y = box("slab_y", 0, (FLANGE_T - 0.002) / 2, 0, BIG, FLANGE_T + 0.002, BIG)
slab_x = box("slab_x", (FLANGE_T - 0.002) / 2, 0, 0, FLANGE_T + 0.002, BIG, BIG)
slab_z = box("slab_z", 0, 0, (FLANGE_T - 0.002) / 2, BIG, BIG, FLANGE_T + 0.002)
boolean(slab_y, slab_x, "UNION")
boolean(slab_y, slab_z, "UNION")          # x=0,y=0,z=0 沿いの十字スラブ
boolean(band, slab_y, "INTERSECT")        # フランジリブ
boolean(shell, band, "UNION")

# --- 3. オクタントへ分割（y<0, x<0, z<0 を除去 → 上半球の +x+y 1/4） ---
boolean(shell, box("c_y", 0, -BIG / 2, 0, BIG, BIG, BIG), "DIFFERENCE")
boolean(shell, box("c_x", -BIG / 2, 0, 0, BIG, BIG, BIG), "DIFFERENCE")
boolean(shell, box("c_z", 0, 0, -BIG / 2, BIG, BIG, BIG), "DIFFERENCE")

# --- 4. ダボ穴（突き出しピンは無し） ---
hole_len = HOLE_DEPTH + 0.001

# 4a. 縦シーム: y=0 面と x=0 面の両方に、同じ (z, 半径) で穴
for z in VHOLE_Z:
    r = math.sqrt(R_IN ** 2 - z ** 2) - FLANGE_DEPTH * 0.5  # フランジ中央付近
    # y=0 面: +y へ掘る（軸Y）
    boolean(shell,
            cylinder("h_y", HOLE_D / 2, hole_len, "Y",
                     r, (HOLE_DEPTH - 0.001) / 2, z),
            "DIFFERENCE")
    # x=0 面: +x へ掘る（軸X）
    boolean(shell,
            cylinder("h_x", HOLE_D / 2, hole_len, "X",
                     (HOLE_DEPTH - 0.001) / 2, r, z),
            "DIFFERENCE")

# 4b. 赤道シーム: z=0 面に垂直(軸Z)の穴。方位角 EHOLE_AZ、半径はフランジ中央
r_eq = R_IN - FLANGE_DEPTH * 0.5
for az in EHOLE_AZ:
    boolean(shell,
            cylinder("h_z", HOLE_D / 2, hole_len, "Z",
                     r_eq * math.cos(az), r_eq * math.sin(az),
                     (HOLE_DEPTH - 0.001) / 2),
            "DIFFERENCE")

_activate(shell)
print(f"[quarter_sphere/8分割] 外径 {R_OUT*2*1000:.0f}mm / 肉厚 {(R_OUT-R_IN)*1000:.1f}mm")
print(f"  1パーツ bbox ~ {R_OUT*1000:.0f} x {R_OUT*1000:.0f} x {R_OUT*1000:.0f} mm")
print(f"  縦シーム穴 {len(VHOLE_Z)}個/面 x2面, 赤道穴 {len(EHOLE_AZ)}個")
print(f"  穴径 {HOLE_D*1000:.1f}mm 深 {HOLE_DEPTH*1000:.0f}mm / ダボ径 5.0mm")

export_stl("quarter_sphere")
