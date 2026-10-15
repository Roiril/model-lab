"""Cassette solids in millimetres; no exports and no scene reset."""
import ast
import math
from pathlib import Path
import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from printmech import geometry as G
from . import params as P, kinematics as K
from .recipe import build_mount

M = lambda x: x*1000
O = M(P.AXIS_U)


def clone(ob, name):
    copy=ob.copy()
    copy.data=ob.data.copy()
    copy.name=name
    bpy.context.collection.objects.link(copy)
    return copy


def radial(ob, angle):
    mat=Matrix.Translation((O,0,0)) @ Matrix.Rotation(math.radians(angle),4,'Z')
    G.transform(ob,mat)
    return ob


def rb(r0,r1,t0,t1,d0,d1,angle,name='radial'):
    return radial(G.box(r0,r1,t0,t1,d0,d1,name),angle)


def ring(ri,ro,d0,d1,name='ring',n=192):
    ob=G.prism(G.circle((O,0),ro,n),'z',d0,d1,name)
    return G.cut(ob,G.prism(G.circle((O,0),ri,n),'z',d0-.5,d1+.5))


def reference_parts(common):
    # Execute definitions only. Never import/execute the exporting model script.
    path=Path(common.ROOT)/'models/sg92r-photo/model.py'
    tree=ast.parse(path.read_text(encoding='utf-8'))
    ns=dict(vars(common.SG),bpy=bpy,bmesh=bmesh,math=math,Vector=Vector,EPS=.00002)
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(path),'exec'),ns)
    placement=Matrix(((-1000,0,0,O),(0,1000,0,0),(0,0,-1000,M(P.SERVO_BOTTOM_D)),(0,0,0,1)))
    out={}
    for pid,fn in (('servo','build_body'),('horn','build_horn')):
        ob=ns[fn]()
        ob.data.transform(ob.matrix_world)
        ob.matrix_world=Matrix.Identity(4)
        ob.data.transform(placement)
        G.clean(ob)
        out[pid]=ob
    return out


def cam_shell(which):
    if which=='upper': return upper_cam_shell()
    angles=np.arange(0,360,P.CAM_MESH_STEP_DEG)
    inner=P.UPPER_CAM_INNER_RADIUS if which=='upper' else P.CAM_INNER_RADIUS
    radii=np.linspace(M(inner),M(P.CAM_RADIUS),P.RADIAL_SAMPLES)
    n=len(angles)
    vs=[]
    for r in radii:
        shallow,deep=K.groove_bounds(r,angles)
        for side in range(2):
            z=(np.full(n,M(P.CAM_FRONT_D)) if side==0 else shallow) if which=='upper' else (deep if side==0 else np.full(n,M(P.CAM_BACK_D)))
            for a,d in zip(np.radians(angles),z):
                vs.append((O+r*math.cos(a),r*math.sin(a),float(d)))
    faces=[]
    def idx(j,side,k): return j*2*n+side*n+(k % n)
    for j in range(len(radii)-1):
        for side in (0,1):
            for k in range(n):
                faces.append((idx(j,side,k),idx(j,side,k+1),idx(j+1,side,k+1),idx(j+1,side,k)))
    for j in (0,len(radii)-1):
        for k in range(n):
            faces.append((idx(j,0,k),idx(j,1,k),idx(j,1,k+1),idx(j,0,k+1)))
    me=bpy.data.meshes.new('cam_'+which)
    me.from_pydata(vs,[],faces); me.update()
    ob=bpy.data.objects.new('cam_'+which,me); bpy.context.collection.objects.link(ob)
    bm=bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(ob.data); bm.free()
    G.clean(ob)
    return ob


