# -*- coding: utf-8 -*-
"""「あと6画のくま」全コンポーネントの GLB を生成する（Blender 5.1 / bpy）。

gen_textures.py の manifest.json を読み、
  - exports/six-strokes-bear/glb/<component>.glb（単体）
  - exports/six-strokes-bear/six-strokes-bear.glb（実セット俯瞰）
を書き出す。単位はメートル、テクスチャは GLB 内へ埋め込む。
"""
from __future__ import annotations

import json
import math
import os

import bmesh
import bpy


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "six-strokes-bear"))
TEX = os.path.join(OUT, "tex")
GLB = os.path.join(OUT, "glb")
os.makedirs(GLB, exist_ok=True)

with open(os.path.join(OUT, "manifest.json"), encoding="utf-8") as f:
    MANIFEST = json.load(f)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for blocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.images,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(blocks):
            blocks.remove(block)


def srgb_to_linear(value: int) -> float:
    c = value / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


_solid_cache: dict[tuple, bpy.types.Material] = {}
_texture_cache: dict[str, bpy.types.Material] = {}
_image_cache: dict[str, bpy.types.Image] = {}


def solid_material(name: str, color: list[int] | tuple[int, ...], roughness: float = 0.74) -> bpy.types.Material:
    key = (tuple(color[:3]), round(roughness, 3))
    if key in _solid_cache:
        return _solid_cache[key]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    r, g, b = [srgb_to_linear(int(v)) for v in color[:3]]
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0
    _solid_cache[key] = mat
    return mat


def texture_material(png: str, roughness: float = 0.70) -> bpy.types.Material:
    if png in _texture_cache:
        return _texture_cache[png]
    path = os.path.join(TEX, png)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    mat = bpy.data.materials.new("tex_" + os.path.splitext(png)[0])
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0
    image = _image_cache.get(png)
    if image is None:
        image = bpy.data.images.load(path, check_existing=True)
        _image_cache[png] = image
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = image
    nt.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
    _texture_cache[png] = mat
    return mat


