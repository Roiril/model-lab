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
F=q('FIT');C=q('RUNNING');PR=q('ROOF_PEG_R');CP=q('COVER_PEG_R');RF=q('RECEIVER_FIT');RS=q('ROOF_SLOT_FIT')
SPACERS=[(q('SPACER_FRONT_Y'),q('SPACER_FRONT_Z')),(q('SPACER_REAR_Y'),q('SPACER_REAR_Z'))]
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
    bm=bmesh.new();bm.from_mesh(o.data);vol=abs(bm.calc_volume());bm.free();assert vol>1e-12,(o.name,'zero-volume CAD')
    parts.append(o);groups[o.name]=g
    T=Matrix.Rotation((1 if reverse else -1)*math.pi/2,4,'Y') if axis=='X' else Matrix.Rotation(math.pi/2,4,'X') if axis=='Y' else Matrix.Rotation(math.pi,4,'Y') if axis=='-Z' else Matrix.Identity(4)
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
# A locally thick bottom leaves a roof over the cable channel.
add(body,cube('cable floor raised pad',(34,60,0),(49,70,6.5)))
clip(body,'connector through entry',(35,60.5,-.5),(47,69.0,7))
clip(body,'continuous underside cable channel',(37.5,63,-.5),(44.5,70.5,3.3))
# Smooth printed wire guides; no tie, clamp force or required extra part.
for x in (33.,49.):
    add(body,cyl('smooth wire guide',(x,55.,5.75),4.,6.9,'Z'))
for xa,xb in ((0,W),(S-W,S)):
    add(body,cube('closed lid seat',(xa,S-4,q('BODY_TOP')-.1),(xb,S,roof)))
# Four positive drop-in receivers; no thin snap hooks. Crossmembers pass below.
for x0,x1 in ((4.,8.7),(q('FRONT_PLATE_X'),q('FRONT_PLATE_X')+q('FRONT_PLATE_T'))):
    for yy in (5.4,60.4):
        upper=52.0 if yy>30 else 48.0
        socket=cube('vertical receiver',(x0-2.7,yy-2.4,W-.1),(x1+2.7,yy+5.6,upper))
        clip(socket,'receiver open slot',(x0-RF,0,18),(x1+RF,70,upper+.5))
        if yy>30:
            ramp=prism('key rear ramp',x0-2.7,x1+2.7,[(56.4,44),(60.4,40),(60.4,52),(56.4,52)])
            add(socket,ramp)
            clip(socket,'receiver repeated clearance',(x0-RF,0,22.3),(x1+RF,70,upper+.5))
        add(body,socket)
        if x0>50:
            # Full-height bridge shortens outward stop-rail bending path.
            add(body,cube('receiver to outer wall bridge',(x1+RF,yy-2.4,W-.1),(70,yy+5.6,upper)))
# Only the inward receiver rail has a crossmember access window. The
# outward locating rail stays joined over full height to the outer wall.
for yy,zz in SPACERS:
    for xa,xb in [(8.85,11.6),(53.,56.)]:
        clip(body,'crossmember receiver inward relief',(xa,yy-.4,zz-.4),(xb,yy+6.,80.))
# The local rear support root passes this narrow ramp relief during drop.
# Bearing loads have a short path to the floor after assembly. These broad
# pads leave0.10mm nominal clearance, requiring gentle physical seating.
add(body,cube('front bearing load pad',(46.,13.,W-.1),(55.,20.,17.9)))
add(body,cube('rear bearing load pad',(46.,48.8,W-.1),(55.,56.2,13.9)))
# A single bottom quarter-turn crossbar captures both rigid cassette feet.
# All assembled print parts lie inside the70mm cube. Head is recessed0.2mm.
# Rigid shoulders carry vertical load; no spring or flexing hook is used.
KX=q('BOTTOM_KEY_X');KY=q('BOTTOM_KEY_Y');KW=q('BOTTOM_KEY_HALF_WIDTH');KFKEY=q('BOTTOM_KEY_FIT')
add(body,cyl('broad bottom key bearing boss',(KX,KY,3.3),14.,6.6,'Z'))
# Circular sweep envelope with two broad diagonal stop faces. Rectangle
#22x10.4 reaches11.455mm along the stop normals at each end pose.
poly=[(12.85*math.cos(i*math.tau/96),12.85*math.sin(i*math.tau/96)) for i in range(96)]
for nx,ny in [(-2**-.5,2**-.5),(2**-.5,-2**-.5)]:
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        va=a[0]*nx+a[1]*ny-11.75;vb=b[0]*nx+b[1]*ny-11.75
        if va<=0:out.append(a)
        if (va<=0)!=(vb<=0):
            t=va/(va-vb);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
    poly=out
