const http = require("http");
const net = require("net");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { spawn, execFile } = require("child_process");
const { WebSocketServer } = require("ws");

// 待ち受けは 127.0.0.1 だけ。依頼で models/ の編集とビルドまで頼めるので、LAN には出さない
const HOST = "127.0.0.1";
const HTTP_PORT_START = 3000;
const WS_PORT_START = 3001;
const ROOT = __dirname;
const EXPORTS_DIR = path.join(ROOT, "exports");
const MODELS_DIR = path.join(ROOT, "models");
const VIEWER_DIR = path.join(ROOT, "viewer");
const STUDIO_DIR = path.join(VIEWER_DIR, "studio");
const PREVIEW_DIR = path.join(VIEWER_DIR, "preview");
const REQUESTS_DIR = path.join(ROOT, "requests");
const LISTENER_FILE = path.join(REQUESTS_DIR, ".listener.json");
const STUDIO_JSON = path.join(ROOT, ".studio.json");
const BLENDER = process.env.BLENDER ||
  "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe";

const MAX_BODY = 80 * 1024 * 1024;
const LISTENER_FRESH_MS = 30 * 1000;
const MODEL_RE = /^[\w.-]+$/;
const REQUEST_ID_RE = /^\d{8}-\d{6}-[0-9a-f]{4}$/;
const IMAGE_NAME_RE = /^[\w.-]+\.(png|svg)$/;
const PNG_PREFIX = "data:image/png;base64,";
const PLACED_NAME_RE = /print|plate|split/i;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".mjs": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".jsonl": "application/x-ndjson; charset=utf-8",
  ".svg": "image/svg+xml",
  ".stl": "application/octet-stream",
  ".glb": "model/gltf-binary",
  ".png": "image/png",
};

class HttpError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}

function findFreePort(start) {
  return new Promise((resolve, reject) => {
    const tryPort = (p) => {
      const tester = net.createServer()
        .once("error", (err) => {
          if (err.code === "EADDRINUSE" && p < start + 100) tryPort(p + 1);
          else reject(err);
        })
        .once("listening", () => tester.close(() => resolve(p)))
        .listen(p, HOST);
    };
    tryPort(start);
  });
}

// --- 時刻 -------------------------------------------------------------------
function pad(n, w = 2) { return String(n).padStart(w, "0"); }

// ローカル時刻の ISO（+09:00 付き、秒精度）
function isoLocal(d) {
  const off = -d.getTimezoneOffset();
  const sign = off >= 0 ? "+" : "-";
  const a = Math.abs(off);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
    `T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}` +
    `${sign}${pad(Math.floor(a / 60))}:${pad(a % 60)}`;
}

