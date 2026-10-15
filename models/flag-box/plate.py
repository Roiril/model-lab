"""Flatten installed X1C profiles and slice a fixed, checked single plate."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'lib'))
sys.path.insert(0,str(ROOT/'tools'))
sys.stdout.reconfigure(encoding='utf-8')
from bambu_profiles import resolve, write_flat
import plate_3mf as P
from printmech.three_mf import inspect_sliced_3mf
from printmech.contract import write_json

OUT=ROOT/'prints'/'flag-box'
WORK=HERE/'build'
os.environ['TEMP']=os.environ['TMP']=str(WORK/'temp')
(WORK/'temp').mkdir(exist_ok=True)
EXE='C:/Program Files/Bambu Studio/bambu-studio.exe'

def build(names,basename):
    parts=[]
    for name in names:
        v,f=P.read_stl(OUT/f'{name}.stl')
        parts.append((name,v,f))
    placed,total=P.arrange(parts,236)
    placed=P.center_on_bed(placed,total)
    boxes=[]
    for name,v,f,dx,dy in placed:
        lo,hi=P.bbox(v)
        bb=[lo[0]+dx,lo[1]+dy,hi[0]+dx,hi[1]+dy]
        assert 0<=bb[0]<bb[2]<=256 and 0<=bb[1]<bb[3]<=256
        assert bb[0]>=18 or bb[1]>=28
        assert hi[2]<=250
        boxes.append({'name':name,'bounds_xy':bb,'height_mm':hi[2]})
    for i,a in enumerate(boxes):
        for b in boxes[i+1:]:
            aa,bb=a['bounds_xy'],b['bounds_xy']
            assert min(aa[2],bb[2])<=max(aa[0],bb[0]) or min(aa[3],bb[3])<=max(aa[1],bb[1])
    layout=OUT/f'{basename}-layout.3mf'
    P.write_3mf(layout,placed)
    profiles=WORK/'profiles'
    profiles.mkdir(exist_ok=True)
    machine=resolve('machine','Bambu Lab X1 Carbon 0.4 nozzle')
    process=resolve('process','0.20mm Standard @BBL X1C')
    process.update({'curr_bed_type':'Textured PEI Plate','wall_loops':'3','sparse_infill_density':'15%',
                    'seam_position':'back','enable_support':'0','exclude_object':'1','elefant_foot_compensation':'0.15',
                    'brim_type':'no_brim'})
    filament=resolve('filament','Bambu PLA Basic @BBL X1C')
    mp=write_flat(str(profiles/'machine.json'),machine)
    pp=write_flat(str(profiles/'process.json'),process)
    fp=write_flat(str(profiles/'filament.json'),filament)
    dest=OUT/f'{basename}.gcode.3mf'
    slice_dir=WORK/f'slice-{basename}'
    slice_dir.mkdir(exist_ok=True)
    cmd=[EXE,'--slice','0','--debug','2','--arrange','0','--load-settings',f'{mp};{pp}',
         '--load-filaments',fp,'--outputdir',str(slice_dir),'--export-3mf',dest.name,str(layout)]
    with (WORK/f'{basename}-slice.log').open('w',encoding='utf-8') as log:
        result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
    sliced=slice_dir/dest.name
    if result.returncode or not sliced.exists():
        raise RuntimeError(f'Slicing failed: {result.returncode}; see {basename}-slice.log')
    shutil.copyfile(sliced,dest)
    report=inspect_sliced_3mf(str(dest))
    report['layout_checks']={'overlap':False,'outside_bed':False,'exclusion':False,'boxes':boxes}
    # Confirm that Bambu retained the submitted placements.
    ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    def poses(path):
        with zipfile.ZipFile(path) as z:
            tree=ET.fromstring(z.read('3D/3dmodel.model'))
        return [e.get('transform') for e in tree.findall('m:build/m:item',ns)]
    report['layout_input_transforms']=poses(layout)
    report['layout_output_transforms']=poses(dest)
    write_json(WORK/f'{basename}-slice.json',report)
    print(basename, 'support',report['support_used'],'seconds',report['prediction_s'],'grams',report['weight_g'])
    for name,row in report['objects'].items():
        print(name,'layers',row['layers'],'top',row['z_top'],'floating',row['floating'])
    return report

if __name__=='__main__':
    if '--trial' in sys.argv:
        build(['horn-fit-trial','bearing_button','servo-fit-trial','key_right'],'flag-box-fit-PLA')
    else:
        build(['box','roof','flag','bearing_button','key_left','key_right'],'flag-box-PLA')
