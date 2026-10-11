import { createWorkspaceNav, themePalette, watchTheme } from '../shared/workspace.mjs';
import {
  C1_REFERENCE_VIEW,
  MECHANISM_FRAGMENT_SHADER,
  MECHANISM_VERTEX_SHADER,
  MECHANISM_VIEW_CONTROLS,
} from '../shared/mechanism-view.mjs';
import { frameAt, identity4 } from './motion.mjs';
import { setupPhysics } from './physics-ui.mjs';
import { drivePresentation } from './sim.mjs';
import { setupAssembly } from './assembly-ui.mjs';

const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
const allowedModels = new Set(['mystery-box-sg92r-c3', 'mystery-box-sg92r-c4']);
const model = allowedModels.has(params.get('model')) ? params.get('model') : 'mystery-box-sg92r-c3';
const mode = params.get('mode') === 'assembly' ? 'assembly' : 'physics';
const assetUrl = `assets/${model}.json`;
const profile = model.endsWith('-c4')
  ? { title: '六角格子の呼吸', label: 'C4', fallback: ['外形', '76 × 76 × 76 mm'], pattern: '19個の六角格子。中心は約6mm。内側の環は約4mm。外側の環は約2mm持ち上がります。' }
  : { title: '立方格子の波', label: 'C3', fallback: ['格子', '5 × 5 / 25枚'], pattern: '25枚の正方形を5列に分けました。中央から外側へ最大3mmの隆起が移ります。' };

document.body.dataset.mode = mode;
const nav = createWorkspaceNav({ active: mode, model });
$('workspaceNav').replaceWith(nav.element);
function updateModelLinks() {
  for (const [id, target] of [['c3Link', 'mystery-box-sg92r-c3'], ['c4Link', 'mystery-box-sg92r-c4']]) {
    const link = $(id);
    const url = new URL(location.href);
    url.searchParams.set('model', target);
    url.searchParams.set('mode', mode);
    link.href = url.pathname + url.search;
    if (target === model) link.setAttribute('aria-current', 'page');
  }
}
updateModelLinks();
const disposeModelTheme = watchTheme(updateModelLinks);
addEventListener('pagehide', () => disposeModelTheme(), { once: true });
$('dataDownload').href = assetUrl;
$('dataDownload').download = `${model}.json`;

const EXTERIOR_WORDS = /(?:box|body|bottom|shell|facade|wall|case|housing|enclosure|roof|frame|base)/i;
const DEFAULT_COLORS = ['#0072b2', '#e69f00', '#009e73', '#cc79a7', '#d55e00', '#56b4e9', '#f0e442'];
const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

function technicalColor(id, original) {
  const column = id.match(/^(?:carrier|cam)_(\d)$/);
  if (column) return [DEFAULT_COLORS[0], DEFAULT_COLORS[1], DEFAULT_COLORS[2], DEFAULT_COLORS[3], DEFAULT_COLORS[4]][Number(column[1])];
  for (const [suffix, color] of [['center', DEFAULT_COLORS[0]], ['inner', DEFAULT_COLORS[1]], ['outer', DEFAULT_COLORS[2]]]) {
    if (id === `carrier_${suffix}` || id === `cam_${suffix}`) return color;
  }
  if (/servo_clip/.test(id)) return DEFAULT_COLORS[3];
  if (/wire/.test(id)) return DEFAULT_COLORS[4];
  if (/^(ref_servo|servo_body)$/.test(id)) return DEFAULT_COLORS[0];
  if (/gear/.test(id)) return DEFAULT_COLORS[1];
  if (/^(camshaft|horn_coupler|ref_horn|servo_horn)$/.test(id)) return '#4d4d4d';
  return original || '#bdb4a6';
}

