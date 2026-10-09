"""刷る 3mf を作る（Bambu Studio の CLI で切った、そのまま印刷に送れる .gcode.3mf）。

    py -3.11 models/mystery-box-sg92r-c2/plate.py

流れ:
  1. 刷る向きの STL（exports/mystery-box-sg92r-c2-*.stl）を build/print/ へ。箱は 180° 回して後ろ面を奥へ向ける
  2. 部品間6mmの配置を3mfへ書く。自動配置を明示的に止めて1度切る
  3. できた 3mf に「高さごとの層の厚み」を足して切り直す（箱の節の上面・蓋の筒の段を細かく）
  4. G-code を物体ごとに分けて確かめる: 層の厚みが変わったか、支えの無い押し出し、サポートの有無
出力: exports/mystery-box-sg92r-c2-<材料>.gcode.3mf と各試し刷りの .gcode.3mf、
      build/plate_report.json
"""
import json
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.stdout.reconfigure(encoding="utf-8")

import print_profile  # noqa: E402
from printmech.stl import (  # noqa: E402
    read_binary_stl as read_stl, rotate_z as rotated, write_binary_stl as write_stl,
)
from printmech.three_mf import (  # noqa: E402
    add_layer_ranges, inspect_sliced_3mf, object_names,
)
from slice_check import EXE  # noqa: E402

EXPORTS = os.path.join(ROOT, "exports")
WORK = os.path.join(HERE, "build", "print")
PARTS = ["box", "lid", "crank", "link", "pin", "clip", "speaker_clip", "roof"]
ROTATE_Z = {"box": 180.0}          # 箱の後ろ面（蝶番側）を奥へ。継ぎ目が後ろに寄る
# 高さごとの層の厚み（刷る姿勢の z、mm）。上向きの浅い丸みが外から見える所だけ細かくする
RANGES = {"box": [(64.0, 70.0, 0.08)], "lid": [(5.0, 10.4, 0.08)]}


def slice_cli(inputs, out_dir, out_name, material=None, arrange=True):
    os.makedirs(out_dir, exist_ok=True)
    cmd = [EXE, "--slice", "0", "--debug", "2", "--outputdir", out_dir, "--export-3mf", out_name]
    cmd += ["--arrange", "1" if arrange else "0"]
    if material:
        m, p, f = print_profile.settings(material)
        cmd += ["--load-settings", f"{m};{p}", "--load-filaments", f]
    cmd += inputs
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    path = os.path.join(out_dir, out_name)
    if r.returncode != 0 or not os.path.exists(path):
        raise RuntimeError(f"slice failed ({r.returncode}): {(r.stdout or '')[-1500:]}{(r.stderr or '')[-800:]}")
    return path


def add_ranges(src, dst, names):
    """Metadata/layer_config_ranges.xml（Bambu の高さ範囲の設定）を足した 3mf を作る。"""
    add_layer_ranges(src, dst, names, RANGES)


def check(path3mf, names):
    """切った結果を物体ごとに確かめる。"""
    return inspect_sliced_3mf(path3mf)


def build(material, parts, out_name, ranges=True):
    os.makedirs(WORK, exist_ok=True)
    inputs = []
    for p in parts:
        tris = read_stl(os.path.join(EXPORTS, f"mystery-box-sg92r-c2-{p}.stl"))
        if p in ROTATE_Z:
            tris = rotated(tris, ROTATE_Z[p])
        path = os.path.join(WORK, f"mystery-box-sg92r-c2-{p}.stl")
        write_stl(path, tris)
        inputs.append(path)
    d1 = os.path.join(WORK, f"{out_name}_1")
    # 6mm離した配置を先に作る。CLIの自動配置は外接箱を重ねて詰める場合がある。
    layout_name = f'{out_name}-layout'
    arrange = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'plate_3mf.py'), layout_name, *inputs],
                             capture_output=True, text=True, encoding='utf-8', errors='replace')
    if arrange.returncode:
        raise RuntimeError(arrange.stderr)
    print(arrange.stdout, flush=True)
    layout = os.path.join(EXPORTS, layout_name + '.3mf')
    if parts == PARTS:
        shutil.copyfile(layout, os.path.join(EXPORTS, 'mystery-box-sg92r-c2-plate.3mf'))
    first = slice_cli([layout], d1, "first.3mf", material=material, arrange=False)
    names = [n for _, n in object_names(zipfile.ZipFile(first))]
    final_dir = os.path.join(WORK, f"{out_name}_2")
    os.makedirs(final_dir, exist_ok=True)
    if ranges:
        mod = os.path.join(final_dir, "with_ranges.3mf")
        add_ranges(first, mod, names)
        final = slice_cli([mod], final_dir, "final.3mf", arrange=False)
    else:
        final = first
    dst = os.path.join(EXPORTS, f"{out_name}.gcode.3mf")
    shutil.copyfile(final, dst)
    res = check(final, names)
    res["file"] = dst
    res["object_order"] = names
    return res


def main():
    report = {"settings": dict(machine=print_profile.MACHINE, process=print_profile.PROCESS,
                               overrides=print_profile.OVERRIDES, ranges=RANGES)}
    for material in ("PLA", "PETG"):
        r = build(material, PARTS, f"mystery-box-sg92r-c2-{material}")
        report[material] = r
        print(f"\n== {material}: {r['file']}")
        print(f"   support_used={r['support_used']} 予測 {r['prediction_s'] / 3600:.2f} h  filament {r['filament']}")
        for name, o in r["objects"].items():
            print(f"   {name}: layers {o['layers']} top {o['z_top']} steps {o['layer_steps']}")
            print(f"      floating {o['floating']}  overhang walls {o['overhang_walls'][:3]}")
    r = build("PLA", ["crank"], "mystery-box-sg92r-c2-crank-test-PLA", ranges=False)
    report["crank_test"] = r
    print(f"\n== crank test: {r['file']} support_used={r['support_used']} 予測 {r['prediction_s'] / 60:.1f} min")
    r = build("PLA", ["speaker_test", "speaker_clip"], "mystery-box-sg92r-c2-speaker-test-PLA", ranges=False)
    report["speaker_test"] = r
    print(f"\n== speaker test: {r['file']} support_used={r['support_used']} 予測 {r['prediction_s'] / 60:.1f} min")
    r = build('PLA', ['link', 'pin', 'clip'], 'mystery-box-sg92r-c2-joints-test-PLA', ranges=False)
    report['joints_test'] = r
    for material in ('PLA', 'PETG'):
        r = build(material, ['roof_test_body', 'roof_test'],
                  f'mystery-box-sg92r-c2-roof-test-{material}', ranges=False)
        report[f'roof_test_{material}'] = r
        print(f"\n== roof test {material}: {r['file']} support_used={r['support_used']} "
              f"予測 {r['prediction_s'] / 60:.1f} min")
    with open(os.path.join(HERE, "build", "plate_report.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
