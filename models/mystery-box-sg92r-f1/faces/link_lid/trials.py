"""Fit samples are cut from the same production objects, never simplified substitutes."""
from printmech import geometry as G
from .geometry import clone


def build(parts, interface, common_params):
    out={}
    for name,pid in (('horn_fit','crank'),('servo_fit','support'),('shield_section','servo_cap')):
        out[name]=clone(parts[pid]['object'],name)
    # Actual cradle region. Leave the ear channels and their adjacent case stops.
    G.intersect(out['servo_fit'],G.box(-25,1,-25,10,8,28))
    G.intersect(out['shield_section'],G.box(-20,7,-19,19,0,12))
    # Open connector nest is dimensioned as a provisional physical trial, not a plug hole.
    out['connector_nest']=G.cut(G.box(-9,9,-6,6,0,16),G.box(-7,7,-4,4,2,17))
    return out
