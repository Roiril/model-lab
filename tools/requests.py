"""Studio の依頼（requests/<model>/<id>/）を読む・返信する・待ち受ける。

  py -3.11 tools/requests.py list [--all] [--model M]
  py -3.11 tools/requests.py show <id>
  py -3.11 tools/requests.py reply <id> "本文" [--status working|done|question] [--claim AGENT] [--force]
  py -3.11 tools/requests.py watch [--agent NAME] [--interval 2]
  py -3.11 tools/requests.py wait [--agent NAME] [--timeout 秒]

id は前方一致。標準ライブラリのみ。
"""
import argparse
import atexit
import datetime
import json
import math
import os
import signal
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)

ROOT = Path(__file__).resolve().parent.parent
REQUESTS_DIR = ROOT / "requests"
LISTENER_FILE = REQUESTS_DIR / ".listener.json"
HEARTBEAT_SEC = 10
DONE_STATUSES = ("done", "closed")
CMD = "py -3.11 tools/requests.py"

# viewer/studio/store.js の ACTIONS / INTENTS と同じ日本語
ACTIONS = {
    "thicken": "厚く", "thin": "薄く", "round": "丸める", "smooth": "滑らかに",
    "flatten": "平らに", "cut": "削る", "add": "足す", "hole": "穴", "other": "その他",
}
# 量の意味（store.js のコメント）
AMOUNT_NOTE = {"round": "半径", "hole": "径"}
INTENTS = {"target": "目標の線", "remove": "削る", "add": "足す", "note": "メモ"}
SIDES = {"out": "外側", "in": "内側", "both": "両側"}
SHAPE_KINDS = {
    "pen": "ペン", "line": "直線", "curve": "曲線", "rect": "四角",
    "ellipse": "楕円", "arrow": "矢印", "text": "文字", "dim": "寸法",
}
ITEM_TYPES = {"faces": "面", "pin": "ピン", "measure": "計測", "section": "断面"}
STATUS_LABELS = {
    "open": "未着手", "working": "対応中", "question": "質問中", "done": "完了", "closed": "閉じた",
}


# --- 小物 -------------------------------------------------------------------
def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def parse_time(s):
    try:
        t = datetime.datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None
    if t.tzinfo is None:
        t = t.astimezone()
    return t


def elapsed_label(s):
    t = parse_time(s)
    if t is None:
        return "?"
    sec = max(0, (datetime.datetime.now().astimezone() - t).total_seconds())
    if sec < 90:
        return f"{int(sec)}秒前"
    if sec < 5400:
        return f"{int(sec // 60)}分前"
    if sec < 36 * 3600:
        return f"{int(sec // 3600)}時間前"
    return f"{int(sec // 86400)}日前"


def head40(text):
    flat = " ".join(str(text or "").split())
    return flat[:40] + ("…" if len(flat) > 40 else "")


def num(x, digits=2):
    if x is None:
        return "?"
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return str(x)
    s = f"{x:.{digits}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def vec(v):
    if not isinstance(v, (list, tuple)):
        return "?"
    return "(" + ", ".join(num(c) for c in v) + ")"


def bbox_str(b):
    if not isinstance(b, dict):
        return "?"
    return f"{vec(b.get('min'))} 〜 {vec(b.get('max'))}"


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json_atomic(path, obj):
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False)
    for attempt in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(0.05 * (attempt + 1))
    # 読み手が掴んだままのとき。直書きに落とす
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False)
    try:
        tmp.unlink()
    except OSError:
        pass


def append_line(path, obj):
    prefix = ""
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            if f.tell() > 0:
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b"\n":
                    prefix = "\n"
    except OSError:
        pass
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(prefix + json.dumps(obj, ensure_ascii=False) + "\n")


