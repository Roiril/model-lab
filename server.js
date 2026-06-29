const http = require("http");
const net = require("net");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");
const { WebSocketServer } = require("ws");

const HTTP_PORT_START = 3000;
const WS_PORT_START = 3001;
const ROOT = __dirname;
const EXPORTS_DIR = path.join(ROOT, "exports");
const MODELS_DIR = path.join(ROOT, "models");
const VIEWER_DIR = path.join(ROOT, "viewer");
const PREVIEW_DIR = path.join(VIEWER_DIR, "preview");
const BLENDER = process.env.BLENDER ||
  "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe";

const MIME = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".stl": "application/octet-stream",
  ".glb": "model/gltf-binary",
  ".png": "image/png",
};

function findFreePort(start) {
  return new Promise((resolve, reject) => {
    const tryPort = (p) => {
      const tester = net.createServer()
        .once("error", (err) => {
          if (err.code === "EADDRINUSE" && p < start + 100) tryPort(p + 1);
          else reject(err);
        })
        .once("listening", () => tester.close(() => resolve(p)))
        .listen(p);
    };
    tryPort(start);
  });
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

function readBody(req) {
  return new Promise((resolve) => {
    let data = "";
    req.on("data", (c) => (data += c));
    req.on("end", () => { try { resolve(JSON.parse(data || "{}")); } catch { resolve({}); } });
  });
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

async function main() {
  const HTTP_PORT = await findFreePort(HTTP_PORT_START);
  const WS_PORT = await findFreePort(Math.max(WS_PORT_START, HTTP_PORT + 1));

  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${HTTP_PORT}`);
    const p = url.pathname;

    // --- API ---
    if (p === "/api/models") {
      const models = listModels().map((m) => ({ name: m, preview: hasPreview(m), category: readCategory(m) }));
      return sendJSON(res, { models });
    }
    if (p === "/api/params") {
      const model = url.searchParams.get("model");
      return sendJSON(res, { model, controls: parseParams(model), preview: hasPreview(model) });
    }
    if (p === "/api/export" && req.method === "POST") {
      const body = await readBody(req);
      const result = await buildModel(body.model, body.params);
      return sendJSON(res, result);
    }
    if (p === "/api/shot" && req.method === "POST") {
      let data = "";
      req.on("data", (c) => (data += c));
      req.on("end", () => {
        const b64 = data.replace(/^data:image\/png;base64,/, "");
        const out = path.join(EXPORTS_DIR, "deep-sea", "_browser_shot.png");
        fs.writeFileSync(out, Buffer.from(b64, "base64"));
        sendJSON(res, { ok: true, bytes: fs.statSync(out).size });
      });
      return;
    }

    // --- static ---
    let filePath = null;
    if (p === "/" || p === "/index.html") {
      filePath = path.join(VIEWER_DIR, "index.html");
    } else if (p.startsWith("/exports/")) {
      filePath = path.join(ROOT, p.slice(1));
    } else if (p.startsWith("/preview/")) {
      filePath = path.join(PREVIEW_DIR, path.basename(p));
    } else if (p.startsWith("/viewer/")) {
      filePath = path.join(ROOT, p.slice(1));
    }
    if (!filePath) { res.writeHead(404); return res.end("Not found"); }

    fs.readFile(filePath, (err, data) => {
      if (err) { res.writeHead(404); return res.end("Not found"); }
      const ext = path.extname(filePath);
      if (ext === ".html") {
        const html = data.toString("utf8")
          .replace(/ws:\/\/localhost:\d+/g, `ws://localhost:${WS_PORT}`);
        res.writeHead(200, { "Content-Type": MIME[ext] });
        return res.end(html);
      }
      res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
      res.end(data);
    });
  });

  function sendJSON(res, obj) {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(obj));
  }

  // WebSocket — STL 変更通知
  const wss = new WebSocketServer({ port: WS_PORT });
  const broadcast = (msg) => wss.clients.forEach((c) => c.readyState === 1 && c.send(msg));
  wss.on("connection", (ws) => ws.send(JSON.stringify({ type: "init", files: latestStlFiles() })));

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

  server.listen(HTTP_PORT, () => {
    console.log(`Viewer:   http://localhost:${HTTP_PORT}`);
    console.log(`WS:       ws://localhost:${WS_PORT}`);
    console.log(`Watching: ${EXPORTS_DIR}`);
  });
}

main().catch((e) => { console.error(e); process.exit(1); });
