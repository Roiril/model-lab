"""Images of actual print meshes; colored faces are removable-support lands only."""
from pathlib import Path
import sys, math, json, hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
import bpy
from mathutils import Vector
from cad_utils import read_stl
records=[]
for number,name in [('04','04_main_cassette'),('06','06_horn_cup_journal')]:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 o=read_stl(R/'stl'/(name+'.stl'),name)
 mats=[]
 for label,col in [('protected',(.56,.60,.64,1)),('support underside',(.98,.55,.12,1)),('recess landing',(.08,.57,.65,1))]:
  m=bpy.data.materials.new(label);m.diffuse_color=col;o.data.materials.append(m);mats.append(m)
 for f in o.data.polygons:
  v=[o.matrix_world@o.data.vertices[i].co*1000 for i in f.vertices];c=sum(v,Vector())/len(v);z=[p.z for p in v]
  if number=='04':
   if all(abs(x-27.3)<.001 for x in z):f.material_index=1
   wy=c.y+5.4;wz=67.3-c.x
   if all(abs(x-2.7)<.001 for x in z) and 24.499<wy<55.501 and 26.999<wz<41.001:f.material_index=2
   if all(abs(x-8.4)<.001 for x in z) and 46.799<wy<51.301 and 30.999<wz<43.301:f.material_index=2
   if all(abs(x-5.)<.001 for x in z) and 46.799<wy<51.301 and 26.999<wz<41.001:f.material_index=2
  elif all(abs(x-11.5)<.001 for x in z):f.material_index=1
 scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=900
 scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_object_outline=True;scene.display.shading.background_type='WORLD';scene.world.color=(.96,.97,.98)
 vv=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector([min(p[i] for p in vv) for i in range(3)]);hi=Vector([max(p[i] for p in vv) for i in range(3)]);target=(lo+hi)/2
 camdata=bpy.data.cameras.new('support');cam=bpy.data.objects.new('support',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=max(hi-lo)*2.;camdata.clip_start=.001;camdata.clip_end=5
 for view,offset in [('under',(-80,90,-90)),('top',(-80,90,110))]:
  cam.location=target+Vector(offset)*.001;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(R/('support_'+number+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
 records.append({'name':name,'stl_sha256':hashlib.sha256((R/'stl'/(name+'.stl')).read_bytes()).hexdigest(),'display_only':True,'marked_polygons':{str(i):sum(f.material_index==i for f in o.data.polygons) for i in range(3)}})
(R/'support_face_images.json').write_text(json.dumps(records,indent=2),encoding='utf8')
