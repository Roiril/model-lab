"""Build exclusively inside models/flag-box and prints/flag-box. Headless Blender."""
import ast
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'lib'))
sys.path.insert(0, str(HERE))
import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from printmech import geometry as G
from printmech import contract as C
from params import *
from kinematics import transforms

BUILD = HERE / 'build'
PRINTS = ROOT / 'prints' / 'flag-box'
BUILD.mkdir(exist_ok=True)
PRINTS.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def export(ob, path, matrix=None):
    clone = ob.copy()
    clone.data = ob.data.copy()
    bpy.context.collection.objects.link(clone)
    if matrix is not None:
        clone.data.transform(matrix)
    bm=bmesh.new()
    bm.from_mesh(clone.data)
    bmesh.ops.dissolve_limit(bm,angle_limit=0.00001,verts=list(bm.verts),edges=list(bm.edges),use_dissolve_boundaries=True)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.00001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(clone.data)
    bm.free()
    bpy.ops.object.select_all(action='DESELECT')
    clone.select_set(True)
    bpy.context.view_layer.objects.active = clone
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True)
    bpy.data.objects.remove(clone, do_unlink=True)

def baked(ob):
    ob.data.transform(ob.matrix_world)
    ob.matrix_world = Matrix.Identity(4)
    G.clean(ob,dist=1e-8)
    return ob

# Execute only function definitions of the approved reference model.
# Its top-level export calls are deliberately never executed.
source = ROOT / 'models' / 'sg92r-photo' / 'model.py'
tree = ast.parse(source.read_text(encoding='utf-8'))
namespace = dict(vars(SG), bpy=bpy, bmesh=bmesh, math=math, Vector=Vector, EPS=0.00002)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[]), str(source), 'exec'), namespace)
servo = baked(namespace['build_body']())
horn = baked(namespace['build_horn']())
# Proper rotation: local Z -> world X, X -> Y, Y -> Z. Metres -> mm.
reference_to_world = Matrix(((0,0,1000,mm(SERVO_ORIGIN_X)), (1000,0,0,mm(AXIS_Y)), (0,1000,0,mm(AXIS_Z)), (0,0,0,1)))
for ob in (servo, horn):
    ob.data.transform(reference_to_world)
    G.clean(ob)
servo.name = 'servo'
horn.name = 'horn'

E, W, Z = mm(EDGE)/2, mm(WALL), mm(AXIS_Z)
O, F = mm(SERVO_ORIGIN_X), mm(FIT)

# Bottom shell, upright print. Open at the top.
box = G.cut(G.box(-E,E,-E,E,0,65,'box'), G.box(-E+W,E-W,-E+W,E-W,W,66))
# A cradle built from the floor upwards. Open channels accept the case and ears.
cradle = G.box(-19,10,-24,14,2.5,55,'cradle')
bc, bl, bw = mm(SG.BODY_CENTER_X), mm(SG.BODY_L), mm(SG.BODY_W)
G.cut(cradle,
      G.box(O-F,O+mm(SG.BODY_H)+F,bc-bl/2-F,bc+bl/2+F,Z-bw/2-F,70),
      G.box(O+mm(SG.FLANGE_BOTTOM_Z)-F,O+mm(SG.FLANGE_BOTTOM_Z+SG.FLANGE_T)+F,
            bc-mm(SG.FLANGE_L)/2-F,bc+mm(SG.FLANGE_L)/2+F,Z-mm(SG.FLANGE_W)/2-F,70),
      G.box(O+mm(SG.GEAR_COVER_BOTTOM_Z)-F,12,-9,7,41.7,70),
      G.box(7,11,-25,15,47.5,70))
G.transform(cradle,Matrix.Translation((0,mm(AXIS_Y),0)))
cradle_trial=cradle.copy();cradle_trial.data=cradle.data.copy();bpy.context.collection.objects.link(cradle_trial)
G.union(box, cradle)
# Wire exits through an open notch: no connector is threaded through a closed hole.
G.cut(box, G.box(-18,-4,30,35,41,66))
# Finger release windows, with 45 degree roofs.
for sign in (-1,1):
    window = G.prism([(18,53),(28,53),(28,56.5),(23,61.5),(18,56.5)], 'x', sign*30 if sign>0 else -35, 35 if sign>0 else -30)
    G.cut(box, window)

