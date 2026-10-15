"""Build cassette objects only. Millimetres, closed pose, no writes or scene reset."""
import ast
import math
from pathlib import Path
import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from printmech import geometry as G
from . import params as P, kinematics as K, gears
from .recipe import build_mount


def clone(ob,name):
    new=ob.copy()
    new.data=ob.data.copy()
    new.name=name
    bpy.context.collection.objects.link(new)
    return new


def reference(common):
    path=Path(common.ROOT)/'models/sg92r-photo/model.py'
    tree=ast.parse(path.read_text(encoding='utf-8'))
    ns=dict(vars(common.SG),bpy=bpy,bmesh=bmesh,math=math,Vector=Vector,EPS=.00002)
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(path),'exec'),ns)
    mat=Matrix(((0,0,1000,P.SERVO_BASE_U*1000),(1000,0,0,K.O[0]),(0,1000,0,K.O[1]),(0,0,0,1)))
    result={}
    for pid,fn in (('servo','build_body'),('horn','build_horn')):
        ob=ns[fn]()
        ob.data.transform(ob.matrix_world)
        ob.matrix_world=Matrix.Identity(4)
        ob.data.transform(mat)
        if pid=='horn': G.transform(ob,Matrix(K.rot_x(P.HORN_CLOSED_DEG,K.O)))
        G.clean(ob,dist=.001)
        result[pid]=ob
    return result


def profile(poly,center):
    return [(v+center[0],d+center[1]) for v,d in poly]


def horn_profile(sg,extra):
    left,right=sg.HORN_LEFT_X*1000,sg.HORN_RIGHT_X*1000
    hub=sg.HORN_HUB_DIA*500
    root,tip=sg.HORN_ROOT_W*500,sg.HORN_TIP_W*500
    return G.hull(G.circle((left+tip,0),tip+extra,48)+G.circle((right-tip,0),tip+extra,48)+
                  G.circle((-hub,0),root+extra,48)+G.circle((hub,0),root+extra,48))


def hood_radius(angle,inside=False):
    f=min(1.,max(0.,(angle-93)/5))
    a=P.SHIELD_INNER_RADIUS if inside else P.SHIELD_RADIUS
    b=P.SHIELD_TAIL_INNER_RADIUS if inside else P.SHIELD_TAIL_RADIUS
    return 1000*(a+(b-a)*f)


def hood_profile(inside=False):
    return [(0.,0.)]+[(hood_radius(a,inside)*math.cos(math.radians(a)),
                       hood_radius(a,inside)*math.sin(math.radians(a)))
                      for a in np.linspace(-8,125,135)]


