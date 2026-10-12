"""タンジブル画素キューブ: 全部品を作って書き出す（bpy）。

実行: "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python-exit-code 1 --python models/tangible-pixel-cube/model.py

- parts_static.build_static()（外装・ベゼル・案内板・SG92R・ホーン）と parts_moving.build_moving()（軸・歯車・カム・クリップ・画素・受け・治具）を呼ぶ。
  どちらも {id: Object}（組立姿勢、m、オブジェクト名 = id）と PRINT_POSE（刷る向き）を持つ。parts_moving.py が無ければ警告して静止部品だけで通す
- build/<id>.stl（組立姿勢、mm）と build/print_<id>.stl（PRINT_POSE で回し、最下点 z=0、XY の外接の中心を原点、mm）
- build/manifest.json（viewer/lattice/CONTRACT.md の部品表）、build/model_report.json（部品ごとの形の検査）
- exports/tangible-pixel-cube.stl（治具以外の全部品を組立姿勢で 1 つに）

検査（model_report.json）は numpy だけで書き出した STL の三角形から数える: 非多様体辺・連結成分・外接寸法・体積・
「水平から 45 度より寝た下向き面」の面積（刷る向き）とそれが見える面か。数える前に答えの分かる形で計器を校正する（calibration）。
"""
import importlib.util
import json
import math
import os
import sys
import time
import traceback

import bpy
import numpy as np
from mathutils import Euler, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402
import parts_static as S  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BUILD = os.path.join(HERE, "build")
EXPORT_ALL = os.path.join(REPO, "exports", "tangible-pixel-cube.stl")
MODEL = "tangible-pixel-cube"

WELD_MM = 1e-4                    # 頂点を同じとみなす距離（mm）。STL は float32 なので 1e-4 より細かくは意味が無い
OVERHANG_DEG = 45.0               # 水平から何度より寝た下向き面を数えるか
OVERHANG_TOL = 0.1                # 45 度ちょうどの面（面取り）を数に入れないための余裕（度）