# --- 依頼の読み込み ---------------------------------------------------------
class Rec:
    """request.json と thread.jsonl をまとめて持つ。"""

    def __init__(self, model, rid, directory, req, thread):
        self.model = model
        self.id = rid
        self.dir = directory
        self.req = req
        self.thread = thread

    @property
    def message(self):
        return self.req.get("message") or ""

    @property
    def items(self):
        items = self.req.get("items")
        return items if isinstance(items, list) else []

    @property
    def status(self):
        s = "open"
        for line in self.thread:
            if line.get("kind") == "status" and line.get("status"):
                s = line["status"]
        return s

    @property
    def claim(self):
        c = None
        for line in self.thread:
            if line.get("claim"):
                c = line["claim"]
        return c

    def user_followup(self):
        """最後の shubie 行より後に user の message 行があるか。"""
        last_shubie = -1
        for i, line in enumerate(self.thread):
            if line.get("from") == "shubie":
                last_shubie = i
        return any(
            line.get("from") == "user" and line.get("kind") == "message"
            for line in self.thread[last_shubie + 1:]
        )

    def pending(self):
        return self.status not in DONE_STATUSES or self.user_followup()

    def actionable(self):
        """今すぐ手を付けるべきもの: 未着手か、ユーザーの追記に未返信。対応中・質問中は含めない。"""
        return self.status == "open" or self.user_followup()


def read_thread(path):
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except ValueError:
                    continue  # 書きかけの行
                if isinstance(obj, dict):
                    out.append(obj)
    except OSError:
        pass
    return out


def load_all(model=None):
    recs = []
    if not REQUESTS_DIR.is_dir():
        return recs
    for mdir in sorted(REQUESTS_DIR.iterdir()):
        if not mdir.is_dir() or mdir.name.startswith("."):
            continue
        if model and mdir.name != model:
            continue
        for rdir in mdir.iterdir():
            if not rdir.is_dir() or rdir.name.startswith("."):
                continue
            try:
                req = read_json(rdir / "request.json")
            except (OSError, ValueError):
                continue
            if not isinstance(req, dict):
                continue
            recs.append(Rec(mdir.name, rdir.name, rdir, req, read_thread(rdir / "thread.jsonl")))
    recs.sort(key=lambda r: r.id, reverse=True)
    return recs


def resolve(prefix):
    recs = load_all()
    exact = [r for r in recs if r.id == prefix]
    if exact:
        return exact[0]
    hits = [r for r in recs if r.id.startswith(prefix)]
    if not hits:
        print(f"依頼が見つかりません: {prefix}", file=sys.stderr)
        sys.exit(1)
    if len(hits) > 1:
        print(f"id が曖昧です（{len(hits)} 件）。もう少し長く指定してください:", file=sys.stderr)
        for r in hits:
            print(f"  {r.id}  {r.model}  「{head40(r.message)}」", file=sys.stderr)
        sys.exit(2)
    return hits[0]


# --- list -------------------------------------------------------------------
def state_label(rec):
    label = rec.status
    if rec.user_followup() and rec.status in DONE_STATUSES:
        label += "+追記"
    elif rec.user_followup():
        label += "+追記あり"
    return label


def cmd_list(args):
    recs = load_all(args.model)
    if not args.all:
        recs = [r for r in recs if r.pending()]
    if not recs:
        print("未対応の依頼はありません" if not args.all else "依頼はありません")
        return 0
    for r in recs:
        claim = f" claim={r.claim}" if r.claim else ""
        print(
            f"{r.id}  {r.model}  [{state_label(r)}]  {elapsed_label(r.req.get('createdAt'))}  "
            f"「{head40(r.message)}」  指示{len(r.items)}件{claim}"
        )
    return 0


# --- show -------------------------------------------------------------------
def polyline_length(pts):
    total = 0.0
    for a, b in zip(pts, pts[1:]):
        total += math.dist(a, b)
    return total


def points_bbox(pts):
    if not pts:
        return None
    dims = len(pts[0])
    return {
        "min": [min(p[i] for p in pts) for i in range(dims)],
        "max": [max(p[i] for p in pts) for i in range(dims)],
    }


