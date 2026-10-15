"""Identical first-hit rays for every design candidate and the final cassette."""
import math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

VIEWS=((0,0),(45,0),(-45,0),(0,45),(0,-45))
GRID=np.arange(-38.,38.001,.5)
RAYS_PER_CANDIDATE=len(GRID)**2*len(VIEWS)*5

def check(solids, transforms, angles, mechanism, *, emit=None, grid_mm=.5,views=VIEWS):
    assert len(angles)==5
    grid=np.arange(-38.,38.00001,grid_mm)
    probe=BVHTree.FromPolygons([(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[(0,1,2),(0,2,3)],all_triangles=True)
    assert abs(probe.ray_cast(Vector((0,0,-10)),Vector((0,0,1)),20)[3]-10)<1e-5
    assert probe.ray_cast(Vector((2,0,-10)),Vector((0,0,1)),20)[0] is None
    rows=[]
    for angle in angles:
        mats=transforms(angle)
        verts=[]; faces=[]; owners=[]; offset=0
        for pid,s in solids.items():
            verts.extend(s.posed(mats[pid]).tolist())
            faces.extend((s.faces+offset).tolist())
            owners.extend([pid]*len(s.faces)); offset+=len(s.verts)
        bvh=BVHTree.FromPolygons(verts,faces,all_triangles=True)
        for au,av in views:
            direction=Vector((math.tan(math.radians(au)),math.tan(math.radians(av)),1.)).normalized()
            seen={}; exposed={}; examples=[]
            for u in grid:
                for v in grid:
                    origin=Vector((u,v,0.))-direction*100
                    co,normal,index,distance=bvh.ray_cast(origin,direction,200)
                    if co is None: continue
                    pid=owners[index]
                    if pid not in mechanism: continue
                    seen[pid]=seen.get(pid,0)+1
                    exposed.setdefault(pid,[]).append(list(co))
                    if len(examples)<8: examples.append({'part':pid,'hit':list(co),'face_uv':[float(u),float(v)]})
            row={'servo_deg':float(angle),'view_degrees':[au,av],
                 'visible_mechanism_pixels':seen,'examples':examples,
                 'visible_bounds':{p:[np.min(vs,axis=0).tolist(),np.max(vs,axis=0).tolist()] for p,vs in exposed.items()},
                 'outside_visible':{p:sum(v[2]<0 for v in vs) for p,vs in exposed.items()}}
            rows.append(row)
            if emit: emit(row)
    total=sum(sum(r['visible_mechanism_pixels'].values()) for r in rows)
    return {'ray_calibration':True,'grid_mm':grid_mm,'rays':len(grid)**2*len(views)*5,
            'mechanism_parts':sorted(mechanism),'views':rows,'visible_hits':total,'pass':total==0}
