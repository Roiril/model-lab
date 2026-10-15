"""Exercise nested receiver operations through all five independent readers."""
import importlib.util
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'lib'))
sys.path.insert(0, str(ROOT))
from printmech import geometry as G
from tools.mechgate_lib import meshcheck
spec = importlib.util.spec_from_file_location('v2_reader_compose', HERE / 'compose.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
receivers = C.read(HERE / 'build/v2-frame-interface.json')['mount_geometry']['frame_receivers']
for face in ('blank', 'template', 'link_lid', 'three_pixels', 'sector_flag'):
    modules = C.face_package(face, 'v2_reader_' + face, with_geometry=True)
    module = modules['geometry'] if face in ('blank', 'template') else __import__('importlib').import_module(modules['geometry'].__package__ + '.recipe')
    reader = getattr(module, '_primitive', None) or module.primitive
    for shape in receivers:
        if not shape.get('operations'):
            continue
        obj = reader(shape) if face == 'link_lid' else reader(shape, shape['id'])
        C.clean_object(obj)
        obj.data.calc_loop_triangles()
        tris = np.array([[list(obj.data.vertices[i].co) for i in t.vertices] for t in obj.data.loop_triangles], dtype=np.float32).astype(float)
        topology = meshcheck.topology(tris)
        volume = G.volume(obj)
        assert topology['pass'] and len(meshcheck.components(tris)) == 1
        assert abs(volume - 164.70625) < .001, (face, shape['id'], volume)
        print(json.dumps({'face': face, 'receiver': shape['id'], 'volume_mm3': volume, 'topology_pass': topology['pass']}), flush=True)
print('V2_NESTED_RECEIVER_READERS_PASS')