function rgb(value) {
  const match = String(value || '').trim().match(/^#([0-9a-f]{6})$/i);
  if (!match) return [0.75, 0.72, 0.67];
  const n = Number.parseInt(match[1], 16);
  return [(n >> 16) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
}

function mul(a, b) {
  const out = new Float32Array(16);
  for (let column = 0; column < 4; column += 1) for (let row = 0; row < 4; row += 1) {
    let sum = 0;
    for (let k = 0; k < 4; k += 1) sum += a[k * 4 + row] * b[column * 4 + k];
    out[column * 4 + row] = sum;
  }
  return out;
}

function perspective(fov, aspect, near, far) {
  const q = 1 / Math.tan(fov / 2), out = new Float32Array(16);
  out[0] = q / aspect;
  out[5] = q;
  out[10] = (far + near) / (near - far);
  out[11] = -1;
  out[14] = (2 * far * near) / (near - far);
  return out;
}

function lookAt(eye, center, up) {
  const normalize = v => { const length = Math.hypot(...v) || 1; return v.map(n => n / length); };
  const subtract = (a, b) => a.map((n, index) => n - b[index]);
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const dot = (a, b) => a.reduce((sum, n, index) => sum + n * b[index], 0);
  const z = normalize(subtract(eye, center)), x = normalize(cross(up, z)), y = cross(z, x);
  return new Float32Array([x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dot(x, eye), -dot(y, eye), -dot(z, eye), 1]);
}

function createShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
  return shader;
}

function meshBounds(vertices) {
  const box = { min: [Infinity, Infinity, Infinity], max: [-Infinity, -Infinity, -Infinity] };
  vertices.forEach((value, i) => { const k = i % 3; box.min[k] = Math.min(box.min[k], value); box.max[k] = Math.max(box.max[k], value); });
  return box;
}

function createRenderer(canvas, data, state) {
  const gl = canvas.getContext('webgl2', { antialias: true, alpha: false });
  if (!gl) throw new Error('WebGL2を利用できません');
  const program = gl.createProgram();
  gl.attachShader(program, createShader(gl, gl.VERTEX_SHADER, MECHANISM_VERTEX_SHADER));
  gl.attachShader(program, createShader(gl, gl.FRAGMENT_SHADER, MECHANISM_FRAGMENT_SHADER));
  gl.bindAttribLocation(program, 0, 'aPos');
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
  gl.useProgram(program);
  const uniforms = {};
  for (const name of ['uVP', 'uM', 'uCol', 'uEye', 'uCutX', 'uCut']) uniforms[name] = gl.getUniformLocation(program, name);
  const exteriorIds = new Set(data.meta?.exterior_parts || []);
  const meshes = data.parts.map((part, partIndex) => {
    // STLの面ごとに頂点を分ける。隣り合う面の法線を平均せず幾何学の稜線を残す。
    const sourceVertices = part.mesh?.vertices || [], sourceTriangles = part.mesh?.triangles || [];
    const vertices = new Float32Array(sourceTriangles.length * 3), triangles = new Uint32Array(sourceTriangles.length);
    sourceTriangles.forEach((source, index) => {
      for (let axis = 0; axis < 3; axis += 1) vertices[index * 3 + axis] = sourceVertices[source * 3 + axis];
      triangles[index] = index;
    });
    const vao = gl.createVertexArray(); gl.bindVertexArray(vao);
    const positions = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, positions); gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
    const indices = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indices); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, triangles, gl.STATIC_DRAW);
    const exterior = part.exterior ?? (exteriorIds.size ? exteriorIds.has(part.id) : !/^(servo|ref)_/.test(part.id) && EXTERIOR_WORDS.test(part.id));
    return { ...part, vertices, vao, bounds: meshBounds(sourceVertices), count: triangles.length, exterior,
      color: rgb(technicalColor(part.id, part.color)) };
  });
  const bounds = data.parts.flatMap(part => part.mesh?.vertices || []).reduce((box, value, index) => {
    const axis = index % 3; box.min[axis] = Math.min(box.min[axis], value); box.max[axis] = Math.max(box.max[axis], value); return box;
  }, { min: [Infinity, Infinity, Infinity], max: [-Infinity, -Infinity, -Infinity] });
  const center = bounds.min.map((value, index) => (value + bounds.max[index]) / 2);
  const radius = Math.max(20, ...bounds.max.map((value, index) => value - bounds.min[index]));
  const exteriorWidth = Number(data.meta?.dimensions_mm?.[0]) || bounds.max[0] - bounds.min[0];
  const target = [...center];
  target[2] += (C1_REFERENCE_VIEW.targetZ - C1_REFERENCE_VIEW.centerZ) * exteriorWidth / C1_REFERENCE_VIEW.width;
  const cutX = data.view?.cutX ?? C1_REFERENCE_VIEW.cutX * exteriorWidth / C1_REFERENCE_VIEW.width;
  const homeDistance = C1_REFERENCE_VIEW.dist * radius / C1_REFERENCE_VIEW.width;
  const minDistance = MECHANISM_VIEW_CONTROLS.minDist * radius / C1_REFERENCE_VIEW.width;
  const maxDistance = MECHANISM_VIEW_CONTROLS.maxDist * radius / C1_REFERENCE_VIEW.width;
  const home = { az: MECHANISM_VIEW_CONTROLS.homeAz, el: MECHANISM_VIEW_CONTROLS.homeEl, dist: homeDistance };
  const camera = { ...home };
  let frameCount = 0;

  function draw() {
    const ratio = Math.min(devicePixelRatio || 1, 2), width = Math.max(1, Math.floor(canvas.clientWidth * ratio)), height = Math.max(1, Math.floor(canvas.clientHeight * ratio));
    if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
    gl.viewport(0, 0, width, height);
    const palette = themePalette(), clear = rgb(palette.paper || '#f5f0e1');
    gl.clearColor(clear[0], clear[1], clear[2], 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.enable(gl.DEPTH_TEST); gl.disable(gl.CULL_FACE);
    const pose = state.transforms ? { transforms: state.transforms } : frameAt(data.motion?.frames || [], state.servoDeg);
    const fitting = state.cameraBounds;
    const liveCenter = fitting ? fitting.min.map((n, k) => (n + fitting.max[k]) / 2) : target;
    const liveRadius = fitting ? Math.max(20, ...fitting.max.map((n, k) => n - fitting.min[k])) : radius;
    const distance = camera.dist * liveRadius / radius / Math.min(1, width / height);
    const elevation = camera.el * Math.PI / 180, azimuth = camera.az * Math.PI / 180;
    const eye = [liveCenter[0] + distance * Math.cos(elevation) * Math.cos(azimuth), liveCenter[1] + distance * Math.cos(elevation) * Math.sin(azimuth), liveCenter[2] + distance * Math.sin(elevation)];
    const viewProjection = mul(perspective(MECHANISM_VIEW_CONTROLS.fovDeg * Math.PI / 180, width / height, 5, 2000), lookAt(eye, liveCenter, [0, 0, 1]));
    const visible = [], clipped = [], matrices = {}, projected = { min: [Infinity, Infinity], max: [-Infinity, -Infinity] };
    gl.uniformMatrix4fv(uniforms.uVP, false, viewProjection);
    gl.uniform3fv(uniforms.uEye, eye);
    gl.uniform1f(uniforms.uCutX, cutX);
    for (const mesh of meshes) {
      if (state.hidden.has(mesh.id) || (state.present && !state.present.has(mesh.id))) continue;
      const modelMatrix = new Float32Array(pose.transforms?.[mesh.id] || identity4());
      const mvp = mul(viewProjection, modelMatrix);
      const clip = state.cut && mesh.exterior;
      gl.uniformMatrix4fv(uniforms.uM, false, modelMatrix); gl.uniform3fv(uniforms.uCol, mesh.color);
      gl.uniform1f(uniforms.uCut, clip ? 1 : 0);
      gl.bindVertexArray(mesh.vao); gl.drawElements(gl.TRIANGLES, mesh.count, gl.UNSIGNED_INT, 0); visible.push(mesh.id);
      if (clip) clipped.push(mesh.id);
      matrices[mesh.id] = Array.from(modelMatrix);
      for (let corner = 0; corner < 8; corner++) {
        const p = [0, 1, 2].map(k => mesh.bounds[corner & (1 << k) ? 'max' : 'min'][k]);
        const w = mvp[3]*p[0] + mvp[7]*p[1] + mvp[11]*p[2] + mvp[15];
        for (let k = 0; k < 2; k++) {
          const v = (mvp[k]*p[0] + mvp[4+k]*p[1] + mvp[8+k]*p[2] + mvp[12+k]) / w;
          projected.min[k] = Math.min(projected.min[k], v); projected.max[k] = Math.max(projected.max[k], v);
        }
      }
    }
    frameCount += 1;
    canvas.dataset.frameCount = String(frameCount);
    canvas.dataset.currentAngle = state.servoDeg.toFixed(2);
    canvas.dataset.servoDeg = state.servoDeg.toFixed(2);
    canvas.dataset.visibleParts = visible.join(',');
    canvas.dataset.clippedParts = clipped.join(',');
    canvas.dataset.cutX = String(cutX);
    canvas.dataset.camera = JSON.stringify({ az: camera.az, el: camera.el, dist: distance, fovDeg: MECHANISM_VIEW_CONTROLS.fovDeg, target: liveCenter });
    canvas.dataset.renderedMatrices = JSON.stringify(matrices);
    canvas.dataset.projectedBounds = JSON.stringify(projected);
  }

  function setCamera(name) {
    Object.assign(camera, home);
    draw();
  }
  const pointers = new Map(); let pinch = 0;
  canvas.addEventListener('pointerdown', event => { pointers.set(event.pointerId, [event.clientX, event.clientY]); canvas.setPointerCapture(event.pointerId); });
  canvas.addEventListener('pointermove', event => {
    if (!pointers.has(event.pointerId)) return;
    const previous = pointers.get(event.pointerId);
    pointers.set(event.pointerId, [event.clientX, event.clientY]);
    if (pointers.size === 1) {
      camera.az -= (event.clientX - previous[0]) * MECHANISM_VIEW_CONTROLS.dragDegPerPixel;
      camera.el = clamp(camera.el + (event.clientY - previous[1]) * MECHANISM_VIEW_CONTROLS.dragDegPerPixel, MECHANISM_VIEW_CONTROLS.minPitchDeg, MECHANISM_VIEW_CONTROLS.maxPitchDeg);
    } else if (pointers.size === 2) {
      const [a, b] = [...pointers.values()], distance = Math.hypot(a[0] - b[0], a[1] - b[1]);
      if (pinch && distance) camera.dist = clamp(camera.dist * pinch / distance, minDistance, maxDistance);
      pinch = distance;
    }
    draw();
  });
  const release = event => { pointers.delete(event.pointerId); pinch = 0; };
  canvas.addEventListener('pointerup', release);
  canvas.addEventListener('pointercancel', release);
  canvas.addEventListener('wheel', event => { event.preventDefault(); camera.dist = clamp(camera.dist * Math.exp(event.deltaY * MECHANISM_VIEW_CONTROLS.wheelFactor), minDistance, maxDistance); draw(); }, { passive: false });
  const disposeTheme = watchTheme(draw);
  const resizeObserver = new ResizeObserver(draw);
  resizeObserver.observe(canvas);
  addEventListener('pagehide', event => { if (!event.persisted) { disposeTheme(); resizeObserver.disconnect(); } });
  function fit(frames) {
    const points = [];
    for (const frame of frames) for (const mesh of meshes) {
      if (!Object.hasOwn(frame.transforms, mesh.id)) continue;
      const matrix = frame.transforms[mesh.id];
      for (let corner = 0; corner < 8; corner++) {
        const p = [0, 1, 2].map(k => mesh.bounds[corner & (1 << k) ? 'max' : 'min'][k]);
        for (let k = 0; k < 3; k++) points.push(matrix[k] * p[0] + matrix[4 + k] * p[1] + matrix[8 + k] * p[2] + matrix[12 + k]);
      }
    }
    state.cameraBounds = points.length ? meshBounds(points) : null;
    draw();
  }
  return { draw, setCamera, meshes, fit };
}

