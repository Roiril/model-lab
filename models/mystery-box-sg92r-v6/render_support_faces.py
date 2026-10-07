"""Actual print STL surfaces, colored by the3MF support paint rule."""
import pathlib,sys,bpy,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));from cad_utils import read_stl,color
for name,plane in [('04_main_cassette',27.3),('06_horn_cup_journal',11.5)]:
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 o=read_stl(R/'stl'/(name+'.stl'),name);color(o,'Protected surfaces',(.61,.65,.69))
 red=bpy.data.materials.new('Allowed manual support only');red.diffuse_color=(.86,.21,.12,1);o.data.materials.append(red)
 for face in o.data.polygons:
  v=[o.data.vertices[i].co for i in face.vertices];n=(v[1]-v[0]).cross(v[2]-v[0]).normalized()
  if n.z<-.9 and all(abs(p.z*1000-plane)<.001 for p in v):face.material_index=1
 s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_object_outline=True;s.display.shading.background_type='WORLD';s.world.color=(.93,.94,.96);s.render.image_settings.file_format='PNG';s.render.image_settings.compression=100;s.render.dither_intensity=0
 d=bpy.data.cameras.new('Support review camera');c=bpy.data.objects.new('Support review camera',d);bpy.context.collection.objects.link(c);s.camera=c;d.type='ORTHO';d.ortho_scale=.096 if name.startswith('04') else .067
 d.clip_start=.001;d.clip_end=10.;s.display.shading.light='FLAT'
 target=Vector((34,34,27.3) if name.startswith('04') else (16,18,12))*.001;c.location=Vector((-90,34,7) if name.startswith('04') else (68,-45,-28))*.001;c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/('support_'+name[:2]+'_actual.png'));bpy.ops.render.render(write_still=True)
 print('Painted actual face count',name,sum(f.material_index==1 for f in o.data.polygons),flush=True)
