"""Actual CAD section along the servo axis; references have no spline teeth."""
import bpy,bmesh,pathlib
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
for o in list(bpy.data.objects):
    if o.type!='MESH':continue
    for v in o.data.vertices:v.co=o.matrix_world@v.co
    o.matrix_world=Matrix.Identity(4);bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,.040,0),plane_no=(0,1,0),clear_inner=True,clear_outer=False,dist=1e-8)
    edges=[e for e in bm.edges if e.is_boundary];bmesh.ops.holes_fill(bm,edges=edges,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1800;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_object_outline=True;s.display.shading.background_type='WORLD';s.world.color=(.92,.94,.96);s.render.image_settings.file_format='PNG'
d=bpy.data.cameras.new('Capture section camera');c=bpy.data.objects.new('Capture section camera',d);bpy.context.collection.objects.link(c);s.camera=c;d.type='ORTHO';d.ortho_scale=.138
c.location=Vector((35,-150,35))*.001;c.rotation_euler=(Vector((35,40,35))*.001-c.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(R/'capture_axis_actual_section.png');bpy.ops.render.render(write_still=True)
print('Actual axial section Y40 rendered')
