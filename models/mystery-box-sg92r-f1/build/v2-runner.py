"""V2-A execution record using the existing generators and unchanged gates."""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from compose import C, MODEL, dependency_status, read
from certify import outputs_exist, run_retention_cases
from lattice_export import prepare_assembly, export as export_lattice

LOGS = Path("G:/マイドライブ/shubie/reports")
results = []


def run(label, command):
    path = LOGS / f"mystery-box-sg92r-f1-v2-{label}.log"
    with path.open("w", encoding="utf-8") as stream:
        code = subprocess.run([str(a) for a in command], cwd=ROOT, stdout=stream,
                              stderr=subprocess.STDOUT, check=False).returncode
    row = {"check": label, "command": [str(a) for a in command], "returncode": code, "log": str(path)}
    results.append(row)
    C.write_json(HERE / "build/v2-execution.json", {"complete": False, "results": results})
    print(json.dumps(row, ensure_ascii=False), flush=True)
    return code


if not dependency_status()[0] or not outputs_exist():
    code = run("build", ["C:/Program Files/Blender Foundation/Blender 5.1/blender.exe", "--background",
                         "--python-exit-code", "1", "--python", HERE / "model.py"])
    if code:
        raise SystemExit(code)
run("plate", [sys.executable, HERE / "plate.py", "--if-stale"])
if run("contract", [sys.executable, HERE / "verify_contract.py"]):
    raise SystemExit(1)
for model in read(HERE / "build/cases.json")["models"] + [MODEL]:
    if model == MODEL:
        prepare_assembly()
    label = "gate-root" if model == MODEL else "gate-" + model.split("/")[-1]
    run(label, [sys.executable, ROOT / "tools/mechgate.py", "check", model])
    report = read(ROOT / "models" / model / "build/gate_report.json")
    unexpected = [row["id"] for row in report["checks"] if not row["pass"] and row["id"] != "print.slice"]
    if unexpected:
        print("MECHANICAL_FAILURES=" + json.dumps(unexpected), flush=True)
        raise SystemExit(1)
retention = run_retention_cases()
results.append({"check": "retention_auxiliary", "returncode": 0 if retention["pass"] else 1})
run("envelopes", [sys.executable, HERE / "verify_envelopes.py"])
fresh, changed = dependency_status()
display = export_lattice()
passed = fresh and all(row["returncode"] == 0 for row in results) and display["overall"]["calculationPass"]
C.write_json(HERE / "build/certification.json", {"pass": passed, "partial": False,
    "inputs_fresh": fresh, "changed_inputs": changed, "results": results, "retention_auxiliary": retention})
C.write_json(HERE / "build/v2-execution.json", {"complete": True, "inputs_fresh": fresh, "results": results})
raise SystemExit(0 if passed else 1)
