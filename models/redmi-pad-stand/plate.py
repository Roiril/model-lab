"""X1C 用にスライスして、実際の押し出し経路を検査する。

使い方:  py -3.11 models/redmi-pad-stand/plate.py [<作業フォルダ>]
作業フォルダ（既定は Drive の renders）にプロファイル・ログ・slice_report.json を書き、
スライス済みの .gcode.3mf と配置の 3mf と STL を prints/redmi-pad-stand/ に置く。
"""
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
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
from bambu_profiles import resolve, write_flat
from printmech.gcode import floating_report
from printmech.three_mf import inspect_sliced_3mf
import params as P

NAME = P.MODEL_NAME
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("G:/マイドライブ/shubie/renders/2026-11-14_redmi-pad-stand")
PRINTS = ROOT / "prints" / NAME
EXE = Path("C:/Program Files/Bambu Studio/bambu-studio.exe")
PLACE = (128.0, 32.0)  # STL の X -75..75, Y 0..192 を X 53..203, Y 32..224 へ
# 重いほど倒れにくいので充填を多めにする（材料の量は問わない依頼）。外周 4 周で見える面を整える
OVERRIDES = {
    "curr_bed_type": "Textured PEI Plate", "wall_loops": "4",
    "sparse_infill_density": "30%", "sparse_infill_pattern": "gyroid",
    "top_shell_layers": "6", "bottom_shell_layers": "5",
    "seam_position": "back", "enable_support": "0",
    "brim_type": "outer_only", "brim_width": "5", "brim_object_gap": "0.1",
    # 細い部分の無い低い塊なので、加速度と内側の速さは標準のまま。見える外周だけ遅くする
    "outer_wall_speed": "80",
}


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    json.loads(tmp.read_text(encoding="utf-8"))
    tmp.replace(path)


def calibrate():
    """共有の計器が、支えのある斜面を通し、宙に浮いた外周を捕まえること。"""
    supported = [(0, 0, 10, 0, "Outer wall", 1, 0.2)]
    slope = [(0.2, 0, 10.2, 0, "Outer wall", 1, 0.4)]
    unsupported = [(0, 10, 10, 10, "Outer wall", 1, 0.4)]
    yes = floating_report([dict(z=0.2, segs=supported), dict(z=0.4, segs=slope)])[0]
    no = floating_report([dict(z=0.2, segs=supported), dict(z=0.4, segs=unsupported)])[0]
    assert yes["external_unsupported_mm"] == 0
    assert no["external_unsupported_mm"] > 9
    return dict(supported_slope=yes, unsupported_fixture=no)


def layout(stl):
    spec = importlib.util.spec_from_file_location("plate_3mf", ROOT / "tools" / "plate_3mf.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    verts, faces = module.read_stl(str(stl))
    path = PRINTS / f"{NAME}-layout.3mf"
    module.write_3mf(str(path), [(NAME, verts, faces, *PLACE)])
    return path


def check(path, sliced, material):
    """保存された設定・配置・経路を読み直して確かめる。"""
    import numpy as np
    if sliced["support_used"] != "false" or not sliced["objects"]:
        raise ValueError("toolpaths missing or support was generated")
    for name, obj in sliced["objects"].items():
        if obj["floating"]["external_unsupported_mm"] > 2.0:
            raise ValueError(f"unsupported outer paths in {name}: {obj['floating']}")
    top = max(obj["z_top"] or 0 for obj in sliced["objects"].values())
    with zipfile.ZipFile(path) as archive:
        config = json.loads(archive.read("Metadata/project_settings.config"))
        for key, expected in OVERRIDES.items():
            actual = config[key]
            values = actual if isinstance(actual, list) else [actual]
            assert all(str(v) == expected for v in values), (key, actual, expected)
        assert config["filament_type"] == [material], config["filament_type"]
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        main = ET.fromstring(archive.read("3D/3dmodel.model"))
        pts = []
        prod = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path"

        def matrix(value):
            a = np.array([float(v) for v in (value or "1 0 0 0 1 0 0 0 1 0 0 0").split()]).reshape(4, 3)
            m = np.eye(4)
            m[:3, :3], m[:3, 3] = a[:3].T, a[3]
            return m

        def collect(file, oid, tf):
            root = ET.fromstring(archive.read(file))
            obj = root.find(f"m:resources/m:object[@id='{oid}']", ns)
            for v in obj.findall("m:mesh/m:vertices/m:vertex", ns):
                pts.append((tf @ np.array([float(v.get(k)) for k in "xyz"] + [1]))[:3])
            for c in obj.findall("m:components/m:component", ns):
                collect(c.get(prod, "/" + file).lstrip("/"), c.get("objectid"), tf @ matrix(c.get("transform")))

        for item in main.findall("m:build/m:item", ns):
            collect("3D/3dmodel.model", item.get("objectid"), matrix(item.get("transform")))
        pts = np.array(pts)
        lo, hi = pts.min(axis=0), pts.max(axis=0)
        brim = float(config["brim_width"])
        assert lo[0] - brim >= 0 and lo[1] - brim >= 0 and hi[0] + brim <= 256 and hi[1] + brim <= 256, (lo, hi)
        assert not (lo[0] - brim < 18 and lo[1] - brim < 28), "brim enters the front-left exclusion zone"
        if top < hi[2] - 0.25:
            raise ValueError(f"upper layers missing: top {top} < {hi[2]}")
        sliced["placement"] = dict(bounds_mm=[lo.tolist(), hi.tolist()], brim_mm=brim,
                                   within_bed=True, exclusion_clear=True, z_top=top)
        (OUT / material / "plate.png").write_bytes(archive.read("Metadata/plate_1.png"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PRINTS.mkdir(parents=True, exist_ok=True)
    stl = PRINTS / f"{NAME}.stl"
    shutil.copyfile(ROOT / "exports" / NAME / "print.stl", stl)
    layout_path = layout(stl)
    report = dict(machine="Bambu Lab X1 Carbon 0.4 nozzle", process="0.20mm Standard @BBL X1C",
                  overrides=OVERRIDES, calibration=calibrate(), materials={})
    for material in ("PLA", "PETG"):
        work = OUT / material
        work.mkdir(exist_ok=True)
        machine = resolve("machine", "Bambu Lab X1 Carbon 0.4 nozzle")
        process = resolve("process", "0.20mm Standard @BBL X1C")
        process.update(OVERRIDES)
        filament = resolve("filament", f"Bambu {material} Basic @BBL X1C")
        m = write_flat(str(work / "machine.json"), machine)
        p = write_flat(str(work / "process.json"), process)
        f = write_flat(str(work / "filament.json"), filament)
        target = f"{NAME}-{material}.gcode.3mf"
        cmd = [str(EXE), "--slice", "0", "--debug", "2", "--arrange", "0",
               "--load-settings", f"{m};{p}", "--load-filaments", f,
               "--outputdir", str(work), "--export-3mf", target, str(layout_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (work / "slice.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"{material} slice failed ({result.returncode}): {(result.stdout + result.stderr)[-1500:]}")
        path = work / target
        sliced = inspect_sliced_3mf(path)
        check(path, sliced, material)
        shutil.copyfile(path, PRINTS / target)
        sliced["file"] = str(PRINTS / target)
        report["materials"][material] = sliced
        atomic_json(OUT / "slice_report.json", report)
        brief = dict(weight_g=sliced["weight_g"], hours=round(sliced["prediction_s"] / 3600, 2), floating={k: v["floating"] for k, v in sliced["objects"].items()})
        print(material, json.dumps(brief, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
