"""An opaque flag well separated from the deeper gear chamber."""
import math
import numpy as np
import bpy,bmesh
from mathutils import Matrix
from printmech import geometry as G
from . import params as P,kinematics as K,gears
from .recipe import build_mount

def sector_outline(centers,start,end):
    r=P.ROOT_RADIUS*1000
    points=[(0,0),(r*math.cos(math.radians(start)),r*math.sin(math.radians(start)))]
    for c in centers:
        tooth=gears.tooth(c)
        a0=math.degrees(math.atan2(points[-1][1],points[-1][0]))
        a1=math.degrees(math.atan2(tooth[0][1],tooth[0][0]))
        while a1<a0: a1+=360
        points.extend((r*math.cos(math.radians(a)),r*math.sin(math.radians(a))) for a in np.linspace(a0,a1,8)[1:-1])
        points.extend(tooth)
    a0=math.degrees(math.atan2(points[-1][1],points[-1][0]))
    while end<a0: end+=360
    points.extend((r*math.cos(math.radians(a)),r*math.sin(math.radians(a))) for a in np.linspace(a0,end,12)[1:])
    return points

def expanded(poly,gap):
    poly=G.hull([(v+dv,d+dd) for v,d in poly for dv,dd in ((-gap,-gap),(-gap,gap),(gap,-gap),(gap,gap))])
    for _ in range(10):
        keep=[]
        for i,b in enumerate(poly):
            a=np.array(poly[i-1]); b=np.array(b); c=np.array(poly[(i+1)%len(poly)])
            distance=abs(float(np.cross(c-a,b-a)))/max(np.linalg.norm(c-a),1e-8)
            if distance>.005 or i%2: keep.append(tuple(b))
        if len(keep)==len(poly): break
        poly=keep
    return poly