def upper_cam_shell():
    angles=np.arange(0,360,P.CAM_MESH_STEP_DEG)
    radii=np.linspace(M(P.UPPER_CAM_INNER_RADIUS),M(P.CAM_RADIUS),P.RADIAL_SAMPLES)
    n=len(angles)
    vertices=[(O,0,M(P.CAM_FRONT_D)),(O,0,4.25)]
    def add_ring(r,depth):
        start=len(vertices)
        depths=np.full(n,depth) if np.isscalar(depth) else depth
        vertices.extend((O+r*math.cos(a),r*math.sin(a),float(d))
                        for a,d in zip(np.radians(angles),depths))
        return start
    front=[add_ring(r,M(P.CAM_FRONT_D)) for r in radii]
    inner=add_ring(M(P.UPPER_CAM_INNER_RADIUS),4.25)
    back=[add_ring(r,K.groove_bounds(r,angles)[0]) for r in radii]
    faces=[]
    def bridge(a,b):
        for k in range(n):
            j=(k+1)%n
            faces.append((a+k,a+j,b+j,b+k))
    for k in range(n):
        j=(k+1)%n
        faces.extend(((0,front[0]+j,front[0]+k),(1,inner+k,inner+j)))
    for a,b in zip(front[:-1],front[1:]): bridge(a,b)
    bridge(inner,back[0])
    for a,b in zip(back[:-1],back[1:]): bridge(a,b)
    bridge(front[-1],back[-1])
    mesh=bpy.data.meshes.new('cam_upper')
    mesh.from_pydata(vertices,[],faces); mesh.update()
    cam=bpy.data.objects.new('cam_upper',mesh); bpy.context.collection.objects.link(cam)
    G.clean(cam,dist=.002)
    bm=bmesh.new(); bm.from_mesh(cam.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(cam.data); bm.free()
    return cam


def upper_cam(sg):
    cam=cam_shell('upper')
    # Two pairs of taper-matched 3 mm tangential bearing blocks, at r=10..14.
    # Horn native x is reversed in local u; 18 mm and 16 mm arms are not exchanged.
    for side,end in ((-1,M(sg.HORN_LEFT_X)),(1,M(sg.HORN_RIGHT_X))):
        for sign in (-1,1):
            xs=[side*10,side*14]
            def halfwidth(x):
                return M(sg.HORN_ROOT_W)/2+(abs(x)-M(sg.HORN_HUB_DIA)/2)*(M(sg.HORN_TIP_W-sg.HORN_ROOT_W)/2)/(abs(end)-M(sg.HORN_HUB_DIA)/2)
            points=[(-x,sign*(halfwidth(x)+M(P.HORN_CLEARANCE))) for x in xs]
            points += [(-x,sign*(halfwidth(x)+M(P.HORN_CLEARANCE)+3)) for x in xs[::-1]]
            points=[(x+O,y) for x,y in points]
            G.union(cam,G.prism(points,'z',4.15,7.25))
    # Short-arm end stop rejects 180 degree reversal; long arm has an open tip.
    short=M(sg.HORN_RIGHT_X)
    G.union(cam,G.box(O-short-2.5,O-short-.25,-2,2,4.15,7.25))
    return cam


def cam_pair(sg):
    upper=upper_cam(sg)
    lower=cam_shell('lower')
    for a in P.CAM_KEY_DEG:
        G.union(upper,rb(19.25,24.5,-3,3,4.2,10.2,a))
        G.union(lower,rb(20.05,24.5,-3,3,10.75,14.95,a))
    # Keep 1.2 mm around the recessed heads; roofs grow inward at 45 degrees.
    for a in P.CAM_KEY_DEG: G.union(upper,rb(17.85,25.65,-3.9,3.9,2.25,6,a))
    for a in P.CAM_KEY_DEG:
        head_outer=27 if a==181 else 24.45
        shaft_outer=27 if a==181 else 23.45
        head=[(19.05,-2.7),(head_outer,-2.7),(head_outer,2.7),(19.05,2.7)]
        shaft=[(20.05,-1.7),(shaft_outer,-1.7),(shaft_outer,1.7),(20.05,1.7)]
        pocket_back=M(P.CAM_KEY_HEAD_D)+M(P.CAM_KEY_HEAD_T)+M(P.CAM_KEY_HEAD_CLEARANCE)
        hole=G.loft_rings([(1.75,head),(pocket_back,head),(pocket_back+1,shaft),(17,shaft)],'key_cavity')
        radial(hole,a); G.cut(upper,hole)
    for a in P.CAM_KEY_DEG:
        # The U receiver keeps both tangential walls and the outer snap hook.
        profile=[(19,3.2),(23.45,3.2),(23.45,13.1),(23.8,13.1),
                 (23.8,14.8),(23.45,14.8),(23.45,17),(19,17)]
        hole=G.prism(profile,'y',-1.7,1.7)
        radial(hole,a); G.cut(lower,hole)
        wedge=G.prism([(19.1,14.96),(23.3,14.96),(19.1,10.5)],'y',-3.01,3.01)
        radial(wedge,a); G.cut(lower,wedge)
    # Keep the full inner working land; relieve only the outer rim at the
    # left exchange key's complete +/-30 degree sweep and panel pad corner.
    angles=np.linspace(150,255,211)
    profile=[(O+30*math.cos(math.radians(a)),30*math.sin(math.radians(a))) for a in angles]
    relief=M(P.UPPER_CAM_RELIEF_RADIUS)
    profile += [(O+relief*math.cos(math.radians(a)),relief*math.sin(math.radians(a))) for a in angles[::-1]]
    G.cut(upper,G.prism(profile,'z',1.5,11.0))
    return upper,lower


def octagon(cx,cy,half,cut):
    return [(cx-half+cut,cy-half),(cx+half-cut,cy-half),
            (cx+half,cy-half+cut),(cx+half,cy+half-cut),
            (cx+half-cut,cy+half),(cx-half+cut,cy+half),
            (cx-half,cy+half-cut),(cx-half,cy-half+cut)]


def stem_box(index,half,z0,z1):
    x,y=[M(v) for v in P.STEM_CENTRES[index]]
    ob=G.box(-half,half,-half,half,z0,z1)
    G.transform(ob,Matrix.Translation((x,y,0))@Matrix.Rotation(math.radians(P.STEM_ANGLES[index]),4,'Z'))
    return ob


def arc_band(r0,r1,start,end,z0,z1,name):
    angles=np.linspace(start,end,int(abs(end-start)*2)+1)
    vs=[]
    for z in (z0,z1):
        for r in (r0,r1):
            for a in np.radians(angles): vs.append((O+r*math.cos(a),r*math.sin(a),z))
    n=len(angles); faces=[]
    def at(z,r,k): return z*2*n+r*n+k
    for k in range(n-1):
        for z in (0,1): faces.append((at(z,0,k),at(z,0,k+1),at(z,1,k+1),at(z,1,k)))
        for r in (0,1): faces.append((at(0,r,k),at(1,r,k),at(1,r,k+1),at(0,r,k+1)))
    for k in (0,n-1): faces.append((at(0,0,k),at(0,1,k),at(1,1,k),at(1,0,k)))
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); G.clean(ob)
    return ob


