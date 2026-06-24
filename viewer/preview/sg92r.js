// sg92r の即時プレビュー（add_servo_dummy と同じ形状を Three.js で再現）。
// build(P, THREE) -> THREE.Group。P の各値は params.py の mm 値。
// 座標マッピング: model(X長手, Y幅, Z上) -> three(x, z, y)。本体底 z=0。

export function build(P, THREE) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0x88ccff, metalness: 0.1, roughness: 0.6 });
  const MM = 0.001;
  const m = (v) => v * MM;
  const V = (x, y, z) => new THREE.Vector3(x, z, y); // model -> three

  // model 寸法の箱（L=x, W=y, H=z）。中心は model 座標 (cx,cy,cz)
  function box(L, W, H, cx, cy, cz) {
    const me = new THREE.Mesh(new THREE.BoxGeometry(m(L), m(H), m(W)), mat);
    me.position.copy(V(m(cx), m(cy), m(cz)));
    g.add(me);
    return me;
  }
  // 縦（model-z）円柱。底面 z=czBottom から高さ h
  function vcyl(dia, h, cx, cy, czBottom, seg = 48) {
    const r = m(dia) / 2;
    const me = new THREE.Mesh(new THREE.CylinderGeometry(r, r, m(h), seg), mat);
    me.position.copy(V(m(cx), m(cy), m(czBottom) + m(h) / 2));
    g.add(me);
    return me;
  }

  const cx = -P.SHAFT_OFFSET;          // 軸が原点に来るよう本体は -X
  const bodyTop = P.BODY_H;            // 本体底 z=0
  const ffb = P.FLANGE_FROM_BOTTOM;

  // 本体
  box(P.BODY_L, P.BODY_W, P.BODY_H, cx, 0, P.BODY_H / 2);
  // 羽根（両耳）
  box(P.FLANGE_L, P.FLANGE_W, P.FLANGE_T, cx, 0, ffb - P.FLANGE_T / 2);
  // 取付タブ穴 ⌀（暗い円柱で穴を表現）
  const holeMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, metalness: 0, roughness: 1 });
  for (const sx of [-1, 1]) {
    const r = m(P.TAB_HOLE_DIA) / 2;
    const h = new THREE.Mesh(new THREE.CylinderGeometry(r, r, m(P.FLANGE_T) + 0.0006, 20), holeMat);
    h.position.copy(V(m(cx + sx * P.SCREW_SPACING / 2), 0, m(ffb - P.FLANGE_T / 2)));
    g.add(h);
  }
  // 大円柱（ギアカバー座）
  vcyl(P.BOSS_DIA, P.BOSS_H, 0, 0, bodyTop);
  // 小円柱（出力軸スプライン）
  vcyl(P.SHAFT_DIA, P.SHAFT_H, 0, 0, bodyTop + P.BOSS_H);
  // 配線スタブ（背面 -X）
  box(8, 4, 4, cx - P.BODY_L / 2 - 4 + 1, 0, 2);

  return g;
}
