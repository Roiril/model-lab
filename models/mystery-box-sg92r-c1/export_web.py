"""C1 の Studio 用データと単一ファイル検証レポートを作る。Blender 不要。

    py -3.11 models/mystery-box-sg92r-c1/export_web.py

build/ の組んだ姿勢の STL（mm）を Int16（0.005mm 刻み）と Uint16 の添字に詰める。
運動学、検証、シミュレーション、スライスの結果も同じデータへまとめる。
"""
import base64
import json
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import linkage as K  # noqa: E402
import params as P  # noqa: E402

BUILD = os.path.join(HERE, "build")
MODEL_ID = P.MODEL_ID
Q = 0.005


def load_json(name):
    with open(os.path.join(BUILD, name), encoding="utf-8") as fh:
        return json.load(fh)


def load_mesh(name):
    with open(os.path.join(BUILD, f"{name}.stl"), "rb") as fh:
        raw = fh.read()
    count = struct.unpack("<I", raw[80:84])[0]
    idx, verts, tris = {}, [], []
    for i in range(count):
        offset = 84 + 50 * i + 12
        values = struct.unpack("<9f", raw[offset:offset + 36])
        tri = []
        for k in range(3):
            key = tuple(int(round(values[3 * k + j] / Q)) for j in range(3))
            if key not in idx:
                idx[key] = len(verts)
                verts.append(key)
            tri.append(idx[key])
        if len(set(tri)) == 3:
            tris.append(tri)
    assert len(verts) < 65536, name
    pos = struct.pack(f"<{3 * len(verts)}h", *[coord for vertex in verts for coord in vertex])
    ind = struct.pack(f"<{3 * len(tris)}H", *[item for tri in tris for item in tri])
    return dict(pos=base64.b64encode(pos).decode(), ind=base64.b64encode(ind).decode(),
                nv=len(verts), nt=len(tris))


