"""Assumed linear 2D beam-frame calculations, in mm / N / MPa.

The actual shape is not a prismatic beam. This calculation compares the design
using conservative sampled sections. It is not an FEA or a tested load rating
of the printed three-dimensional solid.
"""
from __future__ import annotations

import math
import numpy as np


def bezier(points, amount):
    p = np.asarray(points, dtype=float) * 1000
    return ((1-amount)**3*p[0] + 3*(1-amount)**2*amount*p[1]
            + 3*(1-amount)*amount**2*p[2] + amount**3*p[3])


def bezier_tangent(points, amount):
    p = np.asarray(points, dtype=float) * 1000
    value = (3*(1-amount)**2*(p[1]-p[0]) + 6*(1-amount)*amount*(p[2]-p[1])
             + 3*amount**2*(p[3]-p[2]))
    return value / np.linalg.norm(value)


def element_matrix(a, b, area, inertia, modulus=1000):
    delta = np.asarray(b)-a
    length = float(np.linalg.norm(delta))
    c, s = delta / length
    axial = modulus*area/length
    bending = modulus*inertia/length**3
    local = np.array([
        [axial,0,0,-axial,0,0],
        [0,12*bending,6*length*bending,0,-12*bending,6*length*bending],
        [0,6*length*bending,4*length**2*bending,0,-6*length*bending,2*length**2*bending],
        [-axial,0,0,axial,0,0],
        [0,-12*bending,-6*length*bending,0,12*bending,-6*length*bending],
        [0,6*length*bending,2*length**2*bending,0,-6*length*bending,4*length**2*bending],
    ])
    rotation = np.zeros((6,6))
    block = np.array([[c,s,0],[-s,c,0],[0,0,1]])
    rotation[:3,:3] = rotation[3:,3:] = block
    return rotation.T @ local @ rotation, local, rotation


def solve_frame(nodes, elements, fixed, loads):
    stiffness = np.zeros((3*len(nodes),3*len(nodes)))
    cached = []
    for a,b,area,inertia,radius,label in elements:
        global_k, local_k, rotation = element_matrix(nodes[a],nodes[b],area,inertia)
        ids = np.array([3*a,3*a+1,3*a+2,3*b,3*b+1,3*b+2])
        stiffness[np.ix_(ids,ids)] += global_k
        cached.append((ids,local_k,rotation,area,inertia,radius,label))
    force = np.zeros(3*len(nodes))
    for node,fy,fz in loads:
        force[3*node] += fy
        force[3*node+1] += fz
    free = np.setdiff1d(np.arange(len(force)),fixed)
    displacement = np.zeros(len(force))
    displacement[free] = np.linalg.solve(stiffness[np.ix_(free,free)],force[free])
    stresses = {}
    for ids,local_k,rotation,area,inertia,radius,label in cached:
        internal = local_k @ rotation @ displacement[ids]
        stress = max(abs(internal[0]),abs(internal[3]))/area
        stress += max(abs(internal[2]),abs(internal[5]))*radius/inertia
        stresses[label] = max(stresses.get(label,0),float(stress))
    return displacement.reshape(-1,3), stresses


def calibrate_frame():
    # A known cantilever checks sign, units, stiffness and moment recovery.
    width, height, length, force = 20, 10, 100, 10
    inertia = width*height**3/12
    displacement, stress = solve_frame([(0,0),(length,0)],
        [(0,1,width*height,inertia,height/2,'beam')],[0,1,2],[(1,0,-force)])
    expected = force*length**3/(3*1000*inertia)
    expected_stress = force*length*(height/2)/inertia
    assert abs(displacement[1,1]+expected) < 1e-9
    assert abs(stress['beam']-expected_stress) < 1e-9
    assert np.allclose(displacement[0],0)
    return {'known_cantilever_deflection_mm':expected,
            'known_cantilever_stress_mpa':expected_stress,'passed':True}


def sculpture_frame(params):
    nodes, elements = [], []
    index = {}
    def node(point):
        key = tuple(round(float(v),6) for v in point)
        if key not in index:
            index[key] = len(nodes)
            nodes.append(key)
        return index[key]
    def segment(a,b,area,inertia,radius,label):
        elements.append((node(a),node(b),area,inertia,radius,label))
    top_z = params.BODY_HEIGHT*1000-params.TOP_BEAM*500
    base_z = params.BOTTOM_BEAM*500
    curve_top_ys = [points[0][0]*1000
                    for points in (params.S_CURVE_POINTS, params.REAR_CURVE_POINTS)]
    top_ys = sorted(set([0,16,122.5,184,229,params.FRAME_DEPTH*1000,
                         *curve_top_ys]))
    base_ys = sorted(set([0,20.5,24,122.5,224,224.5,245]))
    width = params.FRAME_WIDTH*1000
    height = params.TOP_BEAM*1000
    for a,b in zip(top_ys,top_ys[1:]):
        segment((a,top_z),(b,top_z),width*height,width*height**3/12,height/2,'upper_beam')
    width, height = 80, params.BOTTOM_BEAM*1000
    for a,b in zip(base_ys,base_ys[1:]):
        segment((a,base_z),(b,base_z),width*height,width*height**3/12,height/2,'lower_beam')
    for points,rx,rz,label in [
        (params.S_CURVE_POINTS,params.S_X_RADIUS,params.S_SIDE_RADIUS,'s_curve'),
        (params.REAR_CURVE_POINTS,params.REAR_X_RADIUS,params.REAR_SIDE_RADIUS,'rear_curve'),
    ]:
        # Allow 0.8 mm per radius for fusion and surface smoothing. Geometry
        # checks independently sample whether these assumed cores are solid.
        rx,rz = rx*1000-.8,rz*1000-.8
        area, inertia = math.pi*rx*rz,math.pi*rx*rz**3/4
        curve = [bezier(points,t) for t in np.linspace(0,1,25)]
        segment((curve[0][0],top_z),curve[0],area,inertia,rz,label)
        for a,b in zip(curve,curve[1:]):
            segment(a,b,area,inertia,rz,label)
        segment(curve[-1],(curve[-1][0],base_z),area,inertia,rz,label)
    fixed = [3*node((20.5,base_z)),3*node((20.5,base_z))+1,
             3*node((224.5,base_z))+1]
    cases = []
    for name,force in [('4kg_split_over_two_supports',4*9.80665/2),
                       ('4kg_on_one_support',4*9.80665),
                       ('4kg_on_one_support_plus_20n',4*9.80665+20)]:
        for y in (16,122.5,229):
            displacement, stresses = solve_frame(nodes,elements,fixed,[(node((y,top_z)),0,-force)])
            top_ids = [node((position,top_z)) for position in top_ys]
            cases.append({'case':name,'load_y_mm':y,'load_n':force,
                          'maximum_top_vertical_deflection_mm':float(np.abs(displacement[top_ids,1]).max()),
                          'maximum_section_stress_mpa':max(stresses.values()),
                          'section_stresses_mpa':stresses})
    return {'calibration':calibrate_frame(),'nodes':len(nodes),'elements':len(elements),
            'assumed_modulus_mpa':1000,'assumed_radius_allowance_mm':.8,
            'assumed_stress_threshold_mpa':5.0,
            'cases':cases,'maximum_section_stress_mpa':max(c['maximum_section_stress_mpa'] for c in cases),
            'maximum_top_vertical_deflection_mm':max(c['maximum_top_vertical_deflection_mm'] for c in cases),
            'note':'Assumed linear two-dimensional beam frame. Elliptical struts and rigid connections approximate the actual solid. This is not solid FEA and does not establish printed strength, out-of-plane behaviour, creep or friction.'}
