import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import bmesh
from mathutils import Vector
from blender_utils import clear_scene, export_stl
from params import *


def _activate(ob):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    return ob


def revolve(name, profile, seg=SEG):
    """profile: [(軸方向, 半径)]。軸は Z。上下に蓋をした閉じた立体を返す。"""
    bm = bmesh.new()
    rings = []
    for a, r in profile:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg),
                                    r * math.sin(2 * math.pi * i / seg), a))
                      for i in range(seg)])
    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def boolean(target, cutter, op="DIFFERENCE"):
    # ジョイントと同じく MANIFOLD。EXACT は細かいメッシュで結果が空になることがある
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = "MANIFOLD"
    _activate(target)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def clean(ob, dist=1e-6):
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
    mod.use_clamp_overlap = True
    _activate(ob)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def outer_profile():
    """太い側は襟と同径のまま、そこから TIP_D まで落とす。

    ジョイントの sleeve_profile() と同じ smoothstep を使うので、
    合わせ面をまたいで同じ曲がり方でつながる。
    """
    r_hub, r_tip = HUB_D / 2, TIP_D / 2
    pts = [(Z_BUILD_BOT, r_hub), (COLLAR_L, r_hub)]
    for i in range(1, TAPER_SEG + 1):
        t = i / TAPER_SEG
        pts.append((COLLAR_L + TAPER_L * t, r_hub + (r_tip - r_hub) * smoothstep(t)))
    return [(a * MM, r * MM) for a, r in pts]


clear_scene()

body = revolve("pipe_taper", outer_profile())

# 角を丸める。⚠ 穴より先に通す。ジョイントも同じ順で、穴の縁は立てたままにしてある
clean(body)
bevel(body, FILLET_R * MM, 4, FILLET_ANGLE)

# 底を平らに切る（角丸を残したまま造形板に着く面を作る）
cut = revolve("cut_base", [((Z_BUILD_BOT - 10) * MM, 60 * MM), (0.0, 60 * MM)], seg=8)
boolean(body, cut, "DIFFERENCE")

# パイプの穴
bore = revolve("bore", [(-10 * MM, BORE_D / 2 * MM), ((LEN + 10) * MM, BORE_D / 2 * MM)])
boolean(body, bore, "DIFFERENCE")

clean(body, dist=2e-5)
_activate(body)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.shade_flat()

print("bbox mm:", [round(v * 1000, 2) for v in body.dimensions])
export_stl("pipe_taper_28")
