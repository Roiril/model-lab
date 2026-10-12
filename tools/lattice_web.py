"""格子・カム系モデルの組立STLと運動表を、表示用JSONへまとめる。

models/<name>/build/ の必須ファイルが揃っていれば、どのモデルでも書き出せる。
モデルごとの見せ方（名前・物理画面の系列・再生の仕方・組み立ての文言）は
build/ui.json（任意）に書き、出力 JSON の `ui` 節へ入れる。
C3 / C4-1 / C4-2 は ui 節を足さない（既存の表示データとバイト一致を保つ）。
形の定義は viewer/lattice/CONTRACT.md。
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]

# build/ に無ければ書き出さないファイル。部品ごとの組立STL（manifest の assembly）も要る。
REQUIRED_BUILD_FILES = (
    "manifest.json", "motion.json", "boolean_evidence.json", "sim_tables.json",
    "simulate_report.json", "assembly.json", "drive_report.json",
)
MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
PLAYBACKS = ("group-lift", "motion-frames")
DOWNLOAD_BASES = ("exports", "prints")
MAX_SERIES = 5

# 書き出した JSON に ui 節を持たない 3 モデル。表示データ（HEAD とバイト一致を保つ）は変えず、
# 見せ方は viewer/lattice/ui-config.mjs の LEGACY_UI がモデル名から引く。
LEGACY_MODELS = ("mystery-box-sg92r-c3", "mystery-box-sg92r-c4", "mystery-box-sg92r-c4-2")


def read_mesh(path):
    raw = path.read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + 50 * count:
        raise ValueError(f"STL size mismatch: {path}")
    vertices, triangles, indices = [], [], {}
    for i in range(count):
        xyz = struct.unpack_from("<9f", raw, 96 + i * 50)
        face = []
        for j in range(3):
            p = tuple(round(v, 5) for v in xyz[j * 3:j * 3 + 3])
            if p not in indices:
                indices[p] = len(vertices) // 3
                vertices.extend(p)
            face.append(indices[p])
        triangles.extend(face)
    return {"vertices": vertices, "triangles": triangles}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def missing_inputs(folder):
    """書き出しに要るファイルのうち、無いものの一覧（folder は models/<name>）。"""
    build = folder / "build"
    missing = [f"build/{name}" for name in REQUIRED_BUILD_FILES if not (build / name).is_file()]
    manifest = build / "manifest.json"
    if manifest.is_file():
        for part in load_json(manifest).get("parts", []):
            if part.get("fit_only"):
                continue
            if not part.get("assembly") or not (folder / part["assembly"]).is_file():
                missing.append(str(part.get("assembly") or f"parts[{part.get('id')}].assembly"))
    return missing


def resolve_ui(model, folder):
    """出力に入れる ui 節。旧 3 モデルは None（節を足さない）。"""
    if model in LEGACY_MODELS:
        return None
    path = folder / "build/ui.json"
    return load_json(path) if path.is_file() else {}


def _is_matrix(value):
    return isinstance(value, list) and len(value) == 16 and all(isinstance(n, (int, float)) for n in value)


def validate_inputs(data):
    """ビューアが読む必須キーの検査。問題を日本語の文で返す（空なら適合）。"""
    problems = []
    parts = data["parts"]
    if not parts:
        problems.append("manifest.parts に印刷以外を含む表示部品がありません")
    for part in parts:
        if not part.get("id"):
            problems.append("manifest.parts に id の無い部品があります")
    frames = data["motion"].get("frames")
    if not isinstance(frames, list) or not frames:
        problems.append("motion.frames が空です")
    else:
        for index, frame in enumerate(frames):
            if not isinstance(frame.get("servo_deg"), (int, float)):
                problems.append(f"motion.frames[{index}].servo_deg が数値ではありません")
                break
            bad = [key for key, matrix in frame.get("transforms", {}).items() if not _is_matrix(matrix)]
            if bad or not isinstance(frame.get("transforms"), dict):
                problems.append(f"motion.frames[{index}].transforms の {bad or '全体'} が16要素の行列ではありません")
                break
    tables = data["simTables"]
    for key in ("limitsDeg", "duration_s", "groups", "rows", "const"):
        if key not in tables:
            problems.append(f"sim_tables.{key} がありません")
    if all(key in tables for key in ("groups", "rows", "const", "limitsDeg")):
        groups, rows = tables["groups"], tables["rows"]
        if not groups or any(not {"id", "label", "massKg"} <= set(group) for group in groups):
            problems.append("sim_tables.groups は {id, label, massKg} の空でない配列にしてください")
        if len(rows) < 2:
            problems.append("sim_tables.rows は2行以上要ります")
        else:
            step = rows[1]["servoDeg"] - rows[0]["servoDeg"]
            if step <= 0 or any(abs((b["servoDeg"] - a["servoDeg"]) - step) > 1e-6 for a, b in zip(rows, rows[1:])):
                problems.append("sim_tables.rows の servoDeg は一定の刻みで増える必要があります")
            if abs(rows[0]["servoDeg"] - tables["limitsDeg"][0]) > 1e-6:
                problems.append("sim_tables.rows[0].servoDeg が limitsDeg[0] と一致しません")
        scalar = ("servoDeg", "inertiaRestKgm2", "inertiaGroupsKgm2", "dMGroupsDqKgm2PerRad", "gravityRestNm", "gravityGroupsNm")
        arrays = ("liftsMm", "dLiftDqMPerRad", "d2LiftDq2MPerRad2")
        for index, row in enumerate(rows):
            absent = [key for key in scalar + arrays if key not in row]
            if absent:
                problems.append(f"sim_tables.rows[{index}] に {absent} がありません")
                break
            wrong = [key for key in arrays if len(row[key]) != len(groups)]
            if wrong:
                problems.append(f"sim_tables.rows[{index}] の {wrong} の長さが群の数（{len(groups)}）と違います")
                break
        constants = ("stallTorqueNm", "dtS", "recordS", "settleS", "motorInertiaKgm2", "controlBandRad",
                     "noLoadSpeedRadS", "servoFrictionNm", "gravityMS2", "contactToleranceN")
        absent = [key for key in constants if key not in tables["const"]]
        if absent:
            problems.append(f"sim_tables.const に {absent} がありません")
    sim = data["sim"]
    if "calculationPass" not in (sim.get("overall") or {}):
        problems.append("simulate_report.overall.calculationPass がありません")
    if "geometryPass" not in (sim.get("driveGeometry") or {}):
        problems.append("simulate_report.driveGeometry.geometryPass がありません")
    drive = data["drive"]
    if "geometryPass" not in (drive.get("overall") or {}):
        problems.append("drive_report.overall.geometryPass がありません")
    if not isinstance(drive.get("interfaces"), list):
        problems.append("drive_report.interfaces が配列ではありません")
    steps = data["assembly"].get("steps")
    if not isinstance(steps, list) or not steps:
        problems.append("assembly.steps が空です")
    else:
        for index, step in enumerate(steps):
            absent = [key for key in ("title", "instruction", "checkText", "moving", "frames", "report") if key not in step]
            if not absent and not (step["frames"] and all("progress" in f and isinstance(f.get("transforms"), dict) for f in step["frames"])):
                absent = ["frames[].progress / transforms"]
            if not absent and "samples" not in step["report"]:
                absent = ["report.samples"]
            if absent:
                problems.append(f"assembly.steps[{index}] に {absent} がありません")
                break
    return problems


def validate_ui(ui, data):
    """ui 節の検査。viewer/lattice/ui-config.mjs の normalizeUi と同じ規則。"""
    problems = []
    physics, assembly, printing = ui.get("physics", {}), ui.get("assembly", {}), ui.get("print", {})
    for name, value in (("physics", physics), ("assembly", assembly), ("print", printing)):
        if not isinstance(value, dict):
            problems.append(f"ui.{name} はオブジェクトにしてください")
    if problems:
        return problems
    if physics.get("playback", "group-lift") not in PLAYBACKS:
        problems.append(f"ui.physics.playback は {' / '.join(PLAYBACKS)} のどれかにしてください")
    if printing.get("downloadBase", "prints") not in DOWNLOAD_BASES:
        problems.append(f"ui.print.downloadBase は {' / '.join(DOWNLOAD_BASES)} のどれかにしてください")
    group_ids = [group["id"] for group in data["simTables"].get("groups", [])]
    series = physics.get("chartSeries")
    if series is None:
        if len(group_ids) > MAX_SERIES:
            problems.append(f"sim_tables.groups が{len(group_ids)}個あり折れ線は{MAX_SERIES}本までです。ui.physics.chartSeries で表示する群の id を選んでください")
    elif not isinstance(series, list) or not 1 <= len(series) <= MAX_SERIES or len(set(series)) != len(series):
        problems.append(f"ui.physics.chartSeries は重複のない群 id を1〜{MAX_SERIES}個並べた配列にしてください")
    else:
        for group_id in series:
            if group_id not in group_ids:
                problems.append(f"ui.physics.chartSeries の {group_id} が sim_tables.groups にありません")
    part_ids = {part["id"] for part in data["parts"]}
    for index, group in enumerate(ui.get("legendGroups", [])):
        where = f"ui.legendGroups[{index}]"
        if not isinstance(group, dict) or not group.get("label"):
            problems.append(f"{where} には label が要ります")
            continue
        if "color" in group and not HEX_COLOR.match(str(group["color"])):
            problems.append(f"{where}.color は #rrggbb にしてください")
        if isinstance(group.get("parts"), list):
            problems.extend(f"{where} の部品 {pid} が表示部品にありません" for pid in group["parts"] if pid not in part_ids)
        elif isinstance(group.get("prefix"), str) and group["prefix"]:
            if not any(pid.startswith(group["prefix"]) for pid in part_ids):
                problems.append(f"{where} の prefix {group['prefix']} に合う部品がありません")
        else:
            problems.append(f"{where} には parts（id の配列）か prefix（文字列）が要ります")
    for pid, color in (ui.get("colors") or {}).items():
        if pid not in part_ids:
            problems.append(f"ui.colors の部品 {pid} が表示部品にありません")
        if not HEX_COLOR.match(str(color)):
            problems.append(f"ui.colors.{pid} は #rrggbb にしてください")
    return problems


def export(model, root=ROOT, assets=None):
    folder = root / "models" / model
    if not (folder / "build").is_dir():
        raise FileNotFoundError(f"{folder / 'build'} がありません")
    missing = missing_inputs(folder)
    if missing:
        raise FileNotFoundError("書き出しに要るファイルがありません: " + ", ".join(missing))
    manifest = load_json(folder / "build/manifest.json")
    motion = load_json(folder / "build/motion.json")
    data = {"model": model, "meta": manifest.get("meta", {}), "parts": [], "motion": motion}
    for part in manifest["parts"]:
        if part.get("fit_only"):
            continue
        entry = {k: v for k, v in part.items() if k not in ("assembly", "print")}
        entry["mesh"] = read_mesh(folder / part["assembly"])
        entry["printable"] = bool(part.get("print"))
        data["parts"].append(entry)
    for key in ("verify", "delivery", "print_path_review"):
        report = folder / "build" / ("print_path_review.json" if key == "print_path_review" else f"{key}_report.json")
        data[key] = load_json(report) if report.exists() else None
    evidence = folder / "build/print_path_evidence.json"
    data["print_path_evidence"] = load_json(evidence) if evidence.exists() else None
    data["boolean_evidence"] = load_json(folder / "build/boolean_evidence.json")
    hole_path = folder / "build/hole_clearance.json"
    data["hole_clearance"] = load_json(hole_path) if hole_path.exists() else None
    closed_loop_path = folder / "build/closed_loop_support_evidence.json"
    data["closed_loop_support_evidence"] = load_json(closed_loop_path) if closed_loop_path.exists() else None
    support_geometry_path = folder / "build/print_support_geometry.json"
    data["print_support_geometry"] = load_json(support_geometry_path) if support_geometry_path.exists() else None
    # この 2 つは後から足された報告。無いモデルではキー自体を出さない（layout_only のときだけ下で null にする）。
    for key in ("continuous_path_support_evidence", "first_layer_contact_evidence"):
        report = folder / "build" / f"{key}.json"
        if report.exists():
            data[key] = load_json(report)
    if (data.get("delivery") or {}).get("status") == "layout_only":
        for key in ("print_path_review", "print_path_evidence", "closed_loop_support_evidence",
                    "continuous_path_support_evidence", "first_layer_contact_evidence"):
            data[key] = None
    for key, filename in (("simTables", "sim_tables.json"), ("sim", "simulate_report.json"),
                          ("assembly", "assembly.json"), ("drive", "drive_report.json")):
        data[key] = load_json(folder / "build" / filename)
    problems = validate_inputs(data)
    ui = resolve_ui(model, folder)
    if ui is not None:
        problems += validate_ui(ui, data)
    if problems:
        raise ValueError("表示データの形に問題があります（viewer/lattice/CONTRACT.md を参照）:\n- " + "\n- ".join(problems))
    if ui is not None:
        data["ui"] = ui
    data["meta"]["assembly_steps"] = [step["instruction"] for step in data["assembly"]["steps"]]
    assets = assets or root / "viewer/lattice/assets"
    write_json(assets / f"{model}.json", data)
    entries = rebuild_index(assets)
    return {"path": str(assets / f"{model}.json"), "parts": len(data["parts"]),
            "bytes": (assets / f"{model}.json").stat().st_size, "models": len(entries)}


def write_json(target, value):
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8", newline="\n")
    os.replace(temp, target)


def rebuild_index(assets):
    """assets/index.json（旧 3 モデル以外のモデル切り替えの一覧）を、assets/*.json の ui から作り直す。"""
    entries = []
    for path in assets.glob("*.json"):
        if path.name == "index.json":
            continue
        asset = load_json(path)
        if not isinstance(asset, dict) or "model" not in asset or "ui" not in asset:
            continue
        ui = asset["ui"]
        label = ui.get("label") or asset["model"]
        entries.append({"id": asset["model"], "navLabel": ui.get("navLabel") or label,
                        "navOrder": ui.get("navOrder", 100)})
    entries.sort(key=lambda entry: (entry["navOrder"], entry["id"]))
    # 旧 3 モデルは ui 節が無く一覧に載らない（ページ側が持つ）。一覧が空なら作らない。
    if entries or (assets / "index.json").exists():
        write_json(assets / "index.json", entries)
    return entries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("model", help="models/<model>/build/ の名前")
    model = parser.parse_args(argv).model
    if not MODEL_ID.match(model) or ".." in model:
        parser.error(f"モデル名が不正です: {model}")
    try:
        print(json.dumps(export(model), ensure_ascii=False))
    except (FileNotFoundError, ValueError) as error:
        print(f"書き出せません: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