function makeRequestId(d) {
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-` +
    `${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}-` +
    crypto.randomBytes(2).toString("hex");
}

// --- モデル名 ---------------------------------------------------------------
function validModel(name) {
  if (typeof name !== "string" || !MODEL_RE.test(name) || /^\.+$/.test(name)) return false;
  try { return fs.statSync(path.join(MODELS_DIR, name)).isDirectory(); } catch { return false; }
}

// --- params.py を解析してスカラー / 2要素タプルのパラメータを抽出 -------------
function parseParams(modelName) {
  const file = path.join(MODELS_DIR, modelName, "params.py");
  if (!fs.existsSync(file)) return [];
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
  const controls = [];
  const numScalar = /^([A-Z][A-Z0-9_]*)\s*=\s*(-?\d+(?:\.\d+)?(?:[eE]-?\d+)?)\s*(?:#\s*(.*))?$/;
  const numTuple = /^([A-Z][A-Z0-9_]*)\s*=\s*\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)\s*(?:#\s*(.*))?$/;
  for (const raw of lines) {
    const line = raw.trim();
    let m;
    if ((m = line.match(numTuple))) {
      const [, name, a, b, label] = m;
      controls.push({ name, index: 0, value: parseFloat(a), isInt: !a.includes("."), label: (label || name).trim() });
      controls.push({ name, index: 1, value: parseFloat(b), isInt: !b.includes("."), label: (label || name).trim() });
    } else if ((m = line.match(numScalar))) {
      const [, name, val, label] = m;
      controls.push({ name, value: parseFloat(val), isInt: !val.includes("."), label: (label || name).trim() });
    }
  }
  return controls;
}

// parseParams の結果を {名前: 値} に。タプルは配列
function paramValues(modelName) {
  const values = {};
  for (const c of parseParams(modelName)) {
    if (c.index === undefined) values[c.name] = c.value;
    else (values[c.name] ||= [])[c.index] = c.value;
  }
  return values;
}

function listModels() {
  if (!fs.existsSync(MODELS_DIR)) return [];
  return fs.readdirSync(MODELS_DIR)
    .filter((d) => {
      const p = path.join(MODELS_DIR, d);
      return fs.statSync(p).isDirectory() &&
        fs.existsSync(path.join(p, "params.py")) &&
        fs.existsSync(path.join(p, "model.py"));
    })
    .sort();
}

function hasPreview(modelName) {
  if (!validModel(modelName)) return false;
  return fs.existsSync(path.join(PREVIEW_DIR, modelName + ".js"));
}

// params.py 内の `# CATEGORY: 名前` コメントを読む。無ければ "その他"
function readCategory(modelName) {
  try {
    const txt = fs.readFileSync(path.join(MODELS_DIR, modelName, "params.py"), "utf8");
    const m = txt.match(/#\s*CATEGORY:\s*(.+)/);
    if (m) return m[1].trim();
  } catch { /* noop */ }
  return "その他";
}

// models/<name>/viewer.json（カメラ・材質など）。無ければ null
function readViewerConfig(modelName) {
  if (!validModel(modelName)) return null;
  try {
    return JSON.parse(fs.readFileSync(path.join(MODELS_DIR, modelName, "viewer.json"), "utf8"));
  } catch { return null; }
}

// --- リクエスト本文 ---------------------------------------------------------
function readRaw(req, limit = MAX_BODY) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    let tooBig = false;
    req.on("data", (c) => {
      if (tooBig) return;
      size += c.length;
      if (size > limit) { tooBig = true; chunks.length = 0; return; }
      chunks.push(c);
    });
    req.on("end", () => {
      if (tooBig) reject(new HttpError(413, "本文が大きすぎます"));
      else resolve(Buffer.concat(chunks));
    });
    req.on("error", reject);
  });
}

async function readJSON(req) {
  const type = String(req.headers["content-type"] || "").toLowerCase();
  if (!type.startsWith("application/json")) {
    throw new HttpError(415, "Content-Type は application/json にしてください");
  }
  const raw = await readRaw(req);
  let data;
  try { data = JSON.parse(raw.toString("utf8") || "{}"); }
  catch { throw new HttpError(400, "JSON を読めません"); }
  if (!data || typeof data !== "object" || Array.isArray(data)) throw new HttpError(400, "JSON はオブジェクトにしてください");
  return data;
}

// --- Blender でモデルをビルド（params 上書き付き）---------------------------
function buildModel(modelName, params) {
  return new Promise((resolve) => {
    const dir = path.join(MODELS_DIR, modelName);
    const modelPy = path.join(dir, "model.py");
    if (!fs.existsSync(modelPy)) return resolve({ ok: false, error: "model.py not found" });
    const overridePath = path.join(dir, "_overrides.json");
    fs.writeFileSync(overridePath, JSON.stringify(params || {}, null, 2), "utf8");

    const proc = spawn(BLENDER, ["--background", "--python", modelPy], {
      env: { ...process.env, MODEL_PARAMS_JSON: overridePath },
    });
    let log = "";
    proc.stdout.on("data", (d) => (log += d));
    proc.stderr.on("data", (d) => (log += d));
    proc.on("close", (code) => {
      resolve({ ok: code === 0, code, log: log.slice(-2000) });
    });
    proc.on("error", (e) => resolve({ ok: false, error: String(e) }));
  });
}

