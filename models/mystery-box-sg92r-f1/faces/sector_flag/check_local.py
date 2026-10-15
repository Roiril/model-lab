"""Standalone local evidence. Never imports/executes compose.py or writes outside this face."""
import sys
sys.dont_write_bytecode=True
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import types
import itertools
import numpy as np
import bpy
import bmesh
from mathutils import Matrix

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'lib'))
pkg=types.ModuleType('sector_flag_local')
pkg.__path__=[str(HERE)]
sys.modules[pkg.__name__]=pkg
from sector_flag_local import geometry, kinematics as K, params as P, assembly, trials
from printmech import geometry as G
from printmech.solid_meter import Solid,Meter,calibrate,box_solid,VOLUME_FLOOR_MM3,first_contact


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def solid(ob,name):
    ob.data.calc_loop_triangles()
    verts=np.array([v.co[:] for v in ob.data.vertices])
    faces=np.array([t.vertices[:] for t in ob.data.loop_triangles])
    return Solid(name,verts[faces])


def metrics(ob):
    bm=bmesh.new()
    bm.from_mesh(ob.data)
    remaining=set(bm.verts)
    count=0
    sizes=[]
    bounds=[]
    while remaining:
        count+=1
        todo=[remaining.pop()]
        n=0
        vs=[]
        while todo:
            v=todo.pop(); n+=1; vs.append(v.co[:])
            for e in v.link_edges:
                other=e.other_vert(v)
                if other in remaining: remaining.remove(other); todo.append(other)
        sizes.append(n)
        bounds.append([np.min(vs,axis=0).tolist(),np.max(vs,axis=0).tolist()])
    result={'components':count,'component_vertices':sizes,'nonmanifold':sum(not e.is_manifold for e in bm.edges),
            'volume_mm3':bm.calc_volume(signed=False),'component_bounds':bounds,
            'bad_edges':[[e.verts[0].co[:],e.verts[1].co[:]] for e in bm.edges if not e.is_manifold][:6]}
    bm.free()
    return result


def envelope(s,mat,interface,tolerance,sweep):
    verts=s.posed(mat)
    edges=np.concatenate([s.faces[:,[0,1]],s.faces[:,[1,2]],s.faces[:,[2,0]]])
    a,b=verts[edges[:,0]],verts[edges[:,1]]
    slabs=[(-32.,0.,38.)]+[(r['d_mm'][0],r['d_mm'][1],r['size_uv_mm'][0]/2) for r in interface['internal_envelope']]
    margin=tolerance+sweep
    bad=[]
    if verts[:,2].min()-margin < -32-1e-6 or verts[:,2].max()+margin>37+1e-6:
        bad.append({'slab':'depth','excess_mm':max(-32-verts[:,2].min()+margin,verts[:,2].max()+margin-37)})
    for lo,hi,half in slabs:
        low,high=lo-margin,hi+margin
        p=[verts[(verts[:,2]>=low)&(verts[:,2]<=high)]]
        dz=b[:,2]-a[:,2]
        for cut in (low,high):
            mask=(np.minimum(a[:,2],b[:,2])<=cut)&(np.maximum(a[:,2],b[:,2])>=cut)&(np.abs(dz)>1e-10)
            t=(cut-a[mask,2])/dz[mask]
            p.append(a[mask]+(b[mask]-a[mask])*t[:,None])
        pts=np.concatenate(p)
        if not len(pts): continue
        excess=float(np.max(np.abs(pts[:,:2]))+margin-half)
        if excess>1e-5: bad.append({'slab':[lo,hi],'excess_mm':excess})
    return bad


def mass_properties(s):
    t=s.tris
    v=np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2]))/6
    vol=v.sum()
    com=np.sum(v[:,None]*t.sum(axis=1)/4,axis=0)/vol
    mass=abs(vol)*P.PLA_DENSITY_G_CM3/1000
    return {'volume_mm3':abs(float(vol)),'mass_g':float(mass),'com_mm':com.tolist()}


