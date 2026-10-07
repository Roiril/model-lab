// 座標変換の唯一の置き場。three を import しない純関数だけ。
// モデル座標 = STL の生の値 × unitScale（通常は Blender ワールド mm、Z 上）。
// 断面の平面は { axis, origin, normal, u, v }。normal = u × v。
// 実際の切断面は origin + normal * offset。2D 点 [u0, v0] のモデル座標は
//   origin + normal * offset + u * u0 + v * v0

export const AXES = {
  x: { u: [0, 1, 0], v: [0, 0, 1] },
  y: { u: [1, 0, 0], v: [0, 0, 1] },
  z: { u: [1, 0, 0], v: [0, 1, 0] },
};

// --- ベクトル小物 ---------------------------------------------------------
export const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
export const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
export const scale = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
export const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
export const cross = (a, b) => [
  a[1] * b[2] - a[2] * b[1],
  a[2] * b[0] - a[0] * b[2],
  a[0] * b[1] - a[1] * b[0],
];
export const len = (a) => Math.hypot(a[0], a[1], a[2]);
export const norm = (a) => {
  const l = len(a);
  return l > 0 ? [a[0] / l, a[1] / l, a[2] / l] : [0, 0, 0];
};

// 視線に最も近い軸（x / y / z）。cameraAxes 無しなら z
function pickAxis(cameraAxes) {
  const f = cameraAxes && cameraAxes.forward;
  if (!f) return "z";
  const ax = Math.abs(f[0]), ay = Math.abs(f[1]), az = Math.abs(f[2]);
  if (ax >= ay && ax >= az) return "x";
  if (ay >= az) return "y";
  return "z";
}

// 軸平面の origin は「法線方向の成分だけ」を持たせる。こうすると 2D の (u, v) が
// 正面図・側面図・上面図の座標そのもの（例: Y 面なら u = X, v = Z）になり、
// 人が読む数字とモデル座標がそろう。
// view 平面だけは クリックした点を origin にする（向きが任意で、そろえる軸が無い）。
//   axis: "x" | "y" | "z" | "view" | "auto"（視線に最も近い軸を選ぶ）
//   point: [x, y, z]（クリックしたモデル座標）
//   cameraAxes: { right, up, forward }（モデル座標の単位ベクトル。auto / view で使う）
export function makePlane(axis, point, cameraAxes) {
  if (axis === "view") {
    if (!cameraAxes || !cameraAxes.right || !cameraAxes.up) {
      throw new Error("makePlane: view には cameraAxes（right, up）が要ります");
    }
    const u = norm(cameraAxes.right);
    const v = norm(cameraAxes.up);
    return { axis: "view", origin: [point[0], point[1], point[2]], normal: norm(cross(u, v)), u, v };
  }
  const key = axis === "auto" ? pickAxis(cameraAxes) : axis;
  const basis = AXES[key];
  if (!basis) throw new Error(`makePlane: 未知の軸 ${axis}`);
  const u = basis.u.slice();
  const v = basis.v.slice();
  const normal = cross(u, v);
  const origin = scale(normal, dot(point, normal));
  return { axis: key, origin, normal, u, v };
}

// 実際の切断面（offset を含む）
export function planeAt(plane, offset = 0) {
  return { origin: add(plane.origin, scale(plane.normal, offset)), normal: plane.normal };
}

// 切断面の上の (u, v) → モデル座標
export function uvToModel(plane, offset, uv) {
  const o = add(plane.origin, scale(plane.normal, offset));
  return [
    o[0] + plane.u[0] * uv[0] + plane.v[0] * uv[1],
    o[1] + plane.u[1] * uv[0] + plane.v[1] * uv[1],
    o[2] + plane.u[2] * uv[0] + plane.v[2] * uv[1],
  ];
}

// モデル座標 → 切断面の (u, v)。面の外の点は面へ射影した位置になる
export function modelToUv(plane, offset, p) {
  const d = sub(p, add(plane.origin, scale(plane.normal, offset)));
  return [dot(d, plane.u), dot(d, plane.v)];
}

// 切断面の符号つき距離（normal 側が正）
export function signedDistance(plane, offset, p) {
  return dot(sub(p, add(plane.origin, scale(plane.normal, offset))), plane.normal);
}

// 切断面の位置を、原点から normal 方向に測った絶対値（mm）。UI の「位置」表示用
export function planePosition(plane, offset = 0) {
  return dot(plane.origin, plane.normal) + offset;
}