poly=[(KX+x,KY+y) for x,y in poly]
cut(body,prism_z('quarter turn head recess',-.2,3.2,poly))
cut(body,cyl('key stem rotation clearance',(KX,KY,5.0),6.9,4.0,'Z'))
clip(body,'vertical crossbar insertion slot',(KX-KW-KFKEY,KY-q('BOTTOM_KEY_NEG_ARM')-KFKEY,-.2),(KX+KW+KFKEY,KY+q('BOTTOM_KEY_POS_ARM')+KFKEY,8.))

part(body,axis='Z',mat=shell)

cover=cube('02_fixed_rear_cover',(0,0,roof),(S,q('FIXED_BAND_END'),S))
cut(cover,prism('inner rear-band edge bevel',-.1,S+.1,[(24.8,67.5),(26.9,67.5),(26.9,68.6)]))
# Two axial sockets captured between opposite integral locating pegs.
for x0,x1 in ((9.,14.4),(50.5,55.8)):
    add(cover,cube('cover socket',(x0,4.,58.5),(x1,12.,roof+.1)))
    cut(cover,diamond('cover locating through',x0-.4,x1+.4,8.,64.,CP+F))
part(cover,axis='-Z',mat=shell)

lid=prism('03_planar_lid',0,S,[(q('LID_REAR_TOP'),S),(S,S),(S,roof),(q('LID_REAR_INNER'),roof)])
# Open forks slide into a simple roof dock, retained by the front rocker's peg.
shoe=cube('roof fork dock',(41.,31.5,57.6),(55.9,51.7,roof+.1))
for xx in (back,front):
    clip(shoe,'open fork slot',(xx-RS,26.,57.3),(xx+rt+(.4 if xx==front else RS),49.3,67.3))
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
# Former 47mm upright columns are separate flat-print beams.
KF=q('KEEPER_FIT');SF=q('SPACER_FIT')
for yy,zz in SPACERS:
    clip(cass,'spacer rear socket',(5.6,yy-SF,zz-SF),(9.2,yy+5.6+SF,zz+5.6+SF))
# A short local loop captures the cup before body receiver play can accumulate.
add(cass,cube('local capture outer longitudinal rib',(8.6,13.,18.),(54.6,19.8,24.1)))
LF=q('LOCAL_LIP_FIT');LC=q('LOCAL_CAPTURE_FACE_X')
clip(cass,'local lip vertical mortise',(LC+.5-LF,14.3,19.),(55.,18.5,24.9))
add(cass,cube('second rail root',(4.,49.,14.),(8.8,55.8,18.1)))
add(cass,cube('second local capture rail',(8.6,49.,14.),(54.6,55.8,18.)))
clip(cass,'second local lip mortise',(LC+.5-LF,50.3,14.9),(55.,54.5,18.7))
for yy,z0,z1 in [(13.,19.,24.9),(49.,14.9,18.7)]:
    clip(cass,'local stop bar vertical socket',(49.65,yy,z0),(53.10,yy+6.8,z1))
# Strong hinge boss grows from an axial rib through a 45 degree clipped ramp.
add(cass,cube('hinge axial rib',(8.6,15.,56.3),(28.1,18.4,67.3)))
hb=cyl('rear hinge ramp',(35.875,HY,HZ),5.5,15.75)
clip(hb,'ramp bounding half-space',(0,27.6,0),(37.1,80,90))
# Diagonal cut is independent of z: y <= 18.4+(x-28), until full boss.
cut(hb,prism_z('hinge ramp diagonal',0,90,[(27.9,18.3),(37.2,27.6),(37.2,80),(27.9,80)]))
add(cass,hb)
bore(cass,'rear hinge blind',40.0,43.9,HY,HZ,3.3)
# U-shaped rear thrust saddle. Its front thrust face is printed up; only its
# nonfunctional rear overhang may receive sparse removable support.
saddle=cyl('rear thrust saddle',(34.15,OY,OZ),12.4,5.7)
bore(saddle,'gear keepout',30.9,37.4,OY,OZ,9.2)
clip(saddle,'open upper thrust saddle',(30,0,OZ),(40,80,80))
add(cass,saddle)
# Temporary support columns land on this recessed nonfunctional surface,
# 2.3 mm behind the servo's case datum, not on its axial locating face.
clip(cass,'recessed support landing',(6.7,OY-15.5,27.),(9.,OY+15.5,41.))
add(cass,cube('local rear case upper stop',(8.6,29.,41.),(8.8,44.,43.3)))
# Cover peg and top-keeper end pocket are integral, not tiny snaps.
add(cass,diamond('rear cover integral peg',8.6,14.1,8.,64.,CP))
clip(cass,'top keeper end pocket',(5.6,23.2-KF,43.6-KF),(9.2,29.+KF,47.6+KF))
add(cass,cube('bottom rear retention foot',(4.,KY-3.,3.0),(22.,KY+3.,9.0)))
add(cass,cube('bottom rear foot root',(4.,KY-3.,8.9),(8.7,KY+3.,18.1)))
cut(cass,diamond('rear service lift hole',3.5,9.2,61.5,59.5,2.5))
part(cass,mat=frame)

