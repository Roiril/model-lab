"""V2 shared wiring guide and bayonet tray; world coordinates are millimetres."""
import math
from pathlib import Path
import sys

import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from printmech import geometry as G


def _box(name, size, center):
    lo = np.asarray(center) - np.asarray(size) / 2
    hi = np.asarray(center) + np.asarray(size) / 2
    return G.box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], name)


def apply_receivers(objects, interface):
    """The lower ring supplies the floor; the back carrier supplies the roof."""
    for cx in (-14, 14):
        # The lower ring is printed toward -Z. A narrowing through opening
        # grows its walls at 45 degrees instead of closing with a flat roof.
        # The 7mm T head stops after 0.25mm downward travel on these shoulders.
        floor_profile = [(cx - 3.75, -43.8), (cx + 3.75, -43.8),
                         (cx + 3.75, -47), (cx + 0.25, -50.5),
                         (cx - 0.25, -50.5), (cx - 3.75, -47)]
        G.cut(objects["lower_frame"], G.prism(floor_profile, "y", 42.5, 47.75, "wire_foot_entry_45"))
        # Open at the carrier's lower edge. In its -d print direction this
        # opening expands, so its shoulders do not start in mid-air.
        profile = [(cx - 3.75, 2.5), (cx + 3.75, 2.5),
                   (cx + 3.75, 4), (cx + 2.75, 5), (cx + 2.75, 6.5),
                   (cx - 2.75, 6.5), (cx - 2.75, 5), (cx - 3.75, 4)]
        cutter = G.prism(profile, "y", 45.25, 48.5, "wire_T_capture")
        cutter.data.transform(Matrix(interface["slot_transforms_mm"]["back"]))
        G.cut(objects["carrier_back"], cutter)


def _wiring():
    obj = G.box(-25, 25, -17, 17, -47, -44, "wiring")
    G.union(obj, G.loft_rings([
        (-44, [(-25, -17), (25, -17), (25, 17), (-25, 17)]),
        (-41, [(-28, -20), (28, -20), (28, 20), (-28, 20)])], "floor_45"),
        G.box(-28, 28, -20, 20, -41, -39, "channel_floor"))
    for y in (-12, -4, 4, 12):
        G.union(obj, G.box(-28, 28, y - 1, y + 1, -39, -36, "channel_divider"))
    for sign in (-1, 1):
        cx = sign * 14
        G.union(obj, G.box(cx - 2.5, cx + 2.5, 16.5, 46, -47, -45.45, "wire_stem"),
                G.box(cx - 3.5, cx + 3.5, 46, 47.5, -47, -45.45, "wire_T_head"))
        post = _box("tray_post", (1.6, 5, 11), (sign * 9, 0, -33.5))
        G.intersect(post, G.prism(G.circle((0, 0), 9.8), "z", -40, -27, "turn_clearance"))
        G.union(obj, post)
        hook = [(sign * 9.4, -31.4), (sign * 9.8, -31),
                (sign * 10.4, -30.4), (sign * 10.4, -28), (sign * 9.4, -28)]
        G.union(obj, G.prism(hook, "y", -1.5, 1.5, "tray_hook_45"))
        for sy in (-1, 1):
            G.union(obj, _box("tray_stop", (3, 3, 6.75), (sign * 8, sy * 8, -35.625)))
    return obj


def _tray():
    obj = _box("tray", (24, 24, 44), (0, 0, -10))
    G.cut(obj, _box("tray_inside", (20, 20, 41), (0, 0, -7.5)))
    for sign in (-1, 1):
        G.cut(obj, _box("latch_throat", (5.2, 16.4, 5), (sign * 7.6, 0, -30)),
              _box("latch_pocket", (5.8, 16.4, 3), (sign * 7.9, 0, -29.15)),
              G.prism([(sign * 10, -27.65), (sign * 10.8, -27.65),
                       (sign * 10, -26.85)], "y", -8.2, 8.2, "latch_roof_45"))
    return obj


def build(interface, common_params):
    result = {}
    for part, obj, label in (("wiring", _wiring(), "面別の配線案内"),
                              ("tray", _tray(), "中央の着脱トレー")):
        G.clean(obj, dist=0.00001)
        result[part] = {"object": obj, "print_rotation": np.eye(4),
                        "label": label, "color": "#D2CDC4"}
    return result


def _path(part, start, stop=(0, 0, 0)):
    start, stop = np.asarray(start), np.asarray(stop)
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


def assembly_steps(interface, common_params):
    wiring = _path("wiring", (0, -4, 100), (0, -4, 0))
    wiring.extend(_path("wiring", (0, -4, 0))[1:])
    return [
        {"id": "wiring", "title": "配線案内を置く", "moving": ["wiring"], "frames": wiring,
         "instruction": "下面板と後面の受けを付ける前に、配線案内を前へ4mmずらして下ろします。後ろへ4mm動かしてT字の足を下枠へ入れ、後面の受けと上枠で固定します。"},
        {"id": "tray", "title": "中央トレーを取り付ける", "moving": ["tray"], "frames": _tray_path(),
         "instruction": "中央トレーを上から見て35度回した姿勢で下げ、底が座ったら0度へ戻します。外すときは35度回して上へ抜きます。"}
    ]


def interfaces(interface, common_params):
    result = []
    for label, direction in (("left", (-1, 0, 0)), ("right", (1, 0, 0)),
                              ("front", (0, -1, 0)), ("back", (0, 1, 0)),
                              ("seated", (0, 0, -1)), ("up", (0, 0, 1))):
        result.append({"id": f"wiring-{label}", "type": "retention", "parts": ["wiring"],
                       "direction": list(direction), "max_free_mm": 0.5, "engage_depth_mm": 1.55})
    for label, direction in (("down", (0, 0, -1)), ("up", (0, 0, 1))):
        result.append({"id": f"tray-{label}", "type": "retention", "parts": ["tray"],
                       "direction": list(direction), "max_free_mm": 0.5, "engage_depth_mm": 2.4})
    return result