// --- exports/ ---------------------------------------------------------------
function listStls() {
  if (!fs.existsSync(EXPORTS_DIR)) return [];
  const out = [];
  for (const name of fs.readdirSync(EXPORTS_DIR)) {
    if (!name.toLowerCase().endsWith(".stl")) continue;
    try {
      const st = fs.statSync(path.join(EXPORTS_DIR, name));
      if (st.isFile()) out.push({ name, mtime: Math.round(st.mtimeMs), size: st.size });
    } catch { /* 消えた */ }
  }
  return out.sort((a, b) => b.mtime - a.mtime);
}

function exportsStlPath(file) {
  if (typeof file !== "string" || !file || path.basename(file) !== file) return null;
  if (!file.toLowerCase().endsWith(".stl")) return null;
  const full = path.resolve(EXPORTS_DIR, file);
  if (path.dirname(full) !== path.resolve(EXPORTS_DIR)) return null;
  return full;
}

function sha1File(file) {
  return new Promise((resolve, reject) => {
    const h = crypto.createHash("sha1");
    fs.createReadStream(file)
      .on("data", (c) => h.update(c))
      .on("end", () => resolve(h.digest("hex")))
      .on("error", reject);
  });
}

function gitShortHead() {
  return new Promise((resolve) => {
    execFile("git", ["rev-parse", "--short", "HEAD"], { cwd: ROOT, windowsHide: true, timeout: 5000 }, (err, stdout) => {
      resolve(err ? null : String(stdout).trim() || null);
    });
  });
}

// --- 依頼（requests/<model>/<id>/）------------------------------------------
function enc(s) { return encodeURIComponent(s); }

function appendJSONL(file, obj) {
  let prefix = "";
  try {
    const fd = fs.openSync(file, "r");
    try {
      const size = fs.fstatSync(fd).size;
      if (size > 0) {
        const buf = Buffer.alloc(1);
        fs.readSync(fd, buf, 0, 1, size - 1);
        if (buf[0] !== 0x0a) prefix = "\n";
      }
    } finally { fs.closeSync(fd); }
  } catch { /* まだ無い */ }
  fs.appendFileSync(file, prefix + JSON.stringify(obj) + "\n", "utf8");
}

function readThread(file) {
  let txt;
  try { txt = fs.readFileSync(file, "utf8"); } catch { return []; }
  const out = [];
  for (const line of txt.split(/\r?\n/)) {
    if (!line.trim()) continue;
    try { out.push(JSON.parse(line)); } catch { /* 書きかけの行は飛ばす */ }
  }
  return out;
}

// クライアントが送った STL の手がかり（provenance.stl / files / items の file）を file 名ごとにまとめる
function collectClientStl(request) {
  const map = new Map();
  const add = (e) => {
    if (typeof e === "string") e = { file: e };
    if (!e || typeof e !== "object") return;
    const file = e.file ?? e.name;
    if (typeof file !== "string" || !file) return;
    if (!map.has(file)) map.set(file, { ...e, file });
  };
  const prov = request.provenance;
  if (prov && Array.isArray(prov.stl)) prov.stl.forEach(add);
  if (Array.isArray(request.files)) request.files.forEach(add);
  if (Array.isArray(request.items)) {
    for (const it of request.items) if (it && typeof it.file === "string") add(it.file);
  }
  return map;
}

