"""機構モデルの部品台帳を書く（Studio が部品を人の分かる名前で扱うためのデータ）。

入力: models/<model>/build/manifest.json（parts[{id,label,assembly,...}]）
      models/<model>/build/ui.json の legendGroups（あれば）
      models/<model>/part-names.json（ユーザーの呼び名。あれば）
出力: viewer/studio/parts/<model>.json（台帳。形は viewer/studio/CONTRACT.md §7）
      exports/<model>-part-<id>.stl（組立姿勢のままの部品 STL。mm）

使い方: py -3.11 tools/studio_parts.py [<model> ...]   （引数なしなら build/manifest.json を持つ全モデル）
壊れた入力は日本語で列挙して exit 2。
"""

import hashlib
import json
import os
import re
import struct
import sys
import tempfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_VERSION = 1
MODEL_RE = re.compile(r"^[\w.-]+$")
PART_ID_RE = re.compile(r"^[\w/-]+$")
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
DEFAULT_COLOR = "#999999"
KINDS = ("printed", "stock", "jig")

# 台帳に無い（ui.json の legendGroups が無い）モデルで、id の接頭辞から群を作るときの日本語名
PREFIX_LABELS = {
    "frame": "枠", "front": "正面", "right": "右面", "back": "背面", "left": "左面",
    "top": "上面", "bottom": "下面", "key": "留め具", "cam": "カム", "gear": "歯車",
    "shaft": "カム軸", "pixel": "画素", "servo": "サーボ", "clip": "押さえクリップ",
    "panel": "面板", "horn": "ホーン",
}
FIXED_GROUPS = {
    "shell": "外装",
    "other": "その他",
    "stock": "既製部品",
    "jig": "組立治具",
}


class PartsError(Exception):
    """入力が壊れている。problems は日本語の 1 行ずつ。"""

    def __init__(self, problems):
        super().__init__("; ".join(problems))
        self.problems = list(problems)


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _read_json(path, problems, what):
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as error:
        problems.append(f"{what} を読めません: {error}")
        return None, None
    try:
        return json.loads(raw.decode("utf-8-sig")), raw
    except (UnicodeDecodeError, ValueError) as error:
        problems.append(f"{what} が JSON として壊れています: {error}")
        return None, None


def _stl_problem(data):
    """STL として読めなければ理由を返す。読めれば None。"""
    if len(data) >= 84:
        count = struct.unpack("<I", data[80:84])[0]
        if count > 0 and len(data) == 84 + count * 50:
            return None
    text = data.decode("ascii", "replace")
    if text.lstrip().startswith("solid") and re.search(r"\bvertex\b", text):
        return None
    return "三角形が 0 個、またはサイズが合いません"


def _safe_file_name(model, part_id):
    return f"{model}-part-{part_id.replace('/', '__')}.stl"


def _unique(base, taken):
    name, number = base, 2
    while name in taken:
        name = f"{base}_{number}"
        number += 1
    return name


def _common_group_id(ids):
    """id の配列の共通の先頭から、末尾の `_` と数字を落とした ASCII の名前。無ければ空。"""
    prefix = os.path.commonprefix(list(ids))
    prefix = re.sub(r"[_\d]+$", "", prefix)
    return prefix if re.match(r"^[A-Za-z][\w-]*$", prefix) else ""


def _prefix_group_key(part_id, counts):
    """ui.json に群が無いモデルの、id から決める群キー。属さないなら None。"""
    if "/" in part_id:
        return part_id.split("/", 1)[0]
    if "_" in part_id:
        head = part_id.split("_", 1)[0]
        if counts.get(head, 0) >= 2:
            return head
    return None


def _part_kind(raw):
    if raw.get("jig") is True:
        return "jig"
    if raw.get("stock") is True or not raw.get("print"):
        return "stock"
    return "printed"


def _load_manifest(model, root, problems):
    folder = os.path.join(root, "models", model)
    path = os.path.join(folder, "build", "manifest.json")
    if not os.path.isfile(path):
        problems.append(f"models/{model}/build/manifest.json がありません")
        return None
    data, raw = _read_json(path, problems, f"models/{model}/build/manifest.json")
    if data is None:
        return None
    parts = data.get("parts") if isinstance(data, dict) else None
    if not isinstance(parts, list) or not parts:
        problems.append("manifest.json の parts は 1 個以上の配列にしてください")
        return None
    return {"folder": folder, "data": data, "sha256": _sha256_bytes(raw), "parts": parts}


