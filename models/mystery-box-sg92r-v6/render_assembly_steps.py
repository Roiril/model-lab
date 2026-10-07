"""Actual CAD-only bench assembly stages, no reference servo in manual test."""
import bpy,pathlib,sys,math,json
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_object_outline=True;scene.display.shading.background_type='WORLD';scene.world.color=(.93,.94,.96);scene.render.image_settings.file_format='PNG';scene.render.image_settings.compression=100;scene.render.dither_intensity=0
d=bpy.data.cameras.new('Assembly camera');cam=bpy.data.objects.new('Assembly camera',d);bpy.context.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO';d.ortho_scale=.155
cam.location=Vector((180,-65,112))*.001;cam.rotation_euler=(Vector((35,35,43))*.001-cam.location).to_track_quat('-Z','Y').to_euler()
stages=[('step_01_rear_frame.png',['04','15','16']),('step_02_local_capture.png',['04','06','14','15','16','17','18','19']),('step_03_lid_front_entry.png',['03','04','06','07','09','10','11','12','14','15','16','17','18','19']),('step_04_complete_cassette.png',[f'{i:02d}' for i in range(2,20) if i!=13]),('step_05_manual_box.png',[f'{i:02d}' for i in range(1,20)])]
home={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type=='MESH'}
for filename,visible in stages:
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  o.hide_render=o.name[:2] not in visible;o.matrix_world=home[o.name]
 if filename=='step_03_lid_front_entry.png':bpy.data.objects['03_planar_lid'].location.y+=.016
 scene.render.filepath=str(R/filename);bpy.ops.render.render(write_still=True)
print('Actual assembly5stages rendered',flush=True)
