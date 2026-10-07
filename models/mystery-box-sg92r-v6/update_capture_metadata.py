"""Update requirements metadata only. The already-captive geometry is unchanged."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
p=R/'model.py';t=p.read_text('utf8')
t=t.replace('actual servo/horn/screw/cable are additional','actual servo/horn/cable are additional; no center screw is used')
if 'record=dict(center_screw_required=False,' not in t:t=t.replace('record=dict(size_mm=', 'record=dict(center_screw_required=False,size_mm=')
old="'Hinge carries radial weight; servo supplies gravity torque; unpowered lid can close'"
new="'Original horn is axially captured only after the body receivers and cross key are assembled; reference tooth engagement remains provisional',"+old
if 'Original horn is axially captured only after' not in t:t=t.replace(old,new)
compile(t,str(p),'exec');p.write_text(t,encoding='utf8')
p=R/'assembly_manifest.json';d=json.loads(p.read_text());d['center_screw_required']=False
d['notes']=[s.replace('actual servo/horn/screw/cable are additional','actual servo/horn/cable are additional; no center screw is used') for s in d['notes']]
note='Original horn is axially captured only after the body receivers and cross key are assembled; reference tooth engagement remains provisional'
if note not in d['notes']:d['notes'].append(note)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
p=R/'catalog.json';d=json.loads(p.read_text());d['description']='70 × 70 × 70 mmの箱。固定帯と平板蓋を4節リンクで65度開く。印刷13部品、中心ねじなし。箱と横キーの組立後にホーンを軸方向捕捉。実機未検証。';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print('Screwless capture metadata updated; geometry unchanged')
