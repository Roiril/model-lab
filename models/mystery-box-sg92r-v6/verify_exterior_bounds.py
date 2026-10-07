import bpy,pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
d=json.loads((R/'assembly_manifest.json').read_text('utf8'));rows=[]
for part in d['parts']:
 o=bpy.data.objects[part['name']];pts=[o.matrix_world@v.co*1000 for v in o.data.vertices]
 lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)]
 rows.append({'name':o.name,'bounds_mm':[lo,hi],'within70mm_cube':all(a>=-.01 and b<=70.01 for a,b in zip(lo,hi))})
result={'input_blend_sha256':hashlib.sha256((R/'editable_cube_v6.blend').read_bytes()).hexdigest(),'closed_assembly_print_parts':rows,'all_inside70mm_cube':all(r['within70mm_cube'] for r in rows),'no_required_purchased_mechanical_hardware':True,'physical_tested':False,'scope':'Closed nominal CAD print parts only. External electrical wire is excluded. Underside has functional key entry and cable openings.'}
(R/'exterior_bounds_report.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('EXTERIOR70',result['all_inside70mm_cube'])
assert result['all_inside70mm_cube']
