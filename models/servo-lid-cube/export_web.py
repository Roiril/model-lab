"""検証ページ（reports/2026-10-09_servo-lid-cube.html）に埋め込むデータを作る。Blender 不要。

    py -3.11 models/servo-lid-cube/export_web.py

build/ の組んだ姿勢の STL（mm）を Int16（0.005mm 刻み）＋ Uint16 の添字に詰め、
運動学の表・検証結果・シミュレーションの波形と一緒に build/web_data.js へ書く。
"""
import base64
import json
import math
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import linkage as K  # noqa: E402
import params as P  # noqa: E402

BUILD = os.path.join(HERE, "build")
Q = 0.005


def load(name):
    raw = open(os.path.join(BUILD, f"{name}.stl"), "rb").read()
    n = struct.unpack("<I", raw[80:84])[0]
    idx, verts, tris = {}, [], []
    for i in range(n):
        o = 84 + 50 * i + 12
        f = struct.unpack("<9f", raw[o:o + 36])
        t = []
        for k in range(3):
            key = tuple(int(round(f[3 * k + j] / Q)) for j in range(3))
            if key not in idx:
                idx[key] = len(verts)
                verts.append(key)
            t.append(idx[key])
        if len(set(t)) == 3:
            tris.append(t)
    assert len(verts) < 65536, name
    pos = struct.pack(f"<{3 * len(verts)}h", *[c for v in verts for c in v])
    ind = struct.pack(f"<{3 * len(tris)}H", *[i for t in tris for i in t])
    return dict(pos=base64.b64encode(pos).decode(), ind=base64.b64encode(ind).decode(),
                nv=len(verts), nt=len(tris))


def main():
    names = ["box", "lid", "crank", "link", "pin", "clip", "ref_body", "ref_horn", "ref_wire"]
    meshes = {n: load(n) for n in names}
    # 運動学: θ → α の表（0〜95°、0.5° 刻み）
    table = [(t, a) for t, a in K.sweep(K.THETA_OPEN, 190)]
    pa0, pb0 = K.pin_a(K.ALPHA0), K.pin_b(0.0)
    vr = json.load(open(os.path.join(BUILD, "verify_report.json"), encoding="utf-8"))
    sr = json.load(open(os.path.join(BUILD, "simulate_report.json"), encoding="utf-8"))
    sl = json.load(open(os.path.join(BUILD, "slice_report.json"), encoding="utf-8"))
    mr = json.load(open(os.path.join(BUILD, "model_report.json"), encoding="utf-8"))
    kin = dict(H=K.H, O=K.O, a=K.A_LEN, l=K.L_LINK, alpha0=K.ALPHA0, A0=pa0, B0=pb0,
               table=[[round(t, 2), round(a, 3)] for t, a in table],
               key_rel=P.BAYONET_KEY_DEG,
               mid_theta=47.5, open_theta=K.THETA_OPEN,
               bend_deg=vr["assembly"]["F_lid_down_with_link_bent"]["bend_deg"])
    data = dict(q=Q, meshes=meshes, kin=kin,
                verify=dict(calibration=vr["calibration"], motion=vr["motion_summary"],
                            clearance=vr["motion_clearance_mm"], static=vr["static_closed"],
                            assembly=vr["assembly"], free_open=vr["lid_free_open_limit_deg"],
                            mass=vr["mass"]),
                sim=sr, slice={k: dict(stats=v.get("stats"), floating=v.get("floating"),
                                       by_feature=v.get("floating_by_feature"))
                               for k, v in sl["parts"].items()},
                slice_calibration=sl["calibration"].get("ok"),
                parts=mr["parts"])
    # スライサーのプレート画像（Bambu Studio が書いたもの）
    plate = os.path.join(os.environ.get("LID_CUBE_PLATE_DIR", ""), "plate.3mf")
    if os.path.exists(plate):
        with zipfile.ZipFile(plate) as z:
            data["plate_png"] = base64.b64encode(z.read("Metadata/plate_1.png")).decode()
    js = "window.CUBE=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
    out = os.path.join(BUILD, "web_data.js")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(js)
    print(out, round(len(js) / 1024), "KB", {k: v["nt"] for k, v in meshes.items()})
    # Studio の物理検証・組み立て画面（viewer/lid-cube）が読むデータ
    asset = {k: v for k, v in data.items() if k != "plate_png"}
    asset["simTables"] = json.load(open(os.path.join(BUILD, "sim_tables.json"), encoding="utf-8"))
    vdir = os.path.join(os.path.dirname(os.path.dirname(HERE)), "viewer", "lid-cube", "assets")
    os.makedirs(vdir, exist_ok=True)
    with open(os.path.join(vdir, "data.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(asset, fh, ensure_ascii=False, separators=(",", ":"))
    print(os.path.join(vdir, "data.json"))
    # 報告ページ: テンプレートにデータを差し込む
    tpl = open(os.path.join(HERE, "report_template.html"), encoding="utf-8").read()
    assert tpl.count("/*CUBE_DATA*/") == 1
    page = tpl.replace("/*CUBE_DATA*/", js.replace("</", "<\\/"))
    rep = os.path.join(os.path.dirname(os.path.dirname(HERE)), "reports", "2026-10-09_servo-lid-cube.html")
    with open(rep, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page)
    print(rep, round(len(page) / 1024), "KB")


main()
