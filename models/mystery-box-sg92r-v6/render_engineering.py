"""Actual CAD section/exploded views and actual arranged mesh plate views."""
import bpy,bmesh,pathlib,sys,json,math
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));from cad_utils import read_stl,color
def setup(w=1500,h=1100):
    s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100
    s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_object_outline=True;s.display.shading.background_type='WORLD';s.world.color=(.92,.94,.96);s.render.image_settings.file_format='PNG';s.render.image_settings.compression=100;s.render.dither_intensity=0
    d=bpy.data.cameras.new('Engineering camera');o=bpy.data.objects.new('Engineering camera',d);bpy.context.collection.objects.link(o);s.camera=o;d.type='ORTHO';return s,o
def render(s,cam,path,pos,target,scale):
    cam.location=Vector(pos)*.001;cam.rotation_euler=(Vector(target)*.001-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale*.001;s.render.filepath=str(R/path);bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'));s,cam=setup()
cutmat=bpy.data.materials.new('True section faces');cutmat.diffuse_color=(.78,.19,.13,1)
for o in list(bpy.data.objects):
    if o.type!='MESH':continue
    # Apply saved assembled transform, then truly remove X>49.8 mm and cap it.
    for v in o.data.vertices:v.co=o.matrix_world@v.co
    o.matrix_world=Matrix.Identity(4);bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(.0498,0,0),plane_no=(1,0,0),clear_outer=True,clear_inner=False,dist=1e-8)
    boundary=[e for e in bm.edges if e.is_boundary];new=bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    o.data.materials.append(cutmat);index=len(o.data.materials)-1
    for f in new['faces']:f.material_index=index
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
render(s,cam,'section_actual3d.png',(190,-55,125),(29,35,35),148)
render(s,cam,'section_side_actual3d.png',(180,35,36),(30,35,36),116)
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'));s,cam=setup(1900,1400)
offset={'01_body':(0,0,-65),'02_fixed_rear_cover':(0,0,55),'03_planar_lid':(0,20,86),'04_main_cassette':(-35,0,0),'05_front_closure':(105,0,0),'06_horn_cup_journal':(15,0,-15),'07_rear_rocker':(20,0,27),'08_front_rocker':(60,0,27),'09_link':(50,0,-7),'10_hinge_axle':(95,0,50),'11_drive_axle':(95,0,-25),'12_link_axle':(95,0,20),'13_body_cross_key':(40,0,-58),'14_servo_top_keeper':(-15,-40,55),'15_flat_spacer':(-15,-35,-20),'16_flat_spacer':(-15,40,-20),'17_local_cup_capture':(50,0,-40),'18_local_capture_stop':(85,-25,-55),'19_local_capture_stop':(85,25,-55)}
for n,delta in offset.items():bpy.data.objects[n].matrix_world.translation+=Vector(delta)*.001
for o in bpy.data.objects:
    if o.name.startswith('REFERENCE'):o.hide_render=True
render(s,cam,'exploded_actual3d.png',(310,-210,230),(55,35,48),395)
plate=json.loads((R/'plate_manifest.json').read_text())
for row in plate:
    for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
    s,cam=setup(1200,1200)
    for i,part in enumerate(row['parts']):
        folder='coupons' if part['name'].startswith('test_') else 'stl'
        o=read_stl(R/folder/(part['name']+'.stl'),part['name']);o.location=Vector((*part['position_mm'],0))*.001
        color(o,'Plate '+str(i),(.25,.5,.63) if not part['name'].startswith('0') else (.75,.61,.3))
        d=bpy.data.curves.new('label','FONT');d.body=part['name'].split('_')[1] if part['name'].startswith('test_') else part['name'][:2];d.size=.0045
        t=bpy.data.objects.new('label',d);bpy.context.collection.objects.link(t);t.location=Vector((part['position_mm'][0]+1,part['position_mm'][1]-5,.001))*.001;color(o,'Plate '+str(i),(.25,.5,.63))
    render(s,cam,row['plate']+'_preview.png',(100,100,300),(100,100,0),220)
print('ENGINEERING VIEWS DONE',flush=True)
