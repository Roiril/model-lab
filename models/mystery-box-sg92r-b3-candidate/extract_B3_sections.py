"""Plane sections of actual source triangles for the Japanese guide."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
import bpy
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_B3.blend'))
objects=[bpy.data.objects[n] for n in ['01_body','13_body_cross_key','20_short_body_bolt','21_separate_bolt_cap','22_symmetric_cap_stop']]
def sections(y):
 data={}
 for o in objects:
  o.data.calc_loop_triangles();segments=[]
  for t in o.data.loop_triangles:
   ps=[o.matrix_world@o.data.vertices[i].co*1000 for i in t.vertices];out=[]
   for a,b in zip(ps,ps[1:]+ps[:1]):
    da,db=a.y-y,b.y-y
    if abs(da)<1e-6:out.append((a.x,a.z))
    if da*db<0:
     c=a+(b-a)*da/(da-db);out.append((c.x,c.z))
   out=list(dict.fromkeys(tuple(round(x,4) for x in q) for q in out))
   if len(out)==2 and sum((out[0][k]-out[1][k])**2 for k in range(2))>1e-8:segments.append(out)
  data[o.name]=segments
 return data
(R/'actual_sections.json').write_text(json.dumps({'source_blend_sha256':hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),'units':'mm','plane_sections':{str(y):sections(y) for y in [12.5,26.5]},'physical_tested':False},indent=2),encoding='utf8');print('B3 ACTUAL SECTIONS SAVED',flush=True)
