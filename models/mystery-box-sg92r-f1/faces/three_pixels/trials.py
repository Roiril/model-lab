"""Real production geometry for fit and friction trials; no exports."""
from printmech import geometry as G
from .geometry import clone, O


def build(parts, interface, common_params):
    out={}
    for name,pid in (('horn_fit','cam_upper'),('servo_fit','support'),
                     ('servo_cap_fit','servo_cap'),('pixel_fit','pixel_1'),
                     ('guide_fit','guide'),('lower_cam_fit','cam_lower'),
                     ('upper_cam_fit','cam_upper'),('key_fit','cam_key_1')):
        out[name]=clone(parts[pid]['object'],name)
    G.intersect(out['horn_fit'],G.prism(G.circle((-5,0),18.5,144),'z',2,7.5))
    G.intersect(out['servo_fit'],G.box(-20,21,-15,15,20.5,24))
    # Follower 1 sweeps -29..31 degrees in cam coordinates over servo 60..120.
    # This rectangular crop retains that entire arc, with end margins, while
    # removing the hub and the other two tracks. The working surfaces are exact
    # production mesh intersections, not a simplified replacement cam profile.
    for name in ('lower_cam_fit', 'upper_cam_fit'):
        G.intersect(out[name], G.box(O+18.7,O+33,-17.5,17.5,0,20))
    # Keep only follower 1's U guide; the complete three-pixel guide is a product part.
    G.intersect(out['guide_fit'],G.box(6,22,6.25,16,16.5,20))
    # Connector body is provisional; the nest remains open on its top.
    out['connector_nest']=G.cut(G.box(-9,9,-6,6,0,20),G.box(-7,7,-4,4,2,21))
    return out