function textValue(value) {
  if (value === null || value === undefined || value === '') return '未記録';
  if (typeof value === 'boolean') return value ? '適合' : '要確認';
  if (Array.isArray(value)) return `${value.length}件`;
  if (typeof value === 'object') {
    const status = value.status ?? value.result ?? value.ok;
    return status === undefined ? `${Object.keys(value).length}項目` : textValue(status);
  }
  return String(value);
}

const REPORT_LABELS = Object.freeze({
  status: '状態', result: '結果', ok: '判定', passed: '適合', summary: '概要', notes: '注記',
  manifold: '多様体', collision: '干渉', collisions: '干渉', clearance_mm: 'クリアランス',
  dimensions_mm: '外形寸法', part_count: '部品数', printable_parts: '印刷部品', material: '材料',
  plate: 'プレート', plates: 'プレート', files: 'ファイル', warnings: '要確認', generated_at: '生成日時',
});

function reportLabel(key) {
  return REPORT_LABELS[key] || (/[^\x00-\x7f]/.test(key) ? key : `詳細 · ${key.replaceAll('_', ' ')}`);
}

function reportRows(target, report, emptyMessage) {
  const body = $(target);
  body.replaceChildren();
  const rows = Array.isArray(report) ? report : report && typeof report === 'object' ? Object.entries(report).slice(0, 12) : [];
  if (!rows.length) rows.push(['状態', emptyMessage]);
  for (const [key, value] of rows) {
    const tr = document.createElement('tr');
    const th = document.createElement('th'); th.scope = 'row'; th.textContent = reportLabel(String(key));
    const td = document.createElement('td'); td.textContent = textValue(value);
    tr.append(th, td); body.append(tr);
  }
}

