"""Reproduce the 2026-10-10 SG92R drawing comparison. No CAD files are changed."""
from pathlib import Path
import base64
import hashlib
import json
import runpy
import struct
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
IMAGE = Path("C:/Users/kouga/Downloads/SG92R_2.jpg")
REPORT = ROOT / "reports/2026-10-10_sg92r-dimension-analysis.html"
DATA = REPORT.with_suffix(".json")
CSS = Path("C:/Users/kouga/Projects/Web/claude-global/skills/visual-deliverable/assets/report.css")


def stl_vertices(path):
    blob = path.read_bytes()
    count = struct.unpack_from("<I", blob, 80)[0]
    if len(blob) != 84 + count * 50:
        raise ValueError("Not a binary STL: " + str(path))
    dtype = np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")])
    # export_stl() writes millimetres. Blender's internal metre coordinates
    # have already been converted at export time.
    return np.frombuffer(blob, dtype=dtype, count=count, offset=84)["vertices"].astype(float)


def section_xy(triangles, height):
    points = []
    for tri in triangles:
        for i, j in [(0, 1), (1, 2), (2, 0)]:
            a, b = tri[i], tri[j]
            if (a[2] <= height < b[2]) or (b[2] <= height < a[2]):
                points.append((a + (b - a) * ((height - a[2]) / (b[2] - a[2])))[:2])
    points = np.asarray(points)
    if not len(points):
        raise ValueError("Empty section")
    return [points.min(axis=0).tolist(), points.max(axis=0).tolist()]


# Calibrate the binary reader and section calculation with known geometry.
test = np.array([[[0, 0, 0], [2, 0, 2], [0, 2, 2]]], dtype=float)
assert section_xy(test, 1) == [[0.0, 0.0], [1.0, 1.0]]
assert section_xy(test, 0.5) != [[0.0, 0.0], [1.0, 1.0]]

pixels = np.asarray(Image.open(IMAGE).convert("RGB"))
assert pixels.shape == (600, 600, 3)
gray = pixels.mean(axis=2)
# Manually identified drawing edges. Original image coordinates; no resize.
front_case_left, front_case_right = 60.0, 138.0
front_shaft = 118.0  # shaft sides at x=110 and x=126
top_ear_first, top_ear_last = 228.0, 336.0
top_width_first, top_width_last = 188.0, 227.0
# Centroid of the white central opening, restricted to its interior region.
weights = np.clip(gray[293:309, 201:215] - 180, 0, None)
ys, xs = np.indices(weights.shape)
top_shaft_y = float(((ys + 293) * weights).sum() / weights.sum())
top_shaft_x = float(((xs + 201) * weights).sum() / weights.sum())
front_scale = 22.8 / (front_case_right - front_case_left)
top_scale = 32.5 / (top_ear_last - top_ear_first)
near = (front_case_right - front_shaft) * front_scale
far = (front_shaft - front_case_left) * front_scale
offset = far - 22.8 / 2
ear_offset = (top_shaft_y - (top_ear_first + top_ear_last) / 2) * top_scale
pitch_pixels = 329.9018434282978 - 232.92949499878017

reference = runpy.run_path(str(ROOT / "models/sg92r-photo/params.py"))
snapshot = json.loads((ROOT / "models/mystery-box-sg92r-b3-candidate/reference/dimensions.json").read_text(encoding="utf-8"))
tri = stl_vertices(ROOT / "exports/sg92r-photo-body.stl")
snap_tri = stl_vertices(ROOT / "models/mystery-box-sg92r-b3-candidate/reference/sg92r-photo-body.stl")
current_section = section_xy(tri, 20)
snapshot_section = section_xy(snap_tri, 20)
assert np.allclose(current_section, [[-16.5, -6], [6.5, 6]], atol=0.001)
assert np.allclose(snapshot_section, current_section, atol=0.001)

