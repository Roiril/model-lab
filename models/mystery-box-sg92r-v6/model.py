"""Native Blender CAD. Fixed rear cover, bevelled planar lid, rigid cassette.
Lengths in params.py are metres; construction helpers use millimetres.
The user's canonical servo meshes are imported as references only.
"""
import sys,pathlib,math,json,ast
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.dont_write_bytecode=True
import bpy,bmesh
from mathutils import Vector,Matrix
import params as p
from cad_utils import *
def q(k):return getattr(p,k)*1000
S=q('SIZE');W=q('WALL');roof=S-q('LID_SKIN');HY=q('HINGE_Y');HZ=q('HINGE_Z');OY=q('SERVO_Y');OZ=q('SERVO_Z');r=q('CRANK_R')
F=q('FIT');C=q('RUNNING');PR=q('ROOF_PEG_R');CP=q('COVER_PEG_R')
back=q('ROCKER_BACK_X');front=q('ROCKER_FRONT_X');rt=q('ROCKER_T');lx=q('LINK_X');lt=q('LINK_T')
theta0=math.radians(p.SERVO_CLOSED_DEG);O=Vector((OY,OZ));H=Vector((HY,HZ));uv=Vector((q('ROCKER_U'),q('ROCKER_V')));B0=H+uv;A0=O+r*Vector((math.cos(theta0),math.sin(theta0)));L=(B0-A0).length
def pose(deg):
    t=math.radians(deg);B=H+Vector((uv.x*math.cos(t)-uv.y*math.sin(t),uv.x*math.sin(t)+uv.y*math.cos(t)));d=B-O;c=(d.length**2+r*r-L*L)/(2*d.length*r)
    assert -1<c<1,('unreachable',deg,c)
    th=math.atan2(d.y,d.x)-math.acos(c);A=O+r*Vector((math.cos(th),math.sin(th)));return th,A,B
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
parts=[];groups={};print_rot={}
shell=('Shell',(.75,.76,.75));frame=('Cassette',(.14,.40,.47));moving=('Moving',(.80,.44,.13));linkmat=('Link',(.49,.22,.55));pins=('Keys',(.57,.65,.18))
def part(o,g='fixed',axis='X',reverse=False,mat=frame):
    parts.append(o);groups[o.name]=g
    T=Matrix.Rotation((1 if reverse else -1)*math.pi/2,4,'Y') if axis=='X' else Matrix.Rotation(math.pi,4,'Y') if axis=='-Z' else Matrix.Identity(4)
    print_rot[o.name]=T;color(o,*mat);return o
def bore(o,n,x0,x1,y,z,radius):
    if radius==2.8:radius=q('DRIVE_PIN_D')/2+C
    elif radius==3.3:radius=q('HINGE_PIN_D')/2+C
    elif radius==6.3:radius=q('JOURNAL_D')/2+C
    cut(o,cyl(n,((x0+x1)/2,y,z),radius,x1-x0))
def clip(o,n,lo,hi):cut(o,cube(n,lo,hi))

# Unmarked outside: open-top box, one straight rear-cover seam, planar lid.
body=cube('01_body',(0,0,0),(S,S,q('BODY_TOP')))
clip(body,'cavity',(W,W,W),(S-W,S-W,S+1))
clip(body,'underside cable opening',(3,63.8,-.5),(12,68.6,W+.5))
for xa,xb in ((0,W),(S-W,S)):
    add(body,cube('closed lid seat',(xa,S-4,q('BODY_TOP')-.1),(xb,S,roof)))