def describe_faces(it):
    out = []
    action = it.get("action")
    label = ACTIONS.get(action, action or "?")
    head = f"動作: {label}"
    if it.get("amount") is not None:
        head += f" {num(it['amount'])}mm"
        if action in AMOUNT_NOTE:
            head += f"（{AMOUNT_NOTE[action]}）"
    if it.get("side"):
        head += f" / 側: {SIDES.get(it['side'], it['side'])}"
    out.append(head)
    s = it.get("summary") or {}
    out.append(f"面数 {s.get('faceCount', '?')} / 面積 {num(s.get('area'))}mm²")
    th = s.get("thickness")
    if isinstance(th, dict):
        out.append(f"今の肉厚: min {num(th.get('min'))}mm / median {num(th.get('median'))}mm")
    out.append(f"重心 {vec(s.get('centroid'))} / 法線 {vec(s.get('normal'))}")
    out.append(f"bbox {bbox_str(s.get('bbox'))}")
    if s.get("samples"):
        out.append(f"サンプル点 {len(s['samples'])} 個（request.json の items[].summary.samples）")
    return out


def describe_shape(j, sh):
    kind = SHAPE_KINDS.get(sh.get("kind"), sh.get("kind"))
    intent = INTENTS.get(sh.get("intent"), sh.get("intent"))
    line = f"  図形 {j}: {kind} / {intent}"
    if sh.get("closed"):
        line += " / 閉じている"
    parts = [line]
    if sh.get("text"):
        parts.append(f"    文字: {sh['text']}")
    if sh.get("note"):
        parts.append(f"    メモ: {sh['note']}")
    p3 = sh.get("polyline3d")
    if isinstance(p3, list) and p3:
        bb = points_bbox(p3)
        parts.append(
            f"    折れ線 {len(p3)} 点 / 始点 {vec(p3[0])} / 終点 {vec(p3[-1])} / "
            f"長さ {num(polyline_length(p3))}mm"
        )
        parts.append(f"    bbox {bbox_str(bb)}")
    else:
        parts.append("    折れ線 なし（nodes のみ）")
    return parts


def describe_section(it):
    out = []
    pl = it.get("plane") or {}
    offset = it.get("offset") or 0
    origin, normal = pl.get("origin"), pl.get("normal")
    out.append(f"軸: {pl.get('axis', '?')} / 法線方向オフセット {num(offset)}mm")
    if isinstance(origin, list) and isinstance(normal, list) and len(origin) == 3 and len(normal) == 3:
        cut = [origin[i] + normal[i] * offset for i in range(3)]
        out.append(f"切断面: 通る点 {vec(cut)} / 法線 {vec(normal)}")
    out.append(f"2D の向き: u={vec(pl.get('u'))} v={vec(pl.get('v'))}")
    loops = it.get("loops") or []
    if isinstance(loops, dict):  # 古い送り方（{loops, ghostLoops, bounds}）も読む
        loops = loops.get("loops") or []
    pts = [p for lp in loops if isinstance(lp, dict) for p in (lp.get("points") or [])]
    if pts:
        bb = points_bbox(pts)
        out.append(f"輪郭 {len(loops)} 本 / uv の範囲 u {num(bb['min'][0])}〜{num(bb['max'][0])} v {num(bb['min'][1])}〜{num(bb['max'][1])}")
    else:
        out.append(f"輪郭 {len(loops)} 本")
    if it.get("clip"):
        out.append("片側を隠して表示していた")
    if it.get("image") or it.get("svg"):
        out.append(f"画像: {it.get('image', '-')} / {it.get('svg', '-')}")
    shapes = it.get("shapes") or []
    out.append(f"図形 {len(shapes)} 個")
    for j, sh in enumerate(shapes):
        out.extend(describe_shape(j, sh))
    return out


