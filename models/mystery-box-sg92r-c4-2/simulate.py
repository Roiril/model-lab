"""C4-2 の Z 回転円盤と4キャリアを条件付き1自由度で検証する。"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))

import motion as M  # noqa: E402
import params as P  # noqa: E402
import lattice_simulation as common  # noqa: E402

MODEL = P.MODEL_ID
BUILD = HERE / "build"
GROUP_PARTS = tuple(f"carrier_{name}" for name in P.GROUPS)
ROTATING_PARTS = ("cam_disk", "horn_coupler", "drive_key", "servo_horn")
ALL_PARTS = GROUP_PARTS + ROTATING_PARTS
PP_DENSITY = 900.0
TABLE_STEP_DEG = 0.05
DERIVATIVE_STEP_RAD = math.radians(0.02)
GUIDE_ANGLE_MAX_DEG = 30.0
SUPPORT_RADIUS_M = P.CAM_OUTER_R - P.CAM_TRACK_W / 2.0


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rounded(value: float) -> float:
    return float(f"{value:.12g}")


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def source_hashes(extra_paths=()) -> dict:
    paths = [HERE / "params.py", HERE / "motion.py", HERE / "contact_envelope.py",
             Path(__file__),
             ROOT / "tools/lattice_simulation.py", ROOT / "viewer/lattice/sim.mjs",
             *extra_paths]
    return {path.relative_to(ROOT).as_posix(): digest(path) for path in paths if path.is_file()}


def load_mass_properties() -> tuple[dict, list[str], dict]:
    properties = {}
    missing = []
    paths = []
    for part in ALL_PARTS:
        path = BUILD / f"{part}.stl"
        if not path.is_file():
            missing.append(path.relative_to(ROOT).as_posix())
            continue
        triangles = common.read_stl(path)
        boundary, nonmanifold = common.edge_diagnostics(triangles)
        if boundary or nonmanifold:
            raise ValueError(f"{part}: closed STL required; boundary={boundary}, nonmanifold={nonmanifold}")
        density = PP_DENSITY if part == "servo_horn" else P.PLA_DENSITY
        row = common.signed_tetra_properties(triangles, density)
        row.update({"densityKgM3": density, "triangles": len(triangles),
                    "boundaryEdges": boundary, "nonmanifoldEdges": nonmanifold,
                    "sha256": digest(path)})
        properties[part] = row
        paths.append(path)
    return properties, missing, source_hashes(paths)


def lift(group: int, q_rad: float) -> float:
    return M.lift_m(group, math.degrees(q_rad))


def lift_derivatives(group: int, q_rad: float) -> tuple[float, float, float]:
    h = DERIVATIVE_STEP_RAD
    value = lift(group, q_rad)
    lower = lift(group, q_rad - h)
    upper = lift(group, q_rad + h)
    return value, (upper - lower) / (2.0 * h), (upper - 2.0 * value + lower) / (h * h)


def generalized_group_mass(carrier_masses: list[float], q_rad: float) -> float:
    return sum(mass * lift_derivatives(index, q_rad)[1] ** 2
               for index, mass in enumerate(carrier_masses))


def contact_boundaries() -> list[list[dict]]:
    groups = []
    for index, selected in enumerate(P.SELECT_DEG):
        rows = []
        for delta in (-P.DENT_HALF_WIDTH_DEG, -P.DENT_DWELL_DEG,
                      P.DENT_DWELL_DEG, P.DENT_HALF_WIDTH_DEG):
            degree = selected + delta
            slope = lift_derivatives(index, math.radians(degree))[1]
            rows.append({"deg": rounded(degree), "slopeMPerRad": rounded(slope)})
        groups.append(rows)
    return groups


def build_tables(mass: dict, hashes: dict) -> dict:
    carrier_masses = [mass[name]["massKg"] for name in GROUP_PARTS]
    rotating_inertia = 0.0
    for name in ROTATING_PARTS:
        row = mass[name]
        cx, cy, _cz = row["comM"]
        rotating_inertia += row["inertiaComKgm2"][2] + row["massKg"] * (cx * cx + cy * cy)

    guide_ratio = P.GUIDE_FRICTION_MU * math.tan(math.radians(GUIDE_ANGLE_MAX_DEG))
    guide_amplification = 1.0 / (1.0 - guide_ratio)
    track_friction = P.GUIDE_FRICTION_MU * P.GRAVITY * sum(
        mass_value * radius for mass_value, radius in zip(carrier_masses, P.CAM_RADII))
    guide_friction = track_friction * (guide_amplification - 1.0)
    carrier_thrust_friction = (P.GUIDE_FRICTION_MU * P.GRAVITY
                               * sum(carrier_masses) * SUPPORT_RADIUS_M)
    radial_bearing_radius = float(getattr(P, "CAM_RADIAL_BEARING_R", 0.0))
    radial_bearing_friction = (P.GUIDE_FRICTION_MU
                               * math.tan(math.radians(GUIDE_ANGLE_MAX_DEG))
                               * sum(carrier_masses) * P.GRAVITY
                               * radial_bearing_radius)
    disk_thrust_friction = (P.GUIDE_FRICTION_MU * P.GRAVITY
                            * mass["cam_disk"]["massKg"] * SUPPORT_RADIUS_M)
    contact_friction = (track_friction + guide_friction + carrier_thrust_friction
                        + radial_bearing_friction)

    count = round((P.SERVO_MAX_DEG - P.SERVO_MIN_DEG) / TABLE_STEP_DEG)
    rows = []
    for step in range(count + 1):
        degree = P.SERVO_MIN_DEG + step * TABLE_STEP_DEG
        q = math.radians(degree)
        values = [lift_derivatives(index, q) for index in range(len(P.GROUPS))]
        group_mass = generalized_group_mass(carrier_masses, q)
        h = DERIVATIVE_STEP_RAD
        dmass = (generalized_group_mass(carrier_masses, q + h)
                 - generalized_group_mass(carrier_masses, q - h)) / (2.0 * h)
        gravity = sum(mass_value * P.GRAVITY * value[1]
                      for mass_value, value in zip(carrier_masses, values))
        rows.append({
            "servoDeg": rounded(degree),
            "inertiaRestKgm2": rounded(rotating_inertia),
            "inertiaGroupsKgm2": rounded(group_mass),
            "dMGroupsDqKgm2PerRad": rounded(dmass),
            "gravityRestNm": 0.0,
            "gravityGroupsNm": rounded(gravity),
            "liftsMm": [rounded(value[0] * 1000.0) for value in values],
            "dLiftDqMPerRad": [rounded(value[1]) for value in values],
            "d2LiftDq2MPerRad2": [rounded(value[2]) for value in values],
            "contactHeightsM": [rounded(radius) for radius in P.CAM_RADII],
            "contactFrictionGroupsNm": rounded(contact_friction),
        })
    groups = [{"id": part, "label": label, "massKg": rounded(mass[part]["massKg"]),
               "mass_g": rounded(mass[part]["massKg"] * 1000.0),
               "sourceStl": f"build/{part}.stl"}
              for part, label in zip(GROUP_PARTS, P.GROUP_LABELS)]
    return {
        "version": 1, "model": MODEL,
        "limitsDeg": [P.SERVO_MIN_DEG, P.SERVO_MAX_DEG],
        "duration_s": P.MOVE_TIME_S, "groups": groups,
        "contactModel": "gravity_one_sided",
        "contactBoundariesDeg": contact_boundaries(),
        "columns": list(rows[0]), "rows": rows,
        "const": {
            "stallTorqueNm": P.SERVO_STALL_TORQUE,
            "noLoadSpeedRadS": common.NO_LOAD_SPEED,
            "controlBandRad": common.CONTROL_BAND,
            "motorInertiaKgm2": common.MOTOR_INERTIA,
            "servoFrictionNm": rounded(common.SERVO_FRICTION + disk_thrust_friction),
            "servoEquivalentFrictionNm": common.SERVO_FRICTION,
            "camFrictionMu": P.GUIDE_FRICTION_MU,
            "guideFrictionMu": P.GUIDE_FRICTION_MU,
            "guideAngleMaximumDeg": GUIDE_ANGLE_MAX_DEG,
            "guideMuTanAlpha": rounded(guide_ratio),
            "guideFrictionAmplification": rounded(guide_amplification),
            "trackFrictionNm": rounded(track_friction),
            "guideFrictionEstimateNm": rounded(guide_friction),
            "outerCarrierThrustFrictionNm": rounded(carrier_thrust_friction),
            "radialBearingCarrierFrictionNm": rounded(radial_bearing_friction),
            "radialBearingRadiusM": rounded(radial_bearing_radius),
            "radialBearingAdopted": radial_bearing_radius > 0,
            "outerDiskThrustFrictionNm": rounded(disk_thrust_friction),
            "outerThrustSupportRadiusM": rounded(SUPPORT_RADIUS_M),
            "gravityMS2": P.GRAVITY, "dtS": common.DT,
            "recordS": common.RECORD, "settleS": common.SETTLE,
            "contactToleranceN": 1.0e-8,
            "assumptions": {
                "printedParts": "組立STLを中実PLA 1240 kg/m3として積分。massScaleは4キャリアだけへ掛ける。",
                "servoHorn": "付属ホーンSTLを中実PP 900 kg/m3として積分。",
                "rotation": "cam_disk、horn_coupler、drive_key、servo_hornはZ軸回転。Izz+m(cx^2+cy^2)を使い、Z不変のため重力項は0。",
                "friction": "各平面従動子はμmgR_i。案内横荷重はαmax=30°の1/(1-μtanα)で接点摩擦へ加算。円盤外周はキャリア重量と円盤重量を分けてμmgR_support。中央径方向保持を採用した場合はμtan30°Σm_carrier g R_bossも加算する。横予圧と材料係数は実機未確認。",
                "contact": "4キャリアは重力で各円盤トラックへ追従する片側接触。負の反力は不成立。",
                "collision": "motion.pyの拘束運動。実メッシュの動的衝突は別検査。",
            },
        },
        "massProperties": mass, "sourceHashes": hashes,
        "algorithmHashes": {
            "models/mystery-box-sg92r-c4-2/simulate.py": digest(Path(__file__)),
            "tools/lattice_simulation.py": digest(ROOT / "tools/lattice_simulation.py"),
            "viewer/lattice/sim.mjs": digest(ROOT / "viewer/lattice/sim.mjs"),
        },
    }


def drive_state() -> tuple[dict, dict | None]:
    path = BUILD / "drive_report.json"
    if not path.is_file():
        return ({"geometryPass": False, "sourceHashesFresh": False,
                 "reason": "build/drive_report.json が未生成。", "staleSources": [],
                 "driveReportSha256": None}, None)
    report = json.loads(path.read_text(encoding="utf-8"))
    stale = []
    recorded_hashes = report.get("sourceHashes", {})
    for relative, expected in recorded_hashes.items():
        lexical = Path(relative)
        if lexical.is_absolute() or ".." in lexical.parts:
            stale.append(relative)
            continue
        source = ROOT / lexical
        if not source.is_file() or digest(source) != expected:
            stale.append(relative)
    geometry = report.get("overall", {}).get("geometryPass") is True
    fresh = bool(recorded_hashes) and not stale
    interfaces = report.get("interfaces", [])
    interfaces_acceptable = bool(interfaces) and all(
        row.get("status") in {"pass", "unknown"} for row in interfaces)
    geometry_pass = report.get("model") == MODEL and geometry and fresh and interfaces_acceptable
    return ({"geometryPass": geometry_pass, "sourceHashesFresh": fresh,
             "reason": ("接続形状は確認済み。" if geometry_pass else
                        "drive_reportのgeometryPassまたはsource SHAが未成立。"),
             "staleSources": stale, "driveReportSha256": digest(path)}, report)


def measured_contact_error(report: dict) -> tuple[float, list[dict]]:
    sources = []
    for row in report.get("interfaces", []):
        if row.get("status") != "pass":
            continue
        try:
            value = common.maximum_contact_angle(row, samples=bool(row.get("samples")))
        except ValueError:
            continue
        sources.append({"id": row.get("id"), "maximumOneSidedContactAngleDeg": rounded(value)})
    if not sources:
        raise ValueError("drive report has no measured contact angles")
    return sum(row["maximumOneSidedContactAngleDeg"] for row in sources), sources


def clearance_envelope(report: dict) -> dict:
    error, sources = measured_contact_error(report)
    degrees = {P.SERVO_MIN_DEG, P.SERVO_MAX_DEG, *(row[2] for row in P.PATTERNS)}
    cursor = P.SERVO_MIN_DEG
    while cursor < P.SERVO_MAX_DEG:
        degrees.add(cursor)
        cursor += 2.5
    groups = []
    for index, (name, label) in enumerate(zip(P.GROUPS, P.GROUP_LABELS)):
        samples = []
        for degree in sorted(degrees):
            count = max(2, math.ceil(2.0 * error / 0.1))
            candidates = [degree - error + 2.0 * error * step / count
                          for step in range(count + 1)] if error else [degree]
            heights = [M.lift_m(index, candidate) * 1000.0 for candidate in candidates]
            samples.append({"servoDeg": rounded(degree),
                            "nominalHeightMm": rounded(M.lift_m(index, degree) * 1000.0),
                            "heightRangeMm": [rounded(min(heights)), rounded(max(heights))]})
        groups.append({"id": f"carrier_{name}", "label": label,
                       "nominalPhaseDeg": P.SELECT_DEG[index],
                       "maximumPhaseDifferenceDeg": rounded(error),
                       "sources": sources, "samples": samples})
    return {"version": 1, "model": MODEL, "available": True, "coefficient": 1.0,
            "symmetricPhaseDifference": True, "sampleStepMaximumDeg": 2.5,
            "groups": groups,
            "patternStops": [{"id": identifier, "servoDeg": degree,
                              "nominalHeightsMm": [rounded(M.lift_m(i, degree) * 1000.0)
                                                   for i in range(len(P.GROUPS))]}
                             for identifier, _label, degree in P.PATTERNS]}


def compare_dt(tables: dict, standard: dict) -> dict:
    fine = copy.deepcopy(tables)
    fine["const"]["dtS"] /= 2.0
    result = common.TableSim(fine).run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MAX_DEG,
                                       kind="ease")
    if len(standard["trace"]) != len(result["trace"]):
        raise RuntimeError("dt and dt/2 trace lengths differ")
    differences = {
        "finalServoDeg": abs(standard["final"]["servoDeg"] - result["final"]["servoDeg"]),
        "maxTraceServoDeg": max(abs(a["servoDeg"] - b["servoDeg"])
                                for a, b in zip(standard["trace"], result["trace"])),
        "maxTraceTorqueNm": max(abs(a["torqueNm"] - b["torqueNm"])
                                 for a, b in zip(standard["trace"], result["trace"])),
        "maxTraceLiftMm": max(abs(x - y) for a, b in zip(standard["trace"], result["trace"])
                              for x, y in zip(a["liftsMm"], b["liftsMm"])),
        "peakTorqueNm": abs(standard["peakTorqueNm"] - result["peakTorqueNm"]),
        "maxContactSpeedMmS": abs(standard["maxContactSpeedMmS"] - result["maxContactSpeedMmS"]),
    }
    return {"dtS": tables["const"]["dtS"], "halfDtS": fine["const"]["dtS"],
            "observedAbsoluteDifference": {key: rounded(value) for key, value in differences.items()},
            "reportedUpperBound": {key: rounded(2.0 * value) for key, value in differences.items()},
            "basis": "半陰解法のdtとdt/2を同じ記録時刻で比較。差の2倍を保守上限とする。"}


def scenarios(tables: dict) -> tuple[dict, dict]:
    sim = common.TableSim(tables)
    standard = sim.run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MAX_DEG, kind="ease")
    reverse = sim.run(from_deg=P.SERVO_MAX_DEG, to_deg=P.SERVO_MIN_DEG, kind="ease")
    rows = tables["rows"]
    required = max(abs(row["gravityGroupsNm"]) + row["contactFrictionGroupsNm"]
                   + tables["const"]["servoFrictionNm"] for row in rows)
    half_scale = min(1.0, 0.5 * required / P.SERVO_STALL_TORQUE)
    results = {
        "standard": standard,
        "reverse": reverse,
        "lowPower": sim.run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MAX_DEG,
                            kind="ease", stall_scale=0.30),
        "heavy": sim.run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MAX_DEG,
                         kind="ease", mass_scale=4.0),
        "fullSpeed": sim.run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MAX_DEG, kind="step"),
        "zeroTorque": sim.run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MAX_DEG,
                              kind="ease", stall_scale=0.0),
        "halfRequired": sim.run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MAX_DEG,
                                kind="ease", stall_scale=half_scale),
    }
    stop_runs = []
    for identifier, label, degree in P.PATTERNS:
        forward = sim.run(from_deg=P.SERVO_MIN_DEG, to_deg=degree, kind="ease")
        backward = sim.run(from_deg=degree, to_deg=P.SERVO_MIN_DEG, kind="ease")
        forward_error = abs(forward["final"]["servoDeg"] - degree)
        reverse_error = abs(backward["final"]["servoDeg"] - P.SERVO_MIN_DEG)
        stop_runs.append({"id": identifier, "label": label, "servoDeg": degree,
                          "forwardFinal": forward["final"],
                          "reverseFinal": backward["final"],
                          "forwardErrorDeg": rounded(forward_error),
                          "reverseErrorDeg": rounded(reverse_error),
                          "forwardReached": forward_error <= 1.0,
                          "reverseReached": reverse_error <= 1.0,
                          "forwardContactFeasible": forward["contactFeasible"],
                          "reverseContactFeasible": backward["contactFeasible"],
                          "forwardMinimumNormalN": forward["minNormalForceN"],
                          "reverseMinimumNormalN": backward["minNormalForceN"]})
    negative = {"requiredTorqueNm": rounded(required), "halfAvailableTorqueNm": rounded(required / 2.0),
                "halfRequiredFinalServoDeg": results["halfRequired"]["final"]["servoDeg"],
                "halfRequiredFails": results["halfRequired"]["final"]["servoDeg"] < P.SERVO_MAX_DEG - 1.0,
                "zeroTorqueFinalServoDeg": results["zeroTorque"]["final"]["servoDeg"],
                "zeroTorqueFails": results["zeroTorque"]["final"]["servoDeg"] < P.SERVO_MAX_DEG - 1.0,
                "patternStopRuns": stop_runs}
    return results, negative


def failure_report(missing: list[str], hashes: dict, drive: dict) -> dict:
    return {"version": 1, "model": MODEL,
            "method": "SG92R torque-speed limited one-DOF Lagrange simulation",
            "massIntegration": {"method": "signed tetrahedral volume integration of assembly STL",
                                "calibration": common.mass_calibration(), "parts": {},
                                "missing": missing},
            "calibration": [], "overall": {"pass": False, "calculationPass": False,
                                              "status": "fail", "geometryPass": False,
                                              "basis": "必要な実STLまたはdrive geometry proofが未生成。"},
            "driveGeometry": drive,
            "clearanceEnvelope": {"version": 1, "model": MODEL, "available": False,
                                  "reason": drive["reason"]},
            "scenarios": {}, "sourceHashes": hashes,
            "algorithmHashes": {key: value for key, value in hashes.items()
                                if key.endswith("simulate.py") or key.startswith("tools/")
                                or key.startswith("viewer/")},
            "limitations": ["本体STLまたは駆動形状証拠の生成後に再実行する。",
                            "スプライン嵌合、摩擦係数、材料は実機未確認。"]}


def generate() -> dict:
    mass, missing, hashes = load_mass_properties()
    drive, drive_report = drive_state()
    drive_path = BUILD / "drive_report.json"
    if drive_path.is_file():
        hashes[drive_path.relative_to(ROOT).as_posix()] = digest(drive_path)
    if missing or not drive["geometryPass"]:
        report = failure_report(missing, hashes, drive)
        atomic_json(BUILD / "simulate_report.json", report)
        return {"model": MODEL, "pass": False, "missing": missing, "driveGeometry": drive}

    tables = build_tables(mass, hashes)
    scenario_rows, negative = scenarios(tables)
    convergence = compare_dt(tables, scenario_rows["standard"])
    envelope = clearance_envelope(drive_report)
    envelope["source"] = {
        "path": "models/mystery-box-sg92r-c4-2/build/drive_report.json",
        "sha256": drive["driveReportSha256"],
    }
    max_hold = max(abs(row["gravityGroupsNm"]) for row in tables["rows"])
    max_static = max(abs(row["gravityGroupsNm"]) + row["contactFrictionGroupsNm"]
                     + tables["const"]["servoFrictionNm"] for row in tables["rows"])
    peak_low_speed = max(scenario_rows[name]["peakTorqueNm"] for name in ("standard", "reverse"))
    stop_contact = all(row[direction] for row in negative["patternStopRuns"]
                       for direction in ("forwardContactFeasible", "reverseContactFeasible"))
    stop_reached = all(row[direction] for row in negative["patternStopRuns"]
                       for direction in ("forwardReached", "reverseReached"))
    guide_pass = tables["const"]["guideMuTanAlpha"] < 1.0
    calibration = [
        {"id": "signed-mass", "label": "符号付き四面体積分",
         "pass": common.mass_calibration()["ok"], "detail": common.mass_calibration()},
        {"id": "dynamic-negative", "label": "力不足の負例",
         "pass": negative["halfRequiredFails"] and negative["zeroTorqueFails"], "detail": negative},
        {"id": "guide-angle", "label": "案内横荷重の保守係数", "pass": guide_pass,
         "detail": {"alphaMaximumDeg": GUIDE_ANGLE_MAX_DEG,
                    "muTanAlpha": tables["const"]["guideMuTanAlpha"],
                    "amplification": tables["const"]["guideFrictionAmplification"]}},
    ]
    calculation = (all(row["pass"] for row in calibration)
                   and max_static <= P.SERVO_STALL_TORQUE / 3.0
                   and peak_low_speed <= P.SERVO_STALL_TORQUE / 3.0
                   and scenario_rows["standard"]["contactFeasible"]
                   and scenario_rows["reverse"]["contactFeasible"] and stop_contact and stop_reached
                   and all(value >= -1.0e-12 for row in tables["rows"] for value in row["contactHeightsM"]))
    report = {
        "version": 1, "model": MODEL,
        "method": "SG92R torque-speed limited one-DOF Lagrange simulation",
        "equation": "M(q) qdd + 0.5 dM/dq qdot^2 + G(q) = servoTorque - servoFriction - contactFriction",
        "limitsDeg": tables["limitsDeg"],
        "massIntegration": {"method": "signed tetrahedral volume integration of assembly STL",
                            "calibration": common.mass_calibration(), "parts": mass},
        "dynamicCalibration": common.dynamic_calibration(), "calibration": calibration,
        "overall": {"pass": False, "calculationPass": calculation,
                    "status": "conditional" if calculation else "fail",
                    "geometryPass": drive["geometryPass"],
                    "basis": ("接続形状確認済み。スプライン嵌合と材料は実機未確認。"
                              if calculation else "条件付き1自由度計算の成立条件を満たさない。"),
                    "calculationBasis": "実STL質量、1/3停動トルク、全停止角往復の非負接触反力"},
        "driveGeometry": drive, "clearanceEnvelope": envelope,
        "static": {"maxHoldTorqueNm": rounded(max_hold),
                   "maximumRequiredTorqueNm": rounded(max_static),
                   "fractionOfStall": rounded(max_static / P.SERVO_STALL_TORQUE),
                   "withinOneThirdStall": max_static <= P.SERVO_STALL_TORQUE / 3.0,
                   "peakLowSpeedTorqueNm": rounded(peak_low_speed),
                   "peakWithinOneThirdStall": peak_low_speed <= P.SERVO_STALL_TORQUE / 3.0,
                   "radialBearingCarrierFrictionNm":
                       tables["const"]["radialBearingCarrierFrictionNm"],
                   "radialBearingRadiusM": tables["const"]["radialBearingRadiusM"],
                   "radialBearingAdopted": tables["const"]["radialBearingAdopted"]},
        "integrationConvergence": convergence, "scenarios": scenario_rows,
        "patternStopContact": negative["patternStopRuns"],
        "directControllerAngles": negative["patternStopRuns"],
        "assumptions": tables["const"]["assumptions"], "sourceHashes": hashes,
        "algorithmHashes": tables["algorithmHashes"],
        "limitations": ["横予圧と乾燥PLAの摩擦係数0.30は仮値。",
                        "付属ホーンのスプライン嵌合と材料特性は実機未確認。",
                        "実メッシュの動的衝突はverifyの別検査。"]}
    atomic_json(BUILD / "sim_tables.json", tables)
    atomic_json(BUILD / "simulate_report.json", report)
    return {"model": MODEL, "calculationPass": calculation, "maxStaticNm": rounded(max_static),
            "peakLowSpeedNm": rounded(peak_low_speed), "contactAtPatternStops": stop_contact}


def probe() -> dict:
    mass = {}
    for index, part in enumerate(GROUP_PARTS):
        mass[part] = {"massKg": 0.008 + index * 0.001, "comM": [0.0, 0.0, 0.06],
                      "inertiaComKgm2": [1e-6, 1e-6, 1e-6, 0, 0, 0]}
    for index, part in enumerate(ROTATING_PARTS):
        mass[part] = {"massKg": 0.004, "comM": [0.005 * index, 0.002, 0.045],
                      "inertiaComKgm2": [1e-6, 1e-6, 2e-6, 0, 0, 0]}
    tables = build_tables(mass, source_hashes())
    simulator = common.TableSim(tables)
    samples = [15.0, 37.125, 50.0, 90.0, 130.0, 165.0]
    required = max(abs(row["gravityGroupsNm"]) + row["contactFrictionGroupsNm"]
                   + tables["const"]["servoFrictionNm"] for row in tables["rows"])
    half_scale = min(1.0, 0.5 * required / P.SERVO_STALL_TORQUE)
    runs = {"standard": simulator.run(from_deg=15, to_deg=165, kind="ease"),
            "reverse": simulator.run(from_deg=165, to_deg=15, kind="ease"),
            "zeroTorque": simulator.run(from_deg=15, to_deg=165, kind="ease", stall_scale=0.0),
            "halfRequired": simulator.run(from_deg=15, to_deg=165, kind="ease",
                                             stall_scale=half_scale)}
    return {"tables": tables, "samples": [{"degree": value, "state": simulator.at(value)}
                                            for value in samples], "runs": runs,
            "negative": {"requiredTorqueNm": rounded(required),
                         "halfRequiredStallScale": rounded(half_scale)},
            "convergence": compare_dt(tables, runs["standard"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-json", action="store_true")
    args = parser.parse_args()
    result = probe() if args.probe_json else generate()
    print(json.dumps(result, ensure_ascii=False))
    if not args.probe_json and not result.get("calculationPass", result.get("pass", False)):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