async function buildProvenance(model, request) {
  const gitHead = await gitShortHead();
  const stl = [];
  let newestStl = 0;
  for (const [file, client] of collectClientStl(request)) {
    const full = exportsStlPath(file);
    if (!full) continue;   // exports/ の STL ではない名前は載せない
    let st = null;
    try { st = fs.statSync(full); } catch { /* 無い */ }
    if (!st || !st.isFile()) { stl.push({ ...client, file, missing: true }); continue; }
    newestStl = Math.max(newestStl, st.mtimeMs);
    stl.push({
      ...client,
      file,
      mtime: isoLocal(st.mtime),
      size: st.size,
      sha1: await sha1File(full),
      unitScale: client.unitScale ?? null,
      bbox: client.bbox ?? null,
      placed: typeof client.placed === "boolean" ? client.placed : PLACED_NAME_RE.test(file),
    });
  }

  // Studio の「STL 生成」は _overrides.json を書いてから Blender を走らせるので、STL の方が数秒〜数分新しい。
  // その間隔で書かれた STL は overrides 込みで作られたとみなす（./run.sh のビルドは overrides を読まない）
  let overrides = null;
  try {
    const ovPath = path.join(MODELS_DIR, model, "_overrides.json");
    const ovStat = fs.statSync(ovPath);
    const values = JSON.parse(fs.readFileSync(ovPath, "utf8"));
    const lag = newestStl - ovStat.mtimeMs;
    overrides = {
      values,
      writtenAt: new Date(ovStat.mtimeMs).toISOString(),
      appliedToStl: newestStl > 0 && lag >= 0 && lag < 10 * 60 * 1000,
    };
  } catch { /* 無い・壊れている */ }

  return {
    gitHead,
    stl,
    params: { source: "params.py", values: paramValues(model) },
    overrides,
  };
}

// 画像の検証とデコード。1 つでも不正なら依頼ごと拒否する
function prepareImages(images) {
  if (images == null) return [];
  if (typeof images !== "object" || Array.isArray(images)) throw new HttpError(400, "images はオブジェクトにしてください");
  const out = [];
  for (const [name, val] of Object.entries(images)) {
    const m = name.match(IMAGE_NAME_RE);
    if (!m) throw new HttpError(400, `画像名が不正です: ${name}`);
    if (typeof val !== "string") throw new HttpError(400, `画像の中身が文字列ではありません: ${name}`);
    if (m[1] === "png") {
      if (!val.startsWith(PNG_PREFIX)) throw new HttpError(400, `png は dataURL にしてください: ${name}`);
      const buf = Buffer.from(val.slice(PNG_PREFIX.length), "base64");
      if (buf.length < 8 || buf.readUInt32BE(0) !== 0x89504e47) throw new HttpError(400, `png として読めません: ${name}`);
      out.push({ name, data: buf });
    } else {
      out.push({ name, data: Buffer.from(val, "utf8") });
    }
  }
  return out;
}

async function createRequest(body) {
  const { model, request, images } = body;
  if (!validModel(model)) throw new HttpError(400, "model が不正です");
  if (!request || typeof request !== "object" || Array.isArray(request)) throw new HttpError(400, "request はオブジェクトにしてください");
  const prepared = prepareImages(images);

  const now = new Date();
  const modelDir = path.join(REQUESTS_DIR, model);
  fs.mkdirSync(modelDir, { recursive: true });
  let id;
  do { id = makeRequestId(now); } while (fs.existsSync(path.join(modelDir, id)));

  // 作りかけを watcher と一覧に見せないため、ドット始まりの一時ディレクトリで組んでから改名する
  const tmpDir = path.join(modelDir, `.${id}.tmp`);
  const finalDir = path.join(modelDir, id);
  fs.mkdirSync(tmpDir);
  try {
    const provenance = await buildProvenance(model, request);
    for (const img of prepared) fs.writeFileSync(path.join(tmpDir, img.name), img.data);

    const beforeDir = path.join(tmpDir, "before");
    fs.mkdirSync(beforeDir);
    for (const s of provenance.stl) {
      if (s.missing) continue;
      await fs.promises.copyFile(path.join(EXPORTS_DIR, s.file), path.join(beforeDir, s.file));
    }

    const { id: _i, model: _m, createdAt: _c, provenance: _p, message, frame, ...rest } = request;
    const record = {
      id, model, createdAt: isoLocal(now),
      message: typeof message === "string" ? message : "",
      frame: typeof frame === "string" ? frame : "blender-mm",
      provenance,
      ...rest,
      images: prepared.map((i) => i.name),
    };
    fs.writeFileSync(path.join(tmpDir, "request.json"), JSON.stringify(record, null, 2) + "\n", "utf8");
    appendJSONL(path.join(tmpDir, "thread.jsonl"), { at: isoLocal(now), from: "user", kind: "status", status: "open" });
    fs.renameSync(tmpDir, finalDir);
  } catch (e) {
    fs.rmSync(tmpDir, { recursive: true, force: true });
    throw e;
  }
  return id;
}

