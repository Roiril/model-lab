"""Upright service support and full pusher travel, assumed household bench blocks."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent
exec((R/'check_local.py').read_text('utf8').split("report={'input_blend_sha256'")[0])
from cad_utils import cube,cyl
activate('editable_cube_B3.blend');cap=bpy.data.objects['21_separate_bolt_cap'];stop=bpy.data.objects['22_symmetric_cap_stop']
stands=[cube('ASSUMED stable left support',(-77,-15,-100),(3,85,0)),cube('ASSUMED stable right support',(67,-15,-100),(147,85,0))]
pusher=cyl('ASSUMED3mm service pusher',(36.5,16.4,-.9),1.5,37.8,'Z');home=pusher.matrix_world.copy();rows=[]
for h in range(21):
 restore();offset(bolt,x=5.9);keyangle(90,-31)
 for o in unit:offset(o,z=h)
 pusher.matrix_world=Matrix.Translation(Vector((0,0,h*.001)))@home
 hits=checks([pusher],[body,bolt,cap,stop,speaker]+[o for o in allobjs if o.name.startswith('REFERENCE speaker')]+unit+stands)
 if hits:rows.append({'unit_lift_mm':h,'hits':hits})
report={'source_blend_sha256':hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),'physical_tested':False,'support_top_contact_X_mm':[[0,3],[67,70]],'clear_underside_width_mm':64,'assumed_support_height_mm':100,'required_tool_clearance_min_mm':85,'assumed_stable_block_bounds_mm':[[[-77,-15,-100],[3,85,0]],[[67,-15,-100],[147,85,0]]],'pusher_tip_XYZ_home_mm':[36.5,16.4,18],'pusher_D_mm':3,'full_pusher_and_unit_lift_samples':21,'obstacles':rows,'limits':'No human hand, friction, tipping, slipping or real table qualification. Support only hard outer floor edges; hold unit at fixed cassette top, keep lid closed and unloaded. Stop if binding or support moves. No prying.'}
(R/'bench_support_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('FULL_PUSHER',len(rows),flush=True)
