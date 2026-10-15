"""Headless product views from the exact assembly meshes."""
from pathlib import Path
import math
import bpy
from mathutils import Vector, Matrix
HERE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(HERE/'build'/'flag-box.blend'))
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.background_type='WORLD'
scene.world.color=(0.85,0.85,0.85)
scene.render.resolution_x=1100
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
camdata=bpy.data.cameras.new('camera')
cam=bpy.data.objects.new('camera',camdata)
scene.collection.objects.link(cam)
scene.camera=cam
camdata.type='ORTHO'
camdata.ortho_scale=125
camdata.clip_end=2000
def shot(name,angle=0,exploded=False,cut=False):
    for ob in scene.objects:
        if ob.type=='MESH':
            ob.matrix_world=Matrix.Identity(4)
            ob.hide_render=False
    turn=Matrix.Translation((0,-8,48))@Matrix.Rotation(math.radians(angle),4,'X')@Matrix.Translation((0,8,-48))
    for name2 in ('horn','flag','bearing_button'):
        bpy.data.objects[name2].matrix_world=turn
    if exploded:
        bpy.data.objects['roof'].location.z=45
        bpy.data.objects['flag'].location.x=20
        bpy.data.objects['bearing_button'].location.x=35
        camdata.ortho_scale=220
    else:
        camdata.ortho_scale=165
    if cut:
        bpy.data.objects['box'].hide_render=True
        bpy.data.objects['roof'].hide_render=True
    target=Vector((0,0,48 if not exploded else 62))
    cam.location=target+Vector((140,-180,135))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(HERE/'build'/f'{name}.png')
    bpy.ops.render.render(write_still=True)
shot('closed')
shot('open',90)
shot('inside',45,cut=True)
shot('exploded',exploded=True)
