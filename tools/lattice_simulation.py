"""C3/C4 格子機構の 1 自由度物理表と検証レポートを生成する。

一般化座標は SG92R の指令角と同じサーボ角。質量、重心、慣性は組立 STL を
符号付き四面体へ分解して求める。ブラウザ版はこのファイルが出す表を補間し、
同じ積分式を使う。
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import sys
from typing import Callable, Iterable

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
G = 9.80665
PP_DENSITY = 900.0
MOTOR_INERTIA = 5.0e-6
SERVO_FRICTION = 0.004
NO_LOAD_SPEED = math.radians(60.0) / 0.1
CONTROL_BAND = math.radians(4.0)
DT = 5.0e-5
RECORD = 0.005
SETTLE = 0.5
TABLE_STEP_DEG = 0.25
DERIVATIVE_STEP_RAD = math.radians(0.02)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def read_stl(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    data = path.read_bytes()
    triangles = []
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if 84 + 50 * count == len(data):
            for index in range(count):
                values = struct.unpack_from("<12fH", data, 84 + index * 50)
                triangles.append((values[3:6], values[6:9], values[9:12]))
            return triangles
    vertices = []
    for raw in data.decode("utf-8", errors="strict").splitlines():
        fields = raw.strip().split()
        if fields[:1] == ["vertex"] and len(fields) == 4:
            vertices.append(tuple(float(v) for v in fields[1:]))
    if not vertices or len(vertices) % 3:
        raise ValueError(f"STL を読めない: {path}")
    return [tuple(vertices[i:i + 3]) for i in range(0, len(vertices), 3)]


def edge_diagnostics(triangles: Iterable[tuple[tuple[float, float, float], ...]]) -> tuple[int, int]:
    edges: dict[tuple[tuple[float, float, float], tuple[float, float, float]], int] = {}
    for triangle in triangles:
        for i, j in ((0, 1), (1, 2), (2, 0)):
            a, b = triangle[i], triangle[j]
            edge = (a, b) if a <= b else (b, a)
            edges[edge] = edges.get(edge, 0) + 1
    return sum(count == 1 for count in edges.values()), sum(count > 2 for count in edges.values())


def open_edge_count(triangles: Iterable[tuple[tuple[float, float, float], ...]]) -> int:
    return edge_diagnostics(triangles)[0]


def signed_tetra_properties(triangles, density: float) -> dict:
    """STL の mm 座標を m に直し、符号付き四面体積分で質量特性を返す。"""
    volume = sx = sy = sz = 0.0
    xx = yy = zz = xy = xz = yz = 0.0
    for triangle in triangles:
        a, b, c = [tuple(v * 1.0e-3 for v in point) for point in triangle]
        dv = dot(a, cross(b, c)) / 6.0
        volume += dv
        sx += dv * (a[0] + b[0] + c[0]) / 4.0
        sy += dv * (a[1] + b[1] + c[1]) / 4.0
        sz += dv * (a[2] + b[2] + c[2]) / 4.0
        xx += dv * (a[0] ** 2 + b[0] ** 2 + c[0] ** 2
                    + a[0] * b[0] + a[0] * c[0] + b[0] * c[0]) / 10.0
        yy += dv * (a[1] ** 2 + b[1] ** 2 + c[1] ** 2
                    + a[1] * b[1] + a[1] * c[1] + b[1] * c[1]) / 10.0
        zz += dv * (a[2] ** 2 + b[2] ** 2 + c[2] ** 2
                    + a[2] * b[2] + a[2] * c[2] + b[2] * c[2]) / 10.0
        xy += dv * (2 * (a[0] * a[1] + b[0] * b[1] + c[0] * c[1])
                    + a[0] * b[1] + a[1] * b[0]
                    + a[0] * c[1] + a[1] * c[0]
                    + b[0] * c[1] + b[1] * c[0]) / 20.0
        xz += dv * (2 * (a[0] * a[2] + b[0] * b[2] + c[0] * c[2])
                    + a[0] * b[2] + a[2] * b[0]
                    + a[0] * c[2] + a[2] * c[0]
                    + b[0] * c[2] + b[2] * c[0]) / 20.0
        yz += dv * (2 * (a[1] * a[2] + b[1] * b[2] + c[1] * c[2])
                    + a[1] * b[2] + a[2] * b[1]
                    + a[1] * c[2] + a[2] * c[1]
                    + b[1] * c[2] + b[2] * c[1]) / 20.0
    if abs(volume) < 1.0e-15:
        raise ValueError("STL の符号付き体積が 0")
    orientation = 1.0 if volume > 0 else -1.0
    signed_volume = volume
    volume *= orientation
    sx, sy, sz = sx * orientation, sy * orientation, sz * orientation
    xx, yy, zz = xx * orientation, yy * orientation, zz * orientation
    xy, xz, yz = xy * orientation, xz * orientation, yz * orientation
    com = (sx / volume, sy / volume, sz / volume)
    mass = density * volume
    ixx_origin = density * (yy + zz)
    iyy_origin = density * (xx + zz)
    izz_origin = density * (xx + yy)
    ixy_origin = -density * xy
    ixz_origin = -density * xz
    iyz_origin = -density * yz
    cx, cy, cz = com
    return {
        "signedVolumeMm3": signed_volume * 1.0e9,
        "volumeMm3": volume * 1.0e9,
        "orientation": "positive" if orientation > 0 else "negative",
        "massKg": mass,
        "comM": list(com),
        "inertiaComKgm2": [
            ixx_origin - mass * (cy * cy + cz * cz),
            iyy_origin - mass * (cx * cx + cz * cz),
            izz_origin - mass * (cx * cx + cy * cy),
            ixy_origin + mass * cx * cy,
            ixz_origin + mass * cx * cz,
            iyz_origin + mass * cy * cz,
        ],
    }


def box_triangles(size=(0.02, 0.03, 0.04)):
    x, y, z = (v * 1000.0 for v in size)
    v = [(0, 0, 0), (x, 0, 0), (x, y, 0), (0, y, 0),
         (0, 0, z), (x, 0, z), (x, y, z), (0, y, z)]
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
             (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
             (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    triangles = [tuple(v[index] for index in face) for face in faces]
    if signed_tetra_properties(triangles, 1.0)["signedVolumeMm3"] < 0:
        triangles = [(t[0], t[2], t[1]) for t in triangles]
    return triangles


def mass_calibration() -> dict:
    density = 1240.0
    size = (0.02, 0.03, 0.04)
    triangles = box_triangles(size)
    positive = signed_tetra_properties(triangles, density)
    negative = signed_tetra_properties([(t[0], t[2], t[1]) for t in triangles], density)
    opened = triangles[:-1]
    expected_volume = math.prod(size) * 1.0e9
    expected_mass = density * math.prod(size)
    expected_ixx = expected_mass * (size[1] ** 2 + size[2] ** 2) / 12.0
    checks = {
        "positiveVolume": abs(positive["signedVolumeMm3"] - expected_volume) < 1.0e-6,
        "negativeWindingDetected": negative["signedVolumeMm3"] < 0,
        "mass": abs(positive["massKg"] - expected_mass) < 1.0e-12,
        "centerOfMass": max(abs(a - b) for a, b in zip(positive["comM"], (0.01, 0.015, 0.02))) < 1.0e-12,
        "inertia": abs(positive["inertiaComKgm2"][0] - expected_ixx) < 1.0e-12,
        "openMeshRejected": open_edge_count(opened) > 0,
    }
    return {
        "ok": all(checks.values()),
        "method": "signed tetrahedral volume integration",
        "knownBoxMm": [20.0, 30.0, 40.0],
        "expectedVolumeMm3": expected_volume,
        "positiveSignedVolumeMm3": positive["signedVolumeMm3"],
        "reversedSignedVolumeMm3": negative["signedVolumeMm3"],
        "openMeshBadEdges": open_edge_count(opened),
        "checks": checks,
    }


def load_modules(model_dir: Path):
    params_name = f"lattice_params_{model_dir.name.replace('-', '_')}"
    params_spec = importlib.util.spec_from_file_location(params_name, model_dir / "params.py")
    params = importlib.util.module_from_spec(params_spec)
    assert params_spec.loader
    params_spec.loader.exec_module(params)
    previous = sys.modules.get("params")
    sys.modules["params"] = params
    try:
        motion_name = f"lattice_motion_{model_dir.name.replace('-', '_')}"
        motion_spec = importlib.util.spec_from_file_location(motion_name, model_dir / "motion.py")
        motion = importlib.util.module_from_spec(motion_spec)
        assert motion_spec.loader
        motion_spec.loader.exec_module(motion)
    finally:
        if previous is None:
            del sys.modules["params"]
        else:
            sys.modules["params"] = previous
    return params, motion


def derivative(function: Callable[[float], float], q: float, low: float, high: float, order=1) -> float:
    h = DERIVATIVE_STEP_RAD
    if order == 1:
        if q - h < low:
            return (function(q + h) - function(q)) / h
        if q + h > high:
            return (function(q) - function(q - h)) / h
        return (function(q + h) - function(q - h)) / (2.0 * h)
    if q - h < low:
        return (function(q + 2 * h) - 2 * function(q + h) + function(q)) / (h * h)
    if q + h > high:
        return (function(q) - 2 * function(q - h) + function(q - 2 * h)) / (h * h)
    return (function(q + h) - 2 * function(q) + function(q - h)) / (h * h)


def rounded(value: float) -> float:
    return float(f"{value:.12g}")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)


class TableSim:
    def __init__(self, tables: dict):
        self.tables = tables
        self.rows = tables["rows"]
        self.const = tables["const"]
        self.low, self.high = tables["limitsDeg"]
        self.step = self.rows[1]["servoDeg"] - self.rows[0]["servoDeg"]

    def at(self, deg: float) -> dict:
        deg = clamp(deg, self.low, self.high)
        f = clamp((deg - self.low) / self.step, 0.0, len(self.rows) - 1.000000001)
        index = min(int(f), len(self.rows) - 2)
        u = f - index
        a, b = self.rows[index], self.rows[index + 1]
        mix = lambda key: a[key] + (b[key] - a[key]) * u
        mix_array = lambda key: [x + (y - x) * u for x, y in zip(a[key], b[key])]
        lifts = mix_array("liftsMm")
        active = [True] * len(lifts) if self.tables["contactModel"] == "gravity_one_sided" else [v > 1.0e-7 for v in lifts]
        return {
            "servoDeg": deg,
            "inertiaRestKgm2": mix("inertiaRestKgm2"),
            "inertiaGroupsKgm2": mix("inertiaGroupsKgm2"),
            "dMGroupsDqKgm2PerRad": mix("dMGroupsDqKgm2PerRad"),
            "gravityRestNm": mix("gravityRestNm"),
            "gravityGroupsNm": mix("gravityGroupsNm"),
            "liftsMm": lifts,
            "dLiftDqMPerRad": mix_array("dLiftDqMPerRad"),
            "d2LiftDq2MPerRad2": mix_array("d2LiftDq2MPerRad2"),
            "contactActive": active,
        }

    def hold_torque(self, deg: float, mass_scale=1.0) -> float:
        state = self.at(deg)
        return state["gravityRestNm"] + state["gravityGroupsNm"] * clamp(mass_scale, 0.5, 4.0)

    def run(self, *, from_deg: float, to_deg: float, kind="ease", stall_scale=1.0,
            mass_scale=1.0, duration: float | None = None) -> dict:
        duration = self.tables["duration_s"] if duration is None else max(float(duration), self.const["dtS"])
        stall_scale = clamp(float(stall_scale), 0.0, 1.0)
        mass_scale = clamp(float(mass_scale), 0.5, 4.0)
        start = clamp(float(from_deg), self.low, self.high)
        target = clamp(float(to_deg), self.low, self.high)
        clipped = start != from_deg or target != to_deg
        q = math.radians(start)
        velocity = 0.0
        t = 0.0
        end_time = duration + self.const["settleS"]
        next_record = 0.0
        peak_torque = 0.0
        max_contact_speed = 0.0
        min_normal = float("inf")
        lift_off = set()
        trace = []
        previous_active = self.at(start)["contactActive"]
        last_tau = 0.0

        def command(now: float) -> float:
            if kind == "step":
                return target
            u = clamp(now / duration, 0.0, 1.0)
            u = u ** 3 * (10.0 + u * (-15.0 + 6.0 * u))
            return start + (target - start) * u

        def record(now: float, cmd: float, state: dict, torque: float):
            trace.append({
                "t": rounded(now),
                "commandDeg": rounded(cmd),
                "servoDeg": rounded(math.degrees(q)),
                "torqueNm": rounded(torque),
                "liftsMm": [rounded(v) for v in state["liftsMm"]],
            })

        state = self.at(start)
        record(0.0, command(0.0), state, 0.0)
        next_record = self.const["recordS"]
        while t < end_time - self.const["dtS"] * 0.5:
            state = self.at(math.degrees(q))
            cmd = command(t)
            mass = (self.const["motorInertiaKgm2"] + state["inertiaRestKgm2"]
                    + mass_scale * state["inertiaGroupsKgm2"])
            gravity = state["gravityRestNm"] + mass_scale * state["gravityGroupsNm"]
            dmass = mass_scale * state["dMGroupsDqKgm2PerRad"]
            stall = self.const["stallTorqueNm"] * stall_scale
            effort = clamp((math.radians(cmd) - q) / self.const["controlBandRad"], -1.0, 1.0)
            tau = clamp(stall * effort - stall / self.const["noLoadSpeedRadS"] * velocity, -stall, stall)
            net = tau - gravity - 0.5 * dmass * velocity * velocity
            friction = self.const["servoFrictionNm"]
            if abs(velocity) > 1.0e-4:
                net -= math.copysign(friction, velocity)
            elif abs(net) <= friction:
                net = 0.0
                velocity = 0.0
            else:
                net -= math.copysign(friction, net)
            acceleration = net / mass
            for index, active in enumerate(state["contactActive"]):
                if active:
                    carrier_mass = self.tables["groups"][index]["massKg"] * mass_scale
                    vertical_acceleration = (state["dLiftDqMPerRad"][index] * acceleration
                                             + state["d2LiftDq2MPerRad2"][index] * velocity * velocity)
                    normal = carrier_mass * (self.const["gravityMS2"] + vertical_acceleration)
                    min_normal = min(min_normal, normal)
                    if normal < -self.const["contactToleranceN"]:
                        lift_off.add(index)
                if active and not previous_active[index]:
                    speed = abs(state["dLiftDqMPerRad"][index] * velocity) * 1000.0
                    max_contact_speed = max(max_contact_speed, speed)
            previous_active = state["contactActive"]
            previous_q = q
            previous_velocity = velocity
            velocity += acceleration * self.const["dtS"]
            q += velocity * self.const["dtS"]
            if q < math.radians(self.low):
                q = math.radians(self.low)
                velocity = max(0.0, velocity)
            elif q > math.radians(self.high):
                q = math.radians(self.high)
                velocity = min(0.0, velocity)
            max_contact_speed = max(
                max_contact_speed,
                boundary_crossing_speed_mm_s(
                    math.degrees(previous_q), math.degrees(q), previous_velocity, velocity,
                    self.tables.get("contactBoundariesDeg", []),
                ),
            )
            t += self.const["dtS"]
            last_tau = tau
            peak_torque = max(peak_torque, abs(tau))
            if t + 1.0e-12 >= next_record:
                record(t, command(t), self.at(math.degrees(q)), tau)
                next_record += self.const["recordS"]
        final_state = self.at(math.degrees(q))
        if abs(trace[-1]["t"] - t) > self.const["dtS"]:
            record(t, command(t), final_state, last_tau)
        final = {
            "t": rounded(t),
            "commandDeg": rounded(command(t)),
            "servoDeg": rounded(math.degrees(q)),
            "torqueNm": rounded(last_tau),
            "liftsMm": [rounded(v) for v in final_state["liftsMm"]],
        }
        labels = [self.tables["groups"][index]["label"] for index in sorted(lift_off)]
        return {
            "trace": trace,
            "final": final,
            "peakTorqueNm": rounded(peak_torque),
            "maxContactSpeedMmS": rounded(max_contact_speed),
            "contactFeasible": not lift_off,
            "minNormalForceN": None if min_normal == float("inf") else rounded(min_normal),
            "possibleLiftOffGroups": labels,
            "clippedToLimits": clipped,
        }


def boundary_crossing_speed_mm_s(q0_deg: float, q1_deg: float, w0: float, w1: float,
                                 groups: list[list[dict]]) -> float:
    if q0_deg == q1_deg:
        return 0.0
    low, high = sorted((q0_deg, q1_deg))
    maximum = 0.0
    for boundaries in groups:
        for boundary in boundaries:
            deg = boundary["deg"]
            if low <= deg <= high:
                fraction = (deg - q0_deg) / (q1_deg - q0_deg)
                crossing_velocity = w0 + (w1 - w0) * fraction
                maximum = max(maximum, abs(boundary["slopeMPerRad"] * crossing_velocity) * 1000.0)
    return maximum


def synthetic_tables(gravity_nm=0.0, servo_friction=0.0, record=0.001) -> dict:
    row = lambda deg: {
        "servoDeg": deg, "inertiaRestKgm2": 0.0, "inertiaGroupsKgm2": 0.0,
        "dMGroupsDqKgm2PerRad": 0.0, "gravityRestNm": gravity_nm,
        "gravityGroupsNm": 0.0, "liftsMm": [0.0], "dLiftDqMPerRad": [0.0],
        "d2LiftDq2MPerRad2": [0.0],
    }
    return {
        "model": "calibration", "limitsDeg": [0.0, 60.0], "duration_s": 0.2,
        "contactModel": "gravity_one_sided", "groups": [{"label": "calibration", "massKg": 0.001}],
        "contactBoundariesDeg": [],
        "rows": [row(0.0), row(60.0)],
        "const": {
            "stallTorqueNm": 0.245, "noLoadSpeedRadS": NO_LOAD_SPEED,
            "controlBandRad": CONTROL_BAND, "motorInertiaKgm2": MOTOR_INERTIA,
            "servoFrictionNm": servo_friction, "gravityMS2": G, "dtS": DT,
            "recordS": record, "settleS": 0.1, "contactToleranceN": 1.0e-8,
        },
    }


def dynamic_calibration() -> dict:
    no_load = TableSim(synthetic_tables()).run(from_deg=0.0, to_deg=60.0, kind="step", duration=0.2)
    reached = next((row["t"] for row in no_load["trace"] if row["servoDeg"] >= 59.0), None)
    required = 0.05
    half_scale = (required * 0.5) / 0.245
    half = TableSim(synthetic_tables(gravity_nm=required)).run(
        from_deg=0.0, to_deg=60.0, kind="step", stall_scale=half_scale, duration=0.4)
    zero = TableSim(synthetic_tables()).run(
        from_deg=0.0, to_deg=60.0, kind="step", stall_scale=0.0, duration=0.2)
    boundary_speed = boundary_crossing_speed_mm_s(
        20.0, 40.0, 1.0, 3.0, [[{"deg": 30.0, "slopeMPerRad": 0.005}]],
    )
    checks = {
        "noLoadNominalSpeed": reached is not None and abs(reached - 0.1) <= 0.02,
        "halfStaticTorqueCannotReach": half["final"]["servoDeg"] < 1.0,
        "zeroTorqueCannotFollowTarget": abs(zero["final"]["servoDeg"]) < 1.0e-9,
        "syntheticBoundarySpeed": abs(boundary_speed - 10.0) < 1.0e-12,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "noLoad": {"nominal60DegS": 0.1, "timeToWithin1DegS": reached},
        "halfStaticSyntheticLoad": {
            "requiredTorqueNm": required, "availableTorqueNm": required * 0.5,
            "finalServoDeg": half["final"]["servoDeg"],
        },
        "zeroTorque": {"targetDeg": 60.0, "finalServoDeg": zero["final"]["servoDeg"]},
        "syntheticBoundary": {"expectedMmS": 10.0, "measuredMmS": boundary_speed},
    }


def model_definition(model: str) -> dict:
    model_dir = ROOT / "models" / model
    params, motion = load_modules(model_dir)
    manifest = json.loads((model_dir / "build" / "manifest.json").read_text(encoding="utf-8"))
    assembly = {part["id"]: model_dir / part["assembly"] for part in manifest["parts"] if part.get("assembly")}
    if model.endswith("c3"):
        carrier_names = [f"carrier_{i}" for i in range(params.GRID_N)]
        labels = [f"格子列 {i + 1}" for i in range(params.GRID_N)]
        rotating = [("drive_gear", -1.0, (params.SERVO_AXIS_Y, params.SERVO_AXIS_Z), params.PLA_DENSITY),
                    ("ref_horn", -1.0, (params.SERVO_AXIS_Y, params.SERVO_AXIS_Z), PP_DENSITY)]
        rotating += [(name, 1.0, (params.CAM_AXIS_Y, params.CAM_AXIS_Z), params.PLA_DENSITY)
                     for name in ["camshaft", "cam_gear"] + [f"cam_{i}" for i in range(params.GRID_N)]]
        limits = (params.SERVO_HOME_DEG, params.SERVO_END_DEG)
        duration = params.MOTION_DURATION_S
        lift = lambda i, deg: motion.carrier_height(i, deg)
        contact_model = "max_zero_cam_switch"
        boundary_angle = math.degrees(math.acos(0.4))
        contact_boundaries = []
        for phase in params.CAM_PHASE_DEG:
            group_boundaries = []
            for sign in (-1.0, 1.0):
                theta = sign * boundary_angle
                for turn in range(-2, 3):
                    theta_turn = theta + 360.0 * turn
                    deg = params.SERVO_HOME_DEG + phase - params.CAM_HOME_DEG + theta_turn
                    if limits[0] <= deg <= limits[1]:
                        slope = -params.CAM_E * math.sin(math.radians(theta_turn))
                        group_boundaries.append({"deg": rounded(deg), "slopeMPerRad": rounded(slope)})
            contact_boundaries.append(sorted(group_boundaries, key=lambda item: item["deg"]))
        approximation = "max(0, cam) の高さ拘束。負の反力後も拘束を維持して計算し、浮き上がり可能として別途不合格にする。"
    elif model.endswith("c4"):
        carrier_names = ["carrier_center", "carrier_inner", "carrier_outer"]
        labels = ["中心の格子", "内側の格子", "外側の格子"]
        rotating = [(name, 1.0, (0.0, params.CAM_AXIS_Z), params.PLA_DENSITY)
                    for name in ["camshaft", "horn_coupler", "cam_center", "cam_inner", "cam_outer"]]
        rotating.append(("servo_horn", 1.0, (0.0, params.CAM_AXIS_Z), PP_DENSITY))
        limits = (params.SERVO_MIN_DEG, params.SERVO_MAX_DEG)
        duration = params.MOVE_TIME_S
        lift = lambda i, deg: motion.lift_m(i, deg)
        contact_model = "gravity_one_sided"
        contact_boundaries = [[] for _ in carrier_names]
        approximation = "重力でカムへ追従する片側接触の高さ拘束。負の反力後も拘束を維持して計算し、浮き上がり可能として別途不合格にする。"
    else:
        raise ValueError(f"未対応モデル: {model}")
    return {
        "dir": model_dir, "params": params, "motion": motion, "assembly": assembly,
        "carrierNames": carrier_names, "labels": labels, "rotating": rotating,
        "limits": limits, "duration": duration, "lift": lift,
        "contactModel": contact_model, "approximation": approximation,
        "contactBoundaries": contact_boundaries,
    }


def generate_model(model: str, shared_calibration: dict) -> dict:
    definition = model_definition(model)
    model_dir = definition["dir"]
    params = definition["params"]
    mass: dict[str, dict] = {}
    used_names = definition["carrierNames"] + [item[0] for item in definition["rotating"]]
    hashes = {
        "params.py": sha256(model_dir / "params.py"),
        "motion.py": sha256(model_dir / "motion.py"),
    }
    algorithm_hashes = {
        "tools/lattice_simulation.py": sha256(ROOT / "tools" / "lattice_simulation.py"),
        "viewer/lattice/sim.mjs": sha256(ROOT / "viewer" / "lattice" / "sim.mjs"),
    }
    density_by_name = {name: density for name, _sign, _axis, density in definition["rotating"]}
    for name in used_names:
        path = definition["assembly"][name]
        triangles = read_stl(path)
        boundary_edges, nonmanifold_edges = edge_diagnostics(triangles)
        if boundary_edges:
            raise ValueError(f"{model}/{name}: 閉じていない STL ({boundary_edges} boundary edges)")
        density = density_by_name.get(name, params.PLA_DENSITY)
        properties = signed_tetra_properties(triangles, density)
        properties["densityKgM3"] = density
        properties["triangles"] = len(triangles)
        properties["boundaryEdges"] = boundary_edges
        properties["nonmanifoldEdges"] = nonmanifold_edges
        properties["sha256"] = sha256(path)
        mass[name] = properties
        hashes[str(path.relative_to(model_dir)).replace("\\", "/")] = properties["sha256"]

    low_deg, high_deg = definition["limits"]
    low, high = math.radians(low_deg), math.radians(high_deg)
    carrier_masses = [mass[name]["massKg"] for name in definition["carrierNames"]]

    rotating_inertia = 0.0
    rotating_terms = []
    for name, sign, axis, _density in definition["rotating"]:
        item = mass[name]
        cy, cz = item["comM"][1], item["comM"][2]
        ay, az = axis
        inertia_axis = item["inertiaComKgm2"][0] + item["massKg"] * ((cy - ay) ** 2 + (cz - az) ** 2)
        rotating_inertia += inertia_axis
        rotating_terms.append((item["massKg"], cy - ay, cz - az, sign))

    def lift_at(index: int, q: float) -> float:
        return definition["lift"](index, math.degrees(clamp(q, low, high)))

    def terms(q: float):
        delta = q - low
        lifts, slopes, curvatures = [], [], []
        group_inertia = 0.0
        gravity_groups = 0.0
        gravity_rest = 0.0
        dmass = 0.0
        for index, carrier_mass in enumerate(carrier_masses):
            function = lambda angle, i=index: lift_at(i, angle)
            height = function(q)
            slope = derivative(function, q, low, high, 1)
            curvature = derivative(function, q, low, high, 2)
            lifts.append(height)
            slopes.append(slope)
            curvatures.append(curvature)
            group_inertia += carrier_mass * slope * slope
            dmass += 2.0 * carrier_mass * slope * curvature
            gravity_groups += carrier_mass * G * slope
        for body_mass, y0, z0, sign in rotating_terms:
            angle = sign * delta
            dz_dq = sign * (y0 * math.cos(angle) - z0 * math.sin(angle))
            gravity_rest += body_mass * G * dz_dq
        return (rotating_inertia, group_inertia, dmass, gravity_rest, gravity_groups,
                lifts, slopes, curvatures)

    count = int(round((high_deg - low_deg) / TABLE_STEP_DEG))
    rows = []
    for index in range(count + 1):
        deg = low_deg + (high_deg - low_deg) * index / count
        values = terms(math.radians(deg))
        rows.append({
            "servoDeg": rounded(deg),
            "inertiaRestKgm2": rounded(values[0]),
            "inertiaGroupsKgm2": rounded(values[1]),
            "dMGroupsDqKgm2PerRad": rounded(values[2]),
            "gravityRestNm": rounded(values[3]),
            "gravityGroupsNm": rounded(values[4]),
            "liftsMm": [rounded(v * 1000.0) for v in values[5]],
            "dLiftDqMPerRad": [rounded(v) for v in values[6]],
            "d2LiftDq2MPerRad2": [rounded(v) for v in values[7]],
        })

    groups = [{"id": name, "label": label, "massKg": rounded(mass[name]["massKg"]),
               "mass_g": rounded(mass[name]["massKg"] * 1000.0),
               "sourceStl": f"build/{name}.stl"}
              for name, label in zip(definition["carrierNames"], definition["labels"])]
    tables = {
        "version": 1,
        "model": model,
        "limitsDeg": [low_deg, high_deg],
        "duration_s": definition["duration"],
        "groups": groups,
        "contactModel": definition["contactModel"],
        "contactBoundariesDeg": definition["contactBoundaries"],
        "columns": list(rows[0]),
        "rows": rows,
        "const": {
            "stallTorqueNm": params.SERVO_STALL_TORQUE,
            "noLoadSpeedRadS": NO_LOAD_SPEED,
            "controlBandRad": CONTROL_BAND,
            "motorInertiaKgm2": MOTOR_INERTIA,
            "servoFrictionNm": SERVO_FRICTION,
            "guideFrictionMu": getattr(params, "GUIDE_FRICTION_MU", getattr(params, "FRICTION_COEFF", 0.30)),
            "gravityMS2": G,
            "dtS": DT,
            "recordS": RECORD,
            "settleS": SETTLE,
            "contactToleranceN": 1.0e-8,
            "assumptions": {
                "printedParts": "組立 STL を中実 PLA として積分。massScale は格子キャリアの質量、慣性、重力項だけへ掛ける。回転部は固定。",
                "servoHorn": "組立 STL を中実 PP 900 kg/m3 として積分。",
                "motorInertia": "出力軸換算 5e-6 kg m2 の推定値。",
                "friction": "SG92R ギアの等価クーロン摩擦 0.004 N m を適用。案内の横予圧が不明なため μ=0.30 は記録のみで運動式へ加えない。",
                "contact": definition["approximation"],
                "collision": "この計算は motion.py の拘束運動を解く。実メッシュ衝突の動的証明ではない。",
            },
        },
        "massProperties": mass,
        "sourceHashes": hashes,
        "algorithmHashes": algorithm_hashes,
    }
    simulator = TableSim(tables)
    scenarios = {
        "standard": simulator.run(from_deg=low_deg, to_deg=high_deg, kind="ease"),
        "reverse": simulator.run(from_deg=high_deg, to_deg=low_deg, kind="ease"),
        "lowPower": simulator.run(from_deg=low_deg, to_deg=high_deg, kind="ease", stall_scale=0.30),
        "heavy": simulator.run(from_deg=low_deg, to_deg=high_deg, kind="ease", mass_scale=4.0),
        "fullSpeed": simulator.run(from_deg=low_deg, to_deg=high_deg, kind="step"),
    }
    fine_tables = copy.deepcopy(tables)
    fine_tables["const"]["dtS"] = tables["const"]["dtS"] / 2.0
    fine_standard = TableSim(fine_tables).run(from_deg=low_deg, to_deg=high_deg, kind="ease")
    standard = scenarios["standard"]
    if len(standard["trace"]) != len(fine_standard["trace"]):
        raise RuntimeError("dt convergence traces have different record counts")
    max_trace_servo = 0.0
    max_trace_torque = 0.0
    max_trace_lift = 0.0
    for coarse, fine in zip(standard["trace"], fine_standard["trace"]):
        max_trace_servo = max(max_trace_servo, abs(coarse["servoDeg"] - fine["servoDeg"]))
        max_trace_torque = max(max_trace_torque, abs(coarse["torqueNm"] - fine["torqueNm"]))
        max_trace_lift = max(max_trace_lift, max(abs(a - b) for a, b in zip(coarse["liftsMm"], fine["liftsMm"])))
    integration_differences = {
        "finalServoDeg": rounded(abs(standard["final"]["servoDeg"] - fine_standard["final"]["servoDeg"])),
        "maxTraceServoDeg": rounded(max_trace_servo),
        "maxTraceTorqueNm": rounded(max_trace_torque),
        "maxTraceLiftMm": rounded(max_trace_lift),
        "peakTorqueNm": rounded(abs(standard["peakTorqueNm"] - fine_standard["peakTorqueNm"])),
        "maxContactSpeedMmS": rounded(abs(standard["maxContactSpeedMmS"] - fine_standard["maxContactSpeedMmS"])),
    }
    integration_upper_bounds = {key: rounded(value * 2.0) for key, value in integration_differences.items()}
    max_static = max(abs(row["gravityRestNm"] + row["gravityGroupsNm"]) for row in rows)
    calibration_rows = [
        {
            "id": "signed-mass",
            "label": "符号付き四面体積分",
            "pass": shared_calibration["mass"]["ok"],
            "detail": (f"20×30×40 mm 箱 {shared_calibration['mass']['positiveSignedVolumeMm3']:.3f} mm3。"
                       f"反転 {shared_calibration['mass']['reversedSignedVolumeMm3']:.3f} mm3。"
                       f"開いたメッシュの開いた辺 {shared_calibration['mass']['openMeshBadEdges']}。"),
        },
        {
            "id": "no-load-speed",
            "label": "無負荷の公称速度",
            "pass": shared_calibration["dynamic"]["checks"]["noLoadNominalSpeed"],
            "detail": f"60° の 1°以内へ {shared_calibration['dynamic']['noLoad']['timeToWithin1DegS']:.3f} s（公称 0.100 s）。",
        },
        {
            "id": "half-static-load",
            "label": "必要静荷重の半分",
            "pass": shared_calibration["dynamic"]["checks"]["halfStaticTorqueCannotReach"],
            "detail": f"0.050 N m に 0.025 N m だけを与え、最終 {shared_calibration['dynamic']['halfStaticSyntheticLoad']['finalServoDeg']:.3f}°。",
        },
        {
            "id": "zero-torque",
            "label": "トルク 0",
            "pass": shared_calibration["dynamic"]["checks"]["zeroTorqueCannotFollowTarget"],
            "detail": f"60° 指令に対し最終 {shared_calibration['dynamic']['zeroTorque']['finalServoDeg']:.3f}°。",
        },
        {
            "id": "contact-boundary-speed",
            "label": "接触境界の横断速度",
            "pass": shared_calibration["dynamic"]["checks"]["syntheticBoundarySpeed"],
            "detail": (f"20→40°、速度1→3 rad/s、30°境界、傾き0.005 m/radで "
                       f"{shared_calibration['dynamic']['syntheticBoundary']['measuredMmS']:.3f} mm/s（期待10.000）。"),
        },
    ]
    overall_pass = (all(row["pass"] for row in calibration_rows)
                    and max_static <= params.SERVO_STALL_TORQUE / 3.0
                    and scenarios["standard"]["contactFeasible"]
                    and scenarios["reverse"]["contactFeasible"])
    report = {
        "version": 1,
        "model": model,
        "method": "SG92R torque-speed limited one-DOF Lagrange simulation",
        "equation": "M(q) qdd + 0.5 dM/dq qdot^2 + G(q) = servoTorque - coulombFriction",
        "limitsDeg": tables["limitsDeg"],
        "massIntegration": {
            "method": "signed tetrahedral volume integration of assembly STL",
            "calibration": shared_calibration["mass"],
            "parts": mass,
        },
        "dynamicCalibration": shared_calibration["dynamic"],
        "calibration": calibration_rows,
        "overall": {
            "pass": overall_pass,
            "basis": "計器校正、1/3停動トルク、標準往復の非負接触反力",
        },
        "static": {
            "maxHoldTorqueNm": rounded(max_static),
            "fractionOfStall": rounded(max_static / params.SERVO_STALL_TORQUE),
            "withinOneThirdStall": max_static <= params.SERVO_STALL_TORQUE / 3.0,
        },
        "integrationConvergence": {
            "dtS": tables["const"]["dtS"],
            "halfDtS": fine_tables["const"]["dtS"],
            "observedAbsoluteDifference": integration_differences,
            "reportedUpperBound": integration_upper_bounds,
            "basis": "半陰解法を一次精度として、dt と dt/2 の差の2倍を保守的な上限として報告。",
        },
        "scenarios": scenarios,
        "assumptions": tables["const"]["assumptions"],
        "sourceHashes": hashes,
        "algorithmHashes": algorithm_hashes,
        "limitations": [
            definition["approximation"],
            "負の反力が出た後の自由飛行と再衝突は解いていない。contactFeasible=false は浮き上がり可能の判定。",
            "実メッシュの動的衝突は証明しない。形状干渉は verify_report.json の別検査。",
        ],
    }
    write_json(model_dir / "build" / "sim_tables.json", tables)
    write_json(model_dir / "build" / "simulate_report.json", report)
    return {
        "model": model,
        "maxStaticNm": max_static,
        "massKg": sum(item["massKg"] for item in mass.values()),
        "scenario": {name: {key: value[key] for key in ("peakTorqueNm", "maxContactSpeedMmS", "contactFeasible")}
                     for name, value in scenarios.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("models", nargs="*", default=["mystery-box-sg92r-c3", "mystery-box-sg92r-c4"])
    args = parser.parse_args()
    calibration = {"mass": mass_calibration(), "dynamic": dynamic_calibration()}
    if not calibration["mass"]["ok"] or not calibration["dynamic"]["ok"]:
        raise SystemExit(f"calibration failed: {calibration}")
    for model in args.models:
        print(json.dumps(generate_model(model, calibration), ensure_ascii=False))


if __name__ == "__main__":
    main()
