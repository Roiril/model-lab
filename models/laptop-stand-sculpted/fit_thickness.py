"""Fit five smooth width controls, with a fixed source camera.

This projects filled transverse intervals. Small smooth profile warps are
bounded so individual control points cannot develop oscillations. Final scores are independently
measured from every exported STL triangle by compare.py.
"""
import sys,json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image,ImageDraw
import params as P
from poisson_body import profile,width_field,warp
from compare import source_mask,project,metric

OUT=Path(__file__).resolve().parents[2]/'exports/laptop-stand-sculpted'
INITIAL=[P.BODY_HALF_WIDTH*1000,P.FOOT_EXTRA_HALF_WIDTH*1000,P.SHOULDER_EXTRA_HALF_WIDTH*1000,
         P.FOOT_BLEND_HEIGHT*1000,P.REAR_FOOT_RATIO,0,0,P.PROFILE_MID_SHIFT*1000,
         P.PROFILE_SHOULDER_SHIFT*1000,P.PROFILE_WINDOW_SHIFT*1000,P.PROFILE_WINDOW_LIFT*1000]
P.PROFILE_MID_SHIFT=P.PROFILE_SHOULDER_SHIFT=P.PROFILE_WINDOW_SHIFT=P.PROFILE_WINDOW_LIFT=0
pitch=.75
y,z,mask,u,_,_=profile(pitch)
yy,zz=np.meshgrid(y,z,indexing='ij')
mask&=(zz>=0)&(zz<=140.5)
ys,zs=yy[mask],zz[mask]
radius=np.sqrt(u[mask]/(u[mask]+P.POISSON_SHAPE_SCALE*1e6))
angles=np.arange(48)*2*np.pi/48
rail=[]
for yr in np.linspace(P.RAIL_START*1000,P.RAIL_END*1000,250):
    t=np.clip((yr-(P.RAIL_END*1000-17))/17,0,1)
    edge=min(yr-P.RAIL_START*1000,P.RAIL_END*1000-yr)
    w=P.RAIL_HALF_WIDTH*1000-10+np.sqrt(max(0,100-max(0,10-edge)**2))
    rail.extend([(w*np.sign(np.cos(a))*abs(np.cos(a))**(1/3),yr,
                  P.RAIL_HEIGHT*1000-P.RAIL_HALF_THICKNESS*1000+
                  P.LIP_HEIGHT*1000*(3*t*t-2*t*t*t)+P.RAIL_HALF_THICKNESS*1000*np.sign(np.sin(a))*abs(np.sin(a))**(1/3)) for a in angles])
rail=project(np.array(rail),54,12).reshape(250,48,2)
reference=source_mask((384,256))


def raster(values):
    body,foot,shoulder,height,rear,dx,dy,mid,upper,window,lift=values
    P.BODY_HALF_WIDTH=body/1000;P.FOOT_EXTRA_HALF_WIDTH=foot/1000
    P.SHOULDER_EXTRA_HALF_WIDTH=shoulder/1000;P.FOOT_BLEND_HEIGHT=height/1000;P.REAR_FOOT_RATIO=rear
    P.PROFILE_MID_SHIFT=mid/1000;P.PROFILE_SHOULDER_SHIFT=upper/1000
    P.PROFILE_WINDOW_SHIFT=window/1000;P.PROFILE_WINDOW_LIFT=lift/1000
    yw,zw=warp(ys,zs)
    h=width_field(yw,zw)*radius
    start=project(np.stack((-h,yw,zw),1),54,12)
    end=project(np.stack((h,yw,zw),1),54,12)
    bounds=np.concatenate((start,end,rail.reshape(-1,2)))
    low,high=bounds.min(0),bounds.max(0)
    scale=(840-221)/(high[1]-low[1])*.25
    centre=np.array([(70+688)/8,(221+840)/8])+np.array([dx,dy])
    offset=centre-(low+high)/2*scale
    start=start*scale+offset;end=end*scale+offset
    image=Image.new('L',(384,256));draw=ImageDraw.Draw(image)
    for a,b in zip(start,end):draw.line((*a,*b),fill=255,width=max(1,round(pitch*scale*1.4)))
    r=rail*scale+offset
    for a,b in zip(r,r[1:]):
        for k in range(48):draw.polygon([tuple(a[k]),tuple(a[(k+1)%48]),tuple(b[(k+1)%48]),tuple(b[k])],fill=255)
    return image


def main():
    values=np.array(INITIAL,float)
    low=np.array([6,4,0,5,.2,-5,-5,-12,-8,-10,-8]);high=np.array([20,22,14,28,1,5,5,12,8,10,8])
    steps=np.array([2,2,2,3,.15,1,1,3,2,2,2],float)
    best=metric(reference,raster(values));print('INITIAL',best,flush=True)
    for stage in range(4):
        for sweep in range(5):
            improvement=False
            for k in range(len(values)):
                chosen=values.copy()
                for sign in (-1,1):
                    candidate=values.copy();candidate[k]=np.clip(candidate[k]+sign*steps[k],low[k],high[k])
                    score=metric(reference,raster(candidate))
                    if score>best:chosen=candidate;best=score;improvement=True
                values=chosen
            print('FIT',stage,sweep,round(best,5),values.tolist(),flush=True)
            if not improvement:break
        steps*=.5
    result={'surrogate_iou':best,'camera_deg':[54,12],
            'body_half_width_mm':values[0],'foot_extra_mm':values[1],
            'shoulder_extra_mm':values[2],'foot_blend_height_mm':values[3],
            'rear_foot_ratio':values[4],'translation_quartersize_px':values[5:7].tolist(),
            'profile_mid_shift_mm':values[7],'profile_shoulder_shift_mm':values[8],
            'profile_window_shift_mm':values[9],'profile_window_lift_mm':values[10]}
    (OUT/'fitted-thickness.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    raster(values).save(OUT/'thickness-fit-mask.png')


if __name__=='__main__':main()
