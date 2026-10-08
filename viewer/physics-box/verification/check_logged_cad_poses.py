"""Read-only audit of frozen B3 at logged rigid-body poses. Writes only this workspace."""
import bpy, bmesh, json, hashlib, itertools
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
SOURCE=Path(r'C:\Users\kouga\Projects\Web\model-lab\models\mystery-box-sg92r-b3-candidate\editable_cube_B3.blend')
cad=json.loads((ROOT.parent/'assets/cad.json').read_text('utf8'))
run=json.loads((ROOT/'test-results/cad_face_strips.json').read_text('utf8'))
digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert digest==cad['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
items=[(bpy.data.objects[p['name']],p['group']) for p in cad['parts']]
original={o.name:o.matrix_world.copy() for o,g in items}
log=run['log']; selected=[]
for angle in range(0,66,5):
    selected.append(min((r for r in log if r['t']<=8),key=lambda r:abs(r['lidDeg']-angle)))
selected.extend([min(log,key=lambda r:abs(r['t']-t)) for t in [.17,8,10,12,14,16]])
selected=list({r['t']:r for r in selected}.values())
def tree(o):
    o.data.calc_loop_triangles()
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True,epsilon=1e-9)
def intersection(a,b):
    obj=a.copy();obj.data=a.data.copy();bpy.context.collection.objects.link(obj)
    mod=obj.modifiers.new('read-only audit','BOOLEAN');mod.solver='EXACT';mod.operation='INTERSECT';mod.object=b
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(obj.data);v=abs(bm.calc_volume())*1e9;bad=sum(not e.is_manifold for e in bm.edges)
    points=[obj.matrix_world@p.co*1000 for p in bm.verts]
    span=[max(p[k] for p in points)-min(p[k] for p in points) for k in range(3)] if points else [0,0,0]
    bm.free();mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
    return v,bad,span
result={'method':'Actual CAD at selected logged 3D rigid-body poses: AABB/BVH intersection candidates, Blender EXACT boolean volume; same rigid-body and base/frame pairs excluded. No continuous or full CAD guarantee.', 'source_sha256':digest,'contact_mode':'cad_faces','sample_count':len(selected),'samples':[],'finite_intersections':[],'reference_output_interfaces':[],'invalid_boolean_results':[],'flat_touches':0,'physical_tested':False,'exclusions':['Parts in same rigid body','Base versus frame fixed attachment','No containment-only test; fully nested solids may be missed','Reference servo output-shaft / horn engagement is an ideal motor bearing interface, listed separately'],'threshold_mm3':.005}
for r in selected:
    for o,g in items:
        p=r['poses'][g];q=p['rotation'];rot=Quaternion((q['w'],q['x'],q['y'],q['z'])).to_matrix().to_4x4()
        o.matrix_world=Matrix.Translation(Vector(p['translationM']))@rot@Matrix.Translation(-Vector(cad['bodies'][g]['com']))@original[o.name]
    bpy.context.view_layer.update()
    trees={o.name:tree(o) for o,g in items}
    boxes={o.name:([min((o.matrix_world@v.co)[k] for v in o.data.vertices) for k in range(3)],[max((o.matrix_world@v.co)[k] for v in o.data.vertices) for k in range(3)]) for o,g in items}
    for (a,ga),(b,gb) in itertools.combinations(items,2):
        if ga==gb or {ga,gb}=={'base','frame'}:continue
        ba,bb=boxes[a.name],boxes[b.name]
        if any(ba[1][k]<bb[0][k]+1e-9 or bb[1][k]<ba[0][k]+1e-9 for k in range(3)):continue
        hits=trees[a.name].overlap(trees[b.name])
        if not hits:continue
        volume,bad,span=intersection(a,b)
        row={'t':r['t'],'lid_deg':r['lidDeg'],'parts':[a.name,b.name],'body_groups':[ga,gb],'volume_mm3':volume,'nonmanifold_edges':bad,'span_mm':span,'intended_horn_cup_contact':{ga,gb}=={'cup','rotor'}}
        if bad:result['invalid_boolean_results'].append(row)
        elif min(span)<.00005:result['flat_touches']+=1
        elif volume>.005:
            if {a.name,b.name}=={'REFERENCE SG92R body','REFERENCE SG92R horn'}:result['reference_output_interfaces'].append(row)
            else:result['finite_intersections'].append(row)
    result['samples'].append({'t':r['t'],'lid_deg':r['lidDeg'],'servo_deg':r['servoDeg']})
    print('logged CAD sample',round(r['t'],3),round(r['lidDeg'],3),'finite',len(result['finite_intersections']),'invalid',len(result['invalid_boolean_results']),flush=True)
result['source_unchanged']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()==digest
(ROOT.parent/'assets/logged_cad_pose_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print('COMPLETE',json.dumps({'samples':len(selected),'finite':len(result['finite_intersections']),'invalid':len(result['invalid_boolean_results']),'source_unchanged':result['source_unchanged']}),flush=True)
