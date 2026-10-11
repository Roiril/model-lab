"""既存のBoolean証拠計器をC4-2へ適用する薄いラッパー。"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    tool_path = ROOT / "tools" / "lattice_boolean_evidence.py"
    spec = importlib.util.spec_from_file_location("lattice_boolean_evidence_c42", tool_path)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    calibration = tool.calibration()
    if not all(row["pass"] for row in calibration):
        raise SystemExit("boolean evidence calibration failed before prototype STL inspection")
    tool.MODELS["c42"] = HERE
    output, summary = tool.model_report("c42")
    report = json.loads(output.read_text(encoding="utf-8"))
    report["wrapperSha256"] = {
        Path(__file__).relative_to(ROOT).as_posix(): hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
    temporary.replace(output)
    print(json.dumps({"model": "c42", "output": str(output), **summary}, ensure_ascii=False))
    if (not summary["calibrationPass"] or summary["missingFiles"]
            or summary["invalidClosedSolids"] or summary["properNonadjacentIntersections"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
