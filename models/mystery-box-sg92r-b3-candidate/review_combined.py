"""Finite combined slack screen and true mesh surface distances. No tolerance guarantee."""
from pathlib import Path
import sys,json,math,hashlib,itertools
R=Path(__file__).resolve().parent
exec((R/'check_local.py').read_text('utf8').split("report={'input_blend_sha256'")[0])
import numpy as np
activate('editable_cube_B3.blend')
cap=bpy.data.objects['21_separate_bolt_cap'];stop=bpy.data.objects['22_symmetric_cap_stop']
report={'source_blend_sha256':hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),'physical_tested':False,'limits':'Finite sampled combined translations/tilts and directed extraction paths. No exhaustive configuration-space, strain, wear, vibration or manufacturing-tolerance proof.'}
def points(o):return np.array([list(o.matrix_world@v.co*1000) for v in o.data.vertices],float)
def distance(a,b):
 ta,tb=tree(a),tree(b);pa,pb=points(a),points(b)
 best=min([ta.find_nearest(b.matrix_world@v.co)[3]*1000 for v in b.data.vertices]+[tb.find_nearest(a.matrix_world@v.co)[3]*1000 for v in a.data.vertices])
 ea=np.array([[pa[e.vertices[0]],pa[e.vertices[1]]] for e in a.data.edges]);eb=np.array([[pb[e.vertices[0]],pb[e.vertices[1]]] for e in b.data.edges])
 U=(ea[:,1]-ea[:,0])[:,None,:];V=(eb[:,1]-eb[:,0])[None,:,:];W=ea[:,None,0,:]-eb[None,:,0,:]
 A=(U*U).sum(2);B=(U*V).sum(2);C=(V*V).sum(2);D=(U*W).sum(2);E=(V*W).sum(2);den=A*C-B*B
 s=np.divide(B*E-C*D,den,out=np.zeros_like(den),where=abs(den)>1e-15);t=np.divide(A*E-B*D,den,out=np.zeros_like(den),where=abs(den)>1e-15)
 candidates=[(s,t,(s>=0)&(s<=1)&(t>=0)&(t<=1)&(abs(den)>1e-15)),(np.zeros_like(s),np.clip(E/C,0,1),True),(np.ones_like(s),np.clip((E+B)/C,0,1),True),(np.clip(-D/A,0,1),np.zeros_like(t),True),(np.clip((B-D)/A,0,1),np.ones_like(t),True)]
 for s,t,mask in candidates:
  d2=((W+s[:,:,None]*U-t[:,:,None]*V)**2).sum(2);d2=np.where(mask,d2,np.inf);best=min(best,float(np.sqrt(d2.min())))
 return best
contact=json.loads((R/'contact_order_B3.json').read_text('utf8'));gaps=[]
for row in contact['rows']:
 v=row['minus']
 if any(x.get('start_intersection') for x in v.values()):continue
 structural=min(x['angle_abs_deg'] for n,x in v.items() if n!='REFERENCE exciter25x10' and x['angle_abs_deg'] is not None)
 restore();keyangle(-structural,x=row['bias_XY_mm'][0]);key.matrix_world=Matrix.Translation(Vector((0,row['bias_XY_mm'][1]*.001,0)))@key.matrix_world
 gaps.append({'bias_XY_mm':row['bias_XY_mm'],'structural_contact_abs_deg':structural,'speaker_surface_gap_mm':distance(key,speaker)})
report['speaker_gap_at_first_structural_contact']={'nominal':gaps[0],'minimum_mm':min(r['speaker_surface_gap_mm'] for r in gaps),'rows':gaps,'method':'All vertex-to-triangle and all segment-to-segment distances on actual disjoint triangle solids, double precision. Normalized triangle approximation is CAD geometry only.'}
print('SPEAKER_GAP',gaps[0]['speaker_surface_gap_mm'],report['speaker_gap_at_first_structural_contact']['minimum_mm'],flush=True)
# Worst release placement: key XY clearance circle and bolt Xbacklash0.3,Yplay0.3,Zplay0.15.
biases=[(0,0)]+[(.339*math.cos(i*math.tau/16),.339*math.sin(i*math.tau/16)) for i in range(16)]
issues=[];count=0
for x,y in biases:
 for by,kz in itertools.product([-.3,.3],[-.3,.2]):
  for a in range(0,91,3):
   restore();offset(bolt,x=5.6,y=by,z=.15);keyangle(a,z=kz,x=x);key.matrix_world=Matrix.Translation(Vector((0,y*.001,0)))@key.matrix_world
   hits=checks([key],[bolt]);count+=1
   if hits:issues.append({'key_XY_mm':[x,y],'key_Z_mm':kz,'bolt_XYZ_mm':[5.6,by,.15],'angle_deg':a,'hits':hits})
