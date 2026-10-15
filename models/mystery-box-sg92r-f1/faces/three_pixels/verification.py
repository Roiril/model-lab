"""Contact probes against real solids. The shared meter is used unmodified."""
import math
import copy
import numpy as np
from printmech.solid_meter import first_contact, translation, Solid, VOLUME_FLOOR_MM3
from . import kinematics as K, params as P


def pattern_contract():
    table=K.read_patterns(); errors=[]
    for row in table['stops']:
        for i,a in enumerate(P.FOLLOWER_DEG):
            for offset in np.linspace(-5,5,21):
                phi=a-(row['servo_deg']+offset-90)
                if abs(K.curve(phi)-row['heights_mm'][i])>1e-9: errors.append('dwell')
    alternate=copy.deepcopy(table)
    alternate['stops'][0]['heights_mm'][0]=2.5
    phi=np.arange(0,360,.5)
    before=K.groove_bounds(25,phi,table)
    after=K.groove_bounds(25,phi,alternate)
    changes=[float(np.max(np.abs(a-b))) for a,b in zip(before,after)]
    if min(changes)<.49: errors.append('table did not change both cam surfaces')
    return {'passed':not errors,'errors':errors,'changed_height_mm':.5,
            'upper_lower_surface_change_mm':changes,'dwell_samples':189}


def mass_properties(solids):
    rows={}
    for pid,s in solids.items():
        a,b,c=s.tris[:,0],s.tris[:,1],s.tris[:,2]
        dv=np.einsum('ij,ij->i',a,np.cross(b,c))/6
        volume=float(dv.sum())
        centre=(dv[:,None]*(a+b+c)/4).sum(axis=0)/volume
        second=((a*a+b*b+c*c+a*b+a*c+b*c)*dv[:,None]/10).sum(axis=0)
        polar=second[0]+second[1]-2*(P.AXIS_U*1000)*volume*centre[0]+(P.AXIS_U*1000)**2*volume
        mass=abs(volume)*P.PLA_G_PER_MM3/1000
        if pid=='horn': mass=.0005
        rows[pid]={'volume_mm3':abs(volume),'centre_mm':centre.tolist(),
                   'mass_kg':mass,'inertia_about_servo_kg_m2':abs(polar/volume)*mass*1e-6}
    rotating=['cam_lower','cam_upper','cam_key_1','cam_key_2','horn']
    gravity=sum(rows[p]['mass_kg']*9.80665*math.hypot(rows[p]['centre_mm'][0]-P.AXIS_U*1000,rows[p]['centre_mm'][1])/1000 for p in rotating)
    acceleration=math.radians(60)*10/math.sqrt(3)/P.MOVE_SECONDS**2
    torque_acceleration=sum(rows[p]['inertia_about_servo_kg_m2'] for p in rotating)*acceleration
    bound=K.diagnostics()['torque_conservative_nm']+gravity
    return {'parts':rows,'rotating_gravity_bound_nm':gravity,'rotating_acceleration_nm':torque_acceleration,
            'torque_including_rotating_gravity_nm':bound,'passed':bool(bound<P.SERVO_STALL_NM/3 and torque_acceleration<P.ACCELERATION_NM)}


def flexed_cap(solid):
    """Inextensible beam centreline; cross sections rotate with the tangent."""
    vertices=solid.verts.copy(); strains=[]; tips=[]
    for sign,root,length,thickness,target in ((1,-12.,22.,1.2,5.),(-1,-7.5,17.5,1.6,.6)):
        t=np.linspace(0,1,2201); ds=length/(len(t)-1)
        def shape(parameter):
            slope=parameter/length*(3*t-1.5*t*t)
            theta=np.arctan(slope)
            x=np.r_[0,np.cumsum((np.sin(theta[:-1])+np.sin(theta[1:]))*ds/2)]
            y=np.r_[0,np.cumsum((np.cos(theta[:-1])+np.cos(theta[1:]))*ds/2)]
            return x,y,theta
        lo,hi=target,target*1.2
        for _ in range(30):
            mid=(lo+hi)/2
            if shape(mid)[0][-1]<target: lo=mid
            else: hi=mid
        x,y,theta=shape(hi)
        mask=(vertices[:,0]*sign>17.3)&(vertices[:,1]>root)&(vertices[:,2]>21.6)
        v=vertices[mask]; q=np.clip((v[:,1]-root)/length,0,1)
        tangent=np.interp(q,t,theta); offset=v[:,0]-sign*18.85
        v[:,0]=sign*(18.85+np.interp(q,t,x))+offset*np.cos(tangent)
        v[:,1]=root+np.interp(q,t,y)-sign*offset*np.sin(tangent)
        vertices[mask]=v
        strains.append(100*1.5*thickness*hi/length**2)
        tips.append([sign,float(x[-1]),float(length-y[-1])])
    return Solid('flexed_cap',vertices[solid.faces]),{'strain_percent':strains,'tip_deflection_and_shortening_mm':tips}


