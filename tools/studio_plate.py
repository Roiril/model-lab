"""配置済み core 3MF を Studio 用の個別 STL と manifest に展開する。"""

import hashlib
import io
import json
import math
import os
import re
import struct
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS = os.path.join(ROOT, "exports")
PLATES = os.path.join(ROOT, "viewer", "studio", "plates")
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
IDENTITY = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)
GEOMETRY_TOLERANCE = 0.0003
PLATE_WELD = 0.0001


def _tag(element):
    return element.tag.rsplit("}", 1)[-1]


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_stl_triangles(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    triangles = []
    if len(raw) >= 84:
        count = struct.unpack("<I", raw[80:84])[0]
        if len(raw) == 84 + count * 50:
            for index in range(count):
                offset = 84 + index * 50 + 12
                values = struct.unpack("<9f", raw[offset:offset + 36])
                triangles.append(tuple(tuple(values[vertex * 3:vertex * 3 + 3])
                                       for vertex in range(3)))
    if not triangles:
        text = raw.decode("ascii", "replace")
        points = [tuple(float(value) for value in match)
                  for match in re.findall(r"vertex\s+(\S+)\s+(\S+)\s+(\S+)", text)]
        if not points or len(points) % 3:
            raise ValueError(f"source STL is invalid or empty: {path}")
        triangles = [tuple(points[index:index + 3]) for index in range(0, len(points), 3)]
    if not all(math.isfinite(value) for triangle in triangles for point in triangle for value in point):
        raise ValueError(f"source STL contains a non-finite coordinate: {path}")
    return triangles


def _rotate_quarter(point, quarter_turns):
    x, y, z = point
    return ((x, y, z), (-y, x, z), (-x, -y, z), (y, -x, z))[quarter_turns]


def _shape_signature(triangles, quarter_turns=0):
    welded = [[tuple(round(value / PLATE_WELD) * PLATE_WELD for value in point)
               for point in triangle] for triangle in triangles]
    rotated = [[_rotate_quarter(point, quarter_turns) for point in triangle]
               for triangle in welded]
    points = [point for triangle in rotated for point in triangle]
    minimum = tuple(min(point[axis] for point in points) for axis in range(3))
    normalized = [[tuple(point[axis] - minimum[axis] for axis in range(3))
                   for point in triangle] for triangle in rotated]
    normalized = [sorted(triangle, key=lambda point: tuple(round(value, 4) for value in point))
                  for triangle in normalized]
    return sorted(normalized,
                  key=lambda triangle: tuple(round(value, 4) for point in triangle for value in point))


def _geometry_matches(mesh_triangles, source_triangles):
    if len(mesh_triangles) != len(source_triangles):
        return False
    mesh_signature = _shape_signature(mesh_triangles)
    for quarter_turns in range(4):
        source_signature = _shape_signature(source_triangles, quarter_turns)
        if all(abs(mesh_value - source_value) <= GEOMETRY_TOLERANCE
               for mesh_triangle, source_triangle in zip(mesh_signature, source_signature)
               for mesh_point, source_point in zip(mesh_triangle, source_triangle)
               for mesh_value, source_value in zip(mesh_point, source_point)):
            return True
    return False


def _parse_transform(value, object_id):
    if value is None:
        return IDENTITY
    fields = value.split()
    if len(fields) != 12:
        raise ValueError(f"object {object_id}: build transform must contain 12 numbers")
    try:
        transform = tuple(float(field) for field in fields)
    except ValueError as exc:
        raise ValueError(f"object {object_id}: build transform contains a non-number") from exc
    if not all(math.isfinite(number) for number in transform):
        raise ValueError(f"object {object_id}: build transform contains a non-finite number")
    return transform


def _transform_vertex(vertex, transform):
    x, y, z = vertex
    return (
        x * transform[0] + y * transform[3] + z * transform[6] + transform[9],
        x * transform[1] + y * transform[4] + z * transform[7] + transform[10],
        x * transform[2] + y * transform[5] + z * transform[8] + transform[11],
    )


def _float32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _normal(a, b, c):
    ux, uy, uz = (b[i] - a[i] for i in range(3))
    vx, vy, vz = (c[i] - a[i] for i in range(3))
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if not length:
        return 0.0, 0.0, 0.0
    return nx / length, ny / length, nz / length


def _binary_stl(vertices, triangles):
    output = bytearray(b"model-lab Studio plate".ljust(80, b"\0"))
    output.extend(struct.pack("<I", len(triangles)))
    points = []
    for indices in triangles:
        triangle = [vertices[index] for index in indices]
        points.extend(triangle)
        output.extend(struct.pack("<12fH", *_normal(*triangle),
                                  *(coordinate for point in triangle for coordinate in point), 0))
    return bytes(output), points


def _bbox(points):
    if not points:
        raise ValueError("mesh has no triangle vertices")
    quantized = [tuple(_float32(value) for value in point) for point in points]
    return {
        "min": [min(point[axis] for point in quantized) for axis in range(3)],
        "max": [max(point[axis] for point in quantized) for axis in range(3)],
    }


def _metadata_labels(config_root):
    labels = {}
    for object_element in config_root.iter():
        if _tag(object_element) != "object" or "id" not in object_element.attrib:
            continue
        object_id = object_element.attrib["id"]
        names = [child.attrib.get("value") for child in object_element
                 if _tag(child) == "metadata" and child.attrib.get("key") == "name"]
        if len(names) != 1 or not names[0]:
            raise ValueError(f"object {object_id}: model_settings.config needs one source name")
        if object_id in labels:
            raise ValueError(f"duplicate object id in model_settings.config: {object_id}")
        labels[object_id] = names[0]
    return labels


def _reject_unsupported(model_root, archive):
    unit = model_root.attrib.get("unit")
    if unit != "millimeter":
        raise ValueError(f"unsupported 3MF unit: {unit}")
    for element in model_root.iter():
        name = _tag(element)
        if name in {"components", "component"}:
            raise ValueError("3MF components are unsupported")
        if any(attr.rsplit("}", 1)[-1] in {"path", "href"} for attr in element.attrib):
            raise ValueError("3MF external references are unsupported")
    for name in archive.namelist():
        if name.lower().endswith(".model") and name != "3D/3dmodel.model":
            raise ValueError("3MF external model references are unsupported")
    for name in archive.namelist():
        if not name.lower().endswith(".rels"):
            continue
        relationships = ET.fromstring(archive.read(name))
        for relationship in relationships.iter():
            if (_tag(relationship) == "Relationship"
                    and relationship.attrib.get("TargetMode", "").lower() == "external"):
                raise ValueError("3MF external references are unsupported")


def _parse_3mf(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            model_root = ET.fromstring(archive.read("3D/3dmodel.model"))
            config_root = ET.fromstring(archive.read("Metadata/model_settings.config"))
            _reject_unsupported(model_root, archive)
    except KeyError as exc:
        raise ValueError(f"3MF is missing required entry: {exc.args[0]}") from exc
    except (zipfile.BadZipFile, ET.ParseError) as exc:
        raise ValueError(f"invalid 3MF: {path}") from exc

    labels = _metadata_labels(config_root)
    objects = {}
    for element in model_root.iter():
        if _tag(element) != "object":
            continue
        object_id = element.attrib.get("id")
        if not object_id:
            raise ValueError("3MF object has no id")
        if object_id in objects:
            raise ValueError(f"duplicate 3MF object id: {object_id}")
        mesh = next((child for child in element if _tag(child) == "mesh"), None)
        if mesh is None:
            raise ValueError(f"object {object_id}: only mesh objects are supported")
        vertices_node = next((child for child in mesh if _tag(child) == "vertices"), None)
        triangles_node = next((child for child in mesh if _tag(child) == "triangles"), None)
        if vertices_node is None or triangles_node is None:
            raise ValueError(f"object {object_id}: mesh is incomplete")
        try:
            vertices = [tuple(float(vertex.attrib[axis]) for axis in ("x", "y", "z"))
                        for vertex in vertices_node if _tag(vertex) == "vertex"]
            triangles = [tuple(int(triangle.attrib[index]) for index in ("v1", "v2", "v3"))
                         for triangle in triangles_node if _tag(triangle) == "triangle"]
        except (KeyError, ValueError) as exc:
            raise ValueError(f"object {object_id}: invalid mesh coordinates or indices") from exc
        if not vertices or not triangles:
            raise ValueError(f"object {object_id}: mesh is empty")
        if not all(math.isfinite(value) for vertex in vertices for value in vertex):
            raise ValueError(f"object {object_id}: mesh contains a non-finite coordinate")
        if any(index < 0 or index >= len(vertices) for triangle in triangles for index in triangle):
            raise ValueError(f"object {object_id}: triangle index is outside the vertex list")
        objects[object_id] = (vertices, triangles)

    build = next((element for element in model_root if _tag(element) == "build"), None)
    if build is None:
        raise ValueError("3MF has no build")
    items = []
    seen = set()
    for item in build:
        if _tag(item) != "item":
            continue
        object_id = item.attrib.get("objectid")
        if object_id not in objects:
            raise ValueError(f"build references unknown object: {object_id}")
        if object_id in seen:
            raise ValueError(f"object {object_id}: multiple build items are unsupported")
        seen.add(object_id)
        items.append((object_id, _parse_transform(item.attrib.get("transform"), object_id)))
    if not items:
        raise ValueError("3MF build has no items")
    if set(labels) != seen:
        missing_labels = sorted(seen - set(labels))
        unused_labels = sorted(set(labels) - seen)
        raise ValueError(f"3MF/config object mismatch: missing labels={missing_labels}, unused labels={unused_labels}")
    return raw, labels, objects, items


def _safe_suffix(model, source_part):
    prefix = model + "-"
    suffix = source_part[len(prefix):] if source_part.startswith(prefix) else source_part
    suffix = re.sub(r"[^A-Za-z0-9._-]+", "-", suffix).strip("-._")
    if not suffix:
        raise ValueError(f"source part has no safe filename component: {source_part!r}")
    return suffix


def _write_temp(directory, filename, data):
    os.makedirs(directory, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix=f".{filename}.", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
    except Exception:
        os.unlink(path)
        raise
    return path


def _same_file(path, data, digest=None):
    """既存ファイルが生成内容と同一なら、ロックを伴う置換を避ける。"""
    try:
        if os.path.getsize(path) != len(data):
            return False
        return _sha256_file(path) == (digest or _sha256_bytes(data))
    except FileNotFoundError:
        return False


def export_studio_plate(model, source3mf, bed=(256, 256)):
    """source3mf の build 配置を適用し、Studio 用の各 STL と manifest を公開する。"""
    if not re.fullmatch(r"[A-Za-z0-9._-]+", model):
        raise ValueError(f"unsafe model id: {model!r}")
    source3mf = os.path.abspath(os.fspath(source3mf))
    if not os.path.isfile(source3mf):
        raise FileNotFoundError(f"source 3MF does not exist: {source3mf}")
    if len(bed) != 2 or not all(isinstance(value, (int, float)) and value > 0 for value in bed):
        raise ValueError("bed must contain positive width and depth")

    raw3mf, labels, objects, items = _parse_3mf(source3mf)
    plate_id = _sha256_bytes(raw3mf)
    prepared = []
    parts = []
    for object_id, transform in items:
        source_part = labels[object_id]
        source_file = source_part + ".stl"
        if os.path.basename(source_file) != source_file:
            raise ValueError(f"object {object_id}: source name must be an exports filename")
        source_path = os.path.join(EXPORTS, source_file)
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"source STL does not exist: {source_path}")
        vertices, triangles = objects[object_id]
        mesh_triangles = [tuple(vertices[index] for index in triangle) for triangle in triangles]
        source_triangles = _read_stl_triangles(source_path)
        if not _geometry_matches(mesh_triangles, source_triangles):
            raise ValueError(f"object {object_id}: 3MF geometry does not match {source_file}")
        transformed = [_transform_vertex(vertex, transform) for vertex in vertices]
        stl_data, triangle_points = _binary_stl(transformed, triangles)
        stl_sha256 = _sha256_bytes(stl_data)
        filename = (f"{model}-studio-plate-{plate_id[:12]}-"
                    f"{_safe_suffix(model, source_part)}-{object_id}.stl")
        source_stat = os.stat(source_path)
        part = {
            "file": filename,
            "sourcePart": source_part,
            "sourceFile": source_file,
            "objectId": object_id,
            "buildTransform": list(transform),
            "sha256": stl_sha256,
            "size": len(stl_data),
            "bbox": _bbox(triangle_points),
            "source": {
                "file": source_file,
                "sha256": _sha256_file(source_path),
                "size": source_stat.st_size,
                "mtime": source_stat.st_mtime_ns / 1_000_000.0,
            },
        }
        prepared.append((filename, stl_data, stl_sha256))
        parts.append(part)

    manifest = {
        "version": 1,
        "model": model,
        "kind": "plate",
        "id": plate_id,
        "source3mf": os.path.basename(source3mf),
        "source3mfSha256": plate_id,
        "bed": {"width": bed[0], "depth": bed[1]},
        "parts": parts,
    }
    manifest_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    temporary = []
    manifest_temp = None
    try:
        for filename, data, digest in prepared:
            final_path = os.path.join(EXPORTS, filename)
            if not _same_file(final_path, data, digest):
                temporary.append((_write_temp(EXPORTS, filename, data), final_path))
        manifest_path = os.path.join(PLATES, model + ".json")
        if not _same_file(manifest_path, manifest_data):
            manifest_temp = _write_temp(PLATES, model + ".json", manifest_data)
        for temp_path, final_path in temporary:
            os.replace(temp_path, final_path)
        temporary.clear()
        if manifest_temp is not None:
            os.replace(manifest_temp, manifest_path)
            manifest_temp = None
    finally:
        for temp_path, _ in temporary:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        if manifest_temp is not None and os.path.exists(manifest_temp):
            os.unlink(manifest_temp)
    return manifest


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage: py -3.11 tools/studio_plate.py <model> <path3mf>", file=sys.stderr)
        return 2
    manifest = export_studio_plate(argv[0], argv[1])
    print(f"[studio-plate] {argv[0]}: {len(manifest['parts'])} parts / {manifest['id'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
