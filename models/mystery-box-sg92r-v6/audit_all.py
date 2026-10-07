from pathlib import Path
import numpy as np,struct,collections,json,zipfile,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent
def metrics(a):
    a=np.asarray(a,dtype=float);vs,ids=np.unique(np.round(a.reshape(-1,3),5),axis=0,return_inverse=True);faces=ids.reshape(-1,3)
    edges=collections.Counter(tuple(sorted((int(t[i]),int(t[(i+1)%3])))) for t in faces for i in range(3))
    directed=collections.Counter((int(t[i]),int(t[(i+1)%3])) for t in faces for i in range(3))
    norms=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);area2=np.linalg.norm(norms,axis=1)
    return dict(triangles=len(a),nonmanifold_edges=sum(v!=2 for v in edges.values()),inconsistent_winding_edges=sum(directed[(u,v)]!=directed[(v,u)] for u,v in edges),zero_area=int(sum(area2<1e-9)),minimum_area_mm2=float(area2.min()/2),signed_volume_mm3=float(np.einsum('ij,ij->i',a[:,0],np.cross(a[:,1],a[:,2])).sum()/6),bounds_mm=[a.min(axis=(0,1)).tolist(),a.max(axis=(0,1)).tolist()])
tet=np.array([(0,0,0),(1,0,0),(0,1,0),(0,0,1)],float);closed=tet[np.array([(0,2,1),(0,1,3),(0,3,2),(1,2,3)])]
cal={'closed_tetrahedron':metrics(closed),'open_tetrahedron':metrics(closed[:-1]),'collinear_triangle':metrics([[(0,0,0),(1,0,0),(2,0,0)]])}
assert cal['closed_tetrahedron']['nonmanifold_edges']==0 and abs(cal['closed_tetrahedron']['signed_volume_mm3']-1/6)<1e-9
assert cal['open_tetrahedron']['nonmanifold_edges']==3 and cal['collinear_triangle']['zero_area']==1
rows=[];dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
for folder in ['stl','coupons']:
    for f in sorted((R/folder).glob('*.stl')):
        d=f.read_bytes();n=struct.unpack_from('<I',d,80)[0];assert len(d)==84+n*50
        m=metrics(np.frombuffer(d,dtype=dt,count=n,offset=84)['v']);rows.append({'file':f.relative_to(R).as_posix(),**m})
for f in sorted((R/'plates').glob('*.3mf')):
    with zipfile.ZipFile(f) as z:
        assert z.testzip() is None
        root=ET.fromstring(z.read('3D/3dmodel.model'));ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
        for obj in root.findall('m:resources/m:object',ns):
            v=np.array([[float(t.get(k)) for k in ['x','y','z']] for t in obj.findall('m:mesh/m:vertices/m:vertex',ns)]);t=np.array([[int(t.get(k)) for k in ['v1','v2','v3']] for t in obj.findall('m:mesh/m:triangles/m:triangle',ns)]);rows.append({'file':f.relative_to(R).as_posix(),'object':obj.get('name'),**metrics(v[t])})
bad=[r for r in rows if r['nonmanifold_edges'] or r['inconsistent_winding_edges'] or r['zero_area'] or r['signed_volume_mm3']<=0]
(R/'all_mesh_audit.json').write_text(json.dumps({'calibration':cal,'saved_meshes':rows,'failed':bad},indent=2),encoding='utf8')
print('MESH AUDIT',len(rows),'mesh instances; failures',len(bad),flush=True)
assert not bad,bad
