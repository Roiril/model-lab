"""Actual current bottom/local views plus clearly assumed bench supports."""
from pathlib import Path
import sys,json,math,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
from cad_utils import cube,boolean,color
def setup():
 bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_B3.blend'))
 scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
 scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_object_outline=True;scene.display.shading.background_type='WORLD';scene.world.color=(.94,.96,.97)
 camdata=bpy.data.cameras.new('service view');cam=bpy.data.objects.new('service view',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.clip_start=.001;camdata.clip_end=5
 return scene,cam,camdata
def view(scene,cam,data,pos,target,scale,name):
 cam.location=Vector(pos)*.001;cam.rotation_euler=(Vector(target)*.001-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale*.001;scene.render.filepath=str(R/name);bpy.ops.render.render(write_still=True)
scene,cam,data=setup();view(scene,cam,data,(35,35,-150),(35,35,0),90,'preview_bottom.png')
scene,cam,data=setup();keep=['01_body','13_body_cross_key','20_short_body_bolt','21_separate_bolt_cap','22_symmetric_cap_stop']
for o in list(bpy.data.objects):
 if o.type=='MESH' and o.name not in keep:bpy.data.objects.remove(o,do_unlink=True)
boolean(bpy.data.objects['01_body'],cube('display crop',(28,6,-.1),(64,34,19)),'INTERSECT')
view(scene,cam,data,(100,-50,75),(38,22,8),68,'preview_local.png')
scene,cam,data=setup()
for n,lo,hi in [('assumed left bench block',(-77,-15,-100),(3,85,0)),('assumed right bench block',(67,-15,-100),(147,85,0))]:color(cube(n,lo,hi),'Assumed bench support',(.68,.67,.59))
view(scene,cam,data,(200,-240,170),(35,35,-30),310,'preview_support.png')
(R/'service_render_record.json').write_text(json.dumps({'source_blend_sha256':hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),'display_only_local_crop_mm':[[28,6,-.1],[64,34,19]],'bench_supports_assumed_not_print_parts':True,'source_assembly_unmodified':True},indent=2),encoding='utf8')
