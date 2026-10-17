"""タンジブル画素キューブの組立経路を、表示用フレームと MANIFOLD Boolean 検査へ同じ変換列から書き出す。

実行（Blender ヘッドレス。起動中の Blender には触らない）:
    "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python-exit-code 1 \
        --python models/tangible-pixel-cube/assembly.py [-- --only lower-shaft-1,bezel]

出力: build/assembly.json（viewer/lattice/CONTRACT.md の assembly.json）、build/assembly_report.json（検査結果）

方針（.claude/memory/lattice-verified-assembly.md の失敗知見に従う）
- 表示する位置と検査する位置は同じ 4x4 列（mm）から作る。部品は消さず、既に入れた全部品と全組合せで検査する
- 並進は 0.499mm 以下、回転は 0.99 度以下の刻み。逆順（分解）は同じ検査済みフレームを戻る
- 許すのは設計した接触だけ（潰しリブ・クリップ・爪のしなり）。場所（部品の組立姿勢の座標）と量（mm）とひずみ（%）を測って記録する
- 校正: 当たる経路と当たらない経路を同じ手順で通して計器を確かめてから本題を測る
- finalState は干渉検査ではない。最終姿勢の干渉は各工程の末尾サンプルで測る
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "lib"))
sys.stdout.reconfigure(encoding="utf-8")

import params as P  # noqa: E402
import kinematics as K  # noqa: E402
import motion  # noqa: E402,F401  (C4 の verify.py が `import motion` する。先にこのモデルのものを入れて取り違えを防ぐ)
import parts_static as S  # noqa: E402  (寸法の定数だけ読む。形は作らない)
import parts_moving as M  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import lattice_assembly as LA  # noqa: E402
from lattice_assembly import (  # noqa: E402
    Allowance, AssemblyPlan, ExactAdapter, IDENTITY, audit_step, matrix_close,
)


# =============================================================================================
# 計器（C4 の校正済みメッシュ・Boolean 計器を読む）
# =============================================================================================
def _load_c4_verify():
    path = ROOT / "models" / "mystery-box-sg92r-c4" / "verify.py"
    spec = importlib.util.spec_from_file_location("c4_verify_helpers", path)
    module = importlib.util.module_from_spec(spec)
    saved = list(sys.path)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved
    return module


C4 = _load_c4_verify()
Mesh = C4.Mesh

TRANSLATION_STEP_MM = 0.499                 # 並進だけの区間の刻み
ROLL_HEIGHT_STEP_MM = 0.3                   # 転がり区間の高さの刻み（回転 0.95 度 x 半径 11.2mm = 0.19mm と合わせて全頂点 0.5mm 以内）
ROLL_ANGLE_STEP_DEG = 0.95
VERTEX_STEP_MM = 0.5                        # フレーム間で部品のどの頂点も 0.5mm より動かない
ROTATION_STEP_DEG = 0.99
MODEL = "tangible-pixel-cube"
VOLUME_LIMIT = LA.VOLUME_LIMIT_MM3

# =============================================================================================
# 寸法（params / parts_static / parts_moving から。ここに書き写さない）
# =============================================================================================
def mm(value):
    return round(value * 1000.0, 6)


ZC = mm(P.CAM_AXIS_Z)                       # 51.7
ZS = mm(P.SERVO_AXIS_Z)                     # 24.2
AXIS_Y = [mm(K.axis_y(j)) for j in range(P.N)]
TOOTH_PITCH_DEG = 360.0 / P.CHAIN_Z         # 17 歯の 1 歯 = 21.18 度

STAGE_Z = 55.0                              # 軸を組む台の高さ（箱の上端 93 より下面が上になる）
UNIT_STAGE_Z = 95.0                         # サーボ一式を組む高さ（受けの下端 3.6 が箱の上端 93 より上）
UNIT_SHIFT_X = -1.8                         # 受けのピンが +X 軸受け帯（X 43.8..45）を避ける寄せ量
UNIT_RETURN_Z = 15.0                        # 帯の下を過ぎてから +X へ戻す高さ（ピン上端が帯の下面より下）
SHAFT_ORDER = (2, 1, 3, 0, 4)               # 落とす順（中央 → 隣 → 外側）
PIXEL_STAGE_Z = 30.0
PLATE_STAGE_Z = 30.0
BEZEL_STAGE_Z = 20.0
COMB_STAGE_Z = 25.0
CLIP_STAGE_Z = 22.0                         # 押さえクリップ（サーボ）の台の高さ
JOINT_APPROACH_MM = 1.5                     # 継ぎ目の差し込み前、雄のスタブの先が雌穴の口の手前に空ける距離
CAP_STAGE_Z = 30.0                          # 押さえ棒を差し始める高さ
GUIDE_SUBDIVIDE = 3                         # 導かれる経路では、落とす経路の各区間を 3 分割して滑りを追う
GUIDE_SLIDE_STEP_MM = 0.05                  # 滑りの候補の刻み
GUIDE_MERGE_FRAMES = 3                      # 滑りの間が これ以下のフレーム数なら 同じ面に沿った 1 つの区間とみなす（刻み 0.05 の滑りは 1 フレームおきに起きうる）
GUIDE_RESOLUTION_DESCENT_MM = 0.10          # 区間の下降がこれ未満で、滑りが刻み 1 個以下なら、傾きは刻みで決まってしまい測れない（判定から外して数と場所を書く）
GUIDED_AXES = (1, 2)                        # ずらし検証をする軸（軸 0・3・4 は 軸 1・2 と同じ形の組なので省く。時間のため）
GUIDE_OFFSETS_MM = (1.0, -1.0)              # 落とし始めの X のずれ（人が正確に入れられない、の検証）
CAPTURE_PROBE_MM = (1.5, 3.0, 6.0)         # じょうごが導ける範囲を測るずれ（両側。軸 2 だけで測る）
CAP_RIB_WINDOW_MM = mm(getattr(P, "CAP_RIB_L", 0.002))   # 押さえ棒の潰しリブが擦ってよい最後の差し込み長さ。parts_static の Y 止めと同じ値（params に CAP_RIB_L が無ければ 2.0mm）
FREE_H = 9.0                                # この高さ（軸の中心が最終より上）で歯車が隣の歯車から離れる（中心距離 19.2 > 外径の和 19）

PART_FILE = {name: BUILD / f"{name}.stl" for name in
             ["housing", "bezel", "guide_plate", "horn_coupler", "phase_comb", "sg92r", "sg92r_horn",
              *(f"camshaft_{j}" for j in range(5)), *(f"gear_{j}" for j in range(5)),
              "bearing_cap_px", "bearing_cap_mx",
              "servo_clip_0", "servo_clip_1",
              *(f"pixel_{i}_{j}" for j in range(5) for i in range(5))]}


def T(x=0.0, y=0.0, z=0.0):
    return LA.translation(x, y, z)


def rot_about_axis(degrees, j):
    """軸 j（Y = AXIS_Y[j]、Z = Zc）まわりの +X 右ねじ回転（+Y から +Z へ）"""
    return LA.rotate_x_about(degrees, AXIS_Y[j], ZC)


def group_parts(j):
    """軸 j に載る部品。歯車の部品 gear_j（+X、雌穴）と、カム 5 枚が一体のカム軸 camshaft_j（-X、+X 端に雄スタブ）。継ぎ目は 1 か所"""
    return [f"gear_{j}", f"camshaft_{j}"]


# =============================================================================================
# 設計した接触の許可（場所・量・ひずみ）
# =============================================================================================
@dataclass
class SpecAllowance(Allowance):
    """設計した接触。交差の頂点が決まった場所に収まり、深さと体積が上限以内であることを測って許す"""
    label: str = ""
    point_test: Callable | None = None      # (point_world, left, right, lm, rm) -> (場所に収まるか, 深さ mm)
    gate_fn: Callable | None = None         # (left, right, lm, rm) -> 差し込みの残り mm。記録用（許可の可否は point_test が見る）
    max_depth_mm: float | None = None
    frame_part: str | None = None           # 場所の座標をこの部品の組立姿勢（最終姿勢）の座標へ戻して記録する
    nominal: dict | None = None
    seen: dict = field(default_factory=dict)   # 許可の種類ごと（"rib" / "claw" など）に、接触した差し込みの残り距離の範囲と最大深さを test が書き込む

    def document(self):
        result = super().document()
        result["label"] = self.label
        if self.max_depth_mm is not None:
            result["limitDepthMm"] = self.max_depth_mm
        if self.nominal:
            result["nominal"] = self.nominal
        return result


def hex_rib_faces():
    """潰しリブがある 3 面の法線の極角。形を作る parts_moving の値を読む（切り落とし面を避けた 1 面おき）"""
    return list(getattr(M, "RIB_NORMALS", (30, 150, 270)))


def seam_engage_mm(female):
    """継ぎ目の雄スタブが雌穴へ入る長さ（穴の深さ）。形を作る parts_moving.gear_hole() の値（固定値を持たない）"""
    return M.gear_hole()["depth"]


def seam_allowance(female, male, mouth_x, window_mm=None):
    """継ぎ目（camshaft_j の雄スタブ ⇔ gear_j の雌穴）。雌穴の潰しリブがスタブの六角の面を 0.18mm 押す。
    許すのは差し込みの最後の window_mm（既定は gear_hole() の rib_len = 口の面取りの奥から底までのリブの長さ）だけ。残り距離 r（雄が座りから離れている量）が
    0 <= r <= window_mm で、接触点が穴の底から window_mm 以内のリブの面（法線 30・150・270 度の 3 面の中央）にあるときに限る。
    それより手前の接触、整列していない（ずれ・傾き）接触、許可を持たない組との接触は不合格になる"""
    j = int(female.split("_")[-1])
    hole = M.gear_hole()
    window = hole["rib_len"] if window_mm is None else window_mm
    depth_hole = hole["depth"]
    face = mm(P.STUB_AF) / 2                              # スタブの面までの距離 2.75
    inner = mm(P.SHAFT_BORE_AF) / 2 - mm(P.HEX_RIB_H)     # リブの先端 2.57
    half_w = mm(P.HEX_RIB_W) / 2
    normals = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in hex_rib_faces()]
    bottom_x = hole["x_bot"]                                # 穴の底の X（スタブの先が座る面）
    assert abs(mouth_x - hole["x_mouth"]) < 0.01, (mouth_x, hole)   # 歯車の STL の -X 面と gear_hole() の口が一致していること
    corner_r = mm(P.SHAFT_BORE_AF) / math.sqrt(3.0) + 0.01
    tol = 0.03

    def relative(left, lm, rm):
        female_matrix, male_matrix = (lm, rm) if left == female else (rm, lm)
        return female_matrix, female_matrix.inverted_safe() @ male_matrix

    def remaining(left, right, lm, rm):
        _, rel = relative(left, lm, rm)
        return -rel.translation.x

    def test(point, left, right, lm, rm):
        female_matrix, rel = relative(left, lm, rm)
        r = -rel.translation.x
        aligned = (abs(rel.translation.y) <= 0.01 and abs(rel.translation.z) <= 0.01
                   and math.degrees(rel.to_quaternion().angle) <= 0.05)
        if not aligned or not (-tol <= r <= window + tol):
            return False, 0.0
        local = female_matrix.inverted_safe() @ Vector(point)
        u, v = local[1] - AXIS_Y[j], local[2] - ZC
        # スタブの先が穴の底に座るとき、先の面と底の面は同一平面で接する。その面上の頂点は体積を持たない接触の面
        if abs(local[0] - bottom_x) <= 0.002 and math.hypot(u, v) <= corner_r:
            return True, 0.0
        if not (bottom_x - window - tol <= local[0] <= bottom_x + tol):
            return False, 0.0
        for nu, nv in normals:
            along = u * nu + v * nv
            across = -u * nv + v * nu
            if inner - tol <= along <= face + tol and abs(across) <= half_w + tol:
                return True, max(0.0, along - inner)
        return False, 0.0

    crush = face - inner
    rib_volume = P.HEX_RIB_FACES * mm(P.HEX_RIB_W) * crush * window
    return SpecAllowance((female, male), "press_fit", zone=f"seam:{male}>{female}",
                         allow_at_final=True, maximum_common_volume_mm3=rib_volume * 1.1,
                         label=f"継ぎ目: 雌穴（{female}）の潰しリブが雄スタブ（{male}）の六角の面を押す（差し込みの最後の {window:g}mm だけ）",
                         point_test=test, gate_fn=remaining, max_depth_mm=crush + 0.02, frame_part=female,
                         nominal={"crushMm": round(crush, 4), "ribVolumeMm3": round(rib_volume, 4),
                                  "ribDepthMm": depth_hole, "allowedInsertionWindowMm": window, "ribs": P.HEX_RIB_FACES})


def seam_allowances(meshes, window_mm=None):
    """全 5 軸の継ぎ目（各軸 1 か所）。{j: [seam_allowance]}"""
    return {j: [seam_allowance(f"gear_{j}", f"camshaft_{j}", meshes[f"gear_{j}"].bounds()[0][0], window_mm)]
            for j in range(P.N)}


def cap_allowance(part, window_mm=None, claw_depth_mm=None):
    """押さえ棒（bearing_cap_px / mx）を端壁の溝へ上から差す。棒の Y の両端の許可は 2 種類（棒の組立姿勢の座標で場所を決める）。
    (1) 潰しリブ（各端 2 本、高さ CAP_RIB_H）が外装の Y 止めの面を押す。許すのは差し込みの最後の window_mm（既定 CAP_RIB_WINDOW_MM = 2.0）だけ。
        Y 止めの面は、リブが擦る範囲（高さ zr0-0.1〜zk）で棒の端から CAP_RIB_H - 0.05、それより上は CAP_SNAP_FACE。
    (2) 上向きの抜け止めのスナップ: 縦の腕の端の爪（出っ張り CAP_SNAP_B、X 44.0〜44.6）が Y 止めの面を乗り越える間、腕がしなる。
        爪が外装の面に当たる深さは「爪の先の出っ張り - その点での Y 止めの面」。潰しの面（棒の端から 0.20）は高さ zr0-0.1〜zk かつ X が CAP_X_IN〜リブの外縁のときだけで、爪の X 範囲（CAP_SNAP_X）はそこから離れているので、爪の面はいつも CAP_SNAP_FACE（0.30）。深さは CAP_SNAP_B - CAP_SNAP_FACE = 0.15。
        量は爪の深さ（mm）、ひずみは腕の梁の見積り 3tδ/(2L^2)（L = 付け根から爪の下端まで）で報告し、2% 以下を要求する。
    座りの位置（r = 0）では爪は窪みに入って接触しない。リブは 0.05 食い込む。それ以外の接触、位置ずれは不合格"""
    window = CAP_RIB_WINDOW_MM if window_mm is None else window_mm
    sg = 1 if part.endswith("px") else -1
    side = S.SIDES[sg]
    ys = AXIS_Y[-1] + side["FW"] / 2 + S.CAP_Y_MARGIN        # 棒の Y の半長（parts_static.build_bearing_cap と同じ式）
    g = S._snap_geom(sg)
    rib = S.CAP_RIB_H
    crush_face = rib - 0.05                                    # 擦る範囲の Y 止めの面（棒の端から）
    interference = rib - crush_face
    face = S.CAP_SNAP_FACE
    crush_z0, crush_z1 = g["zr0"] - 0.1, g["zk"]               # Y 止めの面が crush_face になる高さ（外装の座標 = 座りの棒の座標）
    x_lo = min(S.CAP_RIB_X) - S.CAP_RIB_W / 2
    x_hi = max(S.CAP_RIB_X) + S.CAP_RIB_W / 2
    rib_z0 = g["zr0"]
    rib_z1 = S.CAP_TOP - S.CAP_RIB_MARGIN_Z
    claw_x0, claw_x1 = S.CAP_SNAP_X
    crush_x0 = S.CAP_X_IN                                      # Y 止めの潰しの面（0.20）の X 範囲。爪の X 範囲（CAP_SNAP_X）とは離れている
    crush_x1 = max(S.CAP_RIB_X) + S.CAP_RIB_W / 2
    claw_z0 = g["zb0"]
    claw_z1 = g["zt"] + (S.CAP_SNAP_B + 0.2) * S.CAP_SNAP_SLOPE
    split_z = (g["zt"] + g["zr0"]) / 2                         # 爪の高さとリブの高さを分ける線（棒の座標）
    claw_designed = S.CAP_SNAP_B - face                        # 爪が通常の面を乗り越える量（しなり 0.15）
    claw_limit = claw_designed if claw_depth_mm is None else claw_depth_mm    # 爪の X 範囲の面は常に CAP_SNAP_FACE
    arm_len = (S.CAP_TOP - S.CAP_SNAP_ROOT) - g["zb0"]         # 腕の自由長（付け根から爪の下端）
    tol = 0.03
    spec_seen = {}

    def note(kind, r, depth):
        row = spec_seen.setdefault(kind, {"rLo": 1e9, "rHi": -1e9, "maxDepthMm": 0.0})
        row["rLo"] = min(row["rLo"], r)
        row["rHi"] = max(row["rHi"], r)
        row["maxDepthMm"] = max(row["maxDepthMm"], depth)

    def remaining(left, right, lm, rm):
        cap_matrix = lm if left == part else rm
        return cap_matrix.translation.z

    def test(point, left, right, lm, rm):
        cap_matrix = lm if left == part else rm
        r = cap_matrix.translation.z
        if r < -tol:
            return False, 0.0
        if abs(cap_matrix.translation.x) > 0.01 or abs(cap_matrix.translation.y) > 0.01:
            return False, 0.0
        local = cap_matrix.inverted_safe() @ Vector(point)
        ax, ay, z = abs(local[0]), abs(local[1]), local[2]
        # 爪の高さ（棒の座標で split_z より下）
        if claw_z0 - tol <= z <= min(claw_z1, split_z) + tol and claw_x0 - tol <= ax <= claw_x1 + tol and ys <= ay <= ys + S.CAP_SNAP_B + tol:
            zw = z + r                                          # 外装の座標の高さ
            face_here = crush_face if (crush_z0 <= zw <= crush_z1 and crush_x0 - tol <= ax <= crush_x1 + tol) else face   # 潰しの面は高さと X の両方が合うときだけ
            depth = max(0.0, ay - ys - face_here)
            if depth > claw_limit + tol:
                return False, depth
            note("claw", r, depth)
            return True, depth
        # リブ（棒の座標で split_z より上）。差し込みの最後の window だけ
        if split_z < z and rib_z0 - tol <= z <= rib_z1 + tol and x_lo - tol <= ax <= x_hi + tol and ys - tol <= ay <= ys + rib + tol:
            if not (r <= window + tol):
                return False, 0.0
            depth = max(0.0, ay - ys - crush_face)
            note("rib", r, depth)
            return True, depth
        return False, 0.0

    rib_volume = 4 * S.CAP_RIB_W * max(interference, 0.0) * (rib_z1 - rib_z0)
    claw_volume = 2 * (claw_x1 - claw_x0) * claw_limit * (claw_z1 - claw_z0)
    return SpecAllowance((part, "housing"), "press_fit", zone=f"{part}_ribs", allow_at_final=True,
                         maximum_common_volume_mm3=(max(rib_volume, 0.01) + claw_volume) * 1.5,
                         label=f"押さえ棒: Y 端のリブ（各端 2 本）が Y 止めの面を押す（最後の {window:g}mm だけ）＋ 爪（出っ張り {S.CAP_SNAP_B:g}）が面を乗り越えて腕がしなる",
                         point_test=test, gate_fn=remaining, max_depth_mm=max(interference, claw_limit) + 0.03, frame_part=part, seen=spec_seen,
                         nominal={"ribHeightMm": rib, "ribCrushFaceFromEndMm": crush_face, "interferenceMm": round(interference, 3),
                                  "ribs": 4, "ribXRangeMm": [x_lo, x_hi], "ribZRangeMm": [round(rib_z0, 3), round(rib_z1, 3)],
                                  "allowedInsertionWindowMm": window,
                                  "clawProtrusionMm": S.CAP_SNAP_B, "clawFaceFromEndMm": face, "clawDesignedDeflectionMm": round(claw_designed, 3),
                                  "clawMaxDepthAllowedMm": round(claw_limit, 3), "armFreeLengthMm": round(arm_len, 3),
                                  "armThicknessMm": S.CAP_SNAP_ARM, "clawZRangeMm": [round(claw_z0, 3), round(claw_z1, 3)],
                                  "crushFaceZRangeMm": [round(crush_z0, 3), round(crush_z1, 3)]})


def servo_clip_allowance(side):
    """押さえクリップの脚の爪（受けの側面へ 0.3mm 食い込む）。脚のしなりで通り、閉位置では受けの窪みへ入って食い込みは 0"""
    part = f"servo_clip_{side}"
    yb0, yb1 = S._servo_block_y(-1 if side == 0 else +1)
    h = S.CLIP_BARB_H - S.CLIP_CLR                       # 0.3 = 爪の頂が受けの側面へ入る量
    x0, x1 = S.BLOCK_X0, S.BLOCK_X1
    z_lo = S.CLIP_BARB_Z - (S.CLIP_BARB_FLAT / 2 + S.CLIP_BARB_H + 0.3 + 0.2)
    z_hi = S.FENCE_TOP + 0.5
    tol = 0.02

    def test(point, left, right, lm, rm):
        x, y, z = point
        if not (yb0 - tol <= y <= yb1 + tol and z_lo <= z <= z_hi):
            return False, 0.0
        if x0 - tol <= x <= x0 + h + tol:
            return True, x - x0
        if x1 - h - tol <= x <= x1 + tol:
            return True, x1 - x
        return False, 0.0

    free_len = (S.EAR_TOP + S.CLIP_CLR) - S.CLIP_BARB_Z
    strain = 1.5 * S.CLIP_LEG_T * h / free_len ** 2 * 100.0
    area = (S.CLIP_BARB_FLAT + h) * h                    # 爪の断面（頂 0.8、受けの側面の位置で 0.8 + 2h、深さ h）
    volume = 2 * S.CLIP_W * area                         # 両脚
    return SpecAllowance((part, "housing"), "snap", zone=f"{part}_barbs", deflection_mm=h,
                         strain_percent=strain, allow_at_final=False, maximum_common_volume_mm3=volume * 1.1,
                         label="押さえクリップの脚が爪の分だけしなって受けの側面を通る",
                         point_test=test, max_depth_mm=h + 0.02, frame_part=part,
                         nominal={"freeLengthMm": round(free_len, 3), "legThicknessMm": S.CLIP_LEG_T})


def end_wall_hook_allowance(part, label, zone, depth_nominal, play_mm, y_ranges, z_lo, z_hi, strain_pct,
                            volume=None, nominal=None, allow_at_final=False):
    """±X の端壁の内面へ爪が食い込む接触（壁またはつばがたわむ）。位置は壁の内面 |X| = IX から外へ depth 以内、Y は爪の範囲、Z は爪が壁を通る範囲。
    play_mm は部品が壁の片側へ寄る分（片側の隙間）。寄った最悪の深さまで許可し、公称の姿勢は公称の深さを測る"""
    wall_in = S.IX
    limit = depth_nominal + play_mm
    tol = 0.02

    def test(point, left, right, lm, rm):
        x, y, z = point
        if not (z_lo <= z <= z_hi and any(a0 - tol <= y <= a1 + tol for a0, a1 in y_ranges)):
            return False, 0.0
        ax = abs(x)
        if wall_in - tol <= ax <= wall_in + limit + tol:
            return True, max(0.0, ax - wall_in)
        return False, 0.0

    return SpecAllowance((part, "housing"), "snap", zone=zone, deflection_mm=limit, strain_percent=strain_pct,
                         allow_at_final=allow_at_final, maximum_common_volume_mm3=volume,
                         label=label, point_test=test, max_depth_mm=limit + 0.02, frame_part=part, nominal=nominal)


def bezel_allowance():
    """ベゼルの縁の爪（±X の端壁の内面へ公称 0.15mm 食い込む）。端壁のたわみで通り、閉位置では窪みへ入って食い込みは 0。
    ベゼルが片側へ 0.2mm 寄った最悪は深さ 0.35mm まで許す"""
    depth = S.BARB_H - S.FIT
    wall_t = mm(P.WALL_END)
    free_len = S.Z_SEAM - S.PLATE_Z1
    strain = 3.0 * wall_t * (depth + S.FIT) / (2.0 * free_len ** 2) * 100.0       # 最悪 δ = 0.35
    ys = [(y - S.BARB_L / 2 - 0.1, y + S.BARB_L / 2 + 0.1) for y in S.BARB_Y]
    z_lo = S.BARB_Z - (S.BARB_FLAT / 2 + S.BARB_H) - 0.2
    volume = 2 * len(S.BARB_Y) * S.BARB_L * (S.BARB_FLAT + depth + S.FIT) * (depth + S.FIT)    # 最悪の寄りでの全爪の体積の上限
    return end_wall_hook_allowance(
        "bezel", "ベゼルの爪が端壁の内面を押して壁がたわむ（片持ち梁の最悪見積り）", "bezel_barbs", depth, S.FIT, ys,
        z_lo, S.Z_SEAM + 0.1, strain, volume * 1.1,
        {"wallThicknessMm": wall_t, "freeLengthMm": round(free_len, 3), "nominalDepthMm": round(depth, 3),
         "worstDepthMm": round(depth + S.FIT, 3), "claws": 2 * len(S.BARB_Y)})


def plate_allowance():
    """案内板の舌の爪（±X の端壁の内面へ公称 0.2mm 食い込む）。舌が面内にしなって通り、閉位置では窪みへ入って食い込みは 0。
    板が片側へ 0.2mm 寄った最悪は 0.4mm まで許す"""
    depth = S.HOOK_H - S.FIT
    reach = S.TONGUE_L - S.HOOK_HALF                               # 根元から爪の中心まで（Y）。爪の中心は舌の先の端から HOOK_HALF
    worst = depth + S.FIT
    strain = 3.0 * S.TONGUE_T * worst / (2.0 * reach ** 2) * 100.0
    ys = [S._tongue_y(yc)[3:5] for yc in S.TONGUE_YC]            # 爪の Y の範囲（舌の先の向きは窓の符号で決まる）
    return end_wall_hook_allowance(
        "guide_plate", "案内板の舌の爪が端壁の内面を押して、舌が面内にしなる", "plate_hooks", depth, S.FIT, ys,
        S.PLATE_Z1 - 3.0, S.Z_SEAM + 0.1, strain, None,
        {"tongueThicknessMm": S.TONGUE_T, "tongueReachMm": round(reach, 3), "nominalDepthMm": round(depth, 3),
         "worstDepthMm": round(worst, 3), "claws": 2 * len(S.TONGUE_YC)})


# =============================================================================================
# 接続の確認用アダプタ
# =============================================================================================
BIG_STATIC = ("housing", "guide_plate", "bezel")


class Adapter(ExactAdapter):
    """C4 の ExactAdapter に、numpy の外接箱・三角形の外接箱での前段・許可の場所判定を足したもの"""

    def __init__(self, verify, meshes):
        super().__init__(MODEL, verify, meshes)
        self.V = {name: np.array([tuple(v) for v in mesh.v], dtype=float) for name, mesh in meshes.items()}
        self.lohi = {name: (arr.min(0), arr.max(0)) for name, arr in self.V.items()}
        self.tri = {}
        for name in BIG_STATIC:
            if name in meshes:
                triangles = np.array(meshes[name].t, dtype=int)
                pts = self.V[name][triangles]
                self.tri[name] = (pts.min(1), pts.max(1))
        self.bvh = {}
        self.current_step = None
        self.use_prefilter = True
        self.stats = {}
        self.cache = {}
        self.boolean_calls = 0
        self.prefilter_skips = 0

    @staticmethod
    def _np(matrix):
        return np.array(matrix, dtype=float)

    def bounds(self, part, matrix):
        m = self._np(matrix)
        rotation, translation = m[:3, :3], m[:3, 3]
        lo, hi = self.lohi[part]
        if np.allclose(rotation, np.eye(3), atol=1e-12):
            return (tuple(lo + translation), tuple(hi + translation))
        world = self.V[part] @ rotation.T + translation
        return (tuple(world.min(0)), tuple(world.max(0)))

    def no_surface_contact(self, left, right, lm, rm):
        """大きな静止部品は、三角形の外接箱のどれも相手の外接箱と重ならなければ面が触れ得ない"""
        for big, other, bm, om in ((left, right, lm, rm), (right, left, rm, lm)):
            if big not in self.tri:
                continue
            m = self._np(bm)
            if not np.allclose(m[:3, :3], np.eye(3), atol=1e-12):
                continue
            lo, hi = self.bounds(other, om)
            tmin, tmax = self.tri[big]
            t = m[:3, 3]
            hit = np.all(tmax + t >= np.array(lo) - 1e-3, axis=1) & np.all(tmin + t <= np.array(hi) + 1e-3, axis=1)
            if not hit.any():
                return True
            # 外接箱で省けないとき: 大きな静止部品の三角形の BVH と、動く部品の三角形の BVH が重ならなければ、面が触れ得ない。
            # 閉じた 2 部品は、面が交わらなければ（一方が他方の空洞や外にあって）共通体積を持たない
            if big not in self.bvh:
                self.bvh[big] = BVHTree.FromPolygons([tuple(v + t) for v in self.V[big]], self.meshes[big].t, epsilon=1e-4)
            world = self.V[other] @ self._np(om)[:3, :3].T + self._np(om)[:3, 3]
            moved = BVHTree.FromPolygons(world.tolist(), self.meshes[other].t, epsilon=1e-4)
            if not self.bvh[big].overlap(moved):
                return True
        return False

    def measure(self, left, right, left_matrix, right_matrix, allowance=None):
        if self.use_prefilter and self.no_surface_contact(left, right, left_matrix, right_matrix):
            self.prefilter_skips += 1
            return {"common_volume_mm3": 0.0, "intersection_bounds_mm": None,
                    "existing_allowed": False, "existing_detail": None, "zone_ok": None}
        spec = allowance if isinstance(allowance, SpecAllowance) else None
        key = None
        if spec is not None:
            key = (self.current_step, spec.zone, LA.relative_key(left_matrix, right_matrix))
            if key in self.cache:
                return self.cache[key]
        record = {"depth": 0.0, "lo": [1e9] * 3, "hi": [-1e9] * 3}
        predicate = None
        if spec is not None:
            frame = left_matrix if spec.frame_part == left else right_matrix
            inverse = frame.inverted_safe()

            def predicate(point):
                ok, depth = spec.point_test(tuple(point), left, right, left_matrix, right_matrix)
                local = inverse @ Vector(point)
                for axis in range(3):
                    record["lo"][axis] = min(record["lo"][axis], local[axis])
                    record["hi"][axis] = max(record["hi"][axis], local[axis])
                record["depth"] = max(record["depth"], depth)
                return ok
        self.boolean_calls += 1
        result = self.verify.exact_common_geometry(
            self.meshes[left], left_matrix, self.meshes[right], right_matrix, predicate)
        zone_ok = None
        if spec is not None:
            volume = result["common_volume_mm3"]
            within = bool(result["vertices_in_allowed_zone"])
            if volume <= VOLUME_LIMIT:
                within = True
            if spec.maximum_common_volume_mm3 is not None and volume > spec.maximum_common_volume_mm3:
                within = False
            if spec.max_depth_mm is not None and record["depth"] > spec.max_depth_mm:
                within = False
            zone_ok = within
            if volume > VOLUME_LIMIT:
                entry = self.stats.setdefault((self.current_step, spec.zone), {
                    "parts": list(spec.parts), "label": spec.label, "frame": spec.frame_part,
                    "maxVolumeMm3": 0.0, "maxDepthMm": 0.0, "lo": [1e9] * 3, "hi": [-1e9] * 3,
                    "samples": 0, "insertLo": 1e9, "insertHi": -1e9, "limitVolumeMm3": spec.maximum_common_volume_mm3,
                    "limitDepthMm": spec.max_depth_mm, "strainPercent": spec.strain_percent,
                    "declaredDeflectionMm": spec.deflection_mm, "nominal": spec.nominal})
                entry["samples"] += 1
                if spec.gate_fn is not None:
                    r_now = spec.gate_fn(left, right, left_matrix, right_matrix)
                    entry["insertLo"] = min(entry["insertLo"], r_now)
                    entry["insertHi"] = max(entry["insertHi"], r_now)
                entry["maxVolumeMm3"] = max(entry["maxVolumeMm3"], volume)
                entry["maxDepthMm"] = max(entry["maxDepthMm"], record["depth"])
                for axis in range(3):
                    entry["lo"][axis] = min(entry["lo"][axis], record["lo"][axis])
                    entry["hi"][axis] = max(entry["hi"][axis], record["hi"][axis])
        measured = {"common_volume_mm3": result["common_volume_mm3"],
                    "intersection_bounds_mm": result["intersection_bounds_mm"],
                    "existing_allowed": False, "existing_detail": None, "zone_ok": zone_ok}
        if key is not None:
            self.cache[key] = measured
        return measured


# =============================================================================================
# 歯車の転がり経路（2D の輪郭で、隣の歯車に当たらない回転角を落とす高さごとに追う）
# =============================================================================================
def _slice_x(triangles, x):
    segments = []
    for t in triangles:
        xs = t[:, 0]
        if not (xs.min() < x < xs.max()):
            continue
        points = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if (t[a, 0] - x) * (t[b, 0] - x) < 0:
                s = (x - t[a, 0]) / (t[b, 0] - t[a, 0])
                points.append(t[a, 1:] + s * (t[b, 1:] - t[a, 1:]))
        if len(points) == 2:
            segments.append(points)
    return np.array(segments)


def _loops(segments):
    key = lambda p: (round(float(p[0]), 4), round(float(p[1]), 4))  # noqa: E731
    adjacency = {}
    for index, (a, b) in enumerate(segments):
        adjacency.setdefault(key(a), []).append((index, 0))
        adjacency.setdefault(key(b), []).append((index, 1))
    used, loops = set(), []
    for index in range(len(segments)):
        if index in used:
            continue
        used.add(index)
        points = [segments[index][0], segments[index][1]]
        current, start = key(segments[index][1]), key(segments[index][0])
        while current != start:
            step = next(((j, e) for j, e in adjacency.get(current, []) if j not in used), None)
            if step is None:
                break
            j, e = step
            used.add(j)
            point = segments[j][1 - e]
            points.append(point)
            current = key(point)
        loops.append(np.array(points))
    return loops


def _area(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def _rdp(points, eps):
    def rec(pts):
        if len(pts) < 3:
            return pts
        a, b = pts[0], pts[-1]
        ab = b - a
        length = float(np.hypot(*ab))
        if length < 1e-12:
            d = np.hypot(*(pts - a).T)
        else:
            d = np.abs(ab[0] * (pts[:, 1] - a[1]) - ab[1] * (pts[:, 0] - a[0])) / length
        i = int(np.argmax(d))
        if d[i] > eps:
            left, right = rec(pts[:i + 1]), rec(pts[i:])
            return np.vstack([left[:-1], right])
        return np.vstack([a, b])
    split = int(np.argmax(np.hypot(*(points - points[0]).T)))
    first = rec(points[:split + 1])
    second = rec(np.vstack([points[split:], points[:1]]))
    return np.vstack([first[:-1], second[:-1]])


def _resample(poly, step):
    closed = np.vstack([poly, poly[:1]])
    out = []
    for a, b in zip(closed[:-1], closed[1:]):
        count = max(1, int(math.ceil(float(np.hypot(*(b - a))) / step)))
        out.extend(a + (b - a) * k / count for k in range(count))
    return np.array(out)


def _inside(points, poly):
    x, y = points[:, 0][:, None], points[:, 1][:, None]
    x1, y1 = poly[:, 0][None], poly[:, 1][None]
    x2, y2 = np.roll(poly[:, 0], -1)[None], np.roll(poly[:, 1], -1)[None]
    crossing = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / np.where(y2 != y1, y2 - y1, 1e-30) + x1)
    return (crossing.sum(axis=1) % 2) == 1


def _distance(points, poly):
    a, b = poly, np.roll(poly, -1, axis=0)
    ab = b - a
    length2 = np.maximum((ab ** 2).sum(1), 1e-20)
    ap = points[:, None, :] - a[None]
    t = np.clip((ap * ab[None]).sum(2) / length2[None], 0, 1)
    residual = ap - t[..., None] * ab[None]
    return np.sqrt((residual ** 2).sum(2)).min(1)


class SignedDistance:
    """2D 輪郭の符号つき距離の格子（外が正、内が負）。双一次補間で引く"""

    def __init__(self, poly, half=11.5, step=0.04, center=(0.0, 0.0)):
        self.lo = np.array([center[0] - half, center[1] - half])
        self.step = step
        axis = np.arange(0.0, 2 * half + step / 2, step)
        self.n = (len(axis), len(axis))
        grid = np.stack(np.meshgrid(axis + self.lo[0], axis + self.lo[1], indexing="ij"), -1).reshape(-1, 2)
        out = np.empty(len(grid))
        for start in range(0, len(grid), 20000):
            chunk = grid[start:start + 20000]
            d = _distance(chunk, poly)
            out[start:start + 20000] = np.where(_inside(chunk, poly), -d, d)
        self.v = out.reshape(self.n)

    def __call__(self, points):
        u = (points - self.lo) / self.step
        i, j = np.floor(u[:, 0]).astype(int), np.floor(u[:, 1]).astype(int)
        ok = (i >= 0) & (i < self.n[0] - 1) & (j >= 0) & (j < self.n[1] - 1)
        i, j = np.clip(i, 0, self.n[0] - 2), np.clip(j, 0, self.n[1] - 2)
        fx, fy = u[:, 0] - i, u[:, 1] - j
        v = self.v
        value = (v[i, j] * (1 - fx) * (1 - fy) + v[i + 1, j] * fx * (1 - fy)
                 + v[i, j + 1] * (1 - fx) * fy + v[i + 1, j + 1] * fx * fy)
        return np.where(ok, value, 5.0)


def _rot2(points, degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return points @ np.array([[c, s], [-s, c]])


class GearRoll:
    """隣の歯車へ当たらずに、中心を鉛直に落としながら回す角度 psi(h)。h は最終位置より上の高さ（mm）"""

    CLEARANCE_MM = 0.03          # 2D 輪郭どうしの最小の隙間。格子の補間誤差（約 0.003）より十分大きい

    def __init__(self, slice_x=None):
        raw = np.frombuffer(PART_FILE["gear_2"].read_bytes(), dtype=np.uint8)
        count = int(np.frombuffer(raw[80:84].tobytes(), dtype="<u4")[0])
        dtype = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        triangles = np.frombuffer(raw[84:].tobytes(), dtype=dtype, count=count)["v"].astype(float)
        x = slice_x if slice_x is not None else (mm(P.GEAR_X0) + mm(P.GEAR_X1)) / 2
        loops = _loops(_slice_x(triangles, x))
        outline = max(loops, key=lambda lp: abs(_area(lp)))
        self.outline = _rdp(outline - np.array([0.0, ZC]), 0.004)
        self.points = _resample(self.outline, 0.06)
        self.sdf = SignedDistance(self.outline)
        # 受けの半円歯車（同じ X 断面）。受けの軸（サーボ出力軸）を原点にした輪郭
        raw = np.frombuffer(PART_FILE["horn_coupler"].read_bytes(), dtype=np.uint8)
        count = int(np.frombuffer(raw[80:84].tobytes(), dtype="<u4")[0])
        coupler = np.frombuffer(raw[84:].tobytes(), dtype=dtype, count=count)["v"].astype(float)
        loops = _loops(_slice_x(coupler, x))
        self.coupler = _rdp(max(loops, key=lambda lp: abs(_area(lp))) - np.array([0.0, ZS]), 0.004)
        self.coupler_points = _resample(self.coupler, 0.06)
        self.center_distance = ZC - ZS
        self.coupler_sdf = SignedDistance(self.coupler, half=17.0, center=(0.0, self.center_distance + 5.0))

    def clearance(self, psi, dy, dz):
        moving = _rot2(self.points, psi) + np.array([dy, dz])
        other = _rot2(self.points - np.array([dy, dz]), -psi)
        return float(min(self.sdf(moving).min(), self.sdf(other).min()))

    def coupler_clearance(self, h):
        """中央の軸の歯車を、受けの半円歯車へ鉛直に（角度 0 のまま）h だけ上から入れる途中の 2D の隙間"""
        center = np.array([0.0, self.center_distance + h])
        moving = self.points + center
        other = self.coupler_points - center
        return float(min(self.coupler_sdf(moving).min(), self.sdf(other).min()))

    def coupler_descent(self, h_max=12.0, dh=0.02):
        rows = [(round(h, 6), self.coupler_clearance(h)) for h in np.arange(0.0, h_max + 1e-9, dh)]
        worst = min(rows, key=lambda row: row[1])
        return {"minClearanceMm": round(worst[1], 4), "atHeightMm": worst[0], "samples": len(rows), "stepMm": dh}

    def between_frames(self, waypoints, dy, parts=20):
        """転がり経路の隣り合うフレームの間を 1/20 刻みで補間し、2D の隙間の最小を測る（フレーム間の食い込みの見落とし防止）"""
        worst = (1e9, None)
        for (h0, p0), (h1, p1) in zip(waypoints[:-1], waypoints[1:]):
            for k in range(parts + 1):
                f = k / parts
                value = self.clearance(p0 + (p1 - p0) * f, dy, h0 + (h1 - h0) * f)
                if value < worst[0]:
                    worst = (value, (round(h0 + (h1 - h0) * f, 4), round(p0 + (p1 - p0) * f, 4)))
        return {"minClearanceMm": round(worst[0], 4), "at": {"heightMm": worst[1][0], "angleDeg": worst[1][1]},
                "samplesPerInterval": parts + 1}

    def track(self, dy, h_max=FREE_H + 1.0, dh=0.05, window=5.0, dpsi=0.05):
        """h = 0（最終）から上へ、直前の角度に連続して隙間が最大になる角度を追う。
        戻り値 [(h, psi, 隙間, 通れる角度の下端, 同 上端)]（通れる角度 = 2D の隙間が CLEARANCE_MM 以上の連続区間。window で打ち切り）"""
        psi = 0.0
        start = np.arange(-3.0, 3.0 + 1e-9, dpsi)
        start_ok = np.array([self.clearance(p, dy, 0.0) >= self.CLEARANCE_MM for p in start])
        zero = int(np.argmin(abs(start)))
        lo0 = hi0 = zero
        while lo0 > 0 and start_ok[lo0 - 1]:
            lo0 -= 1
        while hi0 < len(start) - 1 and start_ok[hi0 + 1]:
            hi0 += 1
        path = [(0.0, 0.0, self.clearance(0.0, dy, 0.0), float(start[lo0]), float(start[hi0]))]
        h = 0.0
        while h < h_max - 1e-9:
            h = round(h + dh, 6)
            candidates = np.arange(psi - window, psi + window + 1e-9, dpsi)
            values = np.array([self.clearance(p, dy, h) for p in candidates])
            ok = values >= self.CLEARANCE_MM
            if not ok.any():
                raise RuntimeError(f"歯車が当たらずに回れる角度がない: dy={dy} h={h} 最大隙間 {values.max():.4f}")
            free = np.where(ok)[0]
            k = free[np.argmin(abs(candidates[free] - psi))]
            lo = k
            while lo > 0 and ok[lo - 1]:
                lo -= 1
            hi = k
            while hi < len(candidates) - 1 and ok[hi + 1]:
                hi += 1
            segment = np.arange(lo, hi + 1)
            best = segment[np.argmax(values[segment])]
            psi = float(candidates[best])
            path.append((h, psi, float(values[best]), float(candidates[lo]), float(candidates[hi])))
        return path


# =============================================================================================
# 経路（フレーム）の生成
# =============================================================================================
def group_frames(group, matrices):
    """部品群が同じ剛体変換 matrices（行列のリスト）で動くフレーム列"""
    return [{name: matrix.copy() for name in group} for matrix in matrices]


def lerp_points(start, end, maximum=TRANSLATION_STEP_MM):
    start, end = Vector(start), Vector(end)
    if (end - start).length < 1e-12:
        return [start]
    count = max(1, int(math.ceil((end - start).length / maximum - 1e-9)))
    return [start.lerp(end, k / count) for k in range(count + 1)]


def chain_points(*segments):
    points = []
    for segment in segments:
        points.extend(segment if not points else segment[1:])
    return points


def translated_frames(group, waypoints, base=None):
    """部品群を waypoints（オフセット 3 つ組）の折れ線に沿って 0.499mm 以下の刻みで並進。base は各部品の基準行列（既定は組立姿勢）"""
    base = base or {name: IDENTITY for name in group}
    points = chain_points(*(lerp_points(a, b) for a, b in zip(waypoints[:-1], waypoints[1:])))
    return [{name: T(*p) @ base[name] for name in group} for p in points]


def roll_waypoints(path):
    """転がり経路 [(h, psi, 隙間)]（h = 0 から上へ）を、上から下へ、1 フレームあたり h 0.3mm・psi 0.95 度以内に間引いた (h, psi) 列にする"""
    points = [(row[0], row[1]) for row in reversed(path)]
    kept = [points[0]]
    previous = points[0]
    for point in points[1:]:
        if abs(point[0] - kept[-1][0]) > ROLL_HEIGHT_STEP_MM + 1e-9 or abs(point[1] - kept[-1][1]) > ROLL_ANGLE_STEP_DEG + 1e-9:
            kept.append(previous)
        previous = point
    if kept[-1] != points[-1]:
        kept.append(points[-1])
    return kept


def lower_poses(j, y_offset, psi_start, roll_path):
    """軸 j の部品群を、台（鉛直 STAGE_Z・Y をずらした位置）から最終位置まで落とす姿勢列 [(y, h, psi)]。
    1) Y を最終に合わせる 2) 鉛直に FREE_H まで落とす（角度 psi_start のまま）3) 転がりながら最終位置へ（軸 2 は鉛直のまま）"""
    poses = [(p.y, p.z, psi_start) for p in lerp_points((0, y_offset, STAGE_Z), (0, 0, STAGE_Z))]
    poses.extend((0.0, p.z, psi_start) for p in lerp_points((0, 0, STAGE_Z), (0, 0, FREE_H))[1:])
    if roll_path is None:
        poses.extend((0.0, p.z, 0.0) for p in lerp_points((0, 0, FREE_H), (0, 0, 0))[1:])
    else:
        poses.extend((0.0, h, psi) for h, psi in roll_waypoints(roll_path)[1:])
    return poses


def pose_matrix(j, x, y, h, psi):
    """最終姿勢の形に掛ける剛体変換: T(x, y, h) @ Rx(psi; 軸 j)"""
    return T(x, y, h) @ rot_about_axis(psi, j)


def lower_frames(j, y_offset, psi_start, roll_path):
    return [pose_matrix(j, 0.0, y, h, psi) for y, h, psi in lower_poses(j, y_offset, psi_start, roll_path)]


FRICTION_MU = P.MU_GUIDE_HI                 # 導く面の摩擦係数（0.45。厳しい側）
FRICTION_ANGLE_DEG = math.degrees(math.atan(FRICTION_MU))         # 24.2 度
MAX_SLIDE_OVER_DESCENT = 1.0 / FRICTION_MU                        # 面が水平から摩擦角より立っているための、下降量に対する滑りの最大（2.22）


def locate_guide(adapter, names, fixed, matrix):
    """滑りを起こした接触を、当たった部品と外装側の交差の範囲（組立姿勢の座標、mm）で特定する"""
    for name in names:
        measured = adapter.measure(name, fixed, matrix, IDENTITY)
        if measured["common_volume_mm3"] > VOLUME_LIMIT:
            return {"part": name, "against": fixed, "commonVolumeMm3": round(measured["common_volume_mm3"], 4),
                    "contactBoundsMm": measured["intersection_bounds_mm"]}
    return None


def guide_label(contact, fixed_is_housing=True):
    """接触の範囲から、外装のどの面かを日本語で書く（外装の寸法は parts_static / params から）"""
    if not contact or not contact.get("contactBoundsMm"):
        return "不明"
    (x0, y0, z0), (x1, y1, z1) = contact["contactBoundsMm"]
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    side = "+X" if xm > 0 else "-X"
    ax0, ax1 = sorted((abs(x0), abs(x1)))
    if not fixed_is_housing:
        return f"試験の斜面 X {x0:.2f}..{x1:.2f} Z {z0:.2f}..{z1:.2f}"
    if zm > S.Z_SEAM - 6.0:
        where = "端壁の上端のスリット口（面取り）"
    elif zm > S.PAD_TOP[1 if xm > 0 else -1] + 0.5:
        where = "端壁のスリットの側面"
    elif ax1 > S.PAD_X1 + 0.3:
        where = "U 溝の底・じょうごの面（端壁を掘った面）"
    else:
        where = "軸受けパッドの内面のじょうご"
    return f"{side} 側 {where}（X {x0:.2f}..{x1:.2f} Y {y0:.2f}..{y1:.2f} Z {z0:.2f}..{z1:.2f}）"


def judge_guidance(episodes, mu=None):
    """滑りの連続区間（episodes: 各 {slideMm, descentMm}）が、自重で滑れる面だけで導かれたかを判定する。
    導く面の水平からの角 theta は tan(theta) = 下降量 / 滑り。theta が摩擦角 atan(mu) より大きい（= 滑り / 下降量 <= 1/mu）こと。"""
    mu = FRICTION_MU if mu is None else mu
    limit = 1.0 / mu
    rows = []
    for episode in episodes:
        ratio = episode["slideMm"] / max(episode["descentMm"], 1e-9)
        rows.append({**episode, "slideOverDescent": round(ratio, 3),
                     "faceAngleDeg": round(math.degrees(math.atan2(episode["descentMm"], episode["slideMm"])), 2),
                     "ok": ratio <= limit + 1e-9})
    return {"mu": mu, "frictionAngleDeg": round(math.degrees(math.atan(mu)), 2), "limitSlideOverDescent": round(limit, 3),
            "minFaceAngleDeg": min((r["faceAngleDeg"] for r in rows), default=None), "episodes": rows,
            "pass": all(r["ok"] for r in rows)}


def guided_descent(adapter, group, j, poses, x0, fixed="housing", names=None, describe=True, housing_labels=True):
    """落とし始めの X が x0 だけずれた軸が、じょうごの面に沿って滑り、軸方向の遊びの内側に座るかを、同じ Boolean 計器で測る。
    各姿勢で、直前の X のずれから 0 へ向かって GUIDE_SLIDE_STEP_MM ずつ候補を試し、fixed（外装）との共通体積が閾値以下の最初の候補へ滑る
    （最小の滑り）。0 まで試して全部当たれば詰まり（jam）。各区間は GUIDE_SUBDIVIDE 分割して刻みを細かくする。
    滑りが続いた区間（episode）ごとに、滑り量 / 下降量（面に触れ始める高さ（二分で求める）から最後の滑りの姿勢まで）を測り、導く面の傾き
    atan(下降量 / 滑り) が摩擦角 atan(mu) より立っているかを judge_guidance で判定する。導いた面は接触の範囲で特定して書く。
    最後の姿勢の X が軸方向の遊び（片側 AXIAL_DRIFT）の内側なら座ったとする。describe=False は導いた面の特定と二分を省く（導ける範囲の探索用）。戻り値 (姿勢列 [(x, y, h, psi)], 情報)"""
    names = tuple(names) if names else (f"gear_{j}", f"camshaft_{j}")
    fine = []
    for (y0, h0, p0), (y1, h1, p1) in zip(poses[:-1], poses[1:]):
        for k in range(GUIDE_SUBDIVIDE):
            f = k / GUIDE_SUBDIVIDE
            fine.append((y0 + (y1 - y0) * f, h0 + (h1 - h0) * f, p0 + (p1 - p0) * f))
    fine.append(poses[-1])
    x = x0
    out, jam, events = [], None, []
    worst_event_ratio, worst_slide, slid_total = 0.0, 0.0, 0.0
    for index, (y, h, psi) in enumerate(fine):
        if x != 0.0:
            candidates = []
            sign = 1.0 if x > 0 else -1.0
            c = abs(x)
            while c > 1e-9:
                candidates.append(sign * c)
                c -= GUIDE_SLIDE_STEP_MM
            candidates.append(0.0)
            chosen = None
            for c in candidates:
                matrix = pose_matrix(j, c, y, h, psi)
                hit = any(adapter.measure(name, fixed, matrix, IDENTITY)["common_volume_mm3"] > VOLUME_LIMIT for name in names)
                if not hit:
                    chosen = c
                    break
            if chosen is None:
                jam = {"heightMm": round(h, 3), "xOffsetMm": round(x, 3), "frame": index}
                break
            slide = abs(x - chosen)
            if slide > 1e-9:
                previous_h = out[-1][2] if out else h
                dz = max(previous_h - h, 1e-6)
                worst_event_ratio = max(worst_event_ratio, slide / dz)
                worst_slide = max(worst_slide, slide)
                slid_total += slide
                contact = locate_guide(adapter, names, fixed, pose_matrix(j, x, y, h, psi)) if describe else None
                start_h = previous_h
                if describe and index > 0 and (not events or index - events[-1]["index"] > 1):
                    # 滑りの始まり: 直前の姿勢（このずれで自由）と今の姿勢（当たる）の間を二分して、面に触れ始める高さを求める
                    y_p, h_p, psi_p = fine[index - 1]
                    lo_f, hi_f = 0.0, 1.0                          # 0 = 直前（自由）、1 = 今（当たる）
                    for _ in range(9):
                        mid = (lo_f + hi_f) / 2
                        m = pose_matrix(j, x, y_p + (y - y_p) * mid, h_p + (h - h_p) * mid, psi_p + (psi - psi_p) * mid)
                        if any(adapter.measure(name, fixed, m, IDENTITY)["common_volume_mm3"] > VOLUME_LIMIT for name in names):
                            hi_f = mid
                        else:
                            lo_f = mid
                    start_h = h_p + (h - h_p) * hi_f
                events.append({"index": index, "heightMm": round(h, 3), "preHeightMm": round(start_h, 3),
                               "from": round(x, 3), "to": round(chosen, 3), "slideMm": round(slide, 3), "contact": contact})
            x = chosen
        out.append((x, y, h, psi))
    # 連続した滑り（フレーム番号が続くもの）を 1 つの区間にまとめ、区間の滑り合計 / 区間の下降量で面の傾きを出す
    episodes, current = [], None
    for event in events:
        if current is not None and event["index"] - current["lastIndex"] <= GUIDE_MERGE_FRAMES:
            current["slideMm"] += event["slideMm"]
            current["lastIndex"] = event["index"]
            current["lowHeightMm"] = event["heightMm"]
            current["contacts"].append(event["contact"])
        else:
            if current is not None:
                episodes.append(current)
            current = {"firstIndex": event["index"], "lastIndex": event["index"], "highHeightMm": event["preHeightMm"],
                       "lowHeightMm": event["heightMm"], "slideMm": event["slideMm"], "contacts": [event["contact"]]}
    if current is not None:
        episodes.append(current)
    detail = []
    for episode in episodes:
        first = next((c for c in episode["contacts"] if c), None)
        detail.append({"slideMm": round(episode["slideMm"], 3), "descentMm": round(episode["highHeightMm"] - episode["lowHeightMm"], 3),
                       "fromHeightMm": episode["highHeightMm"], "toHeightMm": episode["lowHeightMm"],
                       "guidingPart": first["part"] if first else None,
                       "guidingSurface": guide_label(first, housing_labels),
                       "contactBoundsMm": first["contactBoundsMm"] if first else None})
    resolution = [row for row in detail if row["slideMm"] <= GUIDE_SLIDE_STEP_MM * 1.01 and row["descentMm"] < GUIDE_RESOLUTION_DESCENT_MM]
    judged = [row for row in detail if row not in resolution]
    judgement = judge_guidance(judged)
    judgement["belowResolution"] = resolution
    play = mm(P.AXIAL_DRIFT)
    reached = jam is None and abs(x) <= play + 1e-6          # 最小の滑りで止まる。軸方向の遊び（片側 AXIAL_DRIFT）の内側に座れば正しい位置
    info = {"startOffsetMm": x0, "reachedFinalX": reached, "finalXmm": round(x, 3), "axialPlayMm": play, "jam": jam,
            "slideTotalMm": round(slid_total, 3), "maxSlideStepMm": round(worst_slide, 3),
            "maxSlideOverDescentPerFrame": round(worst_event_ratio, 3),
            "maxSlideOverDescent": max((r["slideOverDescent"] for r in judgement["episodes"]), default=0.0),
            "guidance": judgement,
            "slopeWithin45deg": judgement["pass"],           # 旧名。いまは「摩擦角より立った面だけで導かれた」の意味（判定は judge_guidance）
            "guidedByFriction": judgement["pass"],
            "minFaceAngleDeg": judgement["minFaceAngleDeg"]}
    return out, info


def stage_matrix(j):
    """台の位置（最終位置から Y を 17(j-2) ずらし、STAGE_Z だけ上）"""
    return T(0, mm(P.PITCH) * (j - 2), STAGE_Z)


# =============================================================================================
# 組立の本体
# =============================================================================================
def load_meshes():
    return {name: Mesh.load(str(path), name) for name, path in PART_FILE.items()}


def manifest_targets():
    manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
    parts = [part["id"] for part in manifest["parts"] if not part.get("fit_only") and not part.get("jig")]
    labels = {part["id"]: part["label"] for part in manifest["parts"]}
    return parts, labels


def compute_roll_paths():
    """隣の歯車が +Y 側（軸 1・0）と -Y 側（軸 3・4）の転がり経路。h = 0 から FREE_H まで"""
    gear = GearRoll()
    result = {}
    for name, dy in (("plusY", -mm(P.PITCH)), ("minusY", mm(P.PITCH))):
        path = gear.track(dy)
        result[name] = [row for row in path if row[0] <= FREE_H + 1e-9]
    return gear, result


def shaft_roll(j, rolls):
    """軸 j の (転がり経路, 落とし始めの角度)。中央の軸 2 は受けの歯へ鉛直に入るので転がらない（2D の隙間で確認済み）"""
    if j == 2:
        return None, 0.0
    path = rolls["plusY" if j < 2 else "minusY"]
    return path, path[-1][1]


def build_plan(rolls, meshes, gear, adapter):
    parts, labels = manifest_targets()
    plan = AssemblyPlan(MODEL, parts)
    seams = seam_allowances(meshes)
    plan.labels = labels

    # --- 1 外装 ----------------------------------------------------------------------------------
    plan.add("housing", "外装を置く",
             "外装を底を下にして置く。配線の窓がある面を奥にする。",
             "他の部品がまだ無いので干渉検査の対象は無い。",
             ("housing",), translated_frames(("housing",), [(0, 0, 10), (0, 0, 0)]))

    # --- 2 ホーン・受け・サーボを箱の上で組む --------------------------------------------------------------
    unit_stage = T(0, 0, UNIT_STAGE_Z)
    travel = [T(-p.x, 0, 0) for p in reversed(lerp_points((0, 0, 0), (25.0, 0, 0)))]
    plan.add("horn-into-coupler", "付属ホーンを受けへ入れる",
             "箱の外で、付属ホーンを長い腕を下にして受けのポケットへ -X 側から押し込む（腕の長さが違うので逆向きは入らない）。",
             "ホーンの腕と受けのポケットの隙間 0.15mm。共通体積 0.001mm3 以下を要求する。",
             ("horn_coupler", "sg92r_horn"),
             [{"horn_coupler": unit_stage.copy(), "sg92r_horn": unit_stage @ m} for m in travel])
    travel = [T(-p.x, 0, 0) for p in reversed(lerp_points((0, 0, 0), (35.0, 0, 0)))]
    plan.add("servo-into-horn", "SG92R の出力軸をホーンへ差す",
             "サーボ（サーボ 90 度、出力軸 +X）を -X 側から差して出力軸をホーンのハブへ入れる。配線の自由端は背面の窓から外へ出す側へ向ける。",
             "サーボ本体・ホーン・受けの共通体積 0.001mm3 以下を要求する。配線の未収録部分は窓の断面で別に確認する。",
             ("sg92r",), [{"sg92r": unit_stage @ m} for m in travel])

    # --- 3 一式を柵へ落とす ------------------------------------------------------------------------------
    unit = ("sg92r", "sg92r_horn", "horn_coupler")
    path = chain_points(
        lerp_points((0, 0, UNIT_STAGE_Z), (UNIT_SHIFT_X, 0, UNIT_STAGE_Z)),
        lerp_points((UNIT_SHIFT_X, 0, UNIT_STAGE_Z), (UNIT_SHIFT_X, 0, UNIT_RETURN_Z)),
        lerp_points((UNIT_SHIFT_X, 0, UNIT_RETURN_Z), (0, 0, UNIT_RETURN_Z)),
        lerp_points((0, 0, UNIT_RETURN_Z), (0, 0, 0)))
    plan.add("unit-lower", "サーボ一式を柵へ落とす",
             f"受けごとサーボを箱の上から下ろす。ピンが +X の軸受けの帯に当たるので {abs(UNIT_SHIFT_X):.1f}mm だけ -X へ寄せて通し、帯の下で戻して、取付耳を柵へ・ピンを縦溝へ落とす。",
             "取付耳の溝は片側 0.25mm でリブが無いので、許す接触は無い。全姿勢で共通体積 0.001mm3 以下を要求する。",
             unit, [{name: T(*p) for name in unit} for p in path])

    # --- 4 押さえクリップ ---------------------------------------------------------------------------------
    clip_names = ("servo_clip_0", "servo_clip_1")
    plan.add("servo-clips", "押さえクリップを上から押し込む",
             "押さえクリップ 2 個を耳の上から被せて押し込む。脚の爪が受けの側面の窪みへ入って止まる。",
             "爪が側面を通る間のしなり（0.3mm）の場所と量とひずみを測る。止まった位置の食い込みは 0 を要求する。",
             clip_names, translated_frames(clip_names, [(0, 0, CLIP_STAGE_Z), (0, 0, 0)]),
             (servo_clip_allowance(0), servo_clip_allowance(1)))

    # --- 5 箱の外で各カム軸に歯車を差す ------------------------------------------------------------------
    starts = {j: shaft_roll(j, rolls)[1] for j in range(P.N)}      # j -> 落とし始めの角度
    stage = {j: stage_matrix(j) @ rot_about_axis(starts[j], j) for j in range(P.N)}
    wait = seam_engage_mm("gear_0") + JOINT_APPROACH_MM
    join_frames = []
    for point in reversed(lerp_points((0, 0, 0), (wait, 0, 0))):
        frame = {}
        for j in range(P.N):
            frame[f"camshaft_{j}"] = stage[j].copy()
            frame[f"gear_{j}"] = stage[j] @ T(point.x, 0, 0)
        join_frames.append(frame)
    join_parts = tuple(join_frames[0])
    plan.add("gears-onto-shafts", "各カム軸に歯車を差す",
             "5 本とも、カム軸の +X 端の六角のスタブへ歯車を +X 側から差す。向きは非対称な切り落とし六角で 1 通り。"
             f"潰しリブが擦るのは最後の {M.gear_hole()['rib_len']:g}mm だけで、手前 {M.gear_hole()['depth'] - M.gear_hole()['rib_len']:g}mm は案内になる。",
             f"雌穴の潰しリブがスタブを押すのは差し込みの最後の {M.gear_hole()['rib_len']:g}mm だけ許し、場所・量・差し込み位置を測る。"
             "それより手前の接触、許可を持たない組との接触、ほかの共通体積 0.001mm3 超は不合格。",
             join_parts, join_frames, tuple(a for j in range(P.N) for a in seams[j]))

    # --- 6 軸を 1 本ずつ箱へ落とす（じょうごに導かれる）--------------------------------------------------------
    rolling_info = {}
    plan.variants = []
    plan.variant_info = {}

    def add_variant(variant_id, group, matrices, allowances, state, info=None):
        scratch = AssemblyPlan(MODEL + "-variant", [])
        scratch.state = {name: matrix.copy() for name, matrix in state.items() if name not in group}   # 動かす部品の始点は変種ごとに違う
        scratch.add(variant_id, variant_id, "", "", tuple(group), group_frames(group, matrices), allowances)
        plan.variants.append(scratch.steps[0])
        if info is not None:
            plan.variant_info[variant_id] = info

    captures = {}
    for j in SHAFT_ORDER:
        group = tuple(group_parts(j))
        roll_path, psi_start = shaft_roll(j, rolls)
        y_offset = mm(P.PITCH) * (j - 2)
        poses = lower_poses(j, y_offset, psi_start, roll_path)
        matrices = [pose_matrix(j, 0.0, y, h, psi) for y, h, psi in poses]
        before_axis = {name: matrix.copy() for name, matrix in plan.state.items()}
        if j == 2:
            text = "中央の軸（2）を鉛直に下ろし、両端の丸を U 溝のじょうごへ落とす。歯車は受けの半円歯車の歯へ上から入る。"
        else:
            side = "+Y" if j < 2 else "-Y"
            turn = "時計回り" if psi_start < 0 else "反時計回り"
            text = (f"軸 {j} を、D 面（-X の軸受けの平らな面）を真上から（+X 側から見て）{turn}に {abs(psi_start):.1f} 度回した向きで U 溝の上へ持ち、鉛直に下ろす。"
                    f"歯が隣（{side} 側）の歯車に触れる高さから、軸が転がるように回して D 面を上へ合わせながら落とす。軸受けの口のじょうごが X のずれを導く。")
        neighbor = {1: "軸 2", 3: "軸 2", 0: "軸 1", 4: "軸 3", 2: "受け"}[j]
        rolling_info[j] = {"startAngleDeg": round(psi_start, 3), "neighbor": neighbor,
                           "rotationDeg": round(abs(psi_start), 3), "rollsFromHeightMm": FREE_H}
        if roll_path is None:
            rolling_info[j]["verticalOnly"] = True
            rolling_info[j]["twoDimensionalDescent"] = gear.coupler_descent()
        else:
            dy = -mm(P.PITCH) if j < 2 else mm(P.PITCH)
            rolling_info[j]["betweenFrames"] = gear.between_frames(roll_waypoints(roll_path), dy)
            rolling_info[j]["corridorDeg"] = {f"h={h:g}": [round(lo, 2), round(hi, 2)]
                                              for h, lo, hi in ((row[0], row[3], row[4]) for row in roll_path)
                                              if round(h, 6) in (0.0, 0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 9.0)}
        plan.add(f"lower-shaft-{j}", f"軸 {j} を U 溝へ落とす", text,
                 f"歯車が{neighbor}と噛む間も含めて、既設の全部品との共通体積 0.001mm3 以下を要求する。潰しリブの押しは許可済みの範囲だけ。",
                 group, group_frames(group, matrices), tuple(seams[j]))
        # じょうごの検証: 落とし始めの X を ±GUIDE_OFFSETS_MM ずらした経路。外装に当たったら 0 へ向かって滑らせ、最終位置へ着くかを測る
        for x0 in (GUIDE_OFFSETS_MM if j in GUIDED_AXES else ()):
            guided, info = guided_descent(adapter, group, j, poses, x0)
            print(json.dumps({"guided": f"axis {j} x0 {x0:+g}", "reached": info["reachedFinalX"], "finalX": info["finalXmm"],
                              "minFaceAngleDeg": info["minFaceAngleDeg"], "ok": info["guidedByFriction"]}, ensure_ascii=False), flush=True)
            info["axis"] = j
            rolling_info[j].setdefault("guided", []).append(info)
            frames = [pose_matrix(j, x, y, h, psi) for x, y, h, psi in guided]
            add_variant(f"lower-shaft-{j}@{x0:+.1f}X", group, frames, tuple(seams[j]), before_axis, info)
        if j == 2:
            probes = {}
            for magnitude in CAPTURE_PROBE_MM:
                for sign in (+1, -1):
                    _, probe = guided_descent(adapter, group, j, poses, sign * magnitude, describe=False)
                    probes[f"{sign * magnitude:+g}"] = {
                        "guided": bool(probe["reachedFinalX"] and probe["guidedByFriction"]), "reached": probe["reachedFinalX"],
                        "jam": probe["jam"], "maxSlideOverDescent": probe["maxSlideOverDescent"]}
            captures[j] = probes
    plan.rolling_info = rolling_info
    plan.capture_probes = captures

    # --- 7 位相合わせ治具 ----------------------------------------------------------------------------------
    comb_down = [T(0, 0, p.z) for p in lerp_points((0, 0, COMB_STAGE_Z), (0, 0, 0))]
    plan.add("phase-comb", "位相合わせ治具を被せる",
             "位相合わせ治具を 5 本の軸の -X 端の D 面へ上から被せる。5 本とも D 面が上なら奥まで座り、1 歯ずれた軸があれば浮く。",
             "座るまでの全姿勢で共通体積 0.001mm3 以下を要求する。1 歯ずれた軸との負例は校正で測る。",
             ("phase_comb",), group_frames(("phase_comb",), comb_down))
    comb_up = list(reversed(comb_down))
    plan.add("phase-comb-remove", "治具を外す",
             "治具を真上へ外す（最終形には残らない）。",
             "同じ経路を逆に上げる。共通体積 0.001mm3 以下を要求する。",
             ("phase_comb",), group_frames(("phase_comb",), comb_up))
    del plan.state["phase_comb"]

    # --- 8 押さえ棒 2 本（端壁の溝へ上から）---------------------------------------------------------------------
    caps = ("bearing_cap_px", "bearing_cap_mx")
    plan.add("bearing-caps", "押さえ棒を 2 本、端壁の溝へ上から差す",
             "押さえ棒 2 本を、+X と -X の端壁の溝へ上から差す。パッドの上面に突き当たれば座ったことが分かる（Y 端の爪が外装の窪みに掛かってカチッと止まる。Y 端のリブが軽く圧入）。",
             f"棒の Y 端のリブが外装の Y 止めの面を押すのは差し込みの最後の {CAP_RIB_WINDOW_MM:g}mm だけ、爪が面を乗り越えて腕がしなるのは爪の場所だけ許し、場所・量（深さ）・ひずみを測る。それ以外の接触は不合格。",
             caps, translated_frames(caps, [(0, 0, CAP_STAGE_Z), (0, 0, 0)]), tuple(cap_allowance(c) for c in caps))

    # --- 9 案内板 ----------------------------------------------------------------------------------------
    plate = [T(0, 0, p.z) for p in lerp_points((0, 0, PLATE_STAGE_Z), (0, 0, 0))]
    before_plate = {name: matrix.copy() for name, matrix in plan.state.items()}

    plan.add("guide-plate", "案内板を下ろす",
             "案内板を上から下ろし、押さえ棒を上から覆い、舌の爪を端壁の窪みへ入れる（舌が面内にしなって止まる）。",
             "舌の爪が端壁の内面を通る間のしなりの場所と量とひずみを測る。止まった位置の食い込みは 0 を要求する。",
             ("guide_plate",), group_frames(("guide_plate",), plate), (plate_allowance(),))
    for dx in (+S.FIT, -S.FIT):
        add_variant(f"guide-plate@{dx:+.1f}X", ("guide_plate",), [T(dx, 0, p.z) for p in lerp_points((0, 0, PLATE_STAGE_Z), (0, 0, 0))],
                    (plate_allowance(),), before_plate)
    # 外すときの逆経路: 最終位置から真上へ。爪の上面（水平から 15 度）が窪みの天井に押されて舌が内へ逃げる
    add_variant("guide-plate-removal", ("guide_plate",), [T(0, 0, p.z) for p in lerp_points((0, 0, 0), (0, 0, PLATE_STAGE_Z))],
                (plate_allowance(),), {name: matrix.copy() for name, matrix in before_plate.items()} | {"guide_plate": IDENTITY.copy()})

    # --- 10 画素 25 個 -----------------------------------------------------------------------------------
    pixels = tuple(f"pixel_{i}_{j}" for j in range(P.N) for i in range(P.N))
    plan.add("pixels", "画素 25 個を上から差す",
             "画素 25 個を案内板の十字穴へ上から差す。足が溝を通ってカムの上に載り、面一で止まる。",
             "茎と足が穴と溝を通る全姿勢で共通体積 0.001mm3 以下を要求する。",
             pixels, translated_frames(pixels, [(0, 0, PIXEL_STAGE_Z), (0, 0, 0)]))

    # --- 11 ベゼル ---------------------------------------------------------------------------------------
    before_bezel = {name: matrix.copy() for name, matrix in plan.state.items()}
    plan.add("bezel", "ベゼルを下ろす",
             "ベゼルを上から被せる。25 個の頭が窓へ入り、縁の爪が端壁の窪みへ嵌まる。",
             "爪が壁の内面を通る間のしなりの場所と量とひずみを測る。嵌まった位置の食い込みは 0 を要求する。",
             ("bezel",), translated_frames(("bezel",), [(0, 0, BEZEL_STAGE_Z), (0, 0, 0)]),
             (bezel_allowance(),))
    for dx in (+S.FIT, -S.FIT):
        add_variant(f"bezel@{dx:+.1f}X", ("bezel",), [T(dx, 0, p.z) for p in lerp_points((0, 0, BEZEL_STAGE_Z), (0, 0, 0))],
                    (bezel_allowance(),), before_bezel)
    return plan


# =============================================================================================
# 校正（当たる経路と当たらない経路を同じ手順で通す）
# =============================================================================================
def wedge_meshes(slide_over_descent, half_width=5.0):
    """判定の校正用。動く箱（X -1..1, Z 0..2, Y ±half_width）と、その +X 側の斜面を持つ固定ブロック。
    斜面は X = 1 + slide_over_descent * Z（高さ Z に対し X が増える）で、箱が X のずれを持って落ちると右下の角が斜面に当たり、
    滑り/下降 = slide_over_descent の面に沿って 0 へ押される。ブロックは Z -2..12、X は斜面から 30 まで"""
    h = 12.0

    def prism_xz(polygon):
        n = len(polygon)
        verts = [Vector((px, -half_width, pz)) for px, pz in polygon] + [Vector((px, half_width, pz)) for px, pz in polygon]
        tris = []
        for k in range(1, n - 1):
            tris.append((0, k + 1, k))                    # -Y 側の蓋（外向き）
            tris.append((n, n + k, n + k + 1))            # +Y 側の蓋
        for k in range(n):
            a, b = k, (k + 1) % n
            tris.append((a, b, n + b))
            tris.append((a, n + b, n + a))
        volume6 = sum(verts[a].dot(verts[b].cross(verts[c])) for a, b, c in tris)
        if volume6 < 0:                                   # 向きが逆なら全三角形を反転（閉じた外向きの面にする）
            tris = [(a, c, b) for a, b, c in tris]
        return Mesh(verts, tris, "wedge")

    wedge = prism_xz([(1.0, -2.0), (30.0, -2.0), (30.0, h), (1.0 + slide_over_descent * h, h), (1.0, 0.0)])
    box = prism_xz([(-1.0, 0.0), (1.0, 0.0), (1.0, 2.0), (-1.0, 2.0)])
    box.name = "probe"
    return wedge, box


def scratch_step(name, seeds, group, matrices, allowances=()):
    """校正用の 1 工程。既設部品 seeds（最終姿勢）の上へ group を matrices に沿って動かす。本番と同じ audit_step で測る"""
    plan = AssemblyPlan("calibration", [])
    plan.seed(*seeds)
    plan.add(name, name, "", "", tuple(group), group_frames(group, matrices), allowances)
    return plan.steps[0]


def compare_reports(left, right):
    """2 つの audit_step の結果の、部品の組ごとの最大共通体積が一致するか"""
    a = {tuple(row["parts"]): row["maxCommonVolumeMm3"] for row in left["pairs"]}
    b = {tuple(row["parts"]): row["maxCommonVolumeMm3"] for row in right["pairs"]}
    differences = {"-".join(key): [a.get(key), b.get(key)] for key in set(a) | set(b)
                   if abs((a.get(key) or 0.0) - (b.get(key) or 0.0)) > 1e-6}
    return not differences and left["pass"] == right["pass"], differences


def run_calibration(adapter, meshes, rolls, plan):
    checks = []
    topology = C4.topology_calibration()
    checks.append({"id": "topology-fixture", "label": "多様体検査の既知形状", "pass": topology["pass"], "detail": topology})
    volume = C4.exact_volume_calibration()
    checks.append({"id": "boolean-fixture", "label": "Boolean 共通体積の既知形状（重なり 0.5・離れ 0・面接触 0・薄い重なり 0.01）",
                   "pass": volume["pass"], "detail": volume})

    def audit_named(tag, step):
        adapter.current_step = f"calibration-{tag}"
        return audit_step(adapter, step)

    # 1 軸 1 を、歯車が隣から離れた高さの並進で（当たらない）／転がさずに鉛直に最終位置まで（当たる）
    group1 = tuple(group_parts(1))
    seams_all = seam_allowances(meshes)
    rib1 = tuple(seams_all[1])
    caps_seed = ()
    seeds = ("housing", *group_parts(2))
    free = [T(0, 0, p.z) @ rot_about_axis(shaft_roll(1, rolls)[1], 1)
            for p in lerp_points((0, 0, 20.0), (0, 0, FREE_H + 0.5))]
    straight = [T(0, 0, p.z) for p in lerp_points((0, 0, FREE_H + 0.5), (0, 0, 0))]
    free_report, _ = audit_named("free", scratch_step("free", seeds, group1, free, rib1))
    hit_report, hit = audit_named("straight", scratch_step("straight", seeds, group1, straight, rib1))
    gear_hit = any(set(v["parts"]) == {"gear_1", "gear_2"} for v in hit)
    checks.append({"id": "path-free", "label": "当たらない経路（軸 1 を歯車が離れた高さで並進）は合格",
                   "pass": free_report["pass"],
                   "detail": {"samples": free_report["samples"], "maxCommonVolumeMm3": free_report["maxCommonVolumeMm3"]}})
    checks.append({"id": "path-collide", "label": "当たる経路（軸 1 を転がさず鉛直に落とす）は歯車 1 と歯車 2 の当たりで不合格",
                   "pass": (not hit_report["pass"]) and gear_hit,
                   "detail": {"violations": len(hit), "maxCommonVolumeMm3": hit_report["maxCommonVolumeMm3"],
                              "firstViolation": hit[0] if hit else None}})

    # 2 サーボ一式を寄せずに鉛直に落とすと、受けのピンが +X の軸受けの帯に当たる（寄せた経路との対）
    unit = ("sg92r", "sg92r_horn", "horn_coupler")
    raw = [T(0, 0, p.z) for p in lerp_points((0, 0, 40.0), (0, 0, 0))]
    unit_report, unit_hit = audit_named("unit-straight", scratch_step(
        "unit-straight", ("housing",), unit, raw))
    pin_hit = [v for v in unit_hit if set(v["parts"]) == {"horn_coupler", "housing"}]
    checks.append({"id": "unit-straight", "label": "サーボ一式を寄せずに真下へ落とすと、受けのピンが +X の軸受けの帯に当たって不合格",
                   "pass": (not unit_report["pass"]) and bool(pin_hit),
                   "detail": {"violations": len(unit_hit),
                              "maxPinCommonVolumeMm3": max((v["commonVolumeMm3"] for v in pin_hit), default=0.0),
                              "firstBoundsMm": pin_hit[0]["intersectionBoundsMm"] if pin_hit else None}})

    # 3 画素: 案内板の十字溝は足に片側 0.2mm。0.15mm ずらしても通る／0.35mm ずらすと当たる
    pixel_seeds = ("housing", *(name for j in range(P.N) for name in group_parts(j)),
                   "bearing_cap_px", "bearing_cap_mx", "guide_plate")
    descent = lerp_points((0, 0, PIXEL_STAGE_Z), (0, 0, 0))
    pixel_rows = {}
    slot_clearance = (P.SLOT_X - P.FOOT_X) * 1000.0 / 2           # 足と十字溝の片側の隙間（0.35）
    shifts = (round(slot_clearance - 0.1, 3), round(slot_clearance + 0.15, 3))
    for shift in shifts:
        report_, violations_ = audit_named(f"pixel-{shift}", scratch_step(
            f"pixel-{shift}", pixel_seeds, ("pixel_0_0",), [T(shift, 0, p.z) for p in descent]))
        pixel_rows[shift] = {"pass": report_["pass"], "violations": len(violations_),
                             "pairs": sorted({" x ".join(v["parts"]) for v in violations_})[:4]}
    checks.append({"id": "pixel-slot",
                   "label": f"画素の足が案内板の十字溝を通る（片側の隙間 {slot_clearance:.2f}mm）: X へ {shifts[0]}mm ずらしても通る／{shifts[1]}mm ずらすと当たる",
                   "pass": pixel_rows[shifts[0]]["pass"] and not pixel_rows[shifts[1]]["pass"], "detail": pixel_rows})

    # 4 継ぎ目の許可の場所判定: 設計位置は場所内、0.5mm ずらすと場所外
    allowance = seams_all[2][0]                                   # 雌 gear_2、雄 camshaft_2
    adapter.current_step = "calibration-rib"
    ok = adapter.measure("gear_2", "camshaft_2", IDENTITY, IDENTITY, allowance)
    shifted = adapter.measure("gear_2", "camshaft_2", IDENTITY, T(0, 0.5, 0), allowance)
    checks.append({"id": "allowance-zone", "label": "継ぎ目の潰しリブの許可: 設計位置は場所内、雄を Y へ 0.5mm ずらすと場所外",
                   "pass": ok["zone_ok"] is True and shifted["zone_ok"] is False,
                   "detail": {"designVolumeMm3": ok["common_volume_mm3"], "designZoneOk": ok["zone_ok"],
                              "shiftedVolumeMm3": shifted["common_volume_mm3"], "shiftedZoneOk": shifted["zone_ok"]}})

    # 4a 潰しリブの許可は最後の差し込みの長さだけ
    female, male = "gear_2", "camshaft_2"
    window = M.gear_hole()["rib_len"]
    engage = seam_engage_mm(female)
    approach = [T(point.x, 0, 0) for point in reversed(lerp_points((0, 0, 0), (engage + 6.0, 0, 0)))]   # 歯車を座りの +X 6mm 手前から差す
    good_report, _ = audit_named("seam-ok", scratch_step("seam-ok", (male,), (female,), approach, (seams_all[2][0],)))
    contact = next((entry for key, entry in adapter.stats.items() if key == ("calibration-seam-ok", f"seam:{male}>{female}")), None)
    narrow = seam_allowance(female, male, meshes[female].bounds()[0][0], window_mm=window / 2)
    narrow_report, narrow_hit = audit_named("seam-window", scratch_step("seam-window", (male,), (female,), approach, (narrow,)))
    other = "gear_3"                                              # 許可を持たない組: 歯車 3 を自分のカム軸 3 へ同じ手順で差す（許可 () を渡す）
    wrong_report, wrong_hit = audit_named("seam-wrong", scratch_step("seam-wrong", ("camshaft_3",), (other,), approach, ()))
    checks.append({
        "id": "rib-window",
        "label": f"潰しリブの許可は最後の差し込みだけ: 正しい継ぎ目の最後の {window:g}mm は合格、許可の幅を半分に絞ると手前の接触で不合格、許可の無い組へ差すと不合格",
        "pass": (good_report["pass"] and contact is not None and 0.0 <= contact["insertLo"] and contact["insertHi"] <= window + 0.03
                 and contact["maxVolumeMm3"] > VOLUME_LIMIT
                 and (not narrow_report["pass"]) and any(set(v["parts"]) == {female, male} for v in narrow_hit)
                 and (not wrong_report["pass"])),
        "detail": {
            "engageMm": engage, "ribWindowMm": window,
            "seamOk": {"pass": good_report["pass"], "ribContactInsertionRemainingMm":
                       [round(contact["insertLo"], 3), round(contact["insertHi"], 3)] if contact else None,
                       "maxCommonVolumeMm3": good_report["maxCommonVolumeMm3"]},
            "windowNarrowedToHalf": {"pass": narrow_report["pass"], "violations": len(narrow_hit),
                                    "firstProgress": narrow_hit[0]["progress"] if narrow_hit else None},
            "pairWithoutAllowance": {"socket": other, "pass": wrong_report["pass"], "violations": len(wrong_hit),
                                     "maxCommonVolumeMm3": wrong_report["maxCommonVolumeMm3"]}}})

    # 4f 摩擦角の判定の校正: 傾きを決めた斜面（箱が落ちて斜面に沿って滑る）。緩い面（滑り/下降 3.0 = 18.4 度）は不合格、立った面（1.5 = 33.7 度）は合格
    wedge_rows = {}
    for ratio_design in (1.5, 3.0):
        wedge, box = wedge_meshes(ratio_design)
        test_adapter = Adapter(C4, {"housing": wedge, "camshaft_2": box})
        test_poses = [(0.0, hh, 0.0) for hh in [12.0 - 0.499 * k for k in range(24)] + [0.0]]
        _, wedge_info = guided_descent(test_adapter, ("camshaft_2",), 2, test_poses, 1.2, names=("camshaft_2",), housing_labels=False)
        wedge_rows[ratio_design] = {
            "designedSlideOverDescent": ratio_design,
            "designedFaceAngleDeg": round(math.degrees(math.atan(1.0 / ratio_design)), 2),
            "measuredSlideOverDescent": wedge_info["maxSlideOverDescent"],
            "measuredMinFaceAngleDeg": wedge_info["minFaceAngleDeg"],
            "reachedFinalX": wedge_info["reachedFinalX"], "finalXmm": wedge_info["finalXmm"],
            "guidedByFriction": wedge_info["guidedByFriction"],
            "guidingSurface": next((e["guidingSurface"] for e in wedge_info["guidance"]["episodes"]), None)}
    checks.append({
        "id": "friction-slope",
        "label": (f"導く面の判定（摩擦角 {FRICTION_ANGLE_DEG:.1f} 度 = 滑り/下降 {MAX_SLIDE_OVER_DESCENT:.2f} 以下）の計器: "
                  "傾きを決めた斜面で、立った面（1.5）は合格、緩い面（3.0）は不合格になり、測った傾きが設計値に近い"),
        "pass": bool(wedge_rows[1.5]["guidedByFriction"] and wedge_rows[1.5]["reachedFinalX"]
                     and (not wedge_rows[3.0]["guidedByFriction"])
                     and abs(wedge_rows[1.5]["measuredSlideOverDescent"] - 1.5) <= 0.3
                     and abs(wedge_rows[3.0]["measuredSlideOverDescent"] - 3.0) <= 0.45),
        "detail": wedge_rows})

    # 4e じょうごの計器: ずれ 0 は滑り 0 で着く（正）。ずれが大きい経路（±6mm）は壁に阻まれて導かれない（負）
    zero, zero_info = guided_descent(adapter, group_parts(2), 2, lower_poses(2, 0.0, 0.0, None), 0.0)
    far = {key: plan.capture_probes.get(2, {}).get(key) for key in ("+6", "-6")}
    checks.append({"id": "funnel-meter",
                   "label": "じょうごの検証の計器: ずれ 0 は滑り 0 で着く／落とし始めが 6mm ずれた経路は導かれず不合格（同じ計器・同じ外装）",
                   "pass": bool(zero_info["reachedFinalX"] and zero_info["slideTotalMm"] == 0.0
                                and all(v is not None and not v["guided"] for v in far.values())),
                   "detail": {"zeroOffset": zero_info, "sixMm": far}})

    # 4d 押さえ棒の許可も最後の差し込みだけ: 正しい許可は合格、許可の幅を 0 にすると（座りの位置以外の）接触で不合格
    cap_name = "bearing_cap_px"
    cap_path = [T(0, 0, point.z) for point in reversed(lerp_points((0, 0, 0), (0, 0, CAP_STAGE_Z)))]
    cap_seeds = ("housing", *(name for j in range(P.N) for name in group_parts(j)))
    cap_good = cap_allowance(cap_name)
    cap_ok, cap_ok_hit = audit_named("cap-ok", scratch_step("cap-ok", cap_seeds, (cap_name,), cap_path, (cap_good,)))
    cap_rib_zero = cap_allowance(cap_name, window_mm=0.0)
    cap_rib_zero_report, cap_rib_zero_hit = audit_named("cap-window", scratch_step(
        "cap-window", cap_seeds, (cap_name,), cap_path, (cap_rib_zero,)))
    cap_claw_zero = cap_allowance(cap_name, claw_depth_mm=0.0)
    cap_claw_zero_report, cap_claw_zero_hit = audit_named("cap-claw", scratch_step(
        "cap-claw", cap_seeds, (cap_name,), cap_path, (cap_claw_zero,)))
    rib_seen, claw_seen = cap_good.seen.get("rib"), cap_good.seen.get("claw")
    checks.append({"id": "cap-rib-window",
                   "label": (f"押さえ棒の許可: リブは最後の差し込み {CAP_RIB_WINDOW_MM:g}mm だけ、爪の乗り越えは深さの上限まで。"
                             "リブの許可幅 0 で不合格、爪の深さ上限 0 で不合格（同じ経路・同じ計器）"),
                   "pass": bool(cap_ok["pass"] and rib_seen and claw_seen
                                and rib_seen["rHi"] <= CAP_RIB_WINDOW_MM + 0.03 and rib_seen["rHi"] > 0.05
                                and claw_seen["maxDepthMm"] > 0.0
                                and (not cap_rib_zero_report["pass"]) and (not cap_claw_zero_report["pass"])),
                   "detail": {"window": CAP_RIB_WINDOW_MM, "passAtWindow": cap_ok["pass"], "violationsAtWindow": len(cap_ok_hit),
                              "ribContacts": rib_seen, "clawContacts": claw_seen,
                              "ribWindowZero": {"pass": cap_rib_zero_report["pass"], "violations": len(cap_rib_zero_hit)},
                              "clawDepthZero": {"pass": cap_claw_zero_report["pass"], "violations": len(cap_claw_zero_hit)}}})

    # 5 位相合わせ治具: 5 本とも組立角なら座る（共通体積 0）。1 歯ずらした軸は 5 本とも両方向で当たる
    comb_rows = []
    for j in range(P.N):
        for teeth in (-1, 1):
            matrix = rot_about_axis(teeth * TOOTH_PITCH_DEG, j)
            value = adapter.measure("phase_comb", f"camshaft_{j}", IDENTITY, matrix)["common_volume_mm3"]
            comb_rows.append({"shaft": j, "teethOff": teeth, "angleDeg": round(teeth * TOOTH_PITCH_DEG, 3),
                              "commonVolumeMm3": round(value, 4)})
        aligned = adapter.measure("phase_comb", f"camshaft_{j}", IDENTITY, IDENTITY)["common_volume_mm3"]
        comb_rows.append({"shaft": j, "teethOff": 0, "angleDeg": 0.0, "commonVolumeMm3": round(aligned, 4)})
    comb_pass = all((row["commonVolumeMm3"] <= VOLUME_LIMIT) == (row["teethOff"] == 0) for row in comb_rows)
    checks.append({"id": "phase-comb", "label": "位相合わせ治具: 組立角は座り、1 歯ずらした軸は 5 本とも両方向で当たる",
                   "pass": comb_pass, "detail": comb_rows})

    # 6 三角形の外接箱での前段が、前段なしの全 Boolean と同じ結果になること（外装・案内板を含む 3 工程で照合）
    by_id = {step["id"]: step for step in plan.steps}
    equivalence = {}
    for sid in ("unit-lower", "lower-shaft-2", "guide-plate"):
        adapter.use_prefilter = False
        full, _ = audit_named(f"prefilter-off-{sid}", by_id[sid])
        adapter.use_prefilter = True
        quick, _ = audit_named(f"prefilter-on-{sid}", by_id[sid])
        same, differences = compare_reports(full, quick)
        equivalence[sid] = {"same": same, "differences": differences, "samples": full["samples"]}
    checks.append({"id": "prefilter-equivalence",
                   "label": "三角形の外接箱の前段は、前段なしの全 Boolean と同じ最大共通体積・合否になる",
                   "pass": all(row["same"] for row in equivalence.values()), "detail": equivalence})
    return {"pass": all(row["pass"] for row in checks), "checks": checks}


# =============================================================================================
# 書き出し
# =============================================================================================
def validate_motion(plan, meshes):
    """工程の境目の連続と、フレーム間の動き（部品の全頂点の移動量の最大、回転角）を測る"""
    boundary_errors, motion_errors = [], []
    max_vertex, max_rotation = 0.0, 0.0
    vertices = {}
    for index, step in enumerate(list(plan.steps) + list(getattr(plan, "variants", []))):
        frames = step["_matrices"]
        if 0 < index < len(plan.steps):
            previous = plan.steps[index - 1]["_matrices"][-1]
            for part in set(previous) & set(frames[0]):
                if not matrix_close(previous[part], frames[0][part]):
                    boundary_errors.append({"before": plan.steps[index - 1]["id"], "after": step["id"], "part": part})
        for before, after in zip(frames, frames[1:]):
            for part in step["moving"]:
                a, b = np.array(before[part], dtype=float), np.array(after[part], dtype=float)
                delta = b - a
                if part not in vertices:
                    vertices[part] = np.array([tuple(v) for v in meshes[part].v], dtype=float)
                moved = vertices[part] @ delta[:3, :3].T + delta[:3, 3]
                vertex_step = float(np.linalg.norm(moved, axis=1).max())
                relative = before[part].to_3x3().transposed() @ after[part].to_3x3()
                rotation = math.degrees(relative.to_quaternion().angle)
                max_vertex = max(max_vertex, vertex_step)
                max_rotation = max(max_rotation, rotation)
                if vertex_step > VERTEX_STEP_MM + 1e-6 or rotation > ROTATION_STEP_DEG + 1e-6:
                    motion_errors.append({"step": step["id"], "part": part, "vertexStepMm": vertex_step,
                                          "rotationDeg": rotation})
    return {"pass": not boundary_errors and not motion_errors, "boundaryErrors": boundary_errors,
            "motionErrors": motion_errors[:20], "maxVertexStepMm": round(max_vertex, 6),
            "maxRotationStepDeg": round(max_rotation, 6)}


def write_json(path, document, compact=False):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        if compact:
            json.dump(document, handle, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(document, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, path)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def summarize_step(step):
    report = step["report"]
    return {
        "samples": report["samples"],
        "pass": report["pass"],
        "maxCommonVolumeMm3": report["maxCommonVolumeMm3"],
        "pairsChecked": len(report["pairs"]),
        "pairsWithBoolean": [row for row in report["pairs"] if row["exactSamples"]],
        "allowedContacts": report["allowedContacts"],
    }


CONNECTOR_W, CONNECTOR_T, CONNECTOR_L = (P.CONNECTOR_W * 1000.0, P.CONNECTOR_T * 1000.0, P.CONNECTOR_L * 1000.0)   # コネクタの箱（幅 X・厚み Z・長さ Y）。params の仮定（実物未計測）


def box_mesh(width, length, thickness, name):
    cube = C4.cube_mesh((0.0, 0.0, 0.0), 1.0, name)
    return Mesh([Vector((v.x * width, v.y * length, v.z * thickness)) for v in cube.v], cube.t, name)


def pass_through_window(adapter, box, dx, dz):
    """箱を中心 (WIN_X + dx, Z = ZS + dz) で、窓の内側（Y 38）から外（Y 58）へ 0.5mm 刻みで通し、外装との最大共通体積を返す。
    箱の外接箱が外装のどの三角形の外接箱とも重ならない姿勢は面が触れ得ないので Boolean を省く（本番の前段と同じ根拠）"""
    housing = adapter.meshes["housing"]
    lo, hi = box.bounds()
    tmin, tmax = adapter.tri["housing"]
    worst = 0.0
    for p in lerp_points((0, 38.0, 0), (0, 58.0, 0), 0.5):
        offset = np.array([S.WIN_X + dx, p.y, ZS + dz])
        if not (np.all(tmax >= np.array(lo) + offset - 1e-3, axis=1) & np.all(tmin <= np.array(hi) + offset + 1e-3, axis=1)).any():
            continue
        matrix = T(*offset)
        worst = max(worst, C4.exact_common_geometry(box, matrix, housing, IDENTITY)["common_volume_mm3"])
    return worst


def connector_check(adapter):
    """配線の窓（+Y 壁）をコネクタの箱が通るかを、外装の STL との MANIFOLD 共通体積で測る。余裕（X・Z のずれ）も探す"""
    if getattr(adapter, "connector_result", None) is not None:
        return adapter.connector_result
    nominal = box_mesh(CONNECTOR_W, CONNECTOR_L, CONNECTOR_T, "connector")
    worst_nominal = pass_through_window(adapter, nominal, 0.0, 0.0)
    margins = {}
    for axis in ("dx", "dz+", "dz-"):
        passed = 0.0
        for step in [0.2 * k for k in range(1, 16)]:
            dx = step if axis == "dx" else 0.0
            dz = step if axis == "dz+" else (-step if axis == "dz-" else 0.0)
            if pass_through_window(adapter, nominal, dx, dz) > VOLUME_LIMIT:
                break
            passed = round(step, 1)
        margins[axis] = passed
    oversize = box_mesh(S.WIN_W + 1.0, CONNECTOR_L, CONNECTOR_T, "connector_oversize")
    adapter.connector_result = {"pass": worst_nominal <= VOLUME_LIMIT,
            "connectorBoxMm": {"widthX": CONNECTOR_W, "thicknessZ": CONNECTOR_T, "lengthY": CONNECTOR_L},
            "windowMm": {"width": S.WIN_W, "height": S.WIN_H, "verticalSide": S.WIN_SIDE_H,
                         "centerX": round(S.WIN_X, 3), "centerZ": round(ZS, 3)},
            "maxCommonVolumeMm3": worst_nominal,
            "freeMarginMm": {"xEitherSide": margins["dx"], "zUp": margins["dz+"], "zDown": margins["dz-"]},
            "oversize": {"widthX": S.WIN_W + 1.0, "maxCommonVolumeMm3": round(pass_through_window(adapter, oversize, 0.0, 0.0), 4)},
            "pathYmm": [38.0, 58.0], "stepMm": 0.5,
            "note": f"コネクタの寸法は正本に無い仮定（{CONNECTOR_W:g} x {CONNECTOR_T:g} の箱。params.CONNECTOR_*）。配線の自由端の曲がり・ほどけ方は見ていない。"}
    return adapter.connector_result


def finalize(plan, meshes, adapter, calibration, mesh_checks, only=None):
    variants = []
    start_hashes = {name: sha256(path) for name, path in PART_FILE.items()}
    algorithms = [Path(LA.__file__), ROOT / "lib/solid_volume.py", ROOT / "models/mystery-box-sg92r-c4/verify.py",
                  HERE / "assembly.py", HERE / "params.py", HERE / "build/manifest.json"]
    algorithm_hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in algorithms}
    frame_validation = validate_motion(plan, meshes)
    all_violations = []
    started = time.time()
    for step in plan.steps:
        if only and step["id"] not in only:
            step["report"] = {"samples": len(step["frames"]), "pass": None, "maxCommonVolumeMm3": None,
                              "pairs": [], "allowedContacts": []}
            continue
        adapter.current_step = step["id"]
        before = (adapter.boolean_calls, adapter.prefilter_skips)
        step["report"], violations = audit_step(adapter, step)
        all_violations.extend({"step": step["id"], **item} for item in violations)
        print(json.dumps({"step": step["id"], "samples": step["report"]["samples"], "pass": step["report"]["pass"],
                          "violations": len(violations), "maxCommonVolumeMm3": step["report"]["maxCommonVolumeMm3"],
                          "booleans": adapter.boolean_calls - before[0], "prefilterSkips": adapter.prefilter_skips - before[1],
                          "elapsedS": round(time.time() - started, 1)}, ensure_ascii=False), flush=True)
    for step in plan.variants:
        if only and step["id"] not in only:
            continue
        adapter.current_step = step["id"]
        step["report"], violations = audit_step(adapter, step)
        all_violations.extend({"step": step["id"], **item} for item in violations)
        info = getattr(plan, "variant_info", {}).get(step["id"])
        guided_ok = True if info is None else bool(info["reachedFinalX"] and info["guidedByFriction"])
        variants.append({"id": step["id"], "samples": step["report"]["samples"],
                         "pass": bool(step["report"]["pass"] and guided_ok),
                         "auditPass": step["report"]["pass"], "guided": info,
                         "maxCommonVolumeMm3": step["report"]["maxCommonVolumeMm3"],
                         "allowedContacts": step["report"]["allowedContacts"]})
        print(json.dumps({"variant": step["id"], "pass": step["report"]["pass"], "violations": len(violations),
                          "maxCommonVolumeMm3": step["report"]["maxCommonVolumeMm3"]}, ensure_ascii=False), flush=True)
    connector = connector_check(adapter)
    target = plan.target_parts
    final_missing = [part for part in target if part not in plan.state]
    final_extra = [part for part in plan.state if part not in target]
    final_moved = [part for part in target if part in plan.state and not matrix_close(plan.state[part], IDENTITY)]
    final_state = {"pass": not final_missing and not final_extra and not final_moved,
                   "basis": "部品の過不足と最終変換が単位行列かの検査。干渉検査ではない（最終姿勢の干渉は各工程の末尾サンプルで測る）",
                   "expectedParts": list(target), "missing": final_missing, "extra": final_extra,
                   "nonIdentityTransforms": final_moved}
    reverse = {"pass": all(step["report"]["pass"] for step in plan.steps) if not only else None,
               "guidePlateRemoval": "variants の guide-plate-removal（最終位置から真上へ。爪の上面が窪みの天井に押される向き）を別に測った",
               "method": "検査済みのフレームを逆順に戻す（同じ経路・同じ姿勢の集合）",
               "steps": [{"id": step["id"], "samples": len(step["frames"]), "pass": step["report"]["pass"]}
                         for step in reversed(plan.steps)]}
    end_hashes = {name: sha256(path) for name, path in PART_FILE.items()}
    source_integrity = {"pass": start_hashes == end_hashes, "start": start_hashes, "end": end_hashes}
    algorithm_integrity = all(sha256(ROOT / path) == digest for path, digest in algorithm_hashes.items())
    frame_contract = {"maximumVertexStepMm": VERTEX_STEP_MM, "maximumRotationStepDeg": ROTATION_STEP_DEG,
                      "measuredMaxVertexStepMm": frame_validation["maxVertexStepMm"],
                      "measuredMaxRotationStepDeg": frame_validation["maxRotationStepDeg"],
                      "pass": frame_validation["maxVertexStepMm"] <= VERTEX_STEP_MM + 1e-6
                              and frame_validation["maxRotationStepDeg"] <= ROTATION_STEP_DEG + 1e-6}
    step_pass = (all(step["report"]["pass"] for step in plan.steps) and connector["pass"]) if not only else None
    # 板・ベゼルが片側へ 0.2mm 寄った最悪の姿勢と、案内板を外す経路。結果は別枠に出すが、全体の合否にも含める
    worst_case = {"pass": all(v["pass"] for v in variants) if variants else None,
                  "note": "部品が壁の片側へ 0.2mm 寄った最悪の姿勢（板 ±X、ベゼル ±X）と案内板を外す経路。全体の合否（pass）に含める",
                  "variants": variants,
                  "failures": [v for v in all_violations if "@" in v["step"] or "removal" in v["step"]]}
    # 組立の検査が頼るのは「全辺が 2 面共有（閉じている）」こと。零面積の三角形は Boolean の体積に効かないので数えて報告するだけにする
    cap_snap = []
    for step in plan.steps:
        if step["id"] != "bearing-caps":
            continue
        for allowance in step["_allowances"]:
            nominal = allowance.nominal or {}
            claw = allowance.seen.get("claw")
            if claw is None:
                continue
            length, thickness = nominal["armFreeLengthMm"], nominal["armThicknessMm"]
            strain_max = 1.5 * thickness * claw["maxDepthMm"] / length ** 2 * 100.0
            strain_design = 1.5 * thickness * nominal["clawDesignedDeflectionMm"] / length ** 2 * 100.0
            cap_snap.append({"part": allowance.parts[0], "clawMaxDepthMm": round(claw["maxDepthMm"], 4),
                             "designedDeflectionMm": nominal["clawDesignedDeflectionMm"],
                             "armFreeLengthMm": length, "armThicknessMm": thickness,
                             "strainPercentAtMaxDepth": round(strain_max, 3), "strainPercentAtDesignedDeflection": round(strain_design, 3),
                             "clawInsertionRemainingRangeMm": [round(claw["rLo"], 3), round(claw["rHi"], 3)],
                             "ribContacts": allowance.seen.get("rib"), "pass": strain_max <= 2.0})
    cap_snap_ok = (not cap_snap and bool(only)) or (bool(cap_snap) and all(row["pass"] for row in cap_snap))
    inputs_ok = all(row["bad_edges"] == 0 and row["connected_components"] >= 1 for row in mesh_checks.values())
    passed = bool(calibration["pass"] and inputs_ok and frame_validation["pass"] and frame_contract["pass"] and step_pass
                  and worst_case["pass"] is not False and cap_snap_ok and final_state["pass"] and reverse["pass"] and source_integrity["pass"] and algorithm_integrity)
    designed = [{"step": step_id, "zone": zone, **{k: (round(v, 4) if isinstance(v, float) else v)
                                                     for k, v in entry.items() if k not in ("lo", "hi", "insertLo", "insertHi")},
                 "boundsInPartFrameMm": [[round(v, 3) for v in entry["lo"]], [round(v, 3) for v in entry["hi"]]],
                 **({"insertionRemainingMm": [round(entry["insertLo"], 3), round(entry["insertHi"], 3)]}
                    if entry["insertHi"] >= entry["insertLo"] else {})}
                for (step_id, zone), entry in sorted(adapter.stats.items()) if not step_id.startswith("calibration")]
    output_steps = []
    for step in plan.steps:
        row = {key: value for key, value in step.items() if not key.startswith("_")}
        row["report"] = summarize_step(step)
        output_steps.append(row)
    document = {"model": MODEL, "source_sha256": start_hashes, "algorithm_sha256": algorithm_hashes,
                "steps": output_steps, "calibration": calibration, "pass": passed,
                "worstCasePass": worst_case["pass"]}
    report = {
        "model": MODEL,
        "method": "表示用の変換と Blender Boolean MANIFOLD の検査姿勢を、同じ列優先 mm の変換列から作る",
        "calibration": calibration,
        "inputMeshes": {"pass": inputs_ok, "parts": len(mesh_checks),
                        "badEdges": sum(row["bad_edges"] for row in mesh_checks.values()),
                        "degenerateTriangles": sum(row["degenerate_triangles"] for row in mesh_checks.values()),
                        "partsWithDegenerateTriangles": sorted(name for name, row in mesh_checks.items()
                                                               if row["degenerate_triangles"]),
                        "note": "零面積（または 0.00001mm の丸めで頂点が重なる）三角形は形状の担当への連絡事項。閉じ方（辺の 2 面共有）は全部品で正しい。",
                        "perPart": {name: {"triangles": row["triangles"], "badEdges": row["bad_edges"],
                                           "degenerateTriangles": row["degenerate_triangles"],
                                           "components": row["connected_components"]}
                                    for name, row in mesh_checks.items()}},
        "frameValidation": frame_validation,
        "frameContract": frame_contract,
        "steps": [{"id": step["id"], "title": step["title"], **summarize_step(step)} for step in plan.steps],
        "violations": all_violations,
        "designedContacts": designed,
        "rolling": plan.rolling_info,
        "wireWindow": connector,
        "worstCase": worst_case,
        "capSnap": {"pass": cap_snap_ok, "parts": cap_snap, "limitStrainPercent": 2.0,
                    "note": "爪が外装の面を乗り越える最大の深さから、腕の梁の見積り 3tδ/(2L^2) でひずみを出す（PLA 2% 以下）。実物未検証"},
        "funnelCapture": {"probesByAxis": getattr(plan, "capture_probes", {}),
                          "note": "落とし始めの X のずれごとに、外装に当たったら 0 へ滑らせて最終位置へ着くか（reached）。詰まった（reached=false）ずれがじょうごの導ける範囲の外"},
        "finalState": final_state,
        "reverseDisassembly": reverse,
        "sourceIntegrity": source_integrity,
        "algorithm_sha256": algorithm_hashes,
        "algorithmIntegrity": algorithm_integrity,
        "instrument": {"booleanCalls": adapter.boolean_calls, "prefilterSkips": adapter.prefilter_skips,
                       "volumeLimitMm3": VOLUME_LIMIT,
                       "prefilter": "housing / guide_plate / bezel は三角形の外接箱が相手の外接箱と重ならなければ面が触れ得ないので Boolean を省く"},
        "limitations": [
            "SG92R の配線の自由端とコネクタは正本に無い。コネクタを 7.8 x 2.5 の箱と仮定して窓を通しただけで、実物未確認。",
            "圧入・スナップ・材料収縮・摩擦・指で押す力は実物未検証。しなりは梁の見積りで、実物の着脱力は未確認。",
            "離散経路は並進 0.5mm 以下・回転 1 度以下の刻み。フレームの間の連続空間全体の証明ではない。",
            "歯車の転がり経路は X 断面の 2D 輪郭の隙間（0.03mm 以上）で追い、全姿勢を 3D の Boolean で再検査している。人の手の安定さは見ていない。",
            "ベゼルの爪は縁ではなく端壁のたわみ、案内板の爪は舌の面内のしなりで通る前提（梁の見積り）。実物未確認。",
        ],
        "pass": passed,
    }
    if only:
        print(json.dumps({"only": sorted(only), "violations": len(all_violations)}, ensure_ascii=False))
        write_json(BUILD / "assembly_partial_report.json", report)
        return report
    write_json(BUILD / "assembly.json", document, compact=True)
    write_json(BUILD / "assembly_report.json", report)
    print(json.dumps({"model": MODEL, "pass": passed, "steps": len(plan.steps),
                      "samples": sum(len(step["frames"]) for step in plan.steps), "violations": len(all_violations),
                      "calibration": calibration["pass"], "worst_case_pass": worst_case["pass"],
                      "final_state_pass": final_state["pass"],
                      "reverse_pass": reverse["pass"]}, ensure_ascii=False))
    return report


def main(argv):
    only = None
    if "--only" in argv:
        only = set(argv[argv.index("--only") + 1].split(","))
    started = time.time()
    meshes = load_meshes()
    gear, rolls = compute_roll_paths()
    print(json.dumps({"roll": {k: {"startAngleDeg": round(v[-1][1], 3), "samples": len(v)} for k, v in rolls.items()},
                      "elapsedS": round(time.time() - started, 1)}), flush=True)
    adapter = Adapter(C4, meshes)
    plan = build_plan(rolls, meshes, gear, adapter)
    print(json.dumps({"steps": [step["id"] for step in plan.steps],
                      "frames": {step["id"]: len(step["frames"]) for step in plan.steps}}, ensure_ascii=False), flush=True)
    calibration = run_calibration(adapter, meshes, rolls, plan) if not only else {"pass": True, "checks": [], "skipped": True}
    print(json.dumps({"calibration": calibration["pass"],
                      "checks": [{"id": c["id"], "pass": c["pass"]} for c in calibration["checks"]]}, ensure_ascii=False), flush=True)
    if not calibration["pass"]:
        write_json(BUILD / "assembly_calibration_failed.json", calibration)
        raise SystemExit("calibration failed")
    mesh_checks = {name: C4.topology(str(path)) for name, path in PART_FILE.items()}
    report = finalize(plan, meshes, adapter, calibration, mesh_checks, only)
    if not report["pass"] and not only:
        raise SystemExit(1)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(args)