def elastic_cap_path(meter,solids,steps):
    bent,report=flexed_cap(solids['servo_cap'])
    state={}; violations=[]; count=0
    for row in steps:
        if row['id']=='servo_cap-in':
            fixed={p:(solids[p],m) for p,m in state.items()}
            for frame in row['frames'][:-1]:
                mat=frame['servo_cap']; count+=1
                for pid,(s,pose) in fixed.items():
                    volume,boxes=meter.common(bent,mat,s,pose)
                    if volume>VOLUME_FLOOR_MM3: violations.append([float(mat[2,3]),pid,volume,boxes])
            # Releasing occurs after seating, so only the rear arms move.
            for t in np.linspace(0,1,11):
                # Solid re-indexing changes vertex order. Use original-index tris.
                tris=(1-t)*bent.tris+t*solids['servo_cap'].tris
                released=Solid('release',tris)
                for pid,(s,pose) in fixed.items():
                    volume,_=meter.common(released,np.eye(4),s,pose)
                    if volume>VOLUME_FLOOR_MM3: violations.append(['release',pid,volume])
            break
        state.update(row['frames'][-1])
    report.update(checked_frames=count+11,violations=violations,
                  passed=not violations and max(report['strain_percent'])<=2)
    return report


def interfaces(meter, solids, metadata, angles):
    rows=[]
    for angle in angles:
        pose=K.transforms(angle)
        for item in metadata['interfaces']:
            result={'id':item['id'],'servo_deg':angle,'type':item['type']}
            if item['type']=='drive':
                driver=item['driver']; driven=item['driven']
                fixed={driver:(solids[driver],pose[driver])}
                rotational=driven.startswith('cam_')
                travels=[]
                for sign in (-1,1):
                    def at(t):
                        change=K.rotation(sign*t) if rotational else translation(0,0,sign*t)
                        return change@pose[driven]
                    probe=first_contact(meter,solids[driven],at,fixed,
                                        maximum=3.3 if rotational else .6,
                                        coarse=.3 if rotational else .05,refine=10)
                    travels.append(probe['travel'])
                limit=item['max_play_deg'] if rotational else item['max_play_mm']
                chosen=travels if item['sides']=='both' else [travels[0 if item['contact_direction'][2]<0 else 1]]
                result.update(travels=travels,unit='deg' if rotational else 'mm',
                              limit=limit,passed=all(t is not None and 0<t<=limit for t in chosen))
            else:
                direction=np.asarray(item['direction'])
                fixed={p:(solids[p],pose[p]) for p in item['against']}
                found=[]
                for pid in item['parts']:
                    probe=first_contact(meter,solids[pid],lambda t:translation(*(direction*t))@pose[pid],
                                        fixed,maximum=1.,coarse=.125,refine=10)
                    if probe['travel'] is not None: found.append(probe['travel'])
                travel=min(found) if found else None
                result.update(travel_mm=travel,passed=travel is not None and 0<travel<=item['max_free_mm'])
            rows.append(result)
        print('CONTACT',angle,'failed',sum(not r['passed'] for r in rows),flush=True)
    return {'passed':all(r['passed'] for r in rows),'rows':rows}


def assembly_contract(steps,ids):
    present={}; errors=[]; max_mm=0.; max_deg=0.
    for step in steps:
        if set(step['moving'])!=set(step['frames'][0]): errors.append(step['id']+': moving mismatch')
        previous=None
        for frame in step['frames']:
            if set(frame)!=set(step['moving']): errors.append(step['id']+': frame mismatch')
            for pid,mat in frame.items():
                if pid not in ids: errors.append(pid+': unknown part')
                m=np.asarray(mat,dtype=float)
                if m.shape!=(4,4) or not np.isfinite(m).all(): errors.append(pid+': bad matrix')
                if previous is not None:
                    delta=m@np.linalg.inv(previous[pid])
                    max_mm=max(max_mm,float(np.linalg.norm(delta[:3,3])))
                    max_deg=max(max_deg,math.degrees(math.acos(np.clip((np.trace(delta[:3,:3])-1)/2,-1,1))))
                present[pid]=m
            previous=frame
    missing=set(ids)-set(present)
    if missing: errors.append('missing:'+','.join(sorted(missing)))
    if any(not np.allclose(m,np.eye(4),atol=1e-7) for m in present.values()): errors.append('final pose is not identity')
    if max_mm>1+1e-7 or max_deg>5+1e-7: errors.append('step too large')
    return {'passed':not errors,'steps':len(steps),'max_step_mm':max_mm,'max_step_deg':max_deg,'errors':errors}
