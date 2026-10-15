"""Actual production solids, never an easier substitute for a difficult joint."""
from printmech import geometry as G
from .geometry import clone


def build(parts, interface, common_params):
    result={}
    for name,pid in (('horn_fit','input_gear'),('servo_fit','support'),
                     ('shield_section','flag'),('gear_mesh','sector_gear'),('pin_fit','hinge_pin')):
        result[name]=clone(parts[pid]['object'],name)
    G.intersect(result['servo_fit'],G.box(-28,1,-17,20,3.25,24))
    # The cut crosses the mounting snap. Remove that unrelated detached tongue.
    G.cut(result['servo_fit'],G.box(-27,-25,-18,-6.5,3,5.1))
    # Cut the production bay itself, keeping its cable-entry notch.
    result['connector_nest']=clone(parts['support']['object'],'connector_nest')
    G.intersect(result['connector_nest'],G.box(-24.5,-7.5,13.5,24.5,3.25,22.75))
    return result
