"""Classify previously computed intersection results, without altering geometry."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;P=R/'motion_audit.json';d=json.loads(P.read_text())
remaining=[];flat=d.get('flat_contact_intersections',[])
for row in d['invalid_intersection_volumes']:
    b=row['bounds_mm']
    if row['nonmanifold_edges']==0 and b and min(b[1][k]-b[0][k] for k in range(3))<.00005:flat.append(row)
    else:remaining.append(row)
d['flat_contact_intersections']=flat;d['invalid_intersection_volumes']=remaining
d['flat_contact_tolerance_mm']=.00005
P.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print('Flat contacts',len(flat),'unresolved intersections',len(remaining))
assert not remaining
