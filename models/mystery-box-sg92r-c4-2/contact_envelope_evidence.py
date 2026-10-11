"""実STLの接触包絡と表示用角度表の補間誤差を記録する。"""
from pathlib import Path
import hashlib
import json
import os
import sys
import contact_envelope as envelope
import params as P

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).parent.absolute()
ROOT = HERE.parents[1]
BUILD = HERE / 'build'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interpolation_pass(minimum, maximum, limit_mm):
    return max(abs(minimum), abs(maximum)) <= limit_mm


def main():
    path = BUILD / 'motion.json'
    document = json.loads(path.read_text(encoding='utf-8'))
    frames = document['frames']
    rows = []
    for group_index, group in enumerate(P.GROUPS):
        low = high = 0.0
        worst_low = worst_high = None
        samples = 0
        for left, right in zip(frames, frames[1:]):
            a, b = left['servo_deg'], right['servo_deg']
            za = left['transforms']['carrier_' + group][14]
            zb = right['transforms']['carrier_' + group][14]
            for fraction in (.25, .5, .75):
                degree = a + (b - a) * fraction
                actual = envelope.lift_mm(group_index, round(degree, 10))
                interpolated = za + (zb - za) * fraction
                error = interpolated - actual
                samples += 1
                if error < low:
                    low, worst_low = error, degree
                if error > high:
                    high, worst_high = error, degree
        rows.append({'group': group, 'samples': samples,
                     'minimumInterpolatedMinusActualMm': low,
                     'maximumInterpolatedMinusActualMm': high,
                     'worstBelowAngleDeg': worst_low, 'worstAboveAngleDeg': worst_high})
    calibration = envelope.calibration()
    sources = {f'models/{P.MODEL_ID}/{name}': value
               for name, value in envelope.source_hashes().items()}
    sources.update({f'models/{P.MODEL_ID}/motion.py': digest(HERE / 'motion.py'),
                    f'models/{P.MODEL_ID}/contact_envelope_evidence.py': digest(Path(__file__)),
                    f'models/{P.MODEL_ID}/build/motion.json': digest(path)})
    table_sources_match = document['contactEnvelope']['sourceSha256'] == {
        f'models/{P.MODEL_ID}/{name}': value
        for name, value in envelope.source_hashes().items()}
    minimum = min(row['minimumInterpolatedMinusActualMm'] for row in rows)
    maximum = max(row['maximumInterpolatedMinusActualMm'] for row in rows)
    # 表示表の誤差の上限。151姿勢のSTL体積判定はverify.pyで別に行う。
    interpolation_limit_mm = 0.0001
    # 同じ計器へ実STLから得た粗い1度表を流す。
    # 足の寸法変更後も負例を古い角度に固定しない。
    coarse_candidates = []
    for group_index, row in enumerate(rows):
        for field in ('worstBelowAngleDeg', 'worstAboveAngleDeg'):
            degree = row[field]
            if degree is None:
                continue
            a = float(int(degree))
            b = a + 1.0
            za, zb = envelope.lift_mm(group_index, a), envelope.lift_mm(group_index, b)
            for fraction in (.25, .5, .75):
                actual = envelope.lift_mm(group_index, a + fraction)
                error = za + (zb - za) * fraction - actual
                coarse_candidates.append((abs(error), error, a, b, fraction, row['group']))
    _, coarse_error, coarse_a, coarse_b, coarse_fraction, coarse_group = max(coarse_candidates)
    meter_calibration = {
        'known_small_errors_accepted': interpolation_pass(-.00002, .00002, interpolation_limit_mm),
        'actual_coarse_interval_rejected': not interpolation_pass(coarse_error, coarse_error, interpolation_limit_mm),
        'coarseIntervalDeg': [coarse_a, coarse_b], 'coarseSampleFraction': coarse_fraction,
        'coarseGroup': coarse_group, 'coarseInterpolatedMinusActualMm': coarse_error}
    meter_calibration['pass'] = (meter_calibration['known_small_errors_accepted']
                                 and meter_calibration['actual_coarse_interval_rejected'])
    result = {'model': P.MODEL_ID,
              'method': 'maximum_over_actual_STL_overlap_vertices_and_edge_intersections',
              'calibration': calibration, 'sourceSha256': sources,
              'interpolationMeterCalibration': meter_calibration,
              'tableSourcesMatch': table_sources_match,
              'interpolation': {'frameStepDeg': document['contactEnvelope']['frameStepDeg'],
                  'sampleFractionsPerInterval': [.25, .5, .75], 'groups': rows,
                  'totalSamples': sum(row['samples'] for row in rows),
                  'minimumInterpolatedMinusActualMm': minimum,
                  'maximumInterpolatedMinusActualMm': maximum,
                  'limitMm': interpolation_limit_mm,
                  'pass': interpolation_pass(minimum, maximum, interpolation_limit_mm)},
              'limits': ['Finite samples bound the observed interpolation error.',
                         'This is not a continuous collision proof or a physical test.']}
    result['pass'] = (calibration['pass'] and meter_calibration['pass'] and table_sources_match
                      and result['interpolation']['pass'])
    target = BUILD / 'contact_envelope_evidence.json'
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n',
                         encoding='utf-8', newline='\n')
    os.replace(temporary, target)
    print(json.dumps({'pass': result['pass'], 'samples': result['interpolation']['totalSamples'],
                      'minimumMm': minimum, 'maximumMm': maximum}))
    return 0 if result['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