function verificationSummary(report, assembly, driveReport, simulation) {
  if (!report) return null;
  const rows = [];
  const drive = drivePresentation(driveReport, simulation);
  rows.push(['形状検証の記録', (report.ok ?? report.pass) === true ? '記録した検査は適合' : '要確認']);
  rows.push(['駆動接続', drive.geometryPass ? '接続形状は適合' : '接続未成立']);
  for (const connection of drive.interfaceRows) rows.push([connection.label, connection.result]);
  rows.push(['力学計算', drive.calculationPass ? '計算内成立。実機未確認' : '接続形状が未成立のため不成立']);
  const topology = report.topology || report.stl_direct_parse;
  if (topology) {
    const parts = Object.values(topology);
    const bad = parts.filter(p => p.pass === false || p.ok === false || p.nonmanifold_edges || p.bad_edges || p.degenerate_triangles || p.duplicate_triangles);
    rows.push(['形状の検査', `${parts.length}点中 ${parts.length - bad.length}点が適合`]);
  }
  if ((report.motion?.sample_count ?? report.motion?.frames) !== undefined) rows.push(['動作の検査', `${report.motion.sample_count ?? report.motion.frames}姿勢 / ${report.motion.step_deg}°刻み`]);
  if (report.static_geometry) rows.push(['固定部品の干渉', (report.static_geometry.ok ?? report.static_geometry.pass) === true ? '記録した組み合わせは適合' : '要確認']);
  if (report.exact_scene) rows.push(['全体の干渉', (report.exact_scene.ok ?? report.exact_scene.pass) === true ? '全組み合わせの体積を確認。指定した圧入とばねの変形だけを許容' : '要確認']);
  if (report.motion?.column_max_mm) rows.push(['各列の最大上昇', report.motion.column_max_mm.map(n => `${n} mm`).join(' / ')]);
  if (report.physics?.stroke_mm) rows.push(['各環の最大上昇', report.physics.stroke_mm.map(n => `${n} mm`).join(' / ')]);
  const torque = report.torque?.required_torque_Nm ?? report.physics?.required_Nm;
  const torqueRatio = report.torque?.stall_ratio ?? report.physics?.stall_fraction;
  if (torque !== undefined) rows.push(['必要トルクの推定', `${torque} N·m`]);
  if (torqueRatio !== undefined) rows.push(['公称停動トルクに対する比', `${(torqueRatio * 100).toFixed(2)} %`]);
  if (assembly) rows.push(['組み立て', assembly.pass === true
    ? `${assembly.steps.length}工程の表示経路と逆順の分解を確認`
    : '表示経路に要確認箇所あり']);
  rows.push(['実物の動作', '未確認']);
  return rows;
}

