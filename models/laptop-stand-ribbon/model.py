"""有機的な胴体と細い受け面を、局所的に滑らかな肩でつなぐ。"""
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
               "RAIL_THICKNESS", "RAIL_EDGE_RADIUS", "LIP_RISE", "LIP_LENGTH"}
    if path:
        values = json.loads(Path(path).read_text(encoding="utf-8"))
        for key in allowed & values.keys():
            value = float(values[key])
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{key} must be a positive finite length")
            globals()[key] = value
    if RAIL_EDGE_RADIUS >= min(RAIL_WIDTH, RAIL_THICKNESS) / 2:
        raise ValueError("Rail edge radius must be smaller than half the thickness and width")


def spline_loop(controls, samples):
    result = []
    for index in range(len(controls)):
        p = [controls[(index + offset) % len(controls)] for offset in (-1, 0, 1, 2)]
        for step in range(samples):
            t = step / samples
            weights = ((1-t)**3, 3*t**3-6*t*t+4,
                       -3*t**3+3*t*t+3*t+1, t**3)
            result.append(sum(weight * value for weight, value in zip(weights, p)) / 6)
    return np.array(result)


def mesh_object(name, verts, faces, smooth=True):
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
    if smooth:
        for face in mesh.polygons:
            face.use_smooth = True
    return obj


def apply_modifier(obj, modifier):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def boolean(base, other, operation):
    modifier = base.modifiers.new(operation.title(), "BOOLEAN")
    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = other
    apply_modifier(base, modifier)
    bpy.data.objects.remove(other, do_unlink=True)


