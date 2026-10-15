"""Involute tooth boundaries in the v,d plane, in millimetres."""
import math
import numpy as np
from . import params as P


def tooth(center_deg):
    rp=P.PITCH_RADIUS*1000
    rb=rp*math.cos(math.radians(P.PRESSURE_ANGLE_DEG))
    rr=P.ROOT_RADIUS*1000
    ra=P.TIP_RADIUS*1000
    half=(math.pi*rp/P.TEETH-P.BACKLASH*1000/2)/(2*rp)
    ip=math.tan(math.radians(P.PRESSURE_ANGLE_DEG))-math.radians(P.PRESSURE_ANGLE_DEG)
    def angle(r):
        a=math.acos(min(1.,rb/r))
        return half+ip-(math.tan(a)-a)
    radii=[rr]+list(np.linspace(rb,ra,14))
    flank=[(r,math.radians(center_deg)-angle(r)) for r in radii]
    top=angle(ra)
    flank += [(ra,math.radians(center_deg)+a) for a in np.linspace(-top,top,7)[1:]]
    flank += [(r,math.radians(center_deg)+angle(r)) for r in radii[-2::-1]]
    return [(r*math.cos(a),r*math.sin(a)) for r,a in flank]


def outline(phase=0.,sector=False):
    centers=P.SECTOR_TEETH_DEG if sector else [phase+20*i for i in range(P.TEETH)]
    points=[]
    if sector:
        points=[(0.,0.),(P.ROOT_RADIUS*1000,0.)]
    for index,c in enumerate(centers):
        pts=tooth(c)
        if points and (index or sector):
            a0=math.atan2(points[-1][1],points[-1][0])
            a1=math.atan2(pts[0][1],pts[0][0])
            while a1<a0: a1+=2*math.pi
            points.extend([(P.ROOT_RADIUS*1000*math.cos(a),P.ROOT_RADIUS*1000*math.sin(a))
                           for a in np.linspace(a0,a1,5)[1:-1]])
        points.extend(pts)
    if sector:
        a0=math.degrees(math.atan2(points[-1][1],points[-1][0]))
        for a in np.linspace(a0,P.SECTOR_END_DEG,18)[1:]:
            f=min(1.,max(0.,(a-94)/6))
            r=1000*(P.ROOT_RADIUS+(P.TAIL_ROOT_RADIUS-P.ROOT_RADIUS)*f)
            points.append((r*math.cos(math.radians(a)),r*math.sin(math.radians(a))))
    else:
        a0=math.atan2(points[-1][1],points[-1][0])
        a1=math.atan2(points[0][1],points[0][0])
        while a1<a0: a1+=2*math.pi
        points.extend([(P.ROOT_RADIUS*1000*math.cos(a),P.ROOT_RADIUS*1000*math.sin(a))
                       for a in np.linspace(a0,a1,5)[1:-1]])
    return points
