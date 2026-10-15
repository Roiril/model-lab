"""STL三角形を深さ境界で切り、製造余裕込みの面占有領域を検査する。

連続範囲は契約の剛体補間に対する上界。元の非線形機構の連続証明とは区別する。
"""
from __future__ import annotations

import math
import struct
import sys

import numpy as np

from compose import (C, HERE, ROOT, SLOTS, checked_transforms, common_params,
                     face_package, load_configuration, read)

SAMPLE_STEP_DEG = 0.1


def read_triangles(path):
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError(f"truncated binary STL: {path}")
    count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + count * 50:
        raise ValueError(f"binary STL size mismatch: {path}")
    dtype = np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")])
    triangles = np.frombuffer(data, dtype=dtype, offset=84, count=count)["vertices"].astype(float)
    if not np.isfinite(triangles).all():
        raise ValueError(f"nonfinite STL: {path}")
    return triangles


def transform_triangles(triangles, matrix):
    return triangles @ matrix[:3, :3].T + matrix[:3, 3]


def interpolate_rigid(start, end, fraction):
    """The same screw interpolation as tools/mechgate_lib/bl_job.py."""
    screw = C.screw(end @ np.linalg.inv(start))
    amount = screw["angle_deg"] if screw["angle_deg"] > 0 else screw["slide_mm"]
    return C.screw_motion(screw)(fraction * amount) @ start


def sweep_bound(triangles, start, end):
    """Arc length plus axial slide bounds every point along this rigid interpolant."""
    screw = C.screw(end @ np.linalg.inv(start))
    if screw["angle_deg"] < 1e-8:
        return float(np.linalg.norm(end[:3, 3] - start[:3, 3]))
    points = transform_triangles(triangles, start).reshape(-1, 3)
    relative = points - screw["pivot"]
    radial = relative - np.outer(relative @ screw["axis"], screw["axis"])
    radius = float(np.linalg.norm(radial, axis=1).max())
    return math.radians(screw["angle_deg"]) * radius + abs(float(screw["slide_mm"]))


def dense_case(interface, face, motion, common):
    """Evaluate true kinematics at <=0.1deg and separately subdivide its saved contract."""
    modules = face_package(face["config"]["module"], motion["slot"])
    inverse = np.linalg.inv(face["S"])
    saved = motion["frames"]
    angles, actual, interpolated = [], [], []
    for first, last in zip(saved[:-1], saved[1:]):
        count = max(1, math.ceil((last["servo_deg"] - first["servo_deg"]) / SAMPLE_STEP_DEG))
        first_local = {part: inverse @ C.from_column_major(matrix) @ face["S"]
                       for part, matrix in first["transforms"].items() if part.startswith(motion["slot"] + "/")}
        last_local = {part: inverse @ C.from_column_major(matrix) @ face["S"]
                      for part, matrix in last["transforms"].items() if part.startswith(motion["slot"] + "/")}
        for index in range(count):
            fraction = index / count
            angle = first["servo_deg"] + fraction * (last["servo_deg"] - first["servo_deg"])
            angles.append(float(angle))
            actual.append(checked_transforms(modules["kinematics"], angle, interface, common, face["meta"]["parts"]))
            interpolated.append({part.split("/", 1)[1]: interpolate_rigid(first_local[part], last_local[part], fraction)
                                 for part in first_local})
    angle = float(saved[-1]["servo_deg"])
    angles.append(angle)
    actual.append(checked_transforms(modules["kinematics"], angle, interface, common, face["meta"]["parts"]))
    interpolated.append({part.split("/", 1)[1]: inverse @ C.from_column_major(matrix) @ face["S"]
                         for part, matrix in saved[-1]["transforms"].items() if part.startswith(motion["slot"] + "/")})
    return {"angles": angles, "actual": actual, "interpolated": interpolated}


def clip_depth(polygon, depth, lower):
    if not len(polygon):
        return []
    result = []
    for start, end in zip(polygon, list(polygon[1:]) + [polygon[0]]):
        a = start[2] >= depth - 1e-9 if lower else start[2] <= depth + 1e-9
        b = end[2] >= depth - 1e-9 if lower else end[2] <= depth + 1e-9
        if a:
            result.append(start)
        if a != b:
            result.append(start + (end - start) * ((depth - start[2]) / (end[2] - start[2])))
    return result


