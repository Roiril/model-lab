"""Three self-contained/additive ZIPs; no G-code, caches or old revisions."""
from pathlib import Path
import json,hashlib,zipfile,re
R=Path(__file__).resolve().parent;OUT=R.parent/'sg92r_v6_revision3_distribution_20261008';OUT.mkdir(exist_ok=True)
assert json.loads((R/'release_validation.json').read_text())['revision']==3
original=R.parent/'sg92r_cube_v6_simple_20261008/SG92R_mystery_box_v6_prototype.zip'
original_verified=None
if original.exists():
 original_verified=hashlib.sha256(original.read_bytes()).hexdigest()=='29e3bb91c48156e295636dcb4233b3d0ea1abf7649fb15e7f4f3dbb106820e9f'
 assert original_verified
root='SG92R_v6_rev3/'
docs=['README.md','README_日本語.txt','assembly_guide.html','REVIEW_RESPONSE_日本語.md','QA_SUMMARY_日本語.md']
essential=set(docs+['assembly_overview.png','dimensions.png','assembly_steps.png','horn_capture.png','support_faces.png','print_plates.png','exploded_actual3d.png','assembly_manifest.json','coupon_manifest.json','plate_manifest.json','release_validation.json','bottom_key_operation.png','REQUIREMENTS_RESPONSE_日本語.md','slow_open_demo/slow_open_demo.ino'])
essential.update(p.relative_to(R).as_posix() for d in ['stl','coupons','plates'] for p in (R/d).glob('*') if p.is_file())
sources=['model.py','params.py','cad_utils.py','make_coupons.py','make_plates.py','prepare_slicer.py','slice_plates.py','summarize_slices.py','verify_motion.py','check_assembly_revision.py','check_assembly.py','verify_revision_capture.py','verify_horn_capture.py','verify_key_cable.py','verify_tool_access.py','check_support_revision.py','check_support_contacts.py','audit_all.py','audit_stl.py','mechanics_report.py','mechanical_screen.py','render_preview.py','render_engineering.py','render_capture_section.py','render_assembly_steps.py','render_support_faces.py','render_bottom_key.py','verify_exterior_bounds.py','make_docs_revision.py','make_docs.py','final_validation_revision.py','package_revision.py','editable_cube_v6.blend','machine_x1c_flat.json','process_manual_support.json','process_no_support.json','filament_pla_flat.json']
editable=set(sources)
editable.update(p.relative_to(R).as_posix() for p in (R/'reference').glob('*') if p.is_file())
editable.update(p.name for p in R.glob('*.svg'))
editable.update(n for n in ['all_mesh_audit.json','motion_audit.json','assembly_path_audit.json','horn_capture_report.json','key_cable_report.json','tool_access_report.json','support_contact_report.json','slicer_report.json','mechanics_report.json','load_screen_report.json','exterior_bounds_report.json'] if (R/n).is_file())
extra={p.name for p in R.glob('*.png')} - essential
sets=[essential,editable,extra];assert not any(sets[i]&sets[j] for i in range(3) for j in range(i))
common='''SG92R v6 修正3 / CAD検証済み試作・実物未検証
01印刷ZIPだけで19STL・28試験片・5形状3MF・日本語画像ガイドを読めます。
02は編集CAD・ソース・詳細QA・SVG。03は追加の実CAD画像です。
3ZIPのSG92R_v6_rev3を同じ新しいフォルダーへ展開してください。初版v1へ上書き/混在しません。
中心ねじの代わりに付属ホーン+局所捕捉を使います。実歯の掛かり未確認なら通電しません。
底面の印刷キーで捕捉。ばね/結束バンドの購入追加は不要。支持除去/嵌合/工具/電源/耐久/振動は未検証。
親レビューまで配布保留です。最初は関連試験片、次にサーボ無しで箱/カバー/キーまで組んで手動確認してください。
G-codeや機種専用のスライス済み3MFを配布しません。
'''
rows=[]
for index,(files,suffix) in enumerate(zip(sets,['print','editable_CAD','extra_3D_images']),1):
 fn=f'SG92R_v6_rev3_0{index}_{suffix}.zip';target=OUT/fn
 inventory={f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in sorted(files)}
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.writestr(root+'START_HERE_日本語.txt',common)
  z.writestr(root+f'PACKAGE_0{index}_SHA256.json',json.dumps(inventory,ensure_ascii=False,indent=2))
  for f in sorted(files):z.write(R/f,root+f)
 assert target.stat().st_size<15_000_000,(fn,target.stat().st_size)
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  for f,h in inventory.items():assert hashlib.sha256(z.read(root+f)).hexdigest()==h
  if index==1:
   for image in re.findall(r'<img src="([^"]+)"',z.read(root+'assembly_guide.html').decode('utf8')):assert root+image in z.namelist()
 rows.append({'filename':fn,'size_bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'entries':len(files)+2,'source_files':len(files),'local_path':str(target.resolve())})
report={'revision':3,'root':root,'all_crc_and_bytes_verified':True,'max_zip_bytes':15_000_000,'original_full_v1_zip_unchanged':original_verified,'packages':rows,'source_files_once':sum(len(s) for s in sets)}
(OUT/'distribution_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False),flush=True)
