"""D 系ミステリーボックスを X1C 用の印刷可能な 3mf にする。"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(HERE, "build")
WORK = os.path.join(BUILD, "print")
EXPORTS = os.path.join(ROOT, "exports")
MODEL = os.path.basename(HERE)
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lib"))

import print_profile  # noqa: E402
from printmech.stl import read_binary_stl as read_stl, write_binary_stl as write_stl  # noqa: E402
from printmech.gcode import parse_gcode  # noqa: E402
from printmech.three_mf import add_layer_ranges, inspect_sliced_3mf, object_names  # noqa: E402

EXE = r"C:\Program Files\Bambu Studio\bambu-studio.exe"
PARTS = ("box", "lid", "roof", "crank", "link", "pin", "clip", "speaker_clip")


def _hidden_run(command):
    startupinfo = None
    creationflags = 0
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          startupinfo=startupinfo, creationflags=creationflags)


def _json(name):
    with open(os.path.join(BUILD, name), encoding="utf-8") as handle:
        return json.load(handle)


def layer_ranges():
    """形状生成側が指定した、見える浅い丸みだけの可変層高を読む。"""
    report = _json("model_report.json")
    raw = report.get("print_layer_ranges", {})
    result = {}
    for part, ranges in raw.items():
        if part not in PARTS:
            raise ValueError(f"unknown part in print_layer_ranges: {part}")
        result[part] = [tuple(float(value) for value in row) for row in ranges]
        if any(len(row) != 3 or row[0] < 0 or row[1] <= row[0] or row[2] <= 0 for row in result[part]):
            raise ValueError(f"invalid print_layer_ranges for {part}: {ranges}")
    return result


def support_required():
    report = _json("slice_report.json")
    if not report.get("calibration", {}).get("ok"):
        raise RuntimeError("slice_check calibration failed")
    if any("error" in result for result in report.get("parts", {}).values()):
        raise RuntimeError("slice_check contains failed parts")
    return bool(report.get("support_recommendation", {}).get("required"))


def slice_cli(inputs, out_dir, out_name, material=None, arrange=False, support=False):
    os.makedirs(out_dir, exist_ok=True)
    command = [EXE, "--slice", "0", "--debug", "2", "--outputdir", out_dir,
               "--export-3mf", out_name, "--arrange", "1" if arrange else "0"]
    if material:
        machine, process, filament = print_profile.settings(material, support=support)
        command += ["--load-settings", f"{machine};{process}", "--load-filaments", filament]
    command += inputs
    result = _hidden_run(command)
    path = os.path.join(out_dir, out_name)
    if result.returncode != 0 or not os.path.exists(path):
        log = (result.stdout or "")[-1800:] + (result.stderr or "")[-1200:]
        raise RuntimeError(f"slice failed ({result.returncode}): {log}")
    return path


def prepare(parts):
    os.makedirs(WORK, exist_ok=True)
    inputs = []
    for part in parts:
        source = os.path.join(BUILD, f"print_{part}.stl")
        if not os.path.isfile(source):
            raise FileNotFoundError(source)
        destination = os.path.join(WORK, f"{MODEL}-{part}.stl")
        write_stl(destination, read_stl(source))
        inputs.append(destination)
    return inputs


def select_support_object(source, destination, enabled_part="lid"):
    """自動サポートを蓋だけに限定する物体別設定を3mfへ加える。"""
    with zipfile.ZipFile(source) as archive:
        config = ET.fromstring(archive.read("Metadata/model_settings.config"))
        objects = config.findall("object")
        enabled = []
        for obj in objects:
            name_node = next((node for node in obj.findall("metadata") if node.get("key") == "name"), None)
            if name_node is None:
                raise ValueError(f"object {obj.get('id')} has no name")
            name = name_node.get("value", "")
            value = "1" if name.endswith(f"-{enabled_part}") else "0"
            setting = next((node for node in obj.findall("metadata")
                            if node.get("key") == "enable_support"), None)
            if setting is None:
                setting = ET.Element("metadata", {"key": "enable_support", "value": value})
                obj.insert(1, setting)
            else:
                setting.set("value", value)
            if value == "1":
                enabled.append(name)
        if len(enabled) != 1:
            raise ValueError(f"expected one {enabled_part} object, got {enabled}")
        encoded = ET.tostring(config, encoding="utf-8", xml_declaration=True)
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as target:
            for item in archive.infolist():
                if item.filename != "Metadata/model_settings.config":
                    target.writestr(item, archive.read(item.filename))
            target.writestr("Metadata/model_settings.config", encoded)
    return destination


def support_region(path3mf):
    """実G-codeのサポート押し出し範囲が蓋のXY範囲だけにあることを確認する。"""
    with zipfile.ZipFile(path3mf) as archive:
        gcode_name = next(name for name in archive.namelist() if name.endswith(".gcode"))
        gcode = archive.read(gcode_name)
        documents = {name: ET.fromstring(archive.read(name)) for name in archive.namelist()
                     if name.endswith(".model")}
        config = ET.fromstring(archive.read("Metadata/model_settings.config"))
    with tempfile.TemporaryDirectory(prefix="support_") as temporary:
        path = os.path.join(temporary, "plate.gcode")
        with open(path, "wb") as handle:
            handle.write(gcode)
        layers, _ = parse_gcode(path)
    segments = [segment for layer in layers for segment in layer["segs"]
                if "support" in segment[4].lower()]
    if not segments:
        return {"length_mm": 0.0, "bbox": None, "only_lid_xy": True}

    namespace = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
    names = {obj.get("id"): next((node.get("value") for node in obj.findall("metadata")
                                   if node.get("key") == "name"), "")
             for obj in config.findall("object")}
    def vertices(document, object_id):
        obj = next(node for node in documents[document].iter(namespace + "object")
                   if node.get("id") == object_id)
        mesh = obj.find(namespace + "mesh")
        if mesh is not None:
            return [(float(vertex.get("x")), float(vertex.get("y")), float(vertex.get("z")))
                    for vertex in mesh.find(namespace + "vertices")]
        points = []
        for component in obj.find(namespace + "components"):
            child = next((value.lstrip("/") for key, value in component.attrib.items()
                          if key.split("}")[-1] == "path"), document)
            matrix = tuple(map(float, component.get("transform").split())) if component.get("transform") else (
                1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
            points.extend((x * matrix[0] + y * matrix[3] + z * matrix[6] + matrix[9],
                           x * matrix[1] + y * matrix[4] + z * matrix[7] + matrix[10],
                           x * matrix[2] + y * matrix[5] + z * matrix[8] + matrix[11])
                          for x, y, z in vertices(child, component.get("objectid")))
        return points

    model = documents["3D/3dmodel.model"]
    lid_bounds = None
    for item in model.find(namespace + "build"):
        object_id = item.get("objectid")
        if not names.get(object_id, "").endswith("-lid"):
            continue
        matrix = tuple(map(float, item.get("transform").split())) if item.get("transform") else (
            1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
        points = [(x * matrix[0] + y * matrix[3] + z * matrix[6] + matrix[9],
                   x * matrix[1] + y * matrix[4] + z * matrix[7] + matrix[10])
                  for x, y, z in vertices("3D/3dmodel.model", object_id)]
        lid_bounds = (min(point[0] for point in points), min(point[1] for point in points),
                      max(point[0] for point in points), max(point[1] for point in points))
        break
    if lid_bounds is None:
        raise ValueError("sliced 3mf has no lid object")
    xs = [coordinate for segment in segments for coordinate in (segment[0], segment[2])]
    ys = [coordinate for segment in segments for coordinate in (segment[1], segment[3])]
    zs = [segment[6] for segment in segments]
    margin = 3.0
    only_lid = (min(xs) >= lid_bounds[0] - margin and min(ys) >= lid_bounds[1] - margin
                and max(xs) <= lid_bounds[2] + margin and max(ys) <= lid_bounds[3] + margin)
    length = sum(((segment[2] - segment[0]) ** 2 + (segment[3] - segment[1]) ** 2) ** 0.5
                 for segment in segments)
    return {"length_mm": round(length, 2),
            "bbox": {"x": [round(min(xs), 2), round(max(xs), 2)],
                     "y": [round(min(ys), 2), round(max(ys), 2)],
                     "z": [round(min(zs), 2), round(max(zs), 2)]},
            "lid_bbox_xy": [round(value, 2) for value in lid_bounds],
            "only_lid_xy": only_lid}


def build(material, parts, output_name, ranges, support=False):
    inputs = prepare(parts)
    layout_name = output_name + "-layout"
    command = [sys.executable, os.path.join(ROOT, "tools", "plate_3mf.py"), layout_name, *inputs]
    arranged = _hidden_run(command)
    if arranged.returncode:
        raise RuntimeError((arranged.stdout or "") + (arranged.stderr or ""))
    print(arranged.stdout, flush=True)
    layout = os.path.join(EXPORTS, layout_name + ".3mf")
    if tuple(parts) == PARTS:
        shutil.copyfile(layout, os.path.join(EXPORTS, MODEL + "-plate.3mf"))
    slice_input = layout
    if support:
        support_layout = os.path.join(WORK, output_name + "-lid-support.3mf")
        slice_input = select_support_object(layout, support_layout)
    first_dir = os.path.join(WORK, output_name + "_1")
    first = slice_cli([slice_input], first_dir, "first.3mf", material=material, support=support)
    with zipfile.ZipFile(first) as archive:
        names = [name for _, name in object_names(archive)]
    applicable = {part: value for part, value in ranges.items() if part in parts}
    final = first
    if applicable:
        final_dir = os.path.join(WORK, output_name + "_2")
        os.makedirs(final_dir, exist_ok=True)
        modified = os.path.join(final_dir, "with_ranges.3mf")
        add_layer_ranges(first, modified, names, applicable)
        final = slice_cli([modified], final_dir, "final.3mf", arrange=False)
    destination = os.path.join(EXPORTS, output_name + ".gcode.3mf")
    shutil.copyfile(final, destination)
    report = inspect_sliced_3mf(final)
    report["support_region"] = support_region(final)
    if support and not report["support_region"]["only_lid_xy"]:
        raise RuntimeError(f"support escaped lid region: {report['support_region']}")
    report["file"] = destination
    report["object_order"] = names
    report["support_requested"] = support
    return report


def main():
    ranges = layer_ranges()
    hidden_support = support_required()
    report = {
        "settings": {
            "machine": print_profile.MACHINE,
            "process": print_profile.PROCESS,
            "overrides": print_profile.OVERRIDES,
            "hidden_support_overrides": print_profile.HIDDEN_SUPPORT_OVERRIDES if hidden_support else {},
            "ranges": ranges,
            "accepted_short_unsupported": {
                "box_servo_shelf_mm": 6.1,
                "box_roof_leg_receiver_mm": 3.8,
                "roof_ear_hole_layer_step_mm": 0.9,
                "pin_head_layer_step_mm": 0.56,
                "limit_mm": 10.0,
            },
            "floating_meter_limit": (
                "floating_report does not include support extrusion in previous-layer coverage; "
                "support-enabled lid values are false positives. Use support_region from the actual G-code."
            ),
        }
    }
    for material in ("PLA", "PETG"):
        result = build(material, PARTS, f"{MODEL}-{material}", ranges, support=hidden_support)
        if hidden_support and str(result["support_used"]).lower() != "true":
            raise RuntimeError(f"{material}: support was required but slicer generated none")
        report[material] = result
        print(f"{material}: {result['prediction_s'] / 3600:.2f} h / {result['weight_g']} g / support={result['support_used']}")
    tests = (
        ("crank_test", ("crank",), f"{MODEL}-crank-test-PLA"),
        ("joints_test", ("joint_b_test",), f"{MODEL}-joints-test-PLA"),
        ("speaker_test", ("speaker_test",), f"{MODEL}-speaker-test-PLA"),
    )
    for key, parts, output_name in tests:
        result = build("PLA", parts, output_name, {}, support=False)
        report[key] = result
        print(f"{key}: {result['prediction_s'] / 60:.1f} min / support={result['support_used']}")
    with open(os.path.join(BUILD, "plate_report.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
    no_support = _json("slice_report.json")
    review = {
        "calibration": no_support["calibration"],
        "support_decision": no_support["support_recommendation"],
        "support_target": "lid only",
        "support_visible_surface": False,
        "support_surface_reason": (
            "The contact is on the lid hinge cylinder under the roof. The cylinder stays on the fixed hinge axis "
            "through 0..65 degrees and remains covered from the top, rear, left, and right."
        ),
        "accepted_short_unsupported": report["settings"]["accepted_short_unsupported"],
        "analyzer_limit": report["settings"]["floating_meter_limit"],
        "no_support": {key: value for key, value in no_support["parts"].items()
                       if key.split("/")[-1] in ("box", "lid", "roof", "pin")},
        "post_support": {material: {"support_used": report[material]["support_used"],
                                    "support_region": report[material]["support_region"],
                                    "objects": report[material]["objects"]}
                         for material in ("PLA", "PETG")},
    }
    with open(os.path.join(BUILD, "print_review.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(review, handle, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
