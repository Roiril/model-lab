"""刷る .gcode.3mf を作る（Bambu Studio の CLI）。

    py -3.11 models/phone-slab-walker/plate.py [PLA|PETG]

出力: prints/phone-slab-walker/{1-trial,2-body,3-legs,4-divider}.gcode.3mf、build/plate_report.json
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.stdout.reconfigure(encoding="utf-8")

from bambu_profiles import resolve, write_flat  # noqa: E402

EXE = r"C:\Program Files\Bambu Studio\bambu-studio.exe"
MACHINE = "Bambu Lab X1 Carbon 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL X1C"
FILAMENT = {"PLA": "Bambu PLA Basic @BBL X1C", "PETG": "Bambu PETG Basic @BBL X1C"}
OVERRIDES = {"curr_bed_type": "Textured PEI Plate", "seam_position": "back", "wall_loops": "3",
             "exclude_object": "1", "enable_support": "0"}
BUILD = os.path.join(HERE, "build")
WORK = os.path.join(BUILD, "print")
OUT = os.path.join(ROOT, "prints", "phone-slab-walker")
TRIAL = os.path.join(OUT, "trial")
PLATES = {
    "1-trial": [os.path.join(TRIAL, n) for n in ("servo_pocket.stl", "horn_seat.stl", "phone_slot.stl")],
    "2-body": [os.path.join(BUILD, n) for n in ("print_tray.stl", "print_frame.stl")],
    "3-legs": [os.path.join(BUILD, n) for n in ("print_leg_right.stl", "print_leg_left.stl", "print_cap.stl")],
    "4-divider": [os.path.join(BUILD, "print_divider.stl")],
}


def settings(material):
    os.makedirs(WORK, exist_ok=True)
    process = resolve("process", PROCESS)
    process.update(OVERRIDES)
    return (write_flat(os.path.join(WORK, "machine.json"), resolve("machine", MACHINE)),
            write_flat(os.path.join(WORK, "process.json"), process),
            write_flat(os.path.join(WORK, f"filament_{material}.json"), resolve("filament", FILAMENT[material])))


def slice_plate(name, inputs, material):
    machine, process, filament = settings(material)
    out_name = f"{name}.gcode.3mf"
    cmd = [EXE, "--slice", "0", "--debug", "2", "--outputdir", OUT, "--export-3mf", out_name, "--arrange", "1",
           "--load-settings", f"{machine};{process}", "--load-filaments", filament] + inputs
    run = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    path = os.path.join(OUT, out_name)
    if run.returncode != 0 or not os.path.exists(path):
        raise RuntimeError(f"{name}: {run.returncode} {(run.stdout or '')[-800:]} {(run.stderr or '')[-400:]}")
    with zipfile.ZipFile(path) as z:
        info = z.read("Metadata/slice_info.config").decode("utf-8", "replace")
        plates = sum(1 for n in z.namelist() if re.fullmatch(r"Metadata/plate_\d+\.gcode", n))
    seconds = sum(int(v) for v in re.findall(r'key="prediction" value="(\d+)"', info))
    grams = sum(float(v) for v in re.findall(r'key="weight" value="([\d.]+)"', info))
    return dict(plate=name, file=os.path.relpath(path, ROOT).replace("\\", "/"), buildPlates=plates,
                minutes=round(seconds / 60, 1), grams=round(grams, 1))


def main():
    material = sys.argv[1] if len(sys.argv) > 1 else "PLA"
    # 部品ごとの STL も並べて置く（プレートを組み直したいとき用）
    for inputs in PLATES.values():
        for source in inputs:
            if os.path.dirname(source) == BUILD:
                shutil.copyfile(source, os.path.join(OUT, os.path.basename(source)))
    rows = [slice_plate(name, inputs, material) for name, inputs in PLATES.items()]
    for row in rows:
        print(row)
    with open(os.path.join(BUILD, "plate_report.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(material=material, plates=rows), fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
