"""F1 skeleton in world millimetres. Face mechanisms are not imported here."""
import math
import importlib.util
from pathlib import Path
import sys

import bmesh
import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from printmech import geometry as G


POST_SIGNS = ((-1, -1), (1, -1), (1, 1), (-1, 1))
SIDE_SLOTS = ("front", "right", "back", "left")


def _services():
    spec = importlib.util.spec_from_file_location("_resident_frame_wiring", Path(__file__).with_name("frame_wiring.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _clean(obj):
    G.clean(obj, dist=0.00001)


def _shape(shape, name, transform=None):
    center = shape["center_mm"]
    if shape["type"] == "box":
        half = np.asarray(shape["size_mm"]) / 2
        lo, hi = np.asarray(center) - half, np.asarray(center) + half
        obj = G.box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], name)
    elif shape["type"] == "cylinder":
        axis = {"u": "x", "v": "y", "d": "z"}[shape.get("axis", "d")]
        index = "xyz".index(axis)
        center_2d = [center[i] for i in range(3) if i != index]
        half = shape["depth_mm"] / 2
        obj = G.prism(G.circle(center_2d, shape["radius_mm"]), axis,
                      center[index] - half, center[index] + half, name)
    else:
        raise ValueError(f"Unsupported frame primitive: {shape['type']}")
    for index, operation in enumerate(shape.get("operations", [])):
        _boolean(obj, _shape(operation["shape"], f"{name}_{index}"), operation["op"].upper())
    obj.name = name
    if transform is not None:
        obj.data.transform(Matrix(transform))
        obj.data.update()
    return obj


def _box(name, size, center):
    return _shape({"type": "box", "size_mm": size, "center_mm": center}, name)


def _boolean(obj, other, operation="UNION"):
    G.boolean(obj, other, operation)
    if not obj.data.polygons:
        raise ValueError(f"Empty frame part: {obj.name}")
    return obj


def owner_for(slot, receiver):
    """Return the local skeleton owner of a face receiver descriptor."""
    if slot == "top":
        return "upper_frame"
    if slot == "bottom":
        return "lower_frame"
    if slot not in SIDE_SLOTS:
        raise ValueError(f"Unknown receiver slot: {slot}")
    return f"carrier_{slot}"


def _ring(top, interface):
    sign = 1 if top else -1
    name = "upper_frame" if top else "lower_frame"
    obj = _box(name, (100, 100, 6), (0, 0, sign * 47))
    _boolean(obj, _box("opening", (88, 88, 8), (0, 0, sign * 47)), "DIFFERENCE")
    # The full bar enters the pocket. Its outer wall is the hard outward stop.
    for slot in SIDE_SLOTS:
        matrix = interface["slot_transforms_mm"][slot]
        sign_v = -1 if top else 1
        stop_d = 6.2 if slot == "back" and not top else 6.4
        back = G.prism([(sign_v * 44, stop_d - 0.4), (sign_v * 48, stop_d - 0.4),
                        (sign_v * 46.4, stop_d + 1.2), (sign_v * 44, stop_d + 1.2)],
                       "x", -44.5, 44.5, "carrier_pocket_back")
        back.data.transform(Matrix(matrix))
        _boolean(obj, back)
        pocket = G.prism([(sign_v * 43.5, 3), (sign_v * 48, 3),
                          (sign_v * (51 - stop_d), stop_d), (sign_v * 43.5, stop_d)],
                         "x", -41.7, 41.7, "carrier_pocket")
        pocket.data.transform(Matrix(matrix))
        _boolean(obj, pocket, "DIFFERENCE")
    for sx, sy in POST_SIGNS:
        # The narrow throat receives the beam. The deeper pocket receives its hook.
        _boolean(obj, _box("snap_throat", (2.1, 6.5, 3.5),
                           (sx * 46.5, sy * 47, sign * 45.25)), "DIFFERENCE")
        _boolean(obj, G.prism([(sx * 45.45, sign * 47), (sx * 46.5, sign * 48.05),
                              (sx * 47.55, sign * 47)], "y", sy * 47 - 3.25, sy * 47 + 3.25,
                             "snap_throat_roof"), "DIFFERENCE")
        _boolean(obj, _box("snap_hook_pocket", (0.6, 6.5, 2.3),
                           (sx * 47.85, sy * 47, sign * 45.25)), "DIFFERENCE")
    return obj