def envelope_violation(triangles, interface, margin, cosmetic=False):
    slabs = interface["internal_envelope"]
    external = interface["external_envelope"]
    boundaries = [external["d_mm"][0], external["d_mm"][1]]
    boundaries += [d for slab in slabs for d in slab["d_mm"]]
    cuts = sorted(set(d + offset for d in boundaries for offset in (-margin, 0, margin)))
    # Accept a triangle only when its entire inflated AABB lies in one box.
    # Boundary-crossing triangles continue through the exact polygon clipping below.
    low = triangles.min(axis=1)
    high = triangles.max(axis=1)
    accepted = np.zeros(len(triangles), dtype=bool)
    for slab in slabs:
        half = np.asarray(slab["size_uv_mm"], dtype=float) / 2
        accepted |= ((low[:, 2] - margin >= slab["d_mm"][0] - 1e-9)
                     & (high[:, 2] + margin <= slab["d_mm"][1] + 1e-9)
                     & np.all(low[:, :2] - margin >= -half - 1e-9, axis=1)
                     & np.all(high[:, :2] + margin <= half + 1e-9, axis=1))
    accepted |= ((low[:, 2] - margin >= external["d_mm"][0] - 1e-9)
                 & (high[:, 2] + margin <= external["d_mm"][1] + 1e-9)
                 & (low[:, 0] - margin >= external["u_mm"][0] - 1e-9)
                 & (high[:, 0] + margin <= external["u_mm"][1] + 1e-9)
                 & (low[:, 1] - margin >= external["v_mm"][0] - 1e-9)
                 & (high[:, 1] + margin <= external["v_mm"][1] + 1e-9))
    if cosmetic:
        half = np.asarray(slabs[0]["size_uv_mm"], dtype=float) / 2
        accepted |= ((low[:, 2] >= -1e-6) & (high[:, 2] <= 3 + 1e-6)
                     & np.all(low[:, :2] >= -half - 1e-9, axis=1)
                     & np.all(high[:, :2] <= half + 1e-9, axis=1))
    worst = 0.0
    witness = None
    for triangle in triangles[~accepted]:
        lo, hi = float(triangle[:, 2].min()), float(triangle[:, 2].max())
        partition = sorted(set([lo, hi] + [d for d in cuts if lo < d < hi]))
        if len(partition) == 1:
            partition.append(partition[0])
        for start, end in zip(partition[:-1], partition[1:]):
            polygon = clip_depth(list(triangle), start, True)
            polygon = clip_depth(polygon, end, False)
            if not polygon:
                continue
            points = np.asarray(polygon)
            # The fixed panel datum is nominal, as explicitly specified by envelope_policy.
            datum = cosmetic and start >= -1e-6 and end <= 3 + 1e-6
            allowance = 0.0 if datum else margin
            d0, d1 = start - allowance, end + allowance
            half = []
            if d0 < 0 and d1 > external["d_mm"][0]:
                half.append(np.array([external["u_mm"][1], external["v_mm"][1]], dtype=float))
            for slab in slabs:
                if d0 < slab["d_mm"][1] - 1e-9 and d1 > slab["d_mm"][0] + 1e-9:
                    half.append(np.asarray(slab["size_uv_mm"], dtype=float) / 2)
            # At a zero-thickness face choose a box containing that depth.
            if not half:
                for slab in slabs:
                    if slab["d_mm"][0] <= d0 <= slab["d_mm"][1]:
                        half.append(np.asarray(slab["size_uv_mm"], dtype=float) / 2)
            overflow = max(external["d_mm"][0] - d0, d1 - slabs[-1]["d_mm"][1], 0)
            if half:
                permitted = np.min(half, axis=0)
                overflow = max(overflow, float(np.max(np.abs(points[:, :2]) + allowance - permitted)))
            else:
                overflow = max(overflow, 1.0)
            if overflow > worst:
                worst = overflow
                witness = {"triangle_mm": triangle.tolist(), "slab_d_mm": [start, end],
                           "inflation_mm": allowance, "cosmetic_datum": datum}
    return max(0.0, worst), witness


def selftest():
    interface = {"internal_envelope": [{"d_mm": [0, 10], "size_uv_mm": [10, 10]},
                                       {"d_mm": [10, 20], "size_uv_mm": [6, 6]}],
                 "external_envelope": {"u_mm": [-5, 5], "v_mm": [-5, 5], "d_mm": [-10, 0]}}
    inside = np.array([[[0, 0, 2], [2, 0, 2], [0, 2, 2]]], dtype=float)
    outside = np.array([[[0, 0, 12], [4, 0, 12], [0, 2, 12]]], dtype=float)
    crossing = np.array([[[4.9, 0, 9.9], [0, 0, 12], [0, 2, 9.9]]], dtype=float)
    start = np.eye(4)
    end = C.rotation((0, 0, 1), 0.1, (100, 0, 0))
    radial_triangle = np.array([[[102, 0, 0], [100, 2, 0], [100, 0, 0]]], dtype=float)
    bound = sweep_bound(radial_triangle, start, end)
    midpoint = interpolate_rigid(start, end, 0.5)
    midpoint_motion = transform_triangles(radial_triangle, midpoint) - radial_triangle
    return (envelope_violation(inside, interface, 0.25)[0] == 0
            and envelope_violation(outside, interface, 0.25)[0] > 0
            and envelope_violation(crossing, interface, 0.25)[0] > 0
            and np.isclose(bound, math.radians(0.1) * 2, atol=1e-9)
            and np.linalg.norm(midpoint_motion.reshape(-1, 3), axis=1).max() <= bound)


