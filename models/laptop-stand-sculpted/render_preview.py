"""Render exported geometry, without editing or relying on a live Blender."""
import sys
import math
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/"exports"/"laptop-stand-sculpted"


def material(name,color,roughness=0.8):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=roughness
    return m


def setup(pair=False,photographic=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    bpy.ops.wm.stl_import(filepath=str(ROOT/"exports"/("laptop-stand-sculpted"+("" if pair else "-unit")+".stl")))
    obj=bpy.context.object;obj.scale=(.001,)*3
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    # STL carries independent triangle vertices; weld before smooth shading.
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
    bm.to_mesh(obj.data);bm.free()
    if obj.data.has_custom_normals:
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    for p in obj.data.polygons:p.use_smooth=True
    obj.data.materials.append(material("ivory",(.68,.64,.56)))
    scene.render.engine="BLENDER_EEVEE" if photographic else "BLENDER_WORKBENCH"
    scene.render.film_transparent=not photographic
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGBA"
    scene.view_settings.view_transform="AgX" if photographic else "Standard"
    if photographic:
        scene.world=bpy.data.worlds.new("studio")
        scene.world.use_nodes=True
        scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.36,.34,.30,1)
        scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.7
        bpy.ops.mesh.primitive_plane_add(size=200,location=(0,.12,-.00015))
        bpy.context.object.data.materials.append(material("floor",(.42,.40,.37)))
        for name,pos,energy,size in [("key",(-.3,-.2,.7),24,.55),("fill",(.5,.35,.6),16,.6),
                                     ("rim",(-.5,.6,.5),10,.6)]:
            data=bpy.data.lights.new(name,"AREA");data.energy=energy;data.size=size
            light=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(light)
            light.location=pos
            light.rotation_euler=(Vector((0,.12,.07))-light.location).to_track_quat("-Z","Y").to_euler()
    else:
        sh=scene.display.shading
        sh.light="STUDIO";sh.studiolight_rotate_z=.6
        sh.color_type="SINGLE";sh.single_color=(.72,.69,.63)
        sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type="BOTH"
    return obj


def shoot(name,azimuth,elevation,scale=.33,width=1200,height=1100,pair=False):
    target=Vector((0,.125,.073))
    az,el=math.radians(azimuth),math.radians(elevation)
    camdata=bpy.data.cameras.new(name);camdata.type="ORTHO";camdata.ortho_scale=scale
    cam=bpy.data.objects.new(name,camdata);bpy.context.collection.objects.link(cam)
    cam.location=target+Vector((math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)))*1.5
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    scene=bpy.context.scene;scene.camera=cam
    scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(OUT/(name+".png"))
    bpy.ops.render.render(write_still=True)


def main():
    mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "quick"
    if mode=="quick":
        setup();shoot("iso",54,12)
        shoot("side",0,0,.35,1300,900)
        shoot("top",0,90,.46,1300,900)
        shoot("reverse",180+40,20)
        shoot("front",90,0,.19,900,1000)
    else:
        setup(photographic=True);shoot("studio-unit",54,12)
        setup(pair=True,photographic=True);shoot("studio-pair",35,18,.46,1500,1100,pair=True)


if __name__=="__main__":main()
