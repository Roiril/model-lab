"""toio-cover base — fits over toio cube; dovetail slot on top rim receives modules"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy, bmesh, math
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


def make_dovetail_cutter(w_top, depth, angle_deg, y_len, name):
    """Trapezoidal prism: narrow at top, wide at bottom — for cutting a dovetail slot."""
    ht = w_top / 2
    hb = ht + depth * math.tan(math.radians(angle_deg))
    hy = y_len / 2 + 0.002  # extend past base edges so boolean cuts cleanly

    mesh = bpy.data.meshes.new(name)
    obj  = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    v = [bm.verts.new(c) for c in [
        (-ht, -hy,     0), ( ht, -hy,     0),
        ( ht,  hy,     0), (-ht,  hy,     0),
        (-hb, -hy, -depth), ( hb, -hy, -depth),
        ( hb,  hy, -depth), (-hb,  hy, -depth),
    ]]
    # winding order: CCW when viewed from outside (right-hand rule → outward normals)
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


def bool_subtract(target, cutter):
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new("bool_cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object    = cutter
    mod.solver    = "EXACT"
    bpy.ops.object.modifier_apply(modifier="bool_cut")
    bpy.data.objects.remove(cutter, do_unlink=True)


# --- outer shell ---
bpy.ops.mesh.primitive_cube_add(size=1)
base = bpy.context.active_object
base.name     = "base"
base.scale    = (BASE_OW, BASE_OD, COVER_H)
base.location = (0, 0, COVER_H / 2)
bpy.ops.object.transform_apply(scale=True)

# --- inner cavity: open bottom, closed top by TOP_RIM ---
EPS   = 0.001
cav_h = COVER_H - TOP_RIM + EPS
bpy.ops.mesh.primitive_cube_add(size=1)
cavity = bpy.context.active_object
cavity.name     = "cavity"
cavity.scale    = (BASE_IW, BASE_ID, cav_h)
cavity.location = (0, 0, (COVER_H - TOP_RIM - EPS) / 2)
bpy.ops.object.transform_apply(scale=True)
bool_subtract(base, cavity)

# --- dovetail slot in top rim (opens on both ±Y so module slides in from either end) ---
dt = make_dovetail_cutter(RAIL_TOP_W, RAIL_DEPTH, RAIL_ANGLE, BASE_OD, "dt_slot")
dt.location = (0, 0, COVER_H + 0.0005)  # slightly above top to avoid coplanar face
bool_subtract(base, dt)

export_stl("toio_cover_base")
