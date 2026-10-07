"""Simple conditional hand-load screening, not material/servo validation."""
import pathlib,json,math,hashlib
R=pathlib.Path(__file__).resolve().parent
F=25.;allow=5.;rows=[]
def beam(n,M,b,h,axial=0):
 z=b*h*h/6;stress=M/z+axial/(b*h);rows.append({'part':n,'moment_Nmm':M,'section_mm':[b,h],'calculated_nominal_stress_MPa':stress,'assumed_screening_allowable_MPa':allow,'ratio':allow/stress,'passes_assumed_screen':stress<=allow})
beam('09 curved link, in-plane bending',F*4.4,3.,8.,F)
beam('07/08 rocker, all assumed 0.10Nm on one leg',100.,4.,6.4)
span=38.;a=23.6;reaction_left=F*(span-a)/span;reaction_right=F*a/span
beam('17 deep web between two seated tongues',F*a*(span-a)/span,3.,10.5)
beam('17 front step next to seated tongue',reaction_left*4.0,3.,4.4)
beam('17 axial cup pull, 1N with both tongues seated',1.*a*(span-a)/span,10.5,3.)
beam('04 front loose bench rail, stipulated1N before body seating',43.8,6.8,6.1)
beam('04 rear loose bench rail, stipulated1N before body seating',43.8,6.8,4.)
beam('13 bottom bar at stiffening hub, stipulated12.5N per foot',12.5*(18.75-6.5),10.4,4.5)
beam('04 rear foot cantilever, stipulated12.5N',12.5*9.05,6.,6.)
beam('05 front foot cantilever, stipulated12.5N',12.5*3.25,6.,6.)
report={'physical_tested':False,'revision':3,'method':'Elementary nominal beam/axial stress using rectangular solid sections. No FEM, anisotropic PLA data, notch factors, bearing concentration, fatigue or tested safety factor. 5MPa allowable is a stipulated screening assumption only.','stipulated_cases':{'joint_force_N':25,'servo_like_joint_moment_Nm':.10,'cup_axial_pull_N':1.,'bottom_key_total_upward_pull_N':25.,'free_lid_edge_hand_load_N':1.},'joint_pin_double_shear_nominal_MPa':F/(2*math.pi*5**2/4),'local_web_support_reactions_N':[reaction_left,reaction_right],'sections':rows,'all_pass_stipulated_nominal_screen':all(r['passes_assumed_screen'] for r in rows),'limits':['Real servo stall torque/force may exceed the assumed cases. Slow pulses do not limit stall torque. This is not a servo rating or an allowable user-force claim.','Both local-capture tongues must be seated and plates/bottom key installed. Support loose bench parts during assembly, avoid sideways bending.','Material, layer adhesion, scars, creep, corner stresses and contacts are untested. Fit by gentle hand before power.','Do not push a powered lid. Calibrate pulse endpoints before hard contact and cut power immediately if humming or stuck.']}
(R/'load_screen_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('Conditional stress screen',report['all_pass_stipulated_nominal_screen'],[(r['part'],round(r['calculated_nominal_stress_MPa'],2)) for r in rows])
report['input_blend_sha256']=hashlib.sha256((R/'editable_cube_v6.blend').read_bytes()).hexdigest()
report['limits'].append('Radial bearing loads require both broad body-floor pads to seat under04 rails. The local lip is not a free-standing radial bearing. No vibration survival or automatic angular lock guarantee is made.')
(R/'load_screen_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