closure=cube('05_front_closure',(56.1,5.4,18.),(56.1+q('FRONT_PLATE_T'),67.,67.3))
add(closure,cyl('front hinge axial shoulder',(56.025,HY,HZ),5.5,.35))
bore(closure,'front hinge blind',55.7,59.2,HY,HZ,3.3)
tower=cyl('front journal tower',(51.8,OY,OZ),8.0,10.8)
clip(tower,'lower local capture split clearance',(46,0,0),(50.1,80,OZ+.3))
add(closure,tower)
bore(closure,'journal blind bore',46.,59.2,OY,OZ,6.3)
clip(closure,'keeper front socket',(55.7,23.2-KF,43.6-KF),(58.9,29.+KF,47.6+KF))
for yy,zz in SPACERS:
    clip(closure,'spacer front socket',(55.7,yy-SF,zz-SF),(58.9,yy+5.6+SF,zz+5.6+SF))
add(closure,cube('capture stop bar upper retaining shelf',(50.,13.,24.8),(56.2,55.8,27.2)))
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
cut(closure,prism('A tail blind arc',55.7,59.2,track))
add(closure,cube('bottom front retention foot',(51.,KY-3.,3.0),(61.3,KY+3.,9.0)))
add(closure,cube('bottom front foot root',(56.1,KY-3.,8.9),(61.3,KY+3.,18.1)))
cut(closure,diamond('front service lift hole',55.7,61.7,61.5,59.5,2.5))
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
pad_end=q('CUP_SUPPORT_PAD_END_X');pad_r=q('CUP_SUPPORT_PAD_R')
pad=prism('outer nonmating support pad',cx1-.1,pad_end,arm_outline(3.3))
add(pad,capsule('pad short outer',cx1-.1,pad_end,aa,bb,hd('HORN_SHORT_W')/2+3.3))
add(pad,cyl('pad centre',((cx1-.1+pad_end)/2,OY,OZ),12.1,pad_end-cx1+.1))
add(pad,cyl('pad A boss',((cx1-.1+pad_end)/2,OY+r,OZ),5.5,pad_end-cx1+.1))
bore(pad,'pad annular exclusion',cx1-.5,pad_end+.5,OY,OZ,pad_r)
add(cup,pad)
cut(cup,prism('actual long horn pocket',cx0-.5,ce,arm_outline(F)))
cut(cup,capsule('actual short horn pocket',cx0-.5,ce,aa,bb,hd('HORN_SHORT_W')/2+F))
bore(cup,'hub rear clearance',cx0-.5,ce,OY,OZ,9.1)
add(cup,cyl('integral thick journal',((cx1-.1+q('JOURNAL_END_X'))/2,OY,OZ),q('JOURNAL_D')/2,q('JOURNAL_END_X')-cx1+.1))
bore(cup,'A blind bearing',43.1,pad_end+.4,OY+r,OZ,2.8)
part(cup,'crank',reverse=True,mat=moving)

