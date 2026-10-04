"""Measure resolution convergence before extracting a 3D mesh.

The volume is quadrature of the continuous transverse intervals. It excludes
the separately swept rail and does not pretend to be the exported STL volume.
"""
import sys,json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import params as P
from poisson_body import profile,width_field,solve,warp,cubic,polygon_inside


def main():
    invalid_stopped=False
    try:solve(np.zeros((5,5),bool),.5)
    except ValueError:invalid_stopped=True
    mask=np.zeros((25,25),bool);mask[1:-1,1:-1]=True
    normal,normal_report=solve(mask,.5)
    assert invalid_stopped and normal[mask].min()>0 and normal_report['relative_residual']<1e-7
    reports=[];radii=[]
    for pitch in (.5,.25):
        y,z,mask,u,_,report=profile(pitch)
        yy,zz=np.meshgrid(y,z,indexing='ij')
        width=width_field(yy,zz)
        h=width*np.sqrt(u/(u+P.POISSON_SHAPE_SCALE*1e6))
        seat=(P.RAIL_HEIGHT-2*P.RAIL_HALF_THICKNESS+.0005)*1000
        h=np.where((zz>=0)&(zz<=seat),h,0)
        report['analytic_body_volume_cm3']=float(2*h.sum()*pitch*pitch/1000)
        report['max_transverse_width_mm']=float(2*h.max())
        reports.append(report);radii.append(h)
        print('RESOLUTION',pitch,json.dumps(report),flush=True)
    coarse,fine=radii[0],radii[1][::2,::2]
    shape=np.minimum(coarse.shape,fine.shape)
    difference=np.abs(coarse[:shape[0],:shape[1]]-fine[:shape[0],:shape[1]])
    relative=abs(reports[0]['analytic_body_volume_cm3']/reports[1]['analytic_body_volume_cm3']-1)
    yy,zz=np.meshgrid(np.linspace(-30,280,400),np.linspace(-10,155,220),indexing='ij')
    wy,wz=warp(yy,zz)
    ay,az=np.gradient(wy,yy[:,0],zz[0,:]);by,bz=np.gradient(wz,yy[:,0],zz[0,:])
    determinant=ay*bz-az*by
    outer,inner=cubic(P.OUTER)*1000,cubic(P.INNER)*1000
    inner+=np.array([P.INNER_Y_OFFSET,P.INNER_Z_OFFSET])*1000
    outer=np.stack(warp(outer[:,0],outer[:,1]),1)
    inner=np.stack(warp(inner[:,0],inner[:,1]),1)
    assert polygon_inside(inner[:,0],inner[:,1],outer).all()
    result={'solver_calibration':{'invalid_domain_stopped':invalid_stopped,'normal':normal_report},
            'resolutions':reports,'body_volume_relative_difference':relative,
            'transverse_radius_difference_p95_mm':float(np.percentile(difference,95)),
            'transverse_radius_difference_max_mm':float(difference.max()),
            'warp_jacobian_min':float(determinant.min()),'window_strictly_inside_outline':True}
    assert relative<.01 and determinant.min()>.25
    path=Path(__file__).resolve().parents[2]/'exports/laptop-stand-sculpted/convergence.json'
    path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
