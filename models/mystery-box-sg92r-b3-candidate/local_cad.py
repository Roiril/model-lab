"""Short body-supported captive bolt. Baseline 19 solids stay independent.
Diagnostic local CAD, not a recommended print design. Requires bundled baseline.
"""
from pathlib import Path
import sys,json,math,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.dont_write_bytecode=True
import bpy,bmesh
from mathutils import Matrix
from cad_utils import *
import params as p
def q(k):return getattr(p,k)*1000
bpy.ops.wm.open_mainfile(filepath=str(R/'baseline_reference.blend'))
body=bpy.data.objects['01_body'];key=bpy.data.objects['13_body_cross_key']
# Solid guide body grows directly from the existing box floor; no cassette tie.
add(body,cube('short bolt floor-mounted guide',(40.4,12.5,2.3),(54.,23.,9.0)))
# Reopen the original head recess with its original diagonal end shoulders.
poly=[(12.85*math.cos(i*math.tau/96),12.85*math.sin(i*math.tau/96)) for i in range(96)]
for nx,ny in [(-2**-.5,2**-.5),(2**-.5,-2**-.5)]:
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  va=a[0]*nx+a[1]*ny-11.75;vb=b[0]*nx+b[1]*ny-11.75
  if va<=0:out.append(a)
  if (va<=0)!=(vb<=0):
   t=va/(va-vb);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
 poly=out
cut(body,prism_z('preserve baseline head sweep',-.2,3.2,[(q('KEY_X')+x,q('KEY_Y')+y) for x,y in poly]))
cut(body,cyl('preserve key stem sweep through new guide',(q('KEY_X'),q('KEY_Y'),6.15),6.9,6.3,'Z'))
cut(body,cube('preserve original key bottom insertion',(31.,3.2,-.2),(42.,45.,8.0)))
# L tongue path + wings are trapped between roof and floor outside the stem throat.
cut(body,cube('captive bolt wing chamber',(40.9,13.2,3.0),(51.0,22.3,7.2)))
cut(body,cube('bolt transverse tongue corridor',(37.6,24.2,3.0),(51.0,28.8,7.2)))
cut(body,cube('bolt connecting arm corridor',(40.9,20.2,3.0),(51.0,28.8,7.2)))
cut(body,cube('bolt operation neck throat',(42.9,16.2,-.2),(53.4,20.8,7.2)))
# Head sweep stays open to underside. An isolated narrow tab follows the dogleg.
cut(body,cube('underside head chamber',(40.9,15.4,-.2),(55.4,21.0,3.1)))
cut(body,cube('head raised common chamber',(40.9,15.4,1.9),(55.4,21.0,4.9)))
for xa,xb in [(43.9,46.5),(49.8,52.4)]:
 cut(body,cube('index tab end pocket',(xa,13.2,-.2),(xb,15.7,1.9)))
cut(body,cube('index tab upper connection',(43.9,13.2,1.9),(52.4,15.7,4.9)))
# A thick stem notch catches both tangential key rotation directions.
cut(key,cube('short bolt key notch',(q('NOTCH_LO_X'),q('NOTCH_LO_Y'),q('NOTCH_LO_Z')),(q('NOTCH_HI_X'),q('NOTCH_HI_Y'),q('NOTCH_HI_Z'))))
bolt=cube('20_short_body_bolt',(q('TOOTH_LO_X'),q('TOOTH_LO_Y'),q('TOOTH_LO_Z')),(q('TOOTH_HI_X'),q('TOOTH_HI_Y'),q('TOOTH_HI_Z')))
add(bolt,cube('short transverse root',(41.2,16.5,3.3),(44.7,28.5,5.7)))
add(bolt,cube('broad captive root wing',(41.2,13.5,3.3),(44.7,22.,5.7)))
add(bolt,cube('operation neck',(43.2,16.5,2.5),(47.2,20.5,5.7)))
add(bolt,cube('underside visible handle',(41.2,15.7,.2),(49.2,20.3,2.8)))
add(bolt,cube('broad index tab',(44.2,13.5,.2),(46.2,15.9,1.8)))
color(bolt,'Short bolt',(.08,.55,.60));color(key,'Key',(.85,.49,.12))
# Underside L/R glyphs identify the index tab position; tab can fully lower only at an end.
for xa in (44.2,50.1):
 cut(body,cube('index label stem',(xa,10.,-.2),(xa+.55,12.2,.5)))
cut(body,cube('L index label bottom',(44.2,10.,-.2),(46.2,10.55,.5)))
cut(body,cube('R index label upper',(50.1,11.65,-.2),(51.6,12.2,.5)))
cut(body,cube('R index label mid',(50.1,10.9,-.2),(51.6,11.45,.5)))
cut(body,cube('R index label right',(51.05,10.9,-.2),(51.6,12.2,.5)))
cut(body,prism_z('R index label diagonal',-.2,.5,[(50.7,11.1),(51.25,11.1),(51.8,10.),(51.25,10.)]))
audit=[]
for o in [body,key,bolt]:
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume()*1e9
 seen=set();components=0
 for v in bm.verts:
  if v in seen:continue
  components+=1;stack=[v];seen.add(v)
  while stack:
   a=stack.pop()
   for e in a.link_edges:
    b=e.other_vert(a)
    if b not in seen:seen.add(b);stack.append(b)
 bm.free();assert bad==0 and vol>0 and components==1,(o.name,bad,vol,components)
 audit.append({'name':o.name,'nonmanifold_edges':bad,'volume_mm3':vol,'components':components})
# STL export is deferred until local geometry and access pass; prior diagnostic STL is archived.
bpy.ops.wm.save_as_mainfile(filepath=str(R/'editable_short_bolt_B1.blend'))
report={'version':p.VERSION,'baseline_sha256':hashlib.sha256((R/'baseline_reference.blend').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256((R/'editable_short_bolt_B1.blend').read_bytes()).hexdigest(),'modified_meshes':audit,'physical_tested':False,'print_ready':False,'old_separate_horn_stops_18_19_preserved':True,'baseline_input_readonly':True,'release_sequence_mm':[['Z',q('BOLT_LIFT')],['X',q('BOLT_TRAVEL')],['Z',-q('BOLT_LIFT')]],'limitations':['First bolt +Z is a remaining free DOF; rigid key torque faces have Y normals and cannot directly drive Z/X ideal release','Multi-axis vibration, friction, stiffness, tolerance, tool and printing unverified','Full key rotation with D25 speaker and cassette removal must pass before integration']}
(R/'build_result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('B1 BUILD SAVED',json.dumps(report,ensure_ascii=False),flush=True)
