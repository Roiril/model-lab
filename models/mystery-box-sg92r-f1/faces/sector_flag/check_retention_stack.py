"""Measure the cap's serial clearances, including the purchased actuator group."""
import sys,importlib.util,json
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('candidate_check',HERE/'check_local.py')
C=importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
from printmech.solid_meter import translation,first_contact
from sector_flag_local.evidence import require_meshes
require_meshes(HERE)
manifest=json.loads((HERE/'module.json').read_text(encoding='utf-8'))
solids={p:C.Solid.load(p,HERE/'_local'/(p+'.stl')) for p in manifest['parts']}
meter=C.Meter(); assert C.calibrate(meter)['pass']
rows=[]
for angle in (60,67,90,120):
    poses=C.K.transforms(angle)
    def out(pid,fixed,maximum=1.):
        return first_contact(meter,solids[pid],lambda t:translation(0,0,-t)@poses[pid],fixed,maximum,.05,refine=10)
    foot=out('cap_foot',{'panel':(solids['panel'],poses['panel'])})
    assert foot['travel'] is not None and not foot['nominalContact']
    poses['cap_foot']=translation(0,0,-foot['travel'])@poses['cap_foot']
    cap=out('servo_cap',{p:(solids[p],poses[p]) for p in ('cap_foot','panel','support')})
    assert cap['travel'] is not None and not cap['nominalContact']
    poses['servo_cap']=translation(0,0,-cap['travel'])@poses['servo_cap']
    solo=out('servo',{p:(solids[p],poses[p]) for p in ('support','servo_cap','cap_foot')})
    group=('servo','horn','input_cup','input_gear') if 'input_cup' in solids else ('servo','horn','input_gear')
    spindle=None
    if 'input_spindle' in solids:
        spindle=out('input_spindle',{p:(solids[p],poses[p]) for p in ('support','input_bridge')})
        assert spindle['travel'] is not None and not spindle['nominalContact']
        poses['input_spindle']=translation(0,0,-spindle['travel'])@poses['input_spindle']
    # Do not count meshing teeth as a hard stop; the output gear may rotate.
    fixed={p:(solids[p],poses[p]) for p in ('support','input_bridge','bearing_bridge','panel','servo_cap','cap_foot')}
    if spindle is not None: fixed['input_spindle']=(solids['input_spindle'],poses['input_spindle'])
    contacts={p:out(p,fixed) for p in group}
    free=min(r['travel'] for r in contacts.values() if r['travel'] is not None and not r['nominalContact'])
    for p in group: poses[p]=translation(0,0,-free)@poses[p]
    # The purchased horn can still move within the cup's existing .25mm fit.
    fixed_bought={p:(s,poses[p]) for p,s in solids.items() if p not in ('servo','horn','sector_gear','flag','flag_cover','hinge_pin')}
    bought_contacts={p:out(p,fixed_bought) for p in ('servo','horn')}
    bought_extra=min(r['travel'] for r in bought_contacts.values() if r['travel'] is not None and not r['nominalContact'])
    bought_total=free+bought_extra
    spline=first_contact(meter,solids['horn'],lambda t:translation(0,0,-t)@poses['horn'],
                         {'servo':(solids['servo'],poses['servo'])},.5,.025,refine=10)
    spline_volumes={str(t):meter.common(solids['horn'],translation(0,0,-t)@poses['horn'],
                                       solids['servo'],poses['servo'])[0] for t in (0.,.005,.025,.25,.5)}
    rows.append({'servo_deg':angle,'foot_out':foot,'main_cap_out_after_foot':cap,
                 'isolated_servo_without_horn_radial_support':solo,'actuator_group':contacts,
                 'spindle_out':spindle,'actuator_group_free_mm':free,'bought_group_extra':bought_contacts,
                 'bought_group_total_mm':bought_total,'purchased_spline_contact':spline,
                 'purchased_spline_shift_overlap_mm3':spline_volumes,
                 'pass':bought_total<=.5 and cap['travel']<=.5 and foot['travel']<=.5})
axial=[]
for angle in (60,67,90,120):
    poses=C.K.transforms(angle)
    probes={}
    for name,pid,sign,against in (
        ('cup_negative_support_servo','input_cup',-1,('support','servo')),
        ('cup_negative_horn','input_cup',-1,('horn',)),
        ('wheel_negative_cup','input_gear',-1,('input_cup',)),
        ('cup_positive_wheel','input_cup',1,('input_gear',)),
        ('wheel_positive_bridge','input_gear',1,('input_bridge',)),
        ('spindle_positive_support','input_spindle',1,('support',)),
        ('spindle_negative_bridge','input_spindle',-1,('input_bridge',))):
        probes[name]=first_contact(meter,solids[pid],lambda t:translation(sign*t,0,0)@poses[pid],
                                  {p:(solids[p],poses[p]) for p in against},4.,.05,refine=10)
    spline_axial={str(t):meter.common(solids['horn'],translation(t,0,0)@poses['horn'],
                                     solids['servo'],poses['servo'])[0] for t in (-.5,-.25,-.025,-.005,0.,.005,.025,.25,.5)}
    wheel_plus=probes['wheel_positive_bridge']['travel']
    poses['input_gear']=translation(wheel_plus,0,0)@poses['input_gear']
    cup_plus=first_contact(meter,solids['input_cup'],lambda t:translation(t,0,0)@poses['input_cup'],
                           {'input_gear':(solids['input_gear'],poses['input_gear'])},1.,.05,refine=10)
    poses['input_cup']=translation(cup_plus['travel'],0,0)@poses['input_cup']
    poses['input_spindle']=translation(probes['spindle_positive_support']['travel'],0,0)@poses['input_spindle']
    # The purchased spline permits axial sliding; do not count its nominal overlap.
    horn_plus=first_contact(meter,solids['horn'],lambda t:translation(t,0,0)@poses['horn'],
                            {p:(solids[p],poses[p]) for p in ('support','input_cup','input_spindle')},1.,.05,refine=10)
    poses=C.K.transforms(angle)
    cup_minus=probes['cup_negative_support_servo']['travel']
    poses['input_cup']=translation(-cup_minus,0,0)@poses['input_cup']
    wheel_minus=first_contact(meter,solids['input_gear'],lambda t:translation(-t,0,0)@poses['input_gear'],
                              {'input_cup':(solids['input_cup'],poses['input_cup'])},1.,.05,refine=10)
    cumulative={'wheel_positive':wheel_plus,'cup_positive':cup_plus['travel'],
                'horn_positive':horn_plus['travel'],'cup_negative':cup_minus,
                'wheel_negative':wheel_minus['travel']}
    axial.append({'servo_deg':angle,'contacts':probes,'spline_axial_shift_overlap_mm3':spline_axial,
                  'cumulative_mm':cumulative,'pass':all(t is not None and t<=.5 for t in cumulative.values())})
C.write_json(HERE/'_local/retention_stack.json',{'results':rows,'axial_diagnostics':axial,
                                        'pass':all(r['pass'] for r in rows+axial)})
print('RETENTION_STACK',json.dumps(rows),flush=True)
print('AXIAL_DIAGNOSTICS',json.dumps(axial),flush=True)
meter.dispose()
assert all(r['pass'] for r in rows+axial)