evidence = {
    "image": str(IMAGE), "image_sha256": hashlib.sha256(IMAGE.read_bytes()).hexdigest(),
    "image_size_pixels": [600, 600],
    "written_dimensions_mm": {"A": 34.5, "B": 22.8, "C": 26.7, "D": 12.6, "E": 32.5, "F": 16},
    "manual_pixel_landmarks": {"front_case_x": [60, 138], "front_shaft_x": 118,
        "top_ear_y": [228, 336], "top_width_x": [188, 227],
        "top_shaft_center": [top_shaft_x, top_shaft_y],
        "front_height_A_pixels": 92, "front_height_C_pixels": 76, "side_height_F_pixels": 59},
    "inferred_not_measured_mm": {"near_body_end_to_shaft": near, "far_body_end_to_shaft": far,
        "shaft_offset_from_body_center": offset, "shaft_offset_from_ear_center": ear_offset,
        "mount_hole_pitch": pitch_pixels * top_scale,
        "ear_projection_each_if_symmetric": (32.5 - 22.8) / 2},
    "scale_mm_per_pixel": {"front_B": front_scale, "top_E": top_scale,
        "top_D": 12.6 / 39, "front_C": 26.7 / 76, "front_A": 34.5 / 92, "side_F": 16 / 59},
    "drawing_consistency": {"A_using_C_scale_mm": 92 * 26.7 / 76,
        "F_using_C_scale_mm": 59 * 26.7 / 76,
        "warning": "Views and dimensions are not consistently to scale. Pixel uncertainty does not cover drafting or real-part variation."},
    "binary_stl_sections_at_z20_mm": {"canonical": current_section, "B3_snapshot": snapshot_section},
    "binary_stl_body_bbox_mm": [tri.reshape(-1, 3).min(0).tolist(), tri.reshape(-1, 3).max(0).tolist()],
    "B3_transform_mm": "(X,Y,Z)=(z+9,x+40,y+37)",
    "B3_conditional_fit_image1_mm": {"ear_pocket_length": 32.6, "image_ear_total_free_length": 0.1,
        "case_pocket_length": 23.6, "image_case_total_free_length": 0.8,
        "floor_Z": 31, "predicted_shaft_Z_if_width_12_6_and_centred": 37.3,
        "intended_shaft_Z": 37, "predicted_shaft_Y_if_ear_centred": 35 + ear_offset,
        "intended_shaft_Y": 40},
    "canonical_parameters_mm": {k: v * 1000 for k, v in reference.items() if k.isupper() and isinstance(v, (int, float))},
    "B3_snapshot_parameters": snapshot,
    "physical_assembly_evidence_2026_10_10": {
        "source": "user report",
        "B_failed_reason": "cross horn inserted with unequal left and right arms reversed",
        "B_assembled_after_correcting_orientation": True,
        "B_rotation_confirmed": False,
        "B_exact_revision_confirmed": False,
        "C1_assembled_and_rotated_without_changes": True,
        "C1_prevents_reversed_horn_insertion": True,
        "dimensional_difference_was_not_the_primary_failure": True,
        "absolute_dimensions_confirmed_by_assembly": False,
    },
    "models_modified": False,
}
DATA.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

additional = [Path("C:/Users/kouga/Downloads/images.png"), Path("C:/Users/kouga/Downloads/servo-mini-towerpro-sg92r-details.jpg")]
evidence["additional_images"] = [{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "size": list(Image.open(p).size)} for p in additional]
evidence["images_png_written_mm"] = {"body_length": 22.4, "width": 12.5, "body_height": 22.2, "gear_height": 4.3,
    "horn_top": 30, "flange_length": 32, "hole_pitch": 27.7, "hole_diameter": 2.2, "flange_bottom": 15.7,
    "case_top_to_flange_top": 4}
evidence["images_png_derived_mm"] = {"flange_top": 18.2, "flange_thickness": 2.5, "gear_top": 26.5,
    "near_body_end_to_shaft_approx": 22.4 * (135 - 98) / (230 - 98), "far_body_end_to_shaft_approx": 22.4 * (230 - 135) / (230 - 98)}
evidence["details_jpg_written_mm"] = {"near_body_end_to_shaft": 5.9, "length_segments": [5.9, 8.8, 7.8],
    "body_length": 22.5, "width": 11.8, "body_height": 22.7, "gear_height": 4, "gear_top": 26.7,
    "shaft_height": 3.2, "shaft_diameter": 4.6, "flange_bottom": 15.9, "flange_thickness": 2.5,
    "flange_top": 18.4, "ear_projection_left": 4.7, "hole_to_right_ear_end": 2.3,
    "mount_hole_diameter": 2, "slot_width": 1.3, "gear_large_diameter": 11.8,
    "gear_small_width": 5, "center_hole_diameter": 1.7, "wire_bottom": 4.5, "wire_height": 1.2, "wire_width": 3.6,
    "label_tolerance_percent": 1.5}
