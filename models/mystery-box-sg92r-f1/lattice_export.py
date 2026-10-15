"""合成済みSTL・運動契約・ゲート証拠からStudioの入力を作る。

CLI: lattice_export.py [--prepare-assembly]
prepareは面別ゲート後・ルートゲート前。通常実行は表示用ファイルとassetsを更新する。
単一自由度の共通UIでは代表面を再生し、全可動面の計算を検査一覧へ併記する。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

from compose import HERE, ROOT, MODEL, C, dependency_status, read

sys.path.insert(0, str(ROOT / "tools"))
import lattice_simulation as physics
import lattice_web
from mechgate_lib.gate import freshness
from mechgate_lib import limits

BUILD = HERE / "build"
LABELS = {"front": "正面", "right": "右面", "back": "背面", "left": "左面", "top": "上面", "bottom": "底面"}
GEOMETRY_CHECKS = ("instrument.calibration", "parts.topology", "motion.interference",
                   "motion.torque", "interface.coverage", "interface.drive", "interface.retention", "assembly.path")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, document):
    """Atomic UTF-8; stable bytes keep gate input hashes unchanged on repeated export."""
    text = json.dumps(document, ensure_ascii=False, indent=1, allow_nan=False) + "\n"
    if Path(path).exists() and Path(path).read_text(encoding="utf-8") == text:
        return False
    C.write_json(Path(path), document)
    return True


def gate_evidence(model):
    path = ROOT / "models" / model / "build" / "gate_report.json"
    report = read(path) if path.exists() else {}
    status, changed = freshness(model)
    checks = {row["id"]: row for row in report.get("checks", [])}
    fresh = status in ("pass", "fail")
    passed = status == "pass" and all(checks.get(key, {}).get("pass") is True for key in GEOMETRY_CHECKS)
    return {"model": model, "status": status, "fresh": fresh, "geometryPass": passed,
            "changed": changed, "checks": checks,
            "report": path.relative_to(ROOT).as_posix(),
            "reportSha256": digest(path) if path.exists() else None}


def assembly_shape(document):
    # Display annotations are not the geometry measured by mechgate.
    return [{key: value for key, value in step.items() if key != "report"} for step in document["steps"]]


def prepare_assembly():
    """Use the representative case's measured path; it does not hash root assembly.json.

    Comparing the complete steps prevents using a successful path for another assembly.
    This must precede the root gate so no hash/report feedback loop is needed.
    """
    index = read(BUILD / "cases.json")
    model = f"{MODEL}/checks/{index['representative']}"
    evidence = gate_evidence(model)
    case = read(ROOT / "models" / model / "build" / "assembly.json")
    assembly = read(BUILD / "assembly.json")
    usable = dependency_status()[0] and evidence["fresh"] and assembly_shape(case) == assembly_shape(assembly)
    path = evidence["checks"].get("assembly.path", {}) if usable else {}
    calibration = evidence["checks"].get("instrument.calibration", {}) if usable else {}
    measured = {row["id"]: row for row in (path.get("detail") or {}).get("steps", [])}
    complete = set(measured) == {step["id"] for step in assembly["steps"]}
    assembly["pass"] = path.get("pass") is True and complete
    assembly["calibration"] = {"pass": calibration.get("pass") is True,
                               "source": model + "/build/gate_report.json#instrument.calibration"}
    for step in assembly["steps"]:
        row = measured.get(step["id"], {})
        step["report"] = {"samples": row.get("checkedPoses", 0), "pass": row.get("pass") is True,
                          "source": model + "/build/gate_report.json#assembly.path",
                          "pending": not usable or not complete}
    return write(BUILD / "assembly.json", assembly)


def rigid_properties(matrices, angles_rad, mass):
    """Generalized inertia M=m|dc/dq|²+ωᵀRIcRᵀω, gravity=d(mgz)/dq.

    Matrices are the saved rigid world transforms, translation in mm. All derivatives
    use radians and second-order finite differences (including one-sided endpoints).
    """
    matrices = np.asarray(matrices, dtype=float)
    rotation = matrices[:, :3, :3]
    centers = np.einsum("nij,j->ni", rotation, mass["comM"]) + matrices[:, :3, 3] / 1000
    velocity = np.gradient(centers, angles_rad, axis=0, edge_order=2)
    acceleration = np.gradient(velocity, angles_rad, axis=0, edge_order=2)
    rdot = np.gradient(rotation, angles_rad, axis=0, edge_order=2)
    skew = np.einsum("nij,nkj->nik", rdot, rotation)
    omega = np.column_stack(((skew[:, 2, 1] - skew[:, 1, 2]) / 2,
                             (skew[:, 0, 2] - skew[:, 2, 0]) / 2,
                             (skew[:, 1, 0] - skew[:, 0, 1]) / 2))
    xx, yy, zz, xy, xz, yz = mass["inertiaComKgm2"]
    tensor = np.array([[xx, xy, xz], [xy, yy, yz], [xz, yz, zz]])
    if mass["massKg"] <= 0 or np.linalg.eigvalsh(tensor).min() <= 0:
        raise ValueError("non-positive mass/inertia from STL")
    world_tensor = np.einsum("nij,jk,nlk->nil", rotation, tensor, rotation)
    inertia = mass["massKg"] * np.einsum("ni,ni->n", velocity, velocity)
    inertia += np.einsum("ni,nij,nj->n", omega, world_tensor, omega)
    return {"inertia": inertia, "gravity": mass["massKg"] * limits.GRAVITY * velocity[:, 2],
            "z": centers[:, 2], "dz": velocity[:, 2], "ddz": acceleration[:, 2]}


def calculation_calibration():
    box = physics.mass_calibration()
    mass = physics.signed_tetra_properties(physics.box_triangles(), 1240)
    q = np.linspace(0, math.pi / 2, 181)
    matrices = np.repeat(np.eye(4)[None], len(q), axis=0)
    matrices[:, 0, 0] = matrices[:, 2, 2] = np.cos(q)
    matrices[:, 0, 2] = np.sin(q)
    matrices[:, 2, 0] = -np.sin(q)
    result = rigid_properties(matrices, q, mass)
    cx, _, cz = mass["comM"]
    expected_m = mass["inertiaComKgm2"][1] + mass["massKg"] * (cx * cx + cz * cz)
    expected_g = -mass["massKg"] * limits.GRAVITY * (cx * np.cos(q) + cz * np.sin(q))
    inertia_error = float(np.max(np.abs(result["inertia"] / expected_m - 1)))
    gravity_error = float(np.max(np.abs(result["gravity"] - expected_g)))
    return [{"id": "stl-mass", "label": "実体積積分の正負校正", "pass": box["ok"], "detail": box},
            {"id": "rigid-orbit", "label": "既知の直方体の回転と重力の照合",
             "pass": inertia_error < 1e-4 and gravity_error < 1e-6,
             "detail": {"maximumRelativeInertiaError": inertia_error, "maximumGravityErrorNm": gravity_error}}]


def tables_for_case(model):
    directory = ROOT / "models" / model
    manifest = read(directory / "build" / "manifest.json")
    motion = read(directory / "build" / "motion.json")
    frames = motion["frames"]
    angles = np.array([frame["servo_deg"] for frame in frames])
    if len(angles) < 3 or not np.allclose(np.diff(angles), angles[1] - angles[0], atol=1e-7):
        raise ValueError(f"{model}: uniformly spaced motion with >=3 frames required")
    q = np.radians(angles)
    groups, values, masses = [], [], {}
    hashes = {str((directory / "build" / name).relative_to(ROOT)).replace("\\", "/"):
              digest(directory / "build" / name) for name in ("manifest.json", "motion.json")}
    for part in manifest["parts"]:
        pid = part["id"]
        matrices = np.array([np.array(frame["transforms"][pid]).reshape(4, 4, order="F") for frame in frames])
        if np.allclose(matrices, matrices[0], atol=1e-9, rtol=0):
            continue
        source = (directory / part["assembly"]).resolve()
        triangles = physics.read_stl(source)
        mass = physics.signed_tetra_properties(triangles, limits.PRINT_DENSITY_G_CM3 * 1000)
        if mass["signedVolumeMm3"] <= 0 or any(physics.edge_diagnostics(triangles)):
            raise ValueError(f"{pid}: mass requires closed, outward STL")
        hashes[source.relative_to(ROOT).as_posix()] = digest(source)
        masses[pid] = {**mass, "source": source.relative_to(ROOT).as_posix(),
                       "densityKgM3": limits.PRINT_DENSITY_G_CM3 * 1000,
                       "densityAssumption": "solid PLA equivalent, including purchased horn"}
        groups.append({"id": pid, "label": part.get("label", pid), "massKg": mass["massKg"]})
        values.append(rigid_properties(matrices, q, mass))
    if not groups:
        raise ValueError(f"{model}: no moving meshes")
    inertia = sum(value["inertia"] for value in values)
    gravity = sum(value["gravity"] for value in values)
    dinertia = np.gradient(inertia, q, edge_order=2)
    spec = read(directory / "spec.json")
    servo = spec["motion"]["servo"]
    ledger = read(ROOT / "lib" / "printmech" / "parts_ledger.json")
    stall = spec["motion"].get("stall_torque_nm") or ledger["parts"][servo]["stall_torque_nm"]
    rows = []
    for n, angle in enumerate(angles):
        rows.append({"servoDeg": float(angle), "inertiaRestKgm2": 0.0,
                     "inertiaGroupsKgm2": float(inertia[n]), "dMGroupsDqKgm2PerRad": float(dinertia[n]),
                     "gravityRestNm": 0.0, "gravityGroupsNm": float(gravity[n]),
                     "contactFrictionGroupsNm": 0.0,
                     "liftsMm": [float(value["z"][n] * 1000) for value in values],
                     "dLiftDqMPerRad": [float(value["dz"][n]) for value in values],
                     "d2LiftDq2MPerRad2": [float(value["ddz"][n]) for value in values]})
    tables = {"model": model, "limitsDeg": angles[[0, -1]].tolist(),
              "duration_s": motion["duration_s"], "groups": groups, "rows": rows,
              "contactModel": "gravity_one_sided", "contactBoundariesDeg": [],
              "const": {"stallTorqueNm": stall, "noLoadSpeedRadS": physics.NO_LOAD_SPEED,
                        "controlBandRad": physics.CONTROL_BAND, "motorInertiaKgm2": physics.MOTOR_INERTIA,
                        "servoFrictionNm": physics.SERVO_FRICTION, "gravityMS2": limits.GRAVITY,
                        "dtS": physics.DT, "recordS": physics.RECORD, "settleS": physics.SETTLE,
                        "contactToleranceN": 1e-8}}
    return tables, masses, hashes


def calculate_case(tables):
    """Prescribed 2s quintic inverse dynamics, plus the existing conditional servo model."""
    sim = physics.TableSim(tables)
    low, high = tables["limitsDeg"]
    peaks, runs = [], []
    for start, target in ((low, high), (high, low)):
        peak = 0.0
        for u in np.linspace(0, 1, 2001):
            angle = start + (target - start) * (10 * u**3 - 15 * u**4 + 6 * u**5)
            speed = math.radians(target - start) * (30 * u**2 - 60 * u**3 + 30 * u**4) / tables["duration_s"]
            accel = math.radians(target - start) * (60 * u - 180 * u**2 + 120 * u**3) / tables["duration_s"]**2
            state = sim.at(angle)
            torque = state["inertiaGroupsKgm2"] * accel + 0.5 * state["dMGroupsDqKgm2PerRad"] * speed**2 + state["gravityGroupsNm"]
            peak = max(peak, abs(torque))
        result = sim.run(from_deg=start, to_deg=target)
        # The generic contact reaction proxy assumes a free vertical carrier.
        # It is not a force/retention test of F1's four-bar or captured cam.
        runs.append({"fromDeg": start, "toDeg": target, "final": result["final"],
                     "trace": result["trace"], "peakMotorTorqueNm": result["peakTorqueNm"],
                     "reached": abs(result["final"]["servoDeg"] - target) < 1,
                     "contactAssessment": "not_applicable_to_constrained_linkage"})
        peaks.append(peak)
    peak = float(max(peaks))
    limit = tables["const"]["stallTorqueNm"] * limits.TORQUE_MAX_FRACTION
    finite = all(math.isfinite(v) for row in tables["rows"] for v in
                 [row["inertiaGroupsKgm2"], row["dMGroupsDqKgm2PerRad"], row["gravityGroupsNm"],
                  *row["liftsMm"], *row["dLiftDqMPerRad"], *row["d2LiftDq2MPerRad2"]])
    return {"pass": finite and peak <= limit and all(run["reached"] for run in runs),
            "finite": finite, "peakIdealTorqueNm": peak, "limitNm": limit,
            "stallFraction": peak / tables["const"]["stallTorqueNm"],
            "movingMassKg": sum(group["massKg"] for group in tables["groups"]),
            "limitsDeg": [low, high], "runs": runs}


def export():
    """Refresh even while gates are pending; failed/stale evidence keeps controls disabled."""
    from verify_contract import verify
    contract = verify(True)
    write(BUILD / "contract_report.json", contract)
    index = read(BUILD / "cases.json")
    composition_fresh, changes = dependency_status()
    all_evidence = {model: gate_evidence(model) for model in [MODEL] + index["models"]}
    geometry_pass = composition_fresh and contract["pass"] and all(e["geometryPass"] for e in all_evidence.values())
    calibration = calculation_calibration()
    case_results, tables_by_slot, hashes = {}, {}, {}
    interfaces, gate_calibration = [], []
    for model in index["models"]:
        slot = model.rsplit("/", 1)[-1]
        tables, masses, sources = tables_for_case(model)
        calculation = calculate_case(tables)
        tables_by_slot[slot] = tables
        hashes.update(sources)
        evidence = all_evidence[model]
        case_results[slot] = {"calculation": calculation, "massProperties": masses,
                              "gate": evidence, "sourceHashes": sources}
        write(BUILD / "lattice_cases" / slot / "sim_tables.json", tables)
        write(BUILD / "lattice_cases" / slot / "simulate_report.json", case_results[slot])
        drive = evidence["checks"].get("interface.drive", {})
        measured = {row["id"]: row for row in (drive.get("detail") or {}).get("all", [])}
        spec = read(ROOT / "models" / model / "spec.json")
        for item in spec["interfaces"]:
            if item["type"] != "drive":
                continue
            row = measured.get(item["id"], {})
            passed = evidence["fresh"] and row.get("pass") is True and composition_fresh
            interfaces.append({"id": item["id"], "label": item["id"],
                               "status": "pass" if passed else "fail",
                               "detail": f"{row.get('samples', 0)}姿勢。出典: {model} interface.drive。" +
                                         ("現入力と一致。" if passed else "未検査・不適合・入力更新のいずれか。"),
                               "measurement": row, "source": evidence["report"]})
        for check_id in ("instrument.calibration", "motion.interference", "interface.retention", "assembly.path"):
            check = evidence["checks"].get(check_id, {})
            gate_calibration.append({"id": slot + "/" + check_id, "label": LABELS.get(slot, slot) + " " + check_id,
                                     "pass": composition_fresh and evidence["fresh"] and check.get("pass") is True,
                                     "detail": check.get("summary", "未検査")})
        # This is an actual finite-difference + inverse-dynamics + reached-position check,
        # not a fabricated calibration verdict used merely to print a summary.
        calibration.append({"id": slot + "/calculation", "label": LABELS.get(slot, slot) + "の質量・駆動計算",
                            "pass": calculation["pass"],
                            "detail": f"可動部{calculation['movingMassKg'] * 1000:.3f}g。"
                                      f"{tables['limitsDeg'][0]:.3f}〜{tables['limitsDeg'][1]:.3f}°。"
                                      f"理想拘束での必要トルク最大{calculation['peakIdealTorqueNm'] * 1000:.3f}mN·m。"
                                      f"停動比{calculation['stallFraction'] * 100:.3f}%。"
                                      f"仮定したサーボモデルの往復到達{sum(r['reached'] for r in calculation['runs'])}/2。"
                                      "摩擦・保持力の保証ではありません。"})
    representative = index["representative"]
    representative_motion = read(HERE / "checks" / representative / "build" / "motion.json")
    if read(BUILD / "motion.json") != representative_motion:
        raise ValueError("root motion differs from the representative case used for physics")
    passed = geometry_pass and all(row["pass"] for row in calibration)
    assumptions = ["全可動STLを中実PLA密度1.24g/cm³で近似。付属ホーンの密度も同じ仮定。",
                   "体積・重心・慣性は実STLの四面体積分。変位のグラフは世界Zの重心高さ。",
                   "必要トルクは剛体・理想拘束の逆動力学。摩擦・圧入・ばね・弾性・衝撃を含まない。",
                   "再生は既存サーボモデルの仮定値（摩擦0.004N·m、制御幅4°、慣性5e-6kg·m²、60°/0.1秒）。実機未同定。",
                   "接触反力の定型表示は自由な鉛直従動子の代理値。F1のリンク・拘束カムの保持力判定には使わない。",
                   "各面を別々に動かす。他面は閉じたまま。同時駆動・実機適合・印刷スライスは未検証。"]
    drive = {"model": MODEL, "overall": {"geometryPass": geometry_pass}, "interfaces": interfaces,
             "calibration": gate_calibration, "hardwareUnknown": assumptions[2:], "sourceHashes": hashes}
    report = {"model": MODEL, "method": "STL tetrahedra + rigid transforms, second-order finite differences in radians",
              "equation": "tau = M(q)*qdd + 0.5*dM/dq*qd^2 + dV/dq",
              "representativeSlot": representative, "faceReports": case_results,
              "overall": {"pass": False, "calculationPass": passed, "status": "conditional" if passed else "pending_or_failed"},
              "driveGeometry": {"geometryPass": geometry_pass,
                                "sourceHashesFresh": composition_fresh and all(e["fresh"] for e in all_evidence.values())},
              "calibration": calibration, "assumptions": assumptions, "sourceHashes": hashes,
              "composition": {"fresh": composition_fresh, "changed": changes},
              "algorithmHashes": {path.relative_to(ROOT).as_posix(): digest(path) for path in
                                  (Path(__file__), ROOT / "tools/lattice_simulation.py", ROOT / "viewer/lattice/sim.mjs")},
              "contract": {"pass": contract["pass"], "checks": len(contract["checks"]),
                           "failing": [row for row in contract["checks"] if not row["pass"]]}}
    write(BUILD / "sim_tables.json", tables_by_slot[representative])
    write(BUILD / "simulate_report.json", report)
    write(BUILD / "drive_report.json", drive)
    write(BUILD / "boolean_evidence.json", {"model": MODEL, "geometryPass": geometry_pass, "gates": all_evidence})
    ui = read(BUILD / "ui.json")
    name = LABELS.get(representative, representative)
    ui["displayName"] = f"F1 {name}の代表計算（全体{len(index['models'])}サーボ）"
    ui["physics"].update({"title": name + "の代表計算・他面は保存結果を併記", "playback": "motion-frames",
                           "liftLabel": "重心Z", "chartLabel": "可動部の重心高さ", "chartAxis": "重心Z (mm)",
                           "massNote": assumptions[0] + assumptions[1],
                           "simLimits": f"操作対象は{name}の1台です。他の面は標準条件の保存結果です。" + " ".join(assumptions[2:])})
    available = {group["id"] for group in tables_by_slot[representative]["groups"]}
    series = [pid for pid in ui["physics"].get("chartSeries", []) if pid in available]
    ui["physics"]["chartSeries"] = series or [group["id"] for group in tables_by_slot[representative]["groups"][:5]]
    write(BUILD / "ui.json", ui)
    result = lattice_web.export(MODEL)
    print(f"Studio: {result}; geometry={geometry_pass}; calculation={passed}", flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-assembly", action="store_true")
    args = parser.parse_args()
    if args.prepare_assembly:
        print(f"assembly metadata changed: {prepare_assembly()}")
    else:
        export()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
