// Studio の未対応の依頼を、セッション開始時とユーザー発話時に文脈へ差し込む。
// 未対応が無ければ何も出さない。UserPromptSubmit では「前回知らせた後に増えた/動いた」ときだけ出す。
// 依頼の読み方・返し方はスキル studio-inbox（.claude/skills/studio-inbox/SKILL.md）。
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const REQ_DIR = path.join(ROOT, "requests");
const SEEN = path.join(REQ_DIR, ".hook-seen.json");

function readStdin() {
  try { return JSON.parse(fs.readFileSync(0, "utf8") || "{}"); } catch { return {}; }
}

function readThread(file) {
  try {
    return fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean)
      .map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  } catch { return []; }
}

// requests.py の「未対応」と同じ定義:
// 最後の status が done / closed でない、または最後の shubie 行より後に user の message 行がある
function pending() {
  const out = [];
  if (!fs.existsSync(REQ_DIR)) return out;
  for (const model of fs.readdirSync(REQ_DIR)) {
    const mdir = path.join(REQ_DIR, model);
    if (model.startsWith(".") || !fs.statSync(mdir).isDirectory()) continue;
    for (const id of fs.readdirSync(mdir)) {
      const dir = path.join(mdir, id);
      const thread = readThread(path.join(dir, "thread.jsonl"));
      if (!thread.length) continue;
      const statuses = thread.filter((t) => t.kind === "status");
      const status = statuses.length ? statuses[statuses.length - 1].status : "open";
      let lastShubie = -1;
      thread.forEach((t, i) => { if (t.from === "shubie") lastShubie = i; });
      const userAfter = thread.slice(lastShubie + 1).some((t) => t.from === "user" && t.kind === "message");
      if (status === "closed") continue;
      if (status === "done" && !userAfter) continue;
      // 質問中はユーザーの返事待ち。返事（追記）が来るまで知らせない
      if (status === "question" && !userAfter) continue;
      let message = "";
      try { message = JSON.parse(fs.readFileSync(path.join(dir, "request.json"), "utf8")).message || ""; } catch { /* noop */ }
      out.push({ id, model, status, userAfter, message, last: thread[thread.length - 1].at || "", count: thread.length });
    }
  }
  return out.sort((a, b) => (a.id < b.id ? 1 : -1));
}

function listening() {
  try {
    const l = JSON.parse(fs.readFileSync(path.join(REQ_DIR, ".listener.json"), "utf8"));
    return Date.now() - Date.parse(l.at) < 30000 ? l.agent || "?" : null;
  } catch { return null; }
}

const input = readStdin();
const event = input.hook_event_name || "SessionStart";
const list = pending();
if (!list.length) process.exit(0);

// 何を知らせたかを覚えておき、UserPromptSubmit では変化があった依頼だけ出す
let seen = {};
try { seen = JSON.parse(fs.readFileSync(SEEN, "utf8")); } catch { seen = {}; }
const sig = (r) => `${r.count}:${r.last}`;
const fresh = event === "UserPromptSubmit" ? list.filter((r) => seen[r.id] !== sig(r)) : list;
for (const r of list) seen[r.id] = sig(r);
try { fs.writeFileSync(SEEN, JSON.stringify(seen)); } catch { /* noop */ }
if (!fresh.length) process.exit(0);

const who = listening();
const lines = [
  `[studio] Studio（ビューワー）からの未対応の依頼が ${fresh.length} 件あります。スキル studio-inbox の手順で対応すること。`,
];
for (const r of fresh.slice(0, 5)) {
  const head = r.message.replace(/\s+/g, " ").slice(0, 40);
  const tag = r.userAfter ? "追記あり" : r.status;
  lines.push(`- ${r.model} ${r.id} [${tag}] 「${head}」 → py -3.11 tools/requests.py show ${r.id}`);
}
if (fresh.length > 5) lines.push(`- ほか ${fresh.length - 5} 件 → py -3.11 tools/requests.py list`);
if (!who) lines.push("待ち受けが動いていません。対応後は studio-inbox の手順で watch を張って次の依頼を待つこと。");
process.stdout.write(lines.join("\n") + "\n");
