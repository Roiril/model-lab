import collections
import json
from pathlib import Path
import struct
import sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
PARTS = ('box','lid','crank','link','pin','clip','speaker_clip','roof','servo_fit_test','speaker_test','roof_test_body','roof_test')
def check(path):
    data = path.read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + 50 * count
    edges = collections.Counter()
    directed = collections.Counter()
    faces = collections.Counter()
    degenerate = 0
    for i in range(count):
        xyz = struct.unpack_from('<12f', data, 84 + 50*i)[3:]
        points = [tuple(xyz[j:j+3]) for j in (0,3,6)]
        degenerate += len(set(points)) < 3
        faces[tuple(sorted(points))] += 1
        for a,b in zip(points, points[1:]+points[:1]):
            edges[tuple(sorted((a,b)))] += 1
            directed[(a,b)] += 1
    return dict(triangles=count, nonmanifold_edges=sum(n!=2 for n in edges.values()),
                winding_mismatches=sum(directed[(b,a)]!=n for (a,b),n in directed.items()),
                duplicate_faces=sum(n-1 for n in faces.values() if n>1), degenerate_faces=degenerate)
BUILD = ROOT/'models/mystery-box-sg92r-c2/build'
def fixture(name, faces):
    data = bytearray(b'topology calibration'.ljust(80, b'\0'))
    data.extend(struct.pack('<I', len(faces)))
    for face in faces:
        data.extend(struct.pack('<12fH', 0,0,0, *[c for vertex in face for c in vertex], 0))
    path = BUILD/f'cal_topology_{name}.stl'
    path.write_bytes(data)
    return check(path)
a,b,c,d = (0,0,0),(1,0,0),(0,1,0),(0,0,1)
tetrahedron = [(a,c,b),(a,b,d),(a,d,c),(b,c,d)]
calibration = dict(closed=fixture('closed',tetrahedron), open=fixture('open',tetrahedron[:-1]))
calibration['ok'] = calibration['closed']['nonmanifold_edges']==0 and calibration['open']['nonmanifold_edges']==3
assert calibration['ok'], calibration
report = {p:check(ROOT/f'exports/mystery-box-sg92r-c2-{p}.stl') for p in PARTS}
assert all(not any(v[k] for k in ('nonmanifold_edges','winding_mismatches','duplicate_faces','degenerate_faces')) for v in report.values()), report
out = BUILD/'stl_topology.json'
out.write_text(json.dumps(dict(calibration=calibration, parts=report), indent=1), encoding='utf-8', newline='\n')
print(json.dumps(dict(calibration=calibration, parts=report)))
