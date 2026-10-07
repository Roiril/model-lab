// サーバー（server.js）との薄い接続。fetch の包みと、再接続つきの WebSocket。
// 画面の知識は持たない。形は .agent/plans/2026-10-07_studio.md §4。

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function call(method, url, body) {
  const opt = { method, headers: {} };
  if (body !== undefined) {
    opt.headers["Content-Type"] = "application/json";
    opt.body = JSON.stringify(body);
  }
  const res = await fetch(url, opt);
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = null; }
  if (!res.ok) {
    const why = (data && (data.error || data.message)) || `${res.status} ${res.statusText}`;
    throw new ApiError(why, res.status);
  }
  return data;
}

const enc = encodeURIComponent;

export const api = {
  config: () => call("GET", "/api/config"),
  models: async () => {
    const d = await call("GET", "/api/models");
    return Array.isArray(d) ? d : (d && d.models) || [];
  },
  params: (model) => call("GET", `/api/params?model=${enc(model)}`),
  stls: async () => {
    const d = await call("GET", "/api/stls");
    return Array.isArray(d) ? d : (d && d.files) || [];
  },
  listener: () => call("GET", "/api/listener"),
  requests: async (model) => {
    const d = await call("GET", `/api/requests?model=${enc(model)}`);
    return Array.isArray(d) ? d : (d && d.requests) || [];
  },
  createRequest: (body) => call("POST", "/api/requests", body),
  sendMessage: (id, text) => call("POST", `/api/requests/${enc(id)}/messages`, { text }),
  setRequestStatus: (id, status) => call("POST", `/api/requests/${enc(id)}/status`, { status }),
  exportModel: (model, params) => call("POST", "/api/export", { model, params }),
};

// --- 依頼の読み取り補助（画面と app の両方で使う）---------------------------

export const REQUEST_STATUS = {
  open:     { label: "送信済み" },
  working:  { label: "対応中" },
  done:     { label: "完了" },
  question: { label: "質問" },
  closed:   { label: "閉じた" },
};

// サーバーが返す status を信用し、無ければ thread の最後の status 行から読む
export function requestStatus(r) {
  if (r && r.status) return r.status;
  const t = (r && r.thread) || [];
  for (let i = t.length - 1; i >= 0; i--) {
    if (t[i] && t[i].kind === "status" && t[i].status) return t[i].status;
  }
  return "open";
}

// 変更前の STL の URL。複数あるときは preferFiles（今見ている STL の名前）に合うものを先に取る
export function requestBefore(r, preferFiles = []) {
  const list = Array.isArray(r && r.before) ? r.before : [];
  if (!list.length) return null;
  for (const f of preferFiles) {
    const hit = list.find((b) => b.file === f);
    if (hit) return hit;
  }
  return list[0];
}

// --- WebSocket --------------------------------------------------------------

// 切れたら 2 秒後に繋ぎ直す。on(type, fn) で種類ごとに受け、"*" は全部
export function connectWS(url) {
  const handlers = new Map();
  const stateFns = new Set();
  let ws = null;
  let timer = null;
  let closed = false;

  const emit = (type, msg) => {
    for (const fn of handlers.get(type) || []) {
      try { fn(msg); } catch (e) { console.error(`[ws] ${type}`, e); }
    }
  };
  const setState = (up) => {
    for (const fn of stateFns) {
      try { fn(up); } catch (e) { console.error("[ws] state", e); }
    }
  };

  function open() {
    clearTimeout(timer);
    if (closed) return;
    try { ws = new WebSocket(url); } catch (e) {
      console.error("[ws] 接続できません", e);
      timer = setTimeout(open, 2000);
      return;
    }
    ws.onopen = () => setState(true);
    ws.onmessage = (ev) => {
      let msg = null;
      try { msg = JSON.parse(ev.data); } catch { return; }
      if (!msg || typeof msg !== "object") return;
      emit(msg.type, msg);
      emit("*", msg);
    };
    ws.onerror = () => { try { ws.close(); } catch { /* 既に閉じている */ } };
    ws.onclose = () => {
      setState(false);
      if (closed) return;
      clearTimeout(timer);
      timer = setTimeout(open, 2000);
    };
  }
  open();

  return {
    on(type, fn) {
      if (!handlers.has(type)) handlers.set(type, new Set());
      handlers.get(type).add(fn);
      return () => handlers.get(type)?.delete(fn);
    },
    onState(fn) {
      stateFns.add(fn);
      return () => stateFns.delete(fn);
    },
    close() {
      closed = true;
      clearTimeout(timer);
      try { ws && ws.close(); } catch { /* noop */ }
    },
  };
}
