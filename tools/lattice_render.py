"""Manifestと運動表からC3/C4の実メッシュを撮影する。Blenderで実行。"""
import json
import hashlib
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]


def material(name, color, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = 0.48
    shader.inputs["Metallic"].default_value = metallic
    return mat


def import_part(path, name):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = next(obj for obj in bpy.data.objects if obj not in before)
    obj.name = name
    return obj


def from_column(values):
    return Matrix([[values[c * 4 + r] for c in range(4)] for r in range(4)])


def render(model):
    folder = ROOT / "models" / model
    data = json.loads((folder / "build/manifest.json").read_text(encoding="utf-8"))
    motion = json.loads((folder / "build/motion.json").read_text(encoding="utf-8"))
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.25, 0.25, 0.25)
    scene.view_settings.view_transform = "AgX"
    face = material("磁器を想定した白い樹脂", (0.78, 0.77, 0.72))
    dark = material("内側の濃い樹脂", (0.105, 0.115, 0.12))
    servo = material("サーボ本体", (0.04, 0.12, 0.24))
    ground = material("背景", (0.56, 0.54, 0.49))
    objects = {}
    sources = {}
    for part in data["parts"]:
        if part.get("fit_only"):
            continue
        ob = import_part(folder / part["assembly"], part["id"])
        sources[part["assembly"]] = hashlib.sha256((folder / part["assembly"]).read_bytes()).hexdigest()
        objects[part["id"]] = ob
        key = part["id"].lower()
        outside = key.startswith("cap_") or any(w in key for w in ("case", "housing", "bottom", "shell", "box", "frame", "deck", "carrier", "tile", "face", "lid", "ring", "base"))
        mat = face if outside else (servo if "servo" in key or "ref_body" in key else dark)
        ob.data.materials.clear()
        ob.data.materials.append(mat)
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -0.08))
    bpy.context.object.data.materials.append(ground)
    dimensions = data.get("meta", {}).get("dimensions_mm", [80, 80, 80])
    height = float(dimensions[2])
    target = Vector((0, 0, height * .54))
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(dimensions) * 2.02
    camera.location = target + Vector((140, -190, 170))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    for name, pos, energy, size in (
        ("左の大きな光", (-130, -160, 220), 1400000, 160),
        ("右の光", (160, 30, 150), 950000, 140),
        ("奥の光", (0, 150, 160), 1100000, 100),
    ):
        bpy.ops.object.light_add(type="AREA", location=pos)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()
    frames = motion["frames"]
    output = folder / "build"
    poses = [("rest", frames[0]), ("raised", frames[-1])]
    if model.endswith("c3"):
        poses.insert(1, ("center", frames[len(frames) // 2]))
    for label, frame in poses:
        for key, ob in objects.items():
            ob.matrix_world = from_column(frame["transforms"][key]) if key in frame["transforms"] else Matrix.Identity(4)
        scene.render.filepath = str(output / f"hero-{label}.png")
        bpy.ops.render.render(write_still=True)
        print(json.dumps({"model": model, "pose": label, "servo_deg": frame["servo_deg"], "file": scene.render.filepath}))
    report = {"assembly_sha256": sources,
              "motion_sha256": hashlib.sha256((output / "motion.json").read_bytes()).hexdigest(),
              "images": [{"file": f"hero-{label}.png", "servo_deg": frame["servo_deg"],
                          "sha256": hashlib.sha256((output / f"hero-{label}.png").read_bytes()).hexdigest()}
                         for label, frame in poses]}
    (output / "render_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    if len(argv) != 1 or argv[0] not in ("mystery-box-sg92r-c3", "mystery-box-sg92r-c4"):
        raise ValueError("Use -- mystery-box-sg92r-c3|mystery-box-sg92r-c4")
    render(argv[0])
