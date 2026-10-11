"""C4-2の19個の六角穴を5停止状態の実STL断面で検査する。"""
from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_local(name):
    spec = importlib.util.spec_from_file_location(f"c42_hole_{name}", HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[name] = module
    return module


P = load_local("params")
load_local("motion")
import evidence as E  # noqa: E402

_spec = importlib.util.spec_from_file_location("c42_hole_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


def main():
    manifest = json.loads((E.BUILD / "manifest.json").read_text(encoding="utf-8"))
    names = tuple(part["id"] for part in manifest["parts"] if not part.get("fit_only"))
    meshes = {name: E.load(name) for name in names}
    report = verify.write_hole_clearance_report(meshes, names)
    print(json.dumps({"model": P.MODEL_ID, "pass": report["pass"],
                      "states": report["clearance"]["states"],
                      "cellsPerState": report["clearance"]["cellsPerState"],
                      "failures": len(report["clearance"]["failures"])}, ensure_ascii=False))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
