"""Reserved terminal and lead volumes, provisional until actual speaker chosen."""
from pathlib import Path
import sys,math,json,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
from cad_utils import cube,add,color
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_B3.blend'))
for o in list(bpy.data.objects):
 if o.name.startswith('REFERENCE speaker'):bpy.data.objects.remove(o,do_unlink=True)
terminal=cube('REFERENCE speaker terminals',(14,57.5,7.5),(20,61.5,10.5));color(terminal,'Speaker reserved',(.45,.3,.6))
P=[Vector(v) for v in [(17,60,9.5),(25,60,9.5),(33,62.5,14),(41,62.5,14)]]
def curve(t):return (1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t*t*P[2]+t**3*P[3]
pts=[curve(i/24) for i in range(25)];minr=1e20
for i in range(25):
 t=i/24;d=3*((1-t)**2*(P[1]-P[0])+2*(1-t)*t*(P[2]-P[1])+t*t*(P[3]-P[2]));dd=6*((1-t)*(P[2]-2*P[1]+P[0])+t*(P[3]-2*P[2]+P[1]));cross=d.cross(dd).length
 if cross>1e-8:minr=min(minr,d.length**3/cross)
for i,(a,b) in enumerate(zip(pts,pts[1:])):
 v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.0011,depth=v.length*.001,location=(a+b)*.0005)
 o=bpy.context.object;o.name=f'REFERENCE speaker lead {i:02}';o.rotation_euler=v.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 for pt in [a,b]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.0011,location=pt*.001);add(o,bpy.context.object)
 color(o,'Speaker reserved',(.45,.3,.6))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'editable_cube_B3.blend'))
(R/'speaker_envelope_definition.json').write_text(json.dumps({'speaker_DH_mm':[25,10],'terminal_bounds_mm':[[14,57.5,7.5],[20,61.5,10.5]],'lead_design_nominal_D_mm':2,'checked_envelope_D_mm':2.2,'bezier_controls_mm':[list(v) for v in P],'minimum_sampled_centerline_bend_radius_mm':minr,'segments':24,'source_blend_sha256':hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),'reserved_space_only':True,'physical_speaker_measured':False,'note':'Speaker remains mounted/located per selected hardware later. Connector and external D3R6 exit checked separately. Unplug power and leads before unit service.'},indent=2),encoding='utf8')
print('SPEAKER ENVELOPES',minr,flush=True)
