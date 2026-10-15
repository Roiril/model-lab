"""resident-face-v2 の独立した面を合成する。形状と契約の長さは mm。"""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import types

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = HERE.name
sys.path.insert(0, str(ROOT / "lib"))
from printmech import contract as C

SLOTS = ("front", "right", "back", "left", "top", "bottom")
FACE_FILES = ("module.json", "params.py", "geometry.py", "kinematics.py", "assembly.py", "trials.py")
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_-]*$")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def rigid(matrix, label="matrix"):
    m = np.asarray(matrix, dtype=float)
    if (m.shape != (4, 4) or not np.isfinite(m).all()
            or not np.allclose(m[3], (0, 0, 0, 1), atol=1e-8)
            or not np.allclose(m[:3, :3].T @ m[:3, :3], np.eye(3), atol=1e-8)
            or not np.isclose(np.linalg.det(m[:3, :3]), 1, atol=1e-8)):
        raise ValueError(f"{label}: finite right-handed rigid 4x4 required")
    return m


def slot_matrix(interface, slot):
    value = interface["slot_transforms_mm"][slot]
    if isinstance(value, dict):
        value = value["matrix"]
    return rigid(value, f"slot {slot}")


def world_transform(slot, local):
    return slot @ rigid(local) @ np.linalg.inv(slot)


def qualify(slot, local_id):
    if not isinstance(local_id, str) or not IDENTIFIER.fullmatch(local_id):
        raise ValueError(f"invalid local part id: {local_id!r}")
    return f"{slot}/{local_id}"