def pixel(index,angle,name):
    hx,hy=[M(v) for v in P.HEAD_CENTRES[index]]
    cut=M(P.HEAD_CORNER_CUT[index]); wall=M(P.SKIRT_WALL)
    outline=lambda h,c: octagon(hx,hy,h,c)
    # Full perimeter 8 mm skirt. The face remains 14 x 14 at its extrema.
    head=G.loft_rings([(0,outline(6.7,max(.05,cut-.175736))),
                      (.3,outline(7,cut)),(10,outline(7,cut))],name)
    inner_cut=max(.05,cut-wall*(2-math.sqrt(2)))
    G.cut(head,G.prism(outline(7-wall,inner_cut),'z',2,10.5))
    pin=G.cyl_x((0,M(P.PIN_D)),2,M(P.PIN_R0),M(P.PIN_R1),64)
    radial(pin,angle)
    if index==1: G.union(pin,arc_band(27,M(P.PIXEL_2_BRIDGE_RADIUS),61,122,9.25,12.25,'pixel_bridge_2'))
    if index==2: G.union(pin,arc_band(27,31,240,299,9.25,12.25,'pixel_bridge_3'))
    if index==0: G.union(pin,G.box(13,16,-1,10,9.25,12.25))
    G.union(pin,stem_box(index,2,9.25,M(P.STEM_END_D)))
    return G.union(head,pin)


