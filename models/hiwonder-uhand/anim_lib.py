"""uHand の動き（クリップ）の定義を読む・確かめる・時刻ごとの量に直す。bpy を使わない。

定義は anim/ に置く。
  anim/poses.json          名前つきの姿勢。量（kin.DOFS）の辞書。書かない量は 0
  anim/clips/<name>.json   クリップ。名前はファイル名
    {
      "description": "何をする動きか",
      "loop": true,                      繰り返す動きなら true（最初と最後の姿勢が同じであること）
      "keys": [
        {"t": 0.0, "pose": "open"},      t は秒。pose は poses.json の名前
        {"t": 0.5, "pose": "fist", "set": {"thumb": 0.4}, "ease": "smooth"}
      ]
    }
  ease はそのキーへ向かう区間の進み方: smooth（既定。ゆっくり出てゆっくり止まる）/ linear / in / out / hold
このほかに、量を 1 個ずつ 0 から 1（wrist は -1 から 1）へ動かすクリップ dof_<量> を自動で作る。
Unity では dof_ のクリップを層に分けて時刻で引くと、6 個の量を実行時に自由に決められる。
"""
import json
import os
import re

import kin

HERE = os.path.dirname(os.path.abspath(__file__))
ANIM = os.path.join(HERE, "anim")
FPS = 30
DOF_FRAMES = 30
EASES = ("smooth", "linear", "in", "out", "hold")
MAX_SECONDS = 30.0


def _ease(name, f):
    if name == "linear":
        return f
    if name == "in":
        return f * f
    if name == "out":
        return 1 - (1 - f) * (1 - f)
    if name == "hold":
        return 0.0 if f < 1.0 else 1.0
    return f * f * (3 - 2 * f)


def load_poses():
    with open(os.path.join(ANIM, "poses.json"), encoding="utf-8") as f:
        return json.load(f)


def _resolve(key, poses, errors, where):
    d = {k: rest for k, (_, _, rest) in kin.DOFS.items()}
    if "pose" in key:
        if key["pose"] not in poses:
            errors.append(f"{where}: 姿勢 {key['pose']!r} が poses.json に無い")
        else:
            d.update(poses[key["pose"]])
    d.update(key.get("set", {}))
    for k, v in d.items():
        if k not in kin.DOFS:
            errors.append(f"{where}: 量 {k!r} は無い（使えるのは {', '.join(kin.DOFS)}）")
            continue
        lo, hi, _ = kin.DOFS[k]
        if not isinstance(v, (int, float)) or not lo <= v <= hi:
            errors.append(f"{where}: {k} = {v!r} が範囲 {lo}〜{hi} の外")
    return {k: float(d[k]) for k in kin.DOFS if isinstance(d.get(k), (int, float))}


def load_clip(path, poses=None):
    """クリップを読み、(クリップ, 誤りの一覧) を返す。クリップの keys には量の辞書 dofs が入る。"""
    poses = load_poses() if poses is None else poses
    name = os.path.splitext(os.path.basename(path))[0]
    errors = []
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        return None, [f"{name}: JSON として読めない ({e})"]
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name) or name.startswith("dof_"):
        errors.append(f"{name}: ファイル名は英小文字・数字・_ で、dof_ で始めない")
    keys = raw.get("keys")
    if not isinstance(keys, list) or len(keys) < 2:
        return None, errors + [f"{name}: keys が 2 個以上要る"]
    if not raw.get("description"):
        errors.append(f"{name}: description が無い")
    out, prev = [], None
    for n, key in enumerate(keys):
        where = f"{name} keys[{n}]"
        t = key.get("t")
        if not isinstance(t, (int, float)):
            errors.append(f"{where}: t が数でない")
            continue
        if n == 0 and t != 0:
            errors.append(f"{where}: 最初の t は 0")
        if prev is not None and t <= prev:
            errors.append(f"{where}: t が前のキーより後でない")
        prev = t
        ease = key.get("ease", "smooth")
        if ease not in EASES:
            errors.append(f"{where}: ease {ease!r} は無い（{', '.join(EASES)}）")
        extra = set(key) - {"t", "pose", "set", "ease"}
        if extra:
            errors.append(f"{where}: 知らない項目 {sorted(extra)}")
        out.append(dict(t=float(t), ease=ease, dofs=_resolve(key, poses, errors, where)))
    if out and out[-1]["t"] > MAX_SECONDS:
        errors.append(f"{name}: 長さが {MAX_SECONDS} 秒を超える")
    loop = bool(raw.get("loop", False))
    if loop and out and any(abs(out[0]["dofs"].get(k, 0) - out[-1]["dofs"].get(k, 0)) > 1e-6 for k in kin.DOFS):
        errors.append(f"{name}: loop なのに最初と最後の姿勢が違う")
    return dict(name=name, description=raw.get("description", ""), loop=loop, keys=out), errors


def dof_clips():
    """量を 1 個ずつ端から端まで等速で動かすクリップ。"""
    out = []
    for k, (lo, hi, rest) in kin.DOFS.items():
        base = {d: r for d, (_, _, r) in kin.DOFS.items()}
        out.append(dict(name=f"dof_{k}", description=f"{k} だけを {lo} から {hi} へ等速で動かす（実行時に時刻で引く用）",
                        loop=False, keys=[dict(t=0.0, ease="linear", dofs={**base, k: lo}),
                                          dict(t=DOF_FRAMES / FPS, ease="linear", dofs={**base, k: hi})]))
    return out


def load_all():
    """(クリップの一覧, 誤りの一覧)。dof_ のクリップを先頭に、あとは名前順。"""
    poses = load_poses()
    clips, errors = dof_clips(), []
    d = os.path.join(ANIM, "clips")
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json"):
            clip, err = load_clip(os.path.join(d, fn), poses)
            errors += err
            if clip and not err:
                clips.append(clip)
    return clips, errors


def sample(clip, t):
    keys = clip["keys"]
    if t <= keys[0]["t"]:
        return dict(keys[0]["dofs"])
    for a, b in zip(keys, keys[1:]):
        if t <= b["t"]:
            f = _ease(b["ease"], (t - a["t"]) / (b["t"] - a["t"]))
            return {k: a["dofs"][k] + (b["dofs"][k] - a["dofs"][k]) * f for k in kin.DOFS}
    return dict(keys[-1]["dofs"])


def frame_count(clip):
    return int(round(clip["keys"][-1]["t"] * FPS))


def frames(clip):
    """フレーム 0 から最後までの量の辞書の列。"""
    return [sample(clip, n / FPS) for n in range(frame_count(clip) + 1)]