for k,xx in enumerate((back,front)):
    elbow=H+Vector((14.,-10.))
    rock=capsule('07_rear_rocker' if k==0 else '08_front_rocker',xx,xx+rt,H,elbow,q('ROCKER_LEG_R'))
    add(rock,capsule('rocker elbow',xx,xx+rt,elbow,B0,q('ROCKER_LEG_R')))
    add(rock,cyl('hinge eye',((xx+xx+rt)/2,HY,HZ),5.5,rt))
    add(rock,cyl('B eye',((xx+xx+rt)/2,*B0),5.,rt))
    add(rock,cube('broad roof tenon',(xx,33.3,57.9),(xx+rt,49.,67.)))
    bore(rock,'hinge through',xx-.4,xx+rt+.4,HY,HZ,3.3)
    xa,xb=(xx+1.0,xx+rt+.4) if k==0 else (xx-.4,xx+rt-1.0)
    bore(rock,'B blind bearing',xa,xb,*B0,2.8)
    if k==0:cut(rock,diamond('roof locating through',xx-.4,xx+rt+.4,q('ROOF_PEG_Y'),q('ROOF_PEG_Z'),PR+F))
    else:add(rock,diamond('integral roof peg',41.2,xx+.1,q('ROOF_PEG_Y'),q('ROOF_PEG_Z'),PR))
    part(rock,'lid',reverse=k==1,mat=moving)

v=(B0-A0).normalized();mid=(A0+B0)/2+Vector((v.y,-v.x))*4.4;e1=(mid-A0).normalized();e2=(B0-mid).normalized();n1=Vector((-e1.y,e1.x));n2=Vector((-e2.y,e2.x));mit=(n1+n2)*q('LINK_WEB_HALF')/(1+n1.dot(n2));eye=q('LINK_EYE_R');s=math.sqrt(eye*eye-q('LINK_WEB_HALF')**2);aoff=math.atan2(q('LINK_WEB_HALF'),s)
outline=[tuple(A0+e1*s+n1*q('LINK_WEB_HALF')),tuple(mid+mit),tuple(B0-e2*s+n2*q('LINK_WEB_HALF'))];ang=math.atan2(e2.y,e2.x)
for i in range(1,65):a=ang+math.pi-aoff-(2*math.pi-2*aoff)*i/64;outline.append(tuple(B0+Vector((math.cos(a),math.sin(a)))*eye))
outline.extend([tuple(mid-mit),tuple(A0+e1*s-n1*q('LINK_WEB_HALF'))]);ang=math.atan2(e1.y,e1.x)
for i in range(1,64):a=ang-aoff-(2*math.pi-2*aoff)*i/64;outline.append(tuple(A0+Vector((math.cos(a),math.sin(a)))*eye))
link=prism('09_link',lx,lx+lt,outline)
for yy,zz in (A0,B0):bore(link,'link bearing',lx-.4,lx+lt+.4,yy,zz,2.8)
part(link,'link',mat=linkmat)

def axle(n,x0,x1,y,z,d,g):
    a=cyl(n,((x0+x1)/2,y,z),d/2,x1-x0);h=d/2/math.sqrt(2)
    clip(a,'lower shaft flat',(x0-.1,y-d,z-d),(x1+.1,y+d,z-h))
    clip(a,'upper shaft flat',(x0-.1,y-d,z+h),(x1+.1,y+d,z+d))
    return part(a,g,axis='Z',mat=pins)
axle('10_hinge_axle',40.15,59.05,HY,HZ,q('HINGE_PIN_D'),'fixed')
axle('11_drive_axle',43.25,59.05,OY+r,OZ,q('DRIVE_PIN_D'),'crank')
axle('12_link_axle',back+1.15,front+rt-1.15,*B0,q('DRIVE_PIN_D'),'lid')
# Locked orientation: crossbar extends alongX; bottom tool slot alongX.
# Insert from below at90deg, then turn to0deg. Reverse for disassembly.
# The quarter-turn stop does not automatically resist reverse rotation.
key=cube('13_body_cross_key',(KX-q('BOTTOM_KEY_HEAD_HALF_X'),KY-KW,q('BOTTOM_KEY_HEAD_Z')),(KX+q('BOTTOM_KEY_HEAD_HALF_X'),KY+KW,q('BOTTOM_KEY_HEAD_Z')+q('BOTTOM_KEY_HEAD_T')))
add(key,cube('broad rectangular bottom key stem',(KX-4.,KY-KW,2.9),(KX+4.,KY+KW,14.0)))
add(key,cube('thick bottom capture crossbar',(KX-q('BOTTOM_KEY_NEG_ARM'),KY-KW,q('BOTTOM_KEY_BAR_Z')),(KX+q('BOTTOM_KEY_POS_ARM'),KY+KW,q('BOTTOM_KEY_BAR_Z')+q('BOTTOM_KEY_BAR_T'))))
hub=cyl('central crossbar stiffening hub',(KX,KY,12.6),6.5,6.8,'Z')
clip(hub,'hub common bed flat',(0,0,0),(70,KY-KW,80))
add(key,hub)
clip(key,'bottom screwdriver slot',(KX-7.,KY-1.0,-.1),(KX+7.,KY+1.0,1.35))
part(key,axis='Y',mat=pins)
# Actual-length flat-print keeper and crossmembers, captured by both plates.
keeper=cube('14_servo_top_keeper',(5.9,23.2,43.6),(58.6,29.,47.6))
add(keeper,cube('local servo axial tab',(31.3,23.2,42.),(34.3,29.,43.7)))
# Chamfer the four long end edges using a general mesh bevel, only edges
# at either insertion end. The main 4mm section remains full thickness.
def end_chamfer(o,ends):
    bm=bmesh.new();bm.from_mesh(o.data)
    edges=[e for e in bm.edges if all(any(abs((o.matrix_world@v.co).x*1000-x)<.01 for x in ends) for v in e.verts)]
    bmesh.ops.bevel(bm,geom=edges,offset=.00045,segments=1,affect='EDGES');bm.to_mesh(o.data);bm.free();clean(o)
