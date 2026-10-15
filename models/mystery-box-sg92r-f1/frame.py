"""F1 skeleton in world millimetres. Face mechanisms are not imported here."""
import math
from pathlib import Path
import sys

import bmesh
import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from printmech import geometry as G


POST_SIGNS = ((-1, -1), (1, -1), (1, 1), (-1, 1))


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
    owner = receiver["owner"] if isinstance(receiver, dict) else receiver
    if owner in ("upper_frame", "lower_frame"):
        return owner
    # Seen from each face: the left/right end meets one of its two posts.
    corners = {"front": (0, 1), "right": (1, 2), "back": (2, 3), "left": (3, 0)}
    if owner not in ("post_left", "post_right"):
        raise ValueError(f"Unknown receiver owner: {owner}")
    return f"post_{corners[slot][owner == 'post_right']}"


def _ring(top):
    sign = 1 if top else -1
    name = "upper_frame" if top else "lower_frame"
    obj = _box(name, (100, 100, 3.7), (0, 0, sign * 48.15))
    _boolean(obj, _box("opening", (92.6, 92.6, 5), (0, 0, sign * 48.15)), "DIFFERENCE")
    for sx, sy in POST_SIGNS:
        _boolean(obj, _box("joint_pad", (5.75, 5.75, 3), (sx * 44.875, sy * 44.875, sign * 45.5)))
        # Clearance for the cosmetic outside corner of the separate post.
        _boolean(obj, _box("post_outside_clearance", (4.45, 4.45, 3.3),
                           (sx * 48.275, sy * 48.275, sign * 44.65)), "DIFFERENCE")
        # The narrow throat receives the beam. The deeper pocket receives its hook.
        _boolean(obj, _box("snap_throat", (2.1, 5.5, 4), (sx * 45, sy * 45, sign * 45.5)), "DIFFERENCE")
        _boolean(obj, _box("snap_hook_pocket", (2.7, 5.5, 3),
                           (sx * 45.3, sy * 45, sign * 45.6)), "DIFFERENCE")
    if not top:
        for sx in (-1, 1):
            _boolean(obj, _box("wiring_foot_seat", (16, 4, 1.6), (sx * 41, 40, -47.1)))
            _boolean(obj, _box("wiring_spring_slot", (1.7, 17.5, 4.5),
                               (sx * 47.05, 12, -48.25)), "DIFFERENCE")
            _boolean(obj, _box("wiring_hook_pocket", (1.3, 4, 3),
                               (sx * 47.85, 18.75, -49.25)), "DIFFERENCE")
            _boolean(obj, _box("wiring_keyhole_entry", (2.3, 2.5, 4.5),
                               (sx * 47.35, 19.5, -48.25)), "DIFFERENCE")
    return obj


def _post(index):
    sx, sy = POST_SIGNS[index]
    obj = _box(f"post_{index}", (3.7, 3.7, 92.1), (sx * 48.15, sy * 48.15, 0))
    _boolean(obj, _box("post_inside", (6, 6, 87.5), (sx * 45, sy * 45, 0)))
    for sz in (-1, 1):
        _boolean(obj, _box("spring_clearance", (3.05, 6.5, 15.5),
                           (sx * 45.125, sy * 45, sz * 36.5)), "DIFFERENCE")
        _boolean(obj, _box("spring", (1.6, 5, 18.25),
                           (sx * 45, sy * 45, sz * 37.625)))
        _boolean(obj, _box("spring_hook", (0.8, 3, 1.8),
                           (sx * 46, sy * 45, sz * 45.25)))
    return obj


