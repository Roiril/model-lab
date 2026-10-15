"""Read shared inputs; write ONLY three_pixels/_local. No compose/model imports.

Blender --background --python-exit-code 1 --python <this file> -- [--quick]
"""
import sys
sys.dont_write_bytecode=True
import argparse
import ast
import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import bpy
import bmesh
from mathutils import Matrix

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'lib'))
from printmech.solid_meter import Solid, Meter, calibrate, VOLUME_FLOOR_MM3, first_contact, translation
from printmech import geometry as G


def load(name,path,package=False):
    spec=importlib.util.spec_from_file_location(name,path,submodule_search_locations=[str(path.parent)] if package else None)
    mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod)
    return mod


load('three_pixels',HERE/'__init__.py',True)
from three_pixels import geometry, kinematics as K, params as P, assembly, trials, verification
from three_pixels.recipe import _primitive


def solid(ob,name=None):
    ob.data.calc_loop_triangles()
    vertices=np.array([list(v.co) for v in ob.data.vertices])
    faces=np.array([list(t.vertices) for t in ob.data.loop_triangles])
    return Solid(name or ob.name,vertices[faces])


def metrics(ob):
    bm=bmesh.new(); bm.from_mesh(ob.data)
    left=set(bm.verts); count=0
    while left:
        count+=1; todo=[left.pop()]
        while todo:
            for e in todo.pop().link_edges:
                for v in e.verts:
                    if v in left: left.remove(v); todo.append(v)
    row={'volume_mm3':G.volume(ob),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'components':count}
    bm.free()
    return row


def clipped_points(tris,low,high):
    """Vertices of triangles clipped to a depth slab, without replacing by AABB."""
    t=tris[(tris[:,:,2].max(axis=1)>=low)&(tris[:,:,2].min(axis=1)<=high)]
    if len(t)==0: return np.empty((0,3))
    v=t.reshape(-1,3)
    out=[v[(v[:,2]>=low)&(v[:,2]<=high)]]
    for z in (low,high):
        for i,j in ((0,1),(1,2),(2,0)):
            a=t[:,i]; b=t[:,j]; d=b[:,2]-a[:,2]
            mask=(np.abs(d)>1e-12)&((a[:,2]-z)*(b[:,2]-z)<=0)
            aa=a[mask]; bb=b[mask]
            f=(z-aa[:,2])/(bb[:,2]-aa[:,2])
            out.append(aa+(bb-aa)*f[:,None])
    return np.concatenate(out)


def envelope(s,m,interface,cosmetic=False):
    v=s.posed(m); tris=v[s.faces]
    tol=0 if cosmetic else interface['manufacturing_tolerance_mm']
    rows=[]
    for layer in interface['internal_envelope']:
        d0,d1=layer['d_mm']; half=np.asarray(layer['size_uv_mm'])/2
        pts=clipped_points(tris,d0-tol,d1+tol)
        if len(pts): rows.append(float((half-tol-np.abs(pts[:,:2])).min()))
    pts=clipped_points(tris,-32-tol,tol-1e-7)
    if len(pts): rows.append(float(38-tol-np.abs(pts[:,:2]).max()))
    rows.extend((float(v[:,2].min()+32-tol),float(37-tol-v[:,2].max())))
    return min(rows)


def atomic_json(path,value):
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    json.loads(temp.read_text(encoding='utf-8')); os.replace(temp,path)


def continuous_envelopes(meshes,interface):
    """Enclose full rotations and complete vertical travel, including sample gaps."""
    rotary={'horn','cam_lower','cam_upper','cam_key_1','cam_key_2'}
    result={}
    for pid,s in meshes.items():
        if pid not in rotary and not pid.startswith('pixel_'):
            result[pid]=envelope(s,np.eye(4),interface,pid in ('panel','key_l','key_r')); continue
        lift=max(row['heights_mm'][int(pid[-1])-1] for row in K.read_patterns()['stops']) if pid.startswith('pixel_') else 0
        tol=interface['manufacturing_tolerance_mm']; margins=[]
        layers=[(-32,0,38,38)]+[(row['d_mm'][0],row['d_mm'][1],row['size_uv_mm'][0]/2,row['size_uv_mm'][1]/2) for row in interface['internal_envelope']]
        for d0,d1,hu,hv in layers:
            pts=clipped_points(s.tris,d0-tol,d1+tol+lift)
            if not len(pts): continue
            if pid in rotary:
                radius=np.linalg.norm(pts[:,:2]-np.array([P.AXIS_U*1000,0]),axis=1).max()
                margins.append(min(hu-tol-abs(P.AXIS_U*1000)-radius,hv-tol-radius))
            else: margins.append(float((np.array([hu,hv])-tol-np.abs(pts[:,:2])).min()))
        margins.extend([s.lo[2]-lift+32-tol,37-tol-s.hi[2]])
        result[pid]=float(min(margins))
    return {'passed':min(result.values())>=-1e-4,'margin_mm':result}


