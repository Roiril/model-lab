"""入力が変われば再合成し、各可動面のケースと代表ケースをゲートへ渡す。"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

from compose import C, HERE, MODEL, ROOT, dependency_status, read


def run(arguments):
    print("$ " + subprocess.list2cmdline([str(a) for a in arguments]), flush=True)
    return subprocess.run([str(a) for a in arguments], cwd=ROOT, check=False).returncode


def outputs_exist():
    cases = HERE / "build" / "cases.json"
    if not cases.exists():
        return False
    for model in [MODEL] + read(cases).get("models", []):
        directory = ROOT / "models" / model
        for name in ("manifest.json", "motion.json", "assembly.json"):
            if not (directory / "build" / name).is_file():
                return False
        manifest = read(directory / "build" / "manifest.json")
        for part in manifest["parts"]:
            for key in ("assembly", "print"):
                if key in part and not (directory / part[key]).is_file():
                    return False
    retention_index = HERE / "build" / "retention_cases.json"
    if not retention_index.is_file() or not read(retention_index).get("cases"):
        return False
    for case in read(retention_index)["cases"]:
        job_path = HERE / case["job"]
        if not job_path.is_file():
            return False
        job = read(job_path)
        if not job.get("parts") or any(not Path(path).is_file() for path in job["parts"].values()):
            return False
    return True


def retention_result_passed(result, expected_ids):
    rows = result.get("retention", [])
    ids = [row.get("id") for row in rows]
    return (result.get("ok") is True and result.get("calibration", {}).get("pass") is True
            and bool(expected_ids) and len(set(expected_ids)) == len(expected_ids)
            and len(ids) == len(expected_ids) and set(ids) == set(expected_ids)
            and all(row.get("pass") is True for row in rows))


def retention_path(relative):
    path = (HERE / relative).resolve()
    if not path.is_relative_to((HERE / "build" / "retention_cases").resolve()):
        raise ValueError(f"retention artifact outside its build directory: {relative}")
    return path


def run_retention_cases(no_blender=False):
    index = read(HERE / "build" / "retention_cases.json")
    rows = []
    blender = os.environ.get("BLENDER_EXE", "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")
    for case in index["cases"]:
        job_path = retention_path(case["job"])
        report_path = retention_path(case["report"])
        if no_blender:
            rows.append({"id": case["id"], "pass": False, "partial": True,
                         "reason": "--no-blender: retention auxiliary case not measured"})
            continue
        if report_path.exists():
            report_path.unlink()
        job = read(job_path)
        if Path(job["out"]).resolve() != report_path or len(job["parts"]) != case["parts_count"]:
            raise ValueError(f"{case['id']}: auxiliary job and index disagree")
        code = run([blender, "--background", "--factory-startup", "--python-exit-code", "1",
                    "--python", ROOT / "tools" / "mechgate_lib" / "bl_job.py", "--", job_path])
        result = read(report_path) if report_path.is_file() else {}
        passed = code == 0 and retention_result_passed(result, case["retention_ids"])
        rows.append({"id": case["id"], "pass": passed, "returncode": code,
                     "pose": case["pose"], "checked": len(result.get("retention", [])),
                     "expected": len(case["retention_ids"]), "calibration": result.get("calibration", {}).get("pass"),
                     "failing": [row for row in result.get("retention", []) if row.get("pass") is not True],
                     "error": result.get("error"), "report": case["report"]})
        print(f"retention auxiliary {case['id']}: {'pass' if passed else 'FAIL'} "
              f"{len(result.get('retention', []))}/{len(case['retention_ids'])} interfaces", flush=True)
    fresh, changed = dependency_status()
    passed = bool(rows) and not no_blender and fresh and all(row["pass"] for row in rows)
    summary = {"scope": "retention_only", "pass": passed, "partial": no_blender,
               "inputs_fresh": fresh, "changed_inputs": changed, "cases": rows,
               "not_checked": ["full_gate", "motion.interference", "assembly.path", "parts.self_intersection"]}
    C.write_json(HERE / "build" / "retention_report.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="入力ハッシュが同じでも再合成する")
    parser.add_argument("--no-blender", action="store_true", help="途中確認のみ。必ず非0で終了する")
    parser.add_argument("--retention-only", action="store_true", help="生成済みの中間・開端の抜け止め補助検査だけを流す")
    args = parser.parse_args()
    fresh, changed = dependency_status()
    rebuild = args.force or not fresh or not outputs_exist()
    if args.retention_only:
        if rebuild:
            print("INCOMPLETE: retention-only requires fresh, complete generated inputs; rebuild separately.")
            return 2
        summary = run_retention_cases(args.no_blender)
        return 0 if summary["pass"] else 1
    if rebuild:
        print("Rebuild required: " + ", ".join(changed or ["forced or missing output"]), flush=True)
        if args.no_blender:
            print("INCOMPLETE: inputs changed or output missing; --no-blender cannot rebuild.")
            return 2
        blender = os.environ.get("BLENDER_EXE", "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")
        code = run([blender, "--background", "--python-exit-code", "1", "--python", HERE / "model.py"])
        if code:
            return code
        if not dependency_status()[0] or not outputs_exist():
            print("INCOMPLETE: rebuild did not produce fresh, complete contracts.")
            return 2
    results = []
    if not args.no_blender:
        code = run([sys.executable, HERE / "plate.py", "--if-stale"])
        results.append({"check": "plate.py", "returncode": code})
    for script in ("verify_contract.py", "verify_envelopes.py"):
        code = run([sys.executable, HERE / script])
        results.append({"check": script, "returncode": code})
    cases = read(HERE / "build" / "cases.json")["models"]
    if not cases:
        print("INCOMPLETE: no active face cases.")
        return 2
    from lattice_export import prepare_assembly, export as export_lattice
    for model in cases + [MODEL]:
        if model == MODEL:
            # Case gate evidence supplies measured assembly metadata before root is hashed.
            prepare_assembly()
        command = [sys.executable, ROOT / "tools" / "mechgate.py", "check", model]
        if args.no_blender:
            command.append("--no-blender")
        code = run(command)
        results.append({"check": model, "returncode": code})
    retention = run_retention_cases(args.no_blender)
    results.append({"check": "retention_auxiliary", "returncode": 0 if retention["pass"] else 1})
    fresh, changed = dependency_status()
    passed = not args.no_blender and fresh and all(row["returncode"] == 0 for row in results)
    display = export_lattice()
    passed = passed and display["overall"]["calculationPass"]
    C.write_json(HERE / "build" / "certification.json", {"pass": passed, "partial": args.no_blender,
                 "inputs_fresh": fresh, "changed_inputs": changed, "results": results,
                 "retention_auxiliary": retention})
    if args.no_blender:
        print("INCOMPLETE: --no-blender never certifies a mechanism.")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
