"""Small fit tests derived from actual CAD; not extra assembly components."""
import pathlib,sys,json,math,shutil
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
import bpy
from mathutils import Matrix
from cad_utils import *
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
D=json.loads((R/'assembly_manifest.json').read_text());OUT=R/'coupons';OUT.mkdir(exist_ok=True);rows=[]
cup=bpy.data.objects['06_horn_cup_journal'];cup.matrix_world=pivot_transform(*D['O'],math.radians(D['servo_range_deg'][0])).inverted()@cup.matrix_world
def sample(name,source,lo,hi,T,note):
    o=duplicate(bpy.data.objects[source],name);boolean(o,cube('sample window',lo,hi),'INTERSECT')
    bounds=export(o,OUT/(name+'.stl'),T);rows.append(dict(name=name,source=source,bounds_mm=bounds,purpose_ja=note));bpy.data.objects.remove(o,do_unlink=True)
up=Matrix.Rotation(-math.pi/2,4,'Y');down=Matrix.Rotation(math.pi/2,4,'Y');roofdown=Matrix.Rotation(math.pi,4,'Y')
sample('test_01_servo_cradle','04_main_cassette',(4,18.7,24),(31.2,51.3,43.3),up,'手元のSG92R本体・耳・配線の上入れ確認。無理に押さない。')
sample('test_02_actual_horn_pocket','06_horn_cup_journal',(37.2,0,0),(42.1,80,80),down,'付属十字ホーンの翼形状と0.3 mmクリアランスを確認。スプラインは印刷しない。')
bar=cube('test_03_bearing_bar',(0,0,0),(4,50,22))
for y,d in ((8,5.6),(21,6.6),(39,12.6)):cut(bar,cyl('bearing nominal', (2,y,11),d/2,5))
rows.append(dict(name=bar.name,bounds_mm=export(bar,OUT/(bar.name+'.stl'),up),purpose_ja='D5.6/D6.6/D12.6 mmの軸受け。対応軸が指で軽く回ることを確認。'))
for n,src in [('test_04_actual_axle5','11_drive_axle'),('test_05_actual_axle6','10_hinge_axle'),('test_08_actual_front_rocker','08_front_rocker')]:
    shutil.copyfile(R/'stl'/(src+'.stl'),OUT/(n+'.stl'));rows.append(dict(name=n,source=src,purpose_ja='本体用の実部品を同じ印刷向きで試験。適合すれば本組立へ再利用可能。'))
sample('test_06_actual_journal','06_horn_cup_journal',(46.2,0,0),(58,80,80),down,'D12 mmジャーナルを本部品と同じ向き・端面で印刷する嵌合試験。')
sample('test_07_roof_dock','03_planar_lid',(40.7,40,57.3),(56.1,52,70),roofdown,'前側ロッカーの一体ペグを屋根の穴へ通し、抜き差しできることを確認。')
sample('test_09_cover_socket','02_fixed_rear_cover',(8.5,3.5,58),(15,12.5,70),roofdown,'後部固定カバーの45°菱形穴。相手ペグと0.3 mm隙間。')
sample('test_10_cover_peg','04_main_cassette',(4,5.4,60.4),(14.1,10.6,67.3),up,'カセットの一体ペグ。カバー試験片に挿入し、強い圧入を避ける。')
sample('test_11_side_key_access','01_body',(64,54,38),(70,70,50),Matrix.Identity(4),'側面キー入口の10.2 mm橋渡しと外面の仕上がりを先に確認。')
sample('test_12_side_key_end','13_body_cross_key',(60,0,0),(70,80,80),Matrix.Identity(4),'キー頭部と側面入口の嵌合。入口のブリッジ垂れが引っかからないことを確認。')
(R/'coupon_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print('COUPONS',len(rows),flush=True)
