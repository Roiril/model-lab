"""C3/C4の成果物と検証結果を単一HTMLにまとめる。"""
from __future__ import annotations

import base64
from html import escape
import json
import os
import subprocess
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
STYLE = Path.home() / "Projects/Web/claude-global/skills/visual-deliverable/assets/report.css"


def image(path, caption):
    if not path.exists():
        raise FileNotFoundError(path)
    src = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<figure><img src="data:image/png;base64,{src}" alt="{escape(caption)}"><figcaption>{escape(caption)}</figcaption></figure>'


def value_rows(data, prefix=""):
    """限定した検証JSONの数値を、値を隠さず表へ出す。"""
    rows = []
    for key, value in data.items():
        label = f"{prefix} / {key}" if prefix else key
        if isinstance(value, dict):
            rows.extend(value_rows(value, label))
        elif not isinstance(value, list) or len(value) <= 6:
            rows.append(f'<tr><td>{escape(label)}</td><td>{escape(str(value))}</td></tr>')
    return rows


def compact_measurements(data):
    values = []

    def shown(value):
        return str(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None

    angles = data.get("contactAnglesDeg")
    if isinstance(angles, list) and len(angles) == 2:
        reverse, forward = shown(angles[0]), shown(angles[1])
        if reverse is not None:
            values.append(f"逆方向の接触角 {reverse}°")
        if forward is not None:
            values.append(f"正方向の接触角 {forward}°")
    gap = shown(data.get("nearestGapMm"))
    if gap is not None:
        values.append(f"最小隙間 {gap} mm")

    identifier = data.get("id")
    if identifier == "gear-mesh":
        teeth = data.get("actualTeeth")
        if isinstance(teeth, list):
            rendered = [shown(value) for value in teeth]
            rendered = [value for value in rendered if value is not None]
            if rendered:
                values.append(f"実歯数 {' / '.join(rendered)}")
        for key, label, unit in (
            ("faceWidthOverlapMm", "歯幅の重なり", " mm"),
            ("minimumRetainedFaceOverlapMm", "保持後の最小歯幅重なり", " mm"),
            ("contactRatio", "かみ合い率", ""),
            ("maximumTotalAngularPlayDeg", "最大自由角", "°"),
        ):
            value = shown(data.get(key))
            if value is not None:
                values.append(f"{label} {value}{unit}")
    elif identifier == "servo-seat":
        for key, label in (
            ("nominalEngagementMm", "公称差込"),
            ("minimumRetainedEngagementMm", "保持後の最小差込"),
            ("minimumArmEngagementMm", "ホーン腕の最小差込"),
        ):
            value = shown(data.get(key))
            if value is not None:
                values.append(f"{label} {value} mm")
    elif identifier == "coupler-structure":
        thickness = shown(data.get("minimumAxialThicknessMm"))
        if thickness is not None:
            values.append(f"最小軸方向厚さ {thickness} mm")
        samples = shown(data.get("projectionSamples"))
        if samples is not None:
            values.append(f"投影点 {samples}点")
        floor_range = data.get("floorRangeXmm")
        if isinstance(floor_range, list) and len(floor_range) == 2:
            left, right = shown(floor_range[0]), shown(floor_range[1])
            if left is not None and right is not None:
                values.append(f"盲底範囲 X={left}〜{right} mm")
        for index, section in enumerate(data.get("sections", []), start=1):
            if not isinstance(section, dict):
                continue
            x_mm = shown(section.get("xMm"))
            covered = shown(section.get("coveredSamples"))
            total = shown(section.get("totalSamples"))
            if None not in (x_mm, covered, total):
                result = "適合" if section.get("pass") is True else "不足"
                values.append(f"断面{index} X={x_mm} mm 被覆 {covered}/{total}点（{result}）")
    elif identifier == "retention":
        for item in data.get("cases", []):
            value = shown(item.get("maximumTravelMm")) if isinstance(item, dict) else None
            if value is not None:
                values.append(f"{item.get('label', '保持経路')} 最初に止まるまで最大 {value} mm")
            if isinstance(item, dict) and item.get("method") == "rear-surface-first-contact":
                values.append("ホーン後端は実面の初接触を測定。軸ソケットの体積干渉は未確認")
        axial_stack = data.get("axialStack")
        total = shown(axial_stack.get("totalFreeTravelMm")) if isinstance(axial_stack, dict) else None
        if total is not None:
            values.append(f"軸方向の総遊び {total} mm")
    elif identifier == "cam-followers":
        value = shown(data.get("maximumActiveGapMm"))
        if value is not None:
            values.append(f"最大実隙間 {value} mm")
    elif identifier == "canonical-reference":
        differences = [
            item.get("maximumSurfaceDifferenceMm") for item in data.get("parts", [])
            if isinstance(item, dict) and isinstance(item.get("maximumSurfaceDifferenceMm"), (int, float))
        ]
        if differences:
            values.append(f"最大表面距離 {max(differences):.9f} mm")
    return values


def removable_support_record(review, evidence, review_key="support_check", evidence_key="coupler_support_gap"):
    review_record = review.get(review_key) if isinstance(review, dict) else None
    evidence_record = evidence.get(evidence_key) if isinstance(evidence, dict) else None
    if not isinstance(review_record, dict) and not isinstance(evidence_record, dict):
        return None
    record = dict(evidence_record or {})
    record.update(review_record or {})
    secondary = (evidence_record or {}).get("materials", {})
    primary = (review_record or {}).get("materials", {})
    materials = {key: {**secondary.get(key, {}), **primary.get(key, {})} for key in secondary.keys() | primary.keys()}
    record["materials"] = materials
    return record


def removable_support_html(record, title="ホーン受け内部の印刷専用除去式支え", carrier=False):
    if not record:
        return ""

    def mm(value):
        return f"{value:g} mm" if isinstance(value, (int, float)) and not isinstance(value, bool) else "記録なし"

    rows = []
    for material, values in record.get("materials", {}).items():
        if not isinstance(values, dict):
            continue
        support_layer = values.get("support_last_layer_height_mm")
        peg_layer = values.get("product_first_layer_height_mm") if carrier else values.get("peg_first_layer_height_mm")
        layer_text = (mm(support_layer) if support_layer == peg_layer else
                      f"支え {mm(support_layer)} / 製品 {mm(peg_layer)}")
        rows.append(
            f'<tr><td>{escape(str(material))}</td>'
            f'<td>{escape(mm(values.get("support_last_extrusion_z_mm")))}</td>'
            f'<td>{escape(mm(values.get("product_first_extrusion_z_mm" if carrier else "peg_first_extrusion_z_mm")))}</td>'
            f'<td>{escape(mm(values.get("product_material_bottom_mm" if carrier else "peg_material_bottom_mm")))}</td>'
            f'<td>{escape(layer_text)}</td>'
            f'<td>{escape(mm(values.get("material_gap_mm")))}</td></tr>')
    removal = "実物で確認済み" if record.get("removal_physically_verified") is True else "実物未確認"
    return (
        f'<h4>{escape(title)}</h4>'
        f'<p>支え形状の上端 {escape(mm(record.get("support_geometry_top_mm")))}。'
        + ('' if carrier else f'軸突起形状の下端 {escape(mm(record.get("peg_geometry_bottom_mm")))}。') +
        f'除去性と癒着は{removal}。</p>'
        '<div class="tblwrap"><table><thead><tr><th>材料</th><th>支え最終押出Z</th>'
        '<th>製品の初層Z</th><th>G-code推定材料下面</th><th>層厚</th><th>G-code推定空隙</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>')


def boolean_evidence_html(evidence):
    summary = evidence.get("summary", {})
    calibration = evidence.get("calibration", [])
    passed = sum(row.get("pass") is True for row in calibration)
    algorithm = evidence.get("algorithmSha256", {})
    if isinstance(algorithm, dict):
        algorithm_text = " / ".join(
            f'{Path(path).stem} {str(value)[:12]}' for path, value in algorithm.items())
    else:
        algorithm_text = str(algorithm)[:12]
    text = (
        f'検査 {summary.get("filesChecked", 0)}ファイル。'
        f'欠落 {summary.get("missingFiles", 0)}。'
        f'無効な閉じた形状 {summary.get("invalidClosedSolids", 0)}。'
        f'非隣接面の実交差 {summary.get("properNonadjacentIntersections", 0)}。'
        f'校正 {passed}/{len(calibration)}。計器SHA {algorithm_text or "記録なし"}。')
    probe = evidence.get("shaftCapProbe")
    if isinstance(probe, dict):
        lower = probe.get("independentSection", {}).get("volumeLowerBoundMm3")
        exact = probe.get("solvers", {}).get("EXACT", {}).get("closedBoundaryVolumeMm3")
        manifold = probe.get("solvers", {}).get("MANIFOLD", {}).get("closedBoundaryVolumeMm3")
        if all(isinstance(value, (int, float)) for value in (lower, exact, manifold)):
            text += (f' 軸を0.25 mm移動した共通体積は、独立断面の下限 {lower:.9f} mm³。'
                     f'EXACT {exact:.9f} mm³。MANIFOLD {manifold:.9f} mm³。')
    return f'<h4>検証形状の健全性</h4><p>{escape(text)}</p>'


def print_support_geometry_html(evidence):
    if not evidence:
        return ""
    labels = {"housing": "筐体内側の小柱", "carrier_center": "中央格子の支え",
              "carrier_outer": "外環格子の支え", "horn_coupler": "ホーン受けの支え"}
    rows = []
    for row in evidence.get("supports", []):
        heights = " / ".join(
            f'{item["support_top_z_mm"]:g} → {item["product_first_z_mm"]:g} mm'
            for item in row.get("heights", []))
        gap = " / ".join(str(value) for value in sorted({
            item["material_face_gap_mm"] for item in row.get("heights", [])}))
        connection = "上下の2箇所で折り取り接続" if row.get("attachment") == "breakaway_contact" else "製品とは別体"
        rows.append(f'<tr><td>{escape(labels.get(row["partId"], row["partId"]))}</td>'
            f'<td>{connection}</td><td>{escape(heights)}</td><td>{escape(gap)} mm</td>'
            f'<td>{row["supportProductCommonVolumeMm3"]:.9f} mm³</td>'
            f'<td>{escape(str(row["printComponentMinimumZMm"]))} mm</td></tr>')
    return ('<h4>印刷専用の支え</h4><p>支えは印刷STLに含めた。組み立てる前に除去する。'
        '支持材が最終STLに存在することを体積で確認した。別体の支えは製品との共通材が0。'
        '筐体内側の小柱は上下の宣言した接点だけにつなぐ。除去力と表面の傷は実物未確認。</p>'
        '<div class="tblwrap"><table><thead><tr><th>部品</th><th>接続</th>'
        '<th>支えの最上層Z → 製品の初層Z（公称）</th><th>材料面の空隙（公称）</th>'
        '<th>製品との共通材</th><th>印刷STLの各成分の最低Z</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>')


def closed_loop_html(evidence):
    if not evidence:
        return ""
    rows = "".join(f'<tr><td>{escape(name)}</td><td>{plate["summary"]["closedUnsupportedPathCount"]}</td>'
        f'<td>{sum(row.get("decision") == "rejected" for row in plate.get("closedUnsupportedPaths", []))}</td></tr>'
        for name, plate in evidence.get("plates", {}).items())
    return ('<h4>閉じた経路の支持</h4><p>直下支持のない閉環を押出順で確認した。'
        '閉環の始点と終点の距離だけでは合格にしない。先行する同層の実線幅へ接続するか、'
        '印刷専用支えの実際の最上層へ投影して支持を測る。支持された輪と完全浮遊する輪と、'
        '浮遊した先行輪につながる輪を校正した。</p>'
        '<div class="tblwrap"><table><thead><tr><th>印刷データ</th><th>確認した閉環</th>'
        f'<th>不成立</th></tr></thead><tbody>{rows}</tbody></table></div>')


def main():
    sections = []
    for variant, title, desc in (
        ("c3", "C3 · 立方格子の波", "25枚の正方形を5列に分けた。中央から外へ隆起が移る。平らな面に隠れていた規則が動きとして現れる。"),
        ("c4", "C4 · 六角格子の呼吸", "19個の六角形を中心と2つの環へ分けた。中心ほど深く持ち上がる。格子の輪郭と空隙の影が変わる。"),
    ):
        model = f"mystery-box-sg92r-{variant}"
        folder = ROOT / "models" / model
        manifest = json.loads((folder / "build/manifest.json").read_text(encoding="utf-8"))
        meta = manifest.get("meta", {})
        verify = json.loads((folder / "build/verify_report.json").read_text(encoding="utf-8"))
        delivery = json.loads((folder / "build/delivery_report.json").read_text(encoding="utf-8"))
        integration = json.loads((folder / "build/integration_report.json").read_text(encoding="utf-8"))
        if integration.get("ok") is not True:
            raise ValueError(f"current integration checks have not passed: {model}")
        simulation = json.loads((folder / "build/simulate_report.json").read_text(encoding="utf-8"))
        drive = json.loads((folder / "build/drive_report.json").read_text(encoding="utf-8"))
        boolean_evidence = json.loads((folder / "build/boolean_evidence.json").read_text(encoding="utf-8"))
        hole_path = folder / "build/hole_clearance.json"
        hole_clearance = json.loads(hole_path.read_text(encoding="utf-8")) if hole_path.exists() else None
        assembly = json.loads((folder / "build/assembly.json").read_text(encoding="utf-8"))
        assembly_report = json.loads((folder / "build/assembly_report.json").read_text(encoding="utf-8"))
        review_path = folder / "build/print_review.json"
        print_review = json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else None
        path_review_file = folder / "build/print_path_review.json"
        path_review = json.loads(path_review_file.read_text(encoding="utf-8")) if path_review_file.exists() else None
        path_evidence_file = folder / "build/print_path_evidence.json"
        path_evidence = json.loads(path_evidence_file.read_text(encoding="utf-8")) if path_evidence_file.exists() else None
        closed_loop_file = folder / "build/closed_loop_support_evidence.json"
        closed_loop_evidence = json.loads(closed_loop_file.read_text(encoding="utf-8")) if closed_loop_file.exists() else None
        support_geometry_file = folder / "build/print_support_geometry.json"
        support_geometry = json.loads(support_geometry_file.read_text(encoding="utf-8")) if support_geometry_file.exists() else None
        dimensions = " × ".join(str(x) for x in meta.get("dimensions_mm", []))
        model_url = f"http://localhost:3000/?model={model}"
        motion_url = f"http://localhost:3000/viewer/lattice/index.html?model={model}&amp;mode=physics"
        assembly_url = f"http://localhost:3000/viewer/lattice/index.html?model={model}&amp;mode=assembly"
        photos = image(folder / "build/hero-rest.png", "低い位置。格子の並びを見る。")
        raised_image = "hero-center.png" if variant == "c3" else "hero-raised.png"
        raised_caption = "中央の列が持ち上がった位置。実部品のSTLから描画。" if variant == "c3" else "中心と2つの環が持ち上がった位置。実部品のSTLから描画。"
        photos += image(folder / "build" / raised_image, raised_caption)
        if variant == "c3":
            photos += image(folder / "build/drive-detail.png", "実部品の接続。黄の付属ホーンを赤の駆動歯車が受ける。30歯の歯車対から六角カム軸へ伝える。外装だけを切断したCAD表示。")
        step_html = "".join(f'<li>{escape(step["instruction"])} <span class="muted">検査 {step["report"]["samples"]}姿勢。</span></li>' for step in assembly["steps"])
        simulation_rows = ''.join(f'<tr><td>{escape(label)}</td><td>{result["final"]["servoDeg"]:.2f}°</td><td>{result["peakTorqueNm"]*1000:.2f} mN·m</td><td>{result["maxContactSpeedMmS"]:.2f} mm/s</td><td>{"非負" if result["contactFeasible"] else "負の反力あり"}</td></tr>'
            for name, label in (("standard", "標準"), ("reverse", "戻す"), ("lowPower", "トルク30%"), ("heavy", "格子の重さ4倍"), ("fullSpeed", "全速"))
            for result in [simulation["scenarios"][name]])
        calibration_html = ''.join(f'<li>{escape(row["label"])}。{escape(row["detail"])}</li>' for row in simulation["calibration"])
        drive_rows = ''.join(
            f'<tr><td>{escape(row.get("label", row.get("id", "接続")))}</td>'
            f'<td>{"CAD内接続適合" if row.get("status") == "pass" else "実機未確認" if row.get("status") == "unknown" else "接続未成立"}</td>'
            f'<td>{escape("。".join(compact_measurements(row)) or row.get("basis", "記録なし"))}</td></tr>'
            for row in drive.get("interfaces", []))
        drive_calibration_rows = ''.join(
            f'<tr><td>{escape(row.get("label", row.get("id", "校正")))}</td>'
            f'<td>{"期待どおり検出" if row.get("pass") else "検出失敗"}</td>'
            f'<td>{escape(str(row.get("detail", "")))}</td></tr>'
            for row in drive.get("calibration", []))
        drive_unknown_html = ''.join(
            f'<li>{escape(str(item))}</li>' for item in drive.get("hardwareUnknown", []))
        envelope_groups = simulation.get("clearanceEnvelope", {}).get("summary", {}).get("groups", [])
        envelope_rows = ''.join(
            f'<tr><td>{escape(str(group.get("label", group.get("id", "格子"))))}</td>'
            f'<td>{group.get("nominalPhaseDeg", 0):.3f}°</td>'
            f'<td>±{group.get("maximumPhaseDifferenceDeg", 0):.3f}°</td>'
            f'<td>{group.get("end", {}).get("nominalHeightMm", 0):.3f} mm</td>'
            f'<td>{group.get("end", {}).get("heightRangeMm", [0, 0])[0]:.3f}〜'
            f'{group.get("end", {}).get("heightRangeMm", [0, 0])[1]:.3f} mm</td></tr>'
            for group in envelope_groups)
        assembly_samples = sum(len(step["frames"]) for step in assembly["steps"])
        parts = "".join(f'<tr><td>{escape(p["label"])}</td><td>{"印刷する" if p.get("print") else "既製部品"}</td></tr>' for p in manifest["parts"])
        downloads = "".join(f'<li><a href="../prints/{model}/{escape(p.name)}">{escape(p.name)}</a></li>' for p in sorted((ROOT / "prints" / model).glob("*.3mf")))
        limitations = meta.get("limitations", [])
        if isinstance(limitations, str):
            limitations = [limitations]
        limitations_html = "".join(f"<li>{escape(str(x))}</li>" for x in limitations)
        decisions_html = "".join(f"<li>{escape(str(x))}</li>" for x in meta.get("decisions", []))
        totals = "".join(f'<tr><td>{escape(material)}</td><td>{round(result["prediction_s"]/60)}分</td><td>{result["weight_g"]:.1f} g</td></tr>' for material, result in delivery["plates"]["full"]["materials"].items())
        fit_totals = "".join(f'<tr><td>{escape(material)}</td><td>{round(result["prediction_s"]/60)}分</td><td>{result["weight_g"]:.1f} g</td></tr>' for material, result in delivery["plates"]["fit_test"]["materials"].items())
        print_notes = ""
        if print_review and print_review.get("status") != "superseded":
            print_notes = '<h4>印刷する向きと橋渡し</h4><ul>' + ''.join(
                f'<li>{escape(str(row.get("surface", "")))} {escape(str(row.get("decision", "")))}</li>'
                for row in print_review.get("parts", [])) + '</ul>'
        support_notes = removable_support_html(removable_support_record(path_review, path_evidence))
        support_notes += removable_support_html(removable_support_record(path_review, path_evidence,
            "carrier_support_check", "carrier_outer_support_gap"), "外環格子の印刷専用除去式支え", carrier=True)
        support_notes += print_support_geometry_html(support_geometry)
        support_notes += closed_loop_html(closed_loop_evidence)
        boolean_notes = boolean_evidence_html(boolean_evidence)
        geometry_pass = drive.get("overall", {}).get("geometryPass") is True
        calculation_pass = simulation.get("overall", {}).get("calculationPass") is True
        status = ("CAD内の駆動接続は適合。1自由度計算は条件付きで成立。スプライン嵌合と材料は実機未確認。"
                  if geometry_pass and calculation_pass else
                  "駆動接続または1自由度計算に未成立の項目がある。実機成立とは扱わない。")
        if not integration["ok"]:
            raise ValueError(f"Final artifact audit failed: {model}")
        print_status = "記録した印刷経路の検査は適合。" if delivery["status"] == "ok" else "印刷経路に要確認箇所がある。詳細は末尾の検証記録を参照。"
        if path_review and path_review.get("status") == "accepted_with_fit_test":
            print_status = "G-codeの未支持区間と閉じた経路の支持を確認した。スライサーが追加する自動サポート材は使わない。印刷専用の支えは除去する。実物の試し刷りは未実施。"
        part_count = sum(bool(p.get("print")) and not p.get("fit_only", False) for p in manifest["parts"])
        requirement_rows = (
            ("依頼の動き", "25枚の正方形が5列ごとに最大3mm持ち上がる。" if variant == "c3" else "19個の六角リングが3群で最大5.909／3.939／1.970mm持ち上がる。"),
            ("印刷", f"本体は{part_count}部品を1枚に配置。PLAとPETGの印刷データを用意。スライサーが追加する自動サポート材は使わない。"),
            ("組み立て", "印刷部品とSG92R付属ホーンを使用。挿入経路と固定部の干渉を計算。保持力と着脱感は未実測。"),
            ("動く範囲", "15〜165°を2.5°刻みで検査。片道2秒。" if variant == "c3" else "10〜170°を2.5°刻みで検査。片道1.5秒。"),
            ("検証", f"全{verify['exact_scene'].get('pair_count', verify['exact_scene'].get('unique_pairs'))}組を確認。" + "CAD内の接続形状と指定した圧入・ばね以外の干渉を検査。1自由度計算は接続形状を前提にする。実物は未確認。"),
        )
        requirements = ''.join(f'<tr><th>{escape(label)}</th><td>{escape(result)}</td></tr>' for label, result in requirement_rows)
        sections.append(f'''<section>
<h2>{title}</h2><p>{desc}</p><p class="numbers">閉じた外形 {dimensions} mm。動作中の最大高さ {integration['max_height_mm']:.3f} mm。</p>
<p><a href="{model_url}">Studioで形を見る</a>　<a href="{motion_url}">条件付き計算を操作する</a>　<a href="{assembly_url}">工程を順に再生する</a></p>
<div class="pair">{photos}</div>
<h3>要件ごとの結果</h3><p>幾何学の規則を持つ可動天面。SG92R一台で駆動する。上向きで使用する。印刷部品と付属ホーンで組み立てる。</p>
<div class="tblwrap"><table><tbody>{requirements}</tbody></table></div>
<p>{status}詳細な測定値は専用画面に表示する。検証JSONはこのHTMLにも埋め込んだ。</p>
<h3>決めたこと</h3><ul>{decisions_html}</ul>
<p>寸法を変更するときの定数名と刻みは<a href="../models/{model}/README.md">組み立て説明</a>に記載。<a href="../models/{model}/params.py">寸法の設定ファイル</a>から調整できる。</p>
<h3>接続形状を前提にした1自由度計算</h3>
<p>CAD内の駆動接続が適合した場合だけ、重さとトルクを変えて計算する。SG92Rの速度制限と出せるトルクを入れた1自由度の近似。中実PLAとしてSTLを積分し、質量、重心、慣性を求めた。Pythonとブラウザの動作途中の値も照合する。</p>
<h4>回転遊びによる静的な高さ幅</h4>
<div class="tblwrap"><table><thead><tr><th>格子</th><th>公称位相</th><th>最大位相差</th><th>終点の公称高さ</th><th>終点の幾何学的高さ幅</th></tr></thead><tbody>{envelope_rows}</tbody></table></div>
<p>計算と表示する動作形状は公称位相のまま。回転遊びは実STLの接触角を1:1で足した保守的な±位相差と、その範囲の幾何学的高さ幅だけを示す。位置精度は保証しない。スプライン嵌合と材料は含めない。この高さ幅の動的計算と全組み合わせ干渉は未検証。</p>
{boolean_notes}
<div class="tblwrap"><table><thead><tr><th>接続</th><th>状態</th><th>CAD測定値</th></tr></thead><tbody>{drive_rows}</tbody></table></div>
<h4>接続計器の正例と負例</h4><div class="tblwrap"><table><thead><tr><th>計器</th><th>結果</th><th>測定</th></tr></thead><tbody>{drive_calibration_rows}</tbody></table></div>
<h4>実機未確認</h4><ul>{drive_unknown_html}</ul>
<div class="tblwrap"><table><thead><tr><th>条件</th><th>終点</th><th>最大トルク</th><th>接触開始の速度</th><th>接触反力</th></tr></thead><tbody>{simulation_rows}</tbody></table></div>
<ul>{calibration_html}</ul>
<p>組み立ては{len(assembly['steps'])}工程。表示と検査は同じ{assembly_samples}姿勢を使う。部品を挿入する途中で、既に据えた部品との全組み合わせを検査した。最終位置と工程間の連続性も確認。逆経路で分解する。</p>
<p>格子がカムから浮いた後の飛行や衝撃は解かない。カム接点は格子の自重を法線力とし、摩擦係数0.30で計算する。案内の横予圧は不明。歯車とキー部品の自由角は測定したが、隙間中の動きと衝撃は運動計算に含めない。組立の離散姿勢の間にある連続空間全体は証明していない。実物の着脱力と追従は未確認。</p>
<h3>部品と組み立て</h3><div class="tblwrap"><table><thead><tr><th>部品</th><th>準備</th></tr></thead><tbody>{parts}</tbody></table></div><ol>{step_html}</ol>
<p><a href="../models/{model}/demo/demo.ino">Arduinoの制御例</a>。起動時は90°で停止する。格子を入れる前にhで下限へ戻して停止する。完成後にgで低速往復を始める。sで現在位置に止める。コンパイルと実機への書き込みと動作確認は未実施。</p>
<h3>印刷するファイル</h3><p>X1 Carbon。0.4mmノズル。積層ピッチ0.2mm。Textured PEIプレート。{print_status}</p><div class="tblwrap"><table><thead><tr><th>材料</th><th>全体の予測時間</th><th>全体の使用量</th></tr></thead><tbody>{totals}</tbody></table></div><div class="tblwrap"><table><thead><tr><th>材料</th><th>試片の予測時間</th><th>試片の使用量</th></tr></thead><tbody>{fit_totals}</tbody></table></div>{support_notes}{print_notes}<ul>{downloads}</ul>
<h3>実物で確かめること</h3><ul>{limitations_html}</ul>
<p>初めに嵌合用の試片を刷る。ホーンの左右を合わせる。次にガイドの滑りを手で確かめる。最後に低速でサーボを動かす。</p>
<details><summary>保存した数値と検証記録</summary><pre>{escape(json.dumps({'integration':integration,'drive':drive,'boolean_evidence':boolean_evidence,'hole_clearance':hole_clearance,'simulation':simulation,'assembly':assembly_report,'verify':verify,'delivery':delivery,'print_review':print_review,'print_path_review':path_review,'print_path_evidence':path_evidence,'closed_loop_support_evidence':closed_loop_evidence,'print_support_geometry':support_geometry}, ensure_ascii=False, indent=2))}</pre></details>
</section>''')
    css = STYLE.read_text(encoding="utf-8")
    output = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>住人の箱 C3・C4 — 格子が動く面</title><style>{css}
.wrap{{max-width:68rem}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}.pair figure:nth-child(3){{grid-column:1/-1}}img{{width:100%;height:auto;display:block}}figure{{margin:0}}section{{padding-block:32px;border-top:2px solid var(--line)}}h3{{font-size:var(--fs-md)}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:var(--fs-xs)}}.numbers{{font-variant-numeric:tabular-nums}}@media(max-width:600px){{.pair{{grid-template-columns:1fr}}}}
</style><main class="wrap"><p class="eyebrow">MODEL-LAB · 2026-10-11</p><h1>住人の箱 C3・C4</h1><p class="sub">内側から押されるように変わる2つの格子。</p>
<div class="lead"><p>C3は正方形の波。C4は六角形の段階的な盛り上がり。どちらもSG92R一台で動かす。面の並びと陰影の変化を見せる卓上デモ。</p></div>
<p>画像の色は表示用。用意した印刷データは単色で、実際の色は使うフィラメントで決まる。</p>
<h2>決めたこと</h2><p>可動面を上向きにした。戻る力には自重を使う。ばねは付けない。形はC1・C2と同じ立方体を出発点にした。</p>
<h2>譲ったこと</h2><p>各セルを別々に命令する機能は持たない。1台のサーボから決まった変形を作る。指で押した場所の検出も含めない。サーボに加えて電源と制御用の回路が必要。</p>
{''.join(sections)}
<p class="note">サーボの形はリポジトリ内のSG92R正本を使用。公称の停動トルク2.5kg·cmと速度0.1秒/60°は<a href="https://towerpro.com.tw/product/sg92r-7/">TowerProの仕様</a>を参照。C4の格子は「プロジェクト・ヘイル・メアリー」からの着想。映画小道具の再現寸法ではない。</p></main></html>'''
    git_status = subprocess.run(["git", "status", "--short"], cwd=ROOT, check=True,
        capture_output=True).stdout.decode("utf-8")
    git_diff = subprocess.run(["git", "diff", "--stat"], cwd=ROOT, check=True,
        capture_output=True).stdout.decode("utf-8")
    git_proof = ('<section><h2>Gitの記録</h2><details><summary>保存時の生出力</summary>'
        '<h3>git status --short</h3><pre>' + escape(git_status) +
        '</pre><h3>git diff --stat</h3><pre>' + escape(git_diff) + '</pre></details></section>')
    output = output.replace('</main>', git_proof + '</main>')
    path = ROOT / "reports/2026-10-10_lattice-c3-c4.html"
    temp = path.with_suffix(".tmp")
    temp.write_text(output, encoding="utf-8", newline="\n")
    os.replace(temp, path)
    print(path)


if __name__ == "__main__":
    main()