def describe_item(i, it):
    t = it.get("type")
    out = [f"▼ items[{i}] {ITEM_TYPES.get(t, t)} ({t}) 色 {it.get('color', '?')} / ファイル {it.get('file', '-')}"]
    if t == "faces":
        body = describe_faces(it)
    elif t == "pin":
        body = [f"点 {vec(it.get('point'))} / 法線 {vec(it.get('normal'))}"]
    elif t == "measure":
        body = [f"2 点 {vec(it.get('a'))} → {vec(it.get('b'))} / 距離 {num(it.get('distance'))}mm"]
    elif t == "section":
        body = describe_section(it)
    else:
        body = [json.dumps(it, ensure_ascii=False)[:200]]
    if it.get("note") and t != "section":
        body.append(f"メモ: {it['note']}")
    elif it.get("note"):
        body.insert(0, f"メモ: {it['note']}")
    out.extend("  " + b if not b.startswith("  図形") and not b.startswith("    ") else b for b in body)
    return out


def describe_provenance(rec):
    prov = rec.req.get("provenance") or {}
    out = [f"出どころ: gitHead {prov.get('gitHead') or '?'} / 座標系 {rec.req.get('frame', '?')}"]
    for s in prov.get("stl") or []:
        line = f"  STL {s.get('file')}"
        if s.get("missing"):
            line += "  ※ exports/ に実物が無かった"
        else:
            line += f" / sha1 {str(s.get('sha1') or '?')[:10]} / {s.get('size', '?')}B / {s.get('mtime', '?')}"
        line += f" / unitScale {num(s.get('unitScale'), 4)}"
        if s.get("placed"):
            line += "  ⚠ 配置版（print/plate/split を含む名前。印刷用に並べ替えた位置・向きの可能性）"
        out.append(line)
        if s.get("bbox"):
            out.append(f"      bbox {bbox_str(s['bbox'])}")
    params = (prov.get("params") or {}).get("values") or {}
    out.append(f"  params.py の値 {len(params)} 個（request.json の provenance.params.values）")
    ov = prov.get("overrides")
    if not ov:
        out.append("  _overrides.json: なし")
    elif isinstance(ov, dict) and "appliedToStl" in ov:
        head = ("⚠ STL はスライダーの値で作られている（params.py とずれている）" if ov.get("appliedToStl")
                else "STL には効いていない（古い上書き）")
        out.append(f"  _overrides.json: {head}  {json.dumps(ov.get('values'), ensure_ascii=False)}")
    else:
        out.append("  _overrides.json: " + json.dumps(ov, ensure_ascii=False))
    return out


def cmd_show(args):
    rec = resolve(args.id)
    req = rec.req
    print(f"依頼 {rec.id}  モデル {rec.model}")
    print(f"作成 {req.get('createdAt', '?')}（{elapsed_label(req.get('createdAt'))}） / 状態 {rec.status}"
          + (f" / claim {rec.claim}" if rec.claim else "")
          + (" / ユーザーの追記に未返信" if rec.user_followup() else ""))
    for line in describe_provenance(rec):
        print(line)
    cam = req.get("camera")
    if isinstance(cam, dict):
        print(f"カメラ: 位置 {vec(cam.get('position'))} / 注視点 {vec(cam.get('target'))} / fov {num(cam.get('fov'))}")
    print()
    print("全体メッセージ:")
    print("  " + (rec.message.replace("\n", "\n  ") if rec.message else "（なし）"))
    print()
    print(f"指示 {len(rec.items)} 件")
    for i, it in enumerate(rec.items):
        for line in describe_item(i, it):
            print(line)
        print()

    images = sorted(p for p in rec.dir.iterdir() if p.suffix.lower() in (".png", ".svg"))
    order = req.get("images") if isinstance(req.get("images"), list) else []
    images.sort(key=lambda p: (order.index(p.name) if p.name in order else 1e9, p.name))
    print("画像（Read で開く）:")
    for p in images:
        print(f"  {p}")
    if not images:
        print("  （なし）")
    before_dir = rec.dir / "before"
    befores = sorted(before_dir.glob("*.stl")) if before_dir.is_dir() else []
    print("変更前の STL:")
    for p in befores:
        print(f"  {p}")
    if not befores:
        print("  （なし）")
    print()
    print("スレッド:")
    for line in rec.thread:
        who = line.get("from", "?")
        if line.get("kind") == "status":
            body = f"[状態 → {line.get('status')}]" + (f" claim={line['claim']}" if line.get("claim") else "")
        else:
            body = line.get("text", "")
        print(f"  {line.get('at', '?')} {who}: {body}")
    print()
    print("全点は request.json の items[i].shapes[j].polyline3d にあります:")
    print(f"  {rec.dir / 'request.json'}")
    return 0