# Four positive drop-in receivers; no thin snap hooks. Crossmembers pass below.
for x0,x1 in ((4.,8.7),(56.1,60.1)):
    for yy in (5.4,60.4):
        upper=52.0 if yy>30 else 48.0
        socket=cube('vertical receiver',(x0-2.7,yy-2.4,W),(x1+2.7,yy+5.6,upper))
        clip(socket,'receiver open slot',(x0-.3,0,18),(x1+.3,70,upper+.5))
        if yy>30:
            ramp=prism('key rear ramp',x0-2.7,x1+2.7,[(56.4,44),(60.4,40),(60.4,52),(56.4,52)])
            add(socket,ramp)
            clip(socket,'receiver repeated clearance',(x0-.3,0,22.3),(x1+.3,70,upper+.5))
        add(body,socket)
# Key is rectangular and flat printed; diamond bore roofs have 45 degree slopes.
cut(body,diamond('body cross-key through',2.5,64.5,q('BODY_KEY_Y'),q('BODY_KEY_Z'),4.8))
clip(body,'side key insertion access',(64.0,q('BODY_KEY_Y')-5.1,q('BODY_KEY_Z')-2.4),(S+.5,q('BODY_KEY_Y')+5.1,q('BODY_KEY_Z')+2.4))
part(body,axis='Z',mat=shell)

cover=cube('02_fixed_rear_cover',(0,0,roof),(S,q('FIXED_BAND_END'),S))
# Two axial sockets captured between opposite integral locating pegs.
for x0,x1 in ((9.,14.4),(50.5,55.8)):
    add(cover,cube('cover socket',(x0,4.,58.5),(x1,12.,roof+.1)))
    cut(cover,diamond('cover locating through',x0-.4,x1+.4,8.,64.,CP+F))
part(cover,axis='-Z',mat=shell)

lid=prism('03_planar_lid',0,S,[(q('LID_REAR_TOP'),S),(S,S),(S,roof),(q('LID_REAR_INNER'),roof)])
# Open forks slide into a simple roof dock, retained by the front rocker's peg.
shoe=cube('roof fork dock',(41.,31.5,57.6),(55.9,51.7,roof+.1))
for xx in (back,front):
    clip(shoe,'open fork slot',(xx-.3,26.,57.3),(xx+rt+.3,49.3,67.3))
clip(shoe,'link upper swing well',(back+rt-.2,26.,57.3),(front+.2,44.3,64.))
add(lid,shoe)
cut(lid,diamond('roof peg simple through',40.6,56.3,q('ROOF_PEG_Y'),q('ROOF_PEG_Z'),PR+F))
part(lid,'lid','-Z',mat=shell)

# One cassette: flat rear plate, broad cradle, two integral axial crossmembers.
cass=cube('04_main_cassette',(4.,5.4,18.),(8.7,67.,67.3))
platform=cube('servo floor',(8.6,18.7,24.),(37.,51.3,31.))
add(cass,platform)
walls=cube('servo side walls',(8.6,18.7,30.9),(31.3,51.3,43.3))
clip(walls,'case top entry',(8.7,OY-16.8,31.),(31.7,OY+6.8,80.))
clip(walls,'ear top entry',(24.7,OY-21.3,31.),(31.7,OY+11.3,80.))
clip(walls,'wire top entry',(12.4,OY+6.2,31.),(31.7,OY+15.,80.))
add(cass,walls)
for yy in (12.5,52.):add(cass,cube('integral spacer',(8.6,yy,18.),(55.8,yy+3.6,22.)))
# Strong hinge boss grows from an axial rib through a 45 degree clipped ramp.
add(cass,cube('hinge axial rib',(8.6,15.,56.3),(28.1,18.4,67.3)))
hb=cyl('rear hinge ramp',(35.75,HY,HZ),5.5,15.5)
clip(hb,'ramp bounding half-space',(0,27.6,0),(37.1,80,90))
# Diagonal cut is independent of z: y <= 18.4+(x-28), until full boss.
cut(hb,prism_z('hinge ramp diagonal',0,90,[(27.9,18.3),(37.2,27.6),(37.2,80),(27.9,80)]))
add(cass,hb)
bore(cass,'rear hinge blind',41.3,43.9,HY,HZ,3.3)
# U-shaped rear thrust saddle. Its front thrust face is printed up; only its
# nonfunctional rear overhang may receive sparse removable support.
saddle=cyl('rear thrust saddle',(34.15,OY,OZ),12.4,5.7)
bore(saddle,'gear keepout',30.9,37.4,OY,OZ,9.2)
clip(saddle,'open upper thrust saddle',(30,0,OZ),(40,80,80))
add(cass,saddle)
# Temporary support columns land on this recessed nonfunctional surface,
# 2.3 mm behind the servo's case datum, not on its axial locating face.
clip(cass,'recessed support landing',(6.7,OY-15.5,27.),(9.,OY+15.5,41.))
# Cover peg and top-keeper end pocket are integral, not tiny snaps.
add(cass,diamond('rear cover integral peg',8.6,14.1,8.,64.,CP))
clip(cass,'top keeper end pocket',(6.6,23.2,43.3),(9.2,29.,47.3))
cut(cass,diamond('cassette cross-key',3.5,9.2,q('BODY_KEY_Y'),q('BODY_KEY_Z'),4.8))
part(cass,mat=frame)

