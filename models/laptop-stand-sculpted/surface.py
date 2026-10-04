"""Unambiguous tetrahedral extraction and bounded local mesh smoothing.

Coordinates retain the input field's units. model.py recalculates outward
face normals after extraction and every Boolean operation.
"""
import numpy as np


def marching_tetrahedra(field, origin, pitch):
    """Consistent six-tetrahedron cube subdivision avoids ambiguous faces."""
    corners=np.array([(0,0,0),(1,0,0),(1,1,0),(0,1,0),
                      (0,0,1),(1,0,1),(1,1,1),(0,1,1)])
    shape=np.array(field.shape)-1
    sign=field<0
    total=np.zeros(tuple(shape),np.uint8)
    for c in corners:
        total+=sign[c[0]:c[0]+shape[0],c[1]:c[1]+shape[1],c[2]:c[2]+shape[2]]
    cells=np.argwhere((total>0)&(total<8))
    grid_ids=np.stack([np.ravel_multi_index((cells+c).T,field.shape) for c in corners],1)
    flat=field.ravel()
    edge_batches=[]
    for tet in [(0,1,2,6),(0,2,3,6),(0,3,7,6),(0,7,4,6),(0,4,5,6),(0,5,1,6)]:
        ids=grid_ids[:,tet]
        code=np.sum((flat[ids]<0)*np.array([1,2,4,8]),axis=1)
        for pattern in range(1,15):
            active=ids[code==pattern]
            if not len(active):continue
            inside=[i for i in range(4) if pattern&(1<<i)]
            outside=[i for i in range(4) if not pattern&(1<<i)]
            if len(inside)==1:
                pairs=[(inside[0],j) for j in outside];triangles=[(0,1,2)]
            elif len(outside)==1:
                pairs=[(outside[0],j) for j in inside];triangles=[(0,2,1)]
            else:
                a,b=inside;c,d=outside
                pairs=[(a,c),(a,d),(b,d),(b,c)];triangles=[(0,1,2),(0,2,3)]
            edges=np.stack([active[:,pair] for pair in pairs],axis=1)
            for tri in triangles:edge_batches.append(edges[:,tri,:].reshape(-1,2))
    all_edges=np.sort(np.concatenate(edge_batches),axis=1)
    edges,inverse=np.unique(all_edges,axis=0,return_inverse=True)
    a=np.array(np.unravel_index(edges[:,0],field.shape)).T
    b=np.array(np.unravel_index(edges[:,1],field.shape)).T
    va,vb=flat[edges[:,0]],flat[edges[:,1]]
    fraction=va/(va-vb)
    verts=(a+(b-a)*fraction[:,None])*pitch+np.array(origin)
    return verts.astype(np.float32),inverse.reshape(-1,3)

def taubin(verts, quads, iterations, lam=0.5, mu=-0.53):
    edges = np.concatenate([quads[:, [i, (i+1)%quads.shape[1]]] for i in range(quads.shape[1])])
    edges = np.unique(np.sort(edges, axis=1), axis=0)
    a = np.concatenate([edges[:, 0], edges[:, 1]])
    b = np.concatenate([edges[:, 1], edges[:, 0]])
    count = np.bincount(a, minlength=len(verts)).astype(np.float32)
    v = verts.copy()
    for step in range(iterations * 2):
        acc = np.zeros_like(v)
        np.add.at(acc, a, v[b])
        mean = acc / np.maximum(count, 1)[:, None]
        v += (lam if step % 2 == 0 else mu) * (mean - v)
    return v
