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
const finite3 = (a) => Array.isArray(a) && a.length === 3 && a.every(Number.isFinite);

// u を優先して v を直交化する。normal は必ず u × v から作り直す。
export function orthonormalPlane(plane) {
  if (!plane || !finite3(plane.origin) || !finite3(plane.u) || !finite3(plane.v)) {
    throw new Error("orthonormalPlane: 平面の座標が不正です");
  }
  const u = norm(plane.u);
  if (len(u) < 0.5) throw new Error("orthonormalPlane: u の長さがありません");
  const v0 = sub(plane.v, scale(u, dot(plane.v, u)));
  const v = norm(v0);
  if (len(v) < 0.5) throw new Error("orthonormalPlane: u と v が平行です");
  const normal = norm(cross(u, v));
  return { axis: plane.axis || "view", origin: plane.origin.slice(), normal, u, v };
}

// offset を統合した実際の平面位置と正規直交基底。回転ギズモの中心に使う。
export function planeFrame(plane, offset = 0) {
  if (!Number.isFinite(offset)) throw new Error("planeFrame: offset が不正です");
  const p = orthonormalPlane(plane);
  return { origin: add(p.origin, scale(p.normal, offset)), normal: p.normal, u: p.u, v: p.v };
}

// 軸断面でもハンドルを部品上へ置けるよう、中心を同じ平面へ射影する。
export function planeHandleFrame(plane, offset = 0, center = null) {
  const frame = planeFrame(plane, offset);
  if (center === null) return frame;
  if (!finite3(center)) throw new Error("planeHandleFrame: 中心が不正です");
  const distance = dot(sub(center, frame.origin), frame.normal);
  return { ...frame, origin: sub(center, scale(frame.normal, distance)) };
}

// ギズモの位置・ローカル X/Y から、offset を 0 に統合した平面を作る。
export function planeFromFrame(origin, u, v, axis = "view") {
  return orthonormalPlane({ axis, origin, u, v });
}

// 面法線から安定した u/v を作る。画面右を面へ射影し、平行なら最も離れたモデル軸を使う。
export function makePlaneFromNormal(point, normal, cameraAxes) {
  if (!finite3(point) || !finite3(normal)) throw new Error("makePlaneFromNormal: 点または法線が不正です");
  const n = norm(normal);
  if (len(n) < 0.5) throw new Error("makePlaneFromNormal: 法線の長さがありません");
  const candidates = [];
  if (cameraAxes && finite3(cameraAxes.right)) candidates.push(cameraAxes.right);
  candidates.push([1, 0, 0], [0, 1, 0], [0, 0, 1]);
  let u = null;
  for (const candidate of candidates) {
    const projected = sub(candidate, scale(n, dot(candidate, n)));
    if (len(projected) > 1e-8) { u = norm(projected); break; }
  }
  if (!u) throw new Error("makePlaneFromNormal: u を作れません");
  const v = norm(cross(n, u));
  return { axis: "view", origin: point.slice(), normal: n, u, v };
}

// 表示用 modelBox に依存せず、実メッシュの bbox だけから中心を求める。
export function meshBoundsCenter(meshes) {
  const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  let found = false;
  for (const mesh of meshes || []) {
    const b = mesh && mesh.userData && mesh.userData.bbox;
    if (!b || !finite3(b.min) || !finite3(b.max)) continue;
    found = true;
    for (let axis = 0; axis < 3; axis++) {
      min[axis] = Math.min(min[axis], b.min[axis]);
      max[axis] = Math.max(max[axis], b.max[axis]);
    }
  }
  return found ? min.map((value, axis) => (value + max[axis]) / 2) : null;
}

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
