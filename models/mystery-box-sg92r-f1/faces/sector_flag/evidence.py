"""Freshness checks for the isolated local artifacts."""
import hashlib
import json
from pathlib import Path

GEOMETRY_INPUTS=('geometry.py','deep_geometry.py','params.py','kinematics.py','gears.py','recipe.py','module.json')

def require_meshes(here):
    report=json.loads((here/'_local/report.json').read_text(encoding='utf-8'))
    if report.get('status')=='running':
        raise RuntimeError('check_local did not finish; existing STLs are stale')
    for name in GEOMETRY_INPUTS:
        actual=hashlib.sha256((here/name).read_bytes()).hexdigest()
        if report['source_sha256'].get(name)!=actual:
            raise RuntimeError('Rebuild local meshes after changing '+name)
    actual=hashlib.sha256((here.parents[1]/'interface.json').read_bytes()).hexdigest()
    if actual!=report['interface_sha256']:
        raise RuntimeError('Interface changed; rebuild local meshes')
    for name,expected in report['reference_sha256'].items():
        actual=hashlib.sha256((here.parents[3]/'models/sg92r-photo'/name).read_bytes()).hexdigest()
        if actual!=expected:raise RuntimeError('SG92R reference changed; rebuild local meshes')
    return report
