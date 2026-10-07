"""Validate the saved release inputs, then zip only deliverables."""
from pathlib import Path
import hashlib,json,zipfile,sys,datetime
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from release_files import release_files
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((R/n).read_text('utf8'))
A=read('all_mesh_audit.json');V=read('motion_audit.json');S=read('assembly_path_audit.json');SC=read('support_contact_report.json');ML=read('model_lab_verification.json')
assert len(A['saved_meshes'])==50 and not A['failed']
assert not V['collisions'] and not V['invalid_intersection_volumes']
assert V['input_blend_sha256']==S['input_blend_sha256']==sha(R/'editable_cube_v6.blend')
assert len(S['stages'])==7 and all(not x['collisions'] for x in S['stages'])
assert SC['objects']['04_main_cassette']['actual_landing_projection_endpoint_check']['functional_or_other_surface']==0
assert ML['native_preview_stl']['zero_area_facets']==0
assert all(x['same_sha256'] for x in ML['print_parts_exact_sha256_equal']) and ML['protected_v5_and_canonical_unchanged']
P=read('plate_manifest.json');SR=read('slicer_report.json')['plates']
assert len(SR)==4 and all(x['crc_ok'] for x in SR)
for p,s in zip(P,SR):
    assert s['plate']==p['plate'] and s['input_plate_sha256']==sha(R/'plates'/(p['plate']+'.3mf'))
    for part in p['parts']:
        folder='coupons' if p['plate']=='plate_00_fit_tests' else 'stl'
        assert part['stl_sha256']==sha(R/folder/(part['name']+'.stl'))
    assert all(all(int(v)==0 for k,v in stats.items() if k!='face_count') for stats in s['mesh_statistics'])
assert SC['input_plate_sha256']==sha(R/'plates/plate_02_cassette.3mf')
assert len(list((R/'stl').glob('*.stl')))==13 and len(list((R/'coupons').glob('*.stl')))==12
source={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_tested':False,'servo_source':'User approved model-lab/models/sg92r-photo on 2026-10-07. No manufacturer browser lookup was performed in this revision, per user instruction. Measurements, photo estimates, and assumptions are distinguished in reference/SOURCE_README.md.','reference_snapshots_sha256':{p.name:sha(p) for p in sorted((R/'reference').glob('*')) if p.is_file()},'source_sha256':{n:sha(R/n) for n in ['params.py','model.py','cad_utils.py']},'input_editable_sha256':sha(R/'editable_cube_v6.blend'),'verification':{'mesh_instances':50,'mesh_failures':0,'operating_pose_samples':131,'operating_step_deg':.5,'operating_collisions':0,'assembly_paths':7,'assembly_translation_step_mm':2,'assembly_collisions':0,'offline_sliced_plates':4,'support_landing_functional_endpoint_hits':0,'native_model_lab_print_parts_match':13,'v5_and_canonical_unchanged':True},'limits':['Collision tests sample discrete positions, not continuous mathematical proof.','Support contact analysis samples extruding endpoints and planar projections, not the complete filament envelope or actual removability.','No actual printer, servo, electronics, speaker mount, or endurance test performed.']}
(R/'sources_provenance.json').write_text(json.dumps(source,indent=2,ensure_ascii=False),encoding='utf8')
fs=release_files(R);manifest={p.relative_to(R).as_posix():sha(p) for p in fs}
(R/'manifest_sha256.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8');fs.append(R/'manifest_sha256.json')
out=R/'SG92R_mystery_box_v6_prototype.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in fs:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert all(not n.endswith(('.gcode','.blend1','.pyc')) and 'slice_checks/' not in n and '__pycache__/' not in n for n in z.namelist())
    assert all(z.read(n)==(R/n).read_bytes() for n in manifest)
report={'zip':out.name,'size_bytes':out.stat().st_size,'sha256':sha(out),'entry_count':len(fs),'crc_ok':True,'stl_assembly_parts':13,'stl_fit_tests':12,'geometry_3mf_plates':4,'physical_tested':False}
(R/'package_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