def validate_face_sources(directory):
    """面から他面・骨格・ルート params への依存を受け入れない。"""
    own_modules = {p.stem for p in directory.glob("*.py")}
    for source in directory.glob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8-sig"), filename=str(source))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level > 1:
                    raise ValueError(f"{source.name}: imports outside face package")
                module = (node.module or "").split(".")[0]
                if node.level == 0 and module in own_modules | {"frame", "compose", "faces"}:
                    raise ValueError(f"{source.name}: face imports must be relative: {module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in own_modules | {"frame", "compose", "faces"}:
                        raise ValueError(f"{source.name}: forbidden shared face import: {alias.name}")


def load_file(name, path, package=False):
    spec = importlib.util.spec_from_file_location(
        name, path, submodule_search_locations=[str(Path(path).parent)] if package else None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def face_package(name, slot, with_geometry=False):
    directory = HERE / "faces" / name
    validate_face_sources(directory)
    namespace = f"_resident_{MODEL.replace('-', '_')}_{slot}_{name}"
    # A synthetic package works without writing an __init__.py into an independent face.
    package = types.ModuleType(namespace)
    package.__path__ = [str(directory)]
    package.__package__ = namespace
    sys.modules[namespace] = package
    names = ["params", "kinematics", "assembly"]
    if with_geometry:
        names += ["geometry", "trials"]
    modules = {}
    for item in names:
        modules[item] = load_file(f"{namespace}.{item}", directory / f"{item}.py")
        setattr(package, item, modules[item])
    return modules


def motion_range(motion, calibration_deg=0):
    angles = []
    for key in ("closed_servo_deg", "open_servo_deg", "assembly_servo_deg"):
        angle = motion.get(key)
        if isinstance(angle, bool) or not isinstance(angle, (int, float)) or not math.isfinite(angle):
            raise ValueError(f"invalid motion.{key}")
        if not 0 <= angle <= 180:
            raise ValueError("physical servo range outside 0..180")
        angles.append(angle)
    if "range_servo_deg" in motion:
        bounds = motion["range_servo_deg"]
        if (not isinstance(bounds, list) or len(bounds) != 2
                or any(isinstance(value, bool) or not isinstance(value, (int, float))
                       or not math.isfinite(value) for value in bounds)):
            raise ValueError("motion.range_servo_deg must be exactly two finite numbers")
        low, high = bounds
        if not 0 <= low < high <= 180:
            raise ValueError("motion.range_servo_deg must satisfy 0 <= low < high <= 180")
        if any(not low <= angle <= high for angle in angles):
            raise ValueError("motion.range_servo_deg must include closed, open and assembly commands")
    else:
        low, high = sorted(angles[:2])
    if (isinstance(calibration_deg, bool) or not isinstance(calibration_deg, (int, float))
            or not math.isfinite(calibration_deg)):
        raise ValueError("finite calibration_deg required")
    if not 0 <= low + calibration_deg <= high + calibration_deg <= 180:
        raise ValueError("calibrated command outside servo range")
    return low, high


def load_configuration(configuration=None, interface=None):
    interface = read(HERE / "interface.json") if interface is None else copy.deepcopy(interface)
    configuration = read(HERE / "slots.json") if configuration is None else copy.deepcopy(configuration)
    version = interface.get("interface", interface.get("id"))
    if version != "resident-face-v2" or configuration.get("interface") != version:
        raise ValueError("resident-face-v2 interface version required")
    if set(configuration.get("slots", {})) != set(SLOTS):
        raise ValueError("exactly six named slots required")
    loaded = {}
    for slot in SLOTS:
        row = configuration["slots"][slot]
        name = row.get("module", "")
        if not IDENTIFIER.fullmatch(name) or name == "template":
            raise ValueError(f"{slot}: invalid or unfinished module {name!r}")
        if row.get("rotation_deg") != 0:
            raise ValueError(f"{slot}: asymmetric locating keys permit rotation_deg=0 only")
        calibration = row.get("calibration_deg", 0)
        if isinstance(calibration, bool) or not isinstance(calibration, (int, float)) or not math.isfinite(calibration):
            raise ValueError(f"{slot}: finite calibration_deg required")
        directory = HERE / "faces" / name
        for filename in FACE_FILES:
            if not (directory / filename).is_file():
                raise ValueError(f"{slot}: missing {filename} in module {name}")
        metadata = read(directory / "module.json")
        if metadata.get("interface") != version or metadata.get("module") != name:
            raise ValueError(f"{slot}: module identity or interface mismatch")
        if slot not in metadata.get("supported_slots", []):
            raise ValueError(f"{slot}: unsupported module {name}")
        mass_limit = metadata.get("mass_limit_g")
        if not isinstance(mass_limit, (int, float)) or not math.isfinite(mass_limit) or mass_limit <= 0:
            raise ValueError(f"{slot}: mass_limit_g must be a finite positive number")
        ids = metadata.get("parts", [])
        if not ids or len(set(ids)) != len(ids):
            raise ValueError(f"{slot}: part ids missing or duplicate")
        for part_id in ids:
            qualify(slot, part_id)
        motion = metadata.get("motion")
        if slot == "bottom" and motion:
            raise ValueError("bottom is an inspection panel; active modules forbidden")
        if motion:
            for key in ("actuator", "servo"):
                if motion.get(key) not in ids:
                    raise ValueError(f"{slot}: motion.{key} absent from parts")
            for key in ("step_deg", "duration_s"):
                if (isinstance(motion.get(key), bool) or not isinstance(motion.get(key), (int, float))
                        or not math.isfinite(motion[key])):
                    raise ValueError(f"{slot}: invalid motion.{key}")
            if not 0 < motion["step_deg"] <= 1 or motion["duration_s"] <= 0:
                raise ValueError(f"{slot}: invalid motion sampling or duration")
            motion_range(motion, calibration)
        loaded[slot] = {"config": row, "meta": metadata, "S": slot_matrix(interface, slot)}
    return interface, configuration, loaded


def common_params():
    return load_file("_resident_common_params", HERE / "params.py")


def checked_transforms(module, angle, interface, common, ids):
    transforms = module.transforms(float(angle), interface, common)
    if set(transforms) != set(ids):
        raise ValueError(f"kinematics must return every part exactly once: {set(transforms) ^ set(ids)}")
    return {key: rigid(value, key) for key, value in transforms.items()}


def sample_angles(motion):
    low, high = motion_range(motion)
    count = max(1, math.ceil((high - low) / motion["step_deg"]))
    return np.linspace(low, high, count + 1)


def retention_poses(kinematics, motion, interface, common):
    low, high = motion_range(motion)
    provider = getattr(kinematics, "retention_poses", None)
    if provider is not None and not callable(provider):
        raise ValueError("retention_poses must be callable")
    poses = provider(interface, common) if callable(provider) else [
        {"id": "mid", "label": "サーボ範囲の中間", "servo_deg":
         (low + high) / 2},
        {"id": "open", "label": "開端", "servo_deg": motion["open_servo_deg"]}]
    if (not isinstance(poses, list) or len(poses) != 2 or not all(isinstance(p, dict) for p in poses)
            or {p.get("id") for p in poses} != {"mid", "open"}):
        raise ValueError("retention_poses must provide exactly mid and open")
    for pose in poses:
        angle = pose.get("servo_deg")
        if isinstance(angle, bool) or not isinstance(angle, (int, float)) or not math.isfinite(angle) or not low <= angle <= high:
            raise ValueError(f"invalid retention pose angle: {pose}")
        if not isinstance(pose.get("label"), str) or not pose["label"]:
            raise ValueError("retention pose label required")
        if pose["id"] == "mid" and not low < angle < high:
            raise ValueError("retention mid pose must be inside the servo range")
        if pose["id"] == "open" and not math.isclose(angle, motion["open_servo_deg"], rel_tol=0, abs_tol=1e-8):
            raise ValueError("retention open pose must match the physical open command")
    return poses


def prefixed_document(value, slot, ids, trial_directory=None):
    """Only typed part/step identifiers are rewritten; prose and ledger ids stay intact."""
    result = copy.deepcopy(value)
    for key in ("id", "driver", "driven", "actuator", "servo", "part"):
        if key in result:
            result[key] = qualify(slot, result[key])
    for key in ("parts", "moving", "jigs", "against"):
        if key in result:
            result[key] = [qualify(slot, item) for item in result[key]]
    if "direction" in result:
        result["direction"] = (ids["S"][:3, :3] @ np.asarray(result["direction"], dtype=float)).tolist()
    if "pairs" in result:
        result["pairs"] = [[qualify(slot, p) for p in pair] for pair in result["pairs"]]
    for key in ("steps", "assembly_steps"):
        if key in result:
            result[key] = [f"{slot}/{item}" for item in result[key]]
    if "step" in result:
        result["step"] = f"{slot}/{result['step']}"
    return result


def compose_spec(base, faces, representative, frame_meta=None):
    spec = copy.deepcopy(base)
    spec["model"] = MODEL
    spec["uses"] = sorted(set(base.get("uses", [])) | {u for f in faces.values() for u in f["meta"].get("uses", [])})
    spec["interfaces"] = []
    spec["allowances"] = []
    unknowns = {}
    for slot, face in faces.items():
        meta = face["meta"]
        for requirement in meta.get("requirements", []):
            row = copy.deepcopy(requirement)
            row["id"] = f"{slot}/{row['id']}"
            spec["requirements"].append(row)
        for item in meta.get("interfaces", []):
            if item["type"] != "drive" or slot == representative:
                spec["interfaces"].append(prefixed_document(item, slot, face))
        spec["allowances"].extend(prefixed_document(a, slot, face) for a in meta.get("allowances", []))
        for item in meta.get("unknowns", []):
            row = copy.deepcopy(item)
            trial = row.get("trial_part")
            if trial and trial.startswith("$trial/"):
                row["trial_part"] = f"prints/{MODEL}/trial/{slot}/{trial[7:]}"
            if row["id"] in unknowns and unknowns[row["id"]] != row:
                unknowns[row["id"]].setdefault("additional_trials", []).append(row.get("trial_part"))
            else:
                unknowns[row["id"]] = row
    spec["unknowns"] = list(unknowns.values())
    if frame_meta:
        spec["interfaces"] += frame_meta.get("interfaces", [])
        spec["allowances"] += frame_meta.get("allowances", [])
    motion = faces[representative]["meta"]["motion"]
    spec["motion"] = {"actuator": qualify(representative, motion["actuator"]),
                      "servo": "sg92r", "exclude": []}
    return spec


def scoped_allowances(rows):
    """The gate consumes singular step; never silently broaden a module's step list."""
    result = []
    for row in rows:
        if "steps" not in row:
            result.append(row)
            continue
        for step in row["steps"]:
            item = {key: value for key, value in row.items() if key != "steps"}
            item["step"] = step
            result.append(item)
    return result


def mount_allowances(interface, faces, frame_module):
    rows = []
    keys = interface["mount"]["keys"]
    receivers = {r["id"]: r for r in interface["mount_geometry"]["frame_receivers"]}
    for slot in faces:
        for index, (key, receiver_id) in enumerate((("key_l", "latch_l"), ("key_r", "latch_r"))):
            if key not in faces[slot]["meta"]["parts"]:
                continue
            owner = qualify("frame", frame_module.owner_for(slot, receivers[receiver_id]))
            for step in (f"{slot}/{key}_lock", f"{slot}/exchange_key_{index}_in"):
                rows.append({"type": "snap", "pairs": [[qualify(slot, key), owner]],
                    "engage_mm": keys["engage_mm"], "deflection_mm": keys["deflection_mm"],
                    "strain_percent": keys["strain_percent"], "step": step,
                    "basis": "規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。"})
    return rows


def write_retention_cases(build_dir, interface, faces, common, parts, case_inputs):
    cases = []
    for slot, data in case_inputs.items():
        face = faces[slot]
        kinematics = face["modules"]["kinematics"]
        declared = [copy.deepcopy(item) for item in data["spec"]["interfaces"] if item["type"] == "retention"]
        interface_ids = [item["id"] for item in declared]
        if not interface_ids or len(set(interface_ids)) != len(interface_ids):
            raise ValueError(f"{slot}: retention interfaces must be nonempty and unique")
        original_frames = data["frames"]
        static_parts = sorted(part_id for part_id in parts if all(
            C.to_column_major(transforms[part_id]) == C.to_column_major(original_frames[0][1][part_id])
            for _, transforms in original_frames))
        poses = retention_poses(kinematics, face["meta"]["motion"], interface, common)
        for pose in poses:
            directory = build_dir / "retention_cases" / slot / pose["id"]
            matrices = {part_id: np.eye(4) for part_id in parts}
            local = checked_transforms(kinematics, pose["servo_deg"], interface, common, face["meta"]["parts"])
            matrices.update({qualify(slot, local_id): world_transform(face["S"], matrix)
                             for local_id, matrix in local.items()})
            paths = {}
            for part_id, description in parts.items():
                path = directory / "parts" / f"{part_id}.stl"
                export_binary(path, [description["object"]], matrices[part_id])
                paths[part_id] = str(path)
            job = {"parts": paths, "print_parts": {}, "allowances": [], "interfaces": declared,
                   "jigs": data["spec"].get("parts", {}).get("jigs", []), "static_parts": static_parts,
                   "out": str(directory / "report.json")}
            C.write_json(directory / "job.json", job)
            C.write_json(directory / "pose.json", {"slot": slot, **pose,
                "source_motion": f"checks/{slot}/build/motion.json",
                "baked_transforms": {part_id: C.to_column_major(matrix) for part_id, matrix in matrices.items()},
                "baseline_transforms": {part_id: C.to_column_major(np.eye(4)) for part_id in parts}})
            cases.append({"id": f"{slot}/{pose['id']}", "slot": slot, "pose": pose,
                "job": (directory / "job.json").relative_to(HERE).as_posix(),
                "report": (directory / "report.json").relative_to(HERE).as_posix(),
                "parts_count": len(paths), "retention_ids": interface_ids, "static_parts": static_parts})
    C.write_json(build_dir / "retention_cases.json", {"scope": "retention_only", "cases": cases})


def selected_face_sources(configuration):
    sources = set()
    slots = configuration.get("slots")
    if not isinstance(slots, dict) or set(slots) != set(SLOTS):
        raise ValueError("dependency tracking requires exactly six named slots")
    for row in slots.values():
        name = row.get("module") if isinstance(row, dict) else None
        if not isinstance(name, str) or not IDENTIFIER.fullmatch(name) or name == "template":
            raise ValueError(f"invalid selected module for dependency tracking: {name!r}")
        directory = HERE / "faces" / name
        if not directory.is_dir():
            raise ValueError(f"selected module directory missing: {name}")
        for current, directories, filenames in os.walk(directory):
            directories[:] = [name for name in directories if name not in {"build", "__pycache__", "_local"}]
            sources.update(Path(current) / name for name in filenames if Path(name).suffix in (".py", ".json"))
    return sources


def dependency_hashes():
    paths = {p for p in HERE.glob("*.py")} | {HERE / n for n in ("interface.json", "slots.json", "spec.base.json")}
    paths |= selected_face_sources(read(HERE / "slots.json"))
    paths |= {p for p in (ROOT / "lib").rglob("*") if p.suffix in (".py", ".json")}
    paths |= {ROOT / "models" / "sg92r-photo" / n for n in ("params.py", "model.py")}
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            for p in sorted(paths) if p.is_file()}


def dependency_status():
    path = HERE / "build" / "dependencies.json"
    current = dependency_hashes()
    if not path.exists():
        return False, ["missing dependencies.json"]
    stored = read(path).get("inputs", {})
    changed = changed_dependencies(stored, current)
    return not changed, changed


def changed_dependencies(stored, current):
    return sorted(key for key in set(stored) | set(current) if stored.get(key) != current.get(key))


def export_binary(path, objects, transform=None):
    """Write actual mesh triangles in mm without Blender's metre export multiplier."""
    from mathutils import Matrix
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    transform = Matrix(np.eye(4).tolist() if transform is None else np.asarray(transform).tolist())
    temporary = path.with_suffix(path.suffix + ".tmp")
    triangles = []
    for obj in objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        matrix = transform @ obj.matrix_world
        for triangle in mesh.loop_triangles:
            points = [matrix @ mesh.vertices[i].co for i in triangle.vertices]
            normal = (points[1] - points[0]).cross(points[2] - points[0])
            if normal.length < 1e-9:
                raise ValueError(f"{obj.name}: degenerate triangle at export")
            normal.normalize()
            triangles.append((*normal, *(coordinate for p in points for coordinate in p)))
    if not triangles:
        raise ValueError(f"{path}: empty mesh")
    with temporary.open("wb") as handle:
        handle.write(b"resident-face-v2 mm".ljust(80, b"\0"))
        handle.write(struct.pack("<I", len(triangles)))
        for values in triangles:
            handle.write(struct.pack("<12fH", *values, 0))
    os.replace(temporary, path)


def clean_object(obj):
    import bmesh
    from mathutils import Matrix
    # Bake transforms before applying the slot transform to the closed mesh.
    obj.data.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
    bmesh.ops.dissolve_limit(bm, angle_limit=1e-7, verts=list(bm.verts), edges=list(bm.edges))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def append_step(plan, step, prefix, transform, omit=()):
    moving = [qualify(prefix, item) for item in step["moving"] if item not in omit]
    if not moving:
        return
    frames = []
    for frame in step["frames"]:
        frames.append({qualify(prefix, item): transform(rigid(matrix))
                       for item, matrix in frame.items() if item not in omit})
    if not frames or any(not set(moving).issubset(frame) for frame in frames):
        raise ValueError(f"{prefix}/{step['id']}: missing moving frames")
    plan._append(f"{prefix}/{step['id']}", step["title"], step.get("instruction", ""), moving, frames)
    plan.state.update(frames[-1])


def translate_step(plan, step_id, title, ids, start, end, instruction=""):
    distance = float(np.linalg.norm(np.asarray(end) - np.asarray(start)))
    plan.move(step_id, title, ids, C.straight_path(ids, C.translation(*start), C.translation(*end)),
              samples=max(2, math.ceil(distance) + 1), instruction=instruction)


def key_turn_step(plan, slot, key, index, face, interface, release, step_id):
    definition = interface["mount"]["keys"]
    angle = definition["release_rotation_deg"] * (-1 if index == 0 else 1)
    pivot = (*definition["release_pivot_uv_mm"][index], 0)
    angles = np.linspace(0, angle, 5) if release else np.linspace(angle, 0, 5)
    frames = [{qualify(slot, key): world_transform(face["S"], C.rotation((0, 0, 1), a, pivot))}
              for a in angles]
    plan._append(step_id, "固定キーを解除する" if release else "固定キーを戻す",
                 "キー頭をわずかに回して先端を中央へ逃がします。" if release else "キー頭を面一の向きへ戻します。",
                 [qualify(slot, key)], frames)
    plan.state.update(frames[-1])


def key_slide_step(plan, slot, key, index, face, interface, start, end, step_id):
    definition = interface["mount"]["keys"]
    angle = definition["release_rotation_deg"] * (-1 if index == 0 else 1)
    pivot = (*definition["release_pivot_uv_mm"][index], 0)
    rotated = world_transform(face["S"], C.rotation((0, 0, 1), angle, pivot))
    outward = -face["S"][:3, 2]
    frames = [{qualify(slot, key): C.translation(*(outward * distance)) @ rotated}
              for distance in np.linspace(start, end, math.ceil(abs(end - start)) + 1)]
    plan._append(step_id, "固定キーを引き抜く" if end > start else "固定キーを差し込む",
                 "キーを解除角に保って面法線方向へ動かします。", [qualify(slot, key)], frames)
    plan.state.update(frames[-1])


def assembly_plan(interface, faces, common, frame_module, frame_ids):
    plan = C.AssemblyPlan()
    for step in frame_module.assembly_steps(interface, common):
        append_step(plan, step, "frame", lambda m: m)
    if set(plan.state) != {qualify("frame", p) for p in frame_ids}:
        raise ValueError("frame assembly does not place every frame part")
    for slot in SLOTS:
        face = faces[slot]
        S = face["S"]
        outward = -S[:3, 2]
        staging = C.translation(*(outward * 100.0))
        keys = [p for p in ("key_l", "key_r") if p in face["meta"]["parts"]]
        for step in face["modules"]["assembly"].steps(interface, common):
            append_step(plan, step, slot, lambda m, s=S, stage=staging: stage @ world_transform(s, m), omit=keys)
        cassette = [qualify(slot, p) for p in face["meta"]["parts"] if p not in keys]
        if not set(cassette).issubset(plan.state):
            raise ValueError(f"{slot}: module assembly omits cassette parts")
        for part in cassette:
            if not np.allclose(plan.state[part], staging, atol=1e-6):
                raise ValueError(f"{slot}: cassette must return from assembly angle to closed before insertion")
        translate_step(plan, f"{slot}/insert", "カセットをまっすぐ差し込む", cassette,
                       outward * 100, np.zeros(3), "位置決めを合わせて3個の座面へ着座させます。")
        for index, key in enumerate(keys):
            key_slide_step(plan, slot, key, index, face, interface, 40, 0, f"{slot}/{key}_insert")
            key_turn_step(plan, slot, key, index, face, interface, False, f"{slot}/{key}_lock")
    # The exchange path is real assembly input: all five neighbours remain installed.
    for slot, face in faces.items():
        if not face["meta"].get("motion"):
            continue
        outward = -face["S"][:3, 2]
        local_keys = [key for key in ("key_l", "key_r") if key in face["meta"]["parts"]]
        keys = [qualify(slot, key) for key in local_keys]
        for index, key in enumerate(keys):
            key_turn_step(plan, slot, local_keys[index], index, face, interface, True,
                          f"{slot}/exchange_key_{index}_release")
            key_slide_step(plan, slot, local_keys[index], index, face, interface, 0, 50,
                           f"{slot}/exchange_key_{index}_out")
        cassette = [qualify(slot, p) for p in face["meta"]["parts"] if qualify(slot, p) not in keys]
        translate_step(plan, f"{slot}/exchange_out", "隣の面を残して40mm引き出す", cassette,
                       np.zeros(3), outward * 40, "60mmの線の余長を残し、専用コネクタをつかんで外します。")
        plan._append(f"{slot}/disconnect", "配線を切り離す", "コネクタ本体を持ちます。線を引っ張りません。",
                     [], [{}, {}])
        translate_step(plan, f"{slot}/exchange_in", "配線を戻して再装着する", cassette,
                       outward * 40, np.zeros(3))
        for index, key in enumerate(keys):
            key_slide_step(plan, slot, local_keys[index], index, face, interface, 50, 0,
                           f"{slot}/exchange_key_{index}_in")
            key_turn_step(plan, slot, local_keys[index], index, face, interface, False,
                          f"{slot}/exchange_key_{index}_lock")
    if any(not np.allclose(m, np.eye(4), atol=1e-6) for m in plan.state.values()):
        raise ValueError("final assembly must be identity for every part")
    return plan


def build():
    import bpy
    from mathutils import Matrix
    from blender_utils import clear_scene, export_stl
    inputs_before = dependency_hashes()
    clear_scene()
    interface, configuration, faces = load_configuration()
    common = common_params()
    frame_module = load_file("_resident_frame", HERE / "frame.py")
    frame_parts = frame_module.build(interface, common)
    # A real left receiver cut from the front carrier, paired with blank/mount_panel.
    # Keep the carrier rail and exchange-key catch in their production print pose.
    from printmech import geometry as G
    from mathutils import Matrix
    carrier_source = frame_parts["carrier_front"]["object"]
    corner = carrier_source.copy()
    corner.data = carrier_source.data.copy()
    bpy.context.collection.objects.link(corner)
    clean_object(corner)
    G.transform(corner, Matrix(np.linalg.inv(faces["front"]["S"]).tolist()))
    G.intersect(corner, G.box(-50, -10, -32, -2, -2, 10))
    clean_object(corner)
    G.transform(corner, Matrix.Rotation(math.pi, 4, "X"))
    export_binary(ROOT / "prints" / MODEL / "trial" / "frame_corner.stl", [corner])
    bpy.data.objects.remove(corner, do_unlink=True)
    parts = {}
    frame_meta = {"interfaces": [], "allowances": []}
    for key in frame_meta:
        source = getattr(frame_module, key, None)
        rows = source(interface, common) if callable(source) else source or []
        frame_meta[key] = [prefixed_document(row, "frame", {"S": np.eye(4)}) for row in rows]
    frame_meta["allowances"] += mount_allowances(interface, faces, frame_module)
    for local_id, description in frame_parts.items():
        parts[qualify("frame", local_id)] = {**description, "S": np.eye(4), "slot": "frame", "local_id": local_id}
    for slot, face in faces.items():
        face["modules"] = face_package(face["config"]["module"], slot, with_geometry=True)
        geometry = face["modules"]["geometry"].build(interface, common)
        if set(geometry) != set(face["meta"]["parts"]):
            raise ValueError(f"{slot}: geometry and module.json part ids differ")
        for local_id, description in geometry.items():
            parts[qualify(slot, local_id)] = {**description, "S": face["S"], "slot": slot, "local_id": local_id}
        trial_dir = ROOT / "prints" / MODEL / "trial" / slot
        trials = face["modules"]["trials"].build(geometry, interface, common)
        for name, obj in trials.items():
            if not IDENTIFIER.fullmatch(name):
                raise ValueError(f"invalid trial name {name}")
            clean_object(obj)
            export_binary(trial_dir / f"{name}.stl", [obj])
            bpy.data.objects.remove(obj, do_unlink=True)
    build_dir = HERE / "build"
    manifest = []
    for part_id, description in parts.items():
        obj = description["object"]
        clean_object(obj)
        S = description["S"]
        local_id = description["local_id"]
        slot = description["slot"]
        assembled = build_dir / "parts" / slot / f"{local_id}.stl"
        export_binary(assembled, [obj], S)
        row = {"id": part_id, "assembly": assembled.relative_to(HERE).as_posix(),
               "label": description["label"], "color": description["color"]}
        if not description.get("purchased", False):
            print_matrix = rigid(description["print_rotation"], f"{part_id} print rotation").copy()
            if not np.allclose(print_matrix[:3, 3], 0):
                raise ValueError(f"{part_id}: print_rotation must not contain translation")
            points = np.array([print_matrix[:3, :3] @ np.asarray(v.co) for v in obj.data.vertices])
            print_matrix[2, 3] = -float(points[:, 2].min())
            print_path = ROOT / "prints" / MODEL / slot / f"{local_id}.stl"
            export_binary(print_path, [obj], print_matrix)
            row["print"] = os.path.relpath(print_path, HERE).replace(os.sep, "/")
        obj.data.transform(Matrix(S.tolist()))
        manifest.append(row)
    plan = assembly_plan(interface, faces, common, frame_module, frame_parts)
    active = [s for s in SLOTS if faces[s]["meta"].get("motion")]
    if not active:
        raise ValueError("at least one active cassette is required for certification")
    representative = "front" if "front" in active else active[0]
    base = read(HERE / "spec.base.json")
    outputs = [(HERE, representative)] + [(HERE / "checks" / slot, slot) for slot in active]
    cases = []
    case_inputs = {}
    for case_dir, target in outputs:
        case_build = case_dir / "build"
        case_manifest = copy.deepcopy(manifest)
        for part in case_manifest:
            for key in ("assembly", "print"):
                if key in part:
                    part[key] = os.path.relpath(HERE / part[key], case_dir).replace(os.sep, "/")
        C.write_manifest(case_build, case_manifest, {"dimensions_mm": [100, 100, 100],
                         "description": "面ごとのSG92Rカセットを交換する100mm角の住人の箱。",
                         "representative_slot": target})
        motion = faces[target]["meta"]["motion"]
        frames = []
        for angle in sample_angles(motion):
            transforms = {part: np.eye(4) for part in parts}
            local = checked_transforms(faces[target]["modules"]["kinematics"], angle, interface,
                                       common, faces[target]["meta"]["parts"])
            transforms.update({qualify(target, key): world_transform(faces[target]["S"], value)
                               for key, value in local.items()})
            frames.append((float(angle), transforms))
        calibration = faces[target]["config"].get("calibration_deg", 0)
        motion_range(motion, calibration)
        C.write_motion(case_build, frames, home_servo_deg=motion["closed_servo_deg"],
                       duration_s=motion["duration_s"], easing="quintic", slot=target,
                       calibration_deg=calibration,
                       command_angles_deg=[float(angle + calibration) for angle, _ in frames])
        if case_dir != HERE:
            C.write_json(build_dir / "motion_cases" / f"{target}.json", {
                "model": f"{MODEL}/checks/{target}", "slot": target,
                "motion": os.path.relpath(case_build / "motion.json", HERE).replace(os.sep, "/"),
                "held_closed": [slot for slot in SLOTS if slot != target]})
        plan.write(case_build, calibration={"pass": False, "reason": "組立の幾何検査はmechgateが実施"}, passed=False)
        spec = compose_spec(base, faces, target, frame_meta)
        spec["allowances"] = scoped_allowances(spec["allowances"])
        for slot, face in faces.items():
            # Every cassette has independent frame retention; no drive transmission crosses slots.
            S = face["S"]
            ids = [qualify(slot, p) for p in face["meta"]["parts"]]
            spec["interfaces"].append({"id": f"{slot}/frame_retention", "type": "retention", "parts": ids,
                                       "direction": (-S[:3, 2]).tolist(), "max_free_mm": 0.5,
                                       "engage_depth_mm": 2.4})
        if case_dir != HERE:
            spec["model"] = f"{MODEL}/checks/{target}"
            cases.append(spec["model"])
        C.write_json(case_dir / "spec.json", spec)
        case_inputs[target] = {"spec": spec, "frames": frames}
    C.write_json(build_dir / "cases.json", {"representative": representative, "models": cases})
    write_retention_cases(build_dir, interface, faces, common, parts, case_inputs)
    for target in active:
        C.write_json(build_dir / "exchange_cases" / f"{target}.json", {
            "slot": target, "extraction_mm": interface["mount"]["extraction_mm"],
            "neighbours_remain_installed": [s for s in SLOTS if s != target],
            "steps": [step for step in plan.steps if step["id"].startswith(f"{target}/exchange_")
                      or step["id"] == f"{target}/disconnect"]})
    representative_motion = faces[representative]["meta"]["motion"]
    display_modules = faces[representative]["modules"]["kinematics"]
    display_transforms = checked_transforms(display_modules, representative_motion["open_servo_deg"],
        interface, common, faces[representative]["meta"]["parts"])
    display_parts = [qualify(representative, pid) for pid, matrix in display_transforms.items()
                     if not parts[qualify(representative, pid)].get("purchased", False)
                     and not np.allclose(matrix, np.eye(4), atol=1e-7)]
    face_labels = {"front": "正面", "right": "右面", "back": "背面", "left": "左面", "top": "上面", "bottom": "底面"}
    C.write_json(build_dir / "ui.json", {"label": "住人の箱 F1", "displayName": "面を交換できる住人の箱",
                 "navLabel": "住人の箱 F1", "navOrder": 90, "dimensionsFallback": "100 × 100 × 100mm",
                 "physics": {"title": f"{face_labels[representative]}の動き", "playback": "motion-frames", "term": "可動部",
                             "openLabel": "開く", "closeLabel": "閉じる", "chartSeries": display_parts[:5],
                             "simLimits": f"検査ケースでは{face_labels[representative]}だけを動かし、他の面は閉じたままです。",
                             "massNote": "中実PLAの体積から質量を求めます。実物の摩擦は未測定です。"},
                 "assembly": {"servoSetup": "SG92Rを90°にして付属ホーンを取り付けます。",
                              "maxTranslationMm": 1, "maxRotationDeg": 5},
                 "print": {"downloadBase": "prints"}})
    # export_stl is metre-based; only this boundary scales the scene before its 1000x export.
    assembled_objects = [description["object"] for description in parts.values()]
    for obj in assembled_objects:
        obj.data.transform(Matrix.Scale(0.001, 4))
    export_stl(MODEL, only=assembled_objects)
    for obj in assembled_objects:
        obj.data.transform(Matrix.Scale(1000, 4))
    changed_during_build = changed_dependencies(inputs_before, dependency_hashes())
    C.write_json(build_dir / "dependencies.json", {"inputs": inputs_before,
                 "changed_during_build": changed_during_build,
                 "outputs": ["manifest.json", "motion.json", "assembly.json", "cases.json", "retention_cases.json"]})
    if changed_during_build:
        raise RuntimeError("inputs changed during composition; rebuild required: " + ", ".join(changed_during_build))
    # Refresh Studio even before certification: stale gates must disable playback.
    from lattice_export import prepare_assembly, export as export_lattice
    prepare_assembly()
    export_lattice()
    print(f"Composed {len(parts)} parts; active cases: {', '.join(active)}")
    return parts
