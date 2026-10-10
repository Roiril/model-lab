"""サポートなしで各部品を切り、支えのない押し出しを部品別に測る。"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(HERE, "build")
OUT = os.path.join(BUILD, "slices")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lib"))

import print_profile  # noqa: E402
from printmech.gcode import R_SUP, floating_report, parse_gcode  # noqa: E402
from printmech.stl import write_binary_stl as write_stl  # noqa: E402

EXE = r"C:\Program Files\Bambu Studio\bambu-studio.exe"
PARTS = ("box", "lid", "roof", "crank", "link", "pin", "clip", "speaker_clip")
MATERIALS = ("PLA", "PETG")


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


def source(part):
    return os.path.join(BUILD, f"print_{part}.stl")


def slice_one(stl, material, tag):
    os.makedirs(OUT, exist_ok=True)
    machine, process, filament = print_profile.settings(material, support=False)
    with tempfile.TemporaryDirectory(prefix="slc_") as work:
        command = [EXE, "--slice", "0", "--debug", "3", "--load-settings", f"{machine};{process}",
                   "--load-filaments", filament, "--outputdir", work, "--export-3mf", f"{tag}.3mf", stl]
        result = _hidden_run(command)
        log = (result.stdout or "") + (result.stderr or "")
        gcode = os.path.join(work, "plate_1.gcode")
        if result.returncode != 0 or not os.path.exists(gcode):
            return None, log
        destination = os.path.join(OUT, f"{tag}.gcode")
        os.replace(gcode, destination)
    return destination, log


def calibration():
    """Γ形の張り出しを検出し、45度斜面を検出しないことを確かめる。"""
    with tempfile.TemporaryDirectory(prefix="cal_") as temporary:
        overhang = os.path.join(temporary, "cal_overhang.stl")
        polygon = [(0, 0), (10, 0), (10, 10), (20, 10), (20, 12), (0, 12)]
        faces = [(0, 1, 2), (0, 2, 5), (2, 3, 4), (2, 4, 5)]
        front = [(x, 0.0, z) for x, z in polygon]
        back = [(x, 10.0, z) for x, z in polygon]
        triangles = [(front[c], front[b], front[a]) for a, b, c in faces]
        triangles += [(back[a], back[b], back[c]) for a, b, c in faces]
        for index in range(6):
            following = (index + 1) % 6
            triangles += [(front[index], front[following], back[following]),
                          (front[index], back[following], back[index])]
        write_stl(overhang, triangles)

        slope = os.path.join(temporary, "cal_slope.stl")
        vertices = [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0),
                    (20, 0, 20), (30, 0, 20), (30, 10, 20), (20, 10, 20)]
        indices = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
                   (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
        write_stl(slope, [(vertices[a], vertices[b], vertices[c]) for a, b, c in indices])
        report = {}
        for name, path in (("overhang_10mm", overhang), ("slope_45", slope)):
            gcode, log = slice_one(path, "PLA", f"cal_{name}")
            if gcode is None:
                report[name] = {"error": log[-800:]}
                continue
            layers, _ = parse_gcode(gcode)
            total, _, features = floating_report(layers)
            report[name] = {"total": total, "features": features}
    detected = report.get("overhang_10mm", {}).get("total", {}).get("external_unsupported_mm", 0)
    rejected = report.get("slope_45", {}).get("total", {}).get("external_unsupported_mm", 99)
    report["ok"] = detected > 20 and rejected < 1.0
    return report


def main():
    report = {
        "settings": {
            "machine": print_profile.MACHINE,
            "process": print_profile.PROCESS,
            "support": "off",
            "support_radius_mm": R_SUP,
        },
        "calibration": calibration(),
        "parts": {},
    }
    print("calibration", json.dumps(report["calibration"], ensure_ascii=False))
    for material in MATERIALS:
        for part in PARTS:
            stl = source(part)
            if not os.path.exists(stl):
                report["parts"][f"{material}/{part}"] = {"error": f"missing: {stl}"}
                print(material, part, "missing")
                continue
            gcode, log = slice_one(stl, material, f"{material}_{part}")
            warnings = [line.strip() for line in log.splitlines()
                        if re.search(r"float|cantilever|overhang|empty layer|error|support", line, re.I)
                        and not re.search(r"\[trace\]|\[debug\]", line)][:8]
            if gcode is None:
                report["parts"][f"{material}/{part}"] = {"error": log[-1200:]}
                print(material, part, "slice failed")
                continue
            layers, stats = parse_gcode(gcode)
            total, rows, features = floating_report(layers)
            report["parts"][f"{material}/{part}"] = {
                "layers": len(layers),
                "stats": stats,
                "floating": total,
                "floating_by_feature": features,
                "worst_layers": rows[:10],
                "log_warnings": warnings,
            }
            print(material, part, len(layers), total, features)
    lid_values = [report["parts"].get(f"{material}/lid", {}).get("floating", {}).get("external_unsupported_mm", 0)
                  for material in MATERIALS]
    report["support_recommendation"] = {
        "required": max(lid_values, default=0) >= 1.0,
        "basis": "lid external_unsupported_mm >= 1.0",
        "allowed_surface": "組立時に固定屋根で隠れる蓋内側のグースネック蝶番",
        "measured_mm": dict(zip(MATERIALS, lid_values)),
    }
    os.makedirs(BUILD, exist_ok=True)
    with open(os.path.join(BUILD, "slice_report.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
    return 0 if report["calibration"]["ok"] and all("error" not in value for value in report["parts"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
