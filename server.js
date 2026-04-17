const http = require("http");
const fs = require("fs");
const path = require("path");
const { WebSocketServer } = require("ws");

const PORT = 3000;
const WS_PORT = 3001;
const EXPORTS_DIR = path.join(__dirname, "exports");

const MIME = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".stl": "application/octet-stream",
};

// HTTP server — serves viewer/ and exports/
const server = http.createServer((req, res) => {
  let filePath;
  if (req.url === "/" || req.url === "/index.html") {
    filePath = path.join(__dirname, "viewer", "index.html");
  } else if (req.url.startsWith("/exports/")) {
    filePath = path.join(__dirname, req.url.slice(1));
  } else {
    res.writeHead(404);
    res.end("Not found");
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end("Not found"); return; }
    const ext = path.extname(filePath);
    res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
    res.end(data);
  });
});

// WebSocket server — notifies clients on STL change
const wss = new WebSocketServer({ port: WS_PORT });
const broadcast = (msg) => wss.clients.forEach((c) => c.readyState === 1 && c.send(msg));

// Send latest STL list when client connects
wss.on("connection", (ws) => {
  const files = latestStlFiles();
  ws.send(JSON.stringify({ type: "init", files }));
});

function latestStlFiles() {
  if (!fs.existsSync(EXPORTS_DIR)) return [];
  return fs.readdirSync(EXPORTS_DIR)
    .filter((f) => f.endsWith(".stl"))
    .sort((a, b) => {
      const ta = fs.statSync(path.join(EXPORTS_DIR, a)).mtimeMs;
      const tb = fs.statSync(path.join(EXPORTS_DIR, b)).mtimeMs;
      return tb - ta;
    });
}

// Watch exports/ for changes
fs.mkdirSync(EXPORTS_DIR, { recursive: true });
fs.watch(EXPORTS_DIR, (event, filename) => {
  if (filename && filename.endsWith(".stl")) {
    broadcast(JSON.stringify({ type: "update", files: latestStlFiles() }));
  }
});

server.listen(PORT, () => {
  console.log(`Viewer: http://localhost:${PORT}`);
  console.log(`Watching: ${EXPORTS_DIR}`);
});
