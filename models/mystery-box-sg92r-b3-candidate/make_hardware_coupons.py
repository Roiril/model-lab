"""Regenerate hardware coupons after CAD changes; re-audit/re-slice afterwards.
Does not run in the frozen-preview registration. Shipped coupons are frozen.
"""
from pathlib import Path
import sys,json,math,shutil
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
import bpy
from mathutils import Matrix
from cad_utils import *
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_B3.blend'))
D=json.loads((R/'assembly_manifest.json').read_text());cup=bpy.data.objects['06_horn_cup_journal']
cup.matrix_world=pivot_transform(*D['O'],math.radians(D['servo_range_deg'][0])).inverted()@cup.matrix_world
out=R/'coupons';out.mkdir(exist_ok=True)
up=Matrix.Rotation(-math.pi/2,4,'Y');down=Matrix.Rotation(math.pi/2,4,'Y')
for name,src,lo,hi,T in [('test_01_servo_cradle','04_main_cassette',(4,18.7,24),(31.2,51.3,43.3),up),('test_02_actual_horn_pocket','06_horn_cup_journal',(37.2,0,0),(42.1,80,80),down),('test_25_actual_U_support','04_main_cassette',(4,24.5,24),(37.1,55.5,49.4),up)]:
 o=duplicate(bpy.data.objects[src],name);boolean(o,cube('actual coupon window',lo,hi),'INTERSECT');export(o,out/(name+'.stl'),T);bpy.data.objects.remove(o,do_unlink=True)
shutil.copy2(R/'stl/06_horn_cup_journal.stl',out/'test_26_actual_cup_with_support.stl')
print('Hardware coupons regenerated: revalidate before printing.',flush=True)