def join_meshes(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    return objects[0]


def remove_voxel_fragments(obj, minimum_vertices=100):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    remaining = set(bm.verts)
    removed = 0
    while remaining:
        pending = [remaining.pop()]
        component = []
        while pending:
            vertex = pending.pop()
            component.append(vertex)
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in remaining:
                    remaining.remove(other)
                    pending.append(other)
        if len(component) < minimum_vertices:
            removed += len(component)
            bmesh.ops.delete(bm, geom=component, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    print(f"REMOVED_VOXEL_FRAGMENT_VERTICES={removed}")


def restore_previous_depth(obj):
    ys = [vertex.co.y for vertex in obj.data.vertices]
    lower, upper = min(ys), max(ys)
    target = .279 * LENGTH/.280
    scale = target/(upper-lower)
    centre = (lower+upper)/2
    for vertex in obj.data.vertices:
        vertex.co.y = centre+(vertex.co.y-centre)*scale
    obj.data.update()


def body():
    controls = np.array(BODY_SECTIONS, dtype=float)
    sections = spline_loop(controls, samples_per_section)
    sections[:, [0, 2]] *= LENGTH / .280
    sections[:, [1, 3]] *= HEIGHT / .152
    sections[:, 4] *= FOOT_WIDTH / .084
    outer, inner = sections[:, :2], sections[:, 2:4]
    quads = np.stack((outer, np.roll(outer, -1, axis=0),
                      np.roll(inner, -1, axis=0), inner), axis=1)
    areas = np.sum(quads[:, :, 0] * np.roll(quads[:, :, 1], -1, axis=1)
                   - quads[:, :, 1] * np.roll(quads[:, :, 0], -1, axis=1), axis=1) / 2
    if not (np.all(areas > 1e-12) or np.all(areas < -1e-12)):
        raise ValueError("Body section correspondence folds in side projection")
    verts, faces = [], []
    for oy, oz, iy, iz, width in sections:
        for j in range(section_samples):
            angle = math.tau * j / section_samples
            radial = (1 + math.cos(angle)) / 2
            verts.append((width * math.sin(angle),
                          iy + (oy-iy) * radial,
                          iz + (oz-iz) * radial))
    for i in range(len(sections)):
        for j in range(section_samples):
            faces.append((i*section_samples+j,
                          ((i+1) % len(sections))*section_samples+j,
                          ((i+1) % len(sections))*section_samples+(j+1) % section_samples,
                          i*section_samples+(j+1) % section_samples))
    obj = mesh_object("Organic body", verts, faces)
    modifier = obj.modifiers.new("Body surface continuity", "SUBSURF")
    modifier.levels = 1
    modifier.render_levels = 1
    apply_modifier(obj, modifier)
    print(f"BODY_PATCH_MIN_AREA_MM2={min(abs(areas))*1e6:.4f}")
    return obj


def rounded_section(width, height, radius):
    points = []
    for sx, sz, angle0 in ((1, 1, 0), (-1, 1, math.pi/2),
                           (-1, -1, math.pi), (1, -1, math.pi*1.5)):
        cx, cz = sx*(width/2-radius), sz*(height/2-radius)
        for j in range(16):
            angle = angle0 + j/16*math.pi/2
            points.append((cx+radius*math.cos(angle), cz+radius*math.sin(angle)))
    return points


def rail():
    cross = rounded_section(RAIL_WIDTH, RAIL_THICKNESS, RAIL_EDGE_RADIUS)
    vertices, faces, rings = [], [], []
    for y in np.linspace(shoulder_rail_start, .263, 180):
        u = max(0, min(1, (y-(.263-LIP_LENGTH))/LIP_LENGTH))
        rise = u**3*(10-15*u+6*u*u)
        derivative = 30*u*u*(1-u)**2
        z = .148 - .177*(y-.012) + LIP_RISE*rise
        slope = -.177 + (LIP_RISE/LIP_LENGTH)*derivative
        rings.append((y, z, slope, 1.0))
    first, last = rings[0], rings[-1]
    cap_length = .0045
    caps = [math.pi*j/32 for j in range(1, 16)]
    rings = [(first[0]-cap_length*math.sin(a),
              first[1]-cap_length*math.sin(a)*first[2], first[2], math.cos(a))
             for a in reversed(caps)] + rings
    rings += [(last[0]+cap_length*math.sin(a),
               last[1]+cap_length*math.sin(a)*last[2], last[2], math.cos(a))
              for a in caps]
    for y, z, slope, scale in rings:
        length = math.sqrt(1+slope*slope)
        for x, normal in cross:
            vertices.append((x*scale,
                             (y-normal*scale*slope/length)*LENGTH/.280,
                             (z+normal*scale/length)*HEIGHT/.152))
    count = len(cross)
    for i in range(len(rings)-1):
        for j in range(count):
            faces.append((i*count+j, (i+1)*count+j,
                          (i+1)*count+(j+1) % count, i*count+(j+1) % count))
    for row, end, direction in ((0, first, -1), (len(rings)-1, last, 1)):
        pole = len(vertices)
        vertices.append((0, (end[0]+direction*cap_length)*LENGTH/.280,
                         (end[1]+direction*cap_length*end[2])*HEIGHT/.152))
        for j in range(count):
            faces.append((row*count+j, row*count+(j+1) % count, pole))
    obj = mesh_object("Narrow upper support", vertices, faces)
    modifier = obj.modifiers.new("Soft support edges", "SUBSURF")
    modifier.levels = 1
    modifier.render_levels = 1
    apply_modifier(obj, modifier)
    return obj


def bezier_point(points, t):
    u = 1-t
    return sum((u**3*points[0], 3*u*u*t*points[1],
                3*u*t*t*points[2], t**3*points[3]), np.zeros(2))


def shoulder_bridge():
    """胴の内部から受け面へ接線を合わせた閉鎖ロフトを作る。"""
    sy, sz = LENGTH/.280, HEIGHT/.152
    rail_join_y = .052
    rail_join_z = .148-.177*(rail_join_y-.012)
    path = np.array(((.032*sy, .124*sz), (-.008*sy, .162*sz),
                     (.040*sy, (rail_join_z+.012*.177)*sz),
                     (rail_join_y*sy, rail_join_z*sz)))
    ring_count, around = 49, 64
    vertices, faces = [], []
    for i in range(ring_count):
        t = i/(ring_count-1)
        centre = bezier_point(path, t)
        before = bezier_point(path, max(0, t-.002))
        after = bezier_point(path, min(1, t+.002))
        tangent = after-before
        tangent /= np.linalg.norm(tangent)
        normal = np.array((-tangent[1], tangent[0]))
        taper_t = min(1.0, t/.55)
        ease = taper_t*taper_t*(3-2*taper_t)
        half_width = (1-ease)*.016 + ease*RAIL_WIDTH/2
        half_height = (1-ease)*.009 + ease*RAIL_THICKNESS/2
        for j in range(around):
            angle = math.tau*j/around
            yz = centre + normal*(half_height*math.cos(angle))
            vertices.append((half_width*math.sin(angle), yz[0], yz[1]))
    for i in range(ring_count-1):
        for j in range(around):
            faces.append((i*around+j, (i+1)*around+j,
                          (i+1)*around+(j+1) % around, i*around+(j+1) % around))
    for ring, reverse in ((0, True), (ring_count-1, False)):
        centre_index = len(vertices)
        centre = bezier_point(path, ring/(ring_count-1))
        vertices.append((0, centre[0], centre[1]))
        for j in range(around):
            face = (ring*around+j, ring*around+(j+1) % around, centre_index)
            faces.append(tuple(reversed(face)) if reverse else face)
    return mesh_object("Shoulder transition", vertices, faces)


def remesh_and_smooth_shoulder(obj):
    modifier = obj.modifiers.new("Continuous shoulder surface", "REMESH")
    modifier.mode = "VOXEL"
    modifier.voxel_size = shoulder_voxel_size
    modifier.use_smooth_shade = True
    apply_modifier(obj, modifier)
    remove_voxel_fragments(obj)
    restore_previous_depth(obj)

    group = obj.vertex_groups.new(name="Shoulder only")
    indices = [vertex.index for vertex in obj.data.vertices
               if vertex.co.y < .062*LENGTH/.280 and vertex.co.z > .116*HEIGHT/.152]
    group.add(indices, 1.0, "REPLACE")
    modifier = obj.modifiers.new("Shoulder tangent smoothing", "SMOOTH")
    modifier.vertex_group = group.name
    modifier.factor = shoulder_smooth_factor
    modifier.iterations = shoulder_smooth_steps
    apply_modifier(obj, modifier)
    print(f"SHOULDER_SMOOTHED_VERTICES={len(indices)}")


def flatten_floor(obj):
    """閉鎖メッシュの接地帯だけを同一平面へそろえる。"""
    for vertex in obj.data.vertices:
        if vertex.co.z < .0006:
            vertex.co.z = 0.0
    obj.data.update()


def validate(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    remaining, components = set(bm.verts), 0
    component_bounds = []
    while remaining:
        components += 1
        pending = [remaining.pop()]
        members = []
        while pending:
            vertex = pending.pop()
            members.append(vertex)
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in remaining:
                    remaining.remove(other)
                    pending.append(other)
        component_bounds.append({
            "vertices": len(members),
            "min_mm": [round(min(v.co[i] for v in members)*1000, 2) for i in range(3)],
            "max_mm": [round(max(v.co[i] for v in members)*1000, 2) for i in range(3)],
        })
    downward = []
    for face in bm.faces:
        if face.normal.z < -1e-8 and not all(abs(v.co.z) < 1e-7 for v in face.verts):
            downward.append(math.degrees(math.asin(min(1.0, -face.normal.z))))
    stats = {
        "vertices": len(bm.verts), "triangles": len(bm.faces),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
        "zero_area_faces": sum(face.calc_area() < 1e-16 for face in bm.faces),
        "components": components,
        "component_bounds": component_bounds,
        "volume_cm3": round(abs(bm.calc_volume(signed=True))*1e6, 3),
        "upright_max_downward_overhang_deg": round(max(downward, default=0.0), 4),
        "print_orientation_note": "The upright pose is not asserted to satisfy 45 degrees",
        "shoulder_transition_mm": [32.0, 52.0],
        "shoulder_method": "closed tangent loft, 0.45mm voxel union, local smoothing",
    }
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    bpy.context.view_layer.update()
    stats["dimensions_mm"] = [round(value*1000, 3) for value in obj.dimensions]
    stats["bottom_z_mm"] = round(min(vertex.co.z for vertex in obj.data.vertices)*1000, 6)
    if (components != 1 or stats["non_manifold_edges"] or stats["zero_area_faces"]
            or stats["volume_cm3"] <= 0):
        raise ValueError(stats)
    return stats


def main():
    load_overrides()
    clear_scene()
    OUT.mkdir(parents=True, exist_ok=True)
    obj = join_meshes((body(), rail(), shoulder_bridge()))
    remesh_and_smooth_shoulder(obj)
    flatten_floor(obj)
    obj.name = MODEL_NAME
    stats = validate(obj)
    stats["design"] = "Organic loop body and narrow support joined by a local smooth shoulder"
    export_stl(MODEL_NAME, only=[obj])
    (OUT / "build.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
