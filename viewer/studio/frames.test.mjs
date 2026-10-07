// node viewer/studio/frames.test.mjs
import {
  AXES, makePlane, uvToModel, modelToUv, planeAt, planePosition, signedDistance,
  add, sub, scale, dot, cross, norm, len,
} from "./frames.js";

let pass = 0, fail = 0;
function ok(cond, name, detail = "") {
  if (cond) { pass++; console.log(`OK   ${name}`); }
  else { fail++; console.log(`FAIL ${name} ${detail}`); }
}
const near = (a, b, e = 1e-9) => Math.abs(a - b) <= e;
const nearV = (a, b, e = 1e-9) => a.length === b.length && a.every((x, i) => near(x, b[i], e));

// 1. 軸ごとの基底（CONTRACT §2）
const expect = {
  x: { u: [0, 1, 0], v: [0, 0, 1], n: [1, 0, 0] },
  y: { u: [1, 0, 0], v: [0, 0, 1], n: [0, -1, 0] },
  z: { u: [1, 0, 0], v: [0, 1, 0], n: [0, 0, 1] },
};
const P = [12.5, -7.25, 33];
for (const k of ["x", "y", "z"]) {
  const pl = makePlane(k, P, null);
  ok(pl.axis === k, `${k}: axis`);
  ok(nearV(pl.u, expect[k].u), `${k}: u`, JSON.stringify(pl.u));
  ok(nearV(pl.v, expect[k].v), `${k}: v`, JSON.stringify(pl.v));
  ok(nearV(pl.normal, expect[k].n), `${k}: normal`, JSON.stringify(pl.normal));
  ok(nearV(pl.normal, cross(pl.u, pl.v)), `${k}: normal = u × v`);
  ok(nearV(pl.u, AXES[k].u) && nearV(pl.v, AXES[k].v), `${k}: AXES と一致`);
  ok(near(dot(pl.u, pl.v), 0) && near(dot(pl.u, pl.normal), 0) && near(dot(pl.v, pl.normal), 0), `${k}: 直交`);
  // クリックした点は面の上（offset 0 の符号つき距離が 0）
  ok(near(signedDistance(pl, 0, P), 0), `${k}: クリック点が面上`, String(signedDistance(pl, 0, P)));
}

// 2. 軸平面の (u, v) は人が読むモデル座標そのもの
{
  const py = makePlane("y", P, null);   // 正面図: u = X, v = Z
  ok(nearV(modelToUv(py, 0, P), [P[0], P[2]]), "y 面: (u, v) = (X, Z)", JSON.stringify(modelToUv(py, 0, P)));
  const px = makePlane("x", P, null);   // 側面図: u = Y, v = Z
  ok(nearV(modelToUv(px, 0, P), [P[1], P[2]]), "x 面: (u, v) = (Y, Z)");
  const pz = makePlane("z", P, null);   // 上面図: u = X, v = Y
  ok(nearV(modelToUv(pz, 0, P), [P[0], P[1]]), "z 面: (u, v) = (X, Y)");
}

// 3. 往復 uv → model → uv（offset あり・なし、全種類の平面）
const camera = { right: [0.8, 0.6, 0], up: [-0.36, 0.48, 0.8], forward: [-0.48, 0.64, -0.6] };  // forward = -(right × up)
for (const axis of ["x", "y", "z", "view", "auto"]) {
  const pl = makePlane(axis, P, camera);
  for (const offset of [0, 3.5, -12.25]) {
    let worst = 0;
    for (const uv of [[0, 0], [10, -4], [-123.456, 78.9], [0.001, 0.002]]) {
      const m = uvToModel(pl, offset, uv);
      const back = modelToUv(pl, offset, m);
      worst = Math.max(worst, Math.abs(back[0] - uv[0]), Math.abs(back[1] - uv[1]));
      // 変換した点は切断面の上にある
      worst = Math.max(worst, Math.abs(signedDistance(pl, offset, m)));
    }
    ok(worst < 1e-9, `往復 ${axis} offset=${offset}`, `誤差 ${worst}`);
  }
}

