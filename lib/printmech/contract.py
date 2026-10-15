"""build/ のデータ契約（viewer/lattice/CONTRACT.md）を読み書きする。numpy のみ、Blender 不要。

モデルはこの関数で manifest.json / motion.json / assembly.json を書き出す。
ゲート（tools/mechgate.py）と viewer/lattice は同じファイルを読む。

行列は 4x4 の numpy 配列（mm）。JSON では長さ 16 の列優先（要素 12,13,14 が並進）。
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np


# --- 行列 ---------------------------------------------------------------------------------
def to_column_major(matrix):
    return [round(float(v), 9) for v in np.asarray(matrix, dtype=float).T.reshape(-1)]


def from_column_major(values):
    return np.array(values, dtype=float).reshape(4, 4).T


def translation(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def rotation(axis, angle_deg, pivot=(0.0, 0.0, 0.0)):
    """pivot を通る axis まわりに angle_deg（右ねじ）回す"""
    u = np.asarray(axis, dtype=float)
    u = u / np.linalg.norm(u)
    a = math.radians(angle_deg)
    k = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    r = np.eye(3) + math.sin(a) * k + (1 - math.cos(a)) * (k @ k)
    m = np.eye(4)
    m[:3, :3] = r
    p = np.asarray(pivot, dtype=float)
    m[:3, 3] = p - r @ p
    return m


def rotation_angle_deg(matrix):
    r = np.asarray(matrix)[:3, :3]
    return math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(r) - 1.0) / 2.0))))


def screw(delta):
    """剛体の増分 delta（4x4）をねじ運動に分ける。
    戻り: {angle_deg, axis, pivot, slide_mm}。回転が無ければ angle 0、axis は並進の向き"""
    r = delta[:3, :3]
    t = delta[:3, 3]
    angle = rotation_angle_deg(delta)
    if angle < 1e-6:
        length = float(np.linalg.norm(t))
        axis = t / length if length > 0 else np.array([0.0, 0.0, 1.0])
        return {"angle_deg": 0.0, "axis": axis, "pivot": np.zeros(3), "slide_mm": length}
    w = np.array([r[2, 1] - r[1, 2], r[0, 2] - r[2, 0], r[1, 0] - r[0, 1]])
    if np.linalg.norm(w) < 1e-9:   # 180 度
        eigvals, eigvecs = np.linalg.eig(r)
        axis = np.real(eigvecs[:, np.argmin(np.abs(eigvals - 1.0))])
    else:
        axis = w / np.linalg.norm(w)
    slide = float(axis @ t)
    perpendicular = t - slide * axis
    # (I - R) p = 軸に垂直な並進。軸方向の成分は 0 に選ぶ
    a = np.vstack([np.eye(3) - r, axis[None, :]])
    b = np.concatenate([perpendicular, [0.0]])
    pivot = np.linalg.lstsq(a, b, rcond=None)[0]
    return {"angle_deg": angle, "axis": axis, "pivot": pivot, "slide_mm": slide}


def screw_motion(s, sign=1.0):
    """screw() の結果を s（回転なら度、並進なら mm）だけ進める 4x4"""
    def at(amount):
        if s["angle_deg"] > 0:
            m = rotation(s["axis"], sign * amount, s["pivot"])
            ratio = s["slide_mm"] / s["angle_deg"]
            m[:3, 3] += s["axis"] * ratio * sign * amount
            return m
        return translation(*(s["axis"] * sign * amount))
    return at


def relative_change(m0, m1, radius):
    """2 姿勢の間の移動量（mm）。回転は radius の円弧で mm に直して足す"""
    delta = np.linalg.inv(m0) @ m1
    return float(np.linalg.norm(delta[:3, 3]) + math.radians(rotation_angle_deg(delta)) * radius)


# --- 入出力 ---------------------------------------------------------------------------------
def write_json(path, document):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=1, default=_json_default)
        handle.write("\n")
    os.replace(temporary, path)


def _json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"JSON にできない型: {type(value).__name__}")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_manifest(build, parts, meta=None):
    """parts: [{id, assembly: 'build/x.stl', print: 'build/print_x.stl' or 無し（既製部品）, label, color}]"""
    write_json(Path(build) / "manifest.json", {"meta": meta or {}, "parts": parts})


def write_motion(build, frames, **extra):
    """frames: [(servo_deg, {id: 4x4})]。servo_deg の昇順に並べる"""
    rows = [{"servo_deg": float(deg), "transforms": {k: to_column_major(v) for k, v in tf.items()}}
            for deg, tf in sorted(frames, key=lambda item: item[0])]
    write_json(Path(build) / "motion.json", {**extra, "frames": rows})


class AssemblyPlan:
    """組立工程を、前の工程の終わりの姿勢から続けて積む。終わりの姿勢は全部品が単位行列（組んだ位置）。

    plan = AssemblyPlan()
    plan.place("housing")                                   # 動かさずに置く
    plan.move("lid-in", "蓋を入れる", ["lid"], path)         # path: progress 0..1 -> {id: 4x4}
    plan.write(build, calibration=..., passed=...)
    """

    def __init__(self):
        self.state = {}
        self.steps = []

    def place(self, step_id, title, parts, instruction=""):
        for part in parts:
            self.state[part] = np.eye(4)
        self._append(step_id, title, instruction, parts, [{p: np.eye(4) for p in parts}] * 2)

    def move(self, step_id, title, parts, path, samples, instruction=""):
        frames = [path(i / (samples - 1)) for i in range(samples)]
        self._append(step_id, title, instruction, parts, frames)
        self.state.update(frames[-1])

    def _append(self, step_id, title, instruction, moving, moving_frames):
        rows = []
        for index, moving_tf in enumerate(moving_frames):
            transforms = {p: m for p, m in self.state.items() if p not in moving}
            transforms.update(moving_tf)
            rows.append({"progress": round(index / max(1, len(moving_frames) - 1), 8),
                         "transforms": {p: to_column_major(m) for p, m in transforms.items()}})
        self.steps.append({"id": step_id, "title": title, "instruction": instruction,
                           "checkText": "", "moving": list(moving), "frames": rows})

    def write(self, build, calibration, passed):
        write_json(Path(build) / "assembly.json",
                   {"steps": self.steps, "calibration": calibration, "pass": bool(passed)})


def straight_path(parts, start, end=None):
    """start（4x4、部品ごとに同じ）から end（既定は単位行列）へまっすぐ動かす path"""
    end = np.eye(4) if end is None else end

    def path(t):
        m = start.copy()
        m[:3, 3] = start[:3, 3] * (1 - t) + end[:3, 3] * t
        return {p: m for p in parts}
    return path