def build(interface,common):
    from .geometry import reference,horn_profile,profile,clone
    sg=common.SG; hv,hd=K.H; ov,od=K.O
    u0,u1=P.GEAR_U0*1000,P.GEAR_U1*1000; bore=P.BORE_RADIUS*1000
    panel,kl,kr=build_mount(interface)
    parts={'panel':panel,'key_l':kl,'key_r':kr,**reference(common)}
    receiver=G.prism(profile(horn_profile(sg,1.5),K.O),'x',5.75,u0,'input_gear')
    half=sg.HORN_SHORT_W*500; short=sg.HORN_SPAN_Y*500
    G.union(receiver,G.box(5.75,u0,ov-half-2.25,ov+half+2.25,od-short-2.25,od+short+2.25))
    top=(P.SERVO_BASE_U+sg.HORN_TOP_Z+P.HORN_FIT)*1000; fit=.25
    G.cut(receiver,G.prism(profile(horn_profile(sg,fit),K.O),'x',5.25,top),
          G.box(5.25,top,ov-half-fit,ov+half+fit,od-short-fit,od+short+fit),
          G.cyl_x(K.O,sg.HORN_HUB_DIA*500+fit,5.25,top),
          G.box(5.25,u0+.5,ov-30,ov-13,od-30,od+30))
    G.transform(receiver,Matrix(K.rot_x(P.HORN_CLOSED_DEG,K.O)))
    teeth=[K.INPUT_PHASE_DEG+a for a in P.INPUT_TOOTH_OFFSETS_DEG]
    inp=G.prism(profile(sector_outline(teeth,P.INPUT_START_DEG,P.INPUT_END_DEG),K.O),'x',u0,u1)
    G.union(receiver,inp,G.cyl_x(K.O,4.9,u0,u1),G.cyl_x(K.O,2.5,u1-.5,15.75),G.cyl_x(K.O,3.8,15.75,17.25))
    parts['input_gear']=receiver
    sector=G.prism(profile(sector_outline(P.SECTOR_TEETH_DEG,P.SECTOR_START_DEG,P.SECTOR_END_DEG),K.H),'x',u0,u1,'sector_gear')
    flange=[(0,0)]+G.circle((0,0),P.SHIELD_FLANGE_RADIUS*1000,80,-85,85,closed=False)
    flag_flange=[(0,0)]+G.circle((0,0),P.SHIELD_FLANGE_RADIUS*1000,100,-110,110,closed=False)
    G.union(sector,G.cyl_x(K.H,4.9,3.5,u1),G.prism(profile(flange,K.H),'x',3.5,5.75))
    key=G.cyl_x(K.H,3.5,-1.75,9.75)
    G.cut(key,G.box(-3,10,hv-5,hv-2.3,hd-5,hd+5))
    G.union(sector,key)
    G.union(sector,G.box(-1.75,9.75,hv+4,hv+7,hd-1.5,hd+1.5))
    G.cut(sector,G.cyl_x(K.H,bore,-3,u1+.5))
    parts['sector_gear']=sector
    flag=G.box(P.FLAG_U0*1000,(P.FLAG_U0+P.FLAG_WIDTH)*1000,hv,hv+P.FLAG_LENGTH*1000,0,P.FLAG_THICKNESS*1000,'flag')
    G.union(flag,G.box(-12.,-9.,hv,hv+3,1,hd),G.box(-2.25,.75,hv,hv+3,1,hd),
            G.cyl_x(K.H,3.2,-13.,1.75),G.cyl_x(K.H,4.9,-13.75,-9.75),G.cyl_x(K.H,4.9,-3.5,1.75),
            G.prism(profile(flag_flange,K.H),'x',-3.5,1.75))
    G.cut(flag,G.cyl_x(K.H,bore,-14.25,2.25))
    socket=G.cyl_x(K.H,3.7,-2.,2.25)
    G.cut(socket,G.box(-3,2,hv-5,hv-2.5,hd-5,hd+5))
    G.cut(flag,socket)
    G.cut(flag,G.box(-2.,2.25,hv+3.8,hv+7.2,hd-1.7,hd+1.7))
    parts['flag']=flag
    cover=G.cyl_x(K.H,4.9,12.5,14.75,name='flag_cover')
    G.union(cover,G.box(10.5,13,hv+2.6,hv+5.6,hd-1.5,hd+1.5))
    G.cut(cover,G.cyl_x(K.H,bore,10,15))
    G.cut(sector,G.box(10.25,12.75,hv+2.4,hv+5.8,hd-1.7,hd+1.7))
    parts['flag_cover']=cover
    pin=G.cyl_x(K.H,P.PIN_RADIUS*1000,-17.25,18.25,name='hinge_pin')
    G.union(pin,G.cyl_x(K.H,2.5,-20.25,-17.25))
    groove=G.cut(G.cyl_x(K.H,2,-17.2,-13.75),G.cyl_x(K.H,P.PIN_NECK_RADIUS*1000,-17.4,-13.55))
    G.cut(pin,groove)
    parts['hinge_pin']=pin
    # A rear tray follows the seven-step envelope. All cuts open toward the face.
    support=G.box(-30,24,-36.5,30,3.25,10.65,'support')
    for half,z0,z1 in ((31.65,10.6,16.65),(24.65,16.6,23.65),(19.65,23.6,28.65),(14.65,28.6,33.65)):
        G.union(support,G.box(max(-30,-half),min(24,half),max(-36.5,-half),min(30,half),z0,z1))
    def front_void(poly,ua,ub):
        ext=G.hull(list(poly)+[(v,d-60) for v,d in poly])
        G.cut(support,G.prism(ext,'x',ua,ub))
    # Purchased body and ears insert from the front; the raised rear seat is 3 mm.
    base=P.SERVO_BASE_U*1000
    bl=ov+(sg.BODY_CENTER_X-sg.BODY_L/2)*1000
    bh=ov+(sg.BODY_CENTER_X+sg.BODY_L/2)*1000
    el=ov+(sg.BODY_CENTER_X-sg.FLANGE_L/2)*1000
    eh=ov+(sg.BODY_CENTER_X+sg.FLANGE_L/2)*1000
    G.cut(support,G.box(base-.25,base+22.25,bl-.25,bh+.25,-40,od+6.25),
          G.box(base+15.75,base+18.25,el-.25,eh+.25,-40,od+6.25),
          G.cyl_x(K.O,6.3,-3,5.5))
    front_void(G.circle(K.O,9.),-2.75,2.75)
    ip=[]; op=[]; fp=[]
    for theta in np.linspace(0,60,121):
        for pid,points,pivot,sign in (('input_gear',ip,K.O,1),('horn',ip,K.O,1),('sector_gear',op,K.H,-1),('flag',fp,K.H,-1),('flag_cover',op,K.H,-1)):
            ob=parts[pid]; vv=np.array([v.co[:] for v in ob.data.vertices]); mat=K.rot_x(sign*theta,pivot)
            if pid=='input_gear': vv=vv[vv[:,0]<=u1+.01]
            points.extend((vv@mat[:3,:3].T+mat[:3,3])[:,1:].tolist())
    ip,op,fp=expanded(G.hull(ip),.3),expanded(G.hull(op),.3),expanded(G.hull(fp),.3)
    # Output group first approaches 2.8mm away from the input axis, then meshes.
    op=G.hull(op+[(v-2.8,d-.052) for v,d in op])
    fp=G.hull(fp+[(v-2.8,d-.052) for v,d in fp])
    front_void(ip,2.75,12.5)
    front_void(op,3.25,15.25)
    front_void(fp,-14.,2.)
    # Actual receiver volumes, conservatively enclosed by boxes with 0.40mm gap.
    for row in interface['mount_geometry']['frame_receivers']:
        c=np.array(row['center_mm'])
        size=np.array(row.get('size_mm',[row.get('radius_mm',0)*2]*2+[row.get('depth_mm',0)]))
        lo,hi=c-size/2-.4,c+size/2+.4
        G.cut(support,G.box(lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]))
    # Coaxial passage, overlapped by the flag's left and sector's right collars.
    passage=[(0,0)]+G.circle((0,0),7.8,64,-85,25,closed=False)
    G.cut(support,G.cyl_x(K.H,3.9,1.25,3.5),G.prism(profile(passage,K.H),'x',1.25,3.5))
    front_void(G.hull(G.circle(K.H,3.9)+G.circle(K.H-np.array((2.8,.052)),3.9)),1.25,3.5)
    # Open bearing saddles; their separate front halves are trapped by the panel.
    for a,b in ((-17.,-13.25),(15,18)):
        G.cut(support,G.cyl_x(K.H,bore,a-.1,b+.1),G.box(a,b,hv-5.2,hv+5.2,-40,hd))
    G.cut(support,G.cyl_x(K.H,2.75,-32,-17.25),G.cyl_x(K.O,2.7,12.5,15.5),
          G.box(12.5,15.5,ov-5.95,ov+5.95,-40,od),G.box(15.5,18,ov-4.1,ov+4.1,-40,od+4.1))
    # Shallow cap retains the servo by its front face while leaving the flag well free.
    cap=G.box(-24.5,-12.5,bl-.2,bh+.2,od-9.25,od-6.25,'servo_cap')
    G.union(cap,G.box(-27,-24.5,-6.5,bh+.2,2.25,od-6.25))
    G.union(cap,G.box(-14.75,2.75,hv+9.,hv+29.2,od-9.25,od-6.25),
            G.box(-14.75,-3.75,hv+5.4,hv+29.2,od-9.25,od-6.25))
    G.union(cap,G.box(-9.5,-3.75,hv+3.7,hv+6,od-9.25,od-6.25))
    G.union(cap,G.box(-13.5,-9.5,hv+5.2,hv+6.4,od-9.25,20.6),
            G.box(-9.5,-3.75,hv+3.7,hv+4.9,od-9.25,20.6),
            G.box(-3.75,2.75,hv+9.,hv+10.2,od-9.25,20.6))
    # Close the two steps of the back wall in u as well as v. Without these
    # returns, compound oblique rays can pass the staggered ends to the servo.
    G.union(cap,G.box(-9.5,-8.25,hv+3.7,hv+5.7,od-9.25,20.6),
            G.box(-5.,-3.75,hv+3.7,hv+10.2,od-9.25,20.6))
    G.cut(support,G.box(-27.25,-12.25,bl-.45,bh+.45,-40,od-6.0))
    parts['servo_cap']=cap
    bridge=G.box(-15.25,-13.5,-29.5,hv+29.8,1.2,hd,'bearing_bridge')
    G.union(bridge,G.box(1.5,3.25,-29.5,hv+29.8,1.2,hd),
            G.box(-15.25,2.75,hv+28.6,hv+29.8,1.2,od-6.25))
    G.cut(bridge,G.cyl_x(K.H,3.9,1.25,3.5),G.prism(profile(passage,K.H),'x',1.25,3.5),
          G.cyl_x(K.H,1.9,-15.75,-13.25),G.box(-15.75,3,hv+10.6,hv+30,od-6.25,hd+.5))
    # A recessed outer lip overlaps axially; there is no straight slot between
    # the cosmetic flag flange and the wall, even between the primary ray lines.
    # A complete semicircular recess (the wall ends at the axis depth) also
    # clears the flange while the bridge is inserted from the front.
    G.cut(bridge,G.cyl_x(K.H,9.05,1.25,2.))
    G.cut(bridge,G.box(-15.75,-13.25,hv+5.2,hv+30,od-9.5,hd+.5),
          G.box(1.25,3.5,hv+9.,hv+30,od-9.5,hd+.5),
          G.box(-15.75,3,hv+28.6,hv+30,od-9.5,hd+.5))
    for a,b in ((-17.,-13.25),):
        keeper=G.box(a,b,hv-4.9,hv+4.9,hd-4.9,hd)
        G.cut(keeper,G.cyl_x(K.H,bore,a-.5,b+.5))
        G.union(bridge,keeper,G.box(a,b,hv-4.9,hv-1.9,3.25,hd-1.5))
    right=G.box(18.25,21.25,hv-3,ov+6,2.25,6.25,'input_bridge')
    keeper=G.box(15,18,hv-4.9,hv+4.9,hd-4.9,hd)
    G.cut(keeper,G.cyl_x(K.H,bore,14.5,18.5))
    G.union(right,keeper,G.box(15,18,hv-4.9,hv-1.9,3.25,hd-1.5),
            G.box(15,21.25,hv-3,hv,3.25,6.25),
            G.box(12.5,21.25,ov+2.7,ov+5.7,3.25,od),
            G.box(12.5,15.5,ov-5.7,ov+5.7,od-5.7,od))
    G.cut(right,G.cyl_x(K.O,2.7,12,16),G.cyl_x(K.O,4.1,15.5,17.5))
    parts['input_bridge']=right
    collar=G.box(-17.,-13.25,hv-3.5,hv+3.5,hd-4.9,hd)
    G.cut(collar,G.cyl_x(K.H,1.6,-17.5,-13))
    G.union(bridge,collar)
    # The flag's left collar enters a stepped recess. The front wall and collar
    # overlap axially, without a projecting lip that would cross the flag plate
    # during assembly. The remaining bearing length is -17 .. -14 = 3mm.
    G.cut(bridge,G.cyl_x(K.H,5.2,-14.,-12.75))
    # Carve the bridge's front insertion sweep, with 0.25mm seating clearance.
    for a,b,vl,vh,z in ((-17.,-13.25,hv-4.9,hv+4.9,hd),(15,18,hv-4.9,hv+4.9,hd),
                       (15,21.25,hv-4.9,hv,6.25),(18.25,21.25,hv-3,ov+6,6.25),
                       (12.5,21.25,ov+2.7,ov+5.7,od),(12.5,15.5,ov-5.7,ov+5.7,od)):
        G.cut(support,G.box(a-.25,b+.25,vl-.25,vh+.25,-40,z+.25))
    # The remaining back halves of the pin bearings are integral with the tray.
    for a,b in ((-17.,-13.25),(15,18)):
        saddle=G.cyl_x(K.H,4.9,a,b)
        G.cut(saddle,G.cyl_x(K.H,bore,a-.5,b+.5),G.box(a-.5,b+.5,hv-6,hv+6,-40,hd+.25))
        G.union(support,saddle)
    G.cut(support,G.cyl_x(K.H,5.2,-14.,-12.75))
    parts['bearing_bridge']=bridge
    # Front-inserted fixed shields and retainers have explicit 0.25mm seats.
    for a,b,vl,vh,z in ((-15.5,-13.25,-29.75,hv+30.05,hd+.25),
                       (1.25,3.5,-29.75,hv+30.05,hd+.25),
                       (-15.5,3,hv+28.35,hv+30.05,od-6.),
                       (-15,3,hv+8.75,hv+29.45,od-6.),
                       (-15,-3.5,hv+5.15,hv+29.45,od-6.),
                       (-13.75,-9.25,hv+4.95,hv+6.65,20.85),
                       (-9.75,-3.5,hv+3.45,hv+5.15,20.85),
                       (-4,3,hv+8.75,hv+10.45,20.85),
                       (-9.75,-8.,hv+3.45,hv+6.65,20.85),
                       (-5.25,-3.5,hv+3.45,hv+10.45,20.85),
                       (-9.75,-3.5,hv+3.45,hv+6.25,od-6.)):
        G.cut(support,G.box(a,b,vl,vh,-40,z))
    # Retain the same finger-operated mounting snaps as the baseline cassette.
    for u in (-26,26):
        G.union(support,G.box(u-2.5,u+2.5,-26,-23,3.3,5.25),G.box(min(u,-22),max(u,18)+.2,-35,-32,3.3,6.25),
                G.box(u-2.5,u+2.5,-34,-23,3.3,6.25))
        G.cut(support,G.box(u-2,u+2,-24.8,-6.5,3,8))
        G.union(support,G.box(u-.8,u+.8,-25,-7,3.25,4.85),
                G.box(u-.8,u+.8,-10,-7,.5,4),G.box(u-1.4,u+1.4,-9.4,-7.6,.2,1.2))
        G.cut(panel,G.box(u-1,u+1,-10.2,-6.8,-.5,3.5),G.box(u-1.6,u+1.6,-9.6,-7.4,-.5,1.4))
        G.cut(support,G.box(u-1.1,u+1.1,-23,-10,4.85,6.5))
    # The face is opaque over the gears, with a 1.2mm roof and a separate flag well.
    G.cut(panel,G.box(-13.5,1.5,-30.5,hv+28.6,-1,3.5),G.box(1.4,18.1,-30,29,1.2,3.5),
          G.box(-15.5,-13.25,-30,9.8,.95,3.5),G.box(-13.75,3,hv+28.35,hv+30,.95,3.5))
    # Connector pocket and open cable channel stay behind the flat face.
    G.cut(support,G.box(-23,-9,15,23,3.0,21.25),G.box(-21,-18,bh+.25,15.25,-40,17.9))
    G.cut(support,G.box(-38,-29.25,-26.25,-21.75,3,8.25),
          G.cyl_x(K.H,2.15,-17.5,-16.9),G.cyl_x(K.H,2.15,17.95,18.5))
    front_void(fp,-14.,2.)
    parts['support']=support
    labels={'panel':'旗カセットの面板','key_l':'左の交換キー','key_r':'右の交換キー',
            'support':'サーボ座と後側の軸受け','servo_cap':'旗室の底とサーボ押さえ',
            'input_gear':'ホーン受け付き入力扇形歯車','sector_gear':'出力扇形歯車と駆動キー',
            'flag':'14×28mmの旗と偏心した腕','flag_cover':'旗軸の右カラー',
            'bearing_bridge':'旗室の遮蔽壁と左軸押さえ','input_bridge':'入力軸と右軸の押さえ',
            'hinge_pin':'抜け止め溝付きの旗軸ピン','servo':'SG92R','horn':'SG92R付属ホーン'}
    result={}
    for pid,ob in parts.items():
        G.clean(ob,dist=.0001 if pid=='support' else .001)
        bm=bmesh.new(); bm.from_mesh(ob.data)
        wire=[e for e in bm.edges if e.is_wire]
        if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
        loose=[v for v in bm.verts if not v.link_edges]
        if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        bm.to_mesh(ob.data); bm.free()
        ob.name=pid
        rot=np.eye(4)
        if pid=='input_gear': rot=np.asarray(Matrix.Rotation(-math.pi/2,4,'Y'))
        if pid=='hinge_pin': rot=np.asarray(Matrix.Rotation(-math.pi/2,4,'Y'))
        if pid in ('sector_gear','flag_cover'): rot=np.asarray(Matrix.Rotation(math.pi/2,4,'Y'))
        if pid in ('support','servo_cap'):rot=np.asarray(Matrix.Rotation(math.pi,4,'X'))
        result[pid]={'object':ob,'print_rotation':rot,'label':labels[pid],
                    'color':'#7598b3' if pid=='servo' else '#444844' if pid=='horn' else '#deddd5',
                    'purchased':pid in ('servo','horn')}
    return result