# Rotor: smooth circular body, asymmetric tapered cross pocket open towards the servo.
flag = G.cyl_x((0,Z),mm(ROTOR_RADIUS),12,mm(ROTOR_FRONT_X),n=80,name='flag')
G.union(flag, G.box(mm(FLAG_X0),mm(ROTOR_FRONT_X),mm(FLAG_Y0),mm(FLAG_Y1),65,68))
hc = mm(HORN_FIT)
left, right = mm(SG.HORN_LEFT_X), mm(SG.HORN_RIGHT_X)
root, tip = mm(SG.HORN_ROOT_W)/2, mm(SG.HORN_TIP_W)/2
long_poly = [(left-hc,Z-tip-hc),(-mm(SG.HORN_HUB_DIA)/2,Z-root-hc),
             (mm(SG.HORN_HUB_DIA)/2,Z-root-hc),(right+hc,Z-tip-hc),
             (right+hc,Z+tip+hc),(mm(SG.HORN_HUB_DIA)/2,Z+root+hc),
             (-mm(SG.HORN_HUB_DIA)/2,Z+root+hc),(left-hc,Z+tip+hc)]
arm_x1 = O+mm(SG.HORN_TOP_Z)+hc
G.cut(flag, G.prism(long_poly,'x',10,arm_x1),
      G.box(10,arm_x1,-mm(SG.HORN_SHORT_W)/2-hc,mm(SG.HORN_SHORT_W)/2+hc,
            Z-mm(SG.HORN_SPAN_Y)/2-hc,Z+mm(SG.HORN_SPAN_Y)/2+hc),
      G.cyl_x((0,Z),mm(SG.HORN_HUB_DIA)/2+hc,10,arm_x1,n=64))
# Printed hexagon button connects the rotor to the outer bearing.
hexagon = G.circle((0,Z),4,6,a0=30)
hex_clear = G.circle((0,Z),4.25,6,a0=30)
G.cut(flag, G.prism(hex_clear,'x',18.5,23))
button = G.prism(hexagon,'x',18.75,23,'bearing_button')
G.union(button, G.cyl_x((0,Z),4,22.5,28.85), G.cyl_x((0,Z),6,28.75,30.5))
for ob in (flag,button):
    G.transform(ob,Matrix.Translation((0,mm(AXIS_Y),0)))

# Roof printed exterior face down. Moving envelope is removed from the top.
roof = G.box(-34,34,-34,34,65,68,'roof')
G.cut(roof, G.box(7.0,23.1,-29,28,64,69))
# Three-sided bearing, open downwards for lowering over the button.
bearing = G.box(25,28.5,-10,10,38,65.5)
G.cut(bearing, G.box(24,29,-4.25,4.25,37,Z), G.cyl_x((0,Z),4.25,24,29))
G.transform(bearing,Matrix.Translation((0,mm(AXIS_Y),0)))
G.union(roof, bearing)
# Stops above the servo body keep the servo seated in the cradle.
for ya,yb in ((-16,-12),(2,6)):
    G.union(roof, G.box(-14,-8,ya+mm(AXIS_Y),yb+mm(AXIS_Y),54.25,65.5))
# Rigid roof legs. Separate removable keys flex within their printed layers.
keys={}
for sign in (-1,1):
    leg=G.box(26.75,30.75,19,27,50,65.5)
    G.cut(leg,G.prism([(20.75,56.3),(25.25,56.3),(25.25,53.7),(23,51.45),(20.75,53.7)],'x',26,31.5))
    lower=[(24.5,21),(25.3,20.45),(26,20.45),(26.5,21),(31.6,21),(31.6,22.2),(24.5,22.2)]
    upper=[(x,46-y) for x,y in lower]
    key=G.box(31.25,33.75,19.25,26.75,54,57)
    G.union(key,G.prism(lower,'z',54,56),G.prism(upper,'z',54,56))
    if sign<0:
        reflection=Matrix.Diagonal((-1,1,1,1))
        for ob in (leg,key):
            G.transform(ob,reflection)
            G.clean(ob)
    G.union(roof,leg)
    keys['key_right' if sign>0 else 'key_left']=key

