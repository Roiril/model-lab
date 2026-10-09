"""Bambu Studio の 3mf に層高範囲を加え、スライス結果を mm 単位で調べる。"""
import os
import re
import tempfile
import zipfile

from .gcode import floating_report, parse_gcode


def object_names(archive):
    """物体を id 順の ``(id, name)`` で返す。archive は開いた ZipFile。"""
    config = archive.read("Metadata/model_settings.config").decode("utf-8")
    objects = re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]+)"', config)
    return sorted(((int(object_id), name) for object_id, name in objects), key=lambda item: item[0])


def add_layer_ranges(src, dst, names, ranges):
    """物体名に対応する高さ範囲の層高を ``layer_config_ranges.xml`` として加える。

    ranges は ``{"部品名": [(min_z, max_z, layer_height), ...]}``。値は mm。
    """
    xml = ['<?xml version="1.0" encoding="utf-8"?>\n<objects>\n']
    for index, name in enumerate(names, start=1):
        key = next((part for part in ranges
                    if name.endswith(f"-{part}") or name.endswith(f"-{part}.stl")), None)
        if not key:
            continue
        xml.append(f' <object id="{index}">\n')
        for z0, z1, layer_height in ranges[key]:
            xml.append(f'  <range min_z="{z0}" max_z="{z1}">\n'
                       f'   <option opt_key="extruder">0</option>\n'
                       f'   <option opt_key="layer_height">{layer_height}</option>\n  </range>\n')
        xml.append(' </object>\n')
    xml.append('</objects>\n')
    with zipfile.ZipFile(src) as source, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            if (item.filename.endswith(".gcode") or item.filename.endswith(".gcode.md5")
                    or item.filename == "Metadata/layer_config_ranges.xml"):
                continue
            target.writestr(item, source.read(item.filename))
        target.writestr("Metadata/layer_config_ranges.xml", "".join(xml))


def inspect_sliced_3mf(path3mf):
    """スライス済み 3mf の材料量、時間、層高、支えのない押し出しを物体ごとに返す。"""
    with zipfile.ZipFile(path3mf) as archive:
        slice_info = archive.read("Metadata/slice_info.config").decode("utf-8")
        gcode_names = [name for name in archive.namelist() if name.endswith(".gcode")]
        if not gcode_names:
            raise ValueError(f"3mf has no sliced G-code: {path3mf}")
        gcode = archive.read(gcode_names[0])
    with tempfile.TemporaryDirectory(prefix="plate_") as temp_dir:
        temp_gcode = os.path.join(temp_dir, "plate.gcode")
        with open(temp_gcode, "wb") as fh:
            fh.write(gcode)
        layers, stats = parse_gcode(temp_gcode)
    labels = re.findall(r'<object identify_id="(\d+)" name="([^"]+)"', slice_info)
    label_name = {int(object_id): name for object_id, name in labels}
    per_object = {}
    for layer in layers:
        for segment in layer["segs"]:
            per_object.setdefault(segment[5], []).append(segment)
    support_match = re.search(r'key="support_used" value="(\w+)"', slice_info)
    prediction_match = re.search(r'key="prediction" value="(\d+)"', slice_info)
    weight_match = re.search(r'key="weight" value="([\d.]*)"', slice_info)
    if not (support_match and prediction_match and weight_match):
        raise ValueError(f"3mf has incomplete slice metadata: {path3mf}")
    out = dict(support_used=support_match.group(1), prediction_s=int(prediction_match.group(1)),
               weight_g=weight_match.group(1),
               filament=re.findall(r'<filament [^>]*used_m="([\d.]+)" used_g="([\d.]+)"', slice_info),
               stats=stats, objects={})
    for object_id, segments in per_object.items():
        name = label_name.get(object_id, str(object_id))
        z_values = sorted({round(segment[6], 3) for segment in segments})
        steps = {}
        for a, b in zip(z_values[:-1], z_values[1:]):
            steps.setdefault(round(b - a, 2), []).append(a)
        by_z = {}
        for segment in segments:
            by_z.setdefault(round(segment[6], 3), []).append(segment)
        object_layers = [dict(z=z, segs=by_z[z]) for z in sorted(by_z)]
        total, rows, _features = floating_report(object_layers)
        out["objects"][name] = dict(
            layers=len(z_values), z_top=z_values[-1] if z_values else None,
            layer_steps={str(step): [round(min(values), 2), round(max(values), 2), len(values)]
                         for step, values in sorted(steps.items())},
            floating=total,
            overhang_walls=[row for row in rows if row["feature"] != "Bridge"][:6],
        )
    return out
