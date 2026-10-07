import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
import math
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def inspect(triangles):
    if not triangles:
        raise AssertionError("Empty STL")
    edges = Counter()
    signed = 0.0
    parents = {}
    zero = 0
    def find(x):
        parents.setdefault(x, x)
        while parents[x] != x:
            parents[x] = parents[parents[x]]
            x = parents[x]
        return x
    for a, b, c in triangles:
        ab = tuple(b[i] - a[i] for i in range(3))
        ac = tuple(c[i] - a[i] for i in range(3))
        cross = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
        if math.sqrt(sum(v*v for v in cross)) == 0:
            zero += 1
        signed += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for v, w in [(a,b),(b,c),(c,a)]:
            edges[tuple(sorted((v,w)))] += 1
            parents[find(w)] = find(v)
    vertices = list(parents)
    lo = [min(v[i] for v in vertices) for i in range(3)]
    hi = [max(v[i] for v in vertices) for i in range(3)]
    result = dict(triangles=len(triangles),vertices=len(vertices),min_mm=lo,max_mm=hi,
                  dimensions_mm=[hi[i]-lo[i] for i in range(3)],
                  nonmanifold_edges=sum(n!=2 for n in edges.values()),zero_area_faces=zero,
                  signed_volume_mm3=signed,components=len({find(v) for v in vertices}))
    assert result["nonmanifold_edges"] == 0, result
    assert zero == 0 and signed > 0, result
    return result

def read_stl(file):
    data = file.read_bytes()
    count, = struct.unpack_from("<I", data, 80)
    assert len(data) == 84 + 50*count, "Unexpected binary STL size"
    triangles = []
    for i in range(count):
        values = struct.unpack_from("<12f", data, 84 + i*50)
        triangles.append(tuple(tuple(values[3+j*3:6+j*3]) for j in range(3)))
    return triangles

def cross_section_size(triangles, height):
    points=[]
    for tri in triangles:
        for a,b in zip(tri,tri[1:]+tri[:1]):
            if min(a[2],b[2]) < height < max(a[2],b[2]):
                t=(height-a[2])/(b[2]-a[2])
                points.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
    assert points, "Missing cross section"
    return [max(p[i] for p in points)-min(p[i] for p in points) for i in range(2)]

def ray_heights(triangles, x, y):
    hits=[]
    for a,b,c in triangles:
        denominator=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(denominator)<1e-12:
            continue
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/denominator
        v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/denominator
        w=1-u-v
        if min(u,v,w)>=-1e-8:
            hits.append(u*a[2]+v*b[2]+w*c[2])
    return sorted({round(z,4) for z in hits})

def close(actual, expected):
    assert len(actual)==len(expected)
    assert all(abs(a-e)<0.015 for a,e in zip(actual,expected)), (actual,expected)

# 正常な四面体と、面を1枚落とした異常例で検査を校正する。
a,b,c,d=(0.,0.,0.),(1.,0.,0.),(0.,1.,0.),(0.,0.,1.)
tetra=[(a,c,b),(a,b,d),(b,c,d),(c,a,d)]
assert inspect(tetra)["components"]==1
try:
    inspect(tetra[:-1])
except AssertionError:
    pass
else:
    raise AssertionError("Open mesh was accepted")

results={"calibration":"closed tetrahedron passes; missing face fails","files":{}}
meshes={}
for suffix,dims,components in [("",[37,17,32],3),("-body",[32,12,30.5],1),("-horn",[34,17,4.5],1),("-wire",[8,4,1.6],1)]:
    name="sg92r-photo"+suffix+".stl"
    tri=read_stl(ROOT/"exports"/name)
    result=inspect(tri)
    close(result["dimensions_mm"],dims)
    assert result["components"]==components,result
    meshes[suffix]=tri
    results["files"][name]=result
body,horn=meshes["-body"],meshes["-horn"]
sections=[]
for z,expected in [(10,[23,12]),(17,[32,12]),(24,[14,12]),(29,[4.6,4.6])]:
    actual=cross_section_size(body,z)
    close(actual,expected)
    sections.append({"z_mm":z,"dimensions_mm":actual})
results["body_cross_sections"]=sections
close(ray_heights(body,-20,3),[16,18])
close(ray_heights(horn,-10,1),[30.5,32])
# 上面写真の丸穴と外端へ抜ける幅1mmの溝を検査する。
mount_centers=[-5-28.84/2,-5+28.84/2]
for x in mount_centers:
    for y in [-0.99,0,0.99]:
        assert not ray_heights(body,x,y),(x,y,"Mount hole blocked")
    for y in [-1.01,1.01]:
        close(ray_heights(body,x,y),[16,18])
for x in [-20.8,10.8]:
    for y in [-0.49,0,0.49]:
        assert not ray_heights(body,x,y),(x,y,"Mount slot blocked")
    for y in [-0.51,0.51]:
        close(ray_heights(body,x,y),[16,18])
results["mounting_features"]={"hole_diameter_mm":2,"open_slot_width_mm":1,"center_spacing_mm":28.84}
# 小円の中心を通る平面形状は幅4mm。幅12mmのカプセルが残っていないことも見る。
for y in [-1.99,1.99]:
    close(ray_heights(body,-6,y),[0,27])
for y in [-2.01,2.01]:
    close(ray_heights(body,-6,y),[0,22])
results["gear_cover"]={"length_mm":14,"main_diameter_mm":12,"neck_diameter_mm":4,"neck_center_x_mm":-6}
wire=meshes["-wire"]
close(results["files"]["sg92r-photo-wire.stl"]["min_mm"],[6.5,-2,4.2])
close(results["files"]["sg92r-photo-wire.stl"]["max_mm"],[14.5,2,5.8])
results["wire"]={"width_mm":4,"display_length_mm":8,"provisional_thickness_mm":1.6,"exit_side":"+X"}
holes=[(x,0) for x in [-16.5,-14.5,-12.5,-10.5,-8.5,-6.5,-4.5,5,7,9,11,13,15]]
holes.extend((0,y) for y in [-6.8,-4.8,4.8,6.8])
holes.append((0,0))
for x,y in holes:
    assert not ray_heights(horn,x,y),(x,y,"Hole blocked")
results["open_horn_holes"]=len(holes)
target=ROOT/"exports"/"sg92r-photo-verification.json"
target.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8",newline="\n")
print(json.dumps(results,ensure_ascii=False,indent=2))
