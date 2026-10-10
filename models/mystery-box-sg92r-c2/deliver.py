"""印刷ファイルを集め、3mfの配置をXMLから検査する。"""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPORTS = ROOT / 'exports'
DEST = ROOT / 'prints' / HERE.name
PARTS = ('box', 'lid', 'crank', 'link', 'pin', 'clip', 'speaker_clip', 'roof')
COUPONS = ('servo_fit_test', 'speaker_test', 'roof_test_body', 'roof_test')
NS = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
IDENTITY = (1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)


def placed_bounds(path):
    with zipfile.ZipFile(path) as archive:
        documents = {name: ET.fromstring(archive.read(name)) for name in archive.namelist() if name.endswith('.model')}
        def vertices(document, object_id):
            obj = next(o for o in documents[document].iter(NS + 'object') if o.get('id') == object_id)
            mesh = obj.find(NS + 'mesh')
            if mesh is not None:
                return [tuple(float(v.get(k)) for k in ('x', 'y', 'z')) for v in mesh.find(NS + 'vertices')]
            result = []
            for component in obj.find(NS + 'components'):
                child = next((value.lstrip('/') for key, value in component.attrib.items() if key.split('}')[-1] == 'path'), document)
                points = vertices(child, component.get('objectid'))
                result.extend(transform(points, component.get('transform')))
            return result
        main = documents['3D/3dmodel.model']
        rows = []
        for item in main.find(NS + 'build'):
            points = transform(vertices('3D/3dmodel.model', item.get('objectid')), item.get('transform'))
            lo = [min(v[i] for v in points) for i in range(3)]
            hi = [max(v[i] for v in points) for i in range(3)]
            rows.append(dict(id=item.get('objectid'), min=lo, max=hi,
                             off_bed=lo[0] < 0 or lo[1] < 0 or hi[0] > 256 or hi[1] > 256 or lo[2] < -0.001 or hi[2] > 250,
                             excluded=any(v[0] < 18 and v[1] < 28 for v in points)))
        overlaps = []
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                if all(min(a['max'][j], b['max'][j]) - max(a['min'][j], b['min'][j]) > 0.001 for j in (0, 1)):
                    overlaps.append([a['id'], b['id']])
        return dict(objects=rows, bbox_overlaps=overlaps, ok=not overlaps and not any(r['off_bed'] or r['excluded'] for r in rows))


def transform(points, attribute):
    m = tuple(map(float, attribute.split())) if attribute else IDENTITY
    return [(x*m[0]+y*m[3]+z*m[6]+m[9], x*m[1]+y*m[4]+z*m[7]+m[10], x*m[2]+y*m[5]+z*m[8]+m[11]) for x, y, z in points]


def main():
    read = lambda name: json.loads((HERE / 'build' / name).read_text(encoding='utf-8'))
    model, verify, review, sliced, boolean = [read(name) for name in ('model_report.json', 'verify_report.json', 'print_review.json', 'slice_report.json', 'boolean_report.json')]
    assert verify['calibration']['ok'] and sliced['calibration']['ok'] and review['calibration']['ok'] and boolean['ok']
    assert len(sliced['parts']) == len(PARTS)*2
    assert all('error' not in part for part in sliced['parts'].values())
    plates = read('plate_report.json')
    assert all(str(plates[key]['support_used']).lower() == 'false'
               for key in ('PLA', 'PETG', 'crank_test', 'servo_fit_test', 'speaker_test', 'joints_test',
                           'roof_test_PLA', 'roof_test_PETG'))
    servo_fit = verify['servo_fit']
    assert servo_fit['ok']
    assert servo_fit['coupon_datums']['components'] == 1
    assert servo_fit['minimum_wall_mm'] >= 1.2
    assert not [row for row in review['parts']['servo_fit_test']['thin_under_1_2mm']
                if row['min_mm'] < 1.195]
    assert not verify['assembly']['D_servo_unit_lower']['worst']
    assert verify['assembly']['clip_snap_strain_pct'] <= 2
    assert not verify['motion_summary']['poses_with_hits']
    topology = read('stl_topology.json')
    assert topology['calibration']['ok']
    assert all(not any(result[k] for k in ('nonmanifold_edges', 'winding_mismatches',
                                         'duplicate_faces', 'degenerate_faces'))
               for result in topology['parts'].values())
    assert all(model['parts'][p]['nonmanifold'] == 0 for p in PARTS)
    assert all(not [r for r in review['parts'][p]['thin_under_1_2mm'] if r['min_mm'] < 1.195] for p in PARTS)
    assert verify['assembly']['F_link_bend_strain_pct'] <= 2
    assert verify['assembly']['C3_bayonet_lock']['ok']
    assert not verify['assembly']['G_lid_place_after_servo']['worst']
    assert not verify['assembly']['F_lid_down_with_link_bent']['hits']
    assert not verify['assembly']['F_bent_link_fixed_parts']
    assert not any(verify['assembly']['J_finger_approach']['obstacles'].values())
    assert not any(verify['assembly']['J_finger_press']['obstacles'].values())
    assert verify['assembly']['J_roof_release']['wall_clearance_mm'] >= 0.3
    roof_lower = verify['assembly'].get('J_roof_lower')
    if roof_lower is not None:
        assert roof_lower.get('travel_mm') == 45
        assert all(name == 'roof-box' and hit.get('depth', 99) <= 0.805
                   for name, hit in roof_lower.get('worst', {}).items())
    roof_strain = verify['assembly'].get('J_roof_press_strain_pct')
    if roof_strain is not None:
        assert roof_strain <= 2
    roof_release = verify['assembly'].get('J_roof_release')
    if roof_release is not None:
        assert roof_release.get('travel_mm') == 45
        assert all(hit.get('depth', 99) <= 0.001 for hit in roof_release.get('worst', {}).values())
    DEST.mkdir(parents=True, exist_ok=True)
    files = []
    for part in PARTS + COUPONS:
        src = EXPORTS / f'{HERE.name}-{part}.stl'
        dst = DEST / f'{part}.stl'
        shutil.copyfile(src, dst)
        files.append(dst)
    outputs = ('PLA', 'PETG', 'crank-test-PLA', 'servo-fit-test-PLA', 'speaker-test-PLA', 'joints-test-PLA',
               'roof-test-PLA', 'roof-test-PETG', 'plate')
    placements = {}
    for key in outputs:
        suffix = '.3mf' if key == 'plate' else '.gcode.3mf'
        src = EXPORTS / f'{HERE.name}-{key}{suffix}'
        dst = DEST / src.name
        shutil.copyfile(src, dst)
        files.append(dst)
        placements[key] = placed_bounds(dst)
        assert placements[key]['ok'], placements[key]
    manifest = dict(model=HERE.name, parts=len(PARTS), pose_checks=verify['motion_summary']['steps'],
                    servo_dimension_profile=model.get('servo_dimension_profile'),
                    servo_fit=verify.get('servo_fit'),
                    placements=placements, files=[dict(name=f.name, bytes=f.stat().st_size, sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files])
    tmp = DEST / 'manifest.tmp'
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')
    tmp.replace(DEST / 'manifest.json')
    (HERE / 'build' / 'delivery_report.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')
    print(json.dumps(dict(parts=len(PARTS), poses=manifest['pose_checks'], files=len(files),
                          placements={k:v['ok'] for k,v in placements.items()})))


if __name__ == '__main__':
    main()