closure=cube('05_front_closure',(56.1,5.4,18.),(60.1,67.,67.3))
bore(closure,'front hinge blind',55.7,58.3,HY,HZ,3.3)
add(closure,cyl('front journal tower',(51.7,OY,OZ),8.5,9.0))
bore(closure,'journal blind bore',46.8,58.3,OY,OZ,6.3)
add(closure,cube('rigid servo top keeper',(6.9,23.2,43.3),(56.2,29.,47.3)))
add(closure,cube('servo axial keeper',(31.3,23.2,42.),(56.2,25.8,43.4)))
add(closure,diamond('front cover integral peg',51.,56.2,8.,64.,CP))
# A-axis tail runs in an open-to-rear, blind arc. No spring, detent or pressure.
a0=math.radians(-25);a1=math.radians(85);ht=3.1;track=[]
for i in range(89):
    a=a0+(a1-a0)*i/88;track.append((OY+(r+ht)*math.cos(a),OZ+(r+ht)*math.sin(a)))
ey,ez=OY+r*math.cos(a1),OZ+r*math.sin(a1)
for i in range(1,33):a=a1+math.pi*i/32;track.append((ey+ht*math.cos(a),ez+ht*math.sin(a)))
for i in range(1,89):
    a=a1-(a1-a0)*i/88;track.append((OY+(r-ht)*math.cos(a),OZ+(r-ht)*math.sin(a)))
ey,ez=OY+r*math.cos(a0),OZ+r*math.sin(a0)
for i in range(1,32):a=a0+math.pi+math.pi*i/32;track.append((ey+ht*math.cos(a),ez+ht*math.sin(a)))
cut(closure,prism('A tail blind arc',55.7,58.3,track))
cut(closure,diamond('closure cross-key',55.7,60.5,q('BODY_KEY_Y'),q('BODY_KEY_Z'),4.8))
part(closure,reverse=True,mat=frame)

# Bundle the approved reference without changing or reconstructing it.
ref=pathlib.Path(p.REFERENCE_FOLDER);snap=R/'reference';snap.mkdir(exist_ok=True)
if ref.exists():
    D={}
    for node in ast.parse((ref/'params.py').read_text(encoding='utf-8-sig')).body:
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name):
            try:D[node.targets[0].id]=ast.literal_eval(node.value)
            except (TypeError,ValueError):pass
    (snap/'dimensions.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf8')
    for fn in ('body','horn','wire'):
        (snap/('sg92r-photo-'+fn+'.stl')).write_bytes((ref.parent.parent/'exports'/('sg92r-photo-'+fn+'.stl')).read_bytes())
