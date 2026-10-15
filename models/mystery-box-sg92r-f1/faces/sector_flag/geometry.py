"""Cassette entry point. Closed millimetre coordinates; no exports or scene reset."""
import ast,math
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
from printmech import geometry as G
from . import params as P,kinematics as K

def clone(ob,name):
    result=ob.copy(); result.data=ob.data.copy(); result.name=name
    bpy.context.collection.objects.link(result)
    return result

def profile(poly,center):
    return [(v+center[0],d+center[1]) for v,d in poly]

def horn_profile(sg,extra):
    left,right=sg.HORN_LEFT_X*1000,sg.HORN_RIGHT_X*1000
    hub=sg.HORN_HUB_DIA*500
    root,tip=sg.HORN_ROOT_W*500,sg.HORN_TIP_W*500
    return G.hull(G.circle((left+tip,0),tip+extra,48)+G.circle((right-tip,0),tip+extra,48)+
                  G.circle((-hub,0),root+extra,48)+G.circle((hub,0),root+extra,48))

def reference(common):
    path=Path(common.ROOT)/'models/sg92r-photo/model.py'
    tree=ast.parse(path.read_text(encoding='utf-8'))
    ns=dict(vars(common.SG),bpy=bpy,bmesh=bmesh,math=math,Vector=Vector,EPS=.00002)
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(path),'exec'),ns)
    mat=Matrix(((0,0,1000,P.SERVO_BASE_U*1000),(1000,0,0,K.O[0]),(0,1000,0,K.O[1]),(0,0,0,1)))
    result={}
    for pid,fn in (('servo','build_body'),('horn','build_horn')):
        ob=ns[fn](); ob.data.transform(ob.matrix_world); ob.matrix_world=Matrix.Identity(4)
        ob.data.transform(mat)
        if pid=='horn':G.transform(ob,Matrix(K.rot_x(P.HORN_CLOSED_DEG,K.O)))
        G.clean(ob,dist=.001); result[pid]=ob
    return result

def build(interface,common_params):
    from .deep_geometry import build as build_deep
    return build_deep(interface,common_params)
