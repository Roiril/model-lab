const http = require("http");
const net = require("net");
const fs = require("fs");
const path = require("path");
const { WebSocketServer } = require("ws");

const HTTP_PORT_START = 3000;
const WS_PORT_START = 3001;
const EXPORTS_DIR = path.join(__dirname, "exports");

const MIME = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".stl": "application/octet-stream",
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

async function main() {
  const HTTP_PORT = await findFreePort(HTTP_PORT_START);
  const WS_PORT = await findFreePort(Math.max(WS_PORT_START, HTTP_PORT + 1));

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
      if (ext === ".html") {
        // 実際のWSポートをHTMLに注入
        const html = data.toString("utf8")
          .replace(/ws:\/\/localhost:\d+/g, `ws://localhost:${WS_PORT}`);
        res.writeHead(200, { "Content-Type": MIME[ext] });
        res.end(html);
        return;
      }
      res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
      res.end(data);
    });
  });

  // WebSocket server — notifies clients on STL change
  const wss = new WebSocketServer({ port: WS_PORT });
  const broadcast = (msg) => wss.clients.forEach((c) => c.readyState === 1 && c.send(msg));

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
