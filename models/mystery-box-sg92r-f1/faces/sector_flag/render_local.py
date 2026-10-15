"""Diagnostic views of the exact checked solids; outputs only below this face."""
import sys
sys.dont_write_bytecode=True
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('sector_local_check',Path(__file__).with_name('check_local.py'))
C=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)
import bpy
import json
from mathutils import Vector,Matrix
from sector_flag_local.evidence import require_meshes

require_meshes(C.HERE)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
manifest=json.loads((C.HERE/'module.json').read_text(encoding='utf-8'))
objects={}
for p in manifest['parts']:
    bpy.ops.wm.stl_import(filepath=str(C.HERE/'_local'/(p+'.stl')))
    ob=bpy.context.object; ob.name=p; objects[p]=ob
    ob.color=(.8,.14,.35,1) if p in ('servo','horn','input_gear','sector_gear','hinge_pin') else (.5,.7,.8,1) if p in ('servo_cap','bearing_bridge') else (.8,.8,.76,1)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.color_type='OBJECT'
scene.display.shading.light='STUDIO'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.background_type='WORLD'
scene.world.color=(.08,.08,.08)
scene.render.resolution_x=900; scene.render.resolution_y=900; scene.render.resolution_percentage=100
data=bpy.data.cameras.new('diagnostic'); cam=bpy.data.objects.new('diagnostic',data)
scene.collection.objects.link(cam); scene.camera=cam; data.type='ORTHO'; data.ortho_scale=105; data.clip_end=1000
for angle in (60,90,120):
    mats=C.K.transforms(angle)
    for p,ob in objects.items(): ob.matrix_world=Matrix(mats[p])
    for name,eye in (('front',(0,0,-150)),('oblique',(70,-50,-150))):
        eye=Vector(eye); z=eye.normalized(); x=Vector((0,-1,0)).cross(z).normalized(); y=z.cross(x)
        cam.matrix_world=Matrix(((x.x,y.x,z.x,eye.x),(x.y,y.y,z.y,eye.y),(x.z,y.z,z.z,eye.z),(0,0,0,1)))
        scene.render.filepath=str(C.HERE/'_local'/('view_'+str(angle)+'_'+name+'.png'))
        bpy.ops.render.render(write_still=True)
