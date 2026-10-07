"""Measured CAD planes plus explicit, unvalidated tolerance budgets."""
import bpy,sys,json,pathlib,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));import params as p
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
def mesh(name):
 o=bpy.data.objects[name];o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
T={n:mesh(n) for n in ['04_main_cassette','05_front_closure','06_horn_cup_journal','14_servo_top_keeper','17_local_cup_capture','18_local_capture_stop','19_local_capture_stop','REFERENCE SG92R body','REFERENCE SG92R horn']}
def hit(n,origin,direction,expected):
 h=T[n].ray_cast(Vector(origin)*.001,Vector(direction))[0];assert h is not None,(n,origin)
 x=h.x*1000;assert abs(x-expected)<.003,(n,x,expected);return float(x)
planes={
 'case_back':hit('REFERENCE SG92R body',(0,30,42),(1,0,0),9.),
 'same_cassette_case_stop':hit('04_main_cassette',(20,30,42),(-1,0,0),8.8),
 'horn_front':hit('REFERENCE SG92R horn',(70,42,37),(-1,0,0),41.),
 'cup_roof':hit('06_horn_cup_journal',(30,42,37),(1,0,0),41.2),
 'cup_functional_front':hit('06_horn_cup_journal',(70,40,30),(-1,0,0),46.1),
 'local_lip_stop_face':hit('17_local_cup_capture',(40,40,30),(1,0,0),46.2),
 'local_lip_forward_tongue':hit('17_local_cup_capture',(70,16,21),(-1,0,0),49.7),
 'front_positive_stop_rear':hit('18_local_capture_stop',(49,16,21),(1,0,0),49.8),
 'front_positive_stop_forward':hit('18_local_capture_stop',(70,16,21),(-1,0,0),53.0),
 'same_cassette_mortise_forward_stop':hit('04_main_cassette',(53.02,13.8,21),(1,0,0),53.10),
}
terms={'case_rear_gap':planes['case_back']-planes['same_cassette_case_stop'],'horn_roof_gap':planes['cup_roof']-planes['horn_front'],'cup_to_local_lip':planes['local_lip_stop_face']-planes['cup_functional_front'],'lip_to_positive_stop':planes['front_positive_stop_rear']-planes['local_lip_forward_tongue'],'positive_stop_in_cassette':planes['same_cassette_mortise_forward_stop']-planes['front_positive_stop_forward']}
nom=sum(terms.values());assert abs(nom-.7)<.005
# Each of ten stop planes may err by +/-0.10mm. This is a stipulated
# measurement acceptance, not claimed printer precision or a PLA property.
budget={'ten_stop_plane_errors_0p10_each':1.0,'servo_internal_endplay_acceptance':.1,'capture_loop_relative_flex_acceptance':.1,'effective_axial_tilt_acceptance':.1}
worst=nom+sum(budget.values());ref=3.
axes=[]
for name,eng,play,details in [
 ('10_hinge_axle',[3.60,3.20],.55,'0.15 blind-end clearance + 2x0.20 receiver separation'),
 ('11_drive_axle',[3.25,2.95],.75,'0.15 blind-end clearance + 2x0.20 receiver separation +0.20 cup rear saddle clearance'),
 ('12_link_axle',[2.85,2.85],.85,'0.15 blind-end clearance + 2x0.15 rocker/H-shoulder gap + 2x0.20 receiver separation')]:
  axes.append({'name':name,'nominal_end_engagement_mm':eng,'nominal_worst_engagement_loss_mm':play,'nominal_loss_basis':details,'manufacture_budget_mm':.5,'tilt_budget_mm':.2,'remaining_with_assumed_budgets_mm':[round(e-play-.5-.2,3) for e in eng],'limits':'Conditional measurement acceptance: fully assembled support-face spread, including all receiver/shoulder dimensional errors, is no more than0.2mm above nominal. Additional bore-mouth, bore-floor and shaft-length errors each <=0.1mm. Tilt loss <=0.2mm. This is a stipulated aggregate measured bound, not an assertion about individual printer accuracy. Front roof fork is open axially; H shoulders, not that open slot, bound the rocker spread.'})
report={'revision':2,'physical_tested':False,'geometry_sha256':hashlib.sha256((R/'editable_cube_v6.blend').read_bytes()).hexdigest(),'actual_cad_x_planes_mm':planes,'nominal_withdrawal_terms_mm':terms,'nominal_relative_withdrawal_mm':nom,'reference_smooth_overlap_mm':ref,'unvalidated_acceptance_budget_mm':budget,'assumed_budget_total_withdrawal_mm':worst,'remaining_if_reference_and_all_budgets_hold_mm':ref-worst,'axis_engagement_screen':axes,'capture_condition':'17 seated in the blind mortise of04,05 prevents journal/17 lifting, body receivers and spring-seated bayonet retain plates. Common body/main-plate translation cancels from axial case-to-local-lip loop. The lip must not lift out. Real spline teeth are absent from CAD.','physical_measurements_required':['actual effective tooth engagement E','total relative horn/case withdrawal including internal servo endplay, after full assembly','axis ends/receiver/fork play under gentle hand displacement','spring OD/ID/free/solid height and force at 5.4/3.9mm heights','D3 cable and8x5x15 connector including required bend radius'],'trial_acceptance':'Effective tooth engagement minus measured total withdrawal >=1.0mm; every measured axle end insertion >=1.0mm. These are prototype trial targets, not manufacturer strength specifications. Dimensional errors must meet stipulated budgets; if any unknown, do not power.'}
report['capture_condition']='17 seated in two axially open mortises of04;18/19 stop outward motion and05 shelf prevents their vertical release. Body receivers and spring-seated bayonet retain both plates. Common body/main-plate translation cancels from the axial case-to-local-lip loop. The lip/stops must not lift out. Real spline teeth are absent from CAD.'
(R/'horn_capture_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('Local capture nominal / assumed worst / provisional remaining',nom,worst,ref-worst);print('Axle screening',[(x['name'],x['remaining_with_assumed_budgets_mm']) for x in axes])
