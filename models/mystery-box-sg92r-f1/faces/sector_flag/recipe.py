"""Independent numeric mount recipe interpreter; add local solids in build()."""
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "lib"))
from printmech import geometry as G


def loft_box(shape, name="mount_loft"):
    sections = shape["sections"]
    if len(sections) < 2:
        raise ValueError("loft_box requires at least two sections")
    rings = []
    for section in sections:
        d = section["d_mm"]
        u, v = section["center_uv_mm"]
        width, height = section["size_uv_mm"]
        if width <= 0 or height <= 0 or (rings and d <= rings[-1][0]):
            raise ValueError("loft_box sections need positive sizes and increasing d")
        rings.append((d, [(u-width/2, v-height/2), (u+width/2, v-height/2),
                          (u+width/2, v+height/2), (u-width/2, v+height/2)]))
    obj = G.loft_rings(rings, name)
    G.clean(obj, dist=0.00001)
    return obj


def _primitive(shape, name):
    obj = _primitive_solid(shape, name)
    for index, row in enumerate(shape.get("operations", [])):
        operation = {"union": "UNION", "difference": "DIFFERENCE"}.get(row["op"])
        if operation is None:
            raise ValueError(f"Unsupported CSG operation: {row['op']}")
        G.boolean(obj, _primitive(row["shape"], f"{name}_nested_{index}"), operation)
        if not obj.data.polygons:
            raise ValueError(f"Empty CSG result: {name}")
    return obj


def _primitive_solid(shape, name):
    if shape["type"] == "loft_box":
        return loft_box(shape, name)
    center = shape["center_mm"]
    if shape["type"] == "box":
        half = np.asarray(shape["size_mm"]) / 2
        lo, hi = np.asarray(center) - half, np.asarray(center) + half
        obj = G.box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], name)
    elif shape["type"] == "cylinder":
        axis = {"u": "x", "v": "y", "d": "z"}[shape.get("axis", "d")]
        index = "xyz".index(axis)
        half = shape["depth_mm"] / 2
        obj = G.prism(G.circle([center[i] for i in range(3) if i != index], shape["radius_mm"]),
                      axis, center[index]-half, center[index]+half, name)
    else:
        raise ValueError(f"Unsupported recipe primitive: {shape['type']}")
    obj.name = name
    return obj


def _boolean(obj, cutter, operation):
    G.boolean(obj, cutter, operation)
    if not obj.data.polygons:
        raise ValueError(f"Empty CSG result: {obj.name}")


def build_mount(interface):
    recipe = interface["mount_geometry"]
    if recipe["schema"] != "csg-mm-v2":
        raise ValueError("Unsupported mount geometry schema")
    objects = {}
    for name, definition in recipe["parts"].items():
        obj = _primitive(definition["base"], name)
        for index, row in enumerate(definition.get("operations", [])):
            operation = {"union": "UNION", "difference": "DIFFERENCE"}.get(row["op"])
            if operation is None:
                raise ValueError(f"Unsupported CSG operation: {row['op']}")
            _boolean(obj, _primitive(row["shape"], f"{name}_{index}"), operation)
        objects[name] = obj
    return objects["panel"], objects["key_l"], objects["key_r"]


def build(interface, common_params):
    panel, key_l, key_r = build_mount(interface)
    return {part: {"object": obj, "print_rotation": np.eye(4) if part == "panel" else np.diag([1, -1, -1, 1]), "label": label, "color": "#E6E1D8"}
            for part, obj, label in (("panel", panel, "交換面の前板"), ("key_l", key_l, "左の固定キー"), ("key_r", key_r, "右の固定キー"))}
