"""toio-cover face — robot head piece; peg inserts into module socket from above"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()

# peg actual width = socket - clearance per side
PEG_AW = PEG_W - 2 * PEG_CLR   # 11.6mm

# face carving — carved into +Y face of head
EYE_W     = 0.007   # 7mm wide
EYE_H     = 0.005   # 5mm tall
EYE_DEP   = 0.003   # 3mm deep
EYE_SEP   = 0.010   # 10mm center-to-center
MOUTH_W   = 0.014   # 14mm wide
MOUTH_H   = 0.003   # 3mm tall
MOUTH_DEP = 0.003   # 3mm deep

EMBED    = 0.001    # head block overlaps peg top by 1mm for clean union
OVERHANG = 0.0005   # cutter protrudes 0.5mm past face to avoid coplanar boolean

# Z origin of head block (slightly overlaps peg top)
HEAD_BASE_Z = PEG_H - EMBED
EYE_Z    = HEAD_BASE_Z + HEAD_H * 0.68
MOUTH_Z  = HEAD_BASE_Z + HEAD_H * 0.25


def bool_subtract(target, cutter):
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new("bool_cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object    = cutter
    mod.solver    = "EXACT"
    bpy.ops.object.modifier_apply(modifier="bool_cut")
    bpy.data.objects.remove(cutter, do_unlink=True)


# --- peg (bottom, inserts into module socket) ---
bpy.ops.mesh.primitive_cube_add(size=1)
body = bpy.context.active_object
body.name     = "peg"
body.scale    = (PEG_AW, PEG_AW, PEG_H)
body.location = (0, 0, PEG_H / 2)
bpy.ops.object.transform_apply(scale=True)

# --- head block: UNION on top of peg ---
bpy.ops.mesh.primitive_cube_add(size=1)
head = bpy.context.active_object
head.name     = "head"
head.scale    = (HEAD_W, HEAD_D, HEAD_H)
head.location = (0, 0, HEAD_BASE_Z + HEAD_H / 2)
bpy.ops.object.transform_apply(scale=True)

bpy.context.view_layer.objects.active = body
mod = body.modifiers.new("head_union", "BOOLEAN")
mod.operation = "UNION"
mod.object    = head
mod.solver    = "EXACT"
bpy.ops.object.modifier_apply(modifier="head_union")
bpy.data.objects.remove(head, do_unlink=True)

# --- eyes: two recessed rectangles carved into +Y face ---
for x_off in (-EYE_SEP / 2, EYE_SEP / 2):
    bpy.ops.mesh.primitive_cube_add(size=1)
    eye = bpy.context.active_object
    eye.name  = "eye_cutter"
    eye.scale = (EYE_W, EYE_DEP + OVERHANG, EYE_H)
    eye.location = (x_off,
                    HEAD_D / 2 - EYE_DEP / 2 + OVERHANG / 2,
                    EYE_Z)
    bpy.ops.object.transform_apply(scale=True)
    bool_subtract(body, eye)

# --- mouth: recessed rectangle carved into +Y face ---
bpy.ops.mesh.primitive_cube_add(size=1)
mouth = bpy.context.active_object
mouth.name  = "mouth_cutter"
mouth.scale = (MOUTH_W, MOUTH_DEP + OVERHANG, MOUTH_H)
mouth.location = (0,
                  HEAD_D / 2 - MOUTH_DEP / 2 + OVERHANG / 2,
                  MOUTH_Z)
bpy.ops.object.transform_apply(scale=True)
bool_subtract(body, mouth)

export_stl("toio_cover_face")
