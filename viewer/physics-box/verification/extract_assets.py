"""Read-only extraction of frozen B3. Units: metre / kg / kg m^2."""
import bpy, json, hashlib, math, numpy as np
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parent
SOURCE=Path(r'C:\Users\kouga\Projects\Web\model-lab\models\mystery-box-sg92r-b3-candidate\editable_cube_B3.blend')
OUT=ROOT.parent/'assets'; OUT.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
base_ids={1,13,20,21,22}; lid_ids={3,7,8,12}; cup_ids={6,11}
parts=[]; groups={k:[] for k in ['base','frame','lid','cup','link','rotor']}
def moments(v,idx):
    t=v[idx]; dv=np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2]))/6
    vol=dv.sum(); s=t.sum(axis=1); com=(dv[:,None]*s/4).sum(axis=0)/vol
    Q=(dv[:,None,None]*(np.einsum('ni,nj->nij',s,s)+np.einsum('nki,nkj->nij',t,t))/20).sum(axis=0)
    Q-=vol*np.outer(com,com)
    I=(np.trace(Q)*np.eye(3)-Q)*1260
    return abs(vol)*1260,com,I if vol>0 else -I
for o in sorted(bpy.data.objects,key=lambda x:x.name):
    if o.type!='MESH' or (not o.name[:2].isdigit() and not o.name.startswith('REFERENCE ')): continue
    o.data.calc_loop_triangles()
    v=np.array([tuple(o.matrix_world@x.co) for x in o.data.vertices],dtype=float)
    idx=np.array([tuple(t.vertices) for t in o.data.loop_triangles],dtype=int)
    if not len(idx): continue
    if o.name[:2].isdigit():
        n=int(o.name[:2]); group='base' if n in base_ids else 'lid' if n in lid_ids else 'cup' if n in cup_ids else 'link' if n==9 else 'frame'
        mass,com,I=moments(v,idx)
    else:
        group='rotor' if 'horn' in o.name.lower() else 'base' if 'exciter' in o.name.lower() or 'speaker' in o.name.lower() else 'frame'
        try: mass,com,I=moments(v,idx)
        except Exception: mass,com,I=.0001,v.mean(axis=0),np.eye(3)*1e-9
        target=.0008 if group=='rotor' else .009 if 'body' in o.name.lower() else .012 if 'exciter' in o.name.lower() else .0001
        I*=target/max(mass,1e-9); mass=target
    d={'name':o.name,'group':group,'reference':o.name.startswith('REFERENCE '),'vertices':v.round(10).flatten().tolist(),'indices':idx.flatten().tolist(),'mass':float(mass),'com':com.tolist(),'inertia':I.tolist()}
    parts.append(d); groups[group].append(d)
massdata={}
for name,items in groups.items():
    mass=sum(x['mass'] for x in items); c=sum(x['mass']*np.array(x['com']) for x in items)/mass
    I=sum(np.array(x['inertia'])+x['mass']*((np.dot(np.array(x['com'])-c,np.array(x['com'])-c))*np.eye(3)-np.outer(np.array(x['com'])-c,np.array(x['com'])-c)) for x in items)
    # Reflected motor rotor inertia is a separate estimate; not a second mass.
    if name=='rotor': I+=np.eye(3)*5e-7
    eig, axes=np.linalg.eigh(I)
    if np.linalg.det(axes)<0: axes[:,0]*=-1
    q=Matrix(axes.tolist()).to_quaternion()
    massdata[name]={'mass':float(mass),'com':c.tolist(),'inertia':I.tolist(),'principal':eig.tolist(),'frame':{'x':q.x,'y':q.y,'z':q.z,'w':q.w}}
data={'version':'B3 physics v1','source_sha256':digest,'units':'m kg s kg*m^2','density':1260,'parts':parts,'bodies':massdata,
      'pivots':{'O':[.0498,.040,.037],'H':[.0498,.022,.0618],'A':[.0498,.040+.014*math.cos(math.radians(-10)),.037+.014*math.sin(math.radians(-10))],'B':[.0498,.036,.0578]},
      'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==digest}
(OUT/'cad.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf8')
print(json.dumps({'source':digest,'parts':[(x['name'],x['group'],len(x['indices'])//3) for x in parts],'massdata':massdata},indent=2),flush=True)
