import pathlib,struct,collections,json,numpy as np
R=pathlib.Path(__file__).resolve().parent;rows=[]
for p in sorted((R/'stl').glob('*.stl')):
 d=p.read_bytes();n=struct.unpack_from('<I',d,80)[0];assert len(d)==84+50*n
 typ=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]);a=np.frombuffer(d,dtype=typ,count=n,offset=84)['v'].astype(float)
 vs,ids=np.unique(np.round(a.reshape((-1,3)),5),axis=0,return_inverse=True);f=ids.reshape((-1,3));edges=collections.Counter(tuple(sorted((int(t[i]),int(t[(i+1)%3])))) for t in f for i in range(3))
 norms=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);area2=np.linalg.norm(norms,axis=1);normalz=np.divide(norms[:,2],area2,out=np.zeros_like(area2),where=area2>0)
 bad=(normalz<-.707116)&(a[:,:,2].max(axis=1)>.001)
 rows.append(dict(part=p.name,triangles=n,vertices=len(vs),nonmanifold_edges=sum(v!=2 for v in edges.values()),zero_area=int(sum(area2<1e-9)),volume_mm3=float(abs(np.sum(np.einsum('ij,ij->i',a[:,0],np.cross(a[:,1],a[:,2])))/6)),bounds_mm=[a.min(axis=(0,1)).tolist(),a.max(axis=(0,1)).tolist()],steep_down_faces=int(sum(bad)),steep_down_area_mm2=float(sum(area2[bad])/2)))
(R/'mesh_audit.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows,indent=1))
