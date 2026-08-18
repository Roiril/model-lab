"""足ジョイント 2 個にかぶせる芯間合わせの板（bpy）。単位は m。"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import bmesh
from mathutils import Matrix, Vector

from blender_utils import clear_scene, EXPORTS_DIR
from params import (
    MM, SPAN, HOLE_D, PLATE_W, PLATE_L, PLATE_T, CORNER_R, EDGE_R,
    SEG, CORNER_SEG, FILLET_SEG, FILLET_ANGLE,
)


def _activate(ob):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def _finish(name, bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def prism(name, poly, z0, z1):
    """poly: [(x, y)] を反時計回りで。z0→z1 に押し出す。"""
    bm = bmesh.new()
    lo = [bm.verts.new((x * MM, y * MM, z0 * MM)) for x, y in poly]
    hi = [bm.verts.new((x * MM, y * MM, z1 * MM)) for x, y in poly]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    return _finish(name, bm)


def cyl(name, r, z0, z1, cx=0.0, cy=0.0, seg=SEG):
    poly = [(cx + r * math.cos(2 * math.pi * i / seg),
             cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    return prism(name, poly, z0, z1)


def rounded_rect(hl, hw, r, seg=CORNER_SEG):
    """長辺 2*hl、短辺 2*hw、角丸 r の反時計回りポリゴン。"""
    pts = []
    for cx, cy, a0 in ((hl - r, hw - r, 0.0), (-(hl - r), hw - r, math.pi / 2),
                       (-(hl - r), -(hw - r), math.pi), (hl - r, -(hw - r), 1.5 * math.pi)):
        for i in range(seg + 1):
            a = a0 + math.pi / 2 * i / seg
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def boolean(target, cutter, op="DIFFERENCE", solver="MANIFOLD"):
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = solver
    _activate(target)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def clean(ob, dist=1e-5):
    """boolean が残す極短エッジを掃除する。放置すると Bevel が発散する。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return ob


def bevel(ob, width, segments, angle_deg):
    mod = ob.modifiers.new("bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle_deg)
    mod.miter_outer = "MITER_ARC"
    mod.use_clamp_overlap = False
    _activate(ob)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


def build():
    body = prism("foot_spacer", rounded_rect(PLATE_L / 2, PLATE_W / 2, CORNER_R),
                 0.0, PLATE_T)
    # 穴は上下へ突き出して切る。面一だと boolean が不安定になる
    for s in (+1, -1):
        boolean(body, cyl("hole", HOLE_D / 2, -1.0, PLATE_T + 1.0, s * SPAN / 2, 0.0))
    clean(body)
    bevel(body, EDGE_R * MM, FILLET_SEG, FILLET_ANGLE)
    return body


clear_scene()
body = build()

os.makedirs(EXPORTS_DIR, exist_ok=True)
stl = os.path.join(EXPORTS_DIR, "pipe_foot_spacer.stl")
_activate(body)
bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True, global_scale=1000.0)
print("Exported:", stl)
print("bbox mm:", [round(v * 1000, 2) for v in body.dimensions])
