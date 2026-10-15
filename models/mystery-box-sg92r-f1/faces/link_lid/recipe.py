"""Numerical mounting recipe reader, private to this cassette; no frame imports."""
from printmech import geometry as G


def loft_box(shape, name="mount_loft"):
    sections = shape["sections"]
    if len(sections) < 2:
        raise ValueError("loft_box requires at least two sections")
    rings = []
    for section in sections:
        d = section["d_mm"]
        u, v = section["center_uv_mm"]
        width, height = section["size_uv_mm"]
        if width <= 0 or height <= 0 or (rings and d <= rings[-1][0]):
            raise ValueError("loft_box sections need positive sizes and increasing d")
        rings.append((d, [(u-width/2, v-height/2), (u+width/2, v-height/2),
                          (u+width/2, v+height/2), (u-width/2, v+height/2)]))
    obj = G.loft_rings(rings, name)
    G.clean(obj, dist=0.00001)
    return obj


def primitive(s):
    obj = primitive_solid(s)
    for row in s.get('operations', []):
        operation = {'union':'UNION','difference':'DIFFERENCE'}.get(row['op'])
        if operation is None:
            raise ValueError(f"unsupported CSG operation: {row['op']}")
        G.boolean(obj, primitive(row['shape']), operation)
        if not obj.data.polygons:
            raise ValueError('Empty nested CSG result')
    return obj


def primitive_solid(s):
    kind = s.get('type', s.get('kind'))
    if kind == 'loft_box':
        return loft_box(s)
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
    if interface['mount_geometry']['schema'] != 'csg-mm-v2':
        raise ValueError('Unsupported mount geometry schema')
    result = {}
    for pid, recipe in interface['mount_geometry']['parts'].items():
        obj = primitive(recipe['base'])
        for operation in recipe.get('operations', []):
            G.boolean(obj, primitive(operation['shape']), {'union':'UNION','difference':'DIFFERENCE'}[operation['op']])
        obj.name = pid
        result[pid] = obj
    return result