def _wiring():
    obj = _box("wiring", (56, 40, 2), (0, 0, -42.75))
    # Five independent 6x3 open channels; the bottom blank has no servo lead.
    for y in (-12, -4, 4, 12):
        _boolean(obj, _box("channel_divider", (56, 2, 3.2), (0, y, -40.35)))
    for sx in (-1, 1):
        _boolean(obj, _box("foot_arm", (10, 4, 2), (sx * 30, 18, -42.75)))
        _boolean(obj, _box("foot_bridge", (6, 24, 2), (sx * 36, 29, -42.75)))
        _boolean(obj, _box("foot_leg", (3, 4, 4.3), (sx * 36.75, 40, -43.9)))
        _boolean(obj, _box("foot", (6, 4, 2), (sx * 37.75, 40, -43.05)))
        _boolean(obj, _box("foot_stop", (3, 4, 2.2), (sx * 36.75, 40, -44.95)))
        _boolean(obj, _box("wiring_clip_root", (21.4, 2, 2.2), (sx * 36.95, 4.5, -43.7)))
        _boolean(obj, _box("wiring_clip_anchor", (1.2, 2, 6.2), (sx * 47.05, 4.5, -46.5)))
        _boolean(obj, _box("wiring_clip_arm", (1.2, 15.2, 5), (sx * 47.05, 11.4, -47.1)))
        _boolean(obj, _box("wiring_clip_hook", (0.8, 2, 1.6), (sx * 47.85, 18, -48.8)))
        # Free spring length is 13.75mm above the floor, not the face-key length.
        _boolean(obj, _box("tray_spring_root", (3, 5, 2), (sx * 9, 0, -42.75)))
        spring = _box("tray_spring", (1.6, 5, 15.75), (sx * 9, 0, -35.875))
        _boolean(spring, _shape({"type": "cylinder", "radius_mm": 9.8, "depth_mm": 18,
                                 "center_mm": [0, 0, -35.875], "axis": "d"}, "tray_turn_clearance"), "INTERSECT")
        _boolean(obj, spring)
        _boolean(obj, _box("tray_spring_hook", (0.8, 3, 2.4), (sx * 10, 0, -29.2)))
        for sy in (-1, 1):
            _boolean(obj, _box("tray_stop", (3, 3, 9.7), (sx * 8, sy * 8, -37.1)))
    return obj


def _tray():
    obj = _box("tray", (24, 24, 44), (0, 0, -10))
    _boolean(obj, _box("tray_inside", (20, 20, 41), (0, 0, -7.5)), "DIFFERENCE")
    for sign in (-1, 1):
        _boolean(obj, _box("latch_throat", (5.05, 16.4, 5), (sign * 7.525, 0, -30)), "DIFFERENCE")
        _boolean(obj, _box("latch_pocket", (5.8, 16.4, 3), (sign * 7.9, 0, -29.15)), "DIFFERENCE")
        # Relieve the upper roof of the pocket with a 45-degree print chamfer.
        # The lower retention shelf and the four separate downward stops remain
        # unchanged; the outside wall is still at least 1.2 mm thick.
        _boolean(obj, G.prism([(sign * 10, -27.65), (sign * 10.8, -27.65),
                              (sign * 10, -26.85)], "y", -8.2, 8.2,
                             "latch_roof_chamfer"), "DIFFERENCE")
    return obj


def build(interface, common_params):
    objects = {"lower_frame": _ring(False), "upper_frame": _ring(True)}
    objects.update({f"post_{i}": _post(i) for i in range(4)})
    for slot, matrix in interface["slot_transforms_mm"].items():
        for receiver in interface["mount_geometry"]["frame_receivers"]:
            owner = owner_for(slot, receiver)
            _boolean(objects[owner], _shape(receiver, f"{slot}_{receiver['id']}", matrix))
    for sx in (-1, 1):
        _boolean(objects["lower_frame"], _box("wiring_vertical_entry", (2.3, 2.5, 32.5),
                                              (sx * 47.35, 19.5, -34.25)), "DIFFERENCE")
    objects["wiring"] = _wiring()
    objects["tray"] = _tray()
    labels = {"lower_frame": "下枠", "upper_frame": "上枠", "wiring": "面別の配線案内", "tray": "中央の着脱トレー"}
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
        elif part == "upper_frame":
            rotation[:3, :3] = ((1, 0, 0), (0, -1, 0), (0, 0, -1))
        result[part] = {"object": obj, "print_rotation": rotation,
                        "label": labels.get(part, f"柱{int(part[-1]) + 1}" if part.startswith("post_") else part),
                        "color": "#D2CDC4"}
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


