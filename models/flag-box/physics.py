"""Inverse dynamics of the printed mechanism; no assumed controller behaviour."""
import math
import sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'lib'))
sys.stdout.reconfigure(encoding='utf-8')
from printmech.contract import write_json
from printmech.stl import read_binary_stl
from params import AXIS_Y,AXIS_Z,PLA_DENSITY,MOVE_SECONDS,STALL_TORQUE_NM

def integrals(tris):
    """Signed tetrahedra with the fourth vertex at the origin. SI units."""
    a,b,c=np.asarray(tris).transpose(1,0,2)
    v=np.einsum('ij,ij->i',a,np.cross(b,c))/6
    volume=float(v.sum())
    centroid=(v[:,None]*(a+b+c)/4).sum(axis=0)/volume
    def square(k):
        x,y,z=a[:,k],b[:,k],c[:,k]
        return float((v*(x*x+y*y+z*z+x*y+x*z+y*z)/10).sum())
    return volume,centroid,square(1)+square(2)

def cube_triangles(side):
    v=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]])*side/2
    f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
    return v[f]

def main():
    v,c,j=integrals(cube_triangles(.01))
    expected_v=.01**3
    expected_j=expected_v*(.01**2+.01**2)/12
    assert abs(v/expected_v-1)<1e-12 and np.linalg.norm(c)<1e-12
    assert abs(j/expected_j-1)<1e-12
    report={'method':'signed tetrahedral mass, centroid and inertia; prescribed quintic inverse dynamics',
            'calibration':{'pass':True,'cube_side_m':.01,'volume_m3':v,'inertia_per_density_m5':j,'expected_m5':expected_j},
            'assumptions':{'printed_and_horn_density_kg_m3':PLA_DENSITY,'extra_drag_bound_nm':.01,
                           'drag_note':'Added conservative allowance. Actual friction is unmeasured.',
                           'trajectory_seconds':MOVE_SECONDS,'motion':'0 to 90 degrees, quintic, zero endpoint speed and acceleration'},
            'parts':{}}
    moving=[]
    for pid in ('flag','bearing_button','horn'):
        tris=np.asarray(read_binary_stl(str(HERE/'build'/f'{pid}.stl')),dtype=float).reshape(-1,3,3)*.001
        tris-=np.array([0,AXIS_Y,AXIS_Z])
        vol,cen,integral=integrals(tris)
        mass=vol*PLA_DENSITY
        inertia=integral*PLA_DENSITY
        moving.append((mass,cen,inertia))
        report['parts'][pid]={'mass_kg':mass,'centroid_relative_m':cen.tolist(),'inertia_x_kg_m2':inertia}
    inertia=sum(p[2] for p in moving)
    rows=[]
    trajectory=['time_s,flag_deg,servo_deg,velocity_deg_s,required_torque_nm']
    for t in np.linspace(0,MOVE_SECONDS,2001):
        u=t/MOVE_SECONDS
        q=(math.pi/2)*(10*u**3-15*u**4+6*u**5)
        qd=(math.pi/2)*(30*u*u-60*u**3+30*u**4)/MOVE_SECONDS
        qdd=(math.pi/2)*(60*u-180*u*u+120*u**3)/MOVE_SECONDS**2
        gravity=sum(m*9.81*(c[1]*math.cos(q)-c[2]*math.sin(q)) for m,c,_ in moving)
        tau=inertia*qdd+gravity
        rows.append((float(t),tau,qd,qdd,gravity))
        trajectory.append(f'{t:.4f},{math.degrees(q):.5f},{45+math.degrees(q):.5f},{math.degrees(qd):.5f},{tau:.8f}')
    max_torque=max(abs(r[1]) for r in rows)
    max_with_drag=max_torque+.01
    report['result']={'total_moving_mass_kg':sum(p[0] for p in moving),'inertia_x_kg_m2':inertia,
                      'peak_gravity_nm':max(abs(r[4]) for r in rows),'peak_inertia_gravity_nm':max_torque,
                      'with_drag_bound_nm':max_with_drag,'continuous_budget_nm':STALL_TORQUE_NM/3,
                      'peak_velocity_deg_s':math.degrees(max(r[2] for r in rows)),
                      'peak_acceleration_deg_s2':math.degrees(max(abs(r[3]) for r in rows)),
                      'endpoint_velocity_deg_s':[math.degrees(rows[0][2]),math.degrees(rows[-1][2])],
                      'pass':max_with_drag<STALL_TORQUE_NM/3}
    write_json(HERE/'build'/'physics_report.json',report)
    target=HERE/'build'/'trajectory.csv'
    temp=target.with_suffix('.tmp')
    temp.write_text('\n'.join(trajectory)+'\n',encoding='utf-8',newline='\n')
    temp.replace(target)
    print(report['result'])

if __name__=='__main__': main()