def build(interface,common_params):
    sg=common_params.SG
    u0,u1=P.GEAR_U0*1000,P.GEAR_U1*1000
    hv,hd=K.H
    bore=P.BORE_RADIUS*1000
    panel,kl,kr=build_mount(interface)
    parts={'panel':panel,'key_l':kl,'key_r':kr,**reference(common_params)}

    # Asymmetric sleeve and its axial floor are behind the tooth plane.
    receiver=G.prism(profile(horn_profile(sg,1.5),K.O),'x',5.75,u0,'input_gear')
    half=sg.HORN_SHORT_W*500
    short=sg.HORN_SPAN_Y*500
    G.union(receiver,G.box(5.75,u0,-half-2.25,half+2.25,17.5-short-2.25,17.5+short+2.25))
    pocket_top=(P.SERVO_BASE_U+sg.HORN_TOP_Z+P.HORN_FIT)*1000
    fit=P.HORN_FIT*1000
    G.cut(receiver,G.prism(profile(horn_profile(sg,fit),K.O),'x',5.25,pocket_top),
          G.box(5.25,pocket_top,-half-fit,half+fit,17.5-short-fit,17.5+short+fit),
          G.cyl_x(K.O,sg.HORN_HUB_DIA*500+fit,5.25,pocket_top))
    # Leave the 18 mm tip open; the capped 16 mm end still rejects reversal.
    G.cut(receiver,G.box(5.25,u0+.5,-30,-15.5,-10,45))
    G.transform(receiver,Matrix(K.rot_x(P.HORN_CLOSED_DEG,K.O)))
    G.union(receiver,G.prism(profile(gears.outline(K.INPUT_PHASE_DEG),K.O),'x',u0,u1),
            G.cyl_x(K.O,2.5,u1-.5,15.75),G.cyl_x(K.O,3.8,15.75,17.25))
    parts['input_gear']=receiver

    sector=G.prism(profile(gears.outline(sector=True),K.H),'x',u0,u1,'sector_gear')
    hub=G.cyl_x(K.H,5.7,u0,u1)
    G.cut(hub,G.box(u0-1,u1+1,hv-7,hv+7,-5,1.45))
    G.union(sector,hub)
    G.cut(sector,G.cyl_x(K.H,bore,u0-1,u1+1))
    # Offset rectangular key; the two external bearing cheeks retain the group.
    cv=hv+P.COUPLING_V_OFFSET*1000
    G.union(sector,G.box(-2.25,u0+.5,cv-2,cv+2,2.75,5.75))
    parts['sector_gear']=sector

    # The specified blade stays 14 x 28 x 2. The opaque gear hood is an accessory.
    flag=G.box(P.FLAG_U0*1000,(P.FLAG_U0+P.FLAG_WIDTH)*1000,hv,hv+P.FLAG_LENGTH*1000,0,P.FLAG_THICKNESS*1000,'flag')
    for a,b in ((-11.75,-8),(-1.75,1.75)):
        lug=G.cyl_x(K.H,5.7,a,b)
        G.cut(lug,G.box(a-1,b+1,hv-7,hv+7,-5,0),G.cyl_x(K.H,bore,a-1,b+1))
        G.union(flag,lug)
    socket=G.box(-1.75,1.75,cv-4.7,cv+4.7,0,8.95)
    G.cut(socket,G.box(-2.25,2.25,cv-2.2,cv+2.2,2.55,5.95),
          G.box(-2.25,2.25,cv-.65,cv+.65,5.95,10))
    G.union(flag,socket)
    hood=G.prism(profile(hood_profile(),K.H),'x',6.75,14.75)
    inner=[(0.,0.)]+[(hood_radius(a,True)*math.cos(math.radians(a)),hood_radius(a,True)*math.sin(math.radians(a)))
                     for a in np.linspace(-10,127,139)]
    G.cut(hood,G.prism(profile(inner,K.H),'x',9,12.75),G.cyl_x(K.H,bore,6.25,15.25))
    for a,b in ((6.75,9),(12.5,14.75)):
        cheek=G.cyl_x(K.H,6.5,a,b)
        G.cut(cheek,G.box(a-1,b+1,hv-8,hv+8,-5,0),G.cyl_x(K.H,bore,a-1,b+1))
        G.union(hood,cheek)
    back=G.cyl_x(K.H,7.5,8.5,13)
    G.cut(back,G.cyl_x(K.H,5.95,8,13.5),G.box(8,13.5,hv-9,hv+9,-5,0),G.box(8,13.5,hv-4,hv+9,-1,12))
    G.union(hood,back,G.box(8.5,13,hv-6.5,hv+17.1,0,1.2))
    G.union(hood,G.box(.5,8.25,hv+15.4,hv+17,1.2,3.3))
    G.union(flag,hood)
    key_cover=G.box(-4.25,9,cv-3.5,cv+3.5,1,7.2)
    G.cut(key_cover,G.box(-2.5,9.5,cv-2.25,cv+2.25,2.5,6))
    G.union(flag,key_cover)
    G.cut(flag,G.cyl_x(K.H,bore,-13,15.25),G.box(6.5,9.25,cv-2.25,cv+2.25,2.5,6),
          G.box(-2.25,2.25,cv-2.2,cv+2.2,2.55,5.95))
    G.cut(flag,G.box(-2.5,9.25,cv-2.2,cv+2.2,2.55,5.95))
    # Meshing teeth must enter from inside the cassette. Cut their relative swept path
    # out of the moving hood. Axial cheeks remain the opaque sides of this labyrinth.
    gear_centers=[]
    receiver_points=[]
    rv=np.array([v.co[:] for v in receiver.data.vertices])
    for theta in np.linspace(0,60,31):
        relative=K.rot_x(theta,K.H)@K.rot_x(theta,K.O)
        vv=rv@relative[:3,:3].T+relative[:3,3]
        receiver_points.extend(vv[rv[:,0]<=u0+.01,1:3].tolist())
        center=K.H+np.array(((math.cos(math.radians(theta)),-math.sin(math.radians(theta))),
                            (math.sin(math.radians(theta)),math.cos(math.radians(theta)))))@(K.O-K.H)
        gear_centers.extend(G.circle(center,14.95,64))
    G.cut(flag,G.prism(G.hull(gear_centers),'x',u0-.25,u1+.25))
    receiver_sweep=G.hull([(v+dv,d+dd) for v,d in receiver_points for dv,dd in ((-.3,-.3),(-.3,.3),(.3,-.3),(.3,.3))])
    G.cut(flag,G.prism(receiver_sweep,'x',5.45,u0+.25))
    # The receiver's clearance is behind this opaque ceiling, never through its face.
    G.union(flag,G.box(1.75,8.8,hv+10.75,hv+16.9,0,1.2))
    cover=clone(flag,'flag_cover')
    G.intersect(cover,G.box(12.5,16,-40,10,-10,25))
    G.cut(flag,G.box(12.25,16,-40,10,-10,25))
    G.union(cover,G.box(10.75,13,hv,hv+3,9,12))
    G.cut(sector,G.box(9,13,hv-.2,hv+3.2,8.8,12.2))
    # Overlapping opaque roof at the axial split, with 0.25mm between its two levels.
    G.union(flag,G.box(11.9,13,hv-6.5,hv+16.9,0,1.2))
    G.cut(cover,G.box(12.25,13.25,hv-6.6,hv+17,-.5,1.45))
    G.union(cover,G.box(12.5,14.75,hv-6.5,hv+16.9,1.45,2.65))
    G.cut(cover,G.cyl_x(K.H,bore,12,15.25))
    G.cut(flag,G.cyl_x(K.H,bore,11.5,13.5))
    parts['flag_cover']=cover
    # Join the inner cheek to the flag at a radius clear of both gear teeth.
    parts['flag']=flag

    # The shaft is stationary. Open saddles close under the front cap.
    pin=G.cyl_x(K.H,P.PIN_RADIUS*1000,-15.25,18.25,name='hinge_pin')
    G.union(pin,G.cyl_x(K.H,2.6,-18.25,-15.25))
    groove=G.cut(G.cyl_x(K.H,2.5,-15.2,-11.8),G.cyl_x(K.H,P.PIN_NECK_RADIUS*1000,-15.4,-11.6))
    G.cut(pin,groove,G.box(-19,21,hv-4,hv+4,-1,P.PIN_FLAT_D*1000))
    G.cut(pin,G.box(-19,-15,hv-4,hv+4,-1,2.25))
    parts['hinge_pin']=pin

    # Ear slots use the 0.25 mm per-side physically successful allowance.
    base=P.SERVO_BASE_U*1000
    body_lo=(sg.BODY_CENTER_X-sg.BODY_L/2)*1000
    body_hi=(sg.BODY_CENTER_X+sg.BODY_L/2)*1000
    ear_lo=(sg.BODY_CENTER_X-sg.FLANGE_L/2)*1000
    ear_hi=(sg.BODY_CENTER_X+sg.FLANGE_L/2)*1000
    flange0=base+sg.FLANGE_BOTTOM_Z*1000
    flange1=flange0+sg.FLANGE_T*1000
    back=17.5+sg.BODY_W*500+.25
    support=G.box(-19.5,15.5,-19.5,14,back,back+3,'support')
    for a,b in ((ear_lo-3,body_lo-.25),(body_hi+.25,ear_hi+3)):
        rail=G.box(flange0-3,flange1+3,a,b,11.25,24.5)
        G.cut(rail,G.box(flange0-.25,flange1+.25,a-.5,b+.5,10,back))
        G.union(support,rail)
    G.union(support,G.box(-28,-25,ear_lo-3,ear_hi+3,3.25,16.5),
            G.box(-28,-11,ear_lo-3,ear_lo-.25,11.25,16.5),
            G.box(-28,18,-35.5,-32.5,3.25,8.5),
            G.box(-28,-25,-35.5,-21,8,11.25),
            G.box(12.5,15.5,-6,6,21.5,back+3))
    # Output saddles lie on both sides of the whole rotating flag/hood.
    for a,b in ((-15,-12),(15,18)):
        saddle=G.cyl_x(K.H,5.7,a,b)
        G.cut(saddle,G.cyl_x(K.H,bore,a-.5,b+.5),
              G.box(a-.5,b+.5,hv-7,hv+7,-5,3))
        G.union(support,saddle,G.box(a,b,-35.5,hv-3.5,3.25,9))
    saddle=G.cyl_x(K.O,5.7,12.5,15.5)
    G.cut(saddle,G.cyl_x(K.O,2.7,12,16),G.box(12,16,-7,7,0,17.5))
    G.union(support,saddle)
    # Keep the cradle's wide rail in front of the 24 mm depth step.
    G.cut(support,G.box(-40,40,-40,-19.75,23.7,40),G.box(-40,-19.75,-40,40,23.7,40))
    parts['support']=support

    cap=G.box(-12.25,4.5,hv-5,-10.5,9.25,11.25,'servo_cap')
    G.union(cap,G.box(-14.5,4.5,hv+6,-10.5,9.25,11.25),G.box(-14.5,4.5,-10.75,6,8.25,11.25))
    G.union(cap,G.box(-14.5,-12.5,hv+6,6,2.25,10),G.box(2.5,4.5,hv-5,6,2.25,10))
    G.cut(cap,G.cyl_x(K.H,11.8,2,5))
    bridge=G.box(-15,21,-32.25,-30.75,0,2.75,'bearing_bridge')
    # Independent upper bearing halves can be installed after both moving groups.
    for a,b in ((-15,-12),(15,18)):
        keeper=G.box(a,b,hv-5.7,hv+5.7,0,2.75)
        G.cut(keeper,G.cyl_x(K.H,bore,a-.5,b+.5))
        G.union(bridge,keeper,G.box(a,b,-32.25,hv-5,0,2.75))
    G.union(bridge,G.box(18.25,21,-30,7,2.25,11.8),G.box(14.5,21,4,7,8.25,13),
            G.box(12.5,15.5,-5.7,5.7,11.8,17.5),G.box(12.5,15.5,4,7,8.25,13))
    G.cut(bridge,G.cyl_x(K.O,2.7,12,16))
    collar=G.box(-15,-12,hv-3.3,hv+3.3,0,2.75)
    G.cut(collar,G.cyl_x(K.H,1.8,-15.2,-11.8))
    G.union(bridge,collar)
    # Panel traps these plain rear tabs; release the panel before lifting the bridge.
    G.union(bridge,G.box(-19,-14,-31,-28,2.25,5.25),G.box(20,23.25,-31,-28,2.25,5.25))
    G.cut(support,G.box(-19.25,-13.75,-31.25,-27.75,2,5.5))
    G.union(bridge,G.box(12.5,15.5,-5.4,8,2.25,4.25),G.box(12.5,15.5,5,8,2.25,13))
    parts['bearing_bridge']=bridge
    G.union(cap,G.box(-14.5,12.25,5,8,7.5,11))
    # Shallow front plate hides the entire input mesh; deep side wall tapers with envelope.
    G.union(cap,G.box(4,12.25,-7,8,2.25,4.25))
    G.cut(cap,G.cyl_x(K.O,15.05,4.5,12.5))
    parts['servo_cap']=cap

    # Plain aperture for blade and rotating hood. The backside remains opaque.
    G.cut(panel,G.box(-12.6,15.35,-31.25,hv+28.6,-1,3.5))
    G.union(panel,G.box(2.25,15.35,-5.4,6,0,2))
    G.cut(panel,G.box(-15.25,21.25,-32.5,-30.5,-.5,2.9))
    for a,b in ((-15,-12),(15,18)):
        G.cut(panel,G.box(a-.25,b+.25,-31.25,hv+5.95,-.5,2.5))
    # Two independently releasable support snaps outside the mechanism envelope.
    for u in (-26,26):
        G.union(support,G.box(u-2.5,u+2.5,-26,-23,3.25,5.25),
                G.box(min(u,-22),max(u,18)+.2,-35,-32,3.25,6.25),
                G.box(u-2.5,u+2.5,-34,-23,3.25,6.25),
                G.box(u-.8,u+.8,-25,-7,3.25,4.85),G.box(u-.8,u+.8,-10,-7,.5,4),
                G.box(u-1.4,u+1.4,-9.4,-7.6,.2,1.2))
        G.cut(panel,G.box(u-1,u+1,-10.2,-6.8,-.5,3.5),G.box(u-1.6,u+1.6,-9.6,-7.4,-.5,1.4))
    # Seats trap the cap once the panel is latched, without permanently deflecting it.
    # Real clearance volumes, not collision exclusions. These leave the successful ear slots.
    G.cut(support,G.box(base-.25,base+sg.BODY_H*1000+.25,body_lo-.25,body_hi+.25,11.25,23.75))
    G.cut(support,G.box(-40,40,-40,-31.75,10.74,40))
    G.cut(support,G.cyl_x(K.H,2.85,-32,-19))
    G.cut(support,G.box(8,13.5,-33.5,-31.5,3,9.5))
    G.union(support,G.box(7.5,14,-36.5,-33.5,3.25,8.5))
    input_sweep=[]
    horn_vertices=np.array([v.co[:] for v in parts['horn'].data.vertices])
    for theta in np.linspace(0,60,61):
        mat=K.rot_x(theta,K.O)
        vertices=rv@mat[:3,:3].T+mat[:3,3]
        input_sweep.extend(vertices[rv[:,0]<=u1+.01,1:3].tolist())
        input_sweep.extend((horn_vertices@mat[:3,:3].T+mat[:3,3])[:,1:3].tolist())
    input_sweep=G.hull([(v+dv,d+dd) for v,d in input_sweep for dv,dd in ((-.25,-.25),(-.25,.25),(.25,-.25),(.25,.25))])
    G.cut(support,G.prism(input_sweep,'x',5.5,u1+.25))
    G.cut(cap,G.prism(input_sweep,'x',5.5,u1+.25))
    G.cut(cap,G.box(2.25,15,-8.1,-5.2,1.9,4.6))
    G.cut(cap,G.cyl_x(K.H,6.0,-11.25,-7.75),G.cyl_x(K.H,6.0,-2,2))
    G.cut(cap,G.box(-15.25,-11.75,hv-6,hv+6,3,9.25),G.box(14.75,18.25,hv-6,hv+6,3,9.25))
    G.union(cap,G.box(2.25,6.5,-11.2,-5.4,3.55,5.55))

    # Open connector bay: rotate the interface's 14 x 8 x 18 mm box into u/v/d.
    # Its depth stays before the 17 mm envelope step. Place the connector from +d.
    bay_v,bay_d,bay_u=interface['wiring']['connector_bay_mm']
    cx,cy,cz=-12.,22.,12.5
    x0,x1=cx-bay_u/2,cx+bay_u/2
    y0,y1=cy-bay_v/2,cy+bay_v/2
    z0,z1=cz-bay_d/2,cz+bay_d/2
    t=1.5
    bay=G.cut(G.box(x0-t,x1+t,y0-t,y1+t,z0-t,z1),
              G.box(x0,x1,y0,y1,z0,z1+.5))
    G.union(support,bay)
    # Cable leaves the reference body in +v, at u=base+WIRE_EXIT_Z.
    wire_u=base+sg.WIRE_EXIT_Z*1000
    channel_width,channel_depth=interface['wiring']['open_channel_mm']
    wl,wr=wire_u-channel_depth/2,wire_u+channel_depth/2
    dl,dr=K.O[1]-channel_width/2,K.O[1]+channel_width/2
    start=body_hi+.25
    G.union(support,G.box(wl-t,wl,start,17,dl-t,dr+t),
            G.box(wl-t,wr,start,17,dl-t,dl),
            G.box(wl-t,wr,start,17,dr,dr+t))
    G.cut(support,G.box(wl,wr,start-.25,17.25,dl,dr))
    G.cut(support,G.box(x0,x1,y0,y1,z0,z1+.5))

    labels={'panel':'旗カセットの面板','key_l':'左の交換キー','key_r':'右の交換キー',
            'support':'サーボ座と両側軸受け','servo_cap':'固定の遮蔽壁とサーボ押さえ',
            'flag_cover':'旗の覆いの右側','bearing_bridge':'両軸の押さえ',
            'input_gear':'ホーン受け付き入力歯車','sector_gear':'120度の扇形歯車',
            'flag':'14×28mmの旗と歯車の覆い','hinge_pin':'抜け止め付き蝶番ピン',
            'servo':'SG92R','horn':'SG92R付属ホーン'}
    result={}
    for pid,ob in parts.items():
        G.clean(ob,dist=.003 if pid=='flag' else .001)
        bm=bmesh.new(); bm.from_mesh(ob.data)
        wire=[e for e in bm.edges if e.is_wire]
        if wire: bmesh.ops.delete(bm,geom=wire,context='EDGES')
        loose=[v for v in bm.verts if not v.link_edges]
        if loose: bmesh.ops.delete(bm,geom=loose,context='VERTS')
        boundary=[e for e in bm.edges if e.is_boundary]
        if boundary and len(boundary)<=6:
            coordinates=np.array([v.co[:] for e in boundary for v in e.verts])
            if np.linalg.norm(np.ptp(coordinates,axis=0))<.25:
                bmesh.ops.holes_fill(bm,edges=boundary,sides=6)
                bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
                bm.to_mesh(ob.data)
        bm.to_mesh(ob.data)
        bm.free()
        ob.name=pid
        rotation=np.eye(4)
        if pid=='input_gear': rotation=np.asarray(Matrix.Rotation(-math.pi/2,4,'Y'))
        if pid in ('sector_gear','flag_cover'): rotation=np.asarray(Matrix.Rotation(math.pi/2,4,'Y'))
        if pid=='support': rotation=np.asarray(Matrix.Rotation(math.pi,4,'X'))
        result[pid]={'object':ob,'print_rotation':rotation,'label':labels[pid],
                     'color':'#7598b3' if pid=='servo' else '#444844' if pid=='horn' else '#deddd5',
                     'purchased':pid in ('servo','horn')}
    return result
