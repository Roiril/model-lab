import sys, math, json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import compose
import verify_envelopes as E
K=compose.face_package('link_lid','front')['kinematics']
interface=compose.read(HERE/'interface.json')
def hull(points):
    points=sorted(set(points))
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    low=[]; high=[]
    for p in points:
        while len(low)>1 and cross(low[-2],low[-1],p)<=0: low.pop()
        low.append(p)
    for p in reversed(points):
        while len(high)>1 and cross(high[-2],high[-1],p)<=0: high.pop()
        high.append(p)
    return low[:-1]+high[:-1]
def circle(v,d,r): return [(v+r*math.cos(t),d+r*math.sin(t)) for t in np.linspace(0,2*math.pi,48,endpoint=False)]
def prism(poly,u0,u1):
    n=len(poly); a=[(u0,*p) for p in poly]; b=[(u1,*p) for p in poly]; tri=[]
    for i in range(1,n-1): tri.extend([[a[0],a[i],a[i+1]],[b[0],b[i],b[i+1]]])
    for i in range(n):
        j=(i+1)%n; tri.extend([[a[i],a[j],b[j]],[a[i],b[j],b[i]]])
    return np.array(tri)
v,d=K.O
rect=[(v+x,d+y) for x,y in [(-17.5,-1.8),(-16.3,-1.8),(-16.3,-.6),(-17.5,-.6)]]
variants={'old':np.concatenate([prism(hull(circle(v,d,3.8)+circle(v-17.3,d,1.2)),7.75,10.75),prism(circle(v-17.3,d,1),5.75,8.05)]),
          'new':np.concatenate([prism(hull(circle(v,d,3.8)+rect),7.75,10.75),prism(rect,5.75,8.05)])}
for name,tri in variants.items():
    worst=(0,None)
    for angle in np.linspace(K.OPEN_SERVO,K.CLOSED_SERVO,691):
        transformed=E.transform_triangles(tri,K.rot_x(angle-K.SERVO_OFFSET,K.O))
        excess,_=E.envelope_violation(transformed,interface,.29)
        if excess>worst[0]: worst=(excess,float(angle))
    print(json.dumps({'variant':name,'margin_mm':.29,'max_excess_mm':worst[0],'servo_deg':worst[1]}),flush=True)
    assert (worst[0]>0) if name=='old' else (worst[0]==0)
