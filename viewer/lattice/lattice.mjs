import { createWorkspaceNav, themePalette, watchTheme } from '../shared/workspace.mjs';
import { frameAt, identity4, quintic } from './motion.mjs';

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
for (const [id, target] of [['c3Link', 'mystery-box-sg92r-c3'], ['c4Link', 'mystery-box-sg92r-c4']]) {
  const link = $(id);
  const url = new URL(location.href);
  url.searchParams.set('model', target);
  url.searchParams.set('mode', mode);
  link.href = url.pathname + url.search;
  if (target === model) link.setAttribute('aria-current', 'page');
}
$('dataDownload').href = assetUrl;
$('dataDownload').download = `${model}.json`;

const EXTERIOR_WORDS = /(?:box|body|bottom|shell|facade|wall|case|housing|enclosure|roof|frame|base)/i;
const DEFAULT_COLORS = ['#0072b2', '#e69f00', '#009e73', '#cc79a7', '#d55e00', '#56b4e9', '#f0e442'];
const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

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

function normalsFor(vertices, triangles) {
  const normals = new Float32Array(vertices.length);
  for (let index = 0; index < triangles.length; index += 3) {
    const ia = triangles[index] * 3, ib = triangles[index + 1] * 3, ic = triangles[index + 2] * 3;
    const ab = [vertices[ib] - vertices[ia], vertices[ib + 1] - vertices[ia + 1], vertices[ib + 2] - vertices[ia + 2]];
    const ac = [vertices[ic] - vertices[ia], vertices[ic + 1] - vertices[ia + 1], vertices[ic + 2] - vertices[ia + 2]];
    const n = [ab[1] * ac[2] - ab[2] * ac[1], ab[2] * ac[0] - ab[0] * ac[2], ab[0] * ac[1] - ab[1] * ac[0]];
    for (const offset of [ia, ib, ic]) for (let axis = 0; axis < 3; axis += 1) normals[offset + axis] += n[axis];
  }
  for (let index = 0; index < normals.length; index += 3) {
    const length = Math.hypot(normals[index], normals[index + 1], normals[index + 2]) || 1;
    normals[index] /= length; normals[index + 1] /= length; normals[index + 2] /= length;
  }
  return normals;
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
  gl.attachShader(program, createShader(gl, gl.VERTEX_SHADER, `#version 300 es
    in vec3 position; in vec3 normal; uniform mat4 mvp; uniform mat4 model;
    out vec3 vNormal; out vec3 vPosition;
    void main() { vec4 world = model * vec4(position, 1.0); vPosition = world.xyz; vNormal = mat3(model) * normal; gl_Position = mvp * vec4(position, 1.0); }`));
  gl.attachShader(program, createShader(gl, gl.FRAGMENT_SHADER, `#version 300 es
    precision highp float; in vec3 vNormal; in vec3 vPosition; uniform vec3 color; out vec4 outColor;
    void main() { vec3 n = normalize(vNormal); float diffuse = 0.35 + 0.65 * abs(dot(n, normalize(vec3(0.35, -0.45, 0.82))));
      float rim = pow(1.0 - abs(n.z), 3.0) * 0.12; outColor = vec4(color * diffuse + rim, 1.0); }`));
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
  gl.useProgram(program);
  const positionLoc = gl.getAttribLocation(program, 'position'), normalLoc = gl.getAttribLocation(program, 'normal');
  const mvpLoc = gl.getUniformLocation(program, 'mvp'), modelLoc = gl.getUniformLocation(program, 'model'), colorLoc = gl.getUniformLocation(program, 'color');
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
    gl.enableVertexAttribArray(positionLoc); gl.vertexAttribPointer(positionLoc, 3, gl.FLOAT, false, 0, 0);
    const normals = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, normals); gl.bufferData(gl.ARRAY_BUFFER, normalsFor(vertices, triangles), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(normalLoc); gl.vertexAttribPointer(normalLoc, 3, gl.FLOAT, false, 0, 0);
    const indices = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indices); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, triangles, gl.STATIC_DRAW);
    const exterior = part.exterior ?? (exteriorIds.size ? exteriorIds.has(part.id) : !/^(servo|ref)_/.test(part.id) && EXTERIOR_WORDS.test(part.id));
    return { ...part, vertices, vao, bounds: meshBounds(sourceVertices), count: triangles.length, exterior,
      color: rgb(part.color || (exterior ? '#d8d2c8' : DEFAULT_COLORS[partIndex % DEFAULT_COLORS.length])) };
  });
  const bounds = data.parts.flatMap(part => part.mesh?.vertices || []).reduce((box, value, index) => {
    const axis = index % 3; box.min[axis] = Math.min(box.min[axis], value); box.max[axis] = Math.max(box.max[axis], value); return box;
  }, { min: [Infinity, Infinity, Infinity], max: [-Infinity, -Infinity, -Infinity] });
  const center = bounds.min.map((value, index) => (value + bounds.max[index]) / 2);
  const radius = Math.max(20, ...bounds.max.map((value, index) => value - bounds.min[index]));
  const camera = { yaw: -0.65, pitch: 0.52, zoom: 2.4 };
  let frameCount = 0;

  function draw() {
    const ratio = Math.min(devicePixelRatio || 1, 2), width = Math.max(1, Math.floor(canvas.clientWidth * ratio)), height = Math.max(1, Math.floor(canvas.clientHeight * ratio));
    if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
    gl.viewport(0, 0, width, height);
    const palette = themePalette(), clear = rgb(palette.card || '#ece4d4');
    gl.clearColor(clear[0], clear[1], clear[2], 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.enable(gl.DEPTH_TEST); gl.enable(gl.CULL_FACE); gl.cullFace(gl.BACK);
    const pose = frameAt(data.motion?.frames || [], state.servoDeg);
    let liveCenter = center, liveRadius = radius;
    if (state.explode > 0) {
      const points = [];
      for (const mesh of meshes) {
        const matrix = pose.transforms?.[mesh.id] || identity4(), spread = mesh.explode || [0, 0, 0];
        for (let corner = 0; corner < 8; corner += 1) {
          const p = [0, 1, 2].map(k => mesh.bounds[corner & (1 << k) ? 'max' : 'min'][k]);
          for (let k = 0; k < 3; k += 1) points.push(matrix[k] * p[0] + matrix[4 + k] * p[1] + matrix[8 + k] * p[2] + matrix[12 + k] + (Number(spread[k]) || 0) * state.explode);
        }
      }
      const expanded = meshBounds(points);
      liveCenter = expanded.min.map((n, k) => (n + expanded.max[k]) / 2);
      liveRadius = Math.max(20, ...expanded.max.map((n, k) => n - expanded.min[k]));
    }
    const distance = liveRadius * camera.zoom;
    const eye = [liveCenter[0] + distance * Math.cos(camera.pitch) * Math.sin(camera.yaw), liveCenter[1] - distance * Math.cos(camera.pitch) * Math.cos(camera.yaw), liveCenter[2] + distance * Math.sin(camera.pitch)];
    const viewProjection = mul(perspective(Math.PI / 4, width / height, Math.max(0.1, liveRadius / 100), liveRadius * 20), lookAt(eye, liveCenter, [0, 0, 1]));
    const visible = [];
    for (const mesh of meshes) {
      if (state.hidden.has(mesh.id) || (state.removeExterior && mesh.exterior)) continue;
      const modelMatrix = new Float32Array(pose.transforms?.[mesh.id] || identity4());
      const explode = mesh.explode || [0, 0, 0];
      for (let axis = 0; axis < 3; axis += 1) modelMatrix[12 + axis] += (Number(explode[axis]) || 0) * state.explode;
      gl.uniformMatrix4fv(modelLoc, false, modelMatrix); gl.uniformMatrix4fv(mvpLoc, false, mul(viewProjection, modelMatrix)); gl.uniform3fv(colorLoc, mesh.color);
      gl.bindVertexArray(mesh.vao); gl.drawElements(gl.TRIANGLES, mesh.count, gl.UNSIGNED_INT, 0); visible.push(mesh.id);
    }
    frameCount += 1;
    canvas.dataset.frameCount = String(frameCount);
    canvas.dataset.currentAngle = state.servoDeg.toFixed(2);
    canvas.dataset.servoDeg = state.servoDeg.toFixed(2);
    canvas.dataset.visibleParts = visible.join(',');
  }

  function setCamera(name) {
    if (name === 'front') Object.assign(camera, { yaw: 0, pitch: 0.08, zoom: 2.4 });
    else if (name === 'top') Object.assign(camera, { yaw: 0, pitch: 1.48, zoom: 2.5 });
    else Object.assign(camera, { yaw: -0.65, pitch: 0.52, zoom: 2.4 });
    draw();
  }
  let drag = null;
  canvas.addEventListener('pointerdown', event => { drag = [event.clientX, event.clientY]; canvas.setPointerCapture(event.pointerId); });
  canvas.addEventListener('pointermove', event => {
    if (!drag) return;
    camera.yaw += (event.clientX - drag[0]) * 0.01;
    camera.pitch = clamp(camera.pitch + (event.clientY - drag[1]) * 0.01, -1.45, 1.5);
    drag = [event.clientX, event.clientY]; draw();
  });
  canvas.addEventListener('pointerup', () => { drag = null; });
  canvas.addEventListener('pointercancel', () => { drag = null; });
  canvas.addEventListener('wheel', event => { event.preventDefault(); camera.zoom = clamp(camera.zoom * Math.exp(event.deltaY * 0.001), 1.2, 7); draw(); }, { passive: false });
  const disposeTheme = watchTheme(draw);
  addEventListener('resize', draw);
  addEventListener('pagehide', event => { if (!event.persisted) disposeTheme(); });
  return { draw, setCamera, meshes };
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

function verificationSummary(report) {
  if (!report) return null;
  const rows = [];
  rows.push(['計算上の判定', (report.ok ?? report.pass) === true ? '記録した検査は適合' : '要確認']);
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
  if (report.assembly) rows.push(['組み立て', (report.assembly.ok ?? report.assembly.pass) === true ? '記録した経路を確認' : '実物での確認が必要']);
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
  $('fatal').hidden = true; $('loading').hidden = false; $('loading').textContent = '形を読み込んでいます…';
  try {
    const response = await fetch(assetUrl, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${assetUrl}を読めません（${response.status}）`);
    const data = await response.json();
    if (!Array.isArray(data.parts) || !data.parts.length) throw new Error('表示できる部品がありません');
    const frames = [...(data.motion?.frames || [])].sort((a, b) => a.servo_deg - b.servo_deg);
    data.motion = { ...(data.motion || {}), frames };
    const minimum = frames[0]?.servo_deg ?? 0, maximum = frames.at(-1)?.servo_deg ?? 180;
    const home = clamp(Number(data.motion?.home_servo_deg ?? minimum), minimum, maximum);
    const state = { servoDeg: home, explode: 0, removeExterior: false, hidden: new Set() };
    const canvas = $('gl'), renderer = createRenderer(canvas, data, state);
    const meta = data.meta || {};
    document.title = `${profile.title}の${mode === 'assembly' ? '組み立て' : '物理検証'} · model-lab`;
    $('pageTitle').textContent = profile.title;
    $('summary').textContent = meta.summary || (mode === 'assembly' ? '実際の印刷部品を分解し、部品ごとの位置と組み立て順を確かめます。' : profile.pattern);
    $('principle').textContent = meta.motion_principle || profile.pattern;
    document.querySelector('.workspace-model strong').textContent = `${profile.label} ${profile.title}`;
    document.querySelector('.workspace-model small').textContent = mode === 'assembly' ? '部品と組み立て方' : '格子が持ち上がる動き';
    $('metrics').replaceChildren(
      metric('外形', dimensionText(meta)),
      metric('印刷部品', `${data.parts.filter(part => part.printable).length}点`),
      metric('可動範囲', `${minimum}〜${maximum}°`),
      metric('片道', `${Number(data.motion?.duration_s ?? 1.5).toFixed(1)}秒`),
    );

    const angle = $('angle'); angle.min = String(minimum); angle.max = String(maximum); angle.value = String(home);
    const setAngle = value => { state.servoDeg = clamp(Number(value), minimum, maximum); angle.value = String(state.servoDeg); $('angleValue').value = `${state.servoDeg.toFixed(state.servoDeg % 1 ? 1 : 0)}°`; renderer.draw(); };
    setAngle(home);
    angle.addEventListener('input', () => { stopAnimation(); setAngle(angle.value); });
    $('removeExterior').addEventListener('change', event => { state.removeExterior = event.currentTarget.checked; renderer.draw(); });
    $('explode').addEventListener('input', event => { state.explode = Number(event.currentTarget.value) / 100; $('explodeValue').value = `${event.currentTarget.value}%`; renderer.draw(); });
    for (const button of document.querySelectorAll('[data-camera]')) button.addEventListener('click', () => {
      document.querySelectorAll('[data-camera]').forEach(peer => peer.setAttribute('aria-pressed', String(peer === button)));
      renderer.setCamera(button.dataset.camera);
    });

    let animation = 0;
    function stopAnimation() { cancelAnimationFrame(animation); animation = 0; $('stop').disabled = true; }
    $('stop').addEventListener('click', stopAnimation);
    $('play').addEventListener('click', () => {
      stopAnimation();
      const from = state.servoDeg;
      const target = Math.abs(from - minimum) < Math.abs(from - maximum) ? maximum : minimum;
      if (matchMedia('(prefers-reduced-motion: reduce)').matches) { setAngle(target); return; }
      $('stop').disabled = false;
      const duration = Math.max(0.1, Number(data.motion?.duration_s ?? 1.5)) * 1000, started = performance.now();
      const tick = now => {
        const progress = clamp((now - started) / duration, 0, 1);
        setAngle(from + (target - from) * quintic(progress));
        if (progress < 1) animation = requestAnimationFrame(tick); else { animation = 0; $('stop').disabled = true; }
      };
      animation = requestAnimationFrame(tick);
    });
    $('legend').replaceChildren(...renderer.meshes.map(mesh => {
      const item = document.createElement('span'), swatch = document.createElement('i'); swatch.style.background = `rgb(${mesh.color.map(v => Math.round(v * 255)).join(' ')})`;
      item.append(swatch, document.createTextNode(mesh.label || mesh.id)); return item;
    }));
    $('partList').replaceChildren(...renderer.meshes.map(mesh => {
      const label = document.createElement('label'), input = document.createElement('input'), swatch = document.createElement('i');
      input.type = 'checkbox'; input.checked = true; swatch.className = 'part-color'; swatch.style.background = `rgb(${mesh.color.map(v => Math.round(v * 255)).join(' ')})`;
      input.addEventListener('change', () => { input.checked ? state.hidden.delete(mesh.id) : state.hidden.add(mesh.id); renderer.draw(); });
      label.append(input, swatch, document.createTextNode(mesh.label || mesh.id)); return label;
    }));
    const steps = Array.isArray(meta.assembly_steps) ? meta.assembly_steps : [];
    $('assemblySteps').replaceChildren(...(steps.length ? steps : ['組み立て手順はまだ登録されていません。']).map(step => {
      const li = document.createElement('li');
      li.textContent = (typeof step === 'string' ? step : step.text || step.label || '未登録')
        .replaceAll('列キャリア', '格子列').replaceAll('片道2秒のquintic補間で', '始めと終わりをゆっくり動かしながら片道2秒で');
      return li;
    }));
    reportRows('verifyRows', verificationSummary(data.verify), '検証データの生成待ち');
    reportRows('deliveryRows', deliverySummary(data.delivery, data.print_path_review), '印刷データの検証待ち');
    const printLinks = [];
    for (const [kind, plate] of Object.entries(data.delivery?.plates || {})) {
      for (const [material, result] of Object.entries(plate.materials || {})) {
        const filename = String(result.file?.file || '').split('/').at(-1);
        if (!filename?.startsWith(`${model}-`) || !filename.endsWith('.gcode.3mf')) continue;
        const li = document.createElement('li'), link = document.createElement('a');
        link.href = `/exports/${encodeURIComponent(filename)}`;
        link.download = filename;
        link.textContent = `${kind === 'full' ? '全体' : '試片'} · ${material}をダウンロード`;
        li.append(link); printLinks.push(li);
      }
    }
    $('printDownloads').replaceChildren(...printLinks);
    if (data.verify) { $('verifyDownload').hidden = false; $('verifyDownload').href = assetUrl; $('verifyDownload').download = `${model}-with-verify.json`; }
    $('loading').hidden = true; renderer.draw();
  } catch (error) {
    console.error(error);
    $('loading').hidden = true; $('fatal').hidden = false;
    $('fatalMessage').textContent = `${error.message}。モデルをビルドして tools/lattice_web.py を実行後、読み直してください。`;
  }
}

$('retry').addEventListener('click', start);
start();
