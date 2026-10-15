"""Summarize unchanged slice-meter measurements for the v2-A shared-part scope."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mechgate_lib import limits as L


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def category(part):
    if part.startswith("trial/"):
        shared = part in {"trial/frame_corner", "trial/mount_panel", "trial/mount_key"}
        return "trial_shared" if shared else "trial_face"
    return "shared" if part.startswith("frame/") or part.split("/")[-1] in {
        "panel", "key_l", "key_r"} else "face"


def rows(document):
    return [{**row, "plate": plate["plate"], "category": category(row["part"]),
             "pass": row["external_unsupported_mm"] <= L.SLICE_MAX_EXTERNAL_UNSUPPORTED_MM}
            for plate in document["plates"] for row in plate["parts"]]


def counts(parts):
    return {group: {"total": sum(r["category"] == group for r in parts),
                    "failing": sum(r["category"] == group and not r["pass"] for r in parts)}
            for group in ("shared", "face", "trial_shared", "trial_face")}


def generate():
    before = rows(read(HERE / "build/v1-plate-diagnostics.json"))
    after = rows(read(HERE / "build/plate-diagnostics.json"))
    summary = read(HERE / "build/plate-summary.json")
    supported = [p["plate"] for p in summary["plates"] if p["support_used"] not in ("false", "0")]
    document = {"baseline_commit": "4ceb596", "interface": read(HERE / "interface.json")["id"],
                "limit_mm": L.SLICE_MAX_EXTERNAL_UNSUPPORTED_MM,
                "before": counts(before), "after": counts(after), "parts": after,
                "plates_using_support": supported,
                "shared_pass": not supported and all(r["pass"] for r in after
                                                        if r["category"] in ("shared", "trial_shared"))}
    destination = HERE / "build/v2-print-comparison.json"
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    read(temporary)
    os.replace(temporary, destination)
    return document


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    result = generate()
    print(json.dumps({k: result[k] for k in ("interface", "before", "after", "shared_pass")}, ensure_ascii=False))
    raise SystemExit(0 if result["shared_pass"] else 1)