def write_json(path,data):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    json.loads(tmp.read_text(encoding='utf-8'))
    tmp.replace(path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--quick',action='store_true')
    parser.add_argument('--topology',action='store_true')
    parser.add_argument('--step',type=float,default=P.CHECK_STEP_DEG)
    parser.add_argument('--all',action='store_true',help='Also run wiring, drive, retention, assembly and shielding checks')
    parser.add_argument('--compare',action='store_true',help='Rebuild and compare all three shielding candidates')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    interface=json.loads((HERE.parents[1]/'interface.json').read_text(encoding='utf-8'))
    sg=load(ROOT/'models/sg92r-photo/params.py','sector_sg_reference')
    common=types.SimpleNamespace(ROOT=ROOT,SG=sg)
    out=HERE/'_local'; out.mkdir(exist_ok=True)
    write_json(out/'report.json',{'status':'running','quick':args.quick})
    meter=Meter()
    calibration=calibrate(meter)
    if not calibration['pass']: raise RuntimeError('calibration failed')
    print('CALIBRATION PASS',flush=True)
    meter.dispose()
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    parts=geometry.build(interface,common)
    manifest=json.loads((HERE/'module.json').read_text(encoding='utf-8'))
    if set(parts)!=set(manifest['parts']): raise RuntimeError('Geometry/manifest part mismatch')
    solids={pid:solid(row['object'],pid) for pid,row in parts.items()}
    topology={pid:metrics(row['object']) for pid,row in parts.items()}
    print('TOPOLOGY',json.dumps({p:{k:r[k] for k in ('components','nonmanifold','volume_mm3')} for p,r in topology.items()}),flush=True)
    write_json(out/'topology.json',topology)
    if args.topology: return
    if any(t['nonmanifold'] for t in topology.values()):
        raise RuntimeError('Non-manifold mesh; collision meter has not been run')
    for pid,row in parts.items():
        bpy.ops.object.select_all(action='DESELECT'); row['object'].select_set(True)
        bpy.ops.wm.stl_export(filepath=str(out/(pid+'.stl')),export_selected_objects=True)
    meter=Meter()
    keepouts={}
    moving_ids={'horn','input_gear','sector_gear','flag','flag_cover'}
    max_radius=max(float(np.linalg.norm(s.verts[:,1:3]-(K.O if pid in ('horn','input_gear') else K.H),axis=1).max()) for pid,s in solids.items() if pid in moving_ids)
    frame_sweep=0 if args.quick else 2*max_radius*math.sin(math.radians(args.step/4))
    for row in interface['mount_geometry']['frame_receivers']:
        c=np.array(row['center_mm']); size=np.array(row.get('size_mm',[row.get('radius_mm',0)*2]*2+[row.get('depth_mm',0)]))
        keepouts[row['id']]=box_solid('receiver_'+row['id'],c-size/2-.25-frame_sweep,c+size/2+.25+frame_sweep)
    angles=[60.,90.,120.] if args.quick else np.linspace(60,120,math.ceil(60/args.step)+1)
    report={'calibration':calibration,'topology':topology,'diagnostics':K.diagnostics(),'samples':len(angles),
            'envelope':{},'interference':{},'frame_clearance':{},'frame_clearance_required_mm':.25,
            'frame_sweep_bound_mm':frame_sweep,'bounds':{},'mass':{p:mass_properties(s) for p,s in solids.items()}}
    pairs=list(itertools.combinations(solids,2))
    static=set(solids)-{'horn','input_gear','sector_gear','flag','flag_cover'}
    checked=0
    for i,angle in enumerate(angles):
        mats=K.transforms(float(angle),interface,common)
        poses={p:s.posed(mats[p]) for p,s in solids.items()}
        for pid,points in poses.items():
            lo,hi=points.min(axis=0),points.max(axis=0)
            old=report['bounds'].get(pid,[lo,hi])
            report['bounds'][pid]=[np.minimum(old[0],lo).tolist(),np.maximum(old[1],hi).tolist()]
        bvhs={p:meter.bvh_of(poses[p],s.faces) for p,s in solids.items()}
        for pid,s in solids.items():
            if pid in ('panel','key_l','key_r'): continue
            pivot=K.O if pid in ('horn','input_gear') else K.H
            radius=float(np.linalg.norm(s.verts[:,1:3]-pivot,axis=1).max()) if pid not in static else 0.
            sweep=0 if args.quick else 2*radius*math.sin(math.radians(args.step/4))
            bad=envelope(s,mats[pid],interface,.25,sweep)
            if bad: report['envelope'][pid]={'servo_deg':float(angle),'violations':bad}
            for rid,rs in keepouts.items():
                if i and pid in static: continue
                vol,bounds=meter.common(s,mats[pid],rs,np.eye(4))
                if vol>VOLUME_FLOOR_MM3: report['frame_clearance'][pid+'/'+rid]={'servo_deg':float(angle),'inflated_common_mm3':vol,'bounds':bounds}
        for a,b in pairs:
            if i and a in static and b in static: continue
            v,bounds=meter.common_posed(solids[a],poses[a],bvhs[a],solids[b],poses[b],bvhs[b])
            checked+=1
            key=a+'/'+b
            if v>report['interference'].get(key,{}).get('max_mm3',VOLUME_FLOOR_MM3):
                report['interference'][key]={'servo_deg':float(angle),'max_mm3':v,'bounds':bounds}
        if i%10==0: print('POSE',i+1,'/',len(angles),'hits',len(report['interference']),flush=True)
    report['pair_evaluations']=checked
    reference=report['interference'].get('servo/horn')
    report['reference_internal']=reference
    if reference and reference['max_mm3']<=.05:
        del report['interference']['servo/horn']
    report['meter']=meter.stats
    mass=report['mass']
    gravity_bound=0.
    acceleration_bound=0.
    moving_mass=0.
    for pid,pivot in (('horn',K.O),('input_gear',K.O),('sector_gear',K.H),('flag',K.H),('flag_cover',K.H)):
        moving_mass+=mass[pid]['mass_g']
        gravity_bound+=mass[pid]['mass_g']*.001*9.80665*np.linalg.norm(np.array(mass[pid]['com_mm'])[1:]-pivot)*.001
        radius=np.linalg.norm(solids[pid].verts[:,1:]-pivot,axis=1).max()*.001
        acceleration_bound+=mass[pid]['mass_g']*.001*radius**2*math.radians(K.diagnostics()['max_acceleration_deg_s2'])
    torque=gravity_bound/P.EFFICIENCY+P.FRICTION_NM+P.ACCELERATION_BUDGET_NM
    report['torque']={'moving_mass_g':moving_mass,'gravity_bound_Nm':float(gravity_bound),'required_budget_Nm':float(torque),
                      'acceleration_bound_Nm':float(acceleration_bound),'allowed_Nm':P.STALL_TORQUE_NM/3,
                      'separating_force_at_allowed_N':P.STALL_TORQUE_NM/3/(P.PITCH_RADIUS)*math.tan(math.radians(20))}
    steps=assembly.steps(interface,common)
    report['assembly']={'steps':len(steps),'frames':sum(len(s['frames']) for s in steps)}
    if len({s['id'] for s in steps})!=len(steps): raise RuntimeError('Duplicate assembly step id')
    coupons=trials.build(parts,interface,common)
    report['trials']={name:metrics(ob) for name,ob in coupons.items()}
    for name,ob in coupons.items():
        bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
        bpy.ops.wm.stl_export(filepath=str(out/(name+'.stl')),export_selected_objects=True)
    report['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}
    report['interface_sha256']=hashlib.sha256((HERE.parents[1]/'interface.json').read_bytes()).hexdigest()
    report['reference_sha256']={name:hashlib.sha256((ROOT/'models/sg92r-photo'/name).read_bytes()).hexdigest() for name in ('params.py','model.py')}
    write_json(out/'report.json',report)
    for key in ('diagnostics','envelope','interference','frame_clearance','torque','assembly'):
        print(key.upper(),json.dumps(report[key],ensure_ascii=True),flush=True)
    meter.dispose()
    failed=report['envelope'] or report['frame_clearance'] or report['interference'] or torque>P.STALL_TORQUE_NM/3 or acceleration_bound>P.ACCELERATION_BUDGET_NM or any(t['nonmanifold'] or t['components']!=1 for t in list(topology.values())+list(report['trials'].values()))
    if failed: raise RuntimeError('Local numeric checks failed; see _local/report.json')
    if args.all:
        import runpy
        for script in ('check_features.py','check_interfaces.py','check_assembly.py','check_shield.py'):
            runpy.run_path(str(HERE/script),run_name='__main__')
            print('CHECK_PASS',script,flush=True)
    if args.compare:
        import runpy
        runpy.run_path(str(HERE/'compare_shields.py'),run_name='__main__')


if __name__=='__main__': main()