def guide_plate(interface):
    # Three rear U guides: the pin is entirely in front of them. Each stem
    # retains 3 mm guide engagement at the maximum 3 mm lift.
    ob=stem_box(1,5.25,16.75,19.75); ob.name='guide'
    G.union(ob,G.box(-19.25,-8.75,-23.25,-12.75,16.75,19.75),
            stem_box(0,5.25,16.75,19.75),
            G.box(11,14,12,24.5,16.75,19.75),
            G.box(-23.5,-20.5,-20.25,23.25,16.75,19.75),
            G.box(-23,-18.75,-20.25,-17.25,16.75,19.75))
    G.cut(ob,G.box(0,25,-10,6.25,16,20))
    for sign in (-1,1):
        def bx(x0,x1,y0,y1,z0,z1):
            lo,hi=sorted((sign*y0,sign*y1))
            return G.box(x0,x1,lo,hi,z0,z1)
        G.union(ob,bx(-19,14,21.5,24.5,16.75,19.75),
                bx(-14,-1,14,24.5,16.75,19.75),
                bx(-9,-1,10.75,17,17.5,20.5))
    # Re-cut guide bores after the bridges have been joined.
    for i in range(3): G.cut(ob,stem_box(i,2.25,16.25,21))
    # Taper the tongue undersides from the rear bridges. Retain the cap's
    # contact lands while growing every printed layer from the one below.
    for sign in (-1,1):
        profile=[(sign*y,z) for y,z in ((10,16),(13.9,16),(13.9,17.45),(10,20.57))]
        G.cut(ob,G.prism(profile,'x',-9.1,-.9))
        lo,hi=sorted((sign*10,sign*12.25))
        G.cut(ob,G.box(-9.1,-.9,lo,hi,17.49,21))
    return ob