function loadRequest(model, id) {
  const dir = path.join(REQUESTS_DIR, model, id);
  let req;
  try { req = JSON.parse(fs.readFileSync(path.join(dir, "request.json"), "utf8")); } catch { return null; }
  const thread = readThread(path.join(dir, "thread.jsonl"));

  let status = "open";
  let claimedBy = null;
  for (const line of thread) {
    if (line.kind === "status" && line.status) status = line.status;
    if (line.claim) claimedBy = line.claim;
  }

  const items = Array.isArray(req.items) ? req.items : [];
  const base = `/requests/${enc(model)}/${enc(id)}`;

  let imageNames = [];
  try { imageNames = fs.readdirSync(dir).filter((n) => /\.(png|svg)$/i.test(n)); } catch { /* noop */ }
  const order = Array.isArray(req.images) ? req.images : [];
  imageNames.sort((a, b) => {
    const ia = order.indexOf(a), ib = order.indexOf(b);
    if (ia !== ib) return (ia < 0 ? 1e9 : ia) - (ib < 0 ? 1e9 : ib);
    return a < b ? -1 : a > b ? 1 : 0;
  });

  let before = [];
  try {
    before = fs.readdirSync(path.join(dir, "before"))
      .filter((n) => n.toLowerCase().endsWith(".stl"))
      .sort()
      .map((file) => ({ file, url: `${base}/before/${enc(file)}` }));
  } catch { /* noop */ }

  return {
    id, model,
    createdAt: req.createdAt ?? null,
    message: typeof req.message === "string" ? req.message : "",
    itemCount: items.length,
    items: items.map((it) => ({ type: it && it.type, action: it && it.action, note: (it && it.note) || "" })),
    status, claimedBy, thread,
    images: imageNames.map((n) => `${base}/${enc(n)}`),
    before,
  };
}

function requestModelDirs() {
  try {
    return fs.readdirSync(REQUESTS_DIR, { withFileTypes: true })
      .filter((d) => d.isDirectory() && !d.name.startsWith(".") && MODEL_RE.test(d.name))
      .map((d) => d.name);
  } catch { return []; }
}

function listRequests(modelFilter) {
  const models = modelFilter ? [modelFilter] : requestModelDirs();
  const out = [];
  for (const model of models) {
    let ids = [];
    try { ids = fs.readdirSync(path.join(REQUESTS_DIR, model)).filter((n) => REQUEST_ID_RE.test(n)); } catch { continue; }
    for (const id of ids) {
      const r = loadRequest(model, id);
      if (r) out.push(r);
    }
  }
  return out.sort((a, b) => (a.id < b.id ? 1 : a.id > b.id ? -1 : 0));
}

// id から依頼ディレクトリを全モデルから探す
function findRequestDir(id) {
  if (!REQUEST_ID_RE.test(id)) return null;
  for (const model of requestModelDirs()) {
    const dir = path.join(REQUESTS_DIR, model, id);
    try { if (fs.statSync(dir).isDirectory()) return dir; } catch { /* 次へ */ }
  }
  return null;
}

