import bpy,bmesh,math,struct
from mathutils import Vector,Matrix
M=.001
SOLVER_FALLBACKS=[]
def clean(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
def cube(n,lo,hi):
    bpy.ops.mesh.primitive_cube_add(size=1,location=Vector([(a+b)/2 for a,b in zip(lo,hi)])*M)
    o=bpy.context.object;o.name=n;o.dimensions=Vector([b-a for a,b in zip(lo,hi)])*M
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def cyl(n,c,r,l,axis='X',nv=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=nv,radius=r*M,depth=l*M,location=Vector(c)*M)
    o=bpy.context.object;o.name=n
    if axis=='X':o.rotation_euler[1]=math.pi/2
    elif axis=='Y':o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);return o
def prism(n,x0,x1,poly):
    k=len(poly);vs=[(x*M,y*M,z*M) for x in (x0,x1) for y,z in poly]
    fs=[list(reversed(range(k))),list(range(k,2*k))]+[[i,(i+1)%k,(i+1)%k+k,i+k] for i in range(k)]
    me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update()
    o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return clean(o)
def prism_y(n,y0,y1,poly):
    o=prism(n,y0,y1,poly)
    for v in o.data.vertices:v.co.x,v.co.y=v.co.y,v.co.x
    return clean(o)
def prism_z(n,z0,z1,poly):
    o=prism(n,z0,z1,poly)
    for v in o.data.vertices:v.co.x,v.co.y,v.co.z=v.co.y,v.co.z,v.co.x
    return clean(o)
def circle(y,z,r,n=64):return [(y+r*math.cos(i*math.tau/n),z+r*math.sin(i*math.tau/n)) for i in range(n)]
def capsule(n,x0,x1,a,b,r):
    v=Vector((b[0]-a[0],b[1]-a[1]));v.normalize();q=Vector((-v.y,v.x))*r
    poly=[tuple(Vector(a)+q),tuple(Vector(a)-q),tuple(Vector(b)-q),tuple(Vector(b)+q)]
    o=prism(n,x0,x1,poly)
    add(o,cyl(n+' end0',((x0+x1)/2,*a),r,x1-x0));add(o,cyl(n+' end1',((x0+x1)/2,*b),r,x1-x0));return o
def duplicate(o,n):
    q=o.copy();q.data=o.data.copy();bpy.context.collection.objects.link(q);q.name=n;return q
def boolean(a,b,op='DIFFERENCE'):
    assert len(a.data.vertices)>0,(a.name,'empty input',b.name)
    label=(a.name,op,b.name)
    original=a.data.copy()
    def apply(solver):
        bpy.context.view_layer.objects.active=a;mod=a.modifiers.new(solver+' '+op,'BOOLEAN');mod.solver=solver;mod.operation=op;mod.object=b
        bpy.ops.object.modifier_apply(modifier=mod.name)
    apply('EXACT');clean(a)
    check=bmesh.new();check.from_mesh(a.data);badout=sum(not e.is_manifold for e in check.edges);check.free()
    if not a.data.vertices or badout:
        a.data=original
        for target in (a,b):
            bm=bmesh.new();bm.from_mesh(target.data)
            bad=sum(not e.is_manifold for e in bm.edges);vol=abs(bm.calc_volume());bm.free()
            assert bad==0 and vol>1e-12,(label,'fallback requires closed nonzero inputs',bad,vol)
        apply('MANIFOLD');SOLVER_FALLBACKS.append(label);print('Closed-input MANIFOLD fallback',label,flush=True)
    else:bpy.data.meshes.remove(original)
    bpy.data.objects.remove(b,do_unlink=True);clean(a)
    assert len(a.data.vertices)>0,(label,'Boolean produced empty mesh')
    check=bmesh.new();check.from_mesh(a.data);badout=sum(not e.is_manifold for e in check.edges);vol=abs(check.calc_volume());check.free()
    assert badout==0 and vol>1e-12,(label,'Boolean requires closed positive volume',badout,vol)
    return a
def cut(a,b):return boolean(a,b)
def add(a,b):return boolean(a,b,'UNION')
def color(o,name,c):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*c,1)
    o.data.materials.clear();o.data.materials.append(m);return o
def diamond(n,x0,x1,y,z,r):return prism(n,x0,x1,[(y-r,z),(y,z-r),(y+r,z),(y,z+r)])
def pivot_transform(y,z,t):
    return Matrix.Translation(Vector((0,y,z))*M)@Matrix.Rotation(t,4,'X')@Matrix.Translation(Vector((0,-y,-z))*M)
def read_stl(path,n):
    data=path.read_bytes();count=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*count
    vs=[];faces=[];index={}
    for k in range(count):
        q=struct.unpack_from('<12fH',data,84+50*k);face=[]
        for j in range(3):
            xyz=tuple(round(v,6)*M for v in q[3+j*3:6+j*3])
            if xyz not in index:index[xyz]=len(vs);vs.append(xyz)
            face.append(index[xyz])
        faces.append(face)
    me=bpy.data.meshes.new(n);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return o
def export(o,path,T=None,normalize=True):
    path.parent.mkdir(parents=True,exist_ok=True);T=(T or Matrix.Identity(4))@o.matrix_world
    points=[T@v.co*1000 for v in o.data.vertices];lo=Vector([min(v[k] for v in points) for k in range(3)]) if normalize else Vector((0,0,0))
    me=bpy.data.meshes.new('export '+o.name);o.data.calc_loop_triangles()
    me.from_pydata([tuple(round(v[k]-lo[k],5) for k in range(3)) for v in points],[],[list(t.vertices) for t in o.data.loop_triangles]);me.update()
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00004)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00004)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.to_mesh(me);bm.free();me.calc_loop_triangles()
    # Round to float32 now, then repair collinear diagonals without dropping solid faces.
    pts=[Vector(struct.unpack('<3f',struct.pack('<3f',*v.co))) for v in me.vertices];tris=[list(t.vertices) for t in me.loop_triangles]
    def norm(t):
        a,b,c=[pts[i] for i in t]
        # Float32 STL vertices use double-precision differences for area tests.
        # Blender float32 cross products can erase a very narrow valid face.
        u=[float(b[k])-float(a[k]) for k in range(3)];v=[float(c[k])-float(a[k]) for k in range(3)]
        return Vector((u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]))
    for _ in range(12):
        bad=[i for i,t in enumerate(tris) if norm(t).length<1e-9]
        if not bad:break
        for i in bad:
            q=tris[i];edges=[(q[k],q[(k+1)%3]) for k in range(3)];a,b=max(edges,key=lambda e:(pts[e[0]]-pts[e[1]]).length);c=next(v for v in q if v not in (a,b))
            js=[j for j,t in enumerate(tris) if j!=i and a in t and b in t]
            assert len(js)==1,(o.name,'bad diagonal',i,js)
            j=js[0];d=next(v for v in tris[j] if v not in (a,b));n=norm(tris[j])
            for k,t in ((i,[a,c,d]),(j,[c,b,d])):
                if norm(t).dot(n)<0:t[1],t[2]=t[2],t[1]
                tris[k]=t
    assert all(norm(t).length>1e-9 for t in tris),(o.name,'remaining zero faces')
    with path.open('wb') as f:
        f.write((o.name+' | v6 | mm | PRINT PART').encode()[:80].ljust(80,b'\0'));f.write(struct.pack('<I',len(tris)))
        for t in tris:
            a,b,c=[pts[i] for i in t];n=norm(t).normalized();f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
    bpy.data.meshes.remove(me)
    return [max(v[k] for v in pts) for k in range(3)]
