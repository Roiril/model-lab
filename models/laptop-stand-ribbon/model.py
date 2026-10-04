"""滑らかな環状曲面と細い受け面から、有機的なPCスタンドを作る。"""
import json
import math
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(HERE))

import bpy
import bmesh
import numpy as np
from blender_utils import clear_scene, export_stl
from params import *

OUT = ROOT / "exports" / MODEL_NAME


def load_overrides():
    path = os.environ.get("MODEL_PARAMS_JSON")
    allowed = {"LENGTH", "HEIGHT", "FOOT_WIDTH", "RAIL_WIDTH",
               "RAIL_THICKNESS", "RAIL_EDGE_RADIUS", "LIP_RISE"}
    if path:
        values = json.loads(Path(path).read_text(encoding="utf-8"))
        for key in allowed & values.keys():
            value = float(values[key])
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{key} must be a positive finite length")
            globals()[key] = value
    if RAIL_EDGE_RADIUS >= min(RAIL_WIDTH, RAIL_THICKNESS)/2:
        raise ValueError("Rail edge radius must be smaller than half the thickness and width")


def spline_loop(controls, samples):
    """周期三次Bスプライン。位置と接線と曲率が連続する。"""
    result = []
    for index in range(len(controls)):
        p = [controls[(index + offset) % len(controls)] for offset in (-1, 0, 1, 2)]
        for step in range(samples):
            t = step / samples
            weights = ((1-t)**3, 3*t**3-6*t*t+4,
                       -3*t**3+3*t*t+3*t+1, t**3)
            result.append(sum(w * v for w, v in zip(weights, p)) / 6)
    return np.array(result)