function readListener() {
  try {
    const j = JSON.parse(fs.readFileSync(LISTENER_FILE, "utf8"));
    const t = Date.parse(j.at);
    return {
      listening: Number.isFinite(t) && Date.now() - t <= LISTENER_FRESH_MS,
      agent: j.agent ?? null,
      at: j.at ?? null,
    };
  } catch { return { listening: false }; }
}

// --- 静的配信 ---------------------------------------------------------------
function safeJoin(base, sub) {
  const root = path.resolve(base);
  const full = path.resolve(root, sub);
  if (full !== root && !full.startsWith(root + path.sep)) return null;
  return full;
}

// 戻り値: { file, legacy } | null
function resolveStatic(pathname) {
  let rel;
  try { rel = decodeURIComponent(pathname); } catch { return null; }
  if (rel.includes("\0")) return null;
  if (rel === "/" || rel === "/index.html") return { file: path.join(STUDIO_DIR, "index.html"), legacy: false };
  if (rel === "/legacy" || rel === "/legacy/") return { file: path.join(VIEWER_DIR, "index.html"), legacy: true };
  const table = [
    ["/exports/", EXPORTS_DIR],
    ["/requests/", REQUESTS_DIR],
    ["/preview/", PREVIEW_DIR],
    ["/viewer/", VIEWER_DIR],   // /viewer/studio/* もここ
  ];
  for (const [prefix, base] of table) {
    if (rel.startsWith(prefix)) {
      const file = safeJoin(base, rel.slice(prefix.length));
      return file ? { file, legacy: false } : null;
    }
  }
  return null;
}

