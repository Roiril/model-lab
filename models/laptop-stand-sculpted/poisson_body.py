"""Smooth thickness inside a nonconvex silhouette, with no medial-axis ridge.

Solve -Laplacian(u)=1 with a zero boundary. The positive solution u gives a
smooth transverse radius. Outside the domain the field is strictly positive.
Numerical coordinates in this module are millimetres; output is metres.
"""
import json
from pathlib import Path
import numpy as np
import params as P
from surface import marching_tetrahedra,taubin


def cubic(a,n=660):
    a=np.array(a,float);t=np.arange(n)*len(a)/n;i=np.floor(t).astype(int)
    f=(t-i)[:,None]
    return ((1-f)**3*a[(i-1)%len(a)]+(3*f**3-6*f*f+4)*a[i]+
            (-3*f**3+3*f*f+3*f+1)*a[(i+1)%len(a)]+f**3*a[(i+2)%len(a)])/6


def polygon_inside(y,z,poly):
    inside=np.zeros(y.shape,bool)
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        if a[1]==b[1]:continue
        crossing=(a[1]>z)!=(b[1]>z)
        intercept=(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]
        inside^=crossing&(y<intercept)
    return inside


def warp(y,z):
    local=np.exp(-((y-123)/50)**2-((z-48)/45)**2)
    yy=y+P.PROFILE_MID_SHIFT*1000*np.exp(-((z-78)/25)**2)
    yy+=P.PROFILE_SHOULDER_SHIFT*1000*np.exp(-((z-128)/16)**2)
    yy+=P.PROFILE_WINDOW_SHIFT*1000*local
    zz=z+P.PROFILE_WINDOW_LIFT*1000*local
    return yy,zz


def boundary_distance(y,z,polygons):
    result=np.full(y.shape,np.inf)
    for poly in polygons:
        for a,b in zip(poly,np.roll(poly,-1,axis=0)):
            direction=b-a;length=direction@direction
            if length<1e-12:continue
            t=np.clip(((y-a[0])*direction[0]+(z-a[1])*direction[1])/length,0,1)
            result=np.minimum(result,(y-a[0]-t*direction[0])**2+(z-a[1]-t*direction[1])**2)
    return np.sqrt(result)


def solve(mask,pitch,distance=None):
    """Conjugate gradient on the masked five-point Laplacian."""
    if pitch<=0 or not mask.any():raise ValueError('Nonempty domain and positive pitch required')
    diagonal=np.full(mask.shape,4.0)
    if distance is not None:
        # Cut-cell Dirichlet boundaries. Symmetric conductance retains CG.
        for axis in (0,1):
            for offset in (-1,1):
                neighbour=np.roll(mask,offset,axis)
                d=np.roll(distance,offset,axis)
                boundary=mask&~neighbour
                fraction=np.maximum(distance/(distance+d+1e-12),.001)
                diagonal[boundary]+=1/fraction[boundary]-1
    def apply(a):
        out=diagonal*a
        out[:-1]-=a[1:];out[1:]-=a[:-1]
        out[:,:-1]-=a[:,1:];out[:,1:]-=a[:,:-1]
        out[~mask]=0
        return out
    u=np.zeros(mask.shape,float)
    residual=mask.astype(float)*pitch*pitch
    preconditioned=residual/diagonal
    direction=preconditioned.copy();rr=np.sum(residual*preconditioned)
    initial=np.sum(residual*residual)
    for step in range(3000):
        ad=apply(direction)
        alpha=rr/np.sum(direction*ad)
        u+=alpha*direction;residual-=alpha*ad
        now=np.sum(residual*residual)
        if now<initial*1e-14:break
        preconditioned=residual/diagonal
        next_rr=np.sum(residual*preconditioned)
        direction=preconditioned+(next_rr/rr)*direction;rr=next_rr
    if now>=initial*1e-14:raise RuntimeError("Poisson solver did not converge")
    return u,{"iterations":step+1,"relative_residual":float(np.sqrt(now/initial)),
              "domain_cells":int(mask.sum()),"max_u_mm2":float(u.max())}


