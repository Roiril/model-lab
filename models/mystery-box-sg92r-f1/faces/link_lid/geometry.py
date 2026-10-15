"""Cassette solids in local (u,v,d) millimetres. Builds no files or global scene."""
import ast
import math
from pathlib import Path
import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from printmech import geometry as G
from . import params as P
from . import kinematics as K
from .recipe import build_mount


def clone(ob, name):
    copy = ob.copy()
    copy.data = ob.data.copy()
    copy.name = name
    bpy.context.collection.objects.link(copy)
    return copy


def ref_parts(common):
    """Execute approved reference function definitions only; never its exports."""
    path = Path(common.ROOT)/'models'/'sg92r-photo'/'model.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    ns = dict(vars(common.SG), bpy=bpy, bmesh=bmesh, math=math, Vector=Vector, EPS=.00002)
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[]), str(path), 'exec'), ns)
    out = {}
    matrix = Matrix(((0,0,1000,P.SERVO_BASE_U*1000),(1000,0,0,K.O[0]),(0,1000,0,K.O[1]),(0,0,0,1)))
    for pid, function in [('servo','build_body'),('horn','build_horn')]:
        ob = ns[function]()
        ob.data.transform(ob.matrix_world)
        ob.matrix_world = Matrix.Identity(4)
        ob.data.transform(matrix)
        if pid == 'horn':
            G.transform(ob, Matrix(K.rot_x(P.CLOSED_ALPHA_DEG+180, K.O)))
        G.clean(ob)
        out[pid] = ob
    return out


def capsule(a, ra, b, rb, u0, u1, name):
    return G.prism(G.hull(G.circle(a,ra,48)+G.circle(b,rb,48)), 'x', u0, u1, name)