async function main() {
  const HTTP_PORT = await findFreePort(HTTP_PORT_START);
  const WS_PORT = await findFreePort(Math.max(WS_PORT_START, HTTP_PORT + 1));

  const ALLOWED_ORIGINS = new Set([`http://localhost:${HTTP_PORT}`, `http://127.0.0.1:${HTTP_PORT}`]);
  const ALLOWED_HOSTS = new Set([`localhost:${HTTP_PORT}`, `127.0.0.1:${HTTP_PORT}`]);
  // Origin が無いのは curl 等のローカル呼び出し。付いているなら自分のページのものだけ通す
  const originOk = (origin) => origin === undefined || origin === "" ? true : ALLOWED_ORIGINS.has(origin);

  function sendJSON(res, obj, status = 200) {
    res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify(obj));
  }

  function serveFile(req, res, { file, legacy }) {
    fs.stat(file, (err, st) => {
      if (err || !st.isFile()) { res.writeHead(404); return res.end("Not found"); }
      const ext = path.extname(file).toLowerCase();
      const type = MIME[ext] || "application/octet-stream";
      if (ext === ".html") {
        fs.readFile(file, (e2, data) => {
          if (e2) { res.writeHead(404); return res.end("Not found"); }
          // 旧版は WS を ?client=legacy 付きで繋がせる（requests / listener の通知を旧版に流さないため）
          const html = data.toString("utf8")
            .replace(/ws:\/\/localhost:\d+/g, `ws://${HOST}:${WS_PORT}${legacy ? "/?client=legacy" : ""}`);
          res.writeHead(200, { "Content-Type": type, "Cache-Control": "no-cache" });
          res.end(req.method === "HEAD" ? undefined : html);
        });
        return;
      }
      res.writeHead(200, { "Content-Type": type, "Content-Length": st.size, "Cache-Control": "no-cache" });
      if (req.method === "HEAD") return res.end();
      fs.createReadStream(file).on("error", () => res.destroy()).pipe(res);
    });
  }

  async function handle(req, res) {
    const host = req.headers.host;
    if (host && !ALLOWED_HOSTS.has(host)) throw new HttpError(403, "host が違います");
    let url;
    try { url = new URL(req.url, `http://localhost:${HTTP_PORT}`); }
    catch { throw new HttpError(400, "URL が不正です"); }
    const p = url.pathname;

    if (req.method === "POST" && !originOk(req.headers.origin)) throw new HttpError(403, "Origin が許可されていません");

    // --- API ---
    if (p.startsWith("/api/")) {
      if (p === "/api/models") {
        const models = listModels().map((m) => ({ name: m, preview: hasPreview(m), category: readCategory(m) }));
        return sendJSON(res, { models });
      }
      if (p === "/api/config") return sendJSON(res, { http: HTTP_PORT, ws: WS_PORT });
      if (p === "/api/params") {
        const model = url.searchParams.get("model");
        const ok = validModel(model);
        return sendJSON(res, {
          model,
          controls: ok ? parseParams(model) : [],
          preview: ok && hasPreview(model),
          viewer: ok ? readViewerConfig(model) : null,
        });
      }
      if (p === "/api/stls") return sendJSON(res, listStls());
      if (p === "/api/export" && req.method === "POST") {
        const body = await readJSON(req);
        if (!validModel(body.model)) throw new HttpError(400, "model が不正です");
        return sendJSON(res, await buildModel(body.model, body.params));
      }
      if (p === "/api/shot" && req.method === "POST") {
        const data = (await readRaw(req)).toString("utf8");
        const b64 = data.replace(/^data:image\/png;base64,/, "");
        const outDir = path.join(EXPORTS_DIR, "deep-sea");
        fs.mkdirSync(outDir, { recursive: true });
        const out = path.join(outDir, "_browser_shot.png");
        fs.writeFileSync(out, Buffer.from(b64, "base64"));
        return sendJSON(res, { ok: true, bytes: fs.statSync(out).size });
      }
      if (p === "/api/listener") return sendJSON(res, readListener());
      if (p === "/api/requests") {
        if (req.method === "POST") {
          const id = await createRequest(await readJSON(req));
          return sendJSON(res, { ok: true, id });
        }
        const model = url.searchParams.get("model");
        if (model && !validModel(model)) return sendJSON(res, []);
        return sendJSON(res, listRequests(model || null));
      }
      const sub = p.match(/^\/api\/requests\/([^/]+)\/(messages|status)$/);
      if (sub && req.method === "POST") {
        const dir = findRequestDir(sub[1]);
        if (!dir) throw new HttpError(404, "依頼が見つかりません");
        const body = await readJSON(req);
        const at = isoLocal(new Date());
        let line;
        if (sub[2] === "messages") {
          const text = typeof body.text === "string" ? body.text.trim() : "";
          if (!text) throw new HttpError(400, "text が空です");
          if (text.length > 20000) throw new HttpError(400, "text が長すぎます");
          line = { at, from: "user", kind: "message", text };
        } else {
          if (body.status !== "open" && body.status !== "closed") throw new HttpError(400, "status は open か closed です");
          line = { at, from: "user", kind: "status", status: body.status };
        }
        appendJSONL(path.join(dir, "thread.jsonl"), line);
        return sendJSON(res, { ok: true, line });
      }
      throw new HttpError(404, "API が見つかりません");
    }

    // --- static ---
    if (req.method !== "GET" && req.method !== "HEAD") throw new HttpError(405, "GET のみです");
    const target = resolveStatic(p);
    if (!target) { res.writeHead(404); return res.end("Not found"); }
    serveFile(req, res, target);
  }

  const server = http.createServer((req, res) => {
    handle(req, res).catch((err) => {
      const status = err instanceof HttpError ? err.status : 500;
      if (status === 500) console.error("[server]", err);
      if (res.headersSent) return res.destroy();
      sendJSON(res, { ok: false, error: err instanceof HttpError ? err.message : "server error" }, status);
    });
  });

  // WebSocket — STL 変更通知・依頼通知。Origin が自分のページ以外なら受けない
  const wss = new WebSocketServer({
    host: HOST,
    port: WS_PORT,
    verifyClient: (info, cb) => {
      if (originOk(info.origin)) cb(true);
      else cb(false, 403, "Forbidden");
    },
  });
  const broadcast = (msg, { studioOnly = false } = {}) =>
    wss.clients.forEach((c) => c.readyState === 1 && !(studioOnly && c.legacy) && c.send(msg));
  wss.on("connection", (ws, req) => {
    try { ws.legacy = new URL(req.url, "http://x").searchParams.get("client") === "legacy"; } catch { ws.legacy = false; }
    ws.send(JSON.stringify({ type: "init", files: latestStlFiles() }));
  });

  function latestStlFiles() {
    if (!fs.existsSync(EXPORTS_DIR)) return [];
    return fs.readdirSync(EXPORTS_DIR)
      .filter((f) => f.endsWith(".stl"))
      .sort((a, b) =>
        fs.statSync(path.join(EXPORTS_DIR, b)).mtimeMs -
        fs.statSync(path.join(EXPORTS_DIR, a)).mtimeMs);
  }

  fs.mkdirSync(EXPORTS_DIR, { recursive: true });
  fs.watch(EXPORTS_DIR, (event, filename) => {
    if (filename && filename.endsWith(".stl")) {
      broadcast(JSON.stringify({ type: "update", files: latestStlFiles() }));
    }
  });

  // requests/ の変化 → {type:"requests", model, id}（200ms で間引く）。
  // 一時ディレクトリ（.<id>.tmp）の中の動きは出さない。.listener.json は在席の通知に回す
  const broadcastListener = () => broadcast(JSON.stringify({ type: "listener", ...readListener() }), { studioOnly: true });
  fs.mkdirSync(REQUESTS_DIR, { recursive: true });
  const pendingRequests = new Map();
  let requestsTimer = null;
  try {
    const watcher = fs.watch(REQUESTS_DIR, { recursive: true }, (event, filename) => {
      if (!filename) return;
      const parts = String(filename).split(/[\\/]/);
      if (parts[0] === ".listener.json") return broadcastListener();
      if (parts.length < 2 || parts[0].startsWith(".") || parts[1].startsWith(".")) return;
      pendingRequests.set(`${parts[0]}/${parts[1]}`, { model: parts[0], id: parts[1] });
      if (requestsTimer) return;
      requestsTimer = setTimeout(() => {
        requestsTimer = null;
        for (const m of pendingRequests.values()) {
          broadcast(JSON.stringify({ type: "requests", model: m.model, id: m.id }), { studioOnly: true });
        }
        pendingRequests.clear();
      }, 200);
    });
    watcher.on("error", (e) => console.error("[watch requests]", e));
  } catch (e) { console.error("[watch requests]", e); }
  setInterval(broadcastListener, 5000);

  // 後始末。自分が書いた .studio.json だけ消す
  const cleanup = () => {
    try {
      const j = JSON.parse(fs.readFileSync(STUDIO_JSON, "utf8"));
      if (j.pid === process.pid) fs.rmSync(STUDIO_JSON, { force: true });
    } catch { /* 無い */ }
  };
  process.on("exit", cleanup);
  for (const sig of ["SIGINT", "SIGTERM", "SIGBREAK"]) {
    try { process.on(sig, () => process.exit(0)); } catch { /* この OS に無い */ }
  }

  server.listen(HTTP_PORT, HOST, () => {
    fs.writeFileSync(STUDIO_JSON, JSON.stringify({
      http: HTTP_PORT, ws: WS_PORT, pid: process.pid, startedAt: isoLocal(new Date()),
    }, null, 2) + "\n", "utf8");
    console.log(`Viewer:   http://localhost:${HTTP_PORT}`);
    console.log(`WS:       ws://localhost:${WS_PORT}`);
    console.log(`Watching: ${EXPORTS_DIR}`);
    console.log(`Requests: ${REQUESTS_DIR}`);
  });
}

main().catch((e) => { console.error(e); process.exit(1); });
