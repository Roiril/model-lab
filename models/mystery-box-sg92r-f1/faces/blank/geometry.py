"""Self-contained interpreter for the mount's numeric CSG recipe (mm)."""
from pathlib import Path
import sys

from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "lib"))
from printmech import geometry as G


def clean(obj):
    G.clean(obj, dist=0.00001)


def primitive(shape, name):
    center = shape["center_mm"]
    kind = shape["type"]
    if kind == "box":
        half = [value / 2 for value in shape["size_mm"]]
        obj = G.box(center[0]-half[0], center[0]+half[0], center[1]-half[1], center[1]+half[1],
                    center[2]-half[2], center[2]+half[2], name)
    elif kind == "cylinder":
        axis = {"u": "x", "v": "y", "d": "z"}[shape.get("axis", "d")]
        index = "xyz".index(axis)
        half = shape["depth_mm"] / 2
        obj = G.prism(G.circle([center[i] for i in range(3) if i != index], shape["radius_mm"]),
                      axis, center[index]-half, center[index]+half, name)
    else:
        raise ValueError(f"Unsupported mount primitive: {kind}")
    obj.name = name
    return obj


def boolean(obj, cutter, operation):
    G.boolean(obj, cutter, operation)
    if not obj.data.polygons:
        raise ValueError(f"Empty CSG result: {obj.name}")
    return obj


def build_mount(interface):
    recipe = interface["mount_geometry"]
    if recipe["schema"] != "csg-mm-v1":
        raise ValueError("Unsupported mount recipe version")
    parts = {}
    for part_id, definition in recipe["parts"].items():
        obj = primitive(definition["base"], part_id)
        for index, operation in enumerate(definition.get("operations", [])):
            kind = {"union": "UNION", "difference": "DIFFERENCE"}.get(operation["op"])
            if kind is None:
                raise ValueError(f"Unsupported CSG operation: {operation['op']}")
            cutter = primitive(operation["shape"], f"{part_id}_{index}")
            boolean(obj, cutter, kind)
        parts[part_id] = obj
    return parts["panel"], parts["key_l"], parts["key_r"]


def build(interface, common_params):
    panel, left, right = build_mount(interface)
    # u/v plane on the bed; spring bending remains within the printed layers.
    return {
        "panel": {"object": panel, "print_rotation": Matrix.Identity(4), "label": "空の面板", "color": "#E6E1D8"},
        "key_l": {"object": left, "print_rotation": Matrix.Identity(4), "label": "左の固定キー", "color": "#E6E1D8"},
        "key_r": {"object": right, "print_rotation": Matrix.Identity(4), "label": "右の固定キー", "color": "#E6E1D8"}
    }