def support_and_cap(panel,sg):
    # Ear floors and the cradle. Body and flange dimensions come from SG.
    half_l=M(sg.BODY_L)/2; half_f=M(sg.FLANGE_L)/2
    ear_back=M(P.SERVO_BOTTOM_D-sg.FLANGE_BOTTOM_Z)
    ear_front=ear_back-M(sg.FLANGE_T)
    floor=ear_back+.25
    support=G.box(-17.8,17.8,-14.5,-9.5,floor,floor+3,'support')
    G.union(support,G.box(-17.8,17.8,9.5,14.5,floor,floor+3))
    for sign in (-1,1):
        lo,hi=sorted((sign*(half_l+.25),sign*17.8))
        G.union(support,G.box(lo,hi,-12,12,floor,floor+3))
        lo,hi=sorted((sign*(half_f+.25),sign*17.8))
        G.union(support,G.box(lo,hi,-6.25,6.25,17.1,floor+.3))
    # Rear U frame routes around the cam instead of through its swept volume.
    G.union(support,G.box(-23.5,23.5,-24.5,-21.5,20.5,23.5))
    for sign in (-1,1):
        def mirrored(x0,x1,y0,y1,z0,z1):
            a,b=sorted((sign*x0,sign*x1))
            return G.box(a,b,y0,y1,z0,z1)
        if sign==1:
            G.union(support,G.box(14.8,17.8,10,18,20.5,23.5),
                    G.box(14.8,24,15,18,20.5,23.5),
                    G.box(21,24,15,18,7.5,23.5),
                    G.box(21,37.5,15,18,7.5,10.5),
                    G.box(32.5,37.5,15,18,2.3,10.5),
                    G.box(17,35,15.7,17.3,3.3,4.9),
                    G.box(17,20,15.7,17.3,.8,4),
                    G.box(17.6,19.4,15.1,17.9,.2,1.2))
            G.cut(panel,G.box(16.8,20.2,15.5,17.5,-.5,3.5),
                  G.box(17.4,19.6,14.9,18.1,-.5,1.4))
            continue
        G.union(support,mirrored(19,22,-23,-11.5,20.5,23.5),
                mirrored(14.8,22,-14.5,-11.5,20.5,23.5),
                mirrored(20.5,23.5,-24.5,-21.5,16.75,23.5))
        # Route before the seat (v=-30) and below the key head (v=-26).
        # The old outer U crossed both the seat and latch during insertion.
        G.union(support,G.box(-28.5,-25.5,-29.5,-21.5,10.2,16.5),
                G.box(-36.5,-25.5,-29.5,-26.5,7.5,10.5),
                G.box(-28.5,-21,-24.5,-21.5,13.5,16.5),
                G.box(-37.5,-34.5,-29.5,-26.5,3.25,10.5))
        # Small diagonal bridge is fully behind the rotating cam.
        G.union(support,mirrored(21,24,-24.5,-21.5,16.3,17.25))
        # Same 18 mm x 1.6 mm snap beam, ending before the frame latch.
        G.union(support,G.box(-36.8,-35.2,-28,-10,3.3,4.9),
                G.box(-36.8,-35.2,-13,-10,.8,4),
                G.box(-37.4,-34.6,-12.4,-10.6,.2,1.2))
        G.cut(panel,G.box(-37,-35,-13.2,-9.8,-.5,3.5),
              G.box(-37.6,-34.4,-12.6,-10.4,-.5,1.4))
    # Cap joins two ear retainers around the body. It also traps guide tongues.
    cap=G.box(-16,16,-12.5,12.5,ear_front-3.25,ear_front-.25,'servo_cap')
    G.cut(cap,G.box(-half_l-.25,half_l+.25,-M(sg.BODY_W)/2-.25,M(sg.BODY_W)/2+.25,12,20))
    G.intersect(cap,G.prism(G.circle((O,0),23.2,192),'z',12,20))
    for sign in (-1,1):
        x0,x1=sorted((sign*(14 if sign==1 else 16),sign*19.65))
        root0,root1=(-15,-12) if sign==1 else (-10.5,-7.5)
        G.union(cap,G.box(x0,x1,root0,root1,17.0,20.5))
        u=sign*18.85
        half=.6 if sign==1 else .8
        start=-12.2 if sign==1 else -9
        G.union(cap,G.box(u-half,u+half,root0,root1,17,23.3),
                G.box(u-half,u+half,start,9,21.7,23.3),
                G.box(u-half,u+half,7,10,22,25.2))
        xa,xb=sorted((sign*17.45,sign*19.65))
        G.union(cap,G.box(xa,xb,7,10,24,25.2))
    G.cut(cap,G.box(-16,16,6.0,20,12,20.5))
    G.union(cap,G.box(-15,-12,5,10,15.25,18.25),
            G.box(-15,-1,7,10,15.25,18.25),
            G.box(-9,-1,9,13.75,14.25,17.25),
            G.box(-8.5,-1,-13.75,-9,14.25,17.25))
    G.cut(cap,G.box(-9.25,-.75,-17.25,-10.5,17.25,18.6),
          G.box(-9.25,-.75,10.5,17.25,17.25,18.6))
    G.union(support,G.box(17.5,20.5,10.25,14.5,20.5,23.5))
    for i in range(3): G.cut(support,stem_box(i,2.25,16,24.25))
    return support,cap