def encode_image(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()


def main():
    names = ["box", "lid", "crank", "link", "pin", "clip", "speaker_clip",
             "ref_body", "ref_horn", "ref_wire", "ref_speaker"]
    meshes = {name: load_mesh(name) for name in names}
    table = K.sweep(P.ASSEMBLY_LID_BACK_DEG, int(P.ASSEMBLY_LID_BACK_DEG * 2))
    pa0, pb0 = K.pin_a(K.ALPHA0), K.pin_b(0.0)
    vr = load_json("verify_report.json")
    sr = load_json("simulate_report.json")
    sl = load_json("slice_report.json")
    mr = load_json("model_report.json")

    mid_theta = K.THETA_OPEN / 2
    alpha_mid = K.sweep(mid_theta, 65)[-1][1]
    alpha_open = K.sweep(K.THETA_OPEN, int(K.THETA_OPEN * 2))[-1][1]
    alpha_setup = table[-1][1]
    sim_motion = sr.get("servo_motion", {})
    stroke = sim_motion.get("stroke_deg", abs(K.ALPHA0 - alpha_open))
    motion_time = sr.get("motion_time_s", P.OPEN_TIME_S)
    kin = dict(H=K.H, O=K.O, a=K.A_LEN, l=K.L_LINK, alpha0=K.ALPHA0, A0=pa0, B0=pb0,
               table=[[round(theta, 2), round(alpha, 3)] for theta, alpha in table],
               key_rel=P.BAYONET_KEY_DEG, mid_theta=mid_theta, open_theta=K.THETA_OPEN,
               bend_deg=0)
    data = dict(
        q=Q,
        meshes=meshes,
        kin=kin,
        verify=dict(calibration=vr["calibration"], motion=vr["motion_summary"],
                    clearance=vr["motion_clearance_mm"], static=vr["static_closed"],
                    static_contacts=vr.get("static_contacts", {}),
                    assembly=vr["assembly"], free_open=vr["lid_free_open_limit_deg"],
                    mass=vr["mass"], overhang=vr.get("overhang"),
                    overhang_calibration=vr.get("overhang_calibration")),
        sim=sr,
        slice={key: dict(stats=value.get("stats"), floating=value.get("floating"),
                         by_feature=value.get("floating_by_feature"))
               for key, value in sl["parts"].items()},
        slice_calibration=sl["calibration"].get("ok"),
        parts=mr["parts"],
    )
    data["meta"] = dict(
        title="住人の箱 C1",
        summary="70 × 70 × 70 mm · 蓋側抜け止め · 印刷 7 点",
        eyebrow="全面蓋 0〜65° · 工具、ねじ、接着剤なし",
        howto=[
            "箱の外で蓋とリンクのピンBを留める。クランクをピンAへ留め、蓋95°の姿勢にする。サーボを90°にしてホーンを付け、クランクをかぶせる",
            f"サーボ90°は組立用の蓋95°に合わせる。閉は {90 + K.ALPHA0 - alpha_setup:.1f}°、65°開は {90 + alpha_open - alpha_setup:.1f}°、中央32.5°は {90 + alpha_mid - alpha_setup:.1f}°相当。全ストロークは {stroke:.1f}°",
            "組み終わったら 90° から閉じる側へ 1° ずつ動かし、蓋が縁に載った位置を「閉」とする",
            f"{motion_time:.1f} 秒かけて始めと終わりをゆっくり動かす。「閉」より先へ押し込まない",
        ],
        untested="エキサイターは直径25mm、高さ10mmの包絡寸法だけを確認した。実物の接触面、保持力、音量、びびりは未検証。"
                 "SG92R付属ホーンの幅と先端形状も写真からの推定値なので、クランクを先に刷って嵌まりを確かめる。"
                 "旧C1は組み立てと回転を実物確認済み。新しいピンBの爪は試片で保持と着脱を確かめる。",
    )
    data["view"] = dict(target=[0, 0, 50], dist=300, cutX=14.0)
    data["servo_setup"] = dict(mid_deg=90.0,
                               setup_lid_deg=P.ASSEMBLY_LID_BACK_DEG,
                               closed_offset_deg=round(K.ALPHA0 - alpha_setup, 1),
                               open_offset_deg=round(alpha_open - alpha_setup, 1),
                               stroke_deg=round(stroke, 1), motion_time_s=motion_time)
    data["assembly"] = dict(
        unit_first=True,
        joint_b_retained=True,
        joint_b_key_deg=P.B_KEY_DEG,
        setup_alpha_deg=alpha_setup,
        speaker_travel_mm=45,
        speaker_step="エキサイターを上からレールへ入れ、スピーカー押さえを上から差して留める",
        speaker_check="エキサイターは直径25mm、高さ10mmの包絡寸法で確認。保持力と音量は実物で確かめる",
        pin_travel_mm=78,
        pin_path_mm=70,
        pin_through=True,
        crank_push_mm=8,
        unit_lift_mm=70,
        lower_from_mm=70,
        lid_place_from_mm=40,
        lid_back_deg=P.ASSEMBLY_LID_BACK_DEG,
        clip_from_mm=25,
        knuckle_gap_mm=round(P.KNUCKLE_GAP * 1000, 2),
    )

    previews = {}
    for key in ("closed", "open", "parts"):
        encoded = encode_image(os.path.join(BUILD, f"{key}.png"))
        if encoded:
            previews[key] = encoded
    if previews:
        data["preview_png"] = previews

    plate_path = os.path.join(ROOT, "exports", f"{MODEL_ID}-PLA.gcode.3mf")
    if os.path.exists(plate_path):
        with zipfile.ZipFile(plate_path) as archive:
            data["plate_png"] = base64.b64encode(archive.read("Metadata/plate_1.png")).decode()
    plate_report = os.path.join(BUILD, "plate_report.json")
    if os.path.exists(plate_report):
        with open(plate_report, encoding="utf-8") as fh:
            report = json.load(fh)
        data["plate"] = {
            key: dict(prediction_s=value["prediction_s"], filament=value["filament"],
                      support_used=value["support_used"])
            for key, value in report.items()
            if isinstance(value, dict) and 'prediction_s' in value
        }
    data['print_review'] = load_json('print_review.json')
    data['boolean'] = load_json('boolean_report.json')
    data['delivery'] = load_json('delivery_report.json')

    js = "window.CUBE=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
    web_data = os.path.join(BUILD, "web_data.js")
    with open(web_data + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(js)
    os.replace(web_data + ".tmp", web_data)
    print(web_data, round(len(js) / 1024), "KB", {key: value["nt"] for key, value in meshes.items()})

    asset = {key: value for key, value in data.items() if key not in ("plate_png", "preview_png")}
    asset["simTables"] = load_json("sim_tables.json")
    asset_dir = os.path.join(ROOT, "viewer", "lid-cube", "assets")
    os.makedirs(asset_dir, exist_ok=True)
    asset_path = os.path.join(asset_dir, f"{MODEL_ID}.json")
    with open(asset_path + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(asset, fh, ensure_ascii=False, separators=(",", ":"))
    with open(asset_path + ".tmp", encoding="utf-8") as fh:
        json.load(fh)
    os.replace(asset_path + ".tmp", asset_path)
    print(asset_path)

    with open(os.path.join(HERE, "report_template.html"), encoding="utf-8") as fh:
        template = fh.read()
    assert template.count("/*CUBE_DATA*/") == 1
    page = template.replace("/*CUBE_DATA*/", js.replace("</", "<\\/"))
    report_path = os.path.join(ROOT, "reports", "2026-10-10_mystery-box-c1.html")
    with open(report_path + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page)
    os.replace(report_path + ".tmp", report_path)
    print(report_path, round(len(page) / 1024), "KB")


main()
