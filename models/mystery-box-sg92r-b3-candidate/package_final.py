"""Explicit final candidate archive; no sliced 3MF or G-code."""
from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=sha(R/'editable_cube_B3.blend');assert source=='1ababb93dba4ef81368ba7767d3b13f180b4e43a407c336acef9d6a9150ac4c6'
assert not json.loads((R/'all_mesh_audit.json').read_text())['failed']
assert len(list((R/'stl').glob('*.stl')))==22
assert len(list((R/'coupons').glob('*.stl')))==9
assert len(list((R/'plates').glob('*.3mf')))==6
for n in ['final_support_contact_report.json','final_support_coupon_report.json']:
 d=json.loads((R/n).read_text());assert all(not x['nominal_bead_protected_overlap_detected'] and not x['bead_center_inside_model_examples'] for x in d['objects'].values())
for p in json.loads((R/'plate_manifest.json').read_text()):
 for row in p['parts']:
  f=(R/('coupons' if row['name'].startswith('test_') else 'stl')/(row['name']+'.stl'));assert sha(f)==row['stl_sha256']
src=['model.py','params.py','cad_utils.py','baseline_model.py','local_cad.py','build_B3.py','add_speaker_envelopes.py','export_B3.py','export_native_preview.py','make_local_coupons.py','make_hardware_coupons.py','contact_order.py','review_combined.py','check_local.py','check_tools_capture_B3.py','check_bench_support.py','verify_motion.py','check_assembly_revision.py','verify_wiring.py','audit_all.py','audit_stl.py','make_plates.py','slice_plates.py','summarize_slices.py','check_support_revision.py','check_support_final.py','check_support_coupons_final.py','prepare_final_support_check.py','inspect_slice_lines.py','extract_B3_sections.py','render_preview.py','render_service.py','render_support_faces.py','mechanics_report.py','make_final_guide.py','check_final_guide.mjs','package_final.py']
evidence=['README.md','catalog.json','editable_cube_B3.blend','baseline_reference.blend','B3_print_assembly_guide.html','assembly_manifest.json','baseline_manifest.json','rebuild_provenance.json','all_mesh_audit.json','local_audit.json','local_audit_B3.json','motion_audit.json','assembly_path_audit.json','contact_order_B3.json','combined_slack_report.json','tools_capture_audit_B3.json','bench_support_report.json','speaker_envelope_definition.json','wiring_report.json','slicer_report.json','slice_line_review.json','support_contact_report.json','final_support_contact_report.json','final_support_coupon_report.json','slice_root_lines.svg','slice_root_lines.png','actual_sections.json','coupon_manifest.json','coupon_inventory.json','plate_manifest.json','mechanics_report.json','preview_closed.png','preview_open65.png','preview_mechanism65.png','preview_side_mechanism0.png','preview_bottom.png','preview_local.png','preview_support.png','support_04_under.png','support_04_top.png','support_06_under.png','support_06_top.png','support_face_images.json','service_render_record.json','camera_projected_dimensions.json','guide_visual_check.json','machine_x1c_flat.json','filament_pla_flat.json','process_manual_support.json','process_no_support.json']
paths=[R/n for n in src+evidence]
for folder in ['stl','coupons','plates','reference','slow_open_demo','docs','print_qa']:
 paths+=sorted(p for p in (R/folder).rglob('*') if p.is_file())
assert len(paths)==len(set(paths));assert all(p.is_file() for p in paths)
release={'version':'B3-integrated-3','native_candidate_id':'mystery-box-sg92r-b3-candidate','status':'Design/print candidate; coupons first','date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_blend_sha256':source,'print_parts':22,'conditional_coupons':9,'geometry_plates':6,'mechanism_changed_during_final_documentation':False,'lift20_mm':1.8,'lift22_mm':1.8,'physical_printed':False,'physical_driven':False,'compiled_firmware':False,'old_v6_revision3_and_B2_preserved':True,'no_external_publish_or_push':True,'limits':['Not a physical assembly guarantee','All key Z and bolt slack DOFs not jointly swept for contact order','Finite pose/tool/support screens; no continuous full escape proof','Physical fit, gravity return, root strength, support fusing, hands and bench stability, vibration and wear are untested','X1C slicing is diagnostic only; user printer unknown','No G-code or machine-specific sliced3MF in archive']}
(R/'release_status.json').write_text(json.dumps(release,ensure_ascii=False,indent=2),encoding='utf8');paths.append(R/'release_status.json')
mapping={p.relative_to(R).as_posix():sha(p) for p in paths}
(R/'content_manifest.json').write_text(json.dumps({'version':release['version'],'frozen_blend_sha256':source,'sha256':mapping,'source_params_note':'Final source comments/docs/native export hook changed; frozen candidate geometry unchanged. Rebuild provenance refers to the prior successful full rebuild. Revalidate any regenerated or edited geometry.'},ensure_ascii=False,indent=2),encoding='utf8');paths.append(R/'content_manifest.json')
target=R/'SG92R_mystery_box_B3_design_print_candidate.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for p in paths:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
receipt={'archive':target.name,'archive_sha256':sha(target),'bytes':target.stat().st_size,'file_count':len(paths),'all_zip_files_match_local_original':True,'files':[p.relative_to(R).as_posix() for p in paths]}
(R/'final_archive_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in receipt.items() if k!='files'},ensure_ascii=False),flush=True)
