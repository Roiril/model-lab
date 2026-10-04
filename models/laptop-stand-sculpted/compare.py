"""Hand-traced source silhouette and quantitative, camera-controlled comparison.

The trace is not extracted by colour: the background and cream object overlap
in luminance. Source pixels are never treated as an orthographic side drawing.
"""
import sys,json,math
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from verify import parse_stl
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/"exports/laptop-stand-sculpted"

SOURCE_OUTER=[(215,222),(237,221),(255,225),(626,341),(638,351),(652,347),(677,343),
 (686,345),(688,353),(684,363),(675,369),(650,373),(634,374),(324,299),(307,297),
 (291,303),(282,316),(279,335),(284,357),(296,385),(318,417),(344,449),
 (389,500),(435,551),(480,603),(526,656),(570,708),(612,754),(647,792),
 (656,803),(657,810),(651,815),(622,825),(581,836),(558,840),(539,839),
 (510,833),(435,800),(367,773),(302,752),(233,736),(167,724),(112,712),
 (81,702),(71,695),(70,687),(76,676),(92,665),(118,653),(150,641),
 (180,628),(211,611),(239,590),(263,565),(282,537),(292,514),(294,495),
 (289,477),(273,451),(247,414),(221,375),(199,337),(184,303),(175,276),
 (174,263),(178,251),(187,243),(200,238),(216,236)]
SOURCE_HOLE=[(348,550),(364,570),(383,600),(401,629),(411,650),(414,668),
 (411,685),(402,700),(391,714),(379,711),(359,701),(345,687),(336,674),
 (332,659),(332,642),(335,622),(342,600),(349,580)]


def source_mask(size=(768,512)):
    canvas=Image.new("L",(1536,1024));draw=ImageDraw.Draw(canvas)
    draw.polygon(SOURCE_OUTER,fill=255);draw.polygon(SOURCE_HOLE,fill=0)
    return canvas.resize(size,Image.Resampling.NEAREST)


def metric(a,b):
    a=np.asarray(a)>127;b=np.asarray(b)>127
    return float(np.sum(a&b)/np.sum(a|b))


def boundary_points(mask):
    a=np.asarray(mask)>127
    interior=a & np.roll(a,1,0) & np.roll(a,-1,0) & np.roll(a,1,1) & np.roll(a,-1,1)
    return np.argwhere(a & ~interior).astype(float)


def contour_distance(a,b):
    a,b=boundary_points(a),boundary_points(b)
    distances=[]
    for p,q in [(a,b),(b,a)]:
        for start in range(0,len(p),400):
            d=p[start:start+400,None,:]-q[None,:,:]
            distances.extend(np.sqrt((d*d).sum(2).min(1)).tolist())
    return float(np.mean(distances)*2),float(np.percentile(distances,95)*2)


def project(v,az,el):
    az,el=math.radians(az),math.radians(el)
    # Matches Blender camera looking towards the model with world Z upright.
    right=np.array([-math.sin(az),math.cos(az),0])
    down=np.array([math.sin(el)*math.cos(az),math.sin(el)*math.sin(az),-math.cos(el)])
    return np.stack((v@right,v@down),axis=1)


def raster(v,f,az,el,shift=(0,0),size=(768,512)):
    p=project(v,az,el)
    low=p.min(0);high=p.max(0)
    scale=(840-221)/(high[1]-low[1])*.5
    centre=np.array([(70+688)/4,(221+840)/4])
    p=(p-(low+high)/2)*scale+centre+np.array(shift)
    im=Image.new("L",size);d=ImageDraw.Draw(im)
    for face in f:d.polygon([tuple(q) for q in p[face]],fill=255)
    return im


def main():
    reference=source_mask()
    assert metric(reference,reference)==1
    shifted=Image.new("L",reference.size);shifted.paste(reference,(30,0))
    assert metric(reference,shifted)<.8
    v,f=parse_stl(ROOT/"exports/laptop-stand-sculpted-unit.stl")
    # Mesh for camera search only, with one quarter of the longitudinal samples.
    # Decimate deterministically within Blender for search, then measure full STL.
    search=OUT/"search.stl"
    sv,sf=parse_stl(search) if search.exists() else (v,f)
    best=(-1,None,None,None)
    fixed="--fixed" in sys.argv
    for az in ([54] if fixed else range(28,57,4)):
        for el in ([12] if fixed else range(10,25,2)):
            mask=raster(sv,sf,az,el)
            score=metric(reference,mask)
            if score>best[0]:best=(score,az,el,mask)
    score,az,el,mask=best
    for aa in ([] if fixed else np.arange(az-3,az+3.1,1)):
        for ee in np.arange(el-2,el+2.1,1):
            current=raster(sv,sf,aa,ee)
            now=metric(reference,current)
            if now>score:score,az,el,mask=now,float(aa),float(ee),current
    full=raster(v,f,az,el)
    # Allow a small translation; never distort or independently scale X and Y.
    for dx in range(-8,9,2):
        for dy in range(-8,9,2):
            moved=Image.new("L",full.size);moved.paste(full,(dx,dy))
            now=metric(reference,moved)
            if now>score:score,mask,shift=now,moved,(dx,dy)
    shift=locals().get("shift",(0,0))
    full=raster(v,f,az,el,shift)
    score=metric(reference,full)
    mean_distance,p95=contour_distance(reference,full)
    full.save(OUT/"model-mask.png");reference.save(OUT/"source-mask.png")
    original=Image.open(HERE/"design/original.png").convert("RGB").resize(reference.size)
    a=np.array(reference)>127;b=np.array(full)>127
    overlay=np.array(original,dtype=float)
    overlay[a&~b]=overlay[a&~b]*.45+np.array([213,94,0])*.55
    overlay[b&~a]=overlay[b&~a]*.45+np.array([0,114,178])*.55
    Image.fromarray(overlay.astype("uint8")).save(OUT/"overlay.png")
    results={"silhouette_iou":score,"source":"hand trace of original foreground unit",
             "camera_azimuth_deg":az,"camera_elevation_deg":el,"translation_halfsize_px":shift,
             "calibration":{"identical_iou":1,"shifted_iou":metric(reference,shifted)},
             "trace_uncertainty_original_px":3,"no_anisotropic_scaling":True}
    results["mean_contour_distance_original_px"]=mean_distance
    results["p95_contour_distance_original_px"]=p95
    (OUT/"comparison.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps(results,indent=2))


if __name__=="__main__":main()
