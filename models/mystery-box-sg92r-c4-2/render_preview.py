"""C4-2の5停止位置と内部断面を同じカメラで描画する。"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import motion  # noqa: E402
import params as P  # noqa: E402


COLORS = {
    "housing": (0.88, 0.85, 0.78, 1), "faceplate": (0.92, 0.89, 0.82, 1),
    "bottom": (0.88, 0.85, 0.78, 1), "guide_frame": (0.88, 0.85, 0.78, 1),
    "cam_disk": (0.88, 0.85, 0.78, 1), "cam_keeper": (0.88, 0.85, 0.78, 1),
    "horn_coupler": (0.88, 0.85, 0.78, 1), "drive_key": (0.88, 0.85, 0.78, 1),
    "servo_body": (0.15, 0.34, 0.58, 1), "servo_horn": (0.96, 0.96, 0.93, 1),
    "servo_wire": (0.35, 0.29, 0.25, 1),
}
PRINT_COLOR = (0.62, 0.57, 0.47, 1)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for data in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(data):
            data.remove(item)


def import_part(identifier):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(HERE / "build" / f"{identifier}.stl"))
    ob = next(item for item in bpy.data.objects if item not in before)
    ob.name = identifier
    color = COLORS.get(identifier, PRINT_COLOR) if identifier.startswith("servo_") else PRINT_COLOR
    ob.color = color
    material = bpy.data.materials.new(identifier + "_material")
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.7
    ob.data.materials.append(material)
    return ob


def aim(ob, target):
    ob.rotation_euler = ((Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler())


def half_cut(ob):
    # C1の表示と同じく、幅の20%に切断面を置く。
    cut_x = P.CUBE * 1000.0 * 0.2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cut_x + 80, 0, 70))
    cutter = bpy.context.object
    cutter.name = "render_cut"
    cutter.dimensions = (160, 180, 180)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = ob.modifiers.new("render_half_cut", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def setup_scene(view):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.25, 0.28, 0.30, 1)
    background.inputs["Strength"].default_value = 0.3
    looks = {item.identifier for item in
             scene.view_settings.bl_rna.properties["look"].enum_items}
    if "AgX - Medium High Contrast" in looks:
        scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.film_transparent = False
    if view == "top":
        location, target, scale = (0, -90, 240), (0, 0, 105), 96
    elif view == "cutaway":
        location, target, scale = (175, -85, 125), (0, 0, 57), 150
    else:
        location, target, scale = (165, -185, 350), (0, 0, 55), 210
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    aim(camera, target)
    scene.camera = camera
    for location, energy, size in (((90, -120, 260), 1800000, 180),
                                   ((-150, 70, 190), 700000, 140)):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        aim(light, target)
    bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 0, -0.5))
    floor = bpy.context.object
    floor_material = bpy.data.materials.new("floor_material")
    floor_material.diffuse_color = (0.32, 0.35, 0.38, 1)
    floor_material.use_nodes = True
    floor_shader = floor_material.node_tree.nodes.get("Principled BSDF")
    floor_shader.inputs["Base Color"].default_value = floor_material.diffuse_color
    floor_shader.inputs["Roughness"].default_value = 0.9
    floor.data.materials.append(floor_material)


def render_state(identifier, degree, view="top", cutaway=False):
    clear()
    objects = {}
    manifest = json.loads((HERE / "build" / "manifest.json").read_text(encoding="utf-8"))
    for part in manifest["parts"]:
        if part.get("fit_only"):
            continue
        objects[part["id"]] = import_part(part["id"])
    angle = math.radians(degree - P.HOME_SERVO_DEG)
    for name in ("cam_disk", "horn_coupler", "drive_key", "servo_horn"):
        objects[name].rotation_euler.z = angle
    for group_index, group in enumerate(P.GROUPS):
        objects["carrier_" + group].location.z = 1000.0 * motion.lift_m(group_index, degree)
    if cutaway:
        half_cut(objects["housing"])
        half_cut(objects["faceplate"])
        half_cut(objects["bottom"])
    setup_scene(view)
    target = HERE / "build" / identifier
    bpy.context.scene.render.filepath = str(target)
    bpy.ops.render.render(write_still=True)
    return target


def main():
    outputs = []
    for pattern_id, _label, degree in P.PATTERNS:
        outputs.append(render_state(f"preview_{pattern_id}.png", degree))
    outputs.append(render_state("hero.png", P.HOME_SERVO_DEG, view="hero"))
    outputs.append(render_state("cutaway.png", P.ASSEMBLY_SERVO_DEG,
                                view="cutaway", cutaway=True))
    sources = {name: digest(HERE / name) for name in ("model.py", "params.py", "motion.py", "contact_envelope.py", "render_preview.py")}
    stls = {path.name: digest(path) for path in sorted((HERE / "build").glob("*.stl"))
            if not path.name.startswith("print_")}
    document = {"model": P.MODEL_ID, "renderer": "BLENDER_EEVEE", "resolution_px": [768, 768],
                "cutaway": {"cutPlaneXmm": P.CUBE * 1000.0 * 0.2,
                            "exteriorParts": ["housing", "faceplate", "bottom"],
                            "internalPartsOpaque": True},
                "source_sha256": sources, "assembly_stl_sha256": stls,
                "outputs": {path.name: digest(path) for path in outputs}}
    temporary = HERE / "build" / "preview_evidence.tmp"
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
    os.replace(temporary, HERE / "build" / "preview_evidence.json")
    print(f"rendered {len(outputs)} previews")


if __name__ == "__main__":
    main()