evidence["details_jpg_derived_mm"] = {"far_body_end_to_shaft": 8.8 + 7.8, "shaft_offset": (8.8 + 7.8 - 5.9) / 2,
    "shaft_top": 26.7 + 3.2, "flange_length_if_symmetric": 22.5 + 2 * 4.7,
    "hole_pitch_approx_from_pixels": (501 - 115) * 22.5 / (466 - 148), "wire_center": 4.5 + 1.2 / 2}
DATA.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
all_rows = [
 ("本体の長さ", "22.8", "22.4", "22.5 = 5.9+8.8+7.8", "23.0", "−0.5"),
 ("本体の幅", "12.6", "12.5", "11.8", "12.0", "−0.2"),
 ("近い本体端からホーン中心", "約5.85（推定）", "約6.3（推定）", "5.9（直接記載）", "6.5", "−0.6"),
 ("遠い本体端からホーン中心", "約16.95（推定）", "約16.1（推定）", "16.6 = 8.8+7.8", "16.5", "+0.1"),
 ("本体中心からの偏り", "約5.55（推定）", "約4.9（推定）", "5.35 = (16.6−5.9)÷2", "5.0", "+0.35"),
 ("幅方向の端から中心", "約6.3", "約6.25", "5.9", "6.0", "−0.1"),
 ("本体ケースの高さ", "確定できない", "22.2", "22.7", "22.0", "+0.7"),
 ("上面カバーの高さ", "確定できない", "4.3", "4.0", "5.0", "−1.0"),
 ("底から上面カバー頂部", "26.7", "26.5 = 22.2+4.3", "26.7 = 22.7+4.0", "27.0", "−0.3"),
 ("出力軸の突き出し高さ", "7.8（A−C、疑義あり）", "ホーンで隠れている", "3.2", "3.5", "−0.3"),
 ("底から出力軸頂部", "34.5（図の比率と不一致）", "確定できない", "29.9 = 26.7+3.2", "30.5", "−0.6"),
 ("底からホーン最上部", "ホーンが描かれていない", "30.0", "ホーンが描かれていない", "32.0", "比較不可。画像2との差−2.0"),
 ("取付耳を含む長さ", "32.5", "32.0", "約31.9（両耳4.7なら）", "32.0", "約−0.1（条件付き）"),
 ("底から耳下面", "16.0", "15.7", "15.9", "16.0", "−0.1"),
 ("底から耳上面", "確定できない", "18.2 = 22.2−4", "18.4", "18.0", "+0.4"),
 ("取付耳の厚み", "確定できない", "2.5 = 18.2−15.7", "2.5", "2.0", "+0.5"),
 ("取付穴の中心間距離", "約29.2（推定）", "27.7（直接記載）", "約27.3（推定）", "28.84", "約−1.5（推定）"),
 ("取付穴の直径", "確定できない", "2.2", "2.0", "2.0", "0.0"),
 ("穴から外へ開く溝の幅", "確定できない", "確定できない", "1.3", "1.0", "+0.3"),
 ("出力軸の直径", "確定できない", "確定できない", "4.6", "4.6", "0.0"),
 ("上面カバーの長さ", "確定できない", "確定できない", "14.7 = 5.9+8.8", "14.0", "+0.7"),
 ("上面カバーの大円直径", "確定できない", "確定できない", "11.8", "12.0", "−0.2"),
 ("上面カバーの小円部分の幅", "確定できない", "確定できない", "5.0", "4.0", "+1.0"),
 ("中央のねじ穴の直径", "確定できない", "確定できない", "1.7", "2.4（ホーン側の仮値）", "別部品。直接比較不可"),
 ("配線出口の幅", "確定できない", "確定できない", "3.6", "4.0", "−0.4"),
 ("配線出口の厚み", "確定できない", "確定できない", "1.2", "1.6（1本の仮直径）", "定義が違う。直接比較不可"),
 ("底から配線出口中心", "確定できない", "確定できない", "5.1 = 4.5+1.2÷2", "5.0（仮値）", "+0.1"),
]
combined_table = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>" for row in all_rows)
figures = ""
for n, path in enumerate([IMAGE] + additional, 1):
    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    figures += f'<figure><img src="data:{mime};base64,{encoded}" alt="画像{n}：{path.name}"><figcaption>画像{n}：{path.name}。元画像を埋め込み。クリックすると拡大する。</figcaption></figure>'
body = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SG92Rの3枚の寸法図とB3モデルの差</title><style>{CSS.read_text(encoding="utf-8")}
img{{width:100%;cursor:zoom-in}} td{{overflow-wrap:anywhere}} button{{font:inherit;color:var(--ink);background:var(--card);border:1px solid var(--line);padding:var(--sp-2)}}
dialog{{max-width:calc(100vw - 32px);max-height:calc(100vh - 32px);overflow:auto;background:var(--paper);color:var(--ink);border:1px solid var(--line)}} dialog img{{width:auto;max-width:none}} dialog button{{position:sticky;top:0}}
</style><div class="wrap"><p class="eyebrow">画像3枚の寸法比較 · 2026-10-10</p><h1>SG92Rの寸法図とB3モデルの差</h1>
<p class="sub">記載寸法と引き算を優先。図からの推定を区別する。</p><button onclick="document.documentElement.dataset.theme=document.documentElement.dataset.theme==='dark'?'light':'dark'">明るさを切り替える</button>
<div class="lead"><p>追加の詳細図は、近い本体端から回転中心まで5.9 mmと直接指定している。現行モデルは6.5 mm。差は0.6 mm。</p>
<p>詳細図の本体長は22.5 mm。遠い端から中心までは16.6 mm。本体中心からの偏りは5.35 mmとなる。現行モデルの5.0 mmとは0.35 mm違う。</p>
<p>本体幅は3枚で11.8／12.5／12.6 mmと食い違う。実物の1つの正確な寸法には統合できない。Bの組立不能はホーンの左右逆装着が主因と実物で判明した。向きを直すとBも組めた。寸法差を主因とした推測は撤回する。</p></div>
<p>C1は変更せず印刷して組め、回転も成功した。C1はホーンを左右逆に入れられない構造だった。この結果だけでは本体幅や回転中心までの絶対寸法は確定しない。</p>
<h2>1. 3枚の画像</h2>{figures}<p>画像3には記載寸法に対して±1.5%のずれを許容すると書かれている。5.9 mmなら±0.089 mm。22.5 mmなら±0.338 mm。11.8 mmなら±0.177 mm。画像の発行元と、手持ち個体への適用は未確認。</p>
<h2>2. 寸法とモデルとの差</h2><p>単位はmm。最後の列は画像3とモデルの差。例外は明記した。「直接記載」と計算で得た値は、画像の仕様値であり、ユーザーの実物を測った値ではない。</p>
<div class="tblwrap"><table><thead><tr><th>測るところ</th><th>画像1</th><th>画像2</th><th>画像3：詳細図</th><th>現行モデル</th><th>詳細図 − モデル</th></tr></thead><tbody>{combined_table}</tbody></table></div>
<p>付属ホーンの腕の長さ34 × 17 mm。腕の厚み1.5 mm。腕穴の位置。スプラインの歯数。これらは今回の3枚から確定できない。画像1のA=34.5 mmは縦方向の全高。ホーンの腕の全長ではない。</p>
<h2>3. 回転中心の位置を計算する</h2><p>画像3の長手方向は、5.9 mm。8.8 mm。7.8 mmの3区間に分かれている。合計22.5 mmは本体長の記載と一致する。図の画素比を使わず求められる。</p>
<pre>近い端 → 回転中心 = 5.9 mm
回転中心 → 遠い端 = 8.8 + 7.8 = 16.6 mm
本体長 = 5.9 + 16.6 = 22.5 mm
本体中心から回転中心への偏り = (16.6 − 5.9) ÷ 2 = 5.35 mm
モデル：近い端6.5／遠い端16.5／本体長23.0／偏り5.0 mm</pre>
<p>幅方向は直径11.8 mmの大円と中央の出力軸が描かれている。側面にも5.9 mmがある。幅の中心と読むなら、両端から回転中心まで5.9 mmとなる。モデルは両側6.0 mm。</p>
<p>画像1はB=22.8 mmから横方向だけを換算した。本体両端x=60と138。軸中心x=118。近い端まで5.846 mm。遠い端まで16.954 mm。本体中心からの偏り5.554 mm。上面図の耳全長Eから別に求めた偏りは5.564 mm。これらは推定。画像3の直接指定5.9 mmに近い。</p>
<p>画像2の上面図は本体端x≈98と230。軸中心x≈135。本体長22.4 mmで換算すると近い端約6.3 mm。遠い端約16.1 mm。偏り約4.9 mm。画像3の5.9 mmとは約0.4 mm違う。この図から同じ個体だとは判断できない。</p>
<h2>4. 高さの計算と画像1の食い違い</h2><pre>画像3：ケース22.7 + 上面カバー4.0 = 26.7 mm
画像3：上面カバー頂部26.7 + 出力軸3.2 = 29.9 mm
画像3：耳下面15.9 + 厚み2.5 = 耳上面18.4 mm
画像2：ケース22.2 + 上面カバー4.3 = 26.5 mm
画像2：ケース22.2 − 耳上面までの4.0 = 耳上面18.2 mm
画像2：耳上面18.2 − 耳下面15.7 = 耳厚み2.5 mm</pre>
<p>上面カバー頂部は3枚とも26.5〜26.7 mmで近い。モデルは27.0 mm。ケースだけの高さは22.2〜22.7 mm。モデルは22.0 mm。カバーだけの高さは4.0〜4.3 mm。モデルは5.0 mm。全高が近くても、途中のケースとカバーの境目は同じではない。</p>
<p>画像1のA=34.5 mmは画像3の裸の出力軸頂部29.9 mmと4.6 mm違う。ホーンを装着した画像2の30 mmよりも大きい。画像1のC約76画素とA約92画素を同じ縮尺で換算するとA≈32.3 mmとなり、表の34.5 mmに一致しない。F約59画素も同じ縮尺では20.7 mmとなり、記載16 mmと一致しない。Aをモデルの新しい全高として採用する根拠は弱い。</p>
<p>画像1の上面図は横縮尺0.323 mm/画素。縦縮尺0.301 mm/画素。約7%違う。正面図の横と縦も約20%違う。記載のない寸法を全図共通の拡大率で求める方法は使えない。画素比だけの値には、線の選び方による約0.3 mm程度の変動に加えて図自体の描写誤差がある。</p>
<h2>5. 取付穴と上面カバー</h2><p>穴の中心間距離は画像2で27.7 mmと直接記載されている。モデルは28.84 mm。差は−1.14 mm。画像3の穴中心x≈115と501、本体端x≈148と466から22.5 mmで横方向だけを換算すると約27.3 mm。これは推定。左右の穴が数画素しかない画像1の約29.2 mmより、画像2の直接指定を優先する。</p>
<p>画像3では左耳の張り出し4.7 mm。右耳も同じ張り出しなら耳全長は22.5+4.7×2=31.9 mm。これは対称という条件つきであり、右耳の寸法が直接指定された値ではない。画像2の直接指定32 mmと近い。耳を含む外形は31.9〜32.5 mmの候補がある。</p>
<p>上面カバーの長さは画像3の5.9+8.8=14.7 mm。現在は14.0 mm。小円部分の幅は画像3で5.0 mm。現在は4.0 mm。画像3の側面図には5.9+3.6=9.5 mmのカバー幅も描かれるが、上面の大円直径11.8 mmと整合しない。カバーの幅形状の完全な復元にはこの図だけでは足りない。</p>
<h2>6. B3の寸法を仮定した位置の差</h2><p>以下は図の個体がモデルと同じものだと仮定した計算で、今回の組立不能の原因を示す値ではない。実物で確認された主因はホーンの左右逆装着だった。比較対象のB3は、軸線が箱Y=40 mm、Z=37 mmにあり、箱X方向へ伸びる。参照座標は次の式で変換される。</p>
<pre>箱X = 参照z + 9
箱Y = 参照x + 40
箱Z = 参照y + 37</pre>
<p>長手方向のずれ：詳細図と同じ個体で、本体中心をモデルの位置に置くなら、偏り5.35−5.0=0.35 mmの分だけ中心が箱+Y方向へずれる。近い本体端の位置を揃えて置くなら、6.5−5.9=0.6 mmの分だけ箱+Y方向へずれる。どの面で位置が決まるかによって差が変わる。</p>
<p>幅方向のずれ：B3の受け台上面はZ=31 mm。幅12 mmを支えて中心Z=37 mmにする。画像3の11.8 mmなら中心Z=36.9 mmとなり0.1 mm低い。画像2の12.5 mmなら37.25 mmとなり0.25 mm高い。画像1の12.6 mmなら37.3 mmとなり0.3 mm高い。幅の変更方向も画像ごとに逆になる。</p>
<p>詳細図を本体中心に合わせた場合、Y方向0.35 mmとZ方向−0.10 mmの合成距離は約0.36 mm。近い端に合わせた場合は約0.61 mm。名目上はB3の回転部の半径方向の隙間0.3 mmより大きい。この仮定を手元個体の実寸として扱わない。向きを直したBが組めたため、これを今回の組立不能の説明には使わない。</p>
<p>耳の開口は32.6 mm。モデルの耳32 mmに対して合計0.6 mmの隙間。画像1の32.5 mmなら合計0.1 mmになる。上の押さえ下面はZ=43.6 mm。幅12.6 mmならサーボ上端も43.6 mmになり、隙間がなくなる。幅11.8 mmなら上端42.8 mmで、逆に0.8 mmの隙間となる。</p>
<p>本体ケースの軸方向の開口はおおむね箱X=8.8〜31.3 mm。モデルのケースX=9〜31 mmに対し、合計0.5 mmの隙間がある。画像3のケース高さ22.7 mmなら、同じ底位置でX=9〜31.7 mmとなり、前の押さえの張り出しX=31.3 mmを0.4 mm越える。画像2の22.2 mmならX=31.2 mmまで。ケースが奥まで座らない候補もある。</p>
<p>詳細図の耳厚み2.5 mmはモデルより0.5 mm厚い。B3では横向きのため箱X方向へ影響する。耳を中心として位置決めしているわけではないので、0.5 mmをそのまま回転中心のずれと数えてはいけない。穴間隔の差もB3の受け台には位置決め用の2本のピンがないため、今回の中心のずれの直接原因とは限らない。</p>
<p>出力軸頂部は詳細図なら箱X=38.9 mm。モデルは39.5 mm。ホーン最上部は画像2ならX=39 mm。モデルは41 mm。ただしB3のホーン固定で重要なのは腕下面とハブ形状。今回の図だけではその高さを確定できず、この差をそのまま固定部の変更量にはできない。</p>
<h2>7. 次に確かめる寸法</h2><ol><li>近い本体端から回転中心まで。モデル6.5 mmに対して詳細図5.9 mm。今回最も直接的な差。</li><li>本体幅。11.8／12.5／12.6 mmのどれに近いか。回転中心の上下ずれを決める。</li><li>ケースだけの高さ。本体底からケースと上面カバーの境目まで。22／22.2／22.7 mmのどれか。</li><li>耳の全長と厚み。奥まで座るか。押さえを付ける前後で座りが変わるか。</li><li>本体底からホーン腕下面まで。裸の出力軸頂部と別に測る。ホーン固定部分の軸方向位置を決める。</li></ol>
<p>詳細図の5.9 mmと計算値16.6 mmはC2の試験寸法へ採用した。C2は詳細図の一式を保ち、同じ座と受けを持つ試片で確かめる。3枚から手持ち個体の実寸は断定しない。この分析スクリプトは形状や印刷ファイルを変更しない。</p>
<h2>8. 根拠と再計算</h2><p>SG92R参照モデルのparams.pyとB3のreference/dimensions.jsonを参照した。両方の本体STLを直接解析した。Z=20 mm断面はx=−16.5〜6.5 mm。y=−6〜6 mm。モデルの6.5／16.5 mmと幅12 mmが実際の形状にもあることを確認した。STLはmm。Blenderの内部単位mと区別した。</p>
<p>B3の支持位置はbaseline_model.pyの114〜121行。後端の停止面は150〜153行。押さえは279〜280行。座標変換は305〜307行。B3追加処理はこのサーボ受けを変更していない。</p>
<p class="note">元画像3枚のSHA-256。画素位置。計算式。STL断面。比較値は同名JSONに保存。再計算：py -3.11 tools/analyze_sg92r_drawing.py。寸法図の数字には資料間の食い違いがある。今回の結果は画像の解読とモデルとの差であり、実測結果ではない。</p></div>
<dialog id="zoom"><button onclick="this.parentElement.close()">閉じる</button><img alt="寸法画像の拡大"></dialog>
<script>document.querySelectorAll('figure img').forEach(img=>img.onclick=()=>{{document.querySelector('#zoom img').src=img.src;document.querySelector('#zoom').showModal()}});</script></html>'''
REPORT.write_text(body, encoding="utf-8", newline="\n")
print(json.dumps({"report": str(REPORT), "evidence": str(DATA), "images": 3, "comparison_rows": len(all_rows),
                  "details_near_mm": 5.9, "details_far_mm": 16.6, "details_offset_mm": 5.35,
                  "models_modified": False}, ensure_ascii=False))
