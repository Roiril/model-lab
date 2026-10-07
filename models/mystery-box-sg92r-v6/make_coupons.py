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
sample('test_02_actual_horn_pocket','06_horn_cup_journal',(37.2,0,0),(42.1,80,80),down,'付属十字ホーンの翼形状と0.3 mmクリアランスを確認。輪郭確認用で、軸方向の捕捉強度の試験ではない。スプラインは印刷しない。')
bar=cube('test_03_bearing_bar',(0,0,0),(4,50,22))
for y,d in ((8,5.6),(21,6.6),(39,12.6)):cut(bar,cyl('bearing nominal', (2,y,11),d/2,5))
rows.append(dict(name=bar.name,bounds_mm=export(bar,OUT/(bar.name+'.stl'),up),purpose_ja='D5.6/D6.6/D12.6 mmの軸受け。対応軸が指で軽く回ることを確認。'))
for n,src in [('test_04_actual_axle5','11_drive_axle'),('test_05_actual_axle6','10_hinge_axle'),('test_08_actual_front_rocker','08_front_rocker')]:
    shutil.copyfile(R/'stl'/(src+'.stl'),OUT/(n+'.stl'));rows.append(dict(name=n,source=src,purpose_ja='本体用の実部品を同じ印刷向きで試験。適合すれば本組立へ再利用可能。'))
sample('test_06_actual_journal','06_horn_cup_journal',(46.8,0,0),(58,80,80),down,'D12 mmジャーナルの先端と径を同じ向きで確認。支持用段より先だけの試験片。全カップの印刷/保持強度試験ではない。')
sample('test_07_roof_dock','03_planar_lid',(40.7,40,57.3),(56.1,52,70),roofdown,'前側ロッカーの一体ペグを屋根の穴へ通し、抜き差しできることを確認。')
sample('test_09_cover_socket','02_fixed_rear_cover',(8.5,3.5,58),(15,12.5,70),roofdown,'後部固定カバーの45°菱形穴。相手ペグと0.3 mm隙間。')
sample('test_10_cover_peg','04_main_cassette',(4,5.4,60.4),(14.1,10.6,67.3),up,'カセットの一体ペグ。カバー試験片に挿入し、強い圧入を避ける。')
sample('test_11_bottom_key_floor','01_body',(20.,1.,0),(53.,48.,8.2),Matrix.Identity(4),'実際の底面回転座と長い挿入窓。キーを90度で下から入れ、0度まで軽く回す。ばね/結束バンドは不要。回転端/工具/傷と指での着脱を確認。')
shutil.copyfile(R/'stl/13_body_cross_key.stl',OUT/'test_12_actual_bottom_key.stl');rows.append(dict(name='test_12_actual_bottom_key',source='13_body_cross_key',purpose_ja='本体に再利用できる厚い底面キー。床座と両方の足27/28で0度の引抜き止めと90度の解除を確認。角度は自動固定されない。'))
sample('test_13_keeper_rear_socket','04_main_cassette',(4,22.4,42.7),(9.2,29.8,48.3),up,'52.7mm実寸押さえの後受け。独立隙間0.3/面取り0.45を確認。')
sample('test_14_keeper_front_socket','05_front_closure',(55.7,22.4,42.7),(61.3,29.8,48.3),down,'実寸押さえの前受け。後受けと同時に、指で滑り入ることを確認。')
shutil.copyfile(R/'stl/14_servo_top_keeper.stl',OUT/'test_15_actual_long_keeper.stl');rows.append(dict(name='test_15_actual_long_keeper',source='14_servo_top_keeper',purpose_ja='全長52.7mmの実部品。両端受けと組み合わせ、たわみ/反りと組立向きを確認。適合品は再利用可。'))
shutil.copyfile(R/'stl/17_local_cup_capture.stl',OUT/'test_16_actual_local_capture.stl');rows.append(dict(name='test_16_actual_local_capture',source='17_local_cup_capture',purpose_ja='局所捕捉肩の実部品。寝かせて支持なし。ジャーナル/舌/盲受けを試験、適合品は再利用可。'))
sample('test_17_local_capture_socket','04_main_cassette',(45.5,13.5,18),(52.1,19.2,25),up,'捕捉肩の盲受け。0.15mm軸方向隙間と短い橋渡し。17の実寸部品と手で滑り嵌めする。')
sample('test_18_body_receiver','01_body',(53.4,3.,16.),(70.,11.,26.),Matrix.Identity(4),'0.2mm片側隙間の外壁へ一体接続した実受け。実前板試験片と比較。')
sample('test_19_closure_foot','05_front_closure',(56.1,5.4,18),(61.3,10.6,26),down,'実前板の足。receiver試験片へ軽く入ること。無理な圧入をしない。')
sample('test_20_capture_rear_socket','04_main_cassette',(45.5,48.5,14.),(52.1,56.2,19.),up,'局所捕捉肩の第2受け。舌を2箇所とも座へ入れ、18/19と05で保持したときに肩が傾かないことを全カセットでも確認。')
sample('test_21_front_stop_socket','04_main_cassette',(49.2,12.8,18.),(54.7,20.,25.),up,'前側の止め18の実受け。18を上入れし、17の抜け方向を止める。軸方向の0.1mm遊びは試験片と実物で確認。')
sample('test_22_rear_stop_socket','04_main_cassette',(49.2,48.8,14.),(54.7,56.2,19.),up,'後側の止め19の実受け。05の押さえ棚まで組むと上方向を捕捉。受け単体では止めは抜ける。')
for number in (18,19):
    name=f'test_{number+5}_actual_stop';src=f'{number}_local_capture_stop';shutil.copyfile(R/'stl'/(src+'.stl'),OUT/(name+'.stl'));rows.append(dict(name=name,source=src,purpose_ja='実止め部品。指で滑り入ることを受け試験片と確認。適合品は本組立に再利用可。'))
sample('test_25_actual_U_support','04_main_cassette',(4.,24.5,24.),(37.1,55.5,49.4),up,'04の実U受け・支持着地点・保護面を残す支持除去試験片。plate04の手動支持を使用。実物除去・嵌合は未検証。')
shutil.copyfile(R/'stl/06_horn_cup_journal.stl',OUT/'test_26_actual_cup_with_support.stl');rows.append(dict(name='test_26_actual_cup_with_support',source='06_horn_cup_journal',purpose_ja='06実部品そのもの。plate04で支持位置・内周ブリッジ・支持除去・ホーンと局所保持の面を確認。適合品は本組立へ再利用可。'))
sample('test_27_rear_retention_foot','04_main_cassette',(4.,23.5,3.),(22.,29.5,20.),up,'底キーで捕捉される後板の実足。0.3mm名目上下隙間と引抜き止めを全体組立でも確認。')
sample('test_28_front_retention_foot','05_front_closure',(51.,23.5,3.),(61.3,29.5,20.),down,'前板の実足。底キー先端との名目重なり3.7mm。強度/反り/実際の掛かりは未検証。')
(R/'coupon_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print('COUPONS',len(rows),flush=True)
