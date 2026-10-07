"""Flatten installed official Bambu profiles; offline test only."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
P=Path(r'C:\Program Files\Bambu Studio\resources\profiles\BBL')
files={f.stem:f for f in P.rglob('*.json')}
def resolve(name,seen=()):
    assert name not in seen
    p=files[name];d=json.loads(p.read_text('utf-8-sig'))
    result=resolve(d['inherits'],seen+(name,)) if d.get('inherits') else {}
    result.update(d);result.pop('inherits',None);return result
machine=resolve('Bambu Lab X1 Carbon 0.4 nozzle')
process=resolve('0.20mm Standard @BBL X1C')
filament=resolve('Bambu PLA Basic @BBL X1C')
process.update(layer_height='0.2',wall_loops='4',top_shell_layers='5',bottom_shell_layers='5',sparse_infill_density='20%',enable_support='0',support_threshold_angle='45',support_type='normal(manual)',support_on_build_plate_only='0',support_top_z_distance='0.2',support_bottom_z_distance='0.2',support_object_xy_distance='0.35',brim_width='3',enable_prime_tower='0',outer_wall_speed=['60','60'],small_perimeter_speed=['30%','30%'])
for fn,d in [('machine_x1c_flat.json',machine),('process_no_support.json',process),('filament_pla_flat.json',filament)]:
    (R/fn).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
manual=dict(process);manual.update(enable_support='1')
(R/'process_manual_support.json').write_text(json.dumps(manual,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'machine':machine['name'],'process':process['name'],'filament':filament['name'],'support_route':'manual marked facets only; not global auto support'},ensure_ascii=False))
