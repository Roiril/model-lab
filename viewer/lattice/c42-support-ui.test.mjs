import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { removableSupportRows } from './physics-ui.mjs';

test('支えの表示は実G-codeの値を使い、測定が無い場合は作らない', () => {
  const supportId = 'guide_center_stop_print_support';
  const geometry = { parts: { guide_frame: { supports: [{
    id: supportId, decision: 'accepted', nominalProductCommonManifoldMm3: 0,
    actualComponent: { bedMinZMm: 0 }, supportTopZMm: 8,
    productFirstZMm: 8.4, geometricClearanceMm: 0.4, materialFaceGapMm: 0.2,
  }] } } };
  const footprint = { supportId, actualSupportLastExtrusionZMm: 8,
    actualProductFirstExtrusionZMm: 8.4, actualMaterialFaceGapMm: 0.2,
    footprint: { depositedAreaEstimateMm2: 42 }, decision: 'accepted' };
  const first = { plates: { full_PLA: { objects: [{
    componentStability: { supportFootprints: [footprint] },
  }] } } };
  const show = evidence => removableSupportRows(null, null, geometry, null, evidence)[0];
  const measured = show(first);
  assert.match(measured.detail, /PLA G-code測定.*実材料面空隙 0\.2 mm.*接地面積 42 mm²/);
  assert.equal(measured.pass, false, '実物の除去確認を数値検査で代用しない');
  footprint.actualMaterialFaceGapMm = 0;
  footprint.decision = 'rejected';
  assert.match(show(first).detail, /実材料面空隙 0 mm.*安定性 要確認/);
  assert.match(show(null).detail, /G-code測定なし/);
});

test('C4-2の支えは形状検査を表示し、ユーザーが行うスライスを未検証と表示する', () => {
  const data = JSON.parse(readFileSync(new URL('./assets/mystery-box-sg92r-c4-2.json', import.meta.url)));
  assert.equal(data.delivery.status, 'layout_only');
  assert.equal(data.first_layer_contact_evidence, null);
  assert.equal(data.print_path_review, null);
  const rows = removableSupportRows(data.print_path_review, data.print_path_evidence,
    data.print_support_geometry, data.closed_loop_support_evidence, data.first_layer_contact_evidence);
  const supports = Object.values(data.print_support_geometry.parts)
    .flatMap(part => part.supports || []);
  assert.ok(supports.length > 0, '実STLの分離した支えが記録されている');
  for (const support of supports)
    assert.ok(rows.some(row => row.id.startsWith(`print-support-${support.id}`)),
      `${support.id}の実測を表示する`);
  for (const row of rows) {
    assert.match(row.detail, /形状検査 適合/);
    assert.match(row.detail, /G-code測定なし/);
    assert.doesNotMatch(row.detail, /\[object Object\]/);
    assert.doesNotMatch(row.label, /print_support/);
    assert.equal(row.chip, '実物未確認');
  }
});

test('高さが異なる支持部位の押出Zを混ぜずに表示する', () => {
  const id = 'guide_frame_print_support';
  const regions = [
    { id: 'key_stop_arm', actualSupportLastExtrusionZMm: 3.8,
      actualProductFirstExtrusionZMm: 4.2, actualMaterialFaceGapMm: 0.2, decision: 'accepted' },
    { id: 'outer_frame', actualSupportLastExtrusionZMm: 27.8,
      actualProductFirstExtrusionZMm: 28.2, actualMaterialFaceGapMm: 0.2, decision: 'accepted' },
  ];
  const geometry = { parts: { guide_frame: { supports: [{ id, decision: 'accepted',
    actualComponent: { bedMinZMm: 0 }, materialFaceGapMm: 0.2,
    regionalContactEvidence: regions.map(region => ({ region: region.id,
      support_top_z_mm: region.actualSupportLastExtrusionZMm,
      product_first_z_mm: region.actualProductFirstExtrusionZMm - 0.2,
      declaredGeometricClearanceMm: 0.2 })),
  }] } } };
  const first = { plates: { full_PLA: { objects: [{ componentStability: {
    supportFootprints: [{ supportId: id, regions, decision: 'accepted',
      actualSupportLastExtrusionZMm: null, actualProductFirstExtrusionZMm: null,
      actualMaterialFaceGapMm: 0.2, footprint: { depositedAreaEstimateMm2: 80 } }],
  } }] } } };
  const rows = removableSupportRows(null, null, geometry, null, first);
  const key = rows.find(row => row.id.endsWith('key_stop_arm'));
  const outer = rows.find(row => row.id.endsWith('outer_frame'));
  assert.match(key.detail, /PLA G-code測定（中央の止め板）: 支え最終押出Z 3\.8 mm。製品初層Z 4\.2 mm。実材料面空隙 0\.2 mm/);
  assert.doesNotMatch(key.detail, /製品初層Z 28\.2/);
  assert.match(outer.detail, /PLA G-code測定（外周の枠）: 支え最終押出Z 27\.8 mm。製品初層Z 28\.2 mm。実材料面空隙 0\.2 mm/);
  assert.doesNotMatch(outer.detail, /製品初層Z 4\.2/);
});
