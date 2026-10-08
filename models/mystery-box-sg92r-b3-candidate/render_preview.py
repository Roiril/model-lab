import bpy,sys,pathlib,math,json
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));import params as p
from cad_utils import pivot_transform
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_B3.blend'))
D=json.loads((R/'assembly_manifest.json').read_text(encoding='utf8'))
O=Vector(D['O']);H=Vector(D['H']);uv=Vector(D['rocker_local_mm']);r=D['crank_r_mm'];L=D['link_length_mm'];theta0=math.radians(D['servo_range_deg'][0]);A0=O+r*Vector((math.cos(theta0),math.sin(theta0)));B0=H+uv
groups={x['name']:x['group'] for x in D['parts']};closed={o.name:o.matrix_world.copy() for o in bpy.data.objects};neutral={o.name:pivot_transform(*O,theta0).inverted()@closed[o.name] if groups.get(o.name)=='crank' or o.name.endswith('horn') else closed[o.name] for o in bpy.data.objects}
def setpose(deg):
 t=math.radians(deg);B=H+Vector((uv.x*math.cos(t)-uv.y*math.sin(t),uv.x*math.sin(t)+uv.y*math.cos(t)));d=B-O;th=math.atan2(d.y,d.x)-math.acos((d.length**2+r*r-L*L)/(2*d.length*r));A=O+r*Vector((math.cos(th),math.sin(th)))
 for o in list(bpy.data.objects):
  if o.name not in neutral:continue
  g=groups.get(o.name)
  if g=='lid':o.matrix_world=pivot_transform(*H,t)@neutral[o.name]
  elif g=='crank' or o.name.endswith('horn'):o.matrix_world=pivot_transform(*O,th)@neutral[o.name]
  elif g=='link':
   a=math.atan2((B-A).y,(B-A).x)-math.atan2((B0-A0).y,(B0-A0).x)
   o.matrix_world=Matrix.Translation(Vector((0,*A))*.001)@Matrix.Rotation(a,4,'X')@Matrix.Translation(Vector((0,*(-A0)))*.001)@neutral[o.name]
  else:o.matrix_world=neutral[o.name]
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_object_outline=True;scene.display.shading.background_type='WORLD';scene.world.color=(.90,.92,.94)
scene.render.image_settings.file_format='PNG';scene.render.image_settings.compression=100;scene.render.dither_intensity=0;scene.render.film_transparent=False
camdata=bpy.data.cameras.new('Preview camera');cam=bpy.data.objects.new('Preview camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO'
def camera(pos,target,scale):
 cam.location=Vector(pos)*.001;cam.rotation_euler=(Vector(target)*.001-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale*.001
def render(filename):scene.render.filepath=str(R/filename);bpy.ops.render.render(write_still=True)
setpose(0);camera((155,-125,130),(35,35,35),150);render('preview_closed.png')
from bpy_extras.object_utils import world_to_camera_view
points={'width_start':(0,-6,-4),'width_end':(70,-6,-4),'depth_start':(76,0,-4),'depth_end':(76,70,-4),'height_start':(76,76,0),'height_end':(76,76,70)}
projected={}
for key,point in points.items():
 v=world_to_camera_view(scene,cam,Vector(point)*.001);projected[key]=[v.x*1500,(1-v.y)*1100]
(R/'camera_projected_dimensions.json').write_text(json.dumps(projected,indent=2),encoding='utf8')
setpose(65);camera((162,-128,140),(35,32,55),200);render('preview_open65.png')
# Internal engineering view: hide shell and front plate; assembled geometry retained.
for n in ('01_body','03_planar_lid','02_fixed_rear_cover','05_front_closure'):bpy.data.objects[n].hide_render=True
camera((168,-95,114),(35,32,49),142);render('preview_mechanism65.png')
setpose(0);camera((160,35,35),(35,35,35),118);render('preview_side_mechanism0.png')
print('rendered4views',flush=True)
