"""Axial hard-stop calculation from existing CAD. No spline teeth are printed."""
import bpy,pathlib,json,math,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));import params as p
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
D=json.loads((R/'reference/dimensions.json').read_text());O=(p.SERVO_Y*1000,p.SERVO_Z*1000)
def tree(name):
    o=bpy.data.objects[name];o.data.calc_loop_triangles()
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True,epsilon=1e-10)
T={n:tree(n) for n in ['01_body','04_main_cassette','05_front_closure','06_horn_cup_journal','REFERENCE SG92R body','REFERENCE SG92R horn']}
def hit(name,start,direction,expected):
    v=T[name].ray_cast(Vector(start)*.001,Vector(direction),.100)[0]
    assert v is not None,(name,start)
    mm=v.x*1000;assert abs(mm-expected)<.002,(name,mm,expected)
    return float(mm)
# Probe the actual mesh surfaces, including receivers; no friction in the bound.
planes={
 'main_receiver_rear_wall':hit('01_body',(5.4,6.0,35.0),(-1,0,0),3.7),
 'closure_receiver_front_wall':hit('01_body',(58.0,6.0,35.0),(1,0,0),60.4),
 'servo_rear_case':hit('REFERENCE SG92R body',(0,30,42),(1,0,0),9.0),
 'servo_rear_stop':hit('04_main_cassette',(20,30,42),(-1,0,0),8.7),
 'servo_front_case':hit('REFERENCE SG92R body',(70,24.5,42.8),(-1,0,0),31.0),
 'servo_front_stop':hit('05_front_closure',(31,24.5,42.8),(1,0,0),31.3),
 'horn_front_face':hit('REFERENCE SG92R horn',(70,O[0]+2,O[1]),(-1,0,0),41.0),
 'cup_captive_roof':hit('06_horn_cup_journal',(30,O[0]+2,O[1]),(1,0,0),41.3),
 'journal_tip':hit('06_horn_cup_journal',(70,O[0]+3,O[1]+1.3),(-1,0,0),58.0),
 'journal_blind_end':hit('05_front_closure',(50,O[0]+3,O[1]+1.3),(1,0,0),58.3),
}
main_receiver_play=p.REAR_PLATE_X*1000-planes['main_receiver_rear_wall']
closure_receiver_play=planes['closure_receiver_front_wall']-(p.FRONT_PLATE_X+p.FRONT_PLATE_T)*1000
servo_case_back_play=planes['servo_rear_case']-planes['servo_rear_stop']
journal_forward_play=planes['journal_blind_end']-planes['journal_tip']
horn_to_roof_play=planes['cup_captive_roof']-planes['horn_front_face']
terms={'main_cassette_rearward_in_body_receiver':main_receiver_play,'servo_rearward_in_cassette':servo_case_back_play,'front_closure_forward_in_body_receiver':closure_receiver_play,'journal_forward_in_blind_bore':journal_forward_play,'horn_forward_to_cup_roof':horn_to_roof_play}
max_withdrawal=sum(terms.values())
nominal_engagement=(min(D['SHAFT_BOTTOM_Z']+D['SHAFT_H'],D['HORN_SOCKET_TOP_Z'])-max(D['SHAFT_BOTTOM_Z'],D['HORN_HUB_BOTTOM_Z']))*1000
remaining=nominal_engagement-max_withdrawal
assert remaining>1.0,(nominal_engagement,max_withdrawal)
report={'physical_tested':False,'geometry_changed':False,'input_blend_sha256':hashlib.sha256((R/'editable_cube_v6.blend').read_bytes()).hexdigest(),'center_screw_required':False,'printed_spline':False,'additional_print_parts':0,'capture_condition':'Body receivers and cross key 13 fully assembled; cassette alone is not axially secured. Hard stops, not friction, bound withdrawal.','actual_mesh_stop_planes_world_x_mm':planes,'worst_nominal_withdrawal_terms_mm':terms,'worst_nominal_relative_withdrawal_mm':max_withdrawal,'reference_smooth_socket_overlap_mm':nominal_engagement,'reference_remaining_overlap_mm':remaining,'cup_roof_thickness_mm':(p.CUP_FRONT_X-p.CUP_POCKET_END_X)*1000,'closure_blind_wall_thickness_mm':(p.FRONT_PLATE_X+p.FRONT_PLATE_T)*1000-planes['journal_blind_end'],'limits':['Shaft height 3.5 mm and socket internal positions are provisional reference values, not measurements of the actual tooth engagement.','Bound covers nominal axial translations, not print dimensional error, flex, tilt, servo internal endplay, tooth stripping or retention force.','Spline is the original horn/servo interface. Tooth geometry is absent from reference CAD and never printed.','Do not power the cassette alone. The body receivers and cross key retain the two closure planes.','Prototype acceptance target: measured effective seated tooth engagement minus measured total withdrawal must leave at least 1.0 mm; this is a trial criterion, not a validated strength specification. If unsuitable, do not energize and revise the capture geometry.']}
(R/'horn_capture_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('SCREWLESS CAPTURE: nominal withdrawal',max_withdrawal,'reference overlap',nominal_engagement,'remaining',remaining,flush=True)