# --- reply ------------------------------------------------------------------
def cmd_reply(args):
    rec = resolve(args.id)
    status = args.status
    if args.claim and not status:
        status = "working"  # claim は status 行に載せるので、状態が無ければ「対応中」にする
    if not args.text and not status:
        print("本文か --status のどちらかが要ります", file=sys.stderr)
        return 2
    if args.claim and not args.force:
        current = rec.claim
        if current and current != args.claim and rec.status not in DONE_STATUSES:
            print(
                f"警告: {rec.id} は既に {current} が着手しています（状態 {rec.status}）。"
                f"上書きするなら --force を付けてください",
                file=sys.stderr,
            )
            return 3
    thread = rec.dir / "thread.jsonl"
    if args.text:
        append_line(thread, {"at": now_iso(), "from": "shubie", "kind": "message", "text": args.text})
    if status:
        line = {"at": now_iso(), "from": "shubie", "kind": "status", "status": status}
        if args.claim:
            line["claim"] = args.claim
        append_line(thread, line)
    done = []
    if args.text:
        done.append("本文")
    if status:
        done.append(f"状態 {status}" + (f"（claim {args.claim}）" if args.claim else ""))
    print(f"返信しました: {rec.id}  " + " / ".join(done))
    return 0


# --- watch / wait -----------------------------------------------------------
def event_line(rec, kind, text=None):
    if kind == "new":
        return (f"[新しい依頼] {rec.model} {rec.id} 「{head40(rec.message)}」 指示{len(rec.items)}件 "
                f"→ {CMD} show {rec.id}")
    if kind == "append":
        return f"[追記] {rec.model} {rec.id} 「{head40(text)}」 → {CMD} show {rec.id}"
    return f"[閉じた] {rec.model} {rec.id}"


def pending_lines():
    """起動時に出す未対応の一覧（新しい順の逆＝古い順）。"""
    lines = []
    for rec in reversed([r for r in load_all() if r.actionable()]):
        if rec.user_followup() and any(l.get("from") == "shubie" for l in rec.thread):
            last = [l for l in rec.thread if l.get("from") == "user" and l.get("kind") == "message"][-1]
            lines.append(event_line(rec, "append", last.get("text", "")))
        else:
            lines.append(event_line(rec, "new"))
    return lines


class Watcher:
    """thread の既読行数を持ち、新しい user の出来事を 1 行にする。shubie 自身の行では出さない。"""

    def __init__(self):
        self.seen = {}  # id -> 既読の thread 行数
        for rec in load_all():
            self.seen[rec.id] = len(rec.thread)

    def poll(self):
        lines = []
        for rec in reversed(load_all()):  # 古い順
            n = self.seen.get(rec.id)
            if n is None:
                self.seen[rec.id] = len(rec.thread)
                lines.append(event_line(rec, "new"))
                continue
            fresh = rec.thread[n:]
            self.seen[rec.id] = len(rec.thread)
            for line in fresh:
                if line.get("from") != "user":
                    continue
                if line.get("kind") == "message":
                    lines.append(event_line(rec, "append", line.get("text", "")))
                elif line.get("kind") == "status" and line.get("status") == "closed":
                    lines.append(event_line(rec, "close"))
                elif line.get("kind") == "status" and line.get("status") == "open":
                    lines.append(event_line(rec, "append", "（再び開かれました）"))
        return lines


