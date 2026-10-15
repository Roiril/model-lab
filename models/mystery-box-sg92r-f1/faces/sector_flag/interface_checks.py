"""Probe the declared drive / retention contacts using the unchanged shared meter."""
import numpy as np
from . import kinematics as K
from printmech.solid_meter import first_contact,translation


def check(meter,solids,manifest):
    drives=[]
    retention=[]
    for angle in (60.,90.,120.):
        poses=K.transforms(angle)
        for spec in manifest['interfaces']:
            if spec['type']=='drive':
                a,b=spec['driver'],spec['driven']
                pivot=K.O if b in ('input_cup','input_gear') else K.H
                for sign in (-1,1):
                    limit=float(spec['max_play_deg'])
                    result=first_contact(meter,solids[b],lambda t:K.rot_x(sign*t,pivot)@poses[b],
                                         {a:(solids[a],poses[a])},limit,.1,refine=10)
                    drives.append({'id':spec['id'],'servo_deg':angle,'sign':sign,**result,
                                   'pass':result['travel'] is not None and not result['nominalContact']})
            elif spec['type']=='retention':
                moving=spec['parts']
                fixed={p:(solids[p],poses[p]) for p in spec.get('against',solids) if p not in moving}
                direction=np.array(spec['direction'])
                contacts=[]
                for p in moving:
                    limit=float(spec['max_free_mm'])
                    result=first_contact(meter,solids[p],lambda t:translation(*(direction*t))@poses[p],fixed,
                                         limit+.05,.05,refine=10)
                    contacts.append({'part':p,**result})
                hit=[c['travel'] for c in contacts if c['travel'] is not None and not c['nominalContact']]
                retention.append({'id':spec['id'],'servo_deg':angle,'contacts':contacts,
                                  'first_mm':min(hit) if hit else None,'pass':bool(hit) and min(hit)<=limit+.002})
    return {'drive':drives,'retention':retention,'pass':all(r['pass'] for r in drives+retention)}
