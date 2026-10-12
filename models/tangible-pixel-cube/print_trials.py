"""試し刷りの小片を作る（Blender の Python で走らせる）。

    "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python-exit-code 1 \
        --python models/tangible-pixel-cube/print_trials.py

嵌め合いが不確かな箇所だけを、実部品（build/<id>.stl、組立姿勢）と箱（組立姿勢の座標）の INTERSECT で切り出し、
元の部品と同じ刷る向き（回転は build/print_<id>.stl との剛体対応から求める）に置いて prints/tangible-pixel-cube/trial/ へ書く。
切らない小片（box が None）は刷る向きの STL をそのまま写す。

出力: prints/tangible-pixel-cube/trial/<名前>.stl と trial_pieces.json（切り出しの箱・確かめること）
"""
import json
import os
import shutil
import sys

import bmesh
import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import print_kit as K  # noqa: E402
import params as P  # noqa: E402
import parts_static as S  # noqa: E402

BUILD = os.path.join(HERE, "build")
OUT = os.path.join(ROOT, "prints", "tangible-pixel-cube", "trial")

def mm1(v):
    """params の m を mm の文字列へ（寸法は params から f-string で作る。書き写さない）。"""
    return f"{v * 1000:.2f}".rstrip("0").rstrip(".")


def foot_box(pad_xy):
    """画素 (2,2) の足の外接（組立姿勢）を pad_xy だけ広げた XY と、足から茎の下までの Z。"""
    cx, cy = 0.0, 0.0
    hx, hy = P.FOOT_X * 1000 / 2 + pad_xy, P.FOOT_Y * 1000 / 2 + pad_xy
    return cx - hx, cx + hx, cy - hy, cy + hy


_ZC = P.CAM_AXIS_Z * 1000
_PX = S.PLATE_Z1  # 案内板の上面（mm）
_HW = P.HOLE_W * 1000 / 2
_FX0, _FX1, _FY0, _FY1 = foot_box(0.3)