function deliverySummary(report, pathReview) {
  if (!report) return null;
  const rows = [];
  rows.push(['スライス', report.status === 'ok' ? '記録した検査は適合' : '造形経路に要確認箇所あり']);
  if (pathReview?.status === 'accepted_with_fit_test') rows.push(['残る造形経路', '短い橋渡し等を寸法で確認。試し刷りは未実施']);
  for (const [name, plate] of Object.entries(report.plates || {})) {
    for (const [material, result] of Object.entries(plate.materials || {})) {
      rows.push([`${name === 'full' ? '全体' : '試片'} · ${material}`, `${Math.round(result.prediction_s / 60)}分 / ${Number(result.weight_g).toFixed(1)} g`]);
    }
  }
  rows.push(['プリンター', report.settings?.machine || '未記録']);
  rows.push(['積層ピッチ', `${report.settings?.overrides?.layer_height ?? '未記録'} mm`]);
  return rows;
}

function metric(label, value) {
  const wrap = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
  dt.textContent = label; dd.textContent = value; wrap.append(dt, dd); return wrap;
}

function dimensionText(meta) {
  const source = meta.dimensions_mm ?? meta.outer_dimensions_mm ?? meta.size_mm;
  if (Array.isArray(source)) return `${source.join(' × ')} mm`;
  if (source && typeof source === 'object') return `${source.width ?? source.w ?? '?'} × ${source.depth ?? source.d ?? '?'} × ${source.height ?? source.h ?? '?'} mm`;
  if (typeof source === 'string') return source;
  return model.endsWith('-c4') ? '76 × 76 mm（設計値）' : '76〜80 mm（生成値を優先）';
}

