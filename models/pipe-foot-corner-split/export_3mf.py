"""完成した Blender メッシュを、1 パーツの 3MF として書き出す。"""

import math
import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import bpy


MODEL_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
REVISION = "refined-20260922"


def _xml(root):
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _package_parts(name, vertices, triangles, transform):
    ET.register_namespace("", MODEL_NS)
    model = ET.Element(f"{{{MODEL_NS}}}model", {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "ja-JP"})
    ET.SubElement(model, f"{{{MODEL_NS}}}metadata", {"name": "Title"}).text = name
    ET.SubElement(model, f"{{{MODEL_NS}}}metadata", {"name": "Revision"}).text = REVISION
    resources = ET.SubElement(model, f"{{{MODEL_NS}}}resources")
    obj = ET.SubElement(resources, f"{{{MODEL_NS}}}object", {"id": "1", "type": "model", "name": name})
    mesh = ET.SubElement(obj, f"{{{MODEL_NS}}}mesh")
    vertex_xml = ET.SubElement(mesh, f"{{{MODEL_NS}}}vertices")
    for x, y, z in vertices:
        ET.SubElement(vertex_xml, f"{{{MODEL_NS}}}vertex",
                      {"x": f"{x:.8f}", "y": f"{y:.8f}", "z": f"{z:.8f}"})
    triangle_xml = ET.SubElement(mesh, f"{{{MODEL_NS}}}triangles")
    for a, b, c in triangles:
        ET.SubElement(triangle_xml, f"{{{MODEL_NS}}}triangle",
                      {"v1": str(a), "v2": str(b), "v3": str(c)})
    build = ET.SubElement(model, f"{{{MODEL_NS}}}build")
    ET.SubElement(build, f"{{{MODEL_NS}}}item",
                  {"objectid": "1", "printable": "1", "transform": transform})
    model_xml = _xml(model)

    ET.register_namespace("", TYPES_NS)
    types = ET.Element(f"{{{TYPES_NS}}}Types")
    for extension, content_type in (("rels", "application/vnd.openxmlformats-package.relationships+xml"),
                                    ("model", "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"),
                                    ("config", "application/xml")):
        ET.SubElement(types, f"{{{TYPES_NS}}}Default",
                      {"Extension": extension, "ContentType": content_type})
    types_xml = _xml(types)

    ET.register_namespace("", RELS_NS)
    rels = ET.Element(f"{{{RELS_NS}}}Relationships")
    ET.SubElement(rels, f"{{{RELS_NS}}}Relationship",
                  {"Target": "/3D/3dmodel.model", "Id": "rel-1",
                   "Type": "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"})
    rels_xml = _xml(rels)

    config = ET.Element("config")
    config_obj = ET.SubElement(config, "object", {"id": "1"})
    ET.SubElement(config_obj, "metadata", {"key": "name", "value": name})
    part = ET.SubElement(config_obj, "part", {"id": "1", "subtype": "normal_part"})
    ET.SubElement(part, "metadata", {"key": "name", "value": name})
    ET.SubElement(part, "metadata", {"key": "matrix", "value": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"})

    return {"[Content_Types].xml": types_xml,
            "_rels/.rels": rels_xml,
            "3D/3dmodel.model": model_xml,
            "Metadata/model_settings.config": _xml(config)}


def export_part(ob, exports_dir, filename, bed=256):
    """ワールド座標 m の完成メッシュを mm に変換し、盤面中央へ配置する。"""
    if os.path.basename(filename) != filename or not filename.lower().endswith(".3mf"):
        raise ValueError("filename must be a .3mf basename")
    if not math.isfinite(bed) or bed <= 0:
        raise ValueError("bed must be a positive finite number")

    evaluated = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        world = evaluated.matrix_world
        vertices = [tuple((world @ v.co)[axis] * 1000.0 for axis in range(3))
                    for v in mesh.vertices]
        triangles = [tuple(tri.vertices) for tri in mesh.loop_triangles]
    finally:
        evaluated.to_mesh_clear()
    if not vertices or not triangles or not all(math.isfinite(c) for v in vertices for c in v):
        raise ValueError("mesh must contain finite vertices and triangles")

    mins = [min(v[axis] for v in vertices) for axis in range(3)]
    maxs = [max(v[axis] for v in vertices) for axis in range(3)]
    if maxs[0] - mins[0] > bed or maxs[1] - mins[1] > bed:
        raise ValueError("part does not fit the requested bed")
    dx = bed / 2 - (mins[0] + maxs[0]) / 2
    dy = bed / 2 - (mins[1] + maxs[1]) / 2
    dz = -mins[2]
    transform = f"1 0 0 0 1 0 0 0 1 {dx:.8f} {dy:.8f} {dz:.8f}"
    parts = _package_parts(ob.name, vertices, triangles, transform)

    os.makedirs(exports_dir, exist_ok=True)
    path = os.path.join(exports_dir, filename)
    fd, temp_path = tempfile.mkstemp(prefix=".3mf-", suffix=".tmp", dir=exports_dir)
    try:
        with os.fdopen(fd, "wb") as output:
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
                for part_name, data in parts.items():
                    archive.writestr(part_name, data)
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    print("Exported:", path)
    return path
