"""Consistency gate for revision3 deliverables, not physical certification."""
from pathlib import Path
import json,hashlib,re,ast,zipfile
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
blend=sha(R/'editable_cube_v6.blend');m=read('assembly_manifest.json')
assert m['revision']==3 and len(m['parts'])==19
assert {p['name']+'.stl' for p in m['parts']}=={p.name for p in (R/'stl').glob('*.stl')}
assert len(list((R/'coupons').glob('*.stl')))==len(read('coupon_manifest.json'))==28
audit=read('all_mesh_audit.json');assert len(audit['saved_meshes'])==94 and not audit['failed']
motion=read('motion_audit.json');assert motion['input_blend_sha256']==blend and not motion['collisions'] and not motion['invalid_intersection_volumes']
assembly=read('assembly_path_audit.json');assert assembly['input_blend_sha256']==blend and len(assembly['stages'])==19 and all(not s['collisions'] for s in assembly['stages'])
key=read('key_cable_report.json');assert key['input_blend_sha256']==blend
assert all(not v['obstacles'] for v in key['key_paths'].values()) and all(v['obstacle'] for v in key['blocking_probes'])
assert all(not v['obstacles'] for v in key['cable'].values())
assert key['reverse_rotation_locked'] is False
bounds=read('exterior_bounds_report.json');assert bounds['input_blend_sha256']==blend and bounds['all_inside70mm_cube']
tool=read('tool_access_report.json');assert tool['input_blend_sha256']==blend and all(not p['obstacles'] for p in tool['paths'])
capture=read('horn_capture_report.json');assert capture['geometry_sha256']==blend
support=read('support_contact_report.json');assert support['input_plate_sha256']==sha(R/'plates/plate_02_cassette.3mf')
assert support['input_slice_sha256']==sha(R/'slice_checks/plate_02_cassette/plate_02_cassette.3mf')
for n,v in support['objects'].items():
 assert support['input_stl_sha256'][n]==sha(R/'stl'/(n+'.stl'))
 assert not v['nominal_bead_protected_overlap_detected'] and not v['bead_center_inside_model_examples']
 assert v['samples_by_feature'].get('Support',0)>0 and v['samples_by_feature'].get('Support interface',0)>0
slices=read('slicer_report.json');assert len(slices['plates'])==5
for p in slices['plates']:
 assert p['input_plate_sha256']==sha(R/'plates'/(p['plate']+'.3mf')) and p['crc_ok']
 assert all(all(str(v)=='0' for k,v in s.items() if k!='face_count') for s in p['mesh_statistics'])
for f in R.glob('*.py'):ast.parse(f.read_text('utf8'))
imgs=re.findall(r'<img src="([^"]+)"',(R/'assembly_guide.html').read_text('utf8'))
assert imgs and all((R/i).is_file() for i in imgs)
report={'revision':3,'physical_tested':False,'release_label':'CAD-checked prototype; revision3 prototype; physical testing not performed; parent review pending; real fit/teeth/support removal/servo tests required','blend_sha256':blend,'print_parts':19,'fit_and_support_tests':28,'geometry_plates':5,'mesh_instances_checked':94,'mesh_failures':0,'motion_samples':131,'motion_obstacles':0,'invalid_motion_booleans':0,'assembly_translation_paths':19,'assembly_obstacles':0,'stock_coaxial_reference_intersections':sum(len(s['intended_mating_intersections']) for s in assembly['stages']),'key_paths_clear':True,'no_required_spring_or_tie':True,'key_reverse_rotation_automatically_locked':False,'closed_print_parts_inside70mm_cube':True,'key_blocking_probes_solid':True,'tool_paths_clear':True,'connector_and_cable_envelopes_clear':True,'support_nominal_protected_bead_overlap':False,'support_protected_projection_gap_mm':support['objects']['06_horn_cup_journal']['projected_protected_min_vertical_gap_mm'],'all_offline_slices_succeeded':True,'guide_image_dependencies':imgs,'no_physical_print_or_servo_actuation':True,'limits':['No continuous-motion/printed-fit guarantee','Reference shaft/socket engagement does not model actual spline teeth','Support proximity under06 about0.5mm requires physical trial26','Layer strength, bottom key operation, tool grips, power, wire tension and vibration untested','Electronics/amp mounts unspecified']}
(R/'release_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
note='''# 修正3 検証結果

19部品・28試験片・5プレートの親レビュー用CAD試作です。実印刷・組立・通電は未実施です。

- STL/3MFの94メッシュインスタンス：閉単一成分、向き、非多様体辺、ゼロ面積、正体積を確認。失敗0。
- 0〜65度、0.5度刻み131姿勢：障害衝突0、無効なBoolean交差結果0。
- 19組立経路、1mm刻み：障害衝突0。逆経路は幾何的分解に使用。実ホーン/軸の意図接合モデル交差3件は別分類。
- 底面キー：下からの挿入と90度回転は名目衝突なし。係止時の下向き引抜き/押上げ/両板の持上げと回転範囲外は肩で阻止。解除方向への逆回転は手動で残し、自動固定や振動耐性を保証しない。
- 2mm工具、D3/R6ケーブル、8×5×15コネクター：指定包絡の名目衝突なし。
- Bambu Studioの5プレート：オフラインスライス成功、メッシュ修復0。実プリンターへ接続/送信しない。機種用G-codeは配布しない。
- 04/06の通常支持・接触層・遷移支持、直線/円弧、実線幅/層厚：拡大名目包絡の保護面交差なし。06捕捉面の下へ投影が近づく箇所は約0.5mmの上下間隔。実接触/垂れ/除去傷の保証はしない。

試験片とサーボ無し全体組立を先に行い、実歯の掛かり・最大逃げ・軸端・底キーの掛かり・支持除去・配線を実測してから通電してください。遅いパルスは停止力を制限しません。詳細と未確認項目は日本語ガイド/REVIEW_RESPONSEに記載しています。
'''
(R/'QA_SUMMARY_日本語.md').write_text(note,encoding='utf8')
print('REVISION3 CONSISTENCY PASS',blend,flush=True)