else:D=json.loads((snap/'dimensions.json').read_text(encoding='utf8'))
def hd(k):return D[k]*1000
def arm_outline(c):
    rad=hd('HORN_TIP_W')/2;left=hd('HORN_LEFT_X')+rad;right=hd('HORN_RIGHT_X')-rad;root=hd('HORN_HUB_DIA')/2;half=hd('HORN_ROOT_W')/2;poly=[]
    for i in range(9):a=math.pi+i*math.pi/16;poly.append(Vector((left+rad*math.cos(a),rad*math.sin(a))))
    poly.extend([Vector((-root,-half)),Vector((root,-half)),Vector((right,-rad))])
    for i in range(1,17):a=-math.pi/2+i*math.pi/16;poly.append(Vector((right+rad*math.cos(a),rad*math.sin(a))))
    poly.extend([Vector((root,half)),Vector((-root,half)),Vector((left,rad))])
    for i in range(1,9):a=math.pi/2+i*math.pi/16;poly.append(Vector((left+rad*math.cos(a),rad*math.sin(a))))
    if (poly[-1]-poly[0]).length<1e-6:poly.pop()
    out=[]
    for i,b in enumerate(poly):
        e1=(b-poly[i-1]).normalized();e2=(poly[(i+1)%len(poly)]-b).normalized();n1=Vector((e1.y,-e1.x));n2=Vector((e2.y,-e2.x));out.append(tuple(b+(n1+n2)*c/max(.05,1+n1.dot(n2))))
    t=math.radians(p.HORN_PHASE_DEG)
    return [(OY+y*math.cos(t)-z*math.sin(t),OZ+y*math.sin(t)+z*math.cos(t)) for y,z in out]
cx0=q('CUP_REAR_X');cx1=q('CUP_FRONT_X');ce=q('CUP_POCKET_END_X')
cup=prism('06_horn_cup_journal',cx0,cx1,arm_outline(3.3))
phase=math.radians(p.HORN_PHASE_DEG);v=Vector((-math.sin(phase),math.cos(phase)));aa=O+v*(hd('HORN_SPAN_Y')/2-hd('HORN_SHORT_W')/2);bb=O-v*(hd('HORN_SPAN_Y')/2-hd('HORN_SHORT_W')/2)
add(cup,capsule('short outer',cx0,cx1,aa,bb,hd('HORN_SHORT_W')/2+3.3))
add(cup,cyl('cup centre',((cx0+cx1)/2,OY,OZ),12.1,cx1-cx0))
add(cup,cyl('drive boss',((ce-.1+cx1)/2,OY+r,OZ),5.5,cx1-ce+.1))
cut(cup,prism('actual long horn pocket',cx0-.5,ce,arm_outline(F)))
cut(cup,capsule('actual short horn pocket',cx0-.5,ce,aa,bb,hd('HORN_SHORT_W')/2+F))
bore(cup,'hub rear clearance',cx0-.5,ce,OY,OZ,9.1)
add(cup,cyl('integral thick journal',((cx1-.1+q('JOURNAL_END_X'))/2,OY,OZ),q('JOURNAL_D')/2,q('JOURNAL_END_X')-cx1+.1))
bore(cup,'A blind bearing',43.1,cx1+.4,OY+r,OZ,2.8)
part(cup,'crank',reverse=True,mat=moving)

for k,xx in enumerate((back,front)):
    elbow=H+Vector((14.,-10.))
    rock=capsule('07_rear_rocker' if k==0 else '08_front_rocker',xx,xx+rt,H,elbow,2.4)
    add(rock,capsule('rocker elbow',xx,xx+rt,elbow,B0,2.4))
    add(rock,cyl('hinge eye',((xx+xx+rt)/2,HY,HZ),5.5,rt))
    add(rock,cyl('B eye',((xx+xx+rt)/2,*B0),5.,rt))
    add(rock,cube('broad roof tenon',(xx,33.3,57.9),(xx+rt,49.,67.)))
    bore(rock,'hinge through',xx-.4,xx+rt+.4,HY,HZ,3.3)
    xa,xb=(xx+1.8,xx+rt+.4) if k==0 else (xx-.4,xx+rt-1.8)
    bore(rock,'B blind bearing',xa,xb,*B0,2.8)
    if k==0:cut(rock,diamond('roof locating through',xx-.4,xx+rt+.4,q('ROOF_PEG_Y'),q('ROOF_PEG_Z'),PR+F))
    else:add(rock,diamond('integral roof peg',41.2,xx+.1,q('ROOF_PEG_Y'),q('ROOF_PEG_Z'),PR))
    part(rock,'lid',reverse=k==1,mat=moving)

