"""mm 単位の STL メッシュについて接地、肉厚、段差、下向き面を調べる。Blender の Python で動く。"""
import math

from mathutils import Vector

from .mesh import Mesh, inside


def faces(mesh):
    for index, (a, b, c) in enumerate(mesh.t):
        p, q, r = mesh.v[a], mesh.v[b], mesh.v[c]
        normal = (q - p).cross(r - p)
        area = normal.length / 2
        if area < 1e-9:
            continue
        yield index, (p + q + r) / 3, normal.normalized(), area


def review(mesh, up, exterior_test=None, layer=0.2):
    """印刷姿勢の上向きベクトルを受け、印刷性の数値を返す。

    exterior_test は組み上がった外面を判定する ``callable(center) -> bool``。
    layer と返す距離、面積は mm / mm²。
    """
    up = Vector(up)
    bvh = mesh.bvh()
    heights = [vertex.dot(up) for vertex in mesh.v]
    h0, h1 = min(heights), max(heights)
    result = {}
    contact_area = 0.0
    points = []
    for _index, center, normal, face_area in faces(mesh):
        if normal.dot(up) < -0.999 and center.dot(up) - h0 < 0.05:
            contact_area += face_area
            points.append(center)
    mass_props = mesh.mass_props()
    center_of_mass = Vector(mass_props["com"])
    e1 = up.orthogonal().normalized()
    e2 = up.cross(e1).normalized()
    if points:
        u = [point.dot(e1) for point in points]
        v = [point.dot(e2) for point in points]
        cu, cv = center_of_mass.dot(e1), center_of_mass.dot(e2)
        inside_footprint = min(u) <= cu <= max(u) and min(v) <= cv <= max(v)
        footprint = (max(u) - min(u), max(v) - min(v))
    else:
        inside_footprint, footprint = False, (0, 0)
    result["bed"] = dict(
        contact_mm2=round(contact_area, 1),
        footprint_mm=[round(value, 1) for value in footprint],
        height_mm=round(h1 - h0, 1),
        com_over_footprint=inside_footprint,
        height_to_min_footprint=(round((h1 - h0) / max(0.1, min(footprint)), 2) if points else None),
    )
    thin, terraces, overhangs = [], [], []
    for index, center, normal, face_area in faces(mesh):
        height = center.dot(up) - h0
        vertical = normal.dot(up)
        hit = bvh.ray_cast(center - normal * 1e-3, -normal, 50.0)
        thickness = hit[3] + 1e-3 if hit[0] is not None else None
        if thickness is not None and thickness < 1.2 and hit[1].dot(normal) < -0.6:
            thin.append((thickness, face_area, center))
        if 0.906 < vertical < 0.9994 and height > layer:
            slope = math.degrees(math.acos(min(1.0, vertical)))
            terraces.append((slope, face_area, center,
                             exterior_test(center) if exterior_test is not None else False))
        if vertical < -math.cos(math.radians(44.8)) and height > layer * 1.25:
            overhangs.append((index, face_area, center))

    def cluster(items, position, radius=2.0):
        cells = {}
        for item in items:
            point = position(item)
            key = (round(point.x / radius), round(point.y / radius), round(point.z / radius))
            cells.setdefault(key, []).append(item)
        keys = list(cells)
        parent = {key: key for key in keys}

        def find(key):
            while parent[key] != key:
                parent[key] = parent[parent[key]]
                key = parent[key]
            return key
        for key in keys:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        neighbor = (key[0] + dx, key[1] + dy, key[2] + dz)
                        if neighbor in parent:
                            parent[find(neighbor)] = find(key)
        groups = {}
        for key in keys:
            groups.setdefault(find(key), []).extend(cells[key])
        return list(groups.values())

    rows = []
    for group in cluster(thin, lambda item: item[2]):
        group_area = sum(item[1] for item in group)
        if group_area < 0.5:
            continue
        positions = [item[2] for item in group]
        rows.append(dict(
            min_mm=round(min(item[0] for item in group), 2),
            area_mm2=round(group_area, 1),
            at=[[round(min(point[k] for point in positions), 1) for k in range(3)],
                [round(max(point[k] for point in positions), 1) for k in range(3)]],
        ))
    rows.sort(key=lambda row: row["min_mm"])
    result["thin_under_1_2mm"] = rows
    rows = []
    for group in cluster(terraces, lambda item: item[2], 4.0):
        group_area = sum(item[1] for item in group)
        if group_area < 1.0:
            continue
        positions = [item[2] for item in group]
        exterior_area = sum(item[1] for item in group if item[3])
        rows.append(dict(
            min_slope_deg=round(min(item[0] for item in group), 1),
            area_mm2=round(group_area, 1),
            exterior_mm2=round(exterior_area, 1),
            at=[[round(min(point[k] for point in positions), 1) for k in range(3)],
                [round(max(point[k] for point in positions), 1) for k in range(3)]],
        ))
    rows.sort(key=lambda row: -row["exterior_mm2"] - row["area_mm2"] * 0.01)
    result["terrace_under_25deg"] = rows
    result["terrace_exterior_mm2"] = round(sum(row["exterior_mm2"] for row in rows), 1)
    rows = []
    for group in cluster(overhangs, lambda item: item[2], 1.5):
        group_area = sum(item[1] for item in group)
        positions = [item[2] for item in group]
        center = sum(positions, Vector()) / len(positions)
        supported_count = total_count = 0
        for point in positions:
            direction = point - center
            direction -= up * direction.dot(up)
            if direction.length < 0.3:
                continue
            probe = point + direction.normalized() * 0.6 - up * (layer * 0.5)
            total_count += 1
            supported_count += inside(bvh, probe)
        rows.append(dict(
            area_mm2=round(group_area, 2),
            supported=(round(supported_count / total_count, 2) if total_count else None),
            h=[round(min(point.dot(up) for point in positions) - h0, 2),
               round(max(point.dot(up) for point in positions) - h0, 2)],
            at=[[round(min(point[k] for point in positions), 1) for k in range(3)],
                [round(max(point[k] for point in positions), 1) for k in range(3)]],
        ))
    rows.sort(key=lambda row: -row["area_mm2"])
    result["overhang_clusters"] = rows
    return result


