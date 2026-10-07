"""2mm L-hook envelopes at65deg lid opening. No finger/force validation."""
import pathlib,sys,bpy,hashlib,json
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
# Reuse the independently-run motion setup/state/intersection helpers only.
code=(R/'verify_motion.py').read_text(encoding='utf8').split("result={'angle_step_deg'")[0]
exec(compile(code,'motion_helpers','exec'),globals());state(65)
from cad_utils import cyl,add
tools=[]
for name,a,b,stem in [('rear lift hook',3.8,15.8,14.8),('front lift hook',50.,62.,51.)]:
 o=cyl(name,((a+b)/2,61.5,59.5),1.,b-a);add(o,cyl('vertical handle',(stem,61.5,73.75),1.,28.5,'Z'));tools.append(o)
fixed=[o for o in objs+ghost if o.name!='13_body_cross_key'];home={o.name:o.matrix_world.copy() for o in tools};rows=[]
for tool,direction in zip(tools,[1,-1]):
 issues=[]
 for i in range(41):
  dist=20-i*.5;tool.matrix_world=Matrix.Translation(Vector((direction*dist*.001,0,0)))@home[tool.name];tt=tree(tool)
  for ob in fixed:
   if not tt.overlap(tree(ob)):continue
   v=volume_intersection(tool,ob);bounds=v['bounds_mm'];flat=not bounds or min(bounds[1][k]-bounds[0][k] for k in range(3))<.00005
   if not flat and (v['volume_mm3']>.005 or v['nonmanifold_edges']):issues.append({'distance_mm':dist,'fixed':ob.name,**v})
 tool.matrix_world=home[tool.name];rows.append({'tool':tool.name,'horizontal_insertion_samples':41,'obstacles':issues})
report={'input_blend_sha256':hashlib.sha256((R/'editable_cube_v6.blend').read_bytes()).hexdigest(),'physical_tested':False,'tool_diameter_mm':2.,'service_hole_yz_mm':[61.5,59.5],'service_hole_diamond_diagonal_mm':5.,'lid_angle_deg':65,'paths':rows,'scope':'Conservative cylinders for2mm L hooks with28.5mm straight handles and12mm short legs. Horizontal insertion sampled0.5mm. A real Allen-key bend/handle, grip strength and simultaneous human access remain untested. Use both plates, support the lid and lift gently; do not lift by linkage or planar lid.'}
(R/'tool_access_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('LIFT HOOK',[(r['tool'],len(r['obstacles'])) for r in rows],flush=True)