v=(B0-A0).normalized();mid=(A0+B0)/2+Vector((v.y,-v.x))*4.4;e1=(mid-A0).normalized();e2=(B0-mid).normalized();n1=Vector((-e1.y,e1.x));n2=Vector((-e2.y,e2.x));mit=(n1+n2)*3/(1+n1.dot(n2));eye=q('LINK_EYE_R');s=math.sqrt(eye*eye-9.);aoff=math.atan2(3.,s)
outline=[tuple(A0+e1*s+n1*3),tuple(mid+mit),tuple(B0-e2*s+n2*3)];ang=math.atan2(e2.y,e2.x)
for i in range(1,65):a=ang+math.pi-aoff-(2*math.pi-2*aoff)*i/64;outline.append(tuple(B0+Vector((math.cos(a),math.sin(a)))*eye))
outline.extend([tuple(mid-mit),tuple(A0+e1*s-n1*3)]);ang=math.atan2(e1.y,e1.x)
for i in range(1,64):a=ang-aoff-(2*math.pi-2*aoff)*i/64;outline.append(tuple(A0+Vector((math.cos(a),math.sin(a)))*eye))
link=prism('09_link',lx,lx+lt,outline)
for yy,zz in (A0,B0):bore(link,'link bearing',lx-.4,lx+lt+.4,yy,zz,2.8)
part(link,'link',mat=linkmat)

def axle(n,x0,x1,y,z,d,g):
    a=cyl(n,((x0+x1)/2,y,z),d/2,x1-x0);h=d/2/math.sqrt(2)
    clip(a,'lower shaft flat',(x0-.1,y-d,z-d),(x1+.1,y+d,z-h))
    clip(a,'upper shaft flat',(x0-.1,y-d,z+h),(x1+.1,y+d,z+d))
    return part(a,g,axis='Z',mat=pins)
axle('10_hinge_axle',41.6,58.,HY,HZ,q('HINGE_PIN_D'),'fixed')
axle('11_drive_axle',43.4,58.,OY+r,OZ,q('DRIVE_PIN_D'),'crank')
axle('12_link_axle',back+2.1,front+rt-2.1,*B0,q('DRIVE_PIN_D'),'lid')
key=cube('13_body_cross_key',(3.0,q('BODY_KEY_Y')-2.4,q('BODY_KEY_Z')-2.1),(67.1,q('BODY_KEY_Y')+2.4,q('BODY_KEY_Z')+2.1))
add(key,cube('flush side key cap',(67.0,q('BODY_KEY_Y')-4.8,q('BODY_KEY_Z')-2.1),(S,q('BODY_KEY_Y')+4.8,q('BODY_KEY_Z')+2.1)))
part(key,axis='Z',mat=pins)

mapping=Matrix(((0,0,1,0),(1,0,0,0),(0,1,0,0),(0,0,0,1)));trans=Matrix.Translation(Vector((q('SERVO_BASE_X'),OY,OZ))*.001);ghost=[]
for fn in ('body','horn','wire'):
    o=read_stl(snap/('sg92r-photo-'+fn+'.stl'),'REFERENCE SG92R '+fn);o.matrix_world=trans@mapping
    if fn=='horn':o.matrix_world=pivot_transform(OY,OZ,phase)@o.matrix_world
    color(o,'Servo reference' if fn=='body' else 'Dark reference',(.09,.23,.64) if fn=='body' else (.13,.13,.15));ghost.append(o)
