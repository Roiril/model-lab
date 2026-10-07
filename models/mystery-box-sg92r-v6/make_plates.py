"""Geometry-only 200 mm plates. Bambu facet support paint is retained in 3MF.
No printer commands or G-code are packaged by this script.
"""
from pathlib import Path
import struct,json,zipfile,math,hashlib,html
import numpy as np
R=Path(__file__).resolve().parent;OUT=R/'plates';OUT.mkdir(exist_ok=True)
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
def read(path):
    b=path.read_bytes();n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+50*n
    dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);a=np.frombuffer(b,dtype=dt,count=n,offset=84)['v'].astype(float)
    vv,idx=np.unique(a.reshape(-1,3),axis=0,return_inverse=True);return vv,idx.reshape(-1,3),a
def pack(paths,width=180):
    rows=[]
    for path in paths:
        v,f,t=read(path);d=v.max(axis=0)-v.min(axis=0);rows.append([path,v,f,t,d])
    rows.sort(key=lambda x:-x[4][1]);x=y=h=0;placed=[]
    for path,v,f,t,d in rows:
        if x and x+d[0]>width:x=0;y+=h+8;h=0
        placed.append([path,v,f,t,x,y]);x+=d[0]+8;h=max(h,d[1])
    xmax=max(x+v[:,0].max() for _,v,_,_,x,y in placed);ymax=max(y+v[:,1].max() for _,v,_,_,x,y in placed)
    assert xmax<=180 and ymax<=180,(xmax,ymax)
    for row in placed:row[4]+=(200-xmax)/2;row[5]+=(200-ymax)/2
    return placed,[xmax,ymax]
def write(name,paths,manual=False):
    placed,size=pack(paths);model=[f'<model xmlns="{NS}" unit="millimeter" xml:lang="en-US"><metadata name="Application">SG92R v6 geometry plates</metadata><resources>'];cfg=['<config>'];records=[];merged=[]
    for i,(path,v,f,t,dx,dy) in enumerate(placed,1):
        norms=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(norms,axis=1);nz=norms[:,2]/length
        allowed=np.zeros(len(f),dtype=bool)
        if manual and path.name in ['04_main_cassette.stl','test_25_actual_U_support.stl']:allowed=(nz<-.9)&np.all(np.abs(t[:,:,2]-27.3)<.0001,axis=1)
        if manual and path.name in ['06_horn_cup_journal.stl','test_26_actual_cup_with_support.stl']:allowed=(nz<-.9)&np.all(np.abs(t[:,:,2]-11.5)<.0001,axis=1)
        model.append(f'<object id="{i}" name="{html.escape(path.stem)}" type="model"><mesh><vertices>')
        model.extend(f'<vertex x="{x:.8f}" y="{y:.8f}" z="{z:.8f}"/>' for x,y,z in v);model.append('</vertices><triangles>')
        for k,(a,b,c) in enumerate(f):
            paint=f' paint_supports="{4 if allowed[k] else 8}"' if manual else ''
            model.append(f'<triangle v1="{a}" v2="{b}" v3="{c}"{paint}/>')
        model.append('</triangles></mesh></object>')
        cfg.append(f'<object id="{i}"><metadata key="name" value="{html.escape(path.stem)}"/><metadata key="extruder" value="1"/><part id="{i}" subtype="normal_part"><metadata key="name" value="{html.escape(path.stem)}"/><metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/></part></object>')
        records.append(dict(name=path.stem,object_id=i,position_mm=[dx,dy],bounds_mm=v.max(axis=0).tolist(),stl_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),support_enforced_faces=int(allowed.sum()),support_enforced_area_mm2=float(length[allowed].sum()/2),support_blocked_faces=int((~allowed).sum()) if manual else 0))
        tt=t.copy();tt[:,:,0]+=dx;tt[:,:,1]+=dy;merged.extend(tt)
    model.append('</resources><build>')
    model.extend(f'<item objectid="{i}" printable="1" transform="1 0 0 0 1 0 0 0 1 {dx:.8f} {dy:.8f} 0"/>' for i,(_,_,_,_,dx,dy) in enumerate(placed,1));model.append('</build></model>');cfg.append('</config>')
    with zipfile.ZipFile(OUT/(name+'.3mf'),'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/xml"/></Types>')
        z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model','\n'.join(model));z.writestr('Metadata/model_settings.config','\n'.join(cfg))
        z.writestr('Metadata/project_settings.config',json.dumps({'enable_support':'1' if manual else '0','support_type':'normal(manual)','support_on_build_plate_only':'0','support_top_z_distance':'0.2','support_bottom_z_distance':'0.2','support_object_xy_distance':'0.35','layer_height':'0.2','wall_loops':'4','sparse_infill_density':'20%'},indent=2))
    # 3MF keeps each validated local mesh without float32 translation loss.
    # Individual printable STLs remain in stl/ and coupons/.
    obsolete=OUT/(name+'.stl')
    if obsolete.exists():
        assert obsolete.resolve().parent==OUT.resolve()
        assert b'200mm geometry only' in obsolete.read_bytes()[:80]
        obsolete.unlink()
    return dict(plate=name,bed_mm=[200,200],occupied_mm=size,manual_support=manual,parts=records)
if __name__=='__main__':
    jobs=[('plate_01_shells',['01_body','02_fixed_rear_cover','03_planar_lid'],False),('plate_02_cassette',['04_main_cassette','05_front_closure','06_horn_cup_journal'],True),('plate_03_links',['07_rear_rocker','08_front_rocker','09_link','10_hinge_axle','11_drive_axle','12_link_axle','13_body_cross_key','14_servo_top_keeper','15_flat_spacer','16_flat_spacer','17_local_cup_capture','18_local_capture_stop','19_local_capture_stop'],False)]
    report=[write(n,[R/'stl'/(f+'.stl') for f in fs],support) for n,fs,support in jobs]
    coupons=sorted(f for f in (R/'coupons').glob('*.stl') if not f.name.startswith(('test_25','test_26')))
    if coupons:report.insert(0,write('plate_00_fit_tests',coupons))
    report.append(write('plate_04_support_tests',[R/'coupons/test_25_actual_U_support.stl',R/'coupons/test_26_actual_cup_with_support.stl'],True))
    (R/'plate_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