def _validate_parts(model, manifest, problems):
    """manifest の各部品を検査して、台帳に使う形（id/label/color/kind/source/data）の配列を返す。"""
    folder = os.path.realpath(manifest["folder"])
    seen_ids, seen_files, parts = set(), {}, []
    for index, raw in enumerate(manifest["parts"]):
        where = f"manifest.json の parts[{index}]"
        if not isinstance(raw, dict):
            problems.append(f"{where} はオブジェクトにしてください")
            continue
        part_id = raw.get("id")
        if not isinstance(part_id, str) or not PART_ID_RE.match(part_id):
            problems.append(f"{where} の id は英数字・_・-・/ だけの文字列にしてください: {part_id!r}")
            continue
        where = f"部品 {part_id}"
        if part_id in seen_ids:
            problems.append(f"{where} の id が重複しています")
            continue
        seen_ids.add(part_id)
        label = raw.get("label")
        if not isinstance(label, str) or not label.strip():
            problems.append(f"{where} の label がありません")
            continue
        color = raw.get("color")
        if color is not None and not (isinstance(color, str) and HEX_COLOR.match(color)):
            problems.append(f"{where} の color は #rrggbb にしてください: {color!r}")
            color = None
        assembly = raw.get("assembly")
        if not isinstance(assembly, str) or not assembly:
            problems.append(f"{where} の assembly（組立姿勢の STL）がありません")
            continue
        source = os.path.realpath(os.path.join(folder, assembly))
        if os.path.commonpath([folder, source]) != folder:
            problems.append(f"{where} の assembly がモデルの外を指しています: {assembly}")
            continue
        if not os.path.isfile(source):
            problems.append(f"{where} の STL がありません: models/{model}/{assembly}")
            continue
        data = _read_bytes(source)
        reason = _stl_problem(data)
        if reason:
            problems.append(f"{where} の {assembly} は STL として読めません（{reason}）")
            continue
        file_name = _safe_file_name(model, part_id)
        if file_name in seen_files:
            problems.append(f"{where} と {seen_files[file_name]} の書き出し先が同じです: {file_name}")
            continue
        seen_files[file_name] = part_id
        parts.append({
            "id": part_id, "label": label.strip(), "color": color, "kind": _part_kind(raw),
            "exterior": raw.get("exterior") is True, "file": file_name, "data": data,
        })
    return parts


def _load_part_names(model, root, ids, problems):
    """ユーザーの呼び名。{id: {"label": str|None, "aliases": [str]}}。ファイルが無ければ空。"""
    path = os.path.join(root, "models", model, "part-names.json")
    if not os.path.isfile(path):
        return {}
    where = f"models/{model}/part-names.json"
    data, _ = _read_json(path, problems, where)
    if data is None:
        return {}
    if not isinstance(data, dict):
        problems.append(f"{where} は {{部品id: {{label, aliases}}}} のオブジェクトにしてください")
        return {}
    names = {}
    for part_id, entry in data.items():
        if part_id not in ids:
            problems.append(f"{where} の {part_id} は manifest.json に無い部品です")
            continue
        if not isinstance(entry, dict):
            problems.append(f"{where} の {part_id} は {{label, aliases}} のオブジェクトにしてください")
            continue
        extra = sorted(set(entry) - {"label", "aliases"})
        if extra:
            problems.append(f"{where} の {part_id} に使えないキーがあります: {', '.join(extra)}")
            continue
        label = entry.get("label")
        if label is not None and not (isinstance(label, str) and label.strip()):
            problems.append(f"{where} の {part_id}.label は空でない文字列にしてください")
            continue
        aliases = entry.get("aliases", [])
        if not (isinstance(aliases, list) and all(isinstance(a, str) and a.strip() for a in aliases)):
            problems.append(f"{where} の {part_id}.aliases は空でない文字列の配列にしてください")
            continue
        names[part_id] = {
            "label": label.strip() if label else None,
            "aliases": list(dict.fromkeys(a.strip() for a in aliases)),
        }
    return names


