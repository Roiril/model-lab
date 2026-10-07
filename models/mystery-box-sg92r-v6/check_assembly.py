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
 ('servo_top_entry',[servo[0],next(n for n in servo if n.endswith('wire'))],['04_main_cassette'],(0,0,1),60),
 ('cup_axial_entry',['06_horn_cup_journal'],['04_main_cassette']+servo,(1,0,0),30),
 ('front_rocker_and_peg_entry',['08_front_rocker'],['03_planar_lid','07_rear_rocker','09_link','10_hinge_axle','12_link_axle'],(1,0,0),24),
 ('rear_cover_axial_entry',['02_fixed_rear_cover'],['04_main_cassette','03_planar_lid','07_rear_rocker','08_front_rocker'],(1,0,0),24),
 ('closure_axial_entry',['05_front_closure'],[n for n in P+servo if n not in ['01_body','05_front_closure','13_body_cross_key']],(1,0,0),30),
 ('complete_cassette_vertical_drop',[n for n in P+servo if n not in ['01_body','13_body_cross_key']],['01_body','REFERENCE exciter25x10'],(0,0,1),76),
 ('cross_key_from_right',['13_body_cross_key'],[n for n in P if n!='13_body_cross_key'],(1,0,0),70),
]
result={'translation_step_mm':2,'physical_tested':False,'stages':[]}
result['input_blend_sha256']=hashlib.sha256((R/'editable_cube_v6.blend').read_bytes()).hexdigest()
for name,moving,fixed,axis,travel in steps:
    for n,o in allobjs.items():o.matrix_world=home[n]
    static={n:tree(allobjs[n]) for n in fixed};collisions=[]
    for distance in range(travel,-1,-2):
        T=Matrix.Translation(Vector(axis)*distance*.001)
        for n in moving:allobjs[n].matrix_world=T@home[n]
        for an in moving:
            a=allobjs[an];ta=tree(a)
            for bn in fixed:
                if not ta.overlap(static[bn]):continue
                v=intersects(a,allobjs[bn])
                if v['collision']:collisions.append({'distance_mm':distance,'parts':[an,bn],**v})
    result['stages'].append({'name':name,'moving':moving,'fixed':fixed,'travel_mm':travel,'collisions':collisions})
    print('ASSEMBLY',name,'collisions',len(collisions),flush=True)
(R/'assembly_path_audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
