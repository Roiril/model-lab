"""toio-cover module (sample) — flat slab with dovetail tab; slides into base slot along Y"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy, bmesh, math
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


def make_dovetail_tab(w_top_slot, depth, angle_deg, y_len, clearance, name):
    """Trapezoidal prism matching the slot, reduced by clearance — slides into base slot."""
    w  = w_top_slot - 2 * clearance  # narrower than slot opening
    ht = w / 2
    hb = ht + depth * math.tan(math.radians(angle_deg))
    hy = y_len / 2

    mesh = bpy.data.meshes.new(name)
    obj  = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    v = [bm.verts.new(c) for c in [
        (-ht, -hy,      0), ( ht, -hy,      0),
        ( ht,  hy,      0), (-ht,  hy,      0),
        (-hb, -hy, -depth), ( hb, -hy, -depth),
        ( hb,  hy, -depth), (-hb,  hy, -depth),
    ]]
    bm.faces.new([v[0], v[1], v[2], v[3]])  # top   (+Z)
    bm.faces.new([v[4], v[7], v[6], v[5]])  # bottom (-Z)
    bm.faces.new([v[0], v[4], v[5], v[1]])  # -Y
    bm.faces.new([v[3], v[2], v[6], v[7]])  # +Y
    bm.faces.new([v[0], v[3], v[7], v[4]])  # -X
    bm.faces.new([v[1], v[5], v[6], v[2]])  # +X
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    return obj


# --- module body (flat rectangular slab — customize the shape above this layer) ---
bpy.ops.mesh.primitive_cube_add(size=1)
body = bpy.context.active_object
body.name     = "module_body"
body.scale    = (MODULE_W, MODULE_D, MODULE_H)
body.location = (0, 0, MODULE_H / 2)
bpy.ops.object.transform_apply(scale=True)

# --- dovetail tab: protrudes downward from module bottom, embeds 1mm into body for clean union ---
EMBED = 0.001
tab = make_dovetail_tab(RAIL_TOP_W, RAIL_DEPTH, RAIL_ANGLE, MODULE_D, RAIL_CLR, "dt_tab")
tab.location = (0, 0, EMBED)  # shift up so top of tab is 1mm inside body

bpy.context.view_layer.objects.active = body
mod = body.modifiers.new("tab_union", "BOOLEAN")
mod.operation = "UNION"
mod.object    = tab
mod.solver    = "EXACT"
bpy.ops.object.modifier_apply(modifier="tab_union")
bpy.data.objects.remove(tab, do_unlink=True)

export_stl("toio_cover_module_sample")
