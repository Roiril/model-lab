"""Nominal bayonet operation and conservative cable envelopes; no real tests."""
import bpy,bmesh,pathlib,json,math,hashlib,sys
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R))
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
from cad_utils import capsule,cube,add
body=bpy.data.objects['01_body'];key=bpy.data.objects['13_body_cross_key'];home=key.matrix_world.copy()
fixed=[body,bpy.data.objects['04_main_cassette'],bpy.data.objects['05_front_closure']]
def intersection(a,b):
    aa=a.copy();aa.data=a.data.copy();bpy.context.collection.objects.link(aa)
    mod=aa.modifiers.new('envelope','BOOLEAN');mod.solver='EXACT';mod.operation='INTERSECT';mod.object=b
    bpy.context.view_layer.objects.active=aa;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(aa.data);volume=abs(bm.calc_volume())*1e9;bad=sum(not e.is_manifold for e in bm.edges)
    pts=[aa.matrix_world@v.co*1000 for v in bm.verts];bounds=[[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]] if pts else []
    bm.free();bpy.data.objects.remove(aa,do_unlink=True)
    flat=not bounds or min(bounds[1][k]-bounds[0][k] for k in range(3))<.00005
    return {'volume_mm3':volume,'bad_edges':bad,'bounds_mm':bounds,'obstacle':not flat and (volume>.005 or bad>0)}
def T(z,deg):
    pivot=Vector((.0365,.0265,0))
    return Matrix.Translation(Vector((0,0,z*.001)))@Matrix.Translation(pivot)@Matrix.Rotation(math.radians(deg),4,'Z')@Matrix.Translation(-pivot)@home
report={'input_blend_sha256':hashlib.sha256((R/'editable_cube_v6.blend').read_bytes()).hexdigest(),'physical_tested':False,'key_paths':{},'blocking_probes':[],'cable':{}}
fixed=[o for o in bpy.data.objects if o.type=='MESH' and o!=key]
paths={'vertical_entry_at90deg':[(z,90) for z in range(-30,1)],'quarter_turn_90_to0':[(0,d) for d in range(90,-1,-1)]}
for name,poses in paths.items():
    issues=[]
    for z,deg in poses:
        key.matrix_world=T(z,deg)
        for f in fixed:
            result=intersection(key,f)
            if result['obstacle']:issues.append({'z_offset_mm':z,'rotation_deg':deg,'fixed':f.name,**result})
    report['key_paths'][name]={'samples':len(poses),'obstacles':issues}
    print('KEY',name,len(issues),flush=True)
for name,z,d in [('withdraw_locked',-1.,0),('upward_head_capture',.6,0),('wrong_direction_past_locked_stop',0,-15),('past_release_stop',0,105)]:
    key.matrix_world=T(z,d);hits=[]
    for f in [body,bpy.data.objects['04_main_cassette'],bpy.data.objects['05_front_closure']]:
        v=intersection(key,f)
        if v['obstacle']:hits.append({'fixed':f.name,**v})
    report['blocking_probes'].append({'name':name,'z_offset_mm':z,'rotation_deg':d,'obstacle':bool(hits),'hits':hits})
key.matrix_world=home
for name in ['04_main_cassette','05_front_closure']:
    obj=bpy.data.objects[name];old=obj.matrix_world.copy();obj.location.z+=.001
    v=intersection(obj,key);report['blocking_probes'].append({'name':name+'_lift1mm','obstacle':v['obstacle'],'hits':[v]});obj.matrix_world=old
report['reverse_rotation_locked']=False
report['retention_scope']='Rigid head/floor shoulder and crossbar/feet retain vertical translation at0deg. Two broad angular stops limit0..90. Reverse rotation toward90 remains intentionally manual; no automatic angular lock, spring preload or vibration retention claim.'
print('BLOCKS',[(x['name'],x['obstacle']) for x in report['blocking_probes']],flush=True)
# Actual floor entry with an 8x5x15 mm rectangular connector envelope.
issues=[]
for z in range(-10,25):
    o=cube('connector envelope',(37,61.8,z),(45,66.8,z+15))
    v=intersection(o,body);bpy.data.objects.remove(o,do_unlink=True)
    if v['obstacle']:issues.append({'bottom_z_mm':z,**v})
report['cable']['connector_8x5x15_vertical_entry']={'center_xy_mm':[41,64.3],'obstacles':issues}
# D3 cable, centre bend R6. Spherical segment caps enlarge the discretized
# centreline instead of relying on endpoint-only clearance. 5 degree samples.
centres=[(62.5,14.),(62.5,7.65)]+[(68.5-6*math.cos(math.radians(t)),7.65-6*math.sin(math.radians(t))) for t in range(5,91,5)]+[(76.,1.65)]
wire_issues=[]
for a,b in zip(centres,centres[1:]):
    o=capsule('cable envelope',39.48,42.52,Vector(a),Vector(b),1.52)
    v=intersection(o,body);bpy.data.objects.remove(o,do_unlink=True)
    if v['obstacle']:wire_issues.append({'segment_yz_mm':[a,b],**v})
# capsule is extrusion of a 2D radius1.52 profile, conservative square-ish
# section through X: wider than the actual circular D3 cable.
report['cable']['D3_R6_conservative_envelope']={'centerline_yz_mm':centres,'x_bounds_mm':[39.48,42.52],'obstacles':wire_issues}
report['scope']='Bottom key insertion at1mm and turn at1deg. Reverse paths are the same geometry; tool grip/pull, printed fit, retention strength and vibration are untested. Cable assumes D3 R6 and connector8x5x15 without latch/tails. Smooth posts guide wires but do not prove tensile strain relief.'
(R/'key_cable_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('CABLE connector / bend obstacles',len(issues),len(wire_issues),flush=True)
