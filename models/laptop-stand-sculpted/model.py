"""A smooth solid from independent silhouette and window contours.

The Poisson field creates a continuous transverse thickness. A separately
swept flat rail has an upward retaining nose. Headless builds stay isolated.
"""
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(HERE))
import bpy
import bmesh
import numpy as np
from blender_utils import clear_scene, export_stl
from params import *


def mesh_object(name, vertices, faces, smooth=True):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-8)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = smooth
    return obj


def boolean(obj, cutter, operation):
    bpy.context.view_layer.objects.active=obj
    modifier=obj.modifiers.new(operation,"BOOLEAN")
    modifier.solver="EXACT"
    modifier.operation=operation
    modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter,do_unlink=True)


def triangulate(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method="BEAUTY",ngon_method="BEAUTY")
    bm.to_mesh(obj.data);bm.free()


def rail():
    """Sweep rounded rectangle; last 17mm rises smoothly into the nose."""
    n,m=280,48
    ys=np.linspace(RAIL_START,RAIL_END,n)
    vertices=[]
    for y in ys:
        t=np.clip((y-(RAIL_END-0.017))/0.017,0,1)
        lift=LIP_HEIGHT*(3*t*t-2*t*t*t)
        edge=min(y-RAIL_START,RAIL_END-y)
        # Rounded ends in plan, independent from the edge bevel.
        cap_radius=0.010
        width=RAIL_HALF_WIDTH-cap_radius+np.sqrt(max(0,cap_radius**2-max(0,cap_radius-edge)**2))
        for a in np.arange(m)*2*np.pi/m:
            ca,sa=np.cos(a),np.sin(a)
            vertices.append((width*np.sign(ca)*abs(ca)**(1/3),y,
                             RAIL_HEIGHT-RAIL_HALF_THICKNESS+lift+
                             RAIL_HALF_THICKNESS*np.sign(sa)*abs(sa)**(1/3)))
    faces=[]
    for u in range(n-1):
        for v in range(m):
            faces.append((u*m+v,(u+1)*m+v,(u+1)*m+(v+1)%m,u*m+(v+1)%m))
    faces += [tuple(range(m-1,-1,-1)),tuple((n-1)*m+v for v in range(m))]
    return mesh_object("contact_rail",vertices,faces)


def check(obj):
    bm=bmesh.new(); bm.from_mesh(obj.data)
    bad=sum(not e.is_manifold for e in bm.edges)
    if bad:
        print('BAD_EDGES', [[list(v.co) for v in e.verts] for e in bm.edges if not e.is_manifold])
    volume=bm.calc_volume(signed=True)
    points=np.array([v.co[:] for v in bm.verts])
    report={"vertices":len(bm.verts),"faces":len(bm.faces),"non_manifold_edges":bad,
            "volume_cm3":volume*1e6,"dimensions_mm":((points.max(0)-points.min(0))*1000).tolist(),
            "bounds_mm":[(points.min(0)*1000).tolist(),(points.max(0)*1000).tolist()]}
    bm.free()
    if bad or volume<=0:
        raise RuntimeError(f"Invalid sculpted solid: {report}")
    return report


def main():
    clear_scene()
    from poisson_body import build
    verts,quads,field_report=build()
    body=mesh_object("continuous_sculpture",verts.tolist(),quads.tolist())
    triangulate(body)
    bpy.context.view_layer.objects.active=body
    reduce=body.modifiers.new('bounded_simplification','DECIMATE')
    reduce.ratio=0.14
    bpy.ops.object.modifier_apply(modifier=reduce.name)
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    points=[v.co[:] for v in body.data.vertices]
    faces=[list(p.vertices) for p in body.data.polygons]
    tree=BVHTree.FromPolygons(points,faces,all_triangles=True)
    deviation=[tree.find_nearest(Vector(v))[3]*1000 for v in verts[::max(1,len(verts)//12000)]]
    field_report['simplification_max_sampled_deviation_mm']=max(deviation)
    assert max(deviation)<0.35
    for v in body.data.vertices:
        if v.co.z<.000002:v.co.z=0
    # Flatten only a small hidden rail seat, with overlap for stable union.
    contact=rail()
    triangulate(contact)
    boolean(body,contact,"UNION")
    body.name="sculpted_leg"
    bpy.context.view_layer.update()
    report=check(body)
    report["thickness_field"]=field_report
    out=ROOT/"exports"/MODEL_NAME
    out.mkdir(parents=True,exist_ok=True)
    (out/"build.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    export_stl(MODEL_NAME+"-unit",only=[body])
    body.location.x=-PAIR_SPACING/2
    other=body.copy();other.data=body.data.copy()
    bpy.context.collection.objects.link(other)
    other.location.x=PAIR_SPACING/2
    other.name="sculpted_leg_right"
    export_stl(MODEL_NAME,only=[body,other])
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