def _carrier_pockets(obj, top, interface):
    for slot in SIDE_SLOTS:
        stop_d = 6.2 if slot == "back" and not top else 6.4
        sign_v = -1 if top else 1
        pocket = G.prism([(sign_v * 43.5, 3), (sign_v * 48, 3),
                          (sign_v * (51 - stop_d), stop_d), (sign_v * 43.5, stop_d)],
                         "x", -41.7, 41.7, "carrier_receiver_clearance")
        pocket.data.transform(Matrix(interface["slot_transforms_mm"][slot]))
        _boolean(obj, pocket, "DIFFERENCE")
    return obj


def _post(index):
    sx, sy = POST_SIGNS[index]
    obj = _box(f"post_{index}", (6, 6, 87.5), (sx * 47, sy * 47, 0))
    for sz in (-1, 1):
        _boolean(obj, _box("spring_clearance", (3.05, 6.5, 15.5),
                           (sx * 46.975, sy * 47, sz * 36.75)), "DIFFERENCE")
        _boolean(obj, _box("spring", (1.6, 6, 18.25),
                           (sx * 46.5, sy * 47, sz * 37.625)))
        _boolean(obj, _box("spring_hook", (0.6, 6, 1.8),
                           (sx * 47.6, sy * 47, sz * 45.25)))
    return obj


def _carrier(slot, interface):
    obj = _box(f"carrier_{slot}", (3, 95.5, 3), (-40, 0, 4.5))
    _boolean(obj, _box("carrier_rail", (3, 95.5, 3), (40, 0, 4.5)))
    for sign in (-1, 1):
        _boolean(obj, G.prism([(sign * 41.75, 3), (sign * 47.75, 3),
                              (sign * 44.75, 6), (sign * 41.75, 6)],
                             "x", -41.5, 41.5, "carrier_bar"))
    for receiver in interface["mount_geometry"]["frame_receivers"]:
        _boolean(obj, _shape(receiver, f"{slot}_{receiver['id']}"))
    for sign in (-1, 1):
        cutter = G.prism([(sign * 48.5, 2.5), (sign * 48.5, 6.5),
                          (sign * 44.25, 6.5), (sign * 48.25, 2.5)],
                         "x", -42, 42, "carrier_bar_roof")
        _boolean(obj, cutter, "DIFFERENCE")
    obj.data.transform(Matrix(interface["slot_transforms_mm"][slot]))
    return obj


def build(interface, common_params, include_services=True):
    objects = {"lower_frame": _ring(False, interface), "upper_frame": _ring(True, interface)}
    objects.update({f"post_{i}": _post(i) for i in range(4)})
    objects.update({f"carrier_{slot}": _carrier(slot, interface) for slot in SIDE_SLOTS})
    for slot, matrix in interface["slot_transforms_mm"].items():
        if slot in SIDE_SLOTS:
            continue
        for receiver in interface["mount_geometry"]["frame_receivers"]:
            owner = owner_for(slot, receiver)
            _boolean(objects[owner], _shape(receiver, f"{slot}_{receiver['id']}", matrix))
        for receiver in interface["mount_geometry"].get("frame_receiver_slot_additions", {}).get(slot, []):
            _boolean(objects[owner_for(slot, receiver)], _shape(receiver, f"{slot}_{receiver['id']}", matrix))
    _carrier_pockets(objects["lower_frame"], False, interface)
    _carrier_pockets(objects["upper_frame"], True, interface)
    services = _services() if include_services else None
    if services is not None:
        services.apply_receivers(objects, interface)
    labels = {"lower_frame": "下枠", "upper_frame": "上枠"}
    labels.update({f"carrier_{slot}": f"{label}面の受け" for slot, label in
                   (("front", "前"), ("right", "右"), ("back", "後"), ("left", "左"))})
    result = {}
    for part, obj in objects.items():
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=0.000001, verts=list(bm.verts), edges=list(bm.edges))
        bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
        bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.00001)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        rotation = np.eye(4)
        if part.startswith("post_"):
            sign_y = POST_SIGNS[int(part[-1])][1]
            rotation[:3, :3] = ((1, 0, 0), (0, 0, sign_y), (0, -sign_y, 0))
        elif part == "lower_frame":
            rotation[:3, :3] = ((1, 0, 0), (0, -1, 0), (0, 0, -1))
        elif part.startswith("carrier_"):
            slot = part[len("carrier_"):]
            local_print = np.diag([1, -1, -1, 1])
            world = np.asarray(interface["slot_transforms_mm"][slot], dtype=float)
            rotation[:3, :3] = (local_print @ np.linalg.inv(world))[:3, :3]
        result[part] = {"object": obj, "print_rotation": rotation,
                        "label": labels.get(part, f"柱{int(part[-1]) + 1}" if part.startswith("post_") else part),
                        "color": "#D2CDC4"}
    if services is not None:
        result.update(services.build(interface, common_params))
    return result


