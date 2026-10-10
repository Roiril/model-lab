"""実測結果だけをStudioと一枚のレポートへ出す。"""
from pathlib import Path
import base64
import hashlib
import html
import json
import math
import struct
import sys

HERE = Path(MODEL_HERE)
ROOT = HERE.parents[1]
BUILD = HERE / 'build'
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding='utf-8')
import params as P
import linkage as K

NAMES = ('box', 'lid', 'roof', 'crank', 'link', 'pin', 'clip', 'speaker_clip',
         'ref_body', 'ref_horn', 'ref_wire', 'ref_speaker')
Q = .005


def load(name):
    path = BUILD / name
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def mesh(name):
    raw = (BUILD / (name + '.stl')).read_bytes()
    n = struct.unpack_from('<I', raw, 80)[0]
    vertices, index, faces = [], {}, []
    for i in range(n):
        xyz = struct.unpack_from('<9f', raw, 84 + i * 50 + 12)
        face = []
        for j in range(3):
            point = tuple(round(xyz[3 * j + k] / Q) for k in range(3))
            if point not in index:
                index[point] = len(vertices)
                vertices.append(point)
            face.append(index[point])
        if len(set(face)) == 3:
            faces.extend(face)
    assert len(vertices) < 65536
    return dict(pos=base64.b64encode(struct.pack(f'<{len(vertices)*3}h', *[v for p in vertices for v in p])).decode(),
                ind=base64.b64encode(struct.pack(f'<{len(faces)}H', *faces)).decode(),
                nv=len(vertices), nt=len(faces) // 3)


def main():
    catalog = json.loads((HERE / 'catalog.json').read_text(encoding='utf-8'))
    verified = load('verify_report.json') or {}
    assert verified.get('ok'), 'Geometry and assembly must pass before delivery export'
    current_hashes = {name: hashlib.sha256((BUILD / (name + '.stl')).read_bytes()).hexdigest()
                      for name in NAMES}
    assert verified.get('input_sha256') == current_hashes, 'Verification is stale'
    physics = load('simulate_report.json')
    assert physics and physics.get('ok'), 'Physical simulation must pass before delivery export'
    assert physics.get('input_sha256') == current_hashes, 'Physical simulation is stale'
    plate = load('plate_report.json')
    slicing = load('slice_report.json')
    print_review = load('print_review.json')
    exterior = verified.get('exterior')
    kin = dict(H=K.H, O=K.O, a=K.A_LEN, l=K.L_LINK, alpha0=K.ALPHA0,
               A0=K.pin_a(K.ALPHA0), B0=K.pin_b(0), table=K.sweep(P.LID_OPEN_DEG, math.ceil(P.LID_OPEN_DEG * 2)),
               key_rel=P.BAYONET_KEY_DEG, mid_theta=P.LID_OPEN_DEG / 2, open_theta=P.LID_OPEN_DEG, bend_deg=0)
    notes = ['閉じた外形は80 × 80 × 80mm。外面の角丸と貫通穴は設けない。天面の継ぎ目は残る。',
             '配線口を設けないため電源と制御基板は内部へ置く。搭載する製品と保持方法は未確定。',
             'D1にも後ろの固定天面がある。C1の全面蓋とは異なる。',
             'SG92R正本のホーン長腕の左右配分とハブ寸法には写真推定値がある。クランク試片を先に刷る。',
             '計算結果は実印刷と実機動作の成功を意味しない。摩擦とスナップの固さは実物確認が必要。']
    if P.MODEL_ID.endswith('d2'):
        notes.append('D2のサーボ寸法はC2の寸法図候補。実物との一致は未確認。')
    report = dict(geometry=dict(exterior=exterior, topology=verified.get('topology'), calibration=verified.get('calibration')),
                  motion=verified.get('motion'), assembly=verified.get('assembly'), physics=physics,
                  printing=dict(plate=plate, slice=slicing, review=print_review), notes=notes,
                  input_sha256=current_hashes)
    data = dict(q=Q, meshes={name: mesh(name) for name in NAMES}, kin=kin, report=report,
                meta=dict(title=catalog['title'], summary=catalog['description']), view=dict(target=[0, 0, 60], dist=330))
    dest = ROOT / 'viewer' / 'd-cube' / 'assets'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / (P.MODEL_ID + '.json')).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

    e = html.escape
    rows = []
    def row(requirement, result):
        rows.append(f'<tr><th>{e(requirement)}</th><td>{e(str(result))}</td></tr>')
    row('外形', ' × '.join(f'{value:g}' for value in exterior['size_mm']) + ' mm' if exterior else '未検証')
    row('六面の形', f"{exterior['passed']} / {exterior['checked']} 点が平面。継ぎ目は別扱い。" if exterior else '未検証')
    topo = verified.get('topology')
    row('メッシュ', f"閉じたメッシュ {sum(v['ok'] for v in topo.values())} / {len(topo)} 部品" if topo else '未検証')
    motion = verified.get('motion')
    row('開閉の干渉', f"0〜{P.LID_OPEN_DEG:g}°。{motion['samples']} 姿勢。干渉 {len(motion['failures'])} 件。" if motion else '未検証')
    asm = verified.get('assembly')
    row('組み立て', f"{asm['passed']} / {asm['checked']} 項目が通過。実物は未確認。" if asm and asm.get('ok') else '検証中。合格扱いにしない。')
    row('必要トルク', f"{physics['static']['max_torque_Nm']:.5f} N·m。停動トルクの {physics['static']['ratio_to_stall']*100:.1f}%。" if physics else '未検証')
    row('開閉時間', f'{P.OPEN_TIME_S:g}秒。始めと終わりをゆっくり動かす。')
    row('印刷', 'スライス結果は下の検証値と印刷フォルダを参照。' if plate else 'スライス前。印刷可能とは未判定。')
    if plate:
        for material in ('PLA', 'PETG'):
            values = plate.get(material)
            if values:
                seconds = int(values['prediction_s'])
                row(material + 'の見積もり', f"{seconds // 3600}時間{seconds % 3600 // 60}分。{values['weight_g']}g。X1C / 0.4mm / 0.2mm。")
    css_path = ROOT / 'viewer' / 'd-cube' / 'report.css'
    css = css_path.read_text(encoding='utf-8')
    images = []
    for filename, caption in [('closed.png', '閉じた姿。外面は同じ色。'), ('open.png', '65°開いた姿。'), ('parts.png', '印刷部品。')]:
        path = BUILD / filename
        if path.exists():
            images.append(f'<figure><img style="width:100%;height:auto" alt="{e(caption)}" src="data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"><figcaption>{e(caption)}</figcaption></figure>')
    content = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(catalog['title'])}</title><style>{css}</style><body><main class="wrap">