o=cyl('REFERENCE exciter25x10',(q('EXCITER_X'),q('EXCITER_Y'),W+.5+q('EXCITER_H')/2),q('EXCITER_D')/2,q('EXCITER_H'),'Z');color(o,'Exciter',(.18,.18,.18));ghost.append(o)
base={o.name:o.matrix_world.copy() for o in parts+ghost}
def set_pose(deg):
    th,A,B=pose(deg);Tl=pivot_transform(HY,HZ,math.radians(deg));Tc=pivot_transform(OY,OZ,th);ang=math.atan2((B-A).y,(B-A).x)-math.atan2((B0-A0).y,(B0-A0).x)
    Tk=Matrix.Translation(Vector((0,*A))*.001)@Matrix.Rotation(ang,4,'X')@Matrix.Translation(Vector((0,*(-A0)))*.001)
    for o in parts+ghost:
        g=groups.get(o.name);T=Tl if g=='lid' else Tc if g=='crank' or o.name.endswith('horn') else Tk if g=='link' else Matrix.Identity(4);o.matrix_world=T@base[o.name]
set_pose(0)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'editable_cube_v6.blend'))
manifest=[]
for o in parts:
    state=o.matrix_world.copy();o.matrix_world=base[o.name];dims=export(o,R/'stl'/(o.name+'.stl'),print_rot[o.name]);o.matrix_world=state
    manifest.append(dict(name=o.name,group=groups[o.name],print_bounds_mm=dims,print_axis=list(print_rot[o.name].to_quaternion()),quantity=1))
record=dict(center_screw_required=False,size_mm=S,wall_mm=W,lid_skin_mm=q('LID_SKIN'),O=list(O),H=list(H),crank_r_mm=r,rocker_local_mm=list(uv),link_length_mm=L,lid_range_deg=[0,p.OPEN_DEG],servo_range_deg=[math.degrees(pose(0)[0]),math.degrees(pose(p.OPEN_DEG)[0])],parts=manifest,reference_source=str(ref),physical_tested=False,boolean_solver_fallbacks=SOLVER_FALLBACKS,notes=['13 print parts including three thick axles; actual servo/horn/cable are additional; no center screw is used','Fixed cover and roof locating pegs are integral; front closure and body receivers capture them','Support allowed only on marked inner nonfunctional surfaces of cassette and cup','Original horn is axially captured only after the body receivers and cross key are assembled; reference tooth engagement remains provisional','Hinge carries radial weight; servo supplies gravity torque; unpowered lid can close'])
(R/'assembly_manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print('BUILD OK',json.dumps(record|{'parts':len(parts)},ensure_ascii=False),flush=True)
# Native model-lab export, without changing other models or servo references.
if R.parent.name=='models' and (R.parent.parent/'lib'/'blender_utils.py').exists():
    sys.path.insert(0,str(R.parent.parent/'lib'))
    from blender_utils import export_stl
    export_stl(R.name,only=parts+ghost) # assembly preview only; print individual STLs
    # Repair float32 collinear triangulation in the preview without combining
    # separate moving solids. The native utility above remains the build entry.
    import struct
    preview_dir=R/'preview_components';preview_dir.mkdir(exist_ok=True)
    payload=[];count=0
    for i,o in enumerate(parts+ghost):
        fn=preview_dir/(str(i+1).zfill(2)+'_'+o.name.replace(' ','_')+'.stl')
        export(o,fn,normalize=False);data=fn.read_bytes()
        count+=struct.unpack_from('<I',data,80)[0];payload.append(data[84:])
    target=R.parent.parent/'exports'/(R.name+'.stl')
    target.write_bytes(b'ASSEMBLY PREVIEW ONLY | mm | use separate stl print parts'.ljust(80,b'\0')+struct.pack('<I',count)+b''.join(payload))
    print('Validated separate-solid preview saved:',count,'triangles',flush=True)