def profile(pitch):
    outer,inner=cubic(P.OUTER)*1000,cubic(P.INNER)*1000
    inner+=np.array([P.INNER_Y_OFFSET,P.INNER_Z_OFFSET])*1000
    outer=np.stack(warp(outer[:,0],outer[:,1]),1)
    inner=np.stack(warp(inner[:,0],inner[:,1]),1)
    y=np.arange(np.floor(outer[:,0].min())-3,np.ceil(outer[:,0].max())+3,pitch)
    z=np.arange(np.floor(outer[:,1].min())-3,np.ceil(outer[:,1].max())+3,pitch)
    yy,zz=np.meshgrid(y,z,indexing="ij")
    mask=polygon_inside(yy,zz,outer)&~polygon_inside(yy,zz,inner)
    distance=boundary_distance(yy,zz,[outer,inner])
    u,report=solve(mask,pitch,distance)
    return y,z,mask,u,distance,report


def width_field(yy,zz):
    taper=P.REAR_FOOT_RATIO+(1-P.REAR_FOOT_RATIO)*np.clip((yy+20)/260,0,1)
    return (P.BODY_HALF_WIDTH*1000 + P.FOOT_EXTRA_HALF_WIDTH*1000*taper*np.exp(-(zz/(P.FOOT_BLEND_HEIGHT*1000))**2)
           +P.SHOULDER_EXTRA_HALF_WIDTH*1000*np.exp(-((yy-45)/32)**2-((zz-125)/32)**2))


def build(pitch_mm=None):
    pitch=pitch_mm or P.GRID*1000
    y,z,mask,u,distance,report=profile(pitch)
    yy,zz=np.meshgrid(y,z,indexing='ij')
    width=width_field(yy,zz)
    gradient=np.where(mask,u/np.maximum(distance,pitch*.001),0)
    weight=mask.astype(float)
    # Extend the normal derivative beyond the boundary for a continuous field.
    numerator=gradient.copy()
    for _ in range(16):
        numerator=(numerator*4+np.roll(numerator,1,0)+np.roll(numerator,-1,0)+
                   np.roll(numerator,1,1)+np.roll(numerator,-1,1))/8
        weight=(weight*4+np.roll(weight,1,0)+np.roll(weight,-1,0)+
                np.roll(weight,1,1)+np.roll(weight,-1,1))/8
    slope=numerator/np.maximum(weight,1e-10)
    extended=np.where(mask,u,-distance*slope)
    scale=P.POISSON_SHAPE_SCALE*1e6
    q=np.where(mask,extended/(extended+scale),-np.maximum(.0001,np.minimum(.5,-extended/scale)))
    extent=np.ceil(width.max())+3
    x=np.arange(-extent,extent+pitch,pitch)
    field=(x[:,None,None]/width[None,:,:])**2-q[None,:,:]
    # Planar ground and rail seat. The silhouette extends below ground.
    field=np.maximum(field,-zz[None,:,:]/10)
    seat=(P.RAIL_HEIGHT-2*P.RAIL_HALF_THICKNESS+0.0005)*1000
    field=np.maximum(field,(zz[None,:,:]-seat)/10)
    verts,quads=marching_tetrahedra(field.astype(np.float32),(x[0],y[0],z[0]),pitch)
    corrected=taubin(verts,quads,8)
    shift=np.linalg.norm(corrected-verts,axis=1)
    corrected[:,2]=np.maximum(corrected[:,2],0)
    report.update({"pitch_mm":pitch,"vertices":len(verts),"max_smoothing_shift_mm":float(shift.max()),
                   "mean_smoothing_shift_mm":float(shift.mean())})
    print("POISSON",json.dumps(report),flush=True)
    return corrected/1000,quads,report