def _legend_groups(model, root, ids, problems):
    """ui.json の legendGroups を [{label, color, members}] にする。無ければ None。"""
    path = os.path.join(root, "models", model, "build", "ui.json")
    if not os.path.isfile(path):
        return None
    where = f"models/{model}/build/ui.json"
    data, _ = _read_json(path, problems, where)
    raw_groups = data.get("legendGroups") if isinstance(data, dict) else None
    if not raw_groups:
        return None
    if not isinstance(raw_groups, list):
        problems.append(f"{where} の legendGroups は配列にしてください")
        return None
    groups, claimed = [], set()
    for index, group in enumerate(raw_groups):
        spot = f"{where} の legendGroups[{index}]"
        if not isinstance(group, dict) or not isinstance(group.get("label"), str) or not group["label"].strip():
            problems.append(f"{spot} には label が要ります")
            continue
        color = group.get("color")
        if color is not None and not (isinstance(color, str) and HEX_COLOR.match(color)):
            problems.append(f"{spot}.color は #rrggbb にしてください")
            color = None
        if isinstance(group.get("parts"), list):
            wanted = group["parts"]
        elif isinstance(group.get("prefix"), str) and group["prefix"]:
            wanted = [i for i in ids if i.startswith(group["prefix"])]
        else:
            problems.append(f"{spot} には parts（id の配列）か prefix（文字列）が要ります")
            continue
        unknown = [i for i in wanted if i not in ids]
        if unknown:
            problems.append(f"{spot} の部品 {', '.join(map(str, unknown))} が manifest.json にありません")
        # 部品は最初に載せた群へ入る（viewer/lattice と同じ）
        members = [i for i in wanted if i in ids and i not in claimed]
        if not members:
            problems.append(f"{spot}（{group['label']}）に該当する部品がありません")
            continue
        claimed.update(members)
        groups.append({"label": group["label"].strip(), "color": color, "members": members,
                       "hint": group.get("prefix") if isinstance(group.get("prefix"), str) else None})
    return groups


def _assign_groups(parts, legend, warnings):
    """部品ごとの群 id と、群の配列 [{id,label,color}] を返す。"""
    by_id = {p["id"]: p for p in parts}
    group_defs, group_of = [], {}
    taken = set()

    def add_group(base, label, color, members):
        gid = _unique(base, taken)
        taken.add(gid)
        first = by_id[members[0]]["color"] if members else None
        group_defs.append({"id": gid, "label": label, "color": color or first or DEFAULT_COLOR})
        for member in members:
            group_of[member] = gid

    if legend is not None:
        for number, group in enumerate(legend, 1):
            base = (re.sub(r"[_\d]+$", "", group["hint"]) if group["hint"] else "") \
                or _common_group_id(group["members"]) or f"group{number}"
            add_group(base, group["label"], group["color"], group["members"])
        leftovers = [p for p in parts if p["id"] not in group_of]
        for key, pick in (("jig", lambda p: p["kind"] == "jig"),
                          ("stock", lambda p: p["kind"] == "stock"),
                          ("shell", lambda p: p["exterior"]),
                          ("other", lambda p: True)):
            chosen = [p["id"] for p in leftovers if p["id"] not in group_of and pick(p)]
            if chosen:
                add_group(key, FIXED_GROUPS[key], None, chosen)
    else:
        counts = {}
        for p in parts:
            if "_" in p["id"] and "/" not in p["id"]:
                head = p["id"].split("_", 1)[0]
                counts[head] = counts.get(head, 0) + 1
        order, members = [], {}
        for p in parts:
            key = _prefix_group_key(p["id"], counts)
            if key is None:
                continue
            if key not in members:
                order.append(key)
                members[key] = []
            members[key].append(p["id"])
        for key in order:
            label = PREFIX_LABELS.get(key)
            if label is None:
                warnings.append(f"群 {key} の日本語名が未登録です（PREFIX_LABELS か ui.json の legendGroups に足してください）")
                label = key
            add_group(key, label, None, members[key])
        chosen = [p["id"] for p in parts if p["id"] not in group_of]
        if chosen:
            add_group("other", FIXED_GROUPS["other"], None, chosen)
    return group_defs, group_of


