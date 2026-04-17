"""Toio Core Cube cover — hollow shell, open bottom."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import OUTER_W, OUTER_D, OUTER_H, INNER_W, INNER_D, INNER_H

clear_scene()

# --- Outer shell ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, OUTER_H / 2))
outer = bpy.context.active_object
outer.scale = (OUTER_W, OUTER_D, OUTER_H)
bpy.ops.object.transform_apply(scale=True)

# Bevel outer edges for a softer look (0.5mm)
bev = outer.modifiers.new("bevel", "BEVEL")
bev.width = 0.0005
bev.segments = 3
bpy.ops.object.modifier_apply(modifier="bevel")

# --- Inner cavity cutter (extends 1mm below z=0 for clean boolean) ---
CUT_EXTRA = 0.001
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(0, 0, (INNER_H - CUT_EXTRA) / 2)
)
inner = bpy.context.active_object
inner.scale = (INNER_W, INNER_D, INNER_H + CUT_EXTRA)
bpy.ops.object.transform_apply(scale=True)

# --- Boolean subtract ---
mod = outer.modifiers.new("cavity", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = inner
mod.solver = "EXACT"
bpy.context.view_layer.objects.active = outer
bpy.ops.object.modifier_apply(modifier="cavity")
bpy.data.objects.remove(inner, do_unlink=True)

# --- LED window on top (10mm circle) ---
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.005,
    depth=0.01,
    location=(0, 0, OUTER_H)
)
led_cut = bpy.context.active_object
bpy.ops.object.transform_apply(scale=True)

mod2 = outer.modifiers.new("led_window", "BOOLEAN")
mod2.operation = "DIFFERENCE"
mod2.object = led_cut
mod2.solver = "EXACT"
bpy.context.view_layer.objects.active = outer
bpy.ops.object.modifier_apply(modifier="led_window")
bpy.data.objects.remove(led_cut, do_unlink=True)

export_stl("toio_cover")