# 組立姿勢の座標（mm）。box = (x0, x1, y0, y1, z0, z1)。plate = どの試し刷りのプレートへ載せるか。
# targets = 狙った場所の箱（組立姿勢）。box が全部含み（切る面には 0.3mm 以上の余裕）、元の部品に形がある（三角形が掛かる）ことを流すたびに確かめる
TRIALS = [
    # --- 試し刷り 1: 回す・噛み合わせる部分
    {"name": "horn_coupler", "src": "horn_coupler", "box": None, "plate": 1, "targets": [],
     "checks": f"ホーン（SG92R 付属）が受けのポケットに嵌まるか（ホーンとの隙間 片側 {mm1(P.HORN_CLR)}mm、口の面取り {mm1(P.FIRST_LAYER_CHAMFER)}mm）。"
               f"半円歯車（{P.SERVO_Z} 歯）と中央の軸の歯車（{P.CHAIN_Z} 歯）の噛み合い。支えのピン Ø{mm1(P.RECV_PIN_D)}"},
    {"name": "shaft_2_plusX_end", "src": "shaft_2", "box": (29.0, 44.7, -6.0, 6.0, 44.0, 60.0), "plate": 1,
     "targets": [("鍔・丸・歯車の座", (P.GEAR_X0 * 1000, P.JOURNAL_END * 1000, -5.5, 5.5, _ZC - 5.5, _ZC + 5.5))],
     "checks": f"軸の +X 端（六角 AF{mm1(P.SHAFT_AF)} の切り落とし面（鍵）、鍔、丸 Ø{mm1(P.JOURNAL_D)}）。歯車（穴の二面幅 {mm1(P.SHAFT_BORE_AF)}、"
               f"潰しリブ 幅{mm1(P.HEX_RIB_W)}・潰し代{mm1(P.HEX_RIB_CRUSH)}）が鍔まで入るか、カムが通るか、丸が外装の U 溝（幅 {mm1(P.U_SLOT_W)}）へ落ちるか"},
    {"name": "shaft_2_minusX_end", "src": "shaft_2", "box": (-44.7, -30.0, -6.0, 6.0, 44.0, 60.0), "plate": 1,
     "targets": [("C クリップの溝と丸", (-P.JOURNAL_END * 1000, -33.0, -3.9, 3.9, _ZC - 3.9, _ZC + 3.9))],
     "checks": f"軸の -X 端（裸の六角・C クリップの溝（底の半径 {mm1(P.CLIP_GROOVE_R)}）・丸 Ø{mm1(P.JOURNAL_D)}）。"
               f"C クリップ（厚み {mm1(P.CLIP_T)}）が溝へ嵌まるか"},
    {"name": "cam_4_2", "src": "cam_4_2", "box": None, "plate": 1, "targets": [],
     "checks": f"カムの六角穴（二面幅 {mm1(P.SHAFT_BORE_AF)}、潰しリブ 幅{mm1(P.HEX_RIB_W)}・潰し代{mm1(P.HEX_RIB_CRUSH)}、"
               f"穴の口の面取り {mm1(P.FIRST_LAYER_CHAMFER)}）が軸の六角へ入るか。回転ガタ。軸の切り落とし面（鍵）に穴の出っ張りが当たる向きだけ入るか"},
    {"name": "gear_2", "src": "gear_2", "box": None, "plate": 1, "targets": [],
     "checks": f"歯車（{P.CHAIN_Z} 歯、歯幅 {mm1(P.GEAR_T)}）の六角穴（潰しリブ）と鍵の向き。歯車どうしの噛み合い（2 枚並べて回す）"},
    {"name": "shaft_clip_2", "src": "shaft_clip_2", "box": None, "plate": 1, "targets": [],
     "checks": f"C クリップ（厚み {mm1(P.CLIP_T)}）の嵌め外しの固さ。脚のしなり"},
    # --- 試し刷り 2: 外装・案内・画素
    {"name": "housing_Uslot_shaft1_plusX", "src": "housing", "box": (43.0, 48.1, -25.5, -8.5, 44.5, 58.5), "plate": 2,
     "targets": [("U 溝・帯・栓の縦溝", (P.PAD_X0 * 1000, S.IX + S.U_RECESS_D, -17.0 - 2.9, -17.0 + 2.9, _ZC - 5.0, S.U_RECESS_TOP_Z))],
     "checks": f"外装の U 溝（幅 {mm1(P.U_SLOT_W)}、軸の丸 Ø{mm1(P.JOURNAL_D)}）へ軸の +X 端の丸が落ちるか。帯の 45 度面取り。"
               f"案内板の栓（隙間 {mm1(P.HOLD_GAP)}）が入る縦溝（深さ {S.U_RECESS_D}、壁は {S.HALF - S.IX - S.U_RECESS_D:.1f}mm 残る）"},
    {"name": "housing_servo_block_minusY", "src": "housing", "box": (21.4, 32.4, -25.0, -16.4, 0.0, 28.0), "plate": 2,
     "targets": [("耳の受け（柵・奥の壁）", (S.BLOCK_X0, S.BLOCK_X1, S._servo_block_y(-1)[0], S._servo_block_y(-1)[1], S.FLOOR, S.FENCE_TOP))],
     "checks": f"サーボの取付耳（-Y 側）を挟む柵（厚み {S.EAR_FENCE_T}、耳との隙間 {S.EAR_GAP}、潰しリブ 高さ{S.EAR_RIB_H}・幅{S.EAR_RIB_W}）。"
               f"実物の SG92R の耳が入るか、保持の固さ。押さえクリップ用の側面の窪み（深さ {S.CLIP_GROOVE_D}）"},
    {"name": "servo_clip_0", "src": "servo_clip_0", "box": None, "plate": 2, "targets": [],
     "checks": f"押さえクリップ（幅 {S.CLIP_W}）の爪（出 {S.CLIP_BARB_H}、平らな頂 {S.CLIP_BARB_FLAT}）が受けの側面の窪み（深さ {S.CLIP_GROOVE_D}）へ嵌まるか。上から押し込む力"},
    {"name": "guide_plate_cell_2_2", "src": "guide_plate", "box": (-11.5, 11.5, -13.0, 13.0, 75.4, 83.6), "plate": 2,
     "targets": [("十字穴", (-_HW - 0.3, _HW + 0.3, _FY0, _FY1, 76.0, _PX))],
     "checks": f"案内板の十字穴（茎の穴 {mm1(P.HOLE_W)} 角、足の溝 {mm1(P.SLOT_X)} x {mm1(P.SLOT_Y)}）へ画素の茎と足（{mm1(P.FOOT_X)} x {mm1(P.FOOT_Y)}）が通るか。"
               f"板の上面側の穴の縁の面取り {S.HOLE_MOUTH}。隣の溝との桟（params: 2 x {mm1(P.ROW_SHIFT)} - {mm1(P.SLOT_X)}）"},
    {"name": "guide_plate_tongue_plusX", "src": "guide_plate", "box": (38.0, 45.5, -16.0, -1.0, 72.0, 83.6), "plate": 2,
     "targets": [("舌と爪（-Y 側）", (S.IX - S.FIT - S.TONGUE_T - S.TONGUE_SLIT, S.IX - S.FIT + S.HOOK_H, -8.0 - S.TONGUE_L / 2 - S.TONGUE_SLIT,
                                  -8.0 + S.TONGUE_L / 2, _PX - S.TONGUE_H - S.TONGUE_SLIT, _PX))],
     "checks": f"案内板の舌（厚み {S.TONGUE_T}、長さ {S.TONGUE_L}、切り込み {S.TONGUE_SLIT}、根元だけ板につながる）と爪（出 {S.HOOK_H}、先の面 {S.HOOK_TIP_H}）。"
               f"端壁の窪み（深さ {S.POCKET_PLATE_DEPTH}）へ入れて、面内でしなる量と引き抜く力"},
    {"name": "pixel_2_2_top", "src": "pixel_2_2", "box": (-10.0, 10.0, -12.0, 12.0, 80.0, 96.1), "plate": 2,
     "targets": [("頭・つば・茎の先", (-P.FLANGE_W * 500, P.FLANGE_W * 500, -P.FLANGE_W * 500, P.FLANGE_W * 500, 80.5, P.BEZEL_Z1 * 1000))],
     "checks": f"画素の頭（{mm1(P.HEAD)}mm 角、上縁の面取り {mm1(P.FIRST_LAYER_CHAMFER)}）がベゼルの窓（{mm1(P.WINDOW)}mm 角）へ入るか。"
               f"つば（{mm1(P.FLANGE_W)} 角）。茎（{mm1(P.TOWER_W)} 角）の先が案内板の穴（{mm1(P.HOLE_W)}）へ入るか"},
    {"name": "pixel_2_2_foot", "src": "pixel_2_2", "box": (-10.0, 10.0, -12.0, 12.0, 59.8, 66.0), "plate": 2,
     "targets": [("足", (-P.FOOT_X * 500, P.FOOT_X * 500, -P.FOOT_Y * 500, P.FOOT_Y * 500, P.CAM_TOP_FLUSH * 1000, P.CAM_TOP_FLUSH * 1000 + P.FOOT_FLAT * 1000 + 3.0))],
     "checks": f"画素の足（{mm1(P.FOOT_X)} x {mm1(P.FOOT_Y)}）が案内板の十字溝（{mm1(P.SLOT_X)} x {mm1(P.SLOT_Y)}）を通るか。足の 45 度の広がり"},
    {"name": "bezel_window_2_2", "src": "bezel", "box": (-9.5, 9.5, -9.5, 9.5, 92.0, 96.1), "plate": 2,
     "targets": [("窓と桟", (-P.WINDOW * 500 - 0.3, P.WINDOW * 500 + 0.3, -P.WINDOW * 500 - 0.3, P.WINDOW * 500 + 0.3, P.BEZEL_Z0 * 1000, P.BEZEL_Z1 * 1000))],
     "checks": f"ベゼルの窓 {mm1(P.WINDOW)}mm と桟 {mm1(P.BEZEL_BAR)}mm（params.PRINT_EXCEPTIONS: "
               f"{'bezel_bar_1.6 を例外として許可' if 'bezel_bar_1.6' in P.PRINT_EXCEPTIONS else '例外なし'}）の見た目と固さ。窓の上縁の面取り {S.WIN_MOUTH}、下縁 {S.WIN_MOUTH_IN}"},
    {"name": "bezel_barb_plusX", "src": "bezel", "box": (41.0, 48.1, -12.0, 12.0, 86.0, 96.1), "plate": 2,
     "targets": [("縁と爪", (S.IX - 3.0, S.IX, -S.BARB_L / 2, S.BARB_L / 2, S.BARB_Z - S.BARB_FLAT / 2 - S.BARB_H, S.BARB_Z + S.BARB_FLAT / 2 + S.BARB_H))],
     "checks": f"ベゼルの縁（厚み {S.LIP_T}）の爪（±X の縁、出 {S.BARB_H}、壁への食い込み {S.BARB_H - S.FIT:.2f}mm、長さ {S.BARB_L:.0f}）。"
               "下の housing_endwall_pockets_plusX の窪みへ嵌まる固さ"},
    {"name": "housing_endwall_pockets_plusX", "src": "housing", "box": (42.5, 48.1, -16.0, 16.0, 80.0, 93.1), "plate": 2,
     "targets": [("ベゼルの爪の窪み", (S.IX, S.IX + S.POCKET_DEPTH, -S.POCKET_L / 2, S.POCKET_L / 2, S.BARB_Z - S.BARB_FLAT / 2 - S.POCKET_DEPTH, S.BARB_Z + S.BARB_FLAT / 2 + S.POCKET_DEPTH)),
                 ("案内板の爪の窪み（+Y）", (S.IX, S.IX + S.POCKET_PLATE_DEPTH, 8.0 + S.HOOK_Y0 - S.POCKET_PLATE_PAD, 8.0 + S.HOOK_Y1 + S.POCKET_PLATE_PAD, 82.6, 83.4)),
                 ("指の掛かり（+Y）", (S.HALF - S.FINGER_D, S.HALF, 8.5 - S.FINGER_W / 2, 8.5 + S.FINGER_W / 2, S.Z_SEAM - S.FINGER_H, S.Z_SEAM))],
     "checks": f"+X 端壁（{S.HALF - S.IX:.0f}mm）の窪み 2 種: ベゼルの爪の窪み（深さ {S.POCKET_DEPTH}、壁は {S.HALF - S.IX - S.POCKET_DEPTH:.1f} 残る、z{S.BARB_Z:.0f}）と"
               f"案内板の爪の窪み（深さ {S.POCKET_PLATE_DEPTH}、y±{abs(S.TONGUE_YC[1]):.0f} 付近）。外側の指の掛かり（深さ {S.FINGER_D}、残り {S.HALF - S.IX - S.FINGER_D:.1f}）"},
]


