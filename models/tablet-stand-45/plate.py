"""Slice the reinforced stand with resolved X1C profiles and inspect actual paths."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.stdout.reconfigure(encoding="utf-8")
from bambu_profiles import resolve, write_flat
from printmech.gcode import floating_report
from printmech.three_mf import inspect_sliced_3mf

OUT = Path("G:/マイドライブ/shubie/renders/2026-10-30_redmi-stand")
PRINTS = ROOT / "prints" / "tablet-stand-45"
EXE = Path("C:/Program Files/Bambu Studio/bambu-studio.exe")
OVERRIDES = {
    "curr_bed_type": "Textured PEI Plate", "wall_loops": "4",
    "sparse_infill_density": "18%", "sparse_infill_pattern": "gyroid",
    "top_shell_layers": "5", "bottom_shell_layers": "5",
    "seam_position": "back", "exclude_object": "1", "enable_support": "0",
    "brim_type": "outer_only", "brim_width": "8", "brim_object_gap": "0.1",
    "outer_wall_speed": "40", "inner_wall_speed": "65",
    "sparse_infill_speed": "80", "internal_solid_infill_speed": "80",
    "top_surface_speed": "40", "initial_layer_speed": "20",
    "initial_layer_infill_speed": "35", "default_acceleration": "1000",
    "outer_wall_acceleration": "700", "inner_wall_acceleration": "1000",
    "travel_acceleration": "1500", "reduce_crossing_wall": "1",
}


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    json.loads(tmp.read_text(encoding="utf-8"))
    tmp.replace(path)


def calibrate():
    """Exercise the shared meter with a supported slope and a detached overhang."""
    supported = [(0, 0, 10, 0, "Outer wall", 1, 0.2)]
    slope = [(0.2, 0, 10.2, 0, "Outer wall", 1, 0.4)]
    unsupported = [(0, 10, 10, 10, "Outer wall", 1, 0.4)]
    yes = floating_report([dict(z=0.2, segs=supported), dict(z=0.4, segs=slope)])[0]
    no = floating_report([dict(z=0.2, segs=supported), dict(z=0.4, segs=unsupported)])[0]
    assert yes["external_unsupported_mm"] == 0
    assert no["external_unsupported_mm"] > 9
    return dict(supported_slope=yes, unsupported_fixture=no)


def layout(stl):
    spec = importlib.util.spec_from_file_location("stand_plate", ROOT / "tools" / "plate_3mf.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    verts, faces = module.read_stl(str(stl))
    # Plinth x=28..240, brim x=20..248; y=18..238, brim y=10..246.
    module.write_3mf(str(PRINTS / "tablet-stand-45-layout.3mf"),
                     [("tablet-stand-45", verts, faces, 134.0, 24.0)])


def validate_result(path, sliced, material):
    """Check actual saved settings and recursively transformed mesh bounds."""
    import numpy as np
    if sliced["support_used"] != "false" or not sliced["objects"]:
        raise ValueError("Missing toolpaths or unexpected support")
    for name, obj in sliced["objects"].items():
        # Older CLI G-code omits object labels; None still contains all part paths.
        if obj["floating"]["external_unsupported_mm"] > 2.0:
            raise ValueError(f"Unsupported external paths: {name}: {obj}")
    if max(obj["z_top"] or 0 for obj in sliced["objects"].values()) < 121.5:
        raise ValueError("The stand's upper layers are missing")
    ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
    prod = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path"

    def matrix(value):
        a = np.array([float(v) for v in (value or "1 0 0 0 1 0 0 0 1 0 0 0").split()]).reshape(4, 3)
        m = np.eye(4)
        m[:3, :3], m[:3, 3] = a[:3].T, a[3]
        return m

    with zipfile.ZipFile(path) as archive:
        config = json.loads(archive.read("Metadata/project_settings.config"))
        for key, expected in OVERRIDES.items():
            actual = config[key]
            values = actual if isinstance(actual, list) else [actual]
            assert all(str(value) == expected for value in values), (key, actual, expected)
        assert config["filament_type"] == [material]
        assert config["elefant_foot_compensation"] == "0.15"
        root_name = "3D/3dmodel.model"
        main = ET.fromstring(archive.read(root_name))

        def vertices(file, object_id, transform):
            root = ET.fromstring(archive.read(file))
            obj = root.find(f"m:resources/m:object[@id='{object_id}']", ns)
            if obj is None:
                raise ValueError(f"Missing 3mf object {file}/{object_id}")
            result = []
            for v in obj.findall("m:mesh/m:vertices/m:vertex", ns):
                result.append((transform @ np.array([float(v.get(k)) for k in ("x", "y", "z")] + [1]))[:3])
            for component in obj.findall("m:components/m:component", ns):
                result.extend(vertices(component.get(prod, file).lstrip("/"), component.get("objectid"),
                                       transform @ matrix(component.get("transform"))))
            return result

        points = []
        for item in main.findall("m:build/m:item", ns):
            points.extend(vertices(root_name, item.get("objectid"), matrix(item.get("transform"))))
        points = np.array(points)
        lo, hi = points.min(axis=0), points.max(axis=0)
        assert np.allclose(lo, [28, 18, 0], atol=0.002), lo
        assert np.allclose(hi, [240, 238, 121.65113], atol=0.002), hi
        brim = float(config["brim_width"])
        assert lo[0] - brim >= 18 and lo[1] - brim >= 0
        assert hi[0] + brim <= 256 and hi[1] + brim <= 256
        sliced["placement"] = dict(bounds_mm=[lo.tolist(), hi.tolist()], brim_mm=brim,
                                   within_bed=True, exclusion_clear=True)
        (OUT / material / "plate.png").write_bytes(archive.read("Metadata/plate_1.png"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PRINTS.mkdir(parents=True, exist_ok=True)
    stl = PRINTS / "tablet-stand-45.stl"
    shutil.copyfile(ROOT / "exports" / "tablet-stand-45" / "print.stl", stl)
    layout(stl)
    report = dict(machine="Bambu Lab X1 Carbon 0.4 nozzle", overrides=OVERRIDES,
                  calibration=calibrate(), materials={})
    for material in ("PLA", "PETG"):
        settings = OUT / material
        settings.mkdir(exist_ok=True)
        machine = resolve("machine", "Bambu Lab X1 Carbon 0.4 nozzle")
        process = resolve("process", "0.20mm Standard @BBL X1C")
        process.update(OVERRIDES)
        filament = resolve("filament", f"Bambu {material} Basic @BBL X1C")
        m = write_flat(str(settings / "machine.json"), machine)
        p = write_flat(str(settings / "process.json"), process)
        f = write_flat(str(settings / "filament.json"), filament)
        target = f"tablet-stand-45-{material}.gcode.3mf"
        cmd = [str(EXE), "--slice", "0", "--debug", "2", "--arrange", "0",
               "--load-settings", f"{m};{p}", "--load-filaments", f,
               "--outputdir", str(settings), "--export-3mf", target,
               str(PRINTS / "tablet-stand-45-layout.3mf")]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (settings / "slice.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"{material} slice failed ({result.returncode}): {(result.stdout + result.stderr)[-1500:]}")
        path = settings / target
        sliced = inspect_sliced_3mf(path)
        validate_result(path, sliced, material)
        delivered = PRINTS / target
        shutil.copyfile(path, delivered)
        sliced["file"] = str(delivered)
        report["materials"][material] = sliced
        atomic_json(OUT / "slice_report.json", report)
        print(material, json.dumps(sliced, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