def build(interface, common_params):
    K.read_patterns()
    panel,kl,kr=build_mount(interface)
    parts={'panel':panel,'key_l':kl,'key_r':kr}
    parts.update(reference_parts(common_params))
    for i,a in enumerate(P.FOLLOWER_DEG,1):
        x,y=[M(v) for v in P.HEAD_CENTRES[i-1]]
        cut=M(P.HEAD_CORNER_CUT[i-1])+.3*(2-math.sqrt(2))
        G.cut(panel,G.prism(octagon(x,y,7.3,cut),'z',-.5,2.05))
        parts[f'pixel_{i}']=pixel(i-1,a,f'pixel_{i}')
    support,cap=support_and_cap(panel,common_params.SG)
    parts.update(support=support,servo_cap=cap,guide=guide_plate(interface))
    upper,lower=cam_pair(common_params.SG)
    # Two keyed standoffs join the shells outside the horn and fixed guide ring.
    for i,a in enumerate(P.CAM_KEY_DEG,1):
        key=G.box(20.25,23.25,-1.5,1.5,2.5,14.95,f'cam_key_{i}')
        # Head is recessed in the upper web; split hooks spring into lower pockets.
        head_front=M(P.CAM_KEY_HEAD_D)
        head_back=head_front+M(P.CAM_KEY_HEAD_T)
        # The underside of the head is coplanar with the shaft in its flat
        # print orientation. Three head shoulders remain outside the socket;
        # the axial stops and spring thickness/length are unchanged.
        G.union(key,G.box(19.25,24.25,-1.5,2.5,head_front,head_back),
                G.box(19.9,23.6,-1.5,1.5,13.35,14.55))
        G.cut(key,G.box(21.45,22.05,-2,2,7.0,17))
        radial(key,a)
        parts[f'cam_key_{i}']=key
    parts.update(cam_upper=upper,cam_lower=lower)
    labels={'panel':'3画素の面板','key_l':'左の交換キー','key_r':'右の交換キー',
            'support':'サーボ座と面板の支持枠','servo_cap':'サーボと案内板の押さえ',
            'guide':'画素の案内板とカムの軸受け','cam_upper':'引き戻す上カム',
            'cam_lower':'押し出す下カム','servo':'SG92R','horn':'SG92R付属ホーン',
            'pixel_1':'画素1','pixel_2':'画素2','pixel_3':'画素3',
            'cam_key_1':'カム結合キー1','cam_key_2':'カム結合キー2'}
    out={}
    for pid in P.PART_IDS:
        ob=parts[pid]; ob.name=pid; G.clean(ob,dist=.002)
        bm=bmesh.new(); bm.from_mesh(ob.data)
        wires=[e for e in bm.edges if not e.link_faces]
        if wires: bmesh.ops.delete(bm,geom=wires,context='EDGES')
        if pid in ('cam_lower','cam_upper'):
            # Boolean key pockets leave collinear vertices in otherwise manifold faces.
            # Re-triangulate after each dissolve; one pass can expose a second zero face.
            for _ in range(8):
                bmesh.ops.triangulate(bm,faces=list(bm.faces))
                if all((f.verts[1].co-f.verts[0].co).cross(f.verts[2].co-f.verts[0].co).length >= 1e-9
                       for f in bm.faces):
                    break
                bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6)
            else:
                raise ValueError(f'{pid}: degenerate cam triangles remain')
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(ob.data); bm.free()
        rot=np.eye(4)
        if pid in ('cam_lower','support'):
            rot=np.asarray(Matrix.Rotation(math.pi,4,'X'))
        if pid.startswith('cam_key'):
            # Axial length and radial flex both lie in the print XY plane.
            a=P.CAM_KEY_DEG[int(pid[-1])-1]
            cycle=np.array([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1.]])
            rot=cycle@np.asarray(Matrix.Rotation(math.radians(-a),4,'Z'))
        out[pid]={'object':ob,'print_rotation':rot,'label':labels[pid],
                  'color':'#7598b3' if pid=='servo' else '#444844' if pid=='horn' else '#deddd5',
                  'purchased':pid in ('servo','horn')}
    return out