class Heartbeat:
    """requests/.listener.json に在席を書く。終了時に自分の分だけ消す。"""

    def __init__(self, agent):
        self.agent = agent or "unknown"
        self.last = 0.0
        REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
        atexit.register(self.remove)

        def stop(signum, frame):
            raise SystemExit(0)

        for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
            sig = getattr(signal, name, None)
            if sig is not None:
                try:
                    signal.signal(sig, stop)
                except (ValueError, OSError):
                    pass
        self.beat(force=True)

    def beat(self, force=False):
        if not force and time.monotonic() - self.last < HEARTBEAT_SEC:
            return
        self.last = time.monotonic()
        try:
            write_json_atomic(LISTENER_FILE, {"agent": self.agent, "pid": os.getpid(), "at": now_iso()})
        except OSError as e:
            print(f"[警告] 在席ファイルを書けません: {e}", file=sys.stderr)

    def remove(self):
        try:
            if read_json(LISTENER_FILE).get("pid") == os.getpid():
                LISTENER_FILE.unlink()
        except (OSError, ValueError):
            pass


def sleep_with_beat(hb, seconds):
    end = time.monotonic() + seconds
    while True:
        hb.beat()
        left = end - time.monotonic()
        if left <= 0:
            return
        time.sleep(min(0.2, left))


def cmd_watch(args):
    hb = Heartbeat(args.agent)
    for line in pending_lines():
        print(line)
    watcher = Watcher()
    try:
        while True:
            sleep_with_beat(hb, args.interval)
            for line in watcher.poll():
                print(line)
    except (KeyboardInterrupt, SystemExit):
        return 0


def cmd_wait(args):
    lines = pending_lines()
    if lines:
        for line in lines:
            print(line)
        return 0
    hb = Heartbeat(args.agent)
    watcher = Watcher()
    deadline = time.monotonic() + args.timeout if args.timeout and args.timeout > 0 else None
    try:
        while True:
            step = args.interval
            if deadline is not None:
                step = max(0.0, min(step, deadline - time.monotonic()))
            sleep_with_beat(hb, step)
            events = watcher.poll()
            if events:
                for line in events:
                    print(line)
                return 0
            if deadline is not None and time.monotonic() >= deadline:
                print("[待ち受け終了] 新しい依頼なし")
                return 0
    except (KeyboardInterrupt, SystemExit):
        return 0


# --- main -------------------------------------------------------------------
def build_parser():
    ap = argparse.ArgumentParser(prog="requests.py", description="Studio の依頼を読む・返信する・待ち受ける")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="未対応の依頼を新しい順に 1 行ずつ")
    p.add_argument("--all", action="store_true", help="対応済みも含める")
    p.add_argument("--model", help="モデル名で絞る")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("show", help="依頼の要約（指示・画像・スレッド）")
    p.add_argument("id", help="依頼 id（前方一致）")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("reply", help="返信と状態の更新")
    p.add_argument("id", help="依頼 id（前方一致）")
    p.add_argument("text", nargs="?", default="", help="返信の本文")
    p.add_argument("--status", choices=["working", "done", "question"], help="状態を更新する")
    p.add_argument("--claim", metavar="AGENT", help="着手の宣言（status 行に載る。--status を省くと working）")
    p.add_argument("--force", action="store_true", help="他の claim を上書きする")
    p.set_defaults(fn=cmd_reply)

    p = sub.add_parser("watch", help="起動時に未対応を出し、以後は新しい出来事を 1 行ずつ出し続ける")
    p.add_argument("--agent", default=None, help="在席ファイルに書く名前")
    p.add_argument("--interval", type=float, default=2.0, help="ポーリング間隔（秒）")
    p.set_defaults(fn=cmd_watch)

    p = sub.add_parser("wait", help="未対応があれば出して即終了。無ければ最初の出来事まで待つ")
    p.add_argument("--agent", default=None, help="在席ファイルに書く名前")
    p.add_argument("--timeout", type=float, default=0, help="待つ上限（秒）。0 は無期限")
    p.add_argument("--interval", type=float, default=2.0, help="ポーリング間隔（秒）")
    p.set_defaults(fn=cmd_wait)
    return ap


def main():
    args = build_parser().parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