# =============================================================================================
# 三角形の取り出しと書き出し
# =============================================================================================
def tris_mm(ob):
    """オブジェクトの評価後メッシュ -> 世界座標の頂点（mm）と三角形の頂点番号。巻き向きは世界座標で正す"""
    dg = bpy.context.evaluated_depsgraph_get()
    eo = ob.evaluated_get(dg)
    me = eo.to_mesh()
    me.calc_loop_triangles()
    nv = len(me.vertices)
    co = np.empty(nv * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    nt = len(me.loop_triangles)
    tri = np.empty(nt * 3, dtype=np.int64)
    me.loop_triangles.foreach_get("vertices", tri)
    eo.to_mesh_clear()
    M = np.array(ob.matrix_world, dtype=np.float64)
    V = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
    T = tri.reshape(-1, 3)
    if np.linalg.det(M[:3, :3]) < 0:
        T = T[:, ::-1]
    return V * 1000.0, T


def write_stl(path, V, T):
    P3 = V[T]
    n = np.cross(P3[:, 1] - P3[:, 0], P3[:, 2] - P3[:, 0])
    ln = np.linalg.norm(n, axis=1)
    n = n / np.where(ln > 0, ln, 1.0)[:, None]
    rec = np.zeros(len(T), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    rec["n"] = n
    rec["v"] = P3
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(b"tangible-pixel-cube".ljust(80, b"\0"))
        f.write(np.uint32(len(T)).tobytes())
        f.write(rec.tobytes())
    os.replace(tmp, path)


def stl_triangles(path):
    """書き出した STL を読み直す（検査は書いたファイルから数える）"""
    with open(path, "rb") as f:
        d = f.read()
    n = int(np.frombuffer(d[80:84], dtype="<u4")[0])
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    return a["v"].astype(np.float64).reshape(-1, 3), np.arange(n * 3).reshape(-1, 3)


# =============================================================================================
# 形の検査（numpy）
# =============================================================================================
def weld(V, T, tol=WELD_MM):
    """近い頂点を 1 つにする。面積 0 の三角形は捨てる"""
    key = np.round(V / tol).astype(np.int64)
    u, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    Vw = V[first]
    Tw = inv.reshape(-1)[T]
    ok = (Tw[:, 0] != Tw[:, 1]) & (Tw[:, 1] != Tw[:, 2]) & (Tw[:, 0] != Tw[:, 2])
    return Vw, Tw[ok], np.nonzero(ok)[0]


def components(n_verts, T):
    parent = np.arange(n_verts)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b, c in T:
        for x, y in ((a, b), (b, c)):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry
    used = np.unique(T.ravel())
    return len({find(i) for i in used}), np.array([find(i) for i in range(n_verts)])


def topology(V, T):
    """非多様体辺 = 辺を共有する面が 2 枚でない辺。向きの食い違い = 同じ向きの有向辺が 2 回出る辺（法線の裏返り）"""
    Vw, Tw, _ = weld(V, T)
    de = np.concatenate([Tw[:, [0, 1]], Tw[:, [1, 2]], Tw[:, [2, 0]]])
    und = np.sort(de, axis=1)
    _, cnt = np.unique(und, axis=0, return_counts=True)
    nonman = int((cnt != 2).sum())
    _, cnt_dir = np.unique(de, axis=0, return_counts=True)
    inconsistent = int((cnt_dir > 1).sum())
    ncomp, _ = components(len(Vw), Tw)
    P3 = Vw[Tw]
    vol = float(np.einsum("ij,ij->i", P3[:, 0], np.cross(P3[:, 1], P3[:, 2])).sum() / 6.0)   # mm3
    area = float(0.5 * np.linalg.norm(np.cross(P3[:, 1] - P3[:, 0], P3[:, 2] - P3[:, 0]), axis=1).sum())
    return {"non_manifold_edges": nonman, "inconsistent_edges": inconsistent, "components": ncomp,
            "volume_cm3": round(vol / 1000.0, 4), "surface_cm2": round(area / 100.0, 3)}


def overhang(V, T, R=None, t=None, visible_fn=None):
    """刷る向き（V は print 姿勢、z=0 がベッド）で、水平から OVERHANG_DEG より寝た下向き面を数える。
    R, t: 組立 -> print の変換（p_print = R p_asm + t）。visible_fn(重心, 法線)（組立姿勢）が True の面を「見える面」とする。
    ベッドに接する面（3 頂点とも z≈0）は数えない"""
    Vw, Tw, _ = weld(V, T)
    P3 = Vw[Tw]
    nrm = np.cross(P3[:, 1] - P3[:, 0], P3[:, 2] - P3[:, 0])
    ar = 0.5 * np.linalg.norm(nrm, axis=1)
    un = nrm / np.where(ar > 0, 2 * ar, 1.0)[:, None]
    alpha = np.degrees(np.arccos(np.clip(-un[:, 2], -1.0, 1.0)))       # 法線と -Z の角（0 = 水平の下向き）
    zmin = Vw[:, 2].min()
    at_bed = P3[:, :, 2].max(axis=1) <= zmin + 0.02
    flag = (un[:, 2] < 0) & (alpha < OVERHANG_DEG - OVERHANG_TOL) & ~at_bed & (ar > 1e-9)
    idx = np.nonzero(flag)[0]
    out = {"threshold_deg": OVERHANG_DEG, "area_mm2": round(float(ar[idx].sum()), 3), "visible_area_mm2": 0.0, "faces": int(len(idx)), "clusters": []}
    if len(idx) == 0:
        return out
    cen = P3[idx].mean(axis=1)
    if R is not None:
        cen_a = (cen - t) @ R               # R^T (p - t)
        nrm_a = un[idx] @ R
    else:
        cen_a, nrm_a = cen, un[idx]
    vis = np.array([bool(visible_fn(c, n)) for c, n in zip(cen_a, nrm_a)]) if visible_fn else np.zeros(len(idx), dtype=bool)
    out["visible_area_mm2"] = round(float(ar[idx][vis].sum()), 3)
    # 辺でつながった面ごとにまとめる
    parent = list(range(len(idx)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    emap = {}
    for k, f in enumerate(idx):
        a, b, c = Tw[f]
        for e in ((a, b), (b, c), (c, a)):
            key = (min(e), max(e))
            if key in emap:
                rx, ry = find(k), find(emap[key])
                if rx != ry:
                    parent[rx] = ry
            else:
                emap[key] = k
    groups = {}
    for k in range(len(idx)):
        groups.setdefault(find(k), []).append(k)
    cl = []
    for ks in groups.values():
        ks = np.array(ks)
        a = float(ar[idx][ks].sum())
        pts = P3[idx][ks].reshape(-1, 3)
        pa = cen_a[ks]
        cl.append({"area_mm2": round(a, 3), "print_z_mm": [round(float(pts[:, 2].min()), 2), round(float(pts[:, 2].max()), 2)],
                   "assembly_min_mm": [round(float(v), 2) for v in pa.min(axis=0)], "assembly_max_mm": [round(float(v), 2) for v in pa.max(axis=0)],
                   "alpha_deg": [round(float(alpha[idx][ks].min()), 1), round(float(alpha[idx][ks].max()), 1)],
                   "visible_fraction": round(float(ar[idx][ks][vis[ks]].sum() / a), 3) if a > 0 else 0.0})
    cl.sort(key=lambda c: -c["area_mm2"])
    out["n_clusters"] = len(cl)
    out["clusters"] = cl[:8]
    return out


# =============================================================================================
# 計器の校正（答えの分かる形）
# =============================================================================================
def _clear_objects():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)


def calibrate():
    """答えの分かる形を同じ関数に通す。期待と食い違えば例外にして、本番の数字を信じない"""
    cal = []

    def check(name, got, expect, tol):
        ok = abs(got - expect) <= tol
        cal.append({"name": name, "got": round(float(got), 4), "expect": expect, "tol": tol, "pass": bool(ok)})

    # (1) 10mm の立方体: 体積 1.000 cm3、非多様体 0、連結 1、下向きの張り出し 0（底はベッドに接する）
    c = S.finish(S.box(0, 10, 0, 10, 0, 10, "cal_cube"), "cal_cube")        # 作図は mm、出口で m（部品と同じ扱い）
    V, T = tris_mm(c)
    tp = topology(V, T)
    check("立方体の体積 cm3", tp["volume_cm3"], 1.0, 1e-4)
    check("立方体の非多様体辺", tp["non_manifold_edges"], 0, 0)
    check("立方体の連結成分", tp["components"], 1, 0)
    check("立方体の向きの食い違い", tp["inconsistent_edges"], 0, 0)
    check("立方体の張り出し面積 mm2", overhang(V, T)["area_mm2"], 0.0, 1e-6)
    # (2) 面を 1 枚（三角形 2 つ）抜いた立方体: 非多様体辺 4（穴の縁）
    Tm = T[[i for i in range(len(T)) if not np.allclose(V[T[i]][:, 2], 10.0)]]
    check("上面を抜いた立方体の非多様体辺", topology(V, Tm)["non_manifold_edges"], 4, 0)
    # (3) 離れた 2 つの立方体: 連結成分 2、体積 2cm3
    d = S.finish(S.box(20, 30, 0, 10, 0, 10, "cal_cube2"), "cal_cube2")
    V2, T2 = tris_mm(d)
    Vj = np.concatenate([V, V2])
    Tj = np.concatenate([T, T2 + len(V)])
    tj = topology(Vj, Tj)
    check("離れた 2 立方体の連結成分", tj["components"], 2, 0)
    check("離れた 2 立方体の体積 cm3", tj["volume_cm3"], 2.0, 1e-4)
    # (4) T 字（茎 10x10x10 の上に 30x30x5 の板）: 板の下面の張り出しは 30*30 - 10*10 = 800mm2（水平）
    st = S.box(10, 20, 10, 20, 0, 10.5, "cal_stem")
    pl = S.box(0, 30, 0, 30, 10, 15, "cal_plate")
    S.union(st, [pl], "cal_t")
    S.finish(st, "cal_t")
    Vt, Tt = tris_mm(st)
    ot = overhang(Vt, Tt)
    check("T 字の張り出し面積 mm2（期待 800）", ot["area_mm2"], 800.0, 0.5)
    # 見える面の判定の校正: 全部見える・全部見えない
    check("T 字の張り出しが全部見える扱いのとき", overhang(Vt, Tt, visible_fn=lambda c, n: True)["visible_area_mm2"], 800.0, 0.5)
    check("T 字の張り出しが全部見えない扱いのとき", overhang(Vt, Tt, visible_fn=lambda c, n: False)["visible_area_mm2"], 0.0, 1e-6)
    # (5) 下面が水平から 40 度 / 50 度の斜面の三角柱: 40 度は数え、50 度は数えない（45 度の境）
    for ang, expect_flag in ((40.0, True), (50.0, False), (45.0, False)):
        a = math.radians(ang)
        L = 30.0
        poly = [(0.0, 0.0), (L, L * math.tan(a)), (L, L * math.tan(a) + 40.0), (0.0, 40.0)]
        w = S.finish(S.prism(poly, "y", 0.0, 20.0, "cal_wedge"), "cal_wedge")
        Vw_, Tw_ = tris_mm(w)
        ow = overhang(Vw_, Tw_)
        want = (L / math.cos(a)) * 20.0 if expect_flag else 0.0
        check(f"水平から {ang:.0f} 度の下向きの斜面（{'数える' if expect_flag else '数えない'}）", ow["area_mm2"], want, 0.5)
    # (6) 回転して置いた張り出し: T 字を X 軸まわり 180 度回すと板は下から上になり、張り出しは茎の先（上向き 100mm2 の面）だけ。数えるのは 0
    R = np.array(Euler((math.pi, 0, 0), "XYZ").to_matrix())
    Vr = Vt @ R.T
    Vr[:, 2] -= Vr[:, 2].min()
    check("T 字を逆さにした張り出し面積 mm2", overhang(Vr, Tt)["area_mm2"], 0.0, 1e-6)
    _clear_objects()
    bad = [c for c in cal if not c["pass"]]
    for c in cal:
        print(f"  [{'OK' if c['pass'] else 'NG'}] {c['name']}: {c['got']}（期待 {c['expect']} ± {c['tol']}）")
    if bad:
        raise SystemExit("校正に失敗: " + "; ".join(c["name"] for c in bad))
    return cal


# =============================================================================================
# 部品の収集
# =============================================================================================
def load_moving():
    if importlib.util.find_spec("parts_moving") is None:
        print("警告: parts_moving.py がありません。静止部品だけで通します")
        return None
    import parts_moving
    return parts_moving


def ids_in_order(built):
    order = list(P.PART_IDS) + [i for i in P.EXTRA_PART_IDS if i not in P.PART_IDS]
    seen = [i for i in order if i in built]
    extra = [i for i in built if i not in order]
    if extra:
        print("警告: params.PART_IDS に無い部品:", ", ".join(extra))
    missing = [i for i in order if i not in built]
    return seen + extra, missing


def pose_of(entry):
    if not entry:
        return None
    for key in ("rot_deg", "rotation_deg", "euler_deg", "rot"):
        if key in entry:
            return [float(v) for v in entry[key]]
    return [0.0, 0.0, 0.0]


def print_transform(V, rot_deg):
    """組立姿勢の頂点 V（mm）-> 刷る向き。回転オイラー XYZ（度）、最下点 z=0、XY の外接の中心を原点。(Vp, R, t) を返す"""
    R = np.array(Euler([math.radians(a) for a in rot_deg], "XYZ").to_matrix(), dtype=np.float64)
    Vp = V @ R.T
    lo, hi = Vp.min(axis=0), Vp.max(axis=0)
    t = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    return Vp + t, R, t


def bbox_info(V):
    lo, hi = V.min(axis=0), V.max(axis=0)
    return {"min_mm": [round(float(v), 3) for v in lo], "max_mm": [round(float(v), 3) for v in hi],
            "size_mm": [round(float(v), 3) for v in hi - lo]}


LABELS = {
    "housing": "外装（底と四方の壁）", "bezel": "ベゼル（天面の格子）", "guide_plate": "案内板", "sg92r": "SG92R（本体と配線）",
    "sg92r_horn": "SG92R ホーン", "horn_coupler": "受け（ホーンを包む半円歯車）", "phase_comb": "位相合わせ治具（組立のみ）",
}
COLORS = [
    ("housing", "#d8d4cc"), ("bezel", "#bfc9d0"), ("guide_plate", "#9fb3bf"), ("sg92r_horn", "#f4f4f4"), ("sg92r", "#37474f"),
    ("horn_coupler", "#a1887f"), ("phase_comb", "#ffd54f"), ("shaft_clip_", "#ab47bc"), ("servo_clip_", "#f06292"), ("shaft_", "#5c6bc0"), ("gear_", "#26a69a"),
    ("cam_", "#ef5350"), ("pixel_", "#e69f00"),
]
EXPLODE = [  # 組立姿勢からの分解の向きと量（mm）
    ("bezel", [0, 0, 110]), ("pixel_", [0, 0, 70]), ("guide_plate", [0, 0, 45]), ("phase_comb", [0, 0, 30]),
    ("shaft_clip_", [0, 0, 20]), ("servo_clip_", [0, 0, 40]), ("shaft_", [0, 0, 20]), ("gear_", [0, 0, 20]), ("cam_", [0, 0, 20]),
    ("horn_coupler", [30, 0, 0]), ("sg92r_horn", [60, 0, 0]),
]


def label_of(pid):
    if pid in LABELS:
        return LABELS[pid]
    p = pid.split("_")
    if pid.startswith("servo_clip_"):
        return f"サーボの押さえクリップ {p[-1]}"
    if pid.startswith("shaft_clip_"):
        return f"C クリップ {p[-1]}"
    if p[0] == "shaft":
        return f"カム軸 {p[1]}"
    if p[0] == "gear":
        return f"歯車 {p[1]}"
    if p[0] == "cam":
        return f"カム 列{p[1]} 行{p[2]}"
    if p[0] == "pixel":
        return f"画素 列{p[1]} 行{p[2]}"
    return pid


def lookup(table, pid, default):
    for key, val in table:
        if pid == key or (key.endswith("_") and pid.startswith(key)):
            return val
    return default


# =============================================================================================
# 本体
# =============================================================================================
def main():
    t0 = time.time()
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(os.path.dirname(EXPORT_ALL), exist_ok=True)
    _clear_objects()

    print("== 校正 ==")
    cal = calibrate()

    print("== 部品を作る ==")
    built = dict(S.build_static())
    poses = dict(S.PRINT_POSE)
    visible_fns = dict(S.VISIBLE_FACE)
    stock_ids = {"sg92r", "sg92r_horn"}
    jig_ids = {"phase_comb"}
    moving = load_moving()
    moving_status = {"present": moving is not None, "built": False, "error": None if moving is not None else "parts_moving.py がありません"}
    if moving is not None:
        try:
            mv = moving.build_moving()
        except Exception as e:                # 未完成の間は静止部品だけで通す。握りつぶさず、メッセージ・報告・最後の警告に残す
            traceback.print_exc()
            keep = set(built.values())
            for o in list(bpy.data.objects):
                if o not in keep:
                    bpy.data.objects.remove(o, do_unlink=True)
            moving_status["error"] = f"{type(e).__name__}: {e}"
            print(f"警告: parts_moving.build_moving() が失敗しました（{moving_status['error']}）。静止部品だけで通します")
            mv = {}
        else:
            moving_status["built"] = True
        dup = set(mv) & set(built)
        if dup:
            raise SystemExit(f"parts_moving と parts_static で id が重なっています: {sorted(dup)}")
        built.update(mv)
        if moving_status["built"]:
            poses.update(getattr(moving, "PRINT_POSE", {}) or {})
            visible_fns.update(getattr(moving, "VISIBLE_FACE", {}) or {})
            stock_ids |= set(getattr(moving, "STOCK_IDS", ()) or ())
            jig_ids |= set(getattr(moving, "JIG_IDS", ()) or ())
    ids, missing = ids_in_order(built)
    if moving_status["built"] and missing:
        print("警告: params.PART_IDS にあるのに作られていない部品:", ", ".join(missing))

    print(f"== 書き出し（{len(ids)} 部品）==")
    report_parts = {}
    manifest_parts = []
    merged_V, merged_T = [], []
    offs = 0
    for pid in ids:
        ob = built[pid]
        V, T = tris_mm(ob)
        asm_path = os.path.join(BUILD, f"{pid}.stl")
        write_stl(asm_path, V, T)
        Va, Ta = stl_triangles(asm_path)           # 検査は書いたファイルから
        rec = {"assembly": bbox_info(Va)}
        if pid in stock_ids:
            rec["stock"] = True                  # 既製部品。連結成分は工場の姿（SG92R は本体と配線の 2 つ）で、数えない
        rec.update(topology(Va, Ta))
        pose = poses.get(pid)
        print_rel = None
        if pose is not None and pid not in stock_ids:
            rot = pose_of(pose)
            Vp, R, t = print_transform(Va, rot)
            pp = os.path.join(BUILD, f"print_{pid}.stl")
            write_stl(pp, Vp, Ta)
            Vq, Tq = stl_triangles(pp)
            oh = overhang(Vq, Tq, R, t, visible_fns.get(pid))
            rec["print"] = {"rot_deg": rot, "reason": pose.get("reason", ""), "support": pose.get("support", ""),
                            "bbox_mm": bbox_info(Vq), "overhang": oh}
            print_rel = f"build/print_{pid}.stl"
        else:
            rec["print"] = None
        report_parts[pid] = rec
        mp = {"id": pid, "label": label_of(pid), "assembly": f"build/{pid}.stl", "print": print_rel,
              "color": lookup(COLORS, pid, "#cccccc"), "explode": lookup(EXPLODE, pid, [0, 0, 0])}
        if pid in ("housing", "bezel"):
            mp["exterior"] = True
        if pid in jig_ids:
            mp["jig"] = True
        if pid in stock_ids:
            mp["stock"] = True
        manifest_parts.append(mp)
        if pid not in jig_ids:
            merged_V.append(Va)
            merged_T.append(Ta + offs)
            offs += len(Va)

    write_stl(EXPORT_ALL, np.concatenate(merged_V), np.concatenate(merged_T))

    n_print = sum(1 for m in manifest_parts if m["print"])
    all_min = np.min([report_parts[i]["assembly"]["min_mm"] for i in ids if i not in jig_ids], axis=0)
    all_max = np.max([report_parts[i]["assembly"]["max_mm"] for i in ids if i not in jig_ids], axis=0)
    manifest = {
        "meta": {
            "model": MODEL,
            "dimensions_mm": [round(float(v), 1) for v in (all_max - all_min) + np.array([0.0, 0.0, P.H_MAX * 1000.0])],   # 画素の最大の出っ張り +3mm を高さに足す
            "exterior_parts": ["housing", "bezel"],
            "description": "SG92R 1 台で、5x5 の画素が天面で上下する立方体。画素は重力でカムに載り、高さの表（patterns.py）がカムの形で決まる",
            "decisions": [
                "外形 96mm の立方体。画素の出っ張り +3mm で 99mm（10cm 以下）",
                "外の稜は 1.0mm の 45 度面取りにそろえ、外装とベゼルの継ぎ目だけ面取りせず 1 本の水平線にした",
                "ベゼルは見える上面を下にして刷る。縁の爪（食い込み 0.25mm）が壁の内側の窪みに嵌まり、壁のたわみ（ひずみ 0.2% 未満）で着脱する",
                "SG92R は取付耳を 2 枚の柵で挟んで落とし込む（潰しリブで保持、奥の壁で前後を止める）。ねじ・接着なし",
            ],
            "limitations": ["寸法の仮値（潰しリブの潰し代・柵の隙間・爪の食い込み）は実物で合わせる"],
            "n_parts": len(manifest_parts),
            "n_print": n_print,
        },
        "parts": manifest_parts,
    }
    _dump(os.path.join(BUILD, "manifest.json"), manifest)
    report = {
        "model": MODEL,
        "generated_by": "models/tangible-pixel-cube/model.py",
        "calibration": cal,
        "overhang_rule": f"刷る向きで、下向きの面のうち水平から {OVERHANG_DEG:.0f} 度より寝ているもの（{OVERHANG_DEG - OVERHANG_TOL:.1f} 度未満）。ベッドに接する面は数えない",
        "parts_moving": moving_status,
        "parts_not_built": missing,                       # params.PART_IDS にあるのに作られなかった部品（parts_moving が通らないとき全部）
        "parts": report_parts,
        "totals": {"n_parts": len(ids), "n_print": n_print,
                   "non_manifold_edges": sum(r["non_manifold_edges"] for r in report_parts.values()),
                   "bad_components": [i for i, r in report_parts.items() if r["components"] != 1 and i not in stock_ids],   # 既製部品（SG92R は本体と配線の 2 つ）は数えない
                   "negative_volume": [i for i, r in report_parts.items() if r["volume_cm3"] <= 0]},
    }
    _dump(os.path.join(BUILD, "model_report.json"), report)

    print(f"{'id':16s} {'外接(mm)':26s} {'体積cm3':>8s} {'非多様体':>6s} {'連結':>4s}  刷る向きの張り出し(mm2 / うち見える)")
    shown = 0
    for pid in ids:
        r = report_parts[pid]
        if pid.startswith(("pixel_", "cam_")) and shown > 6 and pid not in ("pixel_4_4", "cam_4_4"):
            continue
        sz = r["assembly"]["size_mm"]
        oh = r["print"]["overhang"] if r["print"] else None
        ohs = f"{oh['area_mm2']:.1f} / {oh['visible_area_mm2']:.1f}" if oh else "刷らない"
        print(f"{pid:16s} {sz[0]:7.2f}x{sz[1]:7.2f}x{sz[2]:7.2f}  {r['volume_cm3']:8.3f} {r['non_manifold_edges']:6d} {r['components']:4d}  {ohs}")
        shown += 1
    tot = report["totals"]
    print(f"部品 {tot['n_parts']}、印刷 {tot['n_print']}、非多様体辺の合計 {tot['non_manifold_edges']}、連結成分が 1 でない: {tot['bad_components']}、体積が 0 以下: {tot['negative_volume']}")
    print(f"外接（治具を除く全部品、高さは画素 +3mm を含む）: {manifest['meta']['dimensions_mm']} mm、{time.time() - t0:.1f}s")
    print(f"書き出し: {BUILD} / {EXPORT_ALL}")
    if not moving_status["built"]:
        print(f"警告: 動く部品が入っていません（{moving_status['error']}）。作られなかった部品 {len(missing)} 個")
    if tot["non_manifold_edges"] or tot["bad_components"] or tot["negative_volume"]:
        raise SystemExit("形の検査に不合格の部品があります（model_report.json を見る）")


def _dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


if __name__ == "__main__":
    main()
