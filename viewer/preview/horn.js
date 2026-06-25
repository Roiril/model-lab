// horn の即時プレビュー（add_horn_dummy と同じ形状を Three.js で再現）。
// build(P, THREE) -> THREE.Group。P の各値は params.py の mm 値。
// 座標: model(X,Y,Z上) -> three(x,z,y)。底 z=0。

export function build(P, THREE) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0x88ccff, metalness: 0.1, roughness: 0.6 });
  const MM = 0.001;
  const m = (v) => v * MM;
  const V = (x, y, z) => new THREE.Vector3(x, z, y);
  const types = ["cross", "single", "round"];
  const t = types[Math.max(0, Math.min(2, Math.round(P.HORN_TYPE || 0)))];
  const thick = P.THICKNESS;

  function vcyl(dia, h) {
    const r = m(dia) / 2;
    const me = new THREE.Mesh(new THREE.CylinderGeometry(r, r, m(h), 48), mat);
    me.position.copy(V(0, 0, m(h) / 2));
    g.add(me);
    return me;
  }
  function box(L, W, H) {
    const me = new THREE.Mesh(new THREE.BoxGeometry(m(L), m(H), m(W)), mat);
    me.position.copy(V(0, 0, m(H) / 2));
    g.add(me);
  }

  vcyl(P.HUB_DIA, thick);                       // 中央ハブ
  if (t === "cross" || t === "single") {
    box(P.ARM_SPAN_X, P.ARM_W_X, thick);          // 長腕（X）
    if (t === "cross") box(P.ARM_W_Y, P.ARM_SPAN_Y, thick); // 短腕（Y）
  } else if (t === "round") {
    vcyl(P.ROUND_DIA, thick);                   // 円盤
  }

  // センタービス穴（暗い円柱で表現）
  const holeMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, metalness: 0, roughness: 1 });
  const r = m(P.SCREW_DIA) / 2;
  const hole = new THREE.Mesh(new THREE.CylinderGeometry(r, r, m(thick) + 0.0006, 24), holeMat);
  hole.position.copy(V(0, 0, m(thick) / 2));
  g.add(hole);

  return g;
}
