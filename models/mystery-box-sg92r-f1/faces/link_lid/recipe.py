"""Numerical mounting recipe reader, private to this cassette; no frame imports."""
from printmech import geometry as G


def primitive(s):
    kind = s.get('type', s.get('kind'))
    if kind == 'box':
        c, d = s['center_mm'], s['size_mm']
        return G.box(c[0]-d[0]/2,c[0]+d[0]/2,c[1]-d[1]/2,c[1]+d[1]/2,c[2]-d[2]/2,c[2]+d[2]/2)
    if kind == 'cylinder':
        c, h, r = s['center_mm'], s['depth_mm']/2, s['radius_mm']
        axis = {'u':'x','v':'y','d':'z'}[s['axis']]
        idx = {'x':0,'y':1,'z':2}[axis]
        p = [c[i] for i in range(3) if i != idx]
        return G.prism(G.circle(p,r),axis,c[idx]-h,c[idx]+h)
    raise ValueError(f'unsupported mount primitive: {kind}')


def build_mount(interface):
    result = {}
    for pid, recipe in interface['mount_geometry']['parts'].items():
        obj = primitive(recipe['base'])
        for operation in recipe.get('operations', []):
            G.boolean(obj, primitive(operation['shape']), {'union':'UNION','difference':'DIFFERENCE'}[operation['op']])
        obj.name = pid
        result[pid] = obj
    return result