parts = {'box':box, 'roof':roof, 'flag':flag, 'bearing_button':button, **keys, 'servo':servo, 'horn':horn}
colors = {'box':'#d2d5d1','roof':'#e5e5df','flag':'#bc5a39','bearing_button':'#bc5a39','servo':'#356ca5','horn':'#303438'}
colors.update(key_right='#70796d',key_left='#70796d')
labels = {'box':'箱','roof':'天板','flag':'旗とホーン受け','bearing_button':'軸受けボタン','servo':'SG92R','horn':'付属ホーン'}
labels.update(key_right='右の留め具',key_left='左の留め具')
manifest=[]
metrics={}
for pid, ob in parts.items():
    G.clean(ob)
    ob.name=pid
    export(ob, BUILD/f'{pid}.stl')
    mat=bpy.data.materials.new(pid)
    h=colors[pid].lstrip('#')
    mat.diffuse_color=tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    row={'id':pid,'label':labels[pid],'assembly':f'build/{pid}.stl','color':colors[pid]}
    if pid not in ('servo','horn'):
        # Roof flips about X. Flag's pocket faces up. Button stands on its head.
        turn = Matrix.Rotation(math.pi,4,'X') if pid=='roof' else Matrix.Rotation(math.pi/2,4,'Y') if pid in ('flag','bearing_button') else Matrix.Identity(4)
        coords=[turn @ v.co for v in ob.data.vertices]
        lo=[min(v[i] for v in coords) for i in range(3)]
        pose=Matrix.Translation(tuple(-v for v in lo)) @ turn
        export(ob, PRINTS/f'{pid}.stl',pose)
        row['print']=f'../../prints/flag-box/{pid}.stl'
    manifest.append(row)
    vs=[v.co for v in ob.data.vertices]
    metrics[pid]={'bounds_mm':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],
                  'nonmanifold':G.nonmanifold(ob),'volume_mm3':G.volume(ob)}
C.write_manifest(BUILD,manifest,{'dimensions_mm':[68,68,68],'description':'天面の旗が起き上がる箱','exterior_parts':['box','roof']})
ids=list(parts)
C.write_motion(BUILD,[(45+i,transforms(45+i,ids)) for i in range(91)],duration_s=MOVE_SECONDS,home_servo_deg=45,easing='quintic')
plan=C.AssemblyPlan()
plan.place('servo','サーボを横に置く',['servo'])
central=C.rotation((1,0,0),45,(0,mm(AXIS_Y),Z))
def central_insertion(pid,distance):
    return lambda t:{pid:C.translation(distance*(1-t),0,0)@central}
plan.move('horn','ホーンを押し込む',['horn'],central_insertion('horn',10),21,
          'サーボを中央の90度にする。長腕18mm側を水平から45度へ向けて付ける。')
plan.move('flag','旗の受けをホーンへ差す',['flag'],central_insertion('flag',12),25)
plan.move('button','六角ボタンを差す',['bearing_button'],central_insertion('bearing_button',15),31)
plan.move('box','機構を箱へ下ろす',['box'],C.straight_path(['box'],C.translation(0,0,-80)),161,
          '実際には箱を置いてサーボ一式を上から下ろす。同じ相対経路を検査する。')
plan.move('roof','天板を閉める',['roof'],C.straight_path(['roof'],C.translation(0,0,40)),81,
          '天板を下ろす。左右の留め具は次の工程で入れる。')
for pid,sign in (('key_right',1),('key_left',-1)):
    plan.move(pid,'側面の留め具を入れる',[pid],C.straight_path([pid],C.translation(sign*15,0,0)),61,
              '頭を指で押す。外すときは側面の窓から頭をつまんで引く。')
plan.move('close','旗をゆっくり寝かせる',['horn','flag','bearing_button'],
          lambda t:{pid:C.rotation((1,0,0),45*(1-t),(0,mm(AXIS_Y),Z)) for pid in ('horn','flag','bearing_button')},46,
          '中央から45度へ戻す。スプラインの刻みでずれた分は指令角を補正する。')
plan.write(BUILD,calibration={'pass':False,'note':'判定はmechgateが独立に計測する'},passed=False)
C.write_json(BUILD/'dimensions.json',metrics)

# Fit trials are actual reductions of the production geometry.
trial=flag.copy(); trial.data=flag.data.copy(); bpy.context.collection.objects.link(trial)
G.cut(trial,G.box(5,24,-30,30,59,70))
# Pocket trial exported in the same orientation as the complete flag.
turn=Matrix.Rotation(math.pi/2,4,'Y')
vs=[turn@v.co for v in trial.data.vertices]
lo=[min(v[i] for v in vs) for i in range(3)]
export(trial,PRINTS/'horn-fit-trial.stl',Matrix.Translation(tuple(-v for v in lo))@turn)
bpy.data.objects.remove(trial,do_unlink=True)
# A short actual cradle section tests both the ear slots and cover clearance.
trial=cradle_trial
G.cut(trial,G.box(-30,20,-40,30,0,38))
vs=[v.co for v in trial.data.vertices]
lo=[min(v[i] for v in vs) for i in range(3)]
export(trial,PRINTS/'servo-fit-trial.stl',Matrix.Translation(tuple(-v for v in lo)))
bpy.data.objects.remove(trial,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BUILD/'flag-box.blend'))
print('FLAG_BOX_METRICS',metrics)
