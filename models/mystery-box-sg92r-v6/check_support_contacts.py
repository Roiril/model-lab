"""Inspect actual support-interface paths in the offline sliced project."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,re,collections
import numpy as np,struct,hashlib
R=Path(__file__).resolve().parent;P=R/'slice_checks/plate_02_cassette/plate_02_cassette.3mf'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};PN='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
def matrix(text):
    a=np.array([float(v) for v in (text or '1 0 0 0 1 0 0 0 1 0 0 0').split()]);return a[:9].reshape(3,3),a[9:]
with zipfile.ZipFile(P) as z:
    root=ET.fromstring(z.read('3D/3dmodel.model'));objects={o.get('id'):o for o in root.findall('m:resources/m:object',NS)}
    config=ET.fromstring(z.read('Metadata/model_settings.config'));names={o.get('id'):next((x.get('value') for x in o.findall('metadata') if x.get('key')=='name'),'?') for o in config.findall('object')};boxes=[]
    for item in root.findall('m:build/m:item',NS):
        oid=item.get('objectid');component=objects[oid].find('m:components/m:component',NS)
        if component is None:continue
        child=ET.fromstring(z.read(component.get(PN+'path').lstrip('/')));ob=next(o for o in child.findall('m:resources/m:object',NS) if o.get('id')==component.get('objectid'))
        verts=np.array([[float(v.get(k)) for k in ('x','y','z')] for v in ob.findall('m:mesh/m:vertices/m:vertex',NS)]);mc,tc=matrix(component.get('transform'));mb,tb=matrix(item.get('transform'))
        local=verts@mc+tc;world=local@mb+tb;boxes.append(dict(name=names[oid],min=world.min(axis=0),max=world.max(axis=0),rotation=mb,translation=tb,local_min=local.min(axis=0)))
    gcode=z.read('Metadata/plate_1.gcode').decode('utf8')
position=np.zeros(4);absolute=True;relative_e=True;feature='';points=collections.defaultdict(list)
for line in gcode.splitlines():
    if line.startswith('; FEATURE: '):feature=line[11:].strip();continue
    raw=line.split(';')[0].strip()
    if raw=='G90':absolute=True;continue
    if raw=='G91':absolute=False;continue
    if raw=='M82':relative_e=False;continue
    if raw=='M83':relative_e=True;continue
    if raw.startswith('G92 '):
        for k,v in re.findall(r'([XYZE])([-+0-9.]+)',raw):position['XYZE'.index(k)]=float(v)
        continue
    if not re.match(r'^G[01]\s',raw):continue
    old=position.copy();values={k:float(v) for k,v in re.findall(r'([XYZE])([-+0-9.]+)',raw)}
    for k,v in values.items():
        j='XYZE'.index(k);position[j]=v if absolute or k=='E' else position[j]+v
    extrusion=values.get('E',0) if relative_e else position[3]-old[3]
    if feature!='Support interface' or extrusion<=0 or np.linalg.norm(position[:2]-old[:2])<.0001:continue
    for box in boxes:
        if np.all(position[:2]>=box['min'][:2]-1) and np.all(position[:2]<=box['max'][:2]+1):
            local=(position[:3]-box['translation'])@np.linalg.inv(box['rotation'])-box['local_min'];points[box['name']].append(local.tolist());break
report={'physical_tested':False,'input_slice_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'input_plate_sha256':hashlib.sha256((R/'plates/plate_02_cassette.3mf').read_bytes()).hexdigest(),'method':'Extruding G0/G1 endpoints in Support interface; source object transform inverted. Low interface projections are checked against actual upward STL facets. Interface paths extend beyond model edges into air. Does not prove every deposited filament contact or removability.','objects':{}}
for box in boxes:
    name=box['name'];a=np.asarray(points[name]);entry={'interface_extrusion_endpoints':len(a)}
    if len(a):
        entry.update(bounds_print_local_mm=[a.min(axis=0).tolist(),a.max(axis=0).tolist()],interface_z_counts=dict(collections.Counter(f'{v:.2f}' for v in a[:,2])))
        if name.startswith('04'):
            low=a[a[:,2]<10];world_y=low[:,1]+5.4;world_z=67.3-low[:,0]
            # Lower interface can rest on recessed plane X6.7, or the non-mating
            # end face X12.4 of the short fore-side guide (wire starts X13.2).
            on_recess=(world_y>=24.5-.35)&(world_y<=55.5+.35)&(world_z>=27.-.35)&(world_z<=41.+.35)&(low[:,2]<4.)
            on_cutend=(world_y>=46.8-.35)&(world_y<=51.3+.35)&(world_z>=31.-.35)&(world_z<=43.3+.35)&(low[:,2]>8.)
            outside=~(on_recess|on_cutend)
            entry['extrusion_endpoints_outside_expected_landing_projection']=int(sum(outside))
            entry['outside_examples_print_xyz']=low[outside][:5].tolist()
            entry['low_interface_world_yz_bounds_mm']=[[float(world_y.min()),float(world_z.min())],[float(world_y.max()),float(world_z.max())]] if len(low) else []
            data=(R/'stl/04_main_cassette.stl').read_bytes();dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]);tri=np.frombuffer(data,dtype=dt,offset=84)['v'].astype(float)
            normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);up=tri[normal[:,2]>1e-6]
            def inside(pt,t):
                a,b,c=t[:,:2];v=b-a;w=c-a;p=pt-a;den=v[0]*w[1]-v[1]*w[0]
                if abs(den)<1e-9:return False
                u=(p[0]*w[1]-p[1]*w[0])/den;vv=(v[0]*p[1]-v[1]*p[0])/den
                return u>=-1e-6 and vv>=-1e-6 and u+vv<=1+1e-6
            allowed=air=forbidden=0;planes=[]
            for point in low:
                plane=2.7 if point[2]<4 else 8.4;planes.append(plane)
                surface=up[np.all(abs(up[:,:,2]-plane)<.0001,axis=1)]
                hit=[t for t in surface if inside(point[:2],t)]
                if not hit:air+=1;continue
                # Classify the physical facet centroid, not an extrusion endpoint
                # in expanded support-interface margins.
                okay=True
                for t in hit:
                    c=t.mean(axis=0);wy=c[1]+5.4;wz=67.3-c[0]
                    okay &= (plane==2.7 and 24.5-.001<=wy<=55.5+.001 and 27-.001<=wz<=41+.001) or (plane==8.4 and 46.8-.001<=wy<=51.3+.001 and 31-.001<=wz<=43.3+.001)
                if okay:allowed+=1
                else:forbidden+=1
            entry['actual_landing_projection_endpoint_check']={'allowed_nonfunctional_surface':allowed,'outside_material_in_interface_margin':air,'functional_or_other_surface':forbidden,'expected_print_surface_z_mm':sorted(set(planes)),'sampling_limitation':'Endpoint projection only, not a complete continuous filament envelope test'}
            assert forbidden==0,entry
    report['objects'][name]=entry
(R/'support_contact_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
