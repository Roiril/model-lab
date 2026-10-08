import bpy,pathlib,json,math,sys,numpy as np,hashlib
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));import params as p
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_B3.blend'));D=json.loads((R/'assembly_manifest.json').read_text());rho=float(json.loads((R/'filament_pla_flat.json').read_text())['filament_density'][0]) if (R/'filament_pla_flat.json').exists() else 1.26;moving=[]
for item in D['parts']:
    if item['group']!='lid':continue
    o=bpy.data.objects[item['name']];o.data.calc_loop_triangles();a=np.array([[tuple(o.matrix_world@o.data.vertices[i].co*1000) for i in t.vertices] for t in o.data.loop_triangles]);vol=np.einsum('ij,ij->i',a[:,0],np.cross(a[:,1],a[:,2]))/6;center=((a.sum(axis=1)/4)*vol[:,None]).sum(axis=0)/vol.sum();mass=abs(vol.sum())/1000*rho
    moving.append(dict(name=o.name,solid_volume_mm3=float(abs(vol.sum())),solid_mass_g=float(mass),centroid_mm=center.tolist()))
O=np.array(D['O']);H=np.array(D['H']);uv=np.array(D['rocker_local_mm']);r=D['crank_r_mm'];L=D['link_length_mm'];angles=[];ratios=[];mins=[180,180];gravity=[];last=None
for i in range(651):
    phi=math.radians(i/10);M=np.array([[math.cos(phi),-math.sin(phi)],[math.sin(phi),math.cos(phi)]]);B=H+M@uv;dd=B-O;d=np.linalg.norm(dd);theta=math.atan2(dd[1],dd[0])-math.acos((d*d+r*r-L*L)/(2*d*r));A=O+r*np.array([math.cos(theta),math.sin(theta)]);link=B-A;av=A-O;bv=B-H
    cross=lambda u,v:u[0]*v[1]-u[1]*v[0]
    ratio=abs(cross(bv,link)/cross(av,link));ratios.append(ratio)
    for j,v in enumerate([av,bv]):mins[j]=min(mins[j],math.degrees(math.acos(min(1,abs(np.dot(v,link)/(np.linalg.norm(v)*L))))))
    assert last is None or theta>last;last=theta
    torque=0
    for item in moving:
        com=H+M@(np.array(item['centroid_mm'][1:])-H);torque+=item['solid_mass_g']/1000*9.80665*(com[0]-H[0])/1000
    gravity.append(abs(torque)/ratio)
    if i in [0,650]:angles.append(math.degrees(theta))
mass=sum(x['solid_mass_g'] for x in moving);bound=mass/1000*9.80665*.049/min(ratios)
report=dict(physical_tested=False,geometry_sha256=hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),lid_angle_step_deg=.1,servo_range_deg=angles,servo_stroke_deg=angles[1]-angles[0],monotonic=True,min_distance_from_toggle_deg=mins,theta_speed_over_lid_speed=[min(ratios),max(ratios)],assumed_density_g_cm3=rho,moving_solid_mass_g=mass,moving_parts=moving,max_ideal_servo_gravity_torque_Nm=max(gravity),conservative_gravity_bound_Nm=bound,conservative_gravity_bound_kgf_cm=bound/.0980665,notes=['Uniform solid mass calculation; actual sparse-infill mass distribution differs','Friction, backlash, startup acceleration, wiring drag, support residue and servo capability are not tested','Servo still supplies gravity torque while open; losing power may close the lid'])
(R/'mechanics_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('MECHANICS',mass,'g solid moving mass; conservative gravity bound',bound/.0980665,'kgf cm',flush=True)
