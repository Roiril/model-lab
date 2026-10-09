"""mm 単位のバイナリ STL を読み書きし、Z 軸まわりに回転する純粋関数。"""
import math
import struct


def read_binary_stl(path):
    """バイナリ STL を 1 面 9 個の座標値からなる tuple のリストとして読む。"""
    with open(path, "rb") as fh:
        raw = fh.read()
    if len(raw) < 84:
        raise ValueError(f"binary STL is shorter than its header: {path}")
    count = struct.unpack("<I", raw[80:84])[0]
    expected = 84 + count * 50
    if len(raw) < expected:
        raise ValueError(f"binary STL is truncated: {path} ({len(raw)} < {expected})")
    return [struct.unpack("<9f", raw[84 + 50 * i + 12:84 + 50 * i + 48]) for i in range(count)]


def _flat_triangle(triangle):
    if len(triangle) == 9:
        return tuple(triangle)
    if len(triangle) == 3 and all(len(vertex) == 3 for vertex in triangle):
        return tuple(value for vertex in triangle for value in vertex)
    raise ValueError("triangle must contain 9 coordinates or 3 xyz vertices")


def write_binary_stl(path, triangles):
    """平坦な 9 座標または 3 個の xyz 頂点で表した面をバイナリ STL に書く。"""
    triangles = [_flat_triangle(triangle) for triangle in triangles]
    with open(path, "wb") as fh:
        fh.write(b"\0" * 80 + struct.pack("<I", len(triangles)))
        for triangle in triangles:
            fh.write(struct.pack("<12fH", 0, 0, 0, *triangle, 0))


def rotate_z(triangles, deg):
    """面を原点まわりに deg 度回転し、平坦な 9 座標の面として返す。"""
    cos_a, sin_a = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    out = []
    for triangle in triangles:
        flat = _flat_triangle(triangle)
        rotated = []
        for k in range(3):
            x, y, z = flat[3 * k:3 * k + 3]
            rotated += [x * cos_a - y * sin_a, x * sin_a + y * cos_a, z]
        out.append(tuple(rotated))
    return out


def box_triangles(x0, x1, y0, y1, z0, z1):
    """軸に平行な直方体を 12 面の三角形として返す。"""
    vertices = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    faces = [(0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6), (0, 1, 5), (0, 5, 4),
             (2, 6, 7), (2, 7, 3), (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5)]
    return [(vertices[a], vertices[b], vertices[c]) for a, b, c in faces]
