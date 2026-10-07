"""Sample bench assembly translations separately from operating motion."""
import bpy,bmesh,pathlib,json,itertools,math,hashlib
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
allobjs={o.name:o for o in bpy.data.objects};home={n:o.matrix_world.copy() for n,o in allobjs.items()}
def tree(o):
    o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True,epsilon=1e-9)
def intersects(a,b):
    aa=a.copy();aa.data=a.data.copy();bpy.context.collection.objects.link(aa)
    mod=aa.modifiers.new('assembly volume','BOOLEAN');mod.solver='EXACT';mod.operation='INTERSECT';mod.object=b;bpy.context.view_layer.objects.active=aa;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(aa.data);vol=abs(bm.calc_volume())*1e9;bad=sum(not e.is_manifold for e in bm.edges)
    pts=[aa.matrix_world@v.co*1000 for v in bm.verts];bounds=[[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]] if pts else []
    bm.free();bpy.data.objects.remove(aa,do_unlink=True)
    flat=not bounds or min(bounds[1][k]-bounds[0][k] for k in range(3))<.00005
    return {'volume_mm3':vol,'bad_edges':bad,'bounds_mm':bounds,'collision':not flat and vol>.005}
P=[n for n in allobjs if n[:2].isdigit()];servo=[n for n in allobjs if n.startswith('REFERENCE SG92R')]
steps=[
 ('front_crossmember_entry',['15_flat_spacer'],['04_main_cassette'],(1,0,0),60),
 ('rear_crossmember_entry',['16_flat_spacer'],['04_main_cassette','15_flat_spacer'],(1,0,0),60),
 ('servo_case_top_entry',[n for n in servo if not n.endswith('horn')],['04_main_cassette','15_flat_spacer','16_flat_spacer'],(0,0,1),60),
 ('original_horn_axial_entry',[n for n in servo if n.endswith('horn')],['04_main_cassette']+[n for n in servo if not n.endswith('horn')],(1,0,0),30),
 ('cup_axial_entry',['06_horn_cup_journal'],['04_main_cassette','15_flat_spacer','16_flat_spacer']+servo,(1,0,0),30),
 ('local_capture_axial_entry',['17_local_cup_capture'],['04_main_cassette','15_flat_spacer','16_flat_spacer','06_horn_cup_journal']+servo,(1,0,0),30),
 ('front_positive_stop_vertical_entry',['18_local_capture_stop'],['04_main_cassette','17_local_cup_capture','15_flat_spacer','16_flat_spacer','06_horn_cup_journal']+servo,(0,0,1),45),
 ('rear_positive_stop_vertical_entry',['19_local_capture_stop'],['04_main_cassette','17_local_cup_capture','15_flat_spacer','16_flat_spacer','06_horn_cup_journal']+servo,(0,0,1),45),
 ('flat_keeper_axial_entry',['14_servo_top_keeper'],['04_main_cassette','17_local_cup_capture','18_local_capture_stop','19_local_capture_stop','15_flat_spacer','16_flat_spacer']+servo+['06_horn_cup_journal'],(1,0,0),60),
 ('hinge_axle_into_rear_bore',['10_hinge_axle'],['04_main_cassette','14_servo_top_keeper'],(1,0,0),30),
 ('rear_rocker_onto_hinge_axle',['07_rear_rocker'],['04_main_cassette','10_hinge_axle','14_servo_top_keeper'],(1,0,0),30),
 ('drive_axle_into_cup',['11_drive_axle'],['04_main_cassette','06_horn_cup_journal','17_local_cup_capture'],(1,0,0),30),
 ('link_onto_drive_axle',['09_link'],['04_main_cassette','06_horn_cup_journal','07_rear_rocker','10_hinge_axle','11_drive_axle','17_local_cup_capture'],(1,0,0),30),
 ('B_axle_into_rear_rocker_and_link',['12_link_axle'],['07_rear_rocker','09_link','11_drive_axle'],(1,0,0),30),
 ('lid_onto_rear_roof_dock_from_front',['03_planar_lid'],['04_main_cassette','06_horn_cup_journal','07_rear_rocker','09_link','10_hinge_axle','11_drive_axle','12_link_axle','14_servo_top_keeper'],(0,1,0),75),
 ('front_rocker_and_peg_entry',['08_front_rocker'],['03_planar_lid','07_rear_rocker','09_link','10_hinge_axle','12_link_axle'],(1,0,0),24),
 ('rear_cover_axial_entry',['02_fixed_rear_cover'],['04_main_cassette','03_planar_lid','07_rear_rocker','08_front_rocker'],(1,0,0),24),
 ('closure_axial_entry',['05_front_closure'],[n for n in P+servo if n not in ['01_body','05_front_closure','13_body_cross_key']],(1,0,0),30),
 ('complete_cassette_vertical_drop',[n for n in P+servo if n not in ['01_body','13_body_cross_key']],['01_body',next(n for n in allobjs if n.startswith('REFERENCE exciter'))],(0,0,1),76),
]
result={'translation_step_mm':1,'physical_tested':False,'stages':[],'scope':'Rigid nominal translations every1mm; reversing collision-free paths checks geometric removal only. Stock horn/shaft intended coaxial engagement classified separately; same nominal faceted diameter does not represent spline fit. No finger access, elastic fit or pin fall-out simulation.'}
result['input_blend_sha256']=hashlib.sha256((R/'editable_cube_v6.blend').read_bytes()).hexdigest()
for name,moving,fixed,axis,travel in steps:
    for n,o in allobjs.items():o.matrix_world=home[n]
    static={n:tree(allobjs[n]) for n in fixed};collisions=[];mating=[]
    for distance in range(travel,-1,-1):
        T=Matrix.Translation(Vector(axis)*distance*.001)
        for n in moving:allobjs[n].matrix_world=T@home[n]
        for an in moving:
            a=allobjs[an];ta=tree(a)
            for bn in fixed:
                if not ta.overlap(static[bn]):continue
                v=intersects(a,allobjs[bn])
                if v['collision']:
                    entry={'distance_mm':distance,'parts':[an,bn],**v}
                    # Canonical reference uses an un-toothed D4.6 shaft and
                    # same nominal D4.6 faceted socket, rotated by horn phase.
                    # Their tessellation makes tiny wedges within the mating
                    # cylinder; all other intersections remain obstacles.
                    lo,hi=v['bounds_mm']; oy,oz=40.,37.
                    shaft_only=(an=='REFERENCE SG92R horn' and bn=='REFERENCE SG92R body'
                        and v['bad_edges']==0 and v['volume_mm3']<.05
                        and lo[0]>=36.-.001 and hi[0]<=39.5+.001
                        and all(abs(t-oy)<=2.301 for t in [lo[1],hi[1]])
                        and all(abs(t-oz)<=2.301 for t in [lo[2],hi[2]]))
                    if shaft_only:mating.append(entry|{'classification':'stock shaft/socket intended coaxial interface; no real spline fit verified'})
                    else:collisions.append(entry)
    result['stages'].append({'name':name,'moving':moving,'fixed':fixed,'travel_mm':travel,'collisions':collisions,'intended_mating_intersections':mating})
    print('ASSEMBLY',name,'collisions',len(collisions),flush=True)
(R/'assembly_path_audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