def glass_material() -> bpy.types.Material:
    mat = bpy.data.materials.new("hourglass_glass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.50, 0.78, 0.78, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.08
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.78
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = 0.78
    bsdf.inputs["Alpha"].default_value = 0.28
    if hasattr(mat, "surface_render_method"):
        try:
            mat.surface_render_method = "DITHERED"
        except Exception:
            pass
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"
    if hasattr(mat, "use_screen_refraction"):
        mat.use_screen_refraction = True
    return mat


def rounded_rect_points(width: float, height: float, radius: float, segments: int = 12) -> list[tuple[float, float]]:
    radius = max(0.0, min(radius, width / 2, height / 2))
    hx, hy = width / 2, height / 2
    if radius <= 1e-8:
        return [(hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy)]
    corners = [
        (hx - radius, hy - radius, 0.0),
        (-hx + radius, hy - radius, 90.0),
        (-hx + radius, -hy + radius, 180.0),
        (hx - radius, -hy + radius, 270.0),
    ]
    points = []
    for cx, cy, start in corners:
        for i in range(segments + 1):
            angle = math.radians(start + 90.0 * i / segments)
            points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def circle_points(radius: float, segments: int = 72) -> list[tuple[float, float]]:
    return [
        (radius * math.cos(2 * math.pi * i / segments), radius * math.sin(2 * math.pi * i / segments))
        for i in range(segments)
    ]


def star_points(radius: float, inner_ratio: float = 0.46) -> list[tuple[float, float]]:
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * inner_ratio
        angle = math.pi / 2 + math.pi * 2 * i / 10
        points.append((r * math.cos(angle), r * math.sin(angle)))
    return points


def make_flat_piece(
    name: str,
    outline: list[tuple[float, float]],
    width: float,
    height: float,
    thickness: float,
    top_material: bpy.types.Material,
    side_material: bpy.types.Material,
    bottom_material: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """CCW 外形を厚み方向へ押し出した、UV付き多様体薄板。"""
    bottom_material = bottom_material or side_material
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    top = [bm.verts.new((x, y, thickness)) for x, y in outline]
    bottom = [bm.verts.new((x, y, 0.0)) for x, y in outline]
    bm.verts.ensure_lookup_table()
    top_face = bm.faces.new(top)
    bottom_face = bm.faces.new(list(reversed(bottom)))
    sides = []
    for i in range(len(outline)):
        j = (i + 1) % len(outline)
        sides.append(bm.faces.new([bottom[i], bottom[j], top[j], top[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    uv_layer = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        for loop in face.loops:
            co = loop.vert.co
            if face is bottom_face:
                loop[uv_layer].uv = (0.5 - co.x / width, 0.5 + co.y / height)
            else:
                loop[uv_layer].uv = (0.5 + co.x / width, 0.5 + co.y / height)

    mesh.materials.append(top_material)
    mesh.materials.append(side_material)
    mesh.materials.append(bottom_material)
    top_face.material_index = 0
    for side in sides:
        side.material_index = 1
        side.smooth = True
    bottom_face.material_index = 2
    top_face.smooth = False
    bottom_face.smooth = False

    bm.to_mesh(mesh)
    bm.free()
    mesh.validate(verbose=False)
    mesh.update()
    return obj


def make_panel(info: dict) -> list[bpy.types.Object]:
    width = info["width_mm"] * 0.001
    height = info["height_mm"] * 0.001
    thickness = info["thick_mm"] * 0.001
    radius = info.get("corner_r_mm", 0.0) * 0.001
    outline = rounded_rect_points(width, height, radius)
    obj = make_flat_piece(
        info["id"],
        outline,
        width,
        height,
        thickness,
        texture_material(info["face_tex"]),
        solid_material(info["id"] + "_side", info["side_color"]),
        texture_material(info["back_tex"]),
    )
    return [obj]


def make_token(info: dict) -> list[bpy.types.Object]:
    kind = info["kind"]
    thickness = info["thick_mm"] * 0.001
    if kind == "token_round":
        width = height = info["diameter_mm"] * 0.001
        outline = circle_points(width / 2)
    elif kind == "token_oval":
        width = info["width_mm"] * 0.001
        height = info["height_mm"] * 0.001
        outline = [
            (
                width * 0.5 * math.cos(math.pi * 2 * i / 64),
                height * 0.5 * math.sin(math.pi * 2 * i / 64),
            )
            for i in range(64)
        ]
    elif kind == "token_rect":
        width = info["width_mm"] * 0.001
        height = info["height_mm"] * 0.001
        outline = rounded_rect_points(width, height, info["corner_r_mm"] * 0.001)
    elif kind == "token_star":
        width = height = info["diameter_mm"] * 0.001
        outline = star_points(width / 2 * 0.94)
    else:
        raise ValueError(kind)
    side = solid_material(info["id"] + "_side", info["side_color"])
    obj = make_flat_piece(
        info["id"],
        outline,
        width,
        height,
        thickness,
        texture_material(info["face_tex"]),
        side,
        side,
    )
    return [obj]


def add_cylinder(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    material: bpy.types.Material,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    vertices: int = 48,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        end_fill_type="NGON",
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def add_cube(
    name: str,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float],
    material: bpy.types.Material,
    bevel: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        modifier = obj.modifiers.new("soft_edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.materials.append(material)
    return obj


def make_marker(info: dict) -> list[bpy.types.Object]:
    length = info["length_mm"] * 0.001
    diameter = info["diameter_mm"] * 0.001
    radius = diameter / 2
    role = solid_material(info["id"] + "_role", info["color"], roughness=0.62)
    dark = solid_material(info["id"] + "_dark", [max(0, int(v * 0.70)) for v in info["color"]], roughness=0.68)
    paper = solid_material("marker_paper", [244, 239, 225], roughness=0.80)
    rotation = (math.pi / 2, 0.0, 0.0)

    objects = [
        add_cylinder(
            info["id"] + "_barrel",
            radius,
            length * 0.625,
            (0.0, -length * 0.0025, radius),
            role,
            rotation,
        ),
        add_cylinder(
            info["id"] + "_cap",
            radius,
            length * 0.19,
            (0.0, length * 0.405, radius),
            dark,
            rotation,
        ),
        add_cylinder(
            info["id"] + "_grip",
            radius,
            length * 0.11,
            (0.0, -length * 0.37, radius),
            paper,
            rotation,
        ),
    ]
    bpy.ops.mesh.primitive_cone_add(
        vertices=48,
        radius1=radius * 0.62,
        radius2=radius * 0.18,
        depth=length * 0.075,
        location=(0.0, -length * 0.4625, radius),
        rotation=rotation,
    )
    tip = bpy.context.active_object
    tip.name = info["id"] + "_tip"
    tip.data.materials.append(dark)
    objects.append(tip)
    return objects


def make_timer(info: dict) -> list[bpy.types.Object]:
    width = info["width_mm"] * 0.001
    depth = info["depth_mm"] * 0.001
    height = info["height_mm"] * 0.001
    base_t = 0.004
    frame = solid_material("timer_frame", [39, 67, 74], roughness=0.68)
    honey = solid_material("timer_sand", [226, 170, 53], roughness=0.84)
    glass = glass_material()

    objects = [
        add_cube("timer_bottom", (width, depth, base_t), (0, 0, base_t / 2), frame, bevel=0.002),
        add_cube("timer_top", (width, depth, base_t), (0, 0, height - base_t / 2), frame, bevel=0.002),
    ]
    post_r = 0.0015
    for ix in (-1, 1):
        for iy in (-1, 1):
            objects.append(add_cylinder(
                f"timer_post_{ix}_{iy}",
                post_r,
                height - base_t * 2,
                (ix * width * 0.39, iy * depth * 0.39, height / 2),
                frame,
            ))

    chamber_h = (height - base_t * 2) / 2
    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=width * 0.34,
        radius2=width * 0.085,
        depth=chamber_h,
        location=(0, 0, base_t + chamber_h / 2),
    )
    lower_glass = bpy.context.active_object
    lower_glass.name = "timer_glass_lower"
    lower_glass.data.materials.append(glass)
    objects.append(lower_glass)
    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=width * 0.085,
        radius2=width * 0.34,
        depth=chamber_h,
        location=(0, 0, height - base_t - chamber_h / 2),
    )
    upper_glass = bpy.context.active_object
    upper_glass.name = "timer_glass_upper"
    upper_glass.data.materials.append(glass)
    objects.append(upper_glass)

    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=width * 0.28,
        radius2=width * 0.025,
        depth=chamber_h * 0.48,
        location=(0, 0, base_t + chamber_h * 0.24),
    )
    sand = bpy.context.active_object
    sand.name = "timer_sand"
    sand.data.materials.append(honey)
    objects.append(sand)
    return objects


def make_component(info: dict) -> list[bpy.types.Object]:
    if info["kind"] == "panel":
        return make_panel(info)
    if info["kind"].startswith("token_"):
        return make_token(info)
    if info["kind"] == "marker":
        return make_marker(info)
    if info["kind"] == "timer":
        return make_timer(info)
    raise ValueError(f"Unknown kind: {info['kind']}")


def assert_manifold(objects: list[bpy.types.Object]) -> None:
    failures = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bad_edges = sum(1 for edge in bm.edges if not edge.is_manifold)
        bm.free()
        if bad_edges:
            failures.append(f"{obj.name}:{bad_edges}")
    if failures:
        raise RuntimeError("non-manifold meshes: " + ", ".join(failures))


def select_only(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def export_group(objects: list[bpy.types.Object], filepath: str) -> None:
    select_only(objects)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_image_format="AUTO",
    )


def duplicate_group(objects: list[bpy.types.Object], suffix: str) -> list[bpy.types.Object]:
    duplicates = []
    for obj in objects:
        duplicate = obj.copy()
        if obj.data:
            duplicate.data = obj.data
        duplicate.name = obj.name + suffix
        bpy.context.collection.objects.link(duplicate)
        duplicates.append(duplicate)
    return duplicates


def place_group(
    objects: list[bpy.types.Object],
    x: float,
    y: float,
    z: float = 0.0,
    rotation_z: float = 0.0,
) -> None:
    c, s = math.cos(rotation_z), math.sin(rotation_z)
    for obj in objects:
        ox, oy, oz = obj.location
        obj.location = (x + c * ox - s * oy, y + s * ox + c * oy, z + oz)
        obj.rotation_euler.z += rotation_z


def build_overview(component_objects: dict[str, list[bpy.types.Object]]) -> list[bpy.types.Object]:
    """実セット1箱分を、約560×380mmのテーブル面へ配置する。"""
    overview: list[bpy.types.Object] = []

    def put(component_id: str, x: float, y: float, z: float = 0.0, rotation_z: float = 0.0) -> list[bpy.types.Object]:
        group = component_objects[component_id]
        place_group(group, x, y, z, rotation_z)
        overview.extend(group)
        return group

    put("drawing_pad", -0.275, 0.070)
    put("rule_card", -0.105, 0.090)
    put("role_circle", 0.005, 0.105, rotation_z=-0.035)
    put("role_segment", 0.087, 0.105, rotation_z=0.035)

    prompt_ids = ["prompt_" + prompt_id for prompt_id in [
        "01_sleepy", "02_cold", "03_hungry", "04_surprised",
        "05_waiting", "06_troubled", "07_attention", "08_joy",
        "09_hiding", "10_brave", "11_awkward", "12_make_up",
    ]]
    gx, gy = 0.069, 0.096
    x0, y0 = 0.190, 0.145
    for index, component_id in enumerate(prompt_ids):
        col, row = index % 4, index // 4
        put(component_id, x0 + col * gx, y0 - row * gy)

    put("achievement_card", -0.150, -0.150)

    # 複製は元オブジェクトを移動する前に作る。移動後に複製すると配置オフセットが累積する。
    circle_groups = [
        component_objects["stroke_circle"],
        duplicate_group(component_objects["stroke_circle"], "_set_2"),
    ]
    for group, x in zip(circle_groups, [-0.060, -0.015]):
        place_group(group, x, -0.105)
        overview.extend(group)
    put("stroke_oval", 0.040, -0.105)

    straight_groups = [
        component_objects["stroke_straight"],
        duplicate_group(component_objects["stroke_straight"], "_set_2"),
    ]
    for group, x in zip(straight_groups, [-0.050, 0.005]):
        place_group(group, x, -0.155)
        overview.extend(group)
    put("stroke_bend", 0.065, -0.155)

    star_groups = [
        component_objects["achievement_token"],
        duplicate_group(component_objects["achievement_token"], "_set_2"),
        duplicate_group(component_objects["achievement_token"], "_set_3"),
    ]
    for group, x in zip(star_groups, [-0.190, -0.150, -0.110]):
        place_group(group, x, -0.205)
        overview.extend(group)

    put("marker_circle", 0.120, -0.165)
    put("marker_segment", 0.150, -0.165)
    put("timer_3min", 0.480, -0.155)
    return overview


# ---------------------------------------------------------------- build
clear_scene()
component_objects: dict[str, list[bpy.types.Object]] = {}
for component_id, info in MANIFEST["components"].items():
    component_objects[component_id] = make_component(info)

all_unique_objects = [obj for objects in component_objects.values() for obj in objects]
assert_manifold(all_unique_objects)

# 単体 GLB は全ギャラリー項目（表示専用プレイ例を含む）を書き出す。
for component_id, objects in component_objects.items():
    export_group(objects, os.path.join(GLB, component_id + ".glb"))

overview_objects = build_overview(component_objects)
export_group(overview_objects, os.path.join(OUT, MANIFEST["overview_glb"]))

mesh_count = sum(1 for obj in overview_objects if obj.type == "MESH")
print("DONE components:", len(component_objects))
print("overview meshes:", mesh_count)
print("GLB:", os.path.join(OUT, MANIFEST["overview_glb"]))