def build(interface, common_params):
    sg = common_params.SG
    m = lambda x: x*1000
    parts = build_mount(interface)
    parts.update(ref_parts(common_params))
    panel = parts['panel']
    # The hinge edge moves 2.60 mm toward -v. Leave that sweep clear.
    G.cut(panel, G.box(-18.6,24.4,-15.8,18.6,-1,3.5),
          G.box(-27.75,27.75,-19.8,-5.5,-1,2.25))
    # The removable front plate cages a plain hinge axle at both ends.
    # No oversized head must be forced through a closed bearing during assembly.
    G.union(panel,G.box(-29.25,-28.05,-15,-9,1.8,3.0),
            G.box(26.6,29.25,-15,-9,1.8,3.0))

    # Ear channels are open toward the face. They are retained by the removable cap.
    support = G.box(-13.75,13.95,-8,2,28.5,31.5,'support')
    G.union(support,G.box(-13.75,-10.75,-8,2,23.75,30))
    G.union(support, G.box(-19.5,-2.5,-19.5,6.5,23.75,26.75))
    for va,vb in ((-24.75,-19.75),(3.75,8.75)):
        rail = G.box(-11.75,-3.25,va,vb,11.25,24.25)
        G.cut(rail, G.box(-8.75,-6.25,va-.5,vb+.5,10,23.75))
        G.union(support,rail)
    # Main cradle side stops and the two narrow arms joining the front mounting rail.
    for va,vb in ((-22.75,-19.75),(3.75,6.75)):
        G.union(support,G.box(-19.5,-10.75,va,vb,11.5,24.25))
    G.union(support,G.box(-30.6,30.6,-28,-25,3.3,8.5),
            G.box(-19.5,-10.75,-26.5,-23.5,7.5,12.75),
            G.box(-2.25,.75,-26,-19.25,7.5,26.75),
            G.box(-4,.75,-24.75,-19.75,11.25,23.74),
            G.box(-4,.75,-19.75,-18.5,23.75,26.75))
    # Open saddles allow the complete moving linkage to be lowered into the support.
    for u0,u1 in ((-28,-25),(23,26)):
        bearing = G.cyl_x(K.H,5.7,u0,u1,name='hinge_saddle')
        G.cut(bearing,G.cyl_x(K.H,2.7,u0-.5,u1+.5),
              G.box(u0-.5,u1+.5,-20,-4,-5,3.3))
        G.union(support,bearing,G.box(u0,u1,-28, -14.7,3.3,8.5))
    bearing = G.cyl_x(K.O,5.7,10.95,13.95,name='crank_saddle')
    G.cut(bearing,G.cyl_x(K.O,2.7,10.5,14.5),G.box(10.5,14.5,-10,4,0,17.5))
    G.union(support,bearing,G.box(10.95,13.95,-6,0,22,30))
    # Two front-operated snap posts; each bends along the 18 mm in-plane arm.
    for sign in (-1,1):
        u = sign*28.4
        arm_d=9.3 if sign<0 else 3.3
        G.union(support,G.box(u-1.5,u+1.5,-28,-25,3.3,arm_d+1.6),
                G.box(u-.8,u+.8,-28,-.5,arm_d,arm_d+1.6),
                G.box(u-.8,u+.8,-3.5,-.5,.8,arm_d+.7),
                G.box(u-1.4,u+1.4,-2.9,-1.1,0,1.2))
        G.cut(panel,G.box(u-1,u+1,-3.7,-.3,-.5,3.5),
              G.box(u-1.6,u+1.6,-3.1,-.9,-.5,1.4))
    # At d=24 the envelope narrows. End the outboard flange rails before it.
    G.cut(support,G.box(-40,40,-40,-19.75,23.74,40),G.box(-40,-19.75,-40,40,23.74,40))
    G.cut(support,G.box(-40,40,-40,-24.75,16.74,40))
    # Bores belong only to the bearing blocks; a full-width cut severs the snap arm.
    for u0,u1 in ((-28,-25),(23,26)):
        G.cut(support,G.cyl_x(K.H,2.7,u0-.01,u1+.01))
    G.cut(support,G.cyl_x(K.O,2.7,10.5,14.5))
    # Released exchange keys rotate past the rail and outer edge of the support heads.
    # Keep the inward support hooks and their 1.2 mm thick heads intact.
    for u0,u1 in ((29.25,31),(-31,-29.25)):
        G.cut(support,G.box(u0,u1,-25.3,-24.7,3.0,8.3))
    for u0,u1 in ((29.3,31),(-31,-29.3)):
        G.cut(support,G.box(u0,u1,-6.65,-4.35,-.3,1.45))
    parts['support'] = support

    # Opaque cap: the wall seen behind the open lid, servo hold-down, and saddle closures.
    cap = G.box(-19.5,4.75,-18.5,18.5,8.25,11.25,'servo_cap')
    # Servo case stops at d=11.5. Pocket below clears the gear cover with 0.25 mm.
    G.cut(cap,G.box(-2.75,3,-12,4,10.75,12))
    G.union(cap,G.box(3.25,4.75,-6.5,18.5,2.3,9.0),
            G.box(-15,-13,-6.5,18.5,2.3,9.0))
    for u0,u1 in ((-27,-25),(24.5,26)):
        keeper = G.box(u0,u1,-16.5,-5.8,0,3.0)
        G.cut(keeper,G.cyl_x(K.H,2.7,u0-.5,u1+.5),G.box(u0-.5,u1+.5,-18,-6,-1,.0))
        G.union(cap,keeper)
    G.union(cap,G.box(-27,-20.75,-6,12,2.3,4.5),
            G.box(-21,-19,10,16,2.3,9),
            G.box(25,27,-6,16,2.3,4.5),
            G.box(25,27,14,16,2.3,6.3),
            G.box(3.25,27,14,16,4.8,6.3))
    # Flat lower saddle can slide in along -v after the complete linkage is seated.
    # Its upper face has 0.4 mm radial clearance to the 5 mm crank axle.
    G.union(cap,G.box(10.95,12.85,-8.7,2.7,11.8,14.6),
            G.box(10.95,12.85,.5,2.7,6,14.6),
            G.box(10.95,12.85,.5,16,4.8,6.3))
    G.cut(cap,G.cyl_x(K.O,2.7,10.5,14.5),G.cyl_x(K.H,2.7,-30,30))
    parts['servo_cap'] = cap

    # Horn-pocket floor and side walls derive exclusively from the approved SG92R.
    fit=m(P.HORN_FIT)
    left,right=m(sg.HORN_LEFT_X),m(sg.HORN_RIGHT_X)
    root,tip=m(sg.HORN_ROOT_W)/2,m(sg.HORN_TIP_W)/2
    hub=m(sg.HORN_HUB_DIA)/2
    def long_profile(extra):
        return [(left-extra,K.O[1]-tip-extra),(-hub,K.O[1]-root-extra),
                (hub,K.O[1]-root-extra),(right+extra,K.O[1]-tip-extra),
                (right+extra,K.O[1]+tip+extra),(hub,K.O[1]+root+extra),
                (-hub,K.O[1]+root+extra),(left-extra,K.O[1]+tip+extra)]
    def shift(poly):
        return [(v+K.O[0],d) for v,d in poly]
    # Central hub and the two short arms provide the drive. The long arms remain exposed.
    crank=G.cyl_x(K.O,5.5,m(P.CRANK_U0),m(P.CRANK_U1),name='crank')
    short=m(sg.HORN_SPAN_Y)/2
    half=m(sg.HORN_SHORT_W)/2
    G.union(crank,G.box(m(P.CRANK_U0),m(P.CRANK_U1),K.O[0]-half-1.5,K.O[0]+half+1.5,K.O[1]-short-1.5,K.O[1]+short+1.5))
    pin_a=(K.O[0]+m(P.CRANK_LENGTH),K.O[1])
    G.union(crank,capsule(K.O,5.5,pin_a,3.8,m(P.CRANK_U0),m(P.CRANK_U1),'crank_web'))
    pocket_end=m(P.SERVO_BASE_U+sg.HORN_TOP_Z+P.HORN_FIT)
    G.cut(crank,G.prism(shift(long_profile(fit)),'x',4.9,pocket_end),
          G.box(4.9,pocket_end,K.O[0]-half-fit,K.O[0]+half+fit,K.O[1]-short-fit,K.O[1]+short+fit),
          G.cyl_x(K.O,hub+fit,4.9,pocket_end))
    # The short-arm pocket is symmetric; the 18 mm horn arm is oriented +v independently.
    G.union(crank,G.cyl_x(K.O,2.5,10.5,14.15))
    # Make the crank at alpha=0, then bake its closed alpha. Its pin is exactly a=12.
    G.union(crank,G.cyl_x(pin_a,3.8,13.15,14.85),G.cyl_x(pin_a,2.5,10.5,18.45),
            G.cyl_x(pin_a,2.85,18.45,19.65))
    # 0.15 mm tip deflection. Free beam after the washer is 4.8 mm, t <= 1.6 mm.
    G.cut(crank,G.box(11.65,19.9,pin_a[0]-.9,pin_a[0]+.9,pin_a[1]-4,pin_a[1]+4))
    # Correct horn: the 16 mm arm points toward -v after its 180 degree indexing.
    # This stop leaves 0.30 mm nominal clearance but blocks the reversed 18 mm arm.
    index_near=K.O[0]-m(sg.HORN_RIGHT_X)-.3
    index_far=index_near-1.2
    # Bias the 1.2 mm square stop toward -d to clear the depth-24 envelope step.
    index_outline=[(index_far,K.O[1]-1.8),(index_near,K.O[1]-1.8),
                   (index_near,K.O[1]-.6),(index_far,K.O[1]-.6)]
    index_floor=G.hull(G.circle(K.O,3.8,48)+index_outline)
    G.union(crank,G.prism(index_floor,'x',7.75,10.75,'horn_index_floor'),
            G.box(5.75,8.05,index_far,index_near,K.O[1]-1.8,K.O[1]-.6,'horn_index_stop'))
    G.transform(crank,Matrix(K.rot_x(P.CLOSED_ALPHA_DEG,K.O)))
    parts['crank']=crank

    link=capsule(K.A_CLOSED,4.2,K.B_CLOSED,3.0,m(P.LINK_U0),m(P.LINK_U1),'link')
    G.cut(link,G.cyl_x(K.A_CLOSED,2.7,14.5,19))
    G.union(link,G.cyl_x(K.B_CLOSED,2.5,17.9,21.75),G.cyl_x(K.B_CLOSED,2.85,21.75,22.95))
    G.cut(link,G.box(17.9,23.4,K.B_CLOSED[0]-.9,K.B_CLOSED[0]+.9,K.B_CLOSED[1]-4,K.B_CLOSED[1]+4))
    parts['link']=link

    lid=G.box(-18,18,-12,18,0,2,'lid')
    for u0,u1 in ((-16,-13),(13,16)):
        lug=G.cyl_x(K.H,5.1,u0,u1)
        G.cut(lug,G.cyl_x(K.H,2.7,u0-.5,u1+.5),G.box(u0-.5,u1+.5,-19,-5,-4,0))
        G.union(lid,lug)
    ear=capsule(K.H,4,K.B_CLOSED,5.7,m(P.EAR_U0),m(P.EAR_U1),'lid_ear')
    G.cut(ear,G.cyl_x(K.B_CLOSED,2.7,18,22),G.box(18,22,-20,8,-5,0),G.cyl_x(K.H,2.7,18,22))
    G.union(lid,ear,G.box(17.5,20.55,-12,-8,1.5,3.5))
    # Back the ear's low circular edge below the B pin's lowest contact surface.
    G.union(lid,G.box(17.9,21.45,-3.5,3.5,0,1.5))
    # A moving side skirt overlaps the opaque wall; never serves as a bearing.
    skirt=G.prism([(-11,1.5),(17.8,1.5),(17.8,5.5),(-9,5.5)],'x',-18,-16)
    G.union(lid,skirt)
    # 45 degree roofs retain the circular seat; the hinge roof leaves 1.32 mm wall.
    G.cut(lid,G.prism(G.teardrop(K.H,2.7,1.08),'x',-30,30),
          G.prism(G.teardrop(K.B_CLOSED,2.7,.4),'x',18,22))
    parts['lid']=lid

    pin=G.cyl_x(K.H,2.5,-27.65,26.2,name='hinge_pin')
    G.cut(pin,G.box(-30,28,-18,-6,-1,1))
    parts['hinge_pin']=pin

    labels={'panel':'正面の面板','key_l':'左の交換キー','key_r':'右の交換キー','support':'サーボ座と軸受け',
            'servo_cap':'サーボ押さえと遮蔽壁','crank':'ホーン受けとクランク','link':'連結リンク',
            'lid':'36×30mmの蓋','hinge_pin':'蝶番ピン','servo':'SG92R','horn':'SG92R付属ホーン'}
    out={}
    for pid,ob in parts.items():
        ob.name=pid
        G.clean(ob)
        # Flat face against bed. Pins on link/crank grow along build +Z.
        turn=np.eye(4)
        if pid in ('crank','link'):
            turn=np.asarray(Matrix.Rotation(-math.pi/2,4,'Y'))
        if pid in ('key_l','key_r'):
            turn=np.asarray(Matrix.Rotation(math.pi,4,'X'))
        if pid=='support':
            turn=np.asarray(Matrix.Rotation(math.pi,4,'X'))
        if pid=='hinge_pin':
            turn=np.eye(4)
        out[pid]={'object':ob,'label':labels[pid],'print_rotation':turn,
                  'color':'#7598b3' if pid=='servo' else '#444844' if pid=='horn' else '#deddd5',
                  'purchased':pid in ('servo','horn')}
    return out