def run():
    parser=argparse.ArgumentParser(); parser.add_argument('--quick',action='store_true')
    parser.add_argument('--build-only',action='store_true')
    parser.add_argument('--contracts',action='store_true')
    parser.add_argument('--assembly-only',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output=HERE/'_local'; output.mkdir(exist_ok=True)
    interface_path=HERE.parents[1]/'interface.json'
    interface=json.loads(interface_path.read_text(encoding='utf-8'))
    sg=load('three_pixels_sg',ROOT/'models/sg92r-photo/params.py')
    common=SimpleNamespace(ROOT=ROOT,SG=sg)
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    print('LOCAL build start',flush=True)
    parts=geometry.build(interface,common)
    meshes={pid:solid(row['object'],pid) for pid,row in parts.items()}
    report={'interface_sha256':hashlib.sha256(interface_path.read_bytes()).hexdigest(),
            'parts':{pid:metrics(row['object']) for pid,row in parts.items()},
            'diagnostics':K.diagnostics()}
    report['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.iterdir()) if p.suffix in ('.py','.json')}
    report['mass_g']={pid:row['volume_mm3']*P.PLA_G_PER_MM3 for pid,row in report['parts'].items() if not parts[pid]['purchased']}
    report['total_mass_g']=sum(report['mass_g'].values())+9+.5
    report['mass_properties']=verification.mass_properties(meshes)
    report['pattern_contract']=verification.pattern_contract()
    report['continuous_envelope']=continuous_envelopes(meshes,interface)
    metadata=json.loads((HERE/'module.json').read_text(encoding='utf-8'))
    if set(metadata['parts'])!=set(parts): raise ValueError('module parts do not match geometry')
    own={p.stem for p in HERE.glob('*.py')}
    for path in HERE.glob('*.py'):
        tree=ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom):
                if node.level>1 or (node.level==0 and (node.module or '').split('.')[0] in own|{'frame','compose','faces'}):
                    raise ValueError('face package boundary: '+path.name)
            if isinstance(node,ast.Import):
                if any(n.name.split('.')[0] in own|{'frame','compose','faces'} for n in node.names):
                    raise ValueError('face package boundary: '+path.name)
    report['package_contract']={'passed':True,'parts':len(parts),'printed':sum(not r['purchased'] for r in parts.values())}
    report['pixel_gravity_n']={pid:mass*.00980665 for pid,mass in report['mass_g'].items() if pid.startswith('pixel_')}
    local_steps=assembly.steps(interface,common)
    report['assembly_contract']=verification.assembly_contract(local_steps,set(parts))
    samples=trials.build(parts,interface,common)
    report['trials']={pid:metrics(ob) for pid,ob in samples.items()}
    for pid,ob in samples.items():
        bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
        bpy.ops.wm.stl_export(filepath=str(output/('trial_'+pid+'.stl')),export_selected_objects=True)
    for pid,row in parts.items():
        report['parts'][pid]['bounds_mm']=[meshes[pid].lo.tolist(),meshes[pid].hi.tolist()]
        print('PART',pid,json.dumps(report['parts'][pid]),flush=True)
    # Save only selected STL files in the explicitly authorised local directory.
    for pid,row in parts.items():
        bpy.ops.object.select_all(action='DESELECT')
        row['object'].select_set(True)
        bpy.ops.wm.stl_export(filepath=str(output/(pid+'.stl')),export_selected_objects=True)
    atomic_json(output/'build.json',report)
    if args.build_only: return
    meter=Meter(); report['calibration']=calibrate(meter)
    if not report['calibration']['pass']: raise RuntimeError('solid meter calibration failed')
    receivers={}
    expanded={}
    for row in interface['mount_geometry']['frame_receivers']:
        receivers[row['id']]=solid(_primitive(row,row['id']))
        inflated=dict(row)
        if row['type']=='box': inflated['size_mm']=[d+.5 for d in row['size_mm']]
        else:
            inflated['radius_mm']+=.25; inflated['depth_mm']+=.5
        expanded[row['id']]=solid(_primitive(inflated,row['id']+'_inflated'))
    step=5 if args.quick else 1
    violations=[]; keepout=[]; collisions=[]; worst={}; env={pid:1e9 for pid in parts}
    pairs=list(itertools.combinations(parts,2)); cached={}
    for angle in np.arange(60,120+step/2,step):
        matrices=K.transforms(float(angle),interface,common)
        for pid,s in meshes.items():
            margin=envelope(s,matrices[pid],interface,pid in ('panel','key_l','key_r'))
            env[pid]=min(env[pid],margin)
            if margin < -1e-4: violations.append([float(angle),pid,margin])
        for a,b in pairs:
            relative=np.linalg.inv(matrices[a])@matrices[b]
            key=(a,b,tuple(relative.round(7).ravel()))
            if key not in cached:
                volume,boxes=meter.common(meshes[a],matrices[a],meshes[b],matrices[b])
                cached[key]=volume
                if volume>VOLUME_FLOOR_MM3 and a+'/'+b not in report.setdefault('intersection_bounds',{}):
                    report['intersection_bounds'][a+'/'+b]=boxes
            vol=cached[key]
            pair=a+'/'+b
            worst[pair]=max(worst.get(pair,0),vol)
            limit=.05 if set((a,b))=={'servo','horn'} else VOLUME_FLOOR_MM3
            if vol>limit: collisions.append([float(angle),a,b,vol])
        for pid,s in meshes.items():
            if pid in ('panel','key_l','key_r'): continue  # standard mount contacts, not mechanism
            for rid,rs in expanded.items():
                key=(pid,'receiver_'+rid,tuple(matrices[pid].round(7).ravel()))
                if key not in cached: cached[key]=meter.common(s,matrices[pid],rs,np.eye(4))[0]
                if cached[key]>VOLUME_FLOOR_MM3:
                    keepout.append([float(angle),pid,rid,cached[key]])
        if angle%10==0: print('SWEEP',float(angle),'collisions',len(collisions),'envelope',len(violations),'keepout',len(keepout),flush=True)
    report.update(sample_step_deg=step,angles=int(60/step+1),envelope_margin_mm=env,
                  envelope_violations=violations,keepout_025mm_violations=keepout,
                  collisions=collisions,worst_pair_mm3=worst,meter_stats=meter.stats)
    report['rotation_sample_displacement_bound_mm']=2*27.6*math.sin(math.radians(step)/4)
    report['translation_sample_displacement_bound_mm']=K.diagnostics()['max_dh_mm_per_rad']*math.radians(step)/2
    report['pass_sampled_geometry']=not(violations or keepout or collisions) and all(r['nonmanifold']==0 and r['components']==1 for r in report['parts'].values())
    if args.contracts or args.assembly_only:
        metadata=json.loads((HERE/'module.json').read_text(encoding='utf-8'))
        report['contact_interfaces']=verification.interfaces(meter,meshes,metadata,[60,75,90,105,120]) if args.contracts else {'passed':None,'rows':[]}
        sys.path.insert(0,str(ROOT/'tools'))
        # bl_job.py has an unconditional main(). Load only declarations; do not
        # execute its file-oriented entry point or create any external output.
        job_path=ROOT/'tools/mechgate_lib/bl_job.py'
        tree=ast.parse(job_path.read_text(encoding='utf-8'))
        declarations=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.Assign,ast.FunctionDef,ast.ClassDef))]
        sys.path.insert(0,str(ROOT/'lib/printmech'))
        namespace={'__file__':str(job_path),'__name__':'three_pixels_local_meter'}
        exec(compile(ast.Module(body=declarations,type_ignores=[]),str(job_path),'exec'),namespace)
        assembly_path=namespace['assembly_path']
        from printmech.contract import AssemblyPlan
        plan=AssemblyPlan()
        for row in local_steps:
            plan._append(row['id'],row['title'],row['instruction'],row['moving'],row['frames'])
            plan.state.update(row['frames'][-1])
        report['assembly_path']=assembly_path(meter,meshes,plan.steps,metadata['allowances'],{})
        report['elastic_cap']=verification.elastic_cap_path(meter,meshes,local_steps)
        atomic_json(output/'assembly.json',{'steps':plan.steps,'result':report['assembly_path']})
        print('CONTRACTS',json.dumps({'interfaces_pass':report['contact_interfaces']['passed'],
              'assembly_pass':report['assembly_path']['pass'],
              'elastic_cap':report['elastic_cap'],
              'failed_interfaces':[r for r in report['contact_interfaces']['rows'] if not r['passed']],
              'assembly_violations':report['assembly_path']['violations']},ensure_ascii=True),flush=True)
    report['inputs_unchanged']=report['interface_sha256']==hashlib.sha256(interface_path.read_bytes()).hexdigest() and all(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==h for name,h in report['source_sha256'].items())
    report['passed']=report['pass_sampled_geometry'] and report['continuous_envelope']['passed'] and report['mass_properties']['passed'] and report['pattern_contract']['passed'] and report['assembly_contract']['passed'] and report['inputs_unchanged'] and all(r['nonmanifold']==0 and r['components']==1 for r in report['trials'].values())
    if args.contracts: report['passed']=report['passed'] and report['contact_interfaces']['passed']
    if args.contracts or args.assembly_only: report['passed']=report['passed'] and report['assembly_path']['pass'] and report['elastic_cap']['passed']
    atomic_json(output/'check.json',report)
    print('RESULT',json.dumps({k:report[k] for k in ('passed','angles','pass_sampled_geometry','envelope_margin_mm','diagnostics')},ensure_ascii=True),flush=True)
    print('COLLISION_MAX',json.dumps({k:v for k,v in worst.items() if v>VOLUME_FLOOR_MM3}),flush=True)
    meter.dispose()
    if not report['passed']: raise RuntimeError('local checks failed; see _local/check.json')


if __name__=='__main__': run()
