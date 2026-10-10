"""格子箱の組立工程を表示用JSONとEXACT検査へ同じフレームから書き出す。"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
from typing import Callable

from mathutils import Matrix, Vector


IDENTITY = Matrix.Identity(4)
VOLUME_LIMIT_MM3 = 0.001


def translation(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((float(x), float(y), float(z)))


def rotate_x_about(degrees, y=0.0, z=0.0):
    return (translation(y=y, z=z)
            @ Matrix.Rotation(math.radians(float(degrees)), 4, "X")
            @ translation(y=-y, z=-z))


def column_major(matrix):
    return [round(float(matrix[row][column]), 10)
            for column in range(4) for row in range(4)]


def samples(start, end, maximum_step):
    count = max(1, int(math.ceil(abs(end - start) / maximum_step)))
    return [start + (end - start) * index / count for index in range(count + 1)]


def translated_group(base, start, end, maximum_step=0.99):
    delta = Vector(end) - Vector(start)
    count = max(1, int(math.ceil(delta.length / maximum_step)))
    frames = []
    for index in range(count + 1):
        point = Vector(start).lerp(Vector(end), index / count)
        offset = translation(*point)
        frames.append({name: offset @ matrix for name, matrix in base.items()})
    return frames


def rotation_group(functions, start_degrees, end_degrees, maximum_step=1.0):
    return [{name: function(angle) for name, function in functions.items()}
            for angle in samples(start_degrees, end_degrees, maximum_step)]


def join_paths(*paths):
    joined = []
    for path in paths:
        if not path:
            continue
        joined.extend(path if not joined else path[1:])
    return joined


def matrix_close(left, right, tolerance=1e-6):
    return max(abs(left[row][column] - right[row][column])
               for row in range(4) for column in range(4)) <= tolerance


@dataclass
class Allowance:
    parts: tuple[str, str]
    kind: str
    zone: str | None = None
    deflection_mm: float | None = None
    strain_percent: float | None = None
    allow_at_final: bool = False
    maximum_common_volume_mm3: float | None = None
    bounds_mm: tuple[tuple[float, float, float], tuple[float, float, float]] | None = None

    def document(self):
        result = {"parts": list(self.parts), "kind": self.kind}
        if self.zone is not None:
            result["zone"] = self.zone
        if self.deflection_mm is not None:
            result["deflectionMm"] = self.deflection_mm
        if self.strain_percent is not None:
            result["strainPercent"] = self.strain_percent
        if self.maximum_common_volume_mm3 is not None:
            result["limitCommonVolumeMm3"] = self.maximum_common_volume_mm3
        if self.bounds_mm is not None:
            result["boundsMm"] = [list(row) for row in self.bounds_mm]
        return result


class AssemblyPlan:
    def __init__(self, model, target_parts):
        self.model = model
        self.target_parts = tuple(target_parts)
        self.state = {}
        self.steps = []

    def seed(self, *parts):
        for part in parts:
            self.state[part] = IDENTITY.copy()

    def add(self, step_id, title, instruction, check_text, moving, moving_frames,
            allowances=()):
        moving = tuple(moving)
        if not moving_frames:
            raise ValueError(f"{step_id}: frames are empty")
        if any(set(frame) != set(moving) for frame in moving_frames):
            raise ValueError(f"{step_id}: every moving frame must contain {moving}")
        for part in moving:
            if part in self.state and not matrix_close(self.state[part], moving_frames[0][part]):
                raise ValueError(f"{step_id}: {part} does not start at its previous endpoint")
        installed = [part for part in self.state if part not in moving]
        frames = []
        denominator = max(1, len(moving_frames) - 1)
        for index, moving_transforms in enumerate(moving_frames):
            transforms = {part: matrix.copy() for part, matrix in self.state.items()
                          if part not in moving}
            transforms.update(moving_transforms)
            frames.append({
                "progress": round(index / denominator, 8),
                "transforms": {part: column_major(matrix)
                               for part, matrix in transforms.items()},
            })
        self.steps.append({
            "id": step_id,
            "title": title,
            "instruction": instruction,
            "checkText": check_text,
            "moving": list(moving),
            "installed": installed,
            "frames": frames,
            "_matrices": [{part: matrix.copy() for part, matrix in self.state.items()
                           if part not in moving} | moving_transforms
                          for moving_transforms in moving_frames],
            "_allowances": list(allowances),
        })
        self.state.update({part: matrix.copy() for part, matrix in moving_frames[-1].items()})


class ExactAdapter:
    def __init__(self, model, verify, meshes):
        self.model = model
        self.verify = verify
        self.meshes = meshes

    def bounds(self, part, matrix):
        mesh = self.meshes[part]
        if self.model.endswith("c3"):
            return self.verify.transformed_mesh(mesh, matrix)["bounds"]
        return mesh.moved(matrix).bounds()

    def measure(self, left, right, left_matrix, right_matrix, allowance=None):
        if self.model.endswith("c3"):
            result = self.verify.exact_pair(
                self.meshes, left, right, left_matrix, right_matrix)
            return {
                "common_volume_mm3": result["volume_mm3"],
                "intersection_bounds_mm": None,
                "existing_allowed": bool(result.get("flex") and result["ok"]),
                "existing_detail": result.get("flex"),
                "zone_ok": None,
            }
        predicate = None
        if allowance is not None and allowance.zone is not None:
            predicate = lambda point: self.verify.point_in_snap_zone(allowance.zone, point)
        result = self.verify.exact_common_geometry(
            self.meshes[left], left_matrix, self.meshes[right], right_matrix, predicate)
        return {
            "common_volume_mm3": result["common_volume_mm3"],
            "intersection_bounds_mm": result["intersection_bounds_mm"],
            "existing_allowed": False,
            "existing_detail": None,
            "zone_ok": result["vertices_in_allowed_zone"],
        }


def disjoint(left, right):
    return any(left[1][axis] <= right[0][axis] or right[1][axis] <= left[0][axis]
               for axis in range(3))


def relative_key(left, right):
    relative = left.inverted_safe() @ right
    return tuple(round(float(relative[row][column]), 7)
                 for row in range(4) for column in range(4))


def bounds_within(actual, allowed, tolerance=0.001):
    if actual is None or allowed is None:
        return False
    return all(allowed[0][axis] - tolerance <= actual[0][axis]
               and actual[1][axis] <= allowed[1][axis] + tolerance
               for axis in range(3))


def audit_step(adapter, step):
    moving = set(step["moving"])
    allowance_map = {tuple(sorted(item.parts)): item for item in step["_allowances"]}
    pair_rows = {}
    allowed_rows = {}
    violations = []
    cache = {}
    matrices_frames = step["_matrices"]
    for sample_index, matrices in enumerate(matrices_frames):
        bounds = {part: adapter.bounds(part, matrix) for part, matrix in matrices.items()}
        for left, right in itertools.combinations(sorted(matrices), 2):
            if left not in moving and right not in moving:
                continue
            key = tuple(sorted((left, right)))
            row = pair_rows.setdefault(key, {
                "parts": list(key), "samples": 0, "aabbZeroSamples": 0,
                "exactSamples": 0, "maxCommonVolumeMm3": 0.0,
                "allowedSamples": 0, "pass": True,
            })
            row["samples"] += 1
            if disjoint(bounds[left], bounds[right]):
                row["aabbZeroSamples"] += 1
                continue
            allowance = allowance_map.get(key)
            cache_key = None
            if allowance is None or allowance.kind == "reference_internal":
                cache_key = (key, relative_key(matrices[left], matrices[right]))
            measured = cache.get(cache_key) if cache_key is not None else None
            if measured is None:
                measured = adapter.measure(
                    left, right, matrices[left], matrices[right], allowance)
                if cache_key is not None:
                    cache[cache_key] = measured
            row["exactSamples"] += 1
            volume = measured["common_volume_mm3"]
            row["maxCommonVolumeMm3"] = max(row["maxCommonVolumeMm3"], volume)
            if volume <= VOLUME_LIMIT_MM3:
                continue
            final = sample_index == len(matrices_frames) - 1
            allowed = False
            reason = None
            if allowance is not None and allowance.kind == "reference_internal":
                allowed = (allowance.maximum_common_volume_mm3 is not None
                           and volume <= allowance.maximum_common_volume_mm3
                           and bounds_within(measured["intersection_bounds_mm"], allowance.bounds_mm))
                reason = ("bounded canonical SG92R internal reference overlap" if allowed else
                          "outside calibrated SG92R internal overlap envelope")
            elif measured["existing_allowed"]:
                allowed = True
                reason = "existing bounded press-fit decision"
            elif allowance is not None:
                strain_ok = allowance.strain_percent is None or allowance.strain_percent <= 2.0
                allowed = (measured["zone_ok"] is True and strain_ok
                           and (allowance.allow_at_final or not final))
                reason = "existing bounded snap-zone decision" if allowed else "outside allowed contact"
            if allowed:
                row["allowedSamples"] += 1
                allowed_row = allowed_rows.setdefault(key, {
                    **(allowance.document() if allowance is not None else {
                        "parts": list(key), "kind": "press_fit"}),
                    "samples": 0, "maxCommonVolumeMm3": 0.0,
                })
                allowed_row["samples"] += 1
                allowed_row["maxCommonVolumeMm3"] = max(
                    allowed_row["maxCommonVolumeMm3"], volume)
                continue
            row["pass"] = False
            violations.append({
                "sample": sample_index,
                "progress": step["frames"][sample_index]["progress"],
                "parts": list(key),
                "commonVolumeMm3": volume,
                "intersectionBoundsMm": measured["intersection_bounds_mm"],
                "reason": reason or "rigid collision",
            })
    pair_documents = []
    for key in sorted(pair_rows):
        row = pair_rows[key]
        row["maxCommonVolumeMm3"] = round(row["maxCommonVolumeMm3"], 6)
        pair_documents.append(row)
    maximum = max((row["maxCommonVolumeMm3"] for row in pair_documents), default=0.0)
    return {
        "pass": not violations,
        "samples": len(matrices_frames),
        "pairs": pair_documents,
        "maxCommonVolumeMm3": round(maximum, 6),
        "allowedContacts": [allowed_rows[key] for key in sorted(allowed_rows)],
    }, violations


def validate_frames(plan):
    boundary_errors = []
    motion_errors = []
    max_translation = 0.0
    max_rotation = 0.0
    for index, step in enumerate(plan.steps):
        matrices_frames = step["_matrices"]
        if index:
            previous = plan.steps[index - 1]["_matrices"][-1]
            current = matrices_frames[0]
            for part in set(previous) & set(current):
                if not matrix_close(previous[part], current[part]):
                    boundary_errors.append({"before": plan.steps[index - 1]["id"],
                                            "after": step["id"], "part": part})
        for before, after in zip(matrices_frames, matrices_frames[1:]):
            for part in step["moving"]:
                translation_mm = (after[part].translation - before[part].translation).length
                relative = before[part].to_3x3().transposed() @ after[part].to_3x3()
                rotation_deg = math.degrees(relative.to_quaternion().angle)
                max_translation = max(max_translation, translation_mm)
                max_rotation = max(max_rotation, rotation_deg)
                if translation_mm > 1.00001 or rotation_deg > 5.00001:
                    motion_errors.append({"step": step["id"], "part": part,
                                          "translationMm": translation_mm,
                                          "rotationDeg": rotation_deg})
    return {
        "pass": not boundary_errors and not motion_errors,
        "boundaryErrors": boundary_errors,
        "motionErrors": motion_errors,
        "maxTranslationStepMm": round(max_translation, 6),
        "maxRotationStepDeg": round(max_rotation, 6),
    }


def file_hashes(build, parts):
    return {part: hashlib.sha256((build / f"{part}.stl").read_bytes()).hexdigest()
            for part in parts}


def run(plan, verify, build, load_mesh: Callable[[str], object], calibration):
    build = Path(build)
    start_hashes = file_hashes(build, plan.target_parts)
    meshes = {part: load_mesh(part) for part in plan.target_parts}
    adapter = ExactAdapter(plan.model, verify, meshes)
    frame_validation = validate_frames(plan)
    all_violations = []
    for step in plan.steps:
        step["report"], violations = audit_step(adapter, step)
        all_violations.extend({"step": step["id"], **item} for item in violations)
    final_missing = [part for part in plan.target_parts if part not in plan.state]
    final_extra = [part for part in plan.state if part not in plan.target_parts]
    final_moved = [part for part in plan.target_parts
                   if part in plan.state and not matrix_close(plan.state[part], IDENTITY)]
    final_state = {
        "pass": not final_missing and not final_extra and not final_moved,
        "expectedParts": list(plan.target_parts),
        "missing": final_missing,
        "extra": final_extra,
        "nonIdentityTransforms": final_moved,
    }
    reverse = {
        "pass": all(step["report"]["pass"] for step in plan.steps),
        "method": "same inspected frames replayed in reverse order",
        "steps": [{"id": step["id"], "samples": len(step["frames"]),
                   "pass": step["report"]["pass"]}
                  for step in reversed(plan.steps)],
    }
    end_hashes = file_hashes(build, plan.target_parts)
    source_integrity = {"pass": start_hashes == end_hashes,
                        "start": start_hashes, "end": end_hashes}
    passed = (calibration["pass"] and frame_validation["pass"]
              and all(step["report"]["pass"] for step in plan.steps)
              and final_state["pass"] and reverse["pass"] and source_integrity["pass"])
    output_steps = []
    for step in plan.steps:
        output_steps.append({key: value for key, value in step.items()
                             if not key.startswith("_")})
    document = {
        "model": plan.model,
        "source_sha256": start_hashes,
        "steps": output_steps,
        "calibration": calibration,
        "pass": passed,
    }
    report = {
        "model": plan.model,
        "method": ("display transforms and Blender Boolean EXACT are generated from the same "
                   "column-major millimetre frames"),
        "calibration": calibration,
        "frameValidation": frame_validation,
        "steps": [{"id": step["id"], **step["report"]} for step in plan.steps],
        "violations": all_violations,
        "finalState": final_state,
        "reverseDisassembly": reverse,
        "sourceIntegrity": source_integrity,
        "limitations": [
            "SG92Rホーンの実物装着と電源操作は未検証。",
            "圧入、スナップ、材料収縮、摩擦は実物未検証。",
            "離散経路は並進1mm以下、回転5度以下。フレーム間の連続空間全体は解析していない。",
        ],
        "pass": passed,
    }
    for name, payload in (("assembly.json", document), ("assembly_report.json", report)):
        path = build / name
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    print(json.dumps({
        "model": plan.model,
        "pass": passed,
        "steps": len(plan.steps),
        "samples": sum(len(step["frames"]) for step in plan.steps),
        "violations": len(all_violations),
        "max_translation_step_mm": frame_validation["maxTranslationStepMm"],
        "max_rotation_step_deg": frame_validation["maxRotationStepDeg"],
        "final_state_pass": final_state["pass"],
        "reverse_pass": reverse["pass"],
    }, ensure_ascii=False))
    if not passed:
        raise SystemExit(1)
