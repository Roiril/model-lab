"""Actual revision3 underside and cutaway capture, no conceptual replacement."""
from pathlib import Path
R=Path(__file__).resolve().parent
prefix=(R/'render_preview.py').read_text('utf8').split('setpose(0);camera((155')[0]
exec(compile(prefix,str(R/'render_preview.py'),'exec'))
setpose(0)
camera((130,-85,-120),(35,28,18),145)
render('bottom_assembled_actual.png')
bpy.data.objects['01_body'].hide_render=True
for o in bpy.data.objects:
 if o.name.startswith('REFERENCE') or o.name in ['02_fixed_rear_cover','03_planar_lid']:o.hide_render=True
camera((125,-95,-65),(35,28,15),145)
render('bottom_key_capture_actual.png')
print('BOTTOM KEY VIEWS SAVED',flush=True)