def check_targets(spec, A):
    """狙った場所が切り出しの箱に（切る面には 0.3mm の余裕をつけて）含まれ、元の部品に形があるかを確かめる。"""
    if spec["box"] is None:
        return
    lo, hi = A.reshape(-1, 3).min(axis=0), A.reshape(-1, 3).max(axis=0)
    box = spec["box"]
    for label, tb in spec["targets"]:
        for ax in range(3):
            for side in (0, 1):
                bval = box[2 * ax + side]
                if not (lo[ax] + 0.05 < bval < hi[ax] - 0.05):
                    continue                                    # 部品の外の面は切っていない
                tval = tb[2 * ax + side]
                inside = (tval - bval) if side == 0 else (bval - tval)
                if inside < 0.3 - 1e-9:
                    raise SystemExit(f"{spec['name']}: 狙い「{label}」が箱の {'xyz'[ax]}{'-+'[side]} 側の面に足りない（余裕 {inside:.2f}mm < 0.3）")
        tl, th_ = np.array(tb[0::2]), np.array(tb[1::2])
        tri_lo, tri_hi = A.min(axis=1), A.max(axis=1)
        hit = np.all((tri_hi >= tl) & (tri_lo <= th_), axis=1).sum()
        if hit == 0:
            raise SystemExit(f"{spec['name']}: 狙い「{label}」の場所に元の部品の形が無い（形が動いた？）")
    print(f"      狙い {len(spec['targets'])} 個を箱が含み、元の部品に形がある")