def mesh_object(name, verts, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for face in mesh.polygons:
        face.use_smooth = True
    return obj


def apply_modifier(obj, mod):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def boolean(base, other, operation):
    mod = base.modifiers.new(operation, "BOOLEAN")
    mod.operation = operation
    mod.solver = "EXACT"
    mod.object = other
    apply_modifier(base, mod)
    bpy.data.objects.remove(other, do_unlink=True)


def body():
    controls = np.array(BODY_SECTIONS, dtype=float)
    # The sparse matched sections belong to four regions, excluding the rail.
    # Interpolation must preserve the orientation of every projected strip.
    c = spline_loop(controls, samples_per_section)
    c[:, [0, 2]] *= LENGTH / .280
    c[:, [1, 3]] *= HEIGHT / .152
    c[:, 4] *= FOOT_WIDTH / .084
    outer, inner = c[:, :2], c[:, 2:4]
    quad = np.stack((outer, np.roll(outer, -1, axis=0),
                     np.roll(inner, -1, axis=0), inner), axis=1)
    area = np.sum(quad[:, :, 0] * np.roll(quad[:, :, 1], -1, axis=1)
                  - quad[:, :, 1] * np.roll(quad[:, :, 0], -1, axis=1), axis=1) / 2
    if not (np.all(area > 1e-12) or np.all(area < -1e-12)):
        raise ValueError("Body section correspondence folds in side projection")
    verts = []
    faces = []
    for row in c:
        oy, oz, iy, iz, width = row
        for j in range(section_samples):
            angle = math.tau * j / section_samples
            radial = (1 + math.cos(angle)) / 2
            verts.append((width * math.sin(angle),
                          iy + (oy-iy) * radial,
                          iz + (oz-iz) * radial))
    for i in range(len(c)):
        for j in range(section_samples):
            faces.append((i*section_samples+j,
                          ((i+1) % len(c))*section_samples+j,
                          ((i+1) % len(c))*section_samples+(j+1) % section_samples,
                          i*section_samples+(j+1) % section_samples))
    obj = mesh_object("Continuous body", verts, faces)
    mod = obj.modifiers.new("Surface continuity", "SUBSURF")
    mod.levels = 1
    apply_modifier(obj, mod)
    # A real plane is cut after smoothing; it cannot float above the floor.
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, .1, -.250))
    cutter = bpy.context.object
    cutter.dimensions = (1, 1, .5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    boolean(obj, cutter, "DIFFERENCE")
    print(f"BODY_PATCH_MIN_AREA_MM2={min(abs(area))*1e6:.4f}")
    return obj


def rounded_section(width, height, radius):
    points = []
    for sx, sz, a in ((1, 1, 0), (-1, 1, math.pi/2),
                      (-1, -1, math.pi), (1, -1, math.pi*1.5)):
        cx, cz = sx*(width/2-radius), sz*(height/2-radius)
        for j in range(8):
            angle = a + j/8*math.pi/2
            points.append((cx+radius*math.cos(angle), cz+radius*math.sin(angle)))
    return points


def rail():
    """A flat central face, rounded edges, and a modest upturned nose."""
    cross = rounded_section(RAIL_WIDTH, RAIL_THICKNESS, RAIL_EDGE_RADIUS)
    vertices, faces = [], []
    rings = []
    # Main rail is straight; the last 22mm follows a cubic upturn.
    for y in np.linspace(.012, .263, 130):
        u = max(0, (y-.240)/.023)
        z = .148 - .177*(y-.012) + LIP_RISE*u*u*(3-2*u)
        slope = -.177 + (LIP_RISE/.023)*6*u*(1-u)
        rings.append((y, z, slope, 1.0))
    # Compact rounded end caps; use the same number of points in every ring.
    first, last = rings[0], rings[-1]
    caps = [math.pi*j/16 for j in range(1, 8)]
    rings = [(first[0]-.002*math.sin(a),
              first[1]-.002*math.sin(a)*first[2], first[2], math.cos(a))
             for a in reversed(caps)] + rings
    rings += [(last[0]+.002*math.sin(a),
               last[1]+.002*math.sin(a)*last[2], last[2], math.cos(a))
              for a in caps]
    for y, z, slope, scale in rings:
        length = math.sqrt(1+slope*slope)
        for x, n in cross:
            vertices.append((x*scale,
                             (y-n*scale*slope/length)*LENGTH/.280,
                             (z+n*scale/length)*HEIGHT/.152))
    n = len(cross)
    for i in range(len(rings)-1):
        for j in range(n):
            faces.append((i*n+j, (i+1)*n+j,
                          (i+1)*n+(j+1) % n, i*n+(j+1) % n))
    faces.extend((tuple(reversed(range(n))), tuple((len(rings)-1)*n+j for j in range(n))))
    return mesh_object("Narrow upper support", vertices, faces)


def validate(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    stats = {
        "vertices": len(bm.verts), "triangles": len(bm.faces),
        "non_manifold_edges": sum(not e.is_manifold for e in bm.edges),
        "zero_area_faces": sum(f.calc_area() < 1e-16 for f in bm.faces),
        "volume_cm3": bm.calc_volume(signed=True)*1e6,
    }
    remaining = set(bm.verts)
    components = 0
    while remaining:
        components += 1
        pending = [remaining.pop()]
        while pending:
            v = pending.pop()
            for e in v.link_edges:
                other = e.other_vert(v)
                if other in remaining:
                    remaining.remove(other)
                    pending.append(other)
    stats["components"] = components
    bm.to_mesh(obj.data)
    bm.free()
    bpy.context.view_layer.update()
    stats["dimensions_mm"] = [round(v*1000, 3) for v in obj.dimensions]
    stats["bottom_z_mm"] = min(v.co.z for v in obj.data.vertices)*1000
    if components != 1 or stats["non_manifold_edges"] or stats["zero_area_faces"] or stats["volume_cm3"] <= 0:
        raise ValueError(stats)
    return stats


def main():
    load_overrides()
    clear_scene()
    OUT.mkdir(parents=True, exist_ok=True)
    obj = body()
    boolean(obj, rail(), "UNION")
    obj.name = MODEL_NAME
    stats = validate(obj)
    export_stl(MODEL_NAME, only=[obj])
    stats["design"] = "A continuous sculpted body; a narrow upper face; a flared flat foot"
    (OUT / "build.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
