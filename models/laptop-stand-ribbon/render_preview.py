"""出力したSTLの形を複数方向から確認する。既存のBlenderは操作しない。"""
import math
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from params import MODEL_NAME
OUT = ROOT / "exports" / MODEL_NAME
SUBJECT = None


def material(name, color, roughness=.72):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = roughness
    return m


def setup(studio=False):
    global SUBJECT
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=str(ROOT / "exports" / (MODEL_NAME+".stl")))
    obj = bpy.context.object
    obj.scale = (.001,)*3
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-8)
    bm.to_mesh(obj.data)
    bm.free()
    for p in obj.data.polygons:
        p.use_smooth = abs(p.normal.z) < .999
    SUBJECT = obj
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE" if studio else "BLENDER_WORKBENCH"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = not studio
    scene.view_settings.view_transform = "AgX" if studio else "Standard"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    if studio:
        obj.data.materials.append(material("Ivory", (.73, .68, .57)))
        scene.world = bpy.data.worlds.new("Studio")
        scene.world.use_nodes = True
        background = scene.world.node_tree.nodes.get("Background")
        background.inputs["Color"].default_value = (.8, .8, .8, 1)
        background.inputs["Strength"].default_value = .45
        bpy.ops.mesh.primitive_plane_add(size=200, location=(0, .14, -.0002))
        bpy.context.object.data.materials.append(material("Floor", (.92, .91, .88)))
        for name, position, power, size in (
                ("Key", (.2, -.15, .5), 8, .4),
                ("Fill", (-.3, .1, .3), 4, .4),
                ("Rim", (.1, .5, .5), 6, .3)):
            data = bpy.data.lights.new(name, "AREA")
            data.energy, data.size = power, size
            light = bpy.data.objects.new(name, data)
            scene.collection.objects.link(light)
            light.location = position
            light.rotation_euler = (Vector((0, .13, .07))-light.location).to_track_quat("-Z", "Y").to_euler()
    else:
        sh = scene.display.shading
        sh.light = "STUDIO"
        sh.color_type = "SINGLE"
        sh.single_color = (.74, .70, .63)
        sh.show_shadows = True
        sh.show_cavity = True
        sh.cavity_type = "BOTH"
    return obj


def shoot(name, azimuth, elevation, scale=.335, width=1280, height=900):
    target = Vector((0, .137, .073))
    az, el = math.radians(azimuth), math.radians(elevation)
    data = bpy.data.cameras.new(name)
    data.type, data.ortho_scale = "ORTHO", scale
    cam = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = target+Vector((math.cos(el)*math.cos(az),
                                 math.cos(el)*math.sin(az), math.sin(el)))
    cam.rotation_euler = (target-cam.location).to_track_quat("-Z", "Y").to_euler()
    # Fit the exported object's actual vertices, excluding the studio floor.
    right = cam.rotation_euler.to_matrix() @ Vector((1, 0, 0))
    up = cam.rotation_euler.to_matrix() @ Vector((0, 1, 0))
    points = [SUBJECT.matrix_world @ v.co for v in SUBJECT.data.vertices]
    xs = [p.dot(right) for p in points]
    ys = [p.dot(up) for p in points]
    target += right*((max(xs)+min(xs))/2-target.dot(right))
    target += up*((max(ys)+min(ys))/2-target.dot(up))
    cam.location = target+Vector((math.cos(el)*math.cos(az),
                                 math.cos(el)*math.sin(az), math.sin(el)))
    aspect = width/height
    xspan, yspan = max(xs)-min(xs), max(ys)-min(ys)
    data.ortho_scale = max(xspan, yspan*aspect)*1.15 if aspect >= 1 else max(xspan/aspect, yspan)*1.15
    scene = bpy.context.scene
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.filepath = str(OUT / (name+".png"))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    studio = "studio" in sys.argv
    setup(studio)
    if studio:
        shoot("studio-left", 35, 12)
        shoot("studio-right", 145, 12)
        shoot("studio-front", 90, 35, .21, 650, 1000)
    else:
        shoot("side", 0, 0)
        shoot("back", 180, 8)
        shoot("front", 90, 35, .21, 650, 1000)
        shoot("top", 0, 90)
        shoot("underside", 0, -40)
        shoot("perspective", 35, 12)