def _tray_path():
    rotation = np.asarray(Matrix.Rotation(math.radians(35), 4, "Z"))
    frames = []
    for distance in np.linspace(80, 0, 161):
        matrix = rotation.copy()
        matrix[2, 3] = distance
        frames.append({"tray": matrix})
    for angle in np.linspace(35, 0, 36)[1:]:
        frames.append({"tray": np.asarray(Matrix.Rotation(math.radians(angle), 4, "Z"))})
    return frames


def _wiring_path():
    frames = _path("wiring", (0, 1.5, 100), (0, 1.5, 0))
    frames.extend(_path("wiring", (0, 1.5, 0))[1:])
    return frames


def assembly_steps(interface, common_params):
    result = [{"id": "lower-frame", "title": "下枠を置く", "instruction": "下枠を水平に置きます。", "moving": ["lower_frame"],
               "frames": [{"lower_frame": np.eye(4)}, {"lower_frame": np.eye(4)}]}]
    for index in range(4):
        part = f"post_{index}"
        result.append({"id": f"insert-{part}", "title": f"柱{index + 1}を入れる",
                       "instruction": "柱の下端の爪を内側へ押し、下枠の角へまっすぐ差して離します。",
                       "moving": [part], "frames": _path(part, (0, 0, 12))})
    result.extend([
        {"id": "wiring", "title": "配線案内を置く", "instruction": "上枠を付ける前に、配線案内を後ろへ1.5mmずらして下ろします。座ったら前へ1.5mm戻して左右の爪を下枠へ掛けます。5本の開放溝に面別の線を置けます。",
         "moving": ["wiring"], "frames": _wiring_path()},
        {"id": "upper-frame", "title": "上枠を取り付ける", "instruction": "4本の柱の上端の爪を押し、上枠を下げて爪を戻します。",
         "moving": ["upper_frame"], "frames": _path("upper_frame", (0, 0, 12))},
        {"id": "tray", "title": "中央トレーを取り付ける", "instruction": "中央トレーを上から見て35度回した姿勢で下げ、底が座ったら0度へ戻します。外すときは35度回して上へ抜きます。",
         "moving": ["tray"], "frames": _tray_path()}
    ])
    return result


def interfaces(interface, common_params):
    result = []
    for index in range(4):
        for suffix, direction in (("bottom", (0, 0, 1)), ("top", (0, 0, -1))):
            result.append({"id": f"post-{index}-{suffix}", "type": "retention", "parts": [f"post_{index}"],
                           "direction": list(direction), "max_free_mm": 0.5, "engage_depth_mm": 1.8})
    result.extend([
        {"id": "wiring-seated", "type": "retention", "parts": ["wiring"], "direction": [0, 0, -1], "max_free_mm": 0.5, "engage_depth_mm": 2},
        {"id": "wiring-up", "type": "retention", "parts": ["wiring"], "direction": [0, 0, 1], "max_free_mm": 0.5, "engage_depth_mm": 1.6},
        {"id": "tray-down", "type": "retention", "parts": ["tray"], "direction": [0, 0, -1], "max_free_mm": 0.5, "engage_depth_mm": 2.4},
        {"id": "tray-up", "type": "retention", "parts": ["tray"], "direction": [0, 0, 1], "max_free_mm": 0.5, "engage_depth_mm": 2.4}
    ])
    return result


def allowances(interface, common_params):
    result = []
    for index, (sx, sy) in enumerate(POST_SIGNS):
        for name, sz in (("lower_frame", -1), ("upper_frame", 1)):
            result.append({"type": "snap", "pairs": [[f"post_{index}", name]], "engage_mm": 2.4,
                           "deflection_mm": 0.6, "strain_percent": 0.4444444444,
                           "basis": "自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。",
                           "region_mm": [np.minimum([sx * 43.5, sy * 42, sz * 43.9], [sx * 46.7, sy * 48, sz * 47.1]).tolist(),
                                         np.maximum([sx * 43.5, sy * 42, sz * 43.9], [sx * 46.7, sy * 48, sz * 47.1]).tolist()],
                           "steps": [f"insert-post_{index}" if sz < 0 else "upper-frame"]})
    return result