def verify():
    interface, _, faces = load_configuration()
    manifest = read(HERE / "build" / "manifest.json")
    case_models = read(HERE / "build" / "cases.json")["models"]
    motions = [read(ROOT / "models" / name / "build" / "motion.json") for name in case_models]
    common = common_params()
    dense = {motion["slot"]: dense_case(interface, faces[motion["slot"]], motion, common) for motion in motions}
    rows = []
    margin = float(interface["manufacturing_tolerance_mm"])
    for part in manifest["parts"]:
        slot, local = part["id"].split("/", 1)
        if slot not in SLOTS:
            continue
        inverse = np.linalg.inv(faces[slot]["S"])
        assembled = read_triangles(HERE / part["assembly"])
        triangles = transform_triangles(assembled, inverse)
        case = dense.get(slot, {"angles": [0.0], "actual": [{local: np.eye(4)}], "interpolated": [{local: np.eye(4)}]})
        angles = case["angles"]
        actual_matrices = [frame[local] for frame in case["actual"]]
        local_matrices = [frame[local] for frame in case["interpolated"]]
        static = all(np.allclose(m, np.eye(4), atol=1e-8) for m in actual_matrices + local_matrices)
        cosmetic = static and local in ("panel", "key_l", "key_r")
        worst, witness, worst_angle = 0.0, None, None
        sampled_worst = 0.0
        sampled_witness = None
        swept_bound = 0.0
        sampled_residual = 0.0
        indices = [0] if static else range(len(local_matrices))
        for index in indices:
            matrix = local_matrices[index]
            delta = 0.0
            if index + 1 < len(local_matrices):
                delta = sweep_bound(triangles, matrix, local_matrices[index + 1])
            swept_bound = max(swept_bound, delta)
            contract_triangles = transform_triangles(triangles, matrix)
            actual_triangles = transform_triangles(triangles, actual_matrices[index])
            sampled_residual = max(sampled_residual, float(np.linalg.norm(
                (contract_triangles - actual_triangles).reshape(-1, 3), axis=1).max()))
            # Full local-subinterval arc expansion covers the saved contract, including its endpoints.
            overflow, detail = envelope_violation(contract_triangles, interface, margin + delta, cosmetic=cosmetic)
            sampled, sampled_detail = envelope_violation(actual_triangles, interface, margin, cosmetic=cosmetic)
            if sampled > sampled_worst:
                sampled_worst, sampled_witness = sampled, sampled_detail
            if overflow > worst:
                worst, witness, worst_angle = overflow, detail, angles[index]
            if sampled > worst:
                worst, witness, worst_angle = sampled, sampled_detail, angles[index]
        rows.append({"part": part["id"], "pass": worst <= 1e-5, "max_excess_mm": worst,
                     "servo_deg": worst_angle, "max_between_sample_displacement_mm": swept_bound,
                     "manufacturing_margin_mm": margin, "nominal_cosmetic_datum": cosmetic,
                     "sample_count": len(angles), "max_sample_step_deg": max(np.diff(angles), default=0.0),
                     "max_nonlinear_sample_residual_mm": sampled_residual,
                     "sampled_manufacturing_excess_mm": sampled_worst,
                     "sampled_manufacturing_witness": sampled_witness,
                     "witness": witness})
    aperture = float(interface["aperture_mm"][0])
    panel_inflated = float(interface["panel_mm"][0]) + 2 * margin
    calibration = selftest()
    return {"pass": calibration and all(row["pass"] for row in rows) and panel_inflated <= aperture,
            "calibration": {"pass": calibration, "inside_accepted_outside_and_boundary_crossing_rejected": calibration},
            "parts": rows, "panel_inflated_mm": panel_inflated, "aperture_mm": aperture,
            "coverage": "全STL三角形を深さ境界で分割。実運動学を0.1°以下で標本化。保存契約は同じ刻みに剛体分割し、軸からの実半径による円弧長と軸移動の上界を製造余裕へ加算。",
            "max_kinematic_sample_step_deg": SAMPLE_STEP_DEG,
            "saved_contract_continuously_bounded": True,
            "not_proven": ["元の非線形運動学のサンプル間は、補間からの偏差の独立上界が未測定。",
                           "フレーム受けとの実メッシュ干渉はmechgateのmotion.interferenceとassembly.pathで判定。",
                           "配線の変形と実物材料のばらつきは試し刷りと実機で確認。"],
            "arbitrary_simultaneous_motion_proven": False}


def main():
    try:
        report = verify()
    except (ValueError, KeyError, FileNotFoundError) as error:
        print(f"FAIL envelopes: {error}")
        return 1
    C.write_json(HERE / "build" / "envelope_report.json", report)
    for row in report["parts"]:
        if not row["pass"]:
            print(f"FAIL {row['part']}: excess={row['max_excess_mm']:.6f}mm at {row['servo_deg']}deg")
    print(f"envelopes: {sum(r['pass'] for r in report['parts'])}/{len(report['parts'])} parts; "
          f"calibration={'pass' if report['calibration']['pass'] else 'fail'}; nonlinear continuous proof=pending")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
