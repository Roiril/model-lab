"""C3/C4の組立STLと運動表を、表示用JSONへまとめる。"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]


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


def export(model):
    folder = ROOT / "models" / model
    manifest = json.loads((folder / "build/manifest.json").read_text(encoding="utf-8"))
    motion = json.loads((folder / "build/motion.json").read_text(encoding="utf-8"))
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
        data[key] = json.loads(report.read_text(encoding="utf-8")) if report.exists() else None
    evidence = folder / "build/print_path_evidence.json"
    data["print_path_evidence"] = json.loads(evidence.read_text(encoding="utf-8")) if evidence.exists() else None
    data["boolean_evidence"] = json.loads((folder / "build/boolean_evidence.json").read_text(encoding="utf-8"))
    hole_path = folder / "build/hole_clearance.json"
    data["hole_clearance"] = json.loads(hole_path.read_text(encoding="utf-8")) if hole_path.exists() else None
    closed_loop_path = folder / "build/closed_loop_support_evidence.json"
    data["closed_loop_support_evidence"] = json.loads(closed_loop_path.read_text(encoding="utf-8")) if closed_loop_path.exists() else None
    support_geometry_path = folder / "build/print_support_geometry.json"
    data["print_support_geometry"] = json.loads(support_geometry_path.read_text(encoding="utf-8")) if support_geometry_path.exists() else None
    for key, filename in (("simTables", "sim_tables.json"), ("sim", "simulate_report.json"),
                          ("assembly", "assembly.json"), ("drive", "drive_report.json")):
        report = folder / "build" / filename
        if not report.exists():
            raise FileNotFoundError(f"C1-style workflow requires {report}")
        data[key] = json.loads(report.read_text(encoding="utf-8"))
    data["meta"]["assembly_steps"] = [step["instruction"] for step in data["assembly"]["steps"]]
    target = ROOT / "viewer/lattice/assets" / f"{model}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8", newline="\n")
    os.replace(temp, target)
    print(json.dumps({"path": str(target), "parts": len(data["parts"]), "bytes": target.stat().st_size}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=("mystery-box-sg92r-c3", "mystery-box-sg92r-c4"))
    export(parser.parse_args().model)
