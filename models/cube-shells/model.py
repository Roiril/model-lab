import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import *


def make_shell(cavity, wall=WALL, origin=(0.0, 0.0)):
    """一辺 cavity の立方体を上方向にくりぬいたシェルを作る。底面 z=0。"""
    outer_xy = cavity + wall * 2
    outer_z = cavity + wall          # 底 1 枚ぶんだけ足す（上は開口）
    ox, oy = origin

    bpy.ops.mesh.primitive_cube_add(size=1)
    base = bpy.context.active_object
    base.name = f"shell_{int(round(cavity * 1000))}"
    base.scale = (outer_xy, outer_xy, outer_z)
    bpy.ops.object.transform_apply(scale=True)
    base.location = (ox, oy, outer_z / 2)

    bpy.ops.mesh.primitive_cube_add(size=1)
    cut = bpy.context.active_object
    cut.scale = (cavity, cavity, cavity + CUT_MARGIN)
    bpy.ops.object.transform_apply(scale=True)
    # 底から wall だけ上に空洞の底、上端は天面より CUT_MARGIN 突き出す
    cut.location = (ox, oy, wall + (cavity + CUT_MARGIN) / 2)

    mod = base.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cut
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.modifier_apply(modifier="cut")
    bpy.data.objects.remove(cut, do_unlink=True)

    return base, outer_xy, outer_z


# --- 個別に 1 つずつ書き出す ---
for cavity in CAVITY_SIZES:
    mm = int(round(cavity * 1000))
    clear_scene()
    _, oxy, oz = make_shell(cavity)
    print(f"[shell {mm}] outer {oxy*1000:.1f} x {oxy*1000:.1f} x {oz*1000:.1f} mm")
    export_stl(f"cube-shell-{mm}")

# --- 4 個を横に並べたセット（プレビュー用） ---
clear_scene()
x = 0.0
for cavity in CAVITY_SIZES:
    outer_xy = cavity + WALL * 2
    x += outer_xy / 2
    make_shell(cavity, origin=(x, 0.0))
    x += outer_xy / 2 + SET_GAP
export_stl("cube-shells-set")