async function start() {
  $('fatal').hidden = true; $('loading').textContent = '形を読み込んでいます…';
  try {
    const response = await fetch(assetUrl, { cache: 'no-store' });
    if (!response.ok) throw new Error(`表示データを読めません（${response.status}）`);
    const data = await response.json();
    if (!Array.isArray(data.parts) || !data.parts.length) throw new Error('表示できる部品がありません');
    const frames = [...data.motion.frames].sort((a, b) => a.servo_deg - b.servo_deg);
    data.motion.frames = frames;
    const minimum = frames[0].servo_deg;
    const state = { servoDeg: minimum, cut: true, hidden: new Set(), transforms: null, present: null };
    const canvas = $('gl'), renderer = createRenderer(canvas, data, state), meta = data.meta;
    document.title = `住人の箱 ${profile.label}の${mode === 'assembly' ? '組み立て' : '物理検証'} · model-lab`;
    $('eyebrow').textContent = mode === 'assembly' ? '工具、ねじ、接着剤なし' : '接続形状を前提にした1自由度計算';
    $('pageTitle').textContent = mode === 'assembly' ? '組み立ての手順と検証' : profile.title;
    $('summary').textContent = mode === 'assembly'
      ? '表示する経路で実際のSTLを動かし、据えた部品との共通体積を測ります。実物では未検証です。'
      : '接続形状の検査を通った場合だけ、質量と慣性にサーボのトルク上限と速度の限界を入れて計算します。スプライン嵌合と材料は実機未確認です。';
    document.querySelector('.workspace-model strong').textContent = `住人の箱 ${profile.label}`;
    document.querySelector('.workspace-model small').textContent = `${dimensionText(meta)} · SG92R 1台 · 印刷 ${data.parts.filter(p => p.printable).length}点`;
    document.querySelector('.workspace-brand').href = `/?model=${model}`;
    $('cut').addEventListener('change', event => { state.cut = event.currentTarget.checked; renderer.draw(); });
    $('home').addEventListener('click', () => renderer.setCamera('iso'));
    $('legend').replaceChildren(...renderer.meshes.map(mesh => {
      const label = document.createElement('label'), input = document.createElement('input'), swatch = document.createElement('i');
      label.dataset.part = mesh.id; input.type = 'checkbox'; input.checked = true;
      swatch.style.background = `rgb(${mesh.color.map(v => Math.round(v * 255)).join(' ')})`;
      input.addEventListener('change', () => { input.checked ? state.hidden.delete(mesh.id) : state.hidden.add(mesh.id); renderer.draw(); });
      label.append(input, swatch, document.createTextNode(mesh.label || mesh.id)); return label;
    }));
    reportRows('verifyRows', verificationSummary(data.verify, data.assembly, data.drive, data.sim), '検証データなし');
    reportRows('deliveryRows', deliverySummary(data.delivery, data.print_path_review), '印刷データなし');
    const printLinks = [];
    for (const [kind, plate] of Object.entries(data.delivery?.plates || {})) {
      for (const [material, result] of Object.entries(plate.materials || {})) {
        const filename = String(result.file?.file || '').split('/').at(-1);
        if (!filename?.startsWith(`${model}-`) || !filename.endsWith('.gcode.3mf')) continue;
        const li = document.createElement('li'), link = document.createElement('a');
        link.href = `/exports/${encodeURIComponent(filename)}`; link.download = filename;
        link.textContent = `${kind === 'full' ? '全体' : '試片'} · ${material}をダウンロード`;
        li.append(link); printLinks.push(li);
      }
    }
    $('printDownloads').replaceChildren(...printLinks);
    $('verifyDownload').href = assetUrl; $('verifyDownload').download = `${model}-with-verify.json`;
    for (const id of ['prev', 'play', 'next', 'all', 'open', 'close']) $(id).disabled = false;
    if (mode === 'assembly') setupAssembly({ data, state, renderer });
    else setupPhysics({ data, state, renderer });
    $('loading').textContent = ''; renderer.draw();
  } catch (error) {
    console.error(error);
    $('loading').textContent = '読み込めませんでした'; $('fatal').hidden = false;
    $('fatalMessage').textContent = `${error.message}。表示データを更新してから読み直してください。`;
  }
}
$('retry').addEventListener('click', () => location.reload());
start();