def read_tris(path):
    return K.read_stl(path)


def box_cut(tris, box):
    """三角形（asm 座標）を箱で切る（INTERSECT / EXACT）。返り値は (n,3,3)。"""
    verts = tris.reshape(-1, 3)
    uniq, inv = np.unique(np.round(verts, 4), axis=0, return_inverse=True)
    faces = inv.reshape(-1, 3)
    ok = ~((faces[:, 0] == faces[:, 1]) | (faces[:, 1] == faces[:, 2]) | (faces[:, 0] == faces[:, 2]))
    mesh = bpy.data.meshes.new("src")
    mesh.from_pydata(uniq.tolist(), [], faces[ok].tolist())
    mesh.update()
    src = bpy.data.objects.new("src", mesh)
    bpy.context.scene.collection.objects.link(src)
    x0, x1, y0, y1, z0, z1 = box
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 if v.co.x < 0 else x1
        v.co.y = y0 if v.co.y < 0 else y1
        v.co.z = z0 if v.co.z < 0 else z1
    cm = bpy.data.meshes.new("cut")
    bm.to_mesh(cm)
    bm.free()
    cutter = bpy.data.objects.new("cut", cm)
    bpy.context.scene.collection.objects.link(cutter)
    mod = src.modifiers.new("i", "BOOLEAN")
    mod.operation = "INTERSECT"
    mod.object = cutter
    mod.solver = "EXACT"
    dg = bpy.context.evaluated_depsgraph_get()
    ev = src.evaluated_get(dg)
    me = ev.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    out = np.array([[tuple(v.co) for v in f.verts] for f in bm.faces], dtype=float)
    bm.free()
    ev.to_mesh_clear()
    bpy.data.objects.remove(src, do_unlink=True)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    report = {}
    for spec in TRIALS:
        src = spec["src"]
        A = read_tris(os.path.join(BUILD, f"{src}.stl"))
        Pr = read_tris(os.path.join(BUILD, f"print_{src}.stl"))
        print(f"  {spec['name']}")
        check_targets(spec, A)
        out_path = os.path.join(OUT, f"{spec['name']}.stl")
        if spec["box"] is None:
            shutil.copyfile(os.path.join(BUILD, f"print_{src}.stl"), out_path)
            T = Pr
            R, t, resid, _, _, det = K.rigid_fit(A, Pr)
            note = "切らずに刷る向きの STL を写した"
        else:
            R, t, resid, _, _, det = K.rigid_fit(A, Pr)
            if resid > 1e-3 or det < 0:
                raise SystemExit(f"{src}: 刷る向きへの対応が崩れている（残差 {resid}）")
            C = box_cut(A, spec["box"])
            if len(C) == 0:
                raise SystemExit(f"{spec['name']}: 切り出しが空")
            T = C @ R.T                                   # 回転だけ（元の部品と同じ刷る向き）
            shift = np.zeros(3)
            shift[2] = -T[:, :, 2].min()
            T[:, :, 2] += shift[2]
            lo = T.reshape(-1, 3).min(axis=0)
            hi = T.reshape(-1, 3).max(axis=0)
            shift[0] = -(lo[0] + hi[0]) / 2.0
            shift[1] = -(lo[1] + hi[1]) / 2.0
            T[:, :, 0] += shift[0]
            T[:, :, 1] += shift[1]
            t = shift                                     # 切り出しの刷る向き = R 組立姿勢 + t
            K.write_stl(out_path, T)
            note = f"{src} を箱 {spec['box']}（組立姿勢の座標）で切り出し"
        S = K.Solid(T)
        topo = S.topology()
        report[spec["name"]] = {
            "src": src, "box_asm_mm": spec["box"], "plate": spec["plate"], "checks": spec["checks"], "note": note,
            "file": os.path.relpath(out_path, ROOT).replace("\\", "/"),
            "size_mm": [round(float(v), 2) for v in (S.hi - S.lo)], "volume_cm3": round(S.volume() / 1000.0, 4),
            "topology": topo, "to_piece": {"R": np.asarray(R).tolist(), "t": [float(v) for v in t]}}
        print(f"  {spec['name']:30s} {report[spec['name']]['size_mm']} {report[spec['name']]['volume_cm3']:.3f}cm3 "
              f"開いた辺 {topo['open_edges']} 連結 {topo['components']}")
    path = os.path.join(OUT, "trial_pieces.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


if __name__ == "__main__":
    main()