def _path(part, start, stop=(0, 0, 0)):
    start = np.asarray(start, dtype=float)
    stop = np.asarray(stop, dtype=float)
    count = max(2, math.ceil(float(np.linalg.norm(stop - start)) / 0.5) + 1)
    frames = []
    for fraction in np.linspace(0, 1, count):
        matrix = np.eye(4)
        matrix[:3, 3] = start + fraction * (stop - start)
        frames.append({part: matrix})
    return frames


def assembly_steps(interface, common_params, include_services=True):
    service_steps = {step["id"]: step for step in _services().assembly_steps(interface, common_params)} if include_services else {}
    result = [{"id": "lower-frame", "title": "下枠を置く", "instruction": "下枠を水平に置きます。", "moving": ["lower_frame"],
               "frames": [{"lower_frame": np.eye(4)}, {"lower_frame": np.eye(4)}]}]
    for index in range(4):
        part = f"post_{index}"
        result.append({"id": f"insert-{part}", "title": f"柱{index + 1}を入れる",
                       "instruction": "柱の下端の爪を内側へ押し、下枠の角へまっすぐ差して離します。",
                       "moving": [part], "frames": _path(part, (0, 0, 12))})
    for slot in SIDE_SLOTS:
        if slot == "back" and include_services:
            result.append(service_steps["wiring"])
        part = f"carrier_{slot}"
        result.append({"id": f"insert-{part}", "title": "側面の受けを入れる",
                       "instruction": "上下の横棒を下枠の溝へ合わせて上から下ろします。面の交換時には残します。取り外すときは上枠を外して上へ抜きます。",
                       "moving": [part], "frames": _path(part, (0, 0, 100))})
    result.append({"id": "upper-frame", "title": "上枠を取り付ける",
                   "instruction": "4本の柱の上端の爪を押し、上枠を下げて爪を戻します。",
                   "moving": ["upper_frame"], "frames": _path("upper_frame", (0, 0, 12))})
    if include_services:
        result.append(service_steps["tray"])
    return result


def interfaces(interface, common_params, include_services=True):
    result = []
    for index in range(4):
        for suffix, direction in (("bottom", (0, 0, 1)), ("top", (0, 0, -1))):
            result.append({"id": f"post-{index}-{suffix}", "type": "retention", "parts": [f"post_{index}"],
                           "direction": list(direction), "max_free_mm": 0.5, "engage_depth_mm": 1.8})
    for slot in SIDE_SLOTS:
        matrix = np.asarray(interface["slot_transforms_mm"][slot], dtype=float)
        for label, direction in (("left", (-1, 0, 0)), ("right", (1, 0, 0)),
                                 ("out", (0, 0, -1)), ("in", (0, 0, 1)),
                                 ("down", (0, 1, 0)), ("up", (0, -1, 0))):
            result.append({"id": f"carrier-{slot}-{label}", "type": "retention",
                           "parts": [f"carrier_{slot}"], "direction": (matrix[:3, :3] @ direction).tolist(),
                           "max_free_mm": 0.5, "engage_depth_mm": 3.75})
    if include_services:
        result.extend(_services().interfaces(interface, common_params))
    return result


def allowances(interface, common_params):
    result = []
    for index, (sx, sy) in enumerate(POST_SIGNS):
        for name, sz in (("lower_frame", -1), ("upper_frame", 1)):
            result.append({"type": "snap", "pairs": [[f"post_{index}", name]], "engage_mm": 2.4,
                           "deflection_mm": 0.6, "strain_percent": 0.4444444444,
                           "basis": "自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。",
                           "region_mm": [np.minimum([sx * 47.3, sy * 44, sz * 44.35], [sx * 47.9, sy * 50, sz * 46.15]).tolist(),
                                         np.maximum([sx * 47.3, sy * 44, sz * 44.35], [sx * 47.9, sy * 50, sz * 46.15]).tolist()],
                           "steps": [f"insert-post_{index}" if sz < 0 else "upper-frame"]})
    return result
