"""Independently expand the final 3mf component transforms and compare to source STL."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'lib'))
sys.stdout.reconfigure(encoding='utf-8')
from mechgate_lib.meshcheck import read_stl,signed_volume
from printmech.contract import write_json
N='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
P='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
OUT=ROOT/'prints'/'flag-box'

def matrix(text):
    m=np.eye(4)
    if text:
        v=[float(x) for x in text.split()]
        m[:3,:3]=np.array(v[:9]).reshape(3,3).T
        m[:3,3]=v[9:]
    return m

def expand(z):
    objects={}
    for path in z.namelist():
        if path.endswith('.model'):
            tree=ET.fromstring(z.read(path))
            for ob in tree.findall(N+'resources/'+N+'object'):
                objects[(path,ob.get('id'))]=ob
    names={}
    cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
    for ob in cfg.findall('object'):
        names[ob.get('id')]=next(m.get('value') for m in ob.findall('metadata') if m.get('key')=='name')
    def geometry(path,oid,pose):
        ob=objects[(path,oid)]
        mesh=ob.find(N+'mesh')
        chunks=[]
        if mesh is not None:
            vs=np.array([[float(v.get(k)) for k in ('x','y','z')] for v in mesh.find(N+'vertices')])
            fs=np.array([[int(t.get(k)) for k in ('v1','v2','v3')] for t in mesh.find(N+'triangles')])
            vs=(pose@np.column_stack([vs,np.ones(len(vs))]).T).T[:,:3]
            chunks.append(vs[fs])
        comps=ob.find(N+'components')
        if comps is not None:
            for c in comps:
                target=c.get(P+'path',path).lstrip('/')
                chunks.extend(geometry(target,c.get('objectid'),pose@matrix(c.get('transform'))))
        return chunks
    tree=ET.fromstring(z.read('3D/3dmodel.model'))
    return {names[item.get('objectid')]:np.concatenate(geometry('3D/3dmodel.model',item.get('objectid'),matrix(item.get('transform'))))
            for item in tree.find(N+'build')}

def bounds(tris):
    v=tris.reshape(-1,3)
    return np.array([v.min(axis=0),v.max(axis=0)])

def verify(basename):
    expected=expand(zipfile.ZipFile(OUT/f'{basename}-layout.3mf'))
    dest=OUT/f'{basename}.gcode.3mf'
    with zipfile.ZipFile(dest) as z:
        actual=expand(z)
        gcode=z.read('Metadata/plate_1.gcode')
        md5=z.read('Metadata/plate_1.gcode.md5').decode().strip()
        assert hashlib.md5(gcode).hexdigest() in md5.lower()
        settings=json.loads(z.read('Metadata/project_settings.config'))
    assert set(expected)==set(actual)
    rows=[]
    for name,tris in actual.items():
        bb=bounds(tris)
        error=float(np.max(np.abs(bb-bounds(expected[name]))))
        assert error<.001,(name,error)
        source=read_stl(OUT/f'{name}.stl')
        assert abs(signed_volume(tris)/signed_volume(source)-1)<.0001,name
        assert np.all(bb[0]>=-.001) and np.all(bb[1]<=[256.001,256.001,250.001])
        assert bb[0,0]>=18 or bb[0,1]>=28
        rows.append({'name':name,'actual_bounds_mm':bb.tolist(),'input_bounds_error_mm':error,
                     'volume_ratio_to_stl':signed_volume(tris)/signed_volume(source),'triangles':len(tris)})
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            aa,bb=np.array(a['actual_bounds_mm']),np.array(b['actual_bounds_mm'])
            assert np.any(np.minimum(aa[1,:2],bb[1,:2])<=np.maximum(aa[0,:2],bb[0,:2]))
    # Positive and injected-negative checks for the placement comparison.
    t=next(iter(expected.values()))
    assert np.max(np.abs(bounds(t)-bounds(t)))<.001
    assert np.max(np.abs(bounds(t+np.array([1,0,0]))-bounds(t)))>.001
    for key,value in [('layer_height','0.2'),('wall_loops','3'),('enable_support','0')]:
        assert str(settings[key])==value,(key,settings[key])
    assert settings['curr_bed_type']=='Textured PEI Plate'
    assert settings['printer_model']=='Bambu Lab X1 Carbon'
    report={'pass':True,'calibration':{'known_unchanged':True,'injected_1mm_shift_rejected':True},
            'gcode_md5':md5,'settings':{k:settings.get(k) for k in ('printer_model','nozzle_diameter','layer_height','wall_loops','sparse_infill_density','enable_support','curr_bed_type','elefant_foot_compensation')},
            'parts':rows}
    write_json(HERE/'build'/f'{basename}-delivery.json',report)
    print(basename, 'PASS',len(rows),'parts; max placement error',max(r['input_bounds_error_mm'] for r in rows))

if __name__=='__main__':
    verify('flag-box-PLA')
    verify('flag-box-fit-PLA')
