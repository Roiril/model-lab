"""mm 単位の Bambu Studio G-code を読み、層間で支えのない押し出しを調べる。"""
import math
import re

R_SUP = 0.6
CELL = 0.2
INTERNAL = ("Sparse infill", "Internal solid infill", "Floating vertical shell", "Internal Bridge")


def parse_gcode(path):
    """層ごとの押し出し線分と統計を返す。G2/G3 は 0.2mm 以下の弦に分割する。"""
    layers = []
    current = None
    x = y = z = 0.0
    feature = ""
    stats = {}
    obj = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(";"):
                if line.startswith("; CHANGE_LAYER"):
                    current = dict(z=None, segs=[])
                    layers.append(current)
                elif line.startswith("; Z_HEIGHT:") and current is not None:
                    current["z"] = float(line.split(":")[1])
                elif line.startswith("; FEATURE:"):
                    feature = line.split(":", 1)[1].strip()
                elif line.startswith("; start printing object, unique label id:"):
                    obj = int(line.rsplit(":", 1)[1])
                elif line.startswith("; stop printing object"):
                    obj = None
                elif "model printing time" in line or "total estimated time" in line:
                    stats["time"] = line.strip("; \n")
                elif line.startswith("; total filament length"):
                    stats["filament_mm"] = float(line.split(":")[1])
                elif line.startswith("; total filament weight"):
                    stats["filament_g_header"] = line.split(":")[1].strip()
                continue
            if not (line.startswith("G1 ") or line.startswith("G0 ")
                    or line.startswith("G2 ") or line.startswith("G3 ")):
                continue
            values = dict(re.findall(r"([XYZEIJ])(-?[\d.]+)", line.split(";")[0]))
            nx = float(values.get("X", x))
            ny = float(values.get("Y", y))
            if "Z" in values:
                z = float(values["Z"])
            extrusion = float(values.get("E", 0.0))
            if (current is not None and extrusion > 0
                    and (line.startswith("G1") or line.startswith("G2") or line.startswith("G3"))
                    and (nx != x or ny != y or "I" in values or "J" in values)):
                if (line.startswith("G2") or line.startswith("G3")) and ("I" in values or "J" in values):
                    center_x = x + float(values.get("I", 0.0))
                    center_y = y + float(values.get("J", 0.0))
                    radius = math.hypot(x - center_x, y - center_y)
                    a0 = math.atan2(y - center_y, x - center_x)
                    a1 = math.atan2(ny - center_y, nx - center_x)
                    if line.startswith("G3"):
                        sweep = (a1 - a0) % (2 * math.pi) or 2 * math.pi
                    else:
                        sweep = -((a0 - a1) % (2 * math.pi) or 2 * math.pi)
                    count = max(2, int(abs(sweep) * radius / 0.2))
                    px, py = x, y
                    for i in range(1, count + 1):
                        angle = a0 + sweep * i / count
                        qx, qy = ((center_x + radius * math.cos(angle), center_y + radius * math.sin(angle))
                                  if i < count else (nx, ny))
                        current["segs"].append((px, py, qx, qy, feature, obj, z))
                        px, py = qx, qy
                else:
                    current["segs"].append((x, y, nx, ny, feature, obj, z))
            x, y = nx, ny
    return layers, stats


def coverage(segments, cell=CELL):
    cells = set()
    for x0, y0, x1, y1, *_ in segments:
        count = max(1, int(math.hypot(x1 - x0, y1 - y0) / (cell * 0.7)))
        for i in range(count + 1):
            px = x0 + (x1 - x0) * i / count
            py = y0 + (y1 - y0) * i / count
            cells.add((int(math.floor(px / cell)), int(math.floor(py / cell))))
    return cells


def supported(cells, px, py, r_support=R_SUP, cell=CELL):
    radius = int(math.ceil(r_support / cell))
    cx, cy = int(math.floor(px / cell)), int(math.floor(py / cell))
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx * dx + dy * dy <= radius * radius and (cx + dx, cy + dy) in cells:
                return True
    return False


def floating_report(layers, r_support=R_SUP, cell=CELL):
    """支えの無い押し出しを、外に見える機能と中の詰め物に分けて返す。"""
    xs = [value for layer in layers for segment in layer["segs"] for value in (segment[0], segment[2])]
    ys = [value for layer in layers for segment in layer["segs"] for value in (segment[1], segment[3])]
    center_x = (min(xs) + max(xs)) / 2 if xs else 0.0
    center_y = (min(ys) + max(ys)) / 2 if ys else 0.0
    rows = []
    previous = None
    total = dict(external_unsupported_mm=0.0, bridge_mm=0.0,
                 bridge_unsupported_mm=0.0, internal_unsupported_mm=0.0)
    by_feature = {}
    for layer_index, layer in enumerate(layers):
        if not layer["segs"]:
            continue
        if previous is None:
            previous = coverage(layer["segs"], cell)
            continue
        found = {}
        for x0, y0, x1, y1, feature, *_ in layer["segs"]:
            length = math.hypot(x1 - x0, y1 - y0)
            count = max(1, int(length / 0.2))
            unsupported = []
            for i in range(count + 1):
                px = x0 + (x1 - x0) * i / count
                py = y0 + (y1 - y0) * i / count
                if not supported(previous, px, py, r_support, cell):
                    unsupported.append((px - center_x, py - center_y))
            unsupported_length = length * len(unsupported) / (count + 1)
            if any(key in feature for key in INTERNAL):
                total["internal_unsupported_mm"] += unsupported_length
                continue
            if "Bridge" in feature:
                total["bridge_mm"] += length
                total["bridge_unsupported_mm"] += unsupported_length
            else:
                total["external_unsupported_mm"] += unsupported_length
            by_feature[feature] = by_feature.get(feature, 0.0) + unsupported_length
            if unsupported:
                found.setdefault(feature, []).extend(unsupported)
        for feature, points in found.items():
            if len(points) < 3:
                continue
            rows.append(dict(layer=layer_index, z=layer["z"], feature=feature, points=len(points),
                             x=[round(min(p[0] for p in points), 1), round(max(p[0] for p in points), 1)],
                             y=[round(min(p[1] for p in points), 1), round(max(p[1] for p in points), 1)]))
        previous = coverage(layer["segs"], cell)
    total = {key: round(value, 2) for key, value in total.items()}
    features = {key: round(value, 2) for key, value in by_feature.items() if value > 0.05}
    return total, rows, features