def calibration_plate(thickness, width=20.0, depth=20.0, height=10.0):
    vertices = [Vector((x, y, z)) for z in (0, height) for y in (0, depth) for x in (0, thickness)]
    faces_ = [(0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6), (0, 1, 5), (0, 5, 4),
              (2, 6, 7), (2, 7, 3), (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5)]
    return Mesh(vertices, faces_, f"plate_{thickness}")


def calibration_wedge(deg, length=20.0, width=10.0, base=2.0):
    """上面が水平から deg 傾いた楔。"""
    height = length * math.tan(math.radians(deg))
    points = [(0, 0), (length, 0), (length, base + height), (0, base)]
    vertices = ([Vector((x, 0, z)) for x, z in points]
                + [Vector((x, width, z)) for x, z in points])
    faces_ = [(0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 4, 5), (0, 5, 1),
              (1, 5, 6), (1, 6, 2), (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0)]
    return Mesh(vertices, faces_, f"wedge_{deg}")


def calibrate():
    result = {}
    result["plate_0.6_thin"] = review(calibration_plate(0.6), (0, 0, 1))["thin_under_1_2mm"][:1]
    result["plate_2.0_thin"] = review(calibration_plate(2.0), (0, 0, 1))["thin_under_1_2mm"][:1]
    result["wedge_10_terrace"] = review(calibration_wedge(10), (0, 0, 1))["terrace_under_25deg"][:1]
    result["wedge_45_terrace"] = review(calibration_wedge(45), (0, 0, 1))["terrace_under_25deg"][:1]
    result["knife_20_thin"] = review(
        calibration_wedge(20, length=6.0, base=0.0), (0, 0, 1))["thin_under_1_2mm"][:1]
    result["blunt_70_thin"] = review(
        calibration_wedge(70, length=6.0, base=0.0), (0, 0, 1))["thin_under_1_2mm"][:1]
    result["ok"] = (
        bool(result["plate_0.6_thin"])
        and abs(result["plate_0.6_thin"][0]["min_mm"] - 0.6) < 0.05
        and not result["plate_2.0_thin"]
        and bool(result["wedge_10_terrace"])
        and not result["wedge_45_terrace"]
        and bool(result["knife_20_thin"])
        and not result["blunt_70_thin"]
    )
    return result
