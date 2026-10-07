"""Read saved CAD and exported meshes; sample real 3D intersections."""
import bpy,bmesh,sys,pathlib,math,json,struct,itertools,hashlib
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
import params as p
from cad_utils import pivot_transform
data=json.loads((R/'assembly_manifest.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
O=Vector(data['O']);H=Vector(data['H']);r=data['crank_r_mm'];L=data['link_length_mm'];uv=Vector(data['rocker_local_mm'])
theta0=math.radians(data['servo_range_deg'][0]);A0=O+r*Vector((math.cos(theta0),math.sin(theta0)));B0=H+uv
groups={x['name']:x['group'] for x in data['parts']};objs=[bpy.data.objects[n] for n in groups];ghost=[o for o in bpy.data.objects if o.name.startswith('REFERENCE')]
closed={o.name:o.matrix_world.copy() for o in objs+ghost};Tc0=pivot_transform(*O,theta0)
neutral={o.name:Tc0.inverted()@closed[o.name] if groups.get(o.name)=='crank' or o.name.endswith('horn') else closed[o.name] for o in objs+ghost}
def state(deg):
    t=math.radians(deg);B=H+Vector((uv.x*math.cos(t)-uv.y*math.sin(t),uv.x*math.sin(t)+uv.y*math.cos(t)))
    d=B-O;c=(d.length**2+r*r-L*L)/(2*d.length*r);th=math.atan2(d.y,d.x)-math.acos(c);A=O+r*Vector((math.cos(th),math.sin(th)))
    Tl=pivot_transform(*H,t);Tc=pivot_transform(*O,th);angle=math.atan2((B-A).y,(B-A).x)-math.atan2((B0-A0).y,(B0-A0).x)
    Tk=Matrix.Translation(Vector((0,*A))*.001)@Matrix.Rotation(angle,4,'X')@Matrix.Translation(Vector((0,*(-A0)))*.001)
    for o in objs+ghost:
        g=groups.get(o.name);T=Tl if g=='lid' else Tc if g=='crank' or o.name.endswith('horn') else Tk if g=='link' else Matrix.Identity(4)
        o.matrix_world=T@neutral[o.name]
    return math.degrees(th)
def tree(o):
    o.data.calc_loop_triangles();verts=[o.matrix_world@v.co for v in o.data.vertices];faces=[tuple(t.vertices) for t in o.data.loop_triangles]
    return BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=1e-9)
def volume_intersection(a,b):
    aa=a.copy();aa.data=a.data.copy();bpy.context.collection.objects.link(aa)
    mod=aa.modifiers.new('intersection check','BOOLEAN');mod.solver='EXACT';mod.operation='INTERSECT';mod.object=b
    bpy.context.view_layer.objects.active=aa;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(aa.data);vol=abs(bm.calc_volume())*1e9;bad=sum(not e.is_manifold for e in bm.edges);bounds=[]
    if bm.verts:
        points=[aa.matrix_world@v.co*1000 for v in bm.verts];bounds=[[min(v[k] for v in points) for k in range(3)],[max(v[k] for v in points) for k in range(3)]]
    bm.free();bpy.data.objects.remove(aa,do_unlink=True)
    return {'volume_mm3':vol,'nonmanifold_edges':bad,'bounds_mm':bounds}
result={'angle_step_deg':.5,'physical_tested':False,'collision_method':'BVH triangle intersections and containment sampled every half degree; exact intersection volumes; does not prove continuous motion or real fit','collisions':[],'touches':[],'invalid_intersection_volumes':[],'flat_contact_intersections':[]}
result['input_blend_sha256']=hashlib.sha256((R/'editable_cube_v6.blend').read_bytes()).hexdigest()
allobjs=objs+ghost
for sample in range(round(data['lid_range_deg'][1]*2)+1):
    deg=sample/2
    state(deg);trees={o.name:tree(o) for o in allobjs}
    boxes={o.name:[Vector([min((o.matrix_world@v.co)[k] for v in o.data.vertices) for k in range(3)]),Vector([max((o.matrix_world@v.co)[k] for v in o.data.vertices) for k in range(3)])] for o in allobjs}
    for a,b in itertools.combinations(allobjs,2):
        if a in ghost and b in ghost:continue
        if deg and groups.get(a.name)=='fixed' and groups.get(b.name)=='fixed':continue
        ba,bb=boxes[a.name],boxes[b.name]
        if any(ba[1][k]<bb[0][k]+1e-9 or bb[1][k]<ba[0][k]+1e-9 for k in range(3)):continue
        overlaps=trees[a.name].overlap(trees[b.name])
        if not overlaps:
            # Closed connected solids can be wholly inside another solid.
            def inside(src,target):
                point=src.matrix_world@src.data.vertices[0].co
                near=trees[target.name].find_nearest(point)
                if near[0] is None or near[3]<1e-7:return False
                direction=Vector((1,.371,.193)).normalized();hits=0
                for j in range(100):
                    hit=trees[target.name].ray_cast(point,direction)
                    if hit[0] is None:break
                    hits+=1;point=hit[0]+direction*1e-7
                return bool(hits%2)
            if not inside(a,b) and not inside(b,a):continue
        x=volume_intersection(a,b);row={'lid_deg':deg,'parts':[a.name,b.name],'overlap_tri_pairs':len(overlaps),**x}
        if x['nonmanifold_edges']:
            result['invalid_intersection_volumes'].append(row)
        elif x['bounds_mm'] and min(x['bounds_mm'][1][k]-x['bounds_mm'][0][k] for k in range(3))<.00005:
            result['flat_contact_intersections'].append(row)
        elif x['volume_mm3']>.005:result['collisions'].append(row)
        elif deg in (0,30,65):result['touches'].append(row)
    if deg%10==0:print('pose',deg,'collisions',len(result['collisions']),flush=True)
state(0)
(R/'motion_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
summary={}
for row in result['collisions']:
    key=' / '.join(row['parts']);s=summary.setdefault(key,{'first_deg':row['lid_deg'],'last_deg':row['lid_deg'],'max_mm3':0});s['last_deg']=row['lid_deg'];s['max_mm3']=max(s['max_mm3'],row['volume_mm3'])
print('COLLISION SUMMARY',json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