<p class="eyebrow">MODEL LAB · 2026-10-10</p><h1>{e(catalog['title'])}</h1>
<p class="sub">角丸と穴がない立方体。SG92Rで天面を開く。</p>
<div class="lead"><p>80mm角の外装に蝶番を収めた。壁と底は3mm。固定天面は蝶番の上だけ最薄1.2mm。外の六面は平らにした。実物の嵌め合いは試片から確かめる。</p></div>
{''.join(images)}
<h2>要件ごとの結果</h2><div class="tblwrap"><table>{''.join(rows)}</table></div>
<h2>決めたこと</h2><p>外形を80mm角にした。蝶番はCから9mm上げて高さ74mmにした。サーボ位置とリンクBの閉位置はCを保った。CUBEとHINGE_Zで変更できる。LID_OPEN_DEGは65°。OPEN_TIME_Sは1.2秒。動き始めと終わりをゆっくりにする。</p>
<h2>譲ったこと</h2><p>D1にも後ろ側の固定天面を設けた。開閉の継ぎ目は残した。外部給電口を設けず内部電源を前提とする。</p>
<h2>印刷の向き</h2><p>外箱は底を下にする。蓋と固定天面は外面を下にする。蓋の内側の蝶番だけサポートを使う。外から見える面へサポートを付けない。サーボ台の短い渡りと爪の固さは試し刷りで確かめる。</p>
<h2>実物で確かめること</h2><ol>{''.join('<li>'+e(n)+'</li>' for n in notes[3:])}</ol>
<p>電源と制御基板の製品は指定されていない。部品の保持形状と実配線の収まりは未確認。</p>
<p><a href="http://localhost:3000/?model={P.MODEL_ID}">Studioを開く</a> · <a href="http://localhost:3000/viewer/d-cube/physics.html?model={P.MODEL_ID}">物理検証</a> · <a href="http://localhost:3000/viewer/d-cube/assembly.html?model={P.MODEL_ID}">組み立て</a></p>
<details><summary>検証値</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere">{e(json.dumps(report, ensure_ascii=False, indent=2))}</pre></details>
<p class="note">サーボの詳細寸法はリポジトリ内の正本を使用。停動トルクと速度は<a href="https://towerpro.com.tw/product/sg92r-7/">TowerPro SG92R仕様</a>を参照。</p>
</main></body></html>'''
    target = ROOT / 'reports' / ('2026-10-10_' + P.MODEL_ID + '.html')
    target.write_text(content, encoding='utf-8', newline='\n')
    print(str(target))


main()
