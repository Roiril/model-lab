"""Verify exported triangles and surface construction independently."""
import sys
import struct
import json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def parse_stl(path):
    raw=path.read_bytes()
    n=struct.unpack_from("<I",raw,80)[0]
    assert len(raw)==84+50*n, "STL byte count mismatch"
    dtype=np.dtype([("normal","<f4",(3,)),("vertices","<f4",(3,3)),("attribute","<u2")])
    rows=np.frombuffer(raw,offset=84,count=n,dtype=dtype)
    vertices,inverse=np.unique(rows["vertices"].reshape(-1,3),axis=0,return_inverse=True)
    return vertices.astype(float),inverse.reshape(-1,3)


def topology(v,f):
    edges=np.sort(np.concatenate((f[:,[0,1]],f[:,[1,2]],f[:,[2,0]])),axis=1)
    unique,count=np.unique(edges,axis=0,return_counts=True)
    parent=np.arange(len(v))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    for a,b in unique:
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    components=len(set(find(i) for i in range(len(v))))
    a,b,c=v[f[:,0]],v[f[:,1]],v[f[:,2]]
    volume=np.einsum("ij,ij->i",a,np.cross(b,c)).sum()/6
    area=np.linalg.norm(np.cross(b-a,c-a),axis=1)/2
    return {"triangles":len(f),"vertices":len(v),"components":components,
            "non_manifold_edges":int((count!=2).sum()),"zero_area_triangles":int((area<1e-12).sum()),
            "volume_cm3":float(volume/1000),"dimensions_mm":(v.max(0)-v.min(0)).tolist(),
            "bottom_min_mm":float(v[:,2].min()),"bottom_contact_area_mm2":float(area[np.all(np.abs(v[f,2])<1e-6,axis=1)].sum())}


def surface_checks():
    # Run within Blender for the analytic parameter surface and BVH intersections.
    import bpy
    import bmesh
    from mathutils.bvhtree import BVHTree
    def disjoint_crossings(vertices,faces):
        array=np.asarray(vertices)
        tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True,epsilon=0)
        pairs=tree.overlap(tree)
        candidates=[]
        for a,b in pairs:
            if a>=b or set(faces[a]).intersection(faces[b]):continue
            aa,bb=array[list(faces[a])],array[list(faces[b])]
            depths=[]
            for p,q in [(aa,bb),(bb,aa)]:
                normal=np.cross(p[1]-p[0],p[2]-p[0])
                normal/=np.linalg.norm(normal)
                distance=(q-p[0])@normal
                depths.append(max(0,min(distance.max(),-distance.min())))
            candidates.append(float(min(depths)))
        # BVH runs in float32. Retest plane straddling in float64 at 1 micron.
        return {"bvh_candidates":len(candidates),"above_1_micron":sum(d>1e-6 for d in candidates),
                "max_straddle_depth_mm":max(candidates,default=0)*1000}
    normal=disjoint_crossings([(0,0,0),(1,0,0),(0,1,0),(0,0,1)],[(0,2,1),(0,1,3),(1,2,3),(2,0,3)])
    bad=disjoint_crossings([(-1,-1,0),(1,-1,0),(0,1,0),(0,-.5,-1),(0,-.5,1),(0,.5,0)],[(0,1,2),(3,4,5)])
    assert normal["above_1_micron"]==0 and bad["above_1_micron"]>0, "Intersection detector calibration failed"
    v,f=parse_stl(ROOT/"exports/laptop-stand-sculpted-unit.stl")
    intersections=disjoint_crossings((v/1000).tolist(),f.tolist())
    result={"intersection_calibration":{"normal":normal,"crossing":bad},
            "intersection_check":intersections}
    print("SURFACE",json.dumps(result))
    assert intersections["above_1_micron"]==0
    return result


def main():
    # Calibrate topology against both a valid tetrahedron and an open version.
    vv=np.array([(0,0,0),(1,0,0),(0,1,0),(0,0,1)])
    ff=np.array([(0,2,1),(0,1,3),(1,2,3),(2,0,3)])
    assert topology(vv,ff)["non_manifold_edges"]==0
    assert topology(vv,ff[:-1])["non_manifold_edges"]==3
    reports={}
    for suffix,parts in [("-unit",1),("",2)]:
        path=ROOT/"exports"/("laptop-stand-sculpted"+suffix+".stl")
        v,f=parse_stl(path);r=topology(v,f);reports[path.name]=r
        assert len(f)>1000 and r["components"]==parts and r["non_manifold_edges"]==0
        assert r["volume_cm3"]>0 and r["zero_area_triangles"]==0 and r["bottom_contact_area_mm2"]>0
    if "bpy" in sys.modules or "--background" in sys.argv:
        reports["surface"]=surface_checks()
    out=ROOT/"exports/laptop-stand-sculpted/validation.json"
    out.write_text(json.dumps(reports,indent=2),encoding="utf-8")
    print(json.dumps(reports,indent=2))


if __name__=="__main__":main()
