"""Offline Bambu Studio checks; never connect, send or start a print."""
from pathlib import Path
import subprocess,json,sys,concurrent.futures
R=Path(__file__).resolve().parent;EXE=r'C:\Program Files\Bambu Studio\bambu-studio.exe'
jobs=[('plate_01_shells',False),('plate_02_cassette',True),('plate_03_links',False),('plate_00_fit_tests',False),('plate_04_support_tests',True)]
if len(sys.argv)>1:jobs=[j for j in jobs if j[0] in sys.argv[1:]]
jobs=[j for j in jobs if (R/'plates'/(j[0]+'.3mf')).exists()]
def run(job):
    name,support=job;folder=R/'slice_checks'/name;folder.mkdir(parents=True,exist_ok=True)
    config='process_manual_support.json' if support else 'process_no_support.json'
    args=[EXE,'--debug','2','--load-settings',str(R/'machine_x1c_flat.json')+';'+str(R/config),'--load-filaments',str(R/'filament_pla_flat.json'),'--orient','0','--arrange','1','--slice','0','--outputdir',str(folder),'--export-3mf',name+'.3mf',str(R/'plates'/(name+'.3mf'))]
    r=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=300)
    (folder/'slice.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf8');print('SLICE',name,r.returncode,flush=True)
    return dict(plate=name,returncode=r.returncode,manual_support_requested=support,output=str(folder))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(run,jobs))
old=json.loads((R/'slice_run.json').read_text()) if (R/'slice_run.json').exists() else [];merged={r['plate']:r for r in old};merged.update({r['plate']:r for r in rows})
(R/'slice_run.json').write_text(json.dumps(list(merged.values()),indent=2),encoding='utf8')
assert all(r['returncode']==0 for r in rows),rows
