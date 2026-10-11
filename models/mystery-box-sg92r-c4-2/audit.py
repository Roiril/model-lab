"""納品直前に検査の合否と参照先SHAをまとめて照合する。"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
MODEL = "mystery-box-sg92r-c4-2"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    delivery = json.loads((BUILD / "delivery_report.json").read_text(encoding="utf-8"))
    layout_only = delivery.get("status") == "layout_only"
    files = ("verify_report.json", "drive_report.json", "assembly_report.json",
             "simulate_report.json", "boolean_evidence.json", "delivery_report.json",
             "print_path_review.json", "print_path_evidence.json",
             "closed_loop_support_evidence.json", "print_geometry_evidence.json",
             "continuous_path_support_evidence.json", "first_layer_contact_evidence.json",
             "print_support_geometry.json", "demo_compile_report.json",
             "motion.json", "assembly.json", "sim_tables.json", "manifest.json",
             "preview_evidence.json", "hole_clearance.json", "contact_envelope_evidence.json")
    slice_reports = {"print_path_review.json", "print_path_evidence.json",
                     "closed_loop_support_evidence.json", "print_geometry_evidence.json",
                     "continuous_path_support_evidence.json", "first_layer_contact_evidence.json"}
    reports = {name: json.loads((BUILD / name).read_text(encoding="utf-8"))
               for name in files if not (layout_only and name in slice_reports)}
    references = {}
    errors = []

    def check(relative, expected, context):
        path = Path(relative)
        if not path.is_absolute():
            path = ROOT / path
        path = path.resolve()
        try:
            key = path.relative_to(ROOT).as_posix()
        except ValueError:
            # Bambu公式設定ファイルはプログラムフォルダに存在する。
            key = str(path)
        if not path.is_file():
            errors.append({"context": context, "path": key, "reason": "missing"})
            return
        actual = digest(path)
        references[key] = actual
        if actual != expected:
            errors.append({"context": context, "path": key, "reason": "stale",
                           "expected": expected, "actual": actual})

    def visit(value, context):
        if isinstance(value, list):
            for i, row in enumerate(value):
                visit(row, f"{context}[{i}]")
        elif isinstance(value, dict):
            if isinstance(value.get("file"), str) and isinstance(value.get("sha256"), str):
                check(value["file"], value["sha256"], context)
            elif isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
                check(value["path"], value["sha256"], context)
            for key, row in value.items():
                if isinstance(row, str) and len(row) == 64 and "/" in key and not key.startswith("http"):
                    check(key, row, context)
                elif isinstance(row, (dict, list)):
                    visit(row, f"{context}.{key}")

    for name, report in reports.items():
        visit(report, name)
    preview = reports["preview_evidence.json"]
    for name, expected in preview["source_sha256"].items():
        check(str(HERE / name), expected, "preview source")
    for field in ("assembly_stl_sha256", "outputs"):
        for name, expected in preview[field].items():
            check(str(BUILD / name), expected, f"preview {field}")
    required_images = {"hero.png", "cutaway.png", "preview_flat.png", "preview_upper_left.png",
                       "preview_center.png", "preview_upper_right.png", "preview_lower_pair.png"}
    if not required_images <= set(preview["outputs"]):
        errors.append({"context": "preview", "reason": "missing views",
                       "files": sorted(required_images - set(preview["outputs"]))})
    for end in (reports["assembly_report.json"].get("sourceIntegrity", {}).get("end", {}),):
        for part, expected in end.items():
            check(f"models/{MODEL}/build/{part}.stl", expected, "assembly STL")
    basis = reports.get("print_path_review.json", {}).get("basis", {})
    for key, name in (("manifest_sha256", "manifest.json"), ("delivery_report_sha256", "delivery_report.json"),
                      ("print_geometry_evidence_sha256", "print_geometry_evidence.json"),
                      ("closed_loop_support_evidence_sha256", "closed_loop_support_evidence.json"),
                      ("continuous_path_support_evidence_sha256", "continuous_path_support_evidence.json"),
                      ("first_layer_contact_evidence_sha256", "first_layer_contact_evidence.json"),
                      ("print_support_geometry_sha256", "print_support_geometry.json"),
                      ("print_path_evidence_sha256", "print_path_evidence.json")):
        if not layout_only:
            check(f"models/{MODEL}/build/{name}", basis[key], "print review basis")
    asset_path = ROOT / f"viewer/lattice/assets/{MODEL}.json"
    asset = json.loads(asset_path.read_text(encoding="utf-8"))
    asset_pairs = (("verify", "verify_report.json"), ("drive", "drive_report.json"),
                   ("sim", "simulate_report.json"), ("delivery", "delivery_report.json"),
                   ("print_path_review", "print_path_review.json"),
                   ("print_path_evidence", "print_path_evidence.json"),
                   ("boolean_evidence", "boolean_evidence.json"),
                   ("hole_clearance", "hole_clearance.json"),
                   ("print_support_geometry", "print_support_geometry.json"),
                   ("closed_loop_support_evidence", "closed_loop_support_evidence.json"),
                   ("continuous_path_support_evidence", "continuous_path_support_evidence.json"),
                   ("first_layer_contact_evidence", "first_layer_contact_evidence.json"),
                   ("motion", "motion.json"), ("assembly", "assembly.json"),
                   ("simTables", "sim_tables.json"))
    for field, name in asset_pairs:
        if asset.get(field) != reports.get(name):
            errors.append({"context": "viewer asset", "field": field, "reason": "stale report"})
    sys.path.insert(0, str(ROOT / "tools"))
    from lattice_web import read_mesh
    expected_parts = []
    for part in reports["manifest.json"]["parts"]:
        if part.get("fit_only"):
            continue
        entry = {key: value for key, value in part.items() if key not in ("assembly", "print")}
        entry["mesh"] = read_mesh(HERE / part["assembly"])
        entry["printable"] = bool(part.get("print"))
        expected_parts.append(entry)
    if asset.get("parts") != expected_parts:
        errors.append({"context": "viewer asset", "field": "parts", "reason": "stale STL mesh"})
    old_geometry = {}
    for relative in (
        "models/mystery-box-sg92r-c4/model.py", "models/mystery-box-sg92r-c4/params.py",
        "models/mystery-box-sg92r-c4/verify.py", "models/mystery-box-sg92r-c4/motion.py",
        "models/mystery-box-sg92r-c4/assembly.py",
        "viewer/lattice/assets/mystery-box-sg92r-c4.json",
    ):
        previous = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=ROOT,
                                  check=True, capture_output=True).stdout
        previous_sha = hashlib.sha256(previous).hexdigest()
        actual_sha = digest(ROOT / relative)
        old_geometry[relative] = {"previousSha256": previous_sha, "actualSha256": actual_sha,
                                  "pass": previous_sha == actual_sha}
        if previous_sha != actual_sha:
            errors.append({"context": "C4-1 preservation", "path": relative, "reason": "geometry changed"})
    checks = {
        "geometry": reports["verify_report.json"].get("pass") is True,
        "contactEnvelope": reports["contact_envelope_evidence.json"].get("pass") is True
            and reports["motion.json"].get("contactEnvelope", {}).get("calibration", {}).get("pass") is True,
        "drive": reports["drive_report.json"].get("overall", {}).get("geometryPass") is True,
        "assembly": reports["assembly_report.json"].get("pass") is True,
        "simulation": reports["simulate_report.json"].get("overall", {}).get("calculationPass") is True,
        "printSupports": reports["print_support_geometry.json"].get("overall", {}).get("pass") is True,
        "demoCompile": reports["demo_compile_report.json"].get("pass") is True
            and reports["demo_compile_report.json"].get("results", {}).get("compileExitCode") == 0
            and reports["demo_compile_report.json"].get("target") == "arduino:avr:uno"
            and reports["demo_compile_report.json"].get("phaseTrim", {}).get("pass") is True,
        "booleanInputs": reports["boolean_evidence.json"].get("summary", {}).get("calibrationPass") is True
            and reports["boolean_evidence.json"].get("summary", {}).get("missingFiles") == 0
            and reports["boolean_evidence.json"].get("summary", {}).get("invalidClosedSolids") == 0
            and reports["boolean_evidence.json"].get("summary", {}).get("properNonadjacentIntersections") == 0,
        "references": not errors,
        "c4_1_preserved": all(row["pass"] for row in old_geometry.values()),
        "hex_holes": reports["hole_clearance.json"].get("pass") is True,
    }
    if layout_only:
        artifacts = delivery.get("artifacts", [])
        checks["editablePrintFiles"] = (len(delivery.get("plates", {})) == 4
            and len(artifacts) == 17
            and sum(row["file"].endswith(".stl") for row in artifacts) == 13
            and sum(row["file"].endswith(".3mf") for row in artifacts) == 4
            and all(not plate.get("materials") for plate in delivery["plates"].values())
            and all(not row["file"].endswith(".gcode.3mf") for row in artifacts))
    else:
        checks.update({
            "closedLoops": reports["closed_loop_support_evidence.json"].get("overall", {}).get("pass") is True,
            "continuousPaths": reports["continuous_path_support_evidence.json"].get("overall", {}).get("pass") is True,
            "firstLayer": reports["first_layer_contact_evidence.json"].get("overall", {}).get("pass") is True,
            "printPaths": reports["print_path_review.json"].get("status") == "accepted_with_fit_test",
        })
    result = {"model": MODEL, "pass": all(checks.values()), "checks": checks,
              "scope": "CAD_STL_and_editable_3MF" if layout_only else "sliced_print_paths",
              "slicing": "user_in_Bambu_Studio" if layout_only else "included",
              "referenceCount": len(references), "references": references, "errors": errors,
              "c4_1": old_geometry,
              "viewerAssetSha256": digest(asset_path)}
    target = BUILD / "delivery_audit.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
    os.replace(temporary, target)
    print(json.dumps({"pass": result["pass"], "checks": checks, "references": len(references), "errors": errors}))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