end_chamfer(keeper,[5.9,58.6]);part(keeper,axis='-Z',mat=frame)
for num,(yy,zz) in enumerate(SPACERS,15):
    beam=cube(f'{num}_flat_spacer',(5.9,yy,zz),(58.6,yy+5.6,zz+5.6))
    end_chamfer(beam,[5.9,58.6]);part(beam,axis='Z',mat=frame)
lip=cyl('17_local_cup_capture',(LC+1.75,OY,OZ),q('LOCAL_CAPTURE_OUTER_R'),3.5)
bore(lip,'local journal running bore',46.,50.,OY,OZ,6.3)
clip(lip,'upper half open',(46.,0,OZ+.01),(50.,80,80))
add(lip,cube('local capture central deep web',(LC+.5,20.1,18.3),(LC+3.5,50.,28.8)))
add(lip,cube('front capture stepped web',(LC+.5,14.,24.4),(LC+3.5,20.2,28.8)))
add(lip,cube('rear capture stepped web',(LC+.5,49.9,18.3),(LC+3.5,55.8,28.8)))
add(lip,cube('front capture mortise tongue',(LC+.5,14.6,19.3),(LC+3.5,18.2,24.5)))
add(lip,cube('rear capture mortise tongue',(LC+.5,50.6,15.2),(LC+3.5,54.2,18.4)))
part(lip,axis='X',reverse=True,mat=frame)

for number,yy,z0 in [(18,13.2,19.3),(19,49.2,15.2)]:
    stop=cube(f'{number}_local_capture_stop',(49.80,yy,z0),(53.,yy+6.4,24.5))
    part(stop,axis='X',reverse=True,mat=frame)

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
record=dict(revision=3,center_screw_required=False,size_mm=S,overall_closed_with_key_width_mm=70.,wall_mm=W,lid_skin_mm=q('LID_SKIN'),O=list(O),H=list(H),crank_r_mm=r,rocker_local_mm=list(uv),link_length_mm=L,lid_range_deg=[0,p.OPEN_DEG],servo_range_deg=[math.degrees(pose(0)[0]),math.degrees(pose(p.OPEN_DEG)[0])],parts=manifest,reference_source=str(ref),physical_tested=False,boolean_solver_fallbacks=SOLVER_FALLBACKS,notes=['19 print parts; no required spring, tie, center screw or metal hinge/link pins. Servo, stock horn, power/wiring and optional speaker are separate.','Revision3 parts only. Do not mix v1/revision2 STLs.','Fixed cover and roof locating pegs are integral; front closure and body receivers capture them','Marked support facets are candidates only; sliced contacts and removal paths must be checked','Cup axial capture uses local plate17 and positive stops18/19 on the same cassette as the rear servo stop; closure retains the stops vertically; actual teeth are unmeasured','Body floor pads support bearing loads after complete assembly. Support the rails gently on the bench','Hinge carries radial weight; servo supplies gravity torque; unpowered lid can close'])
record['overall_closed_with_key_depth_mm']=70.0
record['notes'].append('Bottom crossbar13 captures rigid feet on04/05. Head is inside70mm exterior. It rotates manually between two stops; reverse rotation is not automatically locked. Check slot orientation before use; vibration/transport retention is untested. Smooth cable guides do not prove tensile strain relief.')
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