// 4. 逆向きの往復 model → uv → model（面の上の点は戻る）
{
  const pl = makePlane("view", P, camera);
  const offset = 5;
  const onPlane = uvToModel(pl, offset, [3, 4]);
  const uv = modelToUv(pl, offset, onPlane);
  ok(nearV(uvToModel(pl, offset, uv), onPlane), "view: model → uv → model");
}

// 5. offset は normal 方向の平行移動
{
  const pl = makePlane("y", P, null);
  const a = uvToModel(pl, 0, [10, 20]);
  const b = uvToModel(pl, 7, [10, 20]);
  ok(nearV(sub(b, a), scale(pl.normal, 7)), "offset は normal 方向");
  const at = planeAt(pl, 7);
  ok(nearV(at.normal, pl.normal) && near(signedDistance(pl, 7, at.origin), 0), "planeAt");
  ok(near(planePosition(pl, 0), -P[1]) , "planePosition は normal 方向の絶対位置", String(planePosition(pl, 0)));
  ok(near(planePosition(pl, 7), -P[1] + 7), "planePosition + offset");
}

// 6. auto: 視線に最も近い軸
{
  const cases = [
    [[0.1, -0.99, 0.05], "y"],
    [[0.98, 0.1, -0.1], "x"],
    [[-0.9, 0.2, 0.1], "x"],
    [[0.05, 0.1, -0.99], "z"],
    [[0.5, -0.6, -0.62], "z"],
    [[0.5, -0.7, 0.3], "y"],
  ];
  for (const [forward, want] of cases) {
    const pl = makePlane("auto", P, { right: [1, 0, 0], up: [0, 0, 1], forward });
    ok(pl.axis === want, `auto: forward=${JSON.stringify(forward)} → ${want}`, `実際 ${pl.axis}`);
  }
  const none = makePlane("auto", P, null);
  ok(none.axis === "z", "auto: cameraAxes 無しは z");
}

// 7. view は cameraAxes を使う
{
  const pl = makePlane("view", P, camera);
  ok(pl.axis === "view", "view: axis");
  ok(nearV(pl.u, norm(camera.right)), "view: u = right");
  ok(nearV(pl.v, norm(camera.up)), "view: v = up");
  ok(nearV(pl.normal, cross(pl.u, pl.v)), "view: normal = u × v");
  ok(near(len(pl.normal), 1), "view: normal は単位");
  ok(nearV(pl.origin, P), "view: origin = クリック点");
  // right × up は視線の逆（手前向き）になる右手系の約束
  const f = norm(camera.forward);
  ok(dot(pl.normal, f) < 0, "view: normal は視線と逆向き（手前を向く）", String(dot(pl.normal, f)));
  let threw = false;
  try { makePlane("view", P, null); } catch { threw = true; }
  ok(threw, "view: cameraAxes 無しは例外");
}

// 8. ベクトル小物
ok(nearV(add([1, 2, 3], [4, 5, 6]), [5, 7, 9]), "add");
ok(nearV(sub([4, 5, 6], [1, 2, 3]), [3, 3, 3]), "sub");
ok(nearV(scale([1, 2, 3], 2), [2, 4, 6]), "scale");
ok(near(dot([1, 2, 3], [4, 5, 6]), 32), "dot");
ok(nearV(cross([1, 0, 0], [0, 1, 0]), [0, 0, 1]), "cross");
ok(near(len([3, 4, 12]), 13), "len");
ok(nearV(norm([0, 3, 4]), [0, 0.6, 0.8]), "norm");
ok(nearV(norm([0, 0, 0]), [0, 0, 0]), "norm: ゼロベクトル");

console.log(`\n${pass} OK / ${fail} FAIL`);
process.exit(fail ? 1 : 0);