def build_ledger(model, root=ROOT):
    """台帳 dict と書き出す STL [(file, bytes)] と警告を返す。入力が壊れていれば PartsError。"""
    problems, warnings = [], []
    if not MODEL_RE.match(model) or not os.path.isdir(os.path.join(root, "models", model)):
        raise PartsError([f"モデル {model} が models/ にありません"])
    manifest = _load_manifest(model, root, problems)
    if manifest is None:
        raise PartsError(problems)
    parts = _validate_parts(model, manifest, problems)
    ids = [p["id"] for p in parts]
    names = _load_part_names(model, root, set(ids), problems)
    legend = _legend_groups(model, root, ids, problems)
    if problems:
        raise PartsError(problems)

    group_defs, group_of = _assign_groups(parts, legend, warnings)
    entries = []
    for p in parts:
        user = names.get(p["id"], {"label": None, "aliases": []})
        entry = {
            "id": p["id"],
            "label": user["label"] or p["label"],
            "systemLabel": p["label"],
            "group": group_of[p["id"]],
            "kind": p["kind"],
            "file": p["file"],
            "sha256": _sha256_bytes(p["data"]),
            "size": len(p["data"]),
            "aliases": user["aliases"],
        }
        if p["color"]:
            entry["color"] = p["color"]
        entries.append(entry)
    ledger = {
        "version": LEDGER_VERSION,
        "model": model,
        "source": f"models/{model}/build/manifest.json",
        "sourceSha256": manifest["sha256"],
        "groups": group_defs,
        "parts": entries,
    }
    return ledger, [(p["file"], p["data"]) for p in parts], warnings


def _same_file(path, data):
    try:
        return os.path.getsize(path) == len(data) and _read_bytes(path) == data
    except OSError:
        return False


def _write_temp(folder, name, data):
    os.makedirs(folder, exist_ok=True)
    handle, temp_path = tempfile.mkstemp(prefix=name + ".", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(handle, "wb") as fh:
            fh.write(data)
    except BaseException:
        os.unlink(temp_path)
        raise
    return temp_path


def write_parts(model, root=ROOT):
    """台帳と部品 STL を書く。返り値は (ledger, warnings)。一時ファイル → os.replace。"""
    ledger, stls, warnings = build_ledger(model, root)
    exports = os.path.join(root, "exports")
    ledger_dir = os.path.join(root, "viewer", "studio", "parts")
    ledger_path = os.path.join(ledger_dir, model + ".json")
    ledger_bytes = (json.dumps(ledger, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    previous = []
    if os.path.isfile(ledger_path):
        try:
            with open(ledger_path, "rb") as fh:
                old = json.loads(fh.read().decode("utf-8-sig"))
            previous = [p["file"] for p in old.get("parts", []) if isinstance(p, dict)
                        and isinstance(p.get("file"), str)]
        except (OSError, ValueError, UnicodeDecodeError):
            previous = []
    stale = [name for name in previous if name not in {f for f, _ in stls}
             and re.fullmatch(re.escape(model) + r"-part-[\w-]+\.stl", name)]

    temporary, ledger_temp = [], None
    try:
        for name, data in stls:
            final = os.path.join(exports, name)
            if not _same_file(final, data):
                temporary.append((_write_temp(exports, name, data), final))
        if not _same_file(ledger_path, ledger_bytes):
            ledger_temp = _write_temp(ledger_dir, model + ".json", ledger_bytes)
        for temp_path, final in temporary:
            os.replace(temp_path, final)
        temporary.clear()
        if ledger_temp is not None:
            os.replace(ledger_temp, ledger_path)
            ledger_temp = None
        for name in stale:
            try:
                os.unlink(os.path.join(exports, name))
            except FileNotFoundError:
                pass
    finally:
        for temp_path, _ in temporary:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        if ledger_temp is not None and os.path.exists(ledger_temp):
            os.unlink(ledger_temp)
    return ledger, warnings


def _all_models(root):
    base = os.path.join(root, "models")
    return sorted(name for name in os.listdir(base)
                  if os.path.isfile(os.path.join(base, name, "build", "manifest.json")))


def main(argv=None, root=ROOT):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    argv = sys.argv[1:] if argv is None else argv
    models = argv or _all_models(root)
    if not models:
        print("[studio-parts] build/manifest.json を持つモデルがありません", file=sys.stderr)
        return 2
    failed = False
    for model in models:
        try:
            ledger, warnings = write_parts(model, root)
        except PartsError as error:
            failed = True
            print(f"[studio-parts] {model}: 入力に問題があります（{len(error.problems)} 件）", file=sys.stderr)
            for problem in error.problems:
                print(f"  - {problem}", file=sys.stderr)
            continue
        names = sum(1 for p in ledger["parts"] if p["label"] != p["systemLabel"])
        print(f"[studio-parts] {model}: 部品 {len(ledger['parts'])} / 群 {len(ledger['groups'])}"
              f" / ユーザーの呼び名 {names}")
        for warning in warnings:
            print(f"  警告: {warning}", file=sys.stderr)
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
