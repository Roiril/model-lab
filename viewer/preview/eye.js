// eye の即時プレビュー（目玉ボール）。build(P, THREE) -> THREE.Group。P は mm。
// 座標: model(z上) -> three(y上)。底を少し平らにした球。

export function build(P, THREE) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0x222228, metalness: 0.1, roughness: 0.4 });
  const MM = 0.001;
  const m = (v) => v * MM;
  const r = m(P.EYE_DIA) / 2;
  const flat = m(P.FLAT_H || 0);

  const s = new THREE.Mesh(new THREE.SphereGeometry(r, 48, 32), mat);
  // model: 中心 z=r → three: y=r。底の平面は簡略化（プレビューは球で表示）
  s.position.set(0, r, 0);
  g.add(s);
  return g;
}
