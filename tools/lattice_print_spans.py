"""スライス済み3MFの実押出経路から連続する未支持区間を測る。

    py -3.11 tools/lattice_print_spans.py <gcode.3mf> --output <report.json>
    py -3.11 tools/lattice_print_spans.py --calibrate

この計器が測るのは、直下の押出経路から支持半径0.6mmを超えた経路区間である。
STLにある空隙そのものの寸法ではなく、全警告区間の累計も単一スパンではない。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

from printmech.gcode import (  # noqa: E402
    CELL,
    INTERNAL,
    R_SUP,
    coverage,
    floating_report,
    parse_gcode,
    supported,
)
from lattice_delivery import _bbox_object_assignment, inspect_layout  # noqa: E402


SAMPLE_MM = 0.1
JOIN_TOLERANCE_MM = 1e-6


def _distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _same_point(a, b):
    return _distance(a, b) <= JOIN_TOLERANCE_MM


def _category(feature):
    if any(name in feature for name in INTERNAL):
        return "internal"
    if "Bridge" in feature:
        return "bridge"
    return "external"


def _chains(segments):
    """同じ機能で端点が連続する実押出線をポリラインへまとめる。"""
    chains = []
    current = None
    for segment in segments:
        start = (float(segment[0]), float(segment[1]))
        end = (float(segment[2]), float(segment[3]))
        feature = segment[4]
        if (_distance(start, end) <= JOIN_TOLERANCE_MM):
            continue
        if current is not None and current["feature"] == feature and _same_point(current["points"][-1], start):
            current["points"].append(end)
        else:
            current = {"feature": feature, "points": [start, end]}
            chains.append(current)
    return chains


def _sample_chain(points, previous_cells):
    units = []
    distance = 0.0
    for start, end in zip(points[:-1], points[1:]):
        length = _distance(start, end)
        count = max(1, math.ceil(length / SAMPLE_MM))
        for index in range(count):
            a = index / count
            b = (index + 1) / count
            p0 = (start[0] + (end[0] - start[0]) * a,
                  start[1] + (end[1] - start[1]) * a)
            p1 = (start[0] + (end[0] - start[0]) * b,
                  start[1] + (end[1] - start[1]) * b)
            midpoint = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
            step = _distance(p0, p1)
            units.append({
                "p0": p0,
                "p1": p1,
                "midpoint": midpoint,
                "length": step,
                "startDistance": distance,
                "supported": supported(previous_cells, midpoint[0], midpoint[1], R_SUP, CELL),
            })
            distance += step
    return units


def _unsupported_runs(units, closed):
    runs = []
    start = None
    for index, unit in enumerate(units):
        if not unit["supported"] and start is None:
            start = index
        if unit["supported"] and start is not None:
            runs.append([start, index - 1])
            start = None
    if start is not None:
        runs.append([start, len(units) - 1])
    if closed and len(runs) > 1 and runs[0][0] == 0 and runs[-1][1] == len(units) - 1:
        runs = [[runs[-1][0], runs[0][1]]] + runs[1:-1]
    return runs


def _run_result(units, run, closed):
    start, end = run
    indexes = (list(range(start, len(units))) + list(range(0, end + 1))
               if closed and start > end else list(range(start, end + 1)))
    before = (start - 1) % len(units) if closed else start - 1
    after = (end + 1) % len(units) if closed else end + 1
    supported_before = before >= 0 and before < len(units) and units[before]["supported"]
    supported_after = after >= 0 and after < len(units) and units[after]["supported"]
    points = [units[index]["p0"] for index in indexes] + [units[indexes[-1]]["p1"]]
    if supported_before and supported_after:
        support = "both_ends"
    elif supported_before or supported_after:
        support = "one_end"
    else:
        support = "none"
    return {
        "lengthMm": round(sum(units[index]["length"] for index in indexes), 4),
        "supportedBefore": supported_before,
        "supportedAfter": supported_after,
        "support": support,
        "startXYmm": [round(value, 4) for value in units[indexes[0]]["p0"]],
        "endXYmm": [round(value, 4) for value in units[indexes[-1]]["p1"]],
        "boundsXYmm": [
            [round(min(point[0] for point in points), 4), round(max(point[0] for point in points), 4)],
            [round(min(point[1] for point in points), 4), round(max(point[1] for point in points), 4)],
        ],
    }


def measure_layers(layers):
    """一つの部品の層列を測る。最初の押出層はベッド支持として除外する。"""
    report_layers = []
    totals = {"external": 0.0, "bridge": 0.0, "internal": 0.0}
    previous_cells = None
    analyzed = 0
    for layer in layers:
        segments = layer["segs"]
        if not segments:
            continue
        if previous_cells is None:
            previous_cells = coverage(segments, CELL)
            continue
        analyzed += 1
        intervals = []
        for path_index, chain in enumerate(_chains(segments)):
            units = _sample_chain(chain["points"], previous_cells)
            if not units:
                continue
            closed = _same_point(chain["points"][0], chain["points"][-1])
            category = _category(chain["feature"])
            for run in _unsupported_runs(units, closed):
                result = _run_result(units, run, closed)
                totals[category] += result["lengthMm"]
                intervals.append({
                    "pathIndex": path_index,
                    "feature": chain["feature"],
                    "category": category,
                    **result,
                })
        if intervals:
            intervals.sort(key=lambda row: row["lengthMm"], reverse=True)
            report_layers.append({
                "zMm": round(float(layer["z"]), 4),
                "intervals": intervals,
                "maximumIntervalMm": intervals[0]["lengthMm"],
            })
        previous_cells = coverage(segments, CELL)
    all_intervals = [interval for layer in report_layers for interval in layer["intervals"]]
    maximum_by_category = {
        category: max((row["lengthMm"] for row in all_intervals
                       if row["category"] == category), default=0.0)
        for category in totals
    }
    return {
        "layersAnalyzed": analyzed,
        "layersWithUnsupported": len(report_layers),
        "cumulativeUnsupportedMm": {key: round(value, 4) for key, value in totals.items()},
        "warningCumulativeMm": round(totals["external"], 4),
        "maximumWarningIntervalMm": maximum_by_category["external"],
        "maximumIntervalByCategoryMm": maximum_by_category,
        "maximumUnsupportedIntervalMm": max(
            (row["lengthMm"] for row in all_intervals), default=0.0),
        "layers": report_layers,
    }


def _segment(x0, y0, x1, y1, feature="Outer wall", z=0.2):
    return (x0, y0, x1, y1, feature, 1, z)


def _synthetic_layers(top_segments, support_segments):
    return [
        {"z": 0.2, "segs": support_segments},
        {"z": 0.4, "segs": top_segments},
    ]


def calibration_report():
    anchors = [_segment(-0.3, 0, 0.3, 0), _segment(9.7, 0, 10.3, 0)]
    both = measure_layers(_synthetic_layers([_segment(0, 0, 10, 0, "Bridge")], anchors))
    one = measure_layers(_synthetic_layers(
        [_segment(0, 0, 5, 0)], [_segment(-0.3, 0, 0.3, 0)]))
    supported_case = measure_layers(_synthetic_layers(
        [_segment(0, 0, 10, 0)], [_segment(0, 0, 10, 0)]))
    split = measure_layers(_synthetic_layers([
        _segment(0, 0, 2, 0, "Bridge"), _segment(2, 0, 4, 0, "Bridge"),
        _segment(4, 0, 6, 0, "Bridge"), _segment(6, 0, 8, 0, "Bridge"),
        _segment(8, 0, 10, 0, "Bridge"),
    ], anchors))
    separated = measure_layers(_synthetic_layers([
        _segment(0, 0, 4, 0), _segment(6, 0, 10, 0),
    ], anchors))

    def longest(report):
        return report["maximumUnsupportedIntervalMm"]

    both_intervals = both["layers"][0]["intervals"]
    one_intervals = one["layers"][0]["intervals"]
    separated_intervals = separated["layers"][0]["intervals"]
    rows = [
        {
            "id": "known-both-end-bridge", "label": "両端支持の既知長橋",
            "pass": len(both_intervals) == 1
                    and both_intervals[0]["support"] == "both_ends"
                    and abs(longest(both) - 8.0) <= SAMPLE_MM,
            "inputPathMm": 10.0, "measuredMm": longest(both), "expectedMm": 8.0,
        },
        {
            "id": "known-one-end", "label": "片側だけを支持した浮き",
            "pass": len(one_intervals) == 1 and one_intervals[0]["support"] == "one_end"
                    and abs(longest(one) - 4.0) <= SAMPLE_MM,
            "inputPathMm": 5.0, "measuredMm": longest(one), "expectedMm": 4.0,
        },
        {
            "id": "known-supported", "label": "直下層で支持した経路",
            "pass": supported_case["maximumUnsupportedIntervalMm"] == 0,
            "measuredMm": longest(supported_case), "expectedMm": "0",
        },
        {
            "id": "split-chord-continuous", "label": "分割弦の連続",
            "pass": len(split["layers"][0]["intervals"]) == 1
                    and abs(longest(split) - longest(both)) <= SAMPLE_MM,
            "measuredMm": longest(split), "expectedMm": longest(both),
        },
        {
            "id": "split-chord-separated", "label": "離れた線分の非連結",
            "pass": len(separated_intervals) == 2
                    and all(row["support"] == "one_end" for row in separated_intervals)
                    and longest(separated) < 4.0,
            "measuredMm": longest(separated), "expectedMm": "4.0未満を2区間",
        },
    ]
    return {"pass": all(row["pass"] for row in rows), "cases": rows}


def _read_sliced_3mf(path):
    with zipfile.ZipFile(path) as archive:
        slice_info = archive.read("Metadata/slice_info.config").decode("utf-8")
        gcode_names = [name for name in archive.namelist() if name.endswith(".gcode")]
        if len(gcode_names) != 1:
            raise ValueError(f"expected one G-code in {path}, found {len(gcode_names)}")
        gcode = archive.read(gcode_names[0])
    labels = {
        int(object_id): name
        for object_id, name in re.findall(
            r'<object identify_id="(\d+)" name="([^"]+)"', slice_info)
    }
    with tempfile.TemporaryDirectory(prefix="lattice_print_spans_") as temporary:
        gcode_path = Path(temporary) / "plate.gcode"
        gcode_path.write_bytes(gcode)
        layers, _ = parse_gcode(gcode_path)
    return layers, labels


def inspect(path):
    path = Path(path)
    layers, labels = _read_sliced_3mf(path)
    by_object = {}
    for layer in layers:
        for segment in layer["segs"]:
            by_object.setdefault(segment[5], {}).setdefault(round(segment[6], 4), []).append(segment)
    expected_names = [
        row["name"].removesuffix(".stl") for row in inspect_layout(path)["objects"]
    ]
    object_ids = [str(object_id) for object_id in by_object]
    assigned, assignment_detail = _bbox_object_assignment(path, object_ids, expected_names)
    objects = []
    for object_id, by_z in sorted(by_object.items(), key=lambda row: (-1 if row[0] is None else row[0])):
        object_layers = [{"z": z, "segs": by_z[z]} for z in sorted(by_z)]
        measured = measure_layers(object_layers)
        legacy_total, _, _ = floating_report(object_layers, R_SUP, CELL)
        objects.append({
            "objectId": object_id,
            "name": assigned.get(
                str(object_id), labels.get(
                    object_id, "未割当" if object_id is None else str(object_id))),
            "legacyCumulativeExternalUnsupportedMm": legacy_total["external_unsupported_mm"],
            **measured,
        })
    calibration = calibration_report()
    return {
        "version": 1,
        "source": {
            "file": path.as_posix(),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        },
        "method": {
            "sampleMaximumMm": SAMPLE_MM,
            "supportRadiusMm": R_SUP,
            "coverageCellMm": CELL,
            "coordinateSystem": "スライス済みプレートのXY座標。単位mm。",
            "basis": "直下の実押出経路から支持半径0.6mmを超えた連続区間。STL空隙そのものの寸法ではない。",
            "cumulativeWarningMeaning": "全警告区間の合計であり、単一スパンではない。",
            "acceptance": "この記録だけでprint_path_reviewをacceptedへ変更しない。",
        },
        "calibration": calibration,
        "objectAssignment": {
            "complete": len(assigned) == len(by_object),
            "method": "配置STLとOuter wall押出経路のXY境界を対応",
            "detail": assignment_detail,
        },
        "objects": objects,
    }


def _write_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if path is None:
        sys.stdout.write(data.decode("utf-8"))
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="Bambu Studioが生成したgcode.3mf")
    parser.add_argument("--output", type=Path, help="JSONの保存先。省略時は標準出力")
    parser.add_argument("--calibrate", action="store_true", help="内蔵した正負例だけを測る")
    args = parser.parse_args(argv)
    if not args.calibrate and not args.input:
        parser.error("input または --calibrate が必要です")
    if args.calibrate and args.input:
        parser.error("--calibrate と input は同時に指定できません")
    return args


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args(argv)
    result = ({"version": 1, "calibration": calibration_report()}
              if args.calibrate else inspect(args.input))
    _write_json(args.output, result)
    if not result["calibration"]["pass"]:
        raise RuntimeError("未支持区間計器の校正に失敗しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
