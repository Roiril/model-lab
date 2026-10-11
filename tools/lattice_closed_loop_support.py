"""Audit closed G-code paths that have no support from the previous layer."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.stdout.reconfigure(encoding="utf-8")

from lattice_print_spans import (  # noqa: E402
    CELL,
    _run_result,
    _sample_chain,
    _unsupported_runs,
    coverage,
)
from lattice_delivery import inspect_layout  # noqa: E402
from lattice_span_locator import read_width_layers, width_chains  # noqa: E402
from plate_3mf import bbox, read_stl  # noqa: E402


SAMPLE_MM = 0.1
JOIN_MM = 1e-6


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def point_segment_distance(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    squared = dx * dx + dy * dy
    if squared == 0:
        return math.dist(point, start)
    t = max(0.0, min(1.0, ((point[0] - start[0]) * dx
                            + (point[1] - start[1]) * dy) / squared))
    closest = (start[0] + t * dx, start[1] + t * dy)
    return math.dist(point, closest)


def sample_points(points):
    samples = []
    for start, end in zip(points[:-1], points[1:]):
        length = math.dist(start, end)
        count = max(1, math.ceil(length / SAMPLE_MM))
        for index in range(count):
            t = (index + 0.5) / count
            samples.append(((start[0] + (end[0] - start[0]) * t,
                             start[1] + (end[1] - start[1]) * t),
                            length / count))
    return samples


def chain_length(chain):
    return sum(math.dist(a, b) for a, b in zip(chain["points"][:-1], chain["points"][1:]))


def material_closed(chain):
    """Treat a seam smaller than the extrusion width as a closed material path."""
    return math.dist(chain["points"][0], chain["points"][-1]) <= max(chain["widths"])


def previous_support(chain, previous_cells):
    units = _sample_chain(chain["points"], previous_cells)
    supported_length = sum(unit["length"] for unit in units if unit["supported"])
    total = sum(unit["length"] for unit in units)
    runs = [
        _run_result(units, run, material_closed(chain))
        for run in _unsupported_runs(
            units, material_closed(chain))
    ]
    return units, supported_length / total if total else 1.0, runs


def layer_spatial_index(chains):
    index_cell = 0.5
    maximum_width = max((max(chain["widths"]) for chain in chains), default=0.5)
    spatial = {}
    for path_index, chain in enumerate(chains):
        prior_width = max(chain["widths"])
        search_limit = (maximum_width + prior_width) / 2
        for start, end in zip(chain["points"][:-1], chain["points"][1:]):
            x0 = math.floor((min(start[0], end[0]) - search_limit) / index_cell)
            x1 = math.floor((max(start[0], end[0]) + search_limit) / index_cell)
            y0 = math.floor((min(start[1], end[1]) - search_limit) / index_cell)
            y1 = math.floor((max(start[1], end[1]) + search_limit) / index_cell)
            row = (path_index, start, end, prior_width)
            for ix in range(x0, x1 + 1):
                for iy in range(y0, y1 + 1):
                    spatial.setdefault((ix, iy), []).append(row)
    return index_cell, spatial


def earlier_connections(target, target_index, chains, previous_cells, layer_index):
    target_samples = sample_points(target["points"])
    target_width = max(target["widths"])
    index_cell, spatial = layer_index
    overlaps = {}
    for point, length in target_samples:
        cell = (math.floor(point[0] / index_cell), math.floor(point[1] / index_cell))
        distances = {}
        metadata = {}
        for path_index, start, end, prior_width in spatial.get(cell, []):
            if path_index >= target_index:
                continue
            overlap_limit = (target_width + prior_width) / 2
            distance = point_segment_distance(point, start, end)
            distances[path_index] = min(distance, distances.get(path_index, math.inf))
            metadata[path_index] = (prior_width, overlap_limit)
        for path_index, distance in distances.items():
            prior_width, overlap_limit = metadata[path_index]
            if distance <= overlap_limit:
                result = overlaps.setdefault(path_index, {
                    "length": 0.0, "minimum": math.inf,
                    "priorWidth": prior_width, "limit": overlap_limit})
                result["length"] += length
                result["minimum"] = min(result["minimum"], distance)
    rows = []
    for path_index, overlap in overlaps.items():
        chain = chains[path_index]
        prior_segments = list(zip(chain["points"][:-1], chain["points"][1:]))
        endpoint_distances = [min(point_segment_distance(point, start, end)
                                  for start, end in prior_segments)
                              for point in (target["points"][0], target["points"][-1])]
        _, prior_fraction, prior_runs = previous_support(chain, previous_cells)
        prior_bridge_pass = prior_fraction > 0 and all(
            run["support"] == "both_ends" and run["lengthMm"] <= 10.0
            for run in prior_runs)
        rows.append({
            "pathIndex": path_index,
            "feature": chain["feature"],
            "earlierLineWidthMm": round(overlap["priorWidth"], 5),
            "centerlineOverlapLimitMm": round(overlap["limit"], 5),
            "minimumCenterlineDistanceMm": round(overlap["minimum"], 5),
            "targetPathOverlapLengthMm": round(overlap["length"], 4),
            "targetPathOverlapFraction": round(overlap["length"] / chain_length(target), 6),
            "targetEndpointCenterlineDistancesMm": [
                round(distance, 5) for distance in endpoint_distances],
            "targetEndpointsOverlap": [
                distance <= overlap["limit"] for distance in endpoint_distances],
            "earlierPathPreviousLayerSupportedFraction": round(prior_fraction, 6),
            "earlierPathSupportedBridgePass": prior_bridge_pass,
            "earlierPathMaximumUnsupportedRunMm": round(max(
                (run["lengthMm"] for run in prior_runs), default=0.0), 4),
            "earlierPathUnsupportedRuns": sorted(
                prior_runs, key=lambda run: run["lengthMm"], reverse=True),
        })
    return sorted(rows, key=lambda row: (-row["targetPathOverlapFraction"], row["pathIndex"]))


def decide_finding(finding, established_paths, external_support):
    valid_connections = [
        connection for connection in finding["sameLayerEarlierConnections"]
        if connection["earlierPathSupportedBridgePass"] or
        established_paths.get(connection["pathIndex"], False)
    ]
    if external_support:
        return {
            "pass": True,
            "basis": "removable_support_below_first_product_path",
            "connectedFraction": 1.0,
            "maximumUnconnectedLengthMm": 0.0,
        }
    connected_fraction = max(
        (connection["targetPathOverlapFraction"] for connection in valid_connections),
        default=0.0)
    endpoints_connected = [
        any(connection["targetEndpointsOverlap"][endpoint]
            for connection in valid_connections)
        for endpoint in range(2)
    ]
    unconnected_length = finding["pathLengthMm"] * (1.0 - connected_fraction)
    if connected_fraction > 0 and all(endpoints_connected) and unconnected_length <= 10.0:
        return {
            "pass": True,
            "basis": "material_width_connection_to_established_earlier_path",
            "connectedFraction": round(connected_fraction, 6),
            "startAndEndConnected": endpoints_connected,
            "maximumUnconnectedLengthMm": round(unconnected_length, 4),
            "earlierPathIndices": [connection["pathIndex"] for connection in valid_connections],
        }
    return {
        "pass": False,
        "basis": "no_established_previous_or_same_layer_support",
        "connectedFraction": round(connected_fraction, 6),
        "startAndEndConnected": endpoints_connected,
        "maximumUnconnectedLengthMm": round(unconnected_length, 4),
    }


def external_path_coverage(target, support_segments):
    samples = sample_points(target["points"])
    target_width = max(target["widths"])

    def supported_at(point):
        return any(point_segment_distance(point, start, end) <= (target_width + width) / 2
                   for start, end, width in support_segments)

    supported_length = sum(length for point, length in samples if supported_at(point))
    total = chain_length(target)
    endpoint_supported = [supported_at(point)
                          for point in (target["points"][0], target["points"][-1])]
    return {
        "pathCoverageFraction": round(supported_length / total if total else 1.0, 6),
        "startAndEndCovered": endpoint_supported,
        "supportSegmentCount": len(support_segments),
        "supportLineWidthsMm": sorted({round(segment[2], 5)
                                       for segment in support_segments}),
    }


def inspect_plate(path, span_report, layout_source_path):
    layers = read_width_layers(path)
    layout = inspect_layout(path)
    offset = span_report["objectAssignment"]["detail"]["global_offset_mm"]
    object_records = {obj["objectId"]: obj for obj in span_report["objects"]}
    model = next(iter(object_records.values()))["name"].rsplit("-print-", 1)[0]
    build = ROOT / "models" / model / "build"
    manifest_path = build / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    support_geometry_path = build / "print_support_geometry.json"
    support_geometry = (json.loads(support_geometry_path.read_text(encoding="utf-8"))
                        if support_geometry_path.exists() else None)
    support_geometry_valid = bool(
        support_geometry and support_geometry.get("calibration", {}).get("pass") is True and
        support_geometry.get("sourceIntegrity", {}).get("pass") is True)
    support_geometry_by_part = {
        row["partId"]: row for row in support_geometry.get("supports", [])
    } if support_geometry else {}
    support_definitions_by_part = {}
    for row in manifest.get("print_supports", []):
        support_definitions_by_part.setdefault(row["part_id"], []).append(row)
    candidates = set()
    for obj in span_report["objects"]:
        for layer in obj["layers"]:
            for interval in layer["intervals"]:
                if interval["support"] == "none":
                    candidates.add((obj["objectId"], round(float(layer["zMm"]), 4),
                                    interval["pathIndex"]))
    by_object = {}
    for layer in layers:
        z_mm = round(float(layer["z"]), 4)
        for object_id in {segment[5] for segment in layer["segs"]}:
            segments = [segment for segment in layer["segs"] if segment[5] == object_id]
            if segments:
                by_object.setdefault(object_id, []).append((z_mm, segments))
    findings = []
    for object_id, object_layers in by_object.items():
        object_record = object_records[object_id]
        placement = next(row for row in layout["objects"]
                         if row["name"] == object_record["name"])
        object_model = object_record["name"].rsplit("-print-", 1)[0]
        stl_path = ROOT / "prints" / object_model / f"{object_record['name']}.stl"
        stl_min, _ = bbox(read_stl(stl_path)[0])
        part_id = object_record["name"].rsplit("-print-", 1)[1]
        support_contexts = []
        geometry_record = support_geometry_by_part.get(part_id)
        for definition in support_definitions_by_part.get(part_id, []):
            support_bounds = definition["component_bbox_mm"]

            def plate_xy(point):
                return [point[axis] - stl_min[axis] + placement["min"][axis] - offset[axis]
                        for axis in range(2)]

            plate_min = plate_xy(support_bounds[0])
            plate_max = plate_xy(support_bounds[1])
            support_z = round(definition["support_top_z_mm"], 4)
            support_layer = next((segments for z_value, segments in object_layers
                                  if z_value == support_z), [])
            support_segments = []
            support_layer_heights = set()
            for segment in support_layer:
                midpoint = ((segment[0] + segment[2]) / 2,
                            (segment[1] + segment[3]) / 2)
                if (plate_min[0] <= midpoint[0] <= plate_max[0] and
                        plate_min[1] <= midpoint[1] <= plate_max[1]):
                    support_segments.append(
                        ((segment[0], segment[1]), (segment[2], segment[3]), segment[7]))
                    support_layer_heights.add(round(segment[8], 5))
            support_contexts.append({
                "definition": definition,
                "segments": support_segments,
                "layerHeightsMm": sorted(support_layer_heights),
                "geometryPass": bool(
                    support_geometry_valid and geometry_record and geometry_record.get("pass") is True and
                    definition["support_id"] in geometry_record.get("supportIds", [])),
            })
        previous_cells = None
        for z_mm, segments in object_layers:
            if previous_cells is None:
                previous_cells = coverage(segments, CELL)
                continue
            chains = width_chains(segments)
            established_paths = {}
            for path_index, chain in enumerate(chains):
                if (object_id, z_mm, path_index) not in candidates:
                    continue
                if not material_closed(chain):
                    continue
                _, supported_fraction, runs = previous_support(chain, previous_cells)
                none_runs = [run for run in runs if run["support"] == "none"]
                if not none_runs:
                    continue
                spatial_index = layer_spatial_index(chains)
                connections = earlier_connections(
                    chain, path_index, chains, previous_cells, spatial_index)
                supported_connections = [
                    connection for connection in connections
                    if connection["earlierPathPreviousLayerSupportedFraction"] > 0]
                plate_bounds = [
                    [min(point[axis] for point in chain["points"]),
                     max(point[axis] for point in chain["points"])]
                    for axis in range(2)
                ]
                local_bounds = [
                    [round(value + offset[axis] - placement["min"][axis] + stl_min[axis], 4)
                     for value in plate_bounds[axis]]
                    for axis in range(2)
                ]
                external_support = False
                external_evidence = None
                for context in support_contexts:
                    definition = context["definition"]
                    if abs(z_mm - definition["product_first_z_mm"]) > 1e-6:
                        continue
                    coverage_result = external_path_coverage(chain, context["segments"])
                    product_layer_heights = sorted({round(segment[8], 5)
                                                    for segment in segments})
                    product_material_bottom = z_mm - max(product_layer_heights)
                    actual_material_face_gap = round(
                        product_material_bottom - definition["support_top_z_mm"], 5)
                    gap_matches_definition = abs(
                        actual_material_face_gap - definition["material_face_gap_mm"]) <= 0.01
                    candidate_pass = (context["geometryPass"] and
                                      coverage_result["pathCoverageFraction"] == 1.0 and
                                      all(coverage_result["startAndEndCovered"]) and
                                      gap_matches_definition)
                    if external_evidence is None or coverage_result["pathCoverageFraction"] > \
                            external_evidence["pathCoverageFraction"]:
                        external_evidence = {
                            "supportId": definition["support_id"],
                            "geometryEvidenceFile": str(
                                support_geometry_path.relative_to(ROOT)).replace("\\", "/"),
                            "geometryEvidenceSha256": sha256(support_geometry_path),
                            "geometryPass": context["geometryPass"],
                            "supportTopGcodeZMm": round(definition["support_top_z_mm"], 4),
                            "materialFaceGapMm": definition["material_face_gap_mm"],
                            "supportTopLayerHeightsMm": context["layerHeightsMm"],
                            "productFirstLayerHeightsMm": product_layer_heights,
                            "productMaterialBottomMm": round(product_material_bottom, 5),
                            "actualMaterialFaceGapMm": actual_material_face_gap,
                            "gapMatchesDefinition": gap_matches_definition,
                            **coverage_result,
                        }
                    external_support = external_support or candidate_pass
                finding = {
                    "objectId": object_id,
                    "objectName": object_record["name"],
                    "zMm": z_mm,
                    "pathIndex": path_index,
                    "feature": chain["feature"],
                    "pathLengthMm": round(chain_length(chain), 4),
                    "endpointCenterlineGapMm": round(
                        math.dist(chain["points"][0], chain["points"][-1]), 5),
                    "plateBoundsXYMm": [[round(value, 4) for value in axis]
                                         for axis in plate_bounds],
                    "printStlBoundsXYMm": local_bounds,
                    "printStlCenterMm": [round(sum(axis) / 2, 4) for axis in local_bounds]
                                        + [z_mm],
                    "sourcePrintStl": {
                        "file": str(stl_path.relative_to(ROOT)).replace("\\", "/"),
                        "sha256": sha256(stl_path),
                    },
                    "sourceLayout": {
                        "file": str(layout_source_path.relative_to(ROOT)).replace("\\", "/"),
                        "sha256": sha256(layout_source_path),
                    },
                    "sourceManifest": {
                        "file": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
                        "sha256": sha256(manifest_path),
                    },
                    "lineWidthsMm": sorted({round(width, 5) for width in chain["widths"]}),
                    "previousLayerSupportedFraction": round(supported_fraction, 6),
                    "noneRuns": none_runs,
                    "sameLayerEarlierConnections": connections,
                    "targetEndpointsHaveEarlierSupportedOverlap": [
                        any(connection["targetEndpointsOverlap"][endpoint]
                            for connection in supported_connections)
                        for endpoint in range(2)
                    ],
                    "maximumOverlapFractionFromAnEarlierSupportedPath": round(max(
                        (row["targetPathOverlapFraction"] for row in connections
                         if row["earlierPathPreviousLayerSupportedFraction"] > 0),
                        default=0.0), 6),
                }
                if external_evidence:
                    finding["externalSupportEvidence"] = external_evidence
                decision = decide_finding(finding, established_paths, external_support)
                finding["decision"] = "accepted" if decision.pop("pass") else "rejected"
                finding["basis"] = decision.pop("basis")
                finding["decisionEvidence"] = decision
                established_paths[path_index] = finding["decision"] == "accepted"
                findings.append(finding)
            previous_cells = coverage(segments, CELL)
    return findings


def calibration():
    circle = [(math.cos(index * math.pi / 8), math.sin(index * math.pi / 8))
              for index in range(16)]
    circle.append(circle[0])
    target = {"feature": "Outer wall", "points": circle, "widths": [0.4] * 16}
    supported_cells = coverage([(a[0], a[1], b[0], b[1], "Outer wall", 1, 0.2)
                                for a, b in zip(circle[:-1], circle[1:])], CELL)
    empty_cells = coverage([], CELL)
    _, positive_fraction, _ = previous_support(target, supported_cells)
    _, negative_fraction, negative_runs = previous_support(target, empty_cells)
    prior = {"feature": "Outer wall", "points": [(-1.5, 0), (1.5, 0)], "widths": [0.4]}
    calibration_chains = [prior, target]
    connections = earlier_connections(
        target, 1, calibration_chains, supported_cells,
        layer_spatial_index(calibration_chains))
    floating_prior = {"feature": "Outer wall", "points": circle,
                      "widths": [0.4] * 16}
    outer = [(1.3 * point[0], 1.3 * point[1]) for point in circle]
    chained_target = {"feature": "Outer wall", "points": outer,
                      "widths": [0.4] * 16}
    chained = [floating_prior, chained_target]
    chained_connections = earlier_connections(
        chained_target, 1, chained, empty_cells, layer_spatial_index(chained))
    chained_finding = {
        "pathLengthMm": round(chain_length(chained_target), 4),
        "sameLayerEarlierConnections": chained_connections,
    }
    floating_chain_decision = decide_finding(chained_finding, {}, False)
    positive_material_gap = round((8.2 - 0.2) - 7.8, 5)
    negative_material_gap = round((8.0 - 0.2) - 7.8, 5)
    material_gap_calibration_pass = (
        abs(positive_material_gap - 0.2) <= 0.01 and
        abs(negative_material_gap - 0.2) > 0.01)
    return {
        "positivePreviousLayerSupportedFraction": round(positive_fraction, 6),
        "negativePreviousLayerSupportedFraction": round(negative_fraction, 6),
        "negativeHasNoneRun": any(run["support"] == "none" for run in negative_runs),
        "sameLayerIntersectionDetected": bool(connections),
        "floatingEarlierLoopDoesNotSupportNextLoop": floating_chain_decision["pass"] is False,
        "positiveMaterialFaceGapMm": positive_material_gap,
        "zeroMaterialFaceGapMm": negative_material_gap,
        "materialFaceGapCalibrationPass": material_gap_calibration_pass,
        "pass": positive_fraction == 1.0 and negative_fraction == 0.0
                and any(run["support"] == "none" for run in negative_runs)
                and bool(connections) and floating_chain_decision["pass"] is False
                and material_gap_calibration_pass,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=("mystery-box-sg92r-c3", "mystery-box-sg92r-c4"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    algorithm_paths = [
        Path(__file__),
        ROOT / "tools" / "lattice_print_spans.py",
        ROOT / "tools" / "lattice_span_locator.py",
        ROOT / "tools" / "lattice_delivery.py",
        ROOT / "tools" / "plate_3mf.py",
        ROOT / "lib" / "printmech" / "gcode.py",
    ]
    algorithm_start = {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
                       for path in algorithm_paths}
    print_dir = ROOT / "prints" / args.model
    plates = {}
    for suffix in ("PLA", "PETG", "fit-test-PLA", "fit-test-PETG"):
        path = print_dir / f"{args.model}-{suffix}.gcode.3mf"
        report_name = (f"print_spans_{suffix}.json" if not suffix.startswith("fit-test-")
                       else f"print_spans_fit_{suffix.removeprefix('fit-test-')}.json")
        span_path = ROOT / "models" / args.model / "build" / report_name
        span_report = json.loads(span_path.read_text(encoding="utf-8"))
        layout_name = (f"{args.model}-fit-test-layout.3mf"
                       if suffix.startswith("fit-test-")
                       else f"{args.model}-layout.3mf")
        layout_source_path = print_dir / layout_name
        findings = inspect_plate(path, span_report, layout_source_path)
        plates[suffix] = {
            "sourceGcode": {
                "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(path),
            },
            "sourceSpanReport": {
                "file": str(span_path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(span_path),
            },
            "summary": {
                "closedUnsupportedPathCount": len(findings),
                "pathsWithNoEarlierSupportedConnection": sum(
                    not any(connection["earlierPathPreviousLayerSupportedFraction"] > 0
                            for connection in finding["sameLayerEarlierConnections"])
                    for finding in findings),
            },
            "closedUnsupportedPaths": findings,
        }
    algorithm_end = {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
                     for path in algorithm_paths}
    calibration_result = calibration()
    all_findings = [finding for plate in plates.values()
                    for finding in plate["closedUnsupportedPaths"]]
    result = {
        "model": args.model,
        "sourceAlgorithmSha256": algorithm_end,
        "sourceAlgorithmIntegrity": {
            "start": algorithm_start,
            "end": algorithm_end,
            "pass": algorithm_start == algorithm_end,
        },
        "calibration": calibration_result,
        "overall": {
            "findingCount": len(all_findings),
            "failedFindingCount": sum(finding["decision"] != "accepted"
                                      for finding in all_findings),
            "pass": calibration_result["pass"] and algorithm_start == algorithm_end and
                    all(finding["decision"] == "accepted" for finding in all_findings),
        },
        "plates": plates,
    }
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", newline="\n", delete=False,
                    dir=args.output.parent, prefix=f".{args.output.name}.", suffix=".tmp") as handle:
                temporary = Path(handle.name)
                handle.write(encoded)
            os.replace(temporary, args.output)
        finally:
            if temporary and temporary.exists():
                temporary.unlink()
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
