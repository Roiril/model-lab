"""Copy the independent gate's measured verdict into the viewer contract.

Run after a successful current gate, then rerun the gate to refresh its hashes.
The motion and assembly poses are never changed here.
"""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'lib'))
sys.stdout.reconfigure(encoding='utf-8')
from mechgate_lib.gate import freshness
from printmech.contract import read_json,write_json

if __name__=='__main__':
    state,details=freshness('flag-box')
    if state!='pass':
        raise SystemExit(f'Current independent gate is required: {state}: {details}')
    report=read_json(HERE/'build'/'gate_report.json')
    checks={r['id']:r for r in report['checks']}
    assert checks['assembly.path']['pass'] and checks['instrument.calibration']['pass']
    assembly=read_json(HERE/'build'/'assembly.json')
    assembly['calibration']=checks['instrument.calibration']['detail']
    assembly['pass']=checks['assembly.path']['pass']
    assembly['verified_by']={'command':'py -3.11 tools/mechgate.py check flag-box','generatedAt':report['generatedAt'],
                             'note':'Only metadata copied from independently measured verdict. Poses unchanged.'}
    write_json(HERE/'build'/'assembly.json',assembly)
    print('Independent measured assembly verdict recorded. Rerun gate to refresh hashes.')