report['combined_release']={'samples':count,'obstacles':issues,'estimated_radial_release_margin_mm':.1,'minimum_nominal_nose_X_engagement_under_assumed_slack_mm':1.961,'assumptions':'Key centre diskR0.339,Z-0.3..+0.2. BoltX-0.3,Y+/-0.3,Z+0.15. Key-body infeasible placements are conservatively included for bolt-only clearance. Dimensions are assumed, not measured tolerance.'}
print('COMBINED_RELEASE',count,len(issues),flush=True)
def empty():
 restore();offset(bolt,x=5.9);keyangle(90,-31)
 for o in unit:offset(o,z=100)
def tilt(o,axis,a,dx,dy,dz,pivot):
 P=Vector(pivot)*.001;T=Matrix.Translation(P)@Matrix.Rotation(math.radians(a),4,axis)@Matrix.Translation(-P)
 o.matrix_world=Matrix.Translation(Vector((dx,dy,dz))*.001)@T@base[o.name]
rows=[];valid=0;unexpected=[]
variants=[('X',0),('X',2),('X',-2),('Y',2),('Y',-2)]
for (ca,cv),(sa,sv),(dx,dy) in itertools.product(variants,variants,[(0,0),(.25,.25),(.25,-.25),(-.25,.25),(-.25,-.25)]):
 empty();tilt(cap,ca,cv,dx,dy,.25,(56.8,12.5,10.2));tilt(stop,sa,sv*1.5,-dx,-dy,.25,(56.8,12.5,5.0))
 h=checks([cap,stop],[body,bolt])+checks([cap],[stop]);row={'cap_tilt_axis_deg':[ca,cv],'stop_tilt_axis_deg':[sa,sv*1.5],'cap_XYZ_mm':[dx,dy,.25],'stop_XYZ_mm':[-dx,-dy,.25],'start_obstacles':h}
 if not h:
  valid+=1;homecap=cap.matrix_world.copy();homestop=stop.matrix_world.copy();blocked={}
  for label,obj,vec,maxdist in [('cap_X_exit',cap,(1,0,0),6.8),('cap_Z_exit',cap,(0,0,1),3.2),('stop_down_exit',stop,(0,0,-1),4)]:
   origin=obj.matrix_world.copy();found=None
   for i in range(1,int(maxdist*10)+1):
    obj.matrix_world=Matrix.Translation(Vector(vec)*i*.0001)@origin
    targets=[body,bolt,stop] if obj==cap else [body,cap]
    hit=checks([obj],targets)
    if hit:found={'distance_mm':i*.1,'hits':hit};break
   obj.matrix_world=origin;blocked[label]=found
   if found is None:unexpected.append({'pose':row,'path':label})
  row['extraction_barriers']=blocked;cap.matrix_world=homecap;stop.matrix_world=homestop
 rows.append(row)
report['cap_stop_combined']={'sampled_combined_start_poses':len(rows),'nonintersecting_start_poses':valid,'unblocked_directed_extractions':unexpected,'rows':rows,'scope':'CapX/Y tilt+/-2 degrees,stopX/Ytilt+/-3 degrees, opposingXY shifts+/-0.25mm,bothZ+0.25mm. Directed paths use0.1mm steps. Remaining compound escape paths not exhaustively proved.'}
report['thickness_and_failure']={'20_index_tab_mm':[2,2.4,1.6],'20_tab_root_cross_section_mm2':3.2,'22_each_index_foot_mm':[3.1,2.6,1.6],'22_foot_root_min_cross_section_mm2':4.16,'22_capture_ears_mm':[8.2,2.6,2.0],'21_base_mm':1.8,'T_root_width_mm':1.2,'T_lip_thickness_mm':2.4,'22_rotating_chamber_ceiling':'Body collarZ3.8..5.0 is1.2mm thick. Raised earsZ7.1..9.1 are0.2mm below cap21Z9.3. Base1.8mm; boss radial wall1.2mm.','if_index_tab_breaks':'20 may slide after load/unintended lift;22 may rotate and permit cap21 removal after axial push. Do not use damaged parts; cracked tabs invalidate retention. Remaining opposed ears provide nominal axial bearing only until deliberate rotation aligns them. No single failure safety or vibration qualification.'}
(R/'combined_slack_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('COMBINED_CAP_STOP',len(rows),valid,len(unexpected),flush=True)
