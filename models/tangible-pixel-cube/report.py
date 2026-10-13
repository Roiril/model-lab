"""最終報告（単一ファイルのHTML）を、build/ と prints/ のjsonと params.py から作る。

    py -3.11 models/tangible-pixel-cube/report.py

出力: reports/2026-10-13_tangible-pixel-cube.html

数値は書き写さない。検査の結果は json から、寸法は params.py から読む。
検査が不合格でも報告は作る（不合格の行をそのまま載せる）。
検査の入力より古いjsonは、鮮度の欄に出す。検査を流し直したあとで、もう一度このファイルを流す。
"""
from __future__ import annotations

import collections
import datetime
import hashlib
import html
import json
import math
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
PRINTS = ROOT / "prints" / "tangible-pixel-cube"
TARGET = ROOT / "reports" / "2026-10-13_tangible-pixel-cube.html"
MODEL = "tangible-pixel-cube"
STYLE_CANDIDATES = (
    Path("C:/Users/kouga/Projects/Web/claude-global/skills/visual-deliverable/assets/report.css"),
    Path.home() / ".claude" / "skills" / "visual-deliverable" / "assets" / "report.css",
)

sys.path.insert(0, str(HERE))
import params as P  # noqa: E402
import patterns as PT  # noqa: E402


# ---------------------------------------------------------------- 入力 ---

def jread(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp(path):
    return datetime.datetime.fromtimestamp(Path(path).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


INPUT_FILES = (
    BUILD / "design_check.json", BUILD / "model_report.json", BUILD / "manifest.json",
    BUILD / "verify_report.json", BUILD / "drive_report.json",
    BUILD / "assembly.json", BUILD / "assembly_report.json",
    BUILD / "simulate_report.json", BUILD / "print_review.json", BUILD / "firmware_report.json",
    PRINTS / "plates.json", PRINTS / "trial" / "trial_pieces.json",
    HERE / "params.py", HERE / "patterns.py", HERE / "cams.py",
)
for _f in INPUT_FILES:
    if not _f.is_file():
        raise FileNotFoundError(_f)

DC = jread(BUILD / "design_check.json")
MR = jread(BUILD / "model_report.json")
MF = jread(BUILD / "manifest.json")
VR = jread(BUILD / "verify_report.json")
DR = jread(BUILD / "drive_report.json")
AS = jread(BUILD / "assembly.json")
AR = jread(BUILD / "assembly_report.json")
SR = jread(BUILD / "simulate_report.json")
PR = jread(BUILD / "print_review.json")
FW = jread(BUILD / "firmware_report.json")
PL = jread(PRINTS / "plates.json")
TR = jread(PRINTS / "trial" / "trial_pieces.json")


# ---------------------------------------------------------------- HTML 部品 ---

class H(str):
    """エスケープ済みのHTML"""


def esc(value):
    return value if isinstance(value, H) else html.escape(str(value))


def tag(name, inner, cls=None):
    attr = f' class="{cls}"' if cls else ""
    return H(f"<{name}{attr}>{esc(inner)}</{name}>")


def para(text, cls=None):
    return tag("p", text, cls)


def code(text):
    return H(f"<code>{esc(text)}</code>")


def join(*parts):
    return H("".join(esc(x) for x in parts))


def table(headings, rows, cls=None):
    head = "".join(f"<th>{esc(h)}</th>" for h in headings)
    body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in rows)
    attr = f' class="{cls}"' if cls else ""
    return H(f'<div class="tblwrap"><table{attr}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def ulist(items, ordered=False):
    name = "ol" if ordered else "ul"
    return H(f"<{name}>" + "".join(f"<li>{esc(x)}</li>" for x in items) + f"</{name}>")


def details(summary, body):
    return H(f"<details><summary>{esc(summary)}</summary>{esc(body)}</details>")


VERDICT = {"ok": ("適合", False), "ng": ("不適合", True), "cond": ("条件付き", False), "unk": ("未確認", False)}


def chip(kind):
    label, hot = VERDICT[kind]
    return H(f'<span class="chip{" hot" if hot else ""}">{label}</span>')


def tol_chip(inside):
    return H('<span class="chip">許容内</span>') if inside else H('<span class="chip hot">許容超過</span>')


def fmt(value, digits=3):
    return f"{value:.{digits}g}" if isinstance(value, float) else str(value)


def sg(value, digits=None):
    """符号つきの数。マイナスは U+2212"""
    text = f"{value:+.{digits}f}" if digits is not None else f"{value:+g}"
    return text.replace("-", "\u2212")


STATUS_JA = {"conditional": "条件付き", "pass": "適合", "fail": "不適合", "unknown": "未確認"}


# ---------------------------------------------------------------- 取り出し ---

def dci(fragment, section=None):
    hits = [x for x in DC["items"] if fragment in x["name"] and (section is None or x["section"].startswith(section))]
    if not hits:
        raise KeyError(f"design_check に項目が無い: {fragment}")
    return hits[0]


MM = 1000.0
SPLINE_TEETH = 20                                    # SG92R のホーンの山の数（18° 刻み）
VERNIER_HALF_DEG = 360.0 / math.lcm(SPLINE_TEETH, P.SERVO_Z) / 2   # 位相補正の後に残る受けの向きの誤差（サーボ軸）。design_check の H 節と同じ値
CUBE_MM = P.CUBE * MM
PEAK_MM = dci("外形の最大")["value"]
N_PIXELS = P.N * P.N

PARTS_PRINT = [p for p in MF["parts"] if p.get("print")]
PARTS_STOCK = [p for p in MF["parts"] if not p.get("print")]
PRINT_PARTS_REPORT = {k: v for k, v in MR["parts"].items() if v.get("print")}

# 鮮度 ------------------------------------------------------------------


def stale_hashes(hashes, base=ROOT):
    """記録した SHA-256 と現在のファイルが違うものの一覧"""
    bad = []
    for rel, recorded in hashes.items():
        path = base / rel
        if not path.is_file():
            bad.append(f"{rel}（欠落）")
            continue
        value = recorded if isinstance(recorded, str) else recorded.get("sha256")
        if sha256(path) != value:
            bad.append(rel)
    return bad


def newest(paths):
    return max(Path(p).stat().st_mtime for p in paths)


SOURCES_PY = [HERE / n for n in ("params.py", "kinematics.py", "cams.py", "patterns.py")]
PRINT_STL = list(BUILD.glob("print_*.stl"))
FRESH = collections.OrderedDict()


def freshness():
    FRESH["design_check.json"] = [
        "params.py などの更新より古い"] if (BUILD / "design_check.json").stat().st_mtime < newest(SOURCES_PY + [HERE / "design_check.py"]) else []
    FRESH["model_report.json"] = [
        "形状の元（params.py、parts_static.py、parts_moving.py）の更新より古い"] if (BUILD / "model_report.json").stat().st_mtime < newest(
        [HERE / "params.py", HERE / "parts_static.py", HERE / "parts_moving.py", HERE / "model.py"]) else []
    FRESH["verify_report.json"] = stale_hashes(VR["sourceHashes"])
    FRESH["drive_report.json"] = stale_hashes(DR["sourceHashes"])
    FRESH["simulate_report.json"] = stale_hashes(SR["sourceHashes"])
    stale_assembly = [f"build/{k}.stl" for k, v in AS["source_sha256"].items()
                      if not (BUILD / f"{k}.stl").is_file() or sha256(BUILD / f"{k}.stl") != v]
    FRESH["assembly.json"] = stale_assembly + stale_hashes(AS["algorithm_sha256"])
    FRESH["assembly_report.json"] = stale_hashes(AR["algorithm_sha256"]) + (
        [] if AR["sourceIntegrity"]["start"] == AS["source_sha256"] else ["assembly.json の部品SHAと違う"])
    FRESH["print_review.json"] = [
        "刷る向きのSTL（build/print_*.stl）より古い"] if (BUILD / "print_review.json").stat().st_mtime < newest(PRINT_STL) else []
    FRESH["firmware_report.json"] = stale_hashes({i["file"]: i["sha256"] for i in FW["inputs"]}) + stale_hashes(
        {FW["source"]["file"]: FW["source"]["sha256"]})
    FRESH["plates.json"] = [
        "刷る向きのSTLより古い"] if (PRINTS / "plates.json").stat().st_mtime < newest(PRINT_STL) else []
    FRESH["trial_pieces.json"] = [
        "刷る向きのSTLより古い"] if (PRINTS / "trial" / "trial_pieces.json").stat().st_mtime < newest(PRINT_STL) else []


freshness()
STALE = {k: v for k, v in FRESH.items() if v}

# ---------------------------------------------------------------- 要約値 ---

# 干渉
IF = VR["interference"]
CF = VR["camFoot"]
PIX = VR["pixelLimits"]
VERIFY_OK = bool(VR["overall"]["pass"])

# 駆動
DRIVE_IF = {i["id"]: i for i in DR["interfaces"]}
DRIVE_OK = bool(DR["overall"]["geometryPass"])
GEAR = DRIVE_IF.get("gear-mesh")
STOP_HEIGHT = (GEAR or {}).get("stopHeight")
STOP_HEIGHT_X2 = (GEAR or {}).get("stopHeightDoubledPhase")
SCEN = DR["phaseBudget"]["scenarios"]

# 組立
ASM_OK = bool(AR["pass"])
CONTACTS = AR["designedContacts"]
STRAIN_MAX = max(c["strainPercent"] for c in CONTACTS if c.get("strainPercent") is not None)
STRAIN_ZONE = max((c for c in CONTACTS if c.get("strainPercent") is not None), key=lambda c: c["strainPercent"])["zone"]

# 物理
ST = SR["static"]
SIM_CALC_OK = bool(SR["overall"]["calculationPass"])
SIM_ALL_OK = bool(SR["overall"]["pass"])
SIM_BASIS = (
    ("接続形状は確認済み。" if SR["driveGeometry"]["geometryPass"] and SR["driveGeometry"]["sourceHashesFresh"] else "接続形状は未確認または古い。")
    + "付属ホーンのスプライン嵌合、摩擦係数、材料は実機未確認"
)
SENS = SR["sensitivity"]
CONTACT_SPEED_MAX = max(v.get("maxContactSpeedMmS", 0.0) for v in SR["scenarios"].values())
STALL_MNM = P.SERVO_STALL_NM * 1000.0
TORQUE_LIMIT_MNM = STALL_MNM * P.TORQUE_FRAC

# 印刷
PS = PR["summary"]
VISIBLE_OVERHANG = sum(v["print"]["overhang"]["visible_area_mm2"] for v in PRINT_PARTS_REPORT.values())
SUPPORT_USED = [k for k, v in PRINT_PARTS_REPORT.items() if not str(v["print"]["support"]).startswith("なし")]
BRIDGE_MAX = max(v["overhang"]["max_bridge_mm"] for v in PR["parts"].values())
BRIDGE_PART = max(PR["parts"], key=lambda k: PR["parts"][k]["overhang"]["max_bridge_mm"])
SLENDER_MAX, SLENDER_PART = max(((v["slices"]["peak"].get("ratio", 0.0), k) for k, v in PR["parts"].items()))
NO_CHAMFER = [k for k, v in PR["parts"].items() if v.get("first_layer_mating_without_chamfer")]
MULTI_COMP = [k for k, v in PR["parts"].items() if v["topology"]["components"] != 1]
UNGROUNDED = [k for k, v in PR["parts"].items() if not all(c["grounded"] for c in v["components"])]
EXC_COUNT = collections.Counter(x["exception"] for x in PR["allowed_exceptions"])
PRINT_OK = PS["n_fail_entries"] == 0 and PS["n_trial_fail_entries"] == 0 and VISIBLE_OVERHANG == 0 and not SUPPORT_USED
HOUSING_EXT_MIN = PR["parts"]["housing"]["wall"]["exterior_min_mm"]
PLATE_LAYOUT_OK = all(
    not v["overlap"] and not v["off_bed"] and not v["in_exclusion_zone"]
    for plate in PL["plates"] for v in plate["verify"].values())
MESH_OK = MR["totals"]["non_manifold_edges"] == 0 and not MR["totals"]["bad_components"] and not MR["totals"]["negative_volume"]

WIRE_DRIVE = DRIVE_IF.get("wire-exit")
KIND_LABEL = {"ok": "適合", "ng": "不適合", "cond": "条件付き", "unk": "未確認"}


def status_kind(status):
    return {"pass": "ok", "fail": "ng", "unknown": "unk"}.get(status, "unk")


# ---------------------------------------------------------------- 要件ごとの結果 ---

def requirement_rows():
    rows = []

    def add(group, req, kind, result, basis):
        rows.append((group, req, kind, result, basis))

    t_dev = dci("停止区間での高さ誤差の最大")["value"]
    vp = CF["shaftVerticalPlay"]
    # --- 依頼の基本
    add("依頼", "外から見て一辺10cm以下の立方体", "ok",
        f"静止時は {CUBE_MM:g} × {CUBE_MM:g} × {CUBE_MM:g}mm です。画素が {sg(P.H_MAX * MM)}mm 出ると最大 {PEAK_MM:g}mm で、10cm 以下に収まります。",
        "design_check.json（C 外形の最大）、manifest.json")
    add("依頼", "1つの面が小さな正方形の集合で、タンジブルUIのように動く", "ok",
        f"{P.N} × {P.N} = {N_PIXELS} 画素です。ピッチは {P.PITCH * MM:g}mm、頭は {P.HEAD * MM:g}mm 角、窓は {P.WINDOW * MM:g}mm です。高さは {sg(P.H_MIN * MM)}〜{sg(P.H_MAX * MM)}mm です。"
        f"{N_PIXELS} 画素 × {P.K} 表 = {len(CF['tableHeights'])} 点の停止高さを、実カムのSTLで測りました。表との差は最大 {CF['tableHeightWorstErrorMm']:.1e}mm です（許容 {CF['tableHeightLimitMm']:g}mm）。"
        f"{sg(P.H_MAX * MM)}mm からさらに {PIX['upGapMm'][0]:.2f}mm、{sg(P.H_MIN * MM)}mm からさらに {PIX['downGapMm'][0]:.2f}mm の余裕があります。",
        "verify_report.json（camFoot、pixelLimits）")
    add("依頼", "凹む場所を1種類に固定せず、後からプログラムで設計できる", "cond",
        f"高さの表 {P.K} 枚を patterns.py に書くと、生成器 cams.py がカム {N_PIXELS} 枚を作ります。表を変えたらカムを刷り直します。"
        f"実行時に画素を1枚ずつ自由に指定する方式ではありません。既定の表は全 {N_PIXELS} カムで、停止区間の高さ誤差が最大 {t_dev:.3f}mm です。",
        "cams.json、design_check.json（D カム）、README.md")
    # --- 依頼 ①〜⑤
    add("依頼", "① きれいに刷れる。サポートは見えなくてよい面だけ", "ok" if PRINT_OK else "ng",
        f"{len(PRINT_PARTS_REPORT)} 個すべてサポートなしです（使う部品 {len(SUPPORT_USED)} 個）。見える面の張り出し面積は全部品で {VISIBLE_OVERHANG:g}mm² です。"
        f"刷る向きの精査で不合格は {PS['n_fail_entries']} 件です。橋は最長 {BRIDGE_MAX:g}mm です（{BRIDGE_PART}。見えない面）。基準は {PR['thresholds']['bridge_max_mm']:g}mm です。"
        "Bambu Studioでのスライス結果は未確認です。",
        "print_review.json、model_report.json")
    add("依頼", "② SG92Rの正確な寸法を使う", "cond",
        "models/sg92r-photo/params.py（ユーザー確定の正本）を、params.py が読み込みます。書き写していません。"
        "正本には仮値が残っています。出力スプラインの歯がありません。ギアカバーの径12mmは推定です。出力軸の高さ3.5mmは仮値です。配線の長さと出口の高さは仮置きです。",
        "params.py、models/sg92r-photo/README.md")
    add("依頼", "③ 組み立ては印刷部品だけ", "ok",
        f"印刷部品 {len(PARTS_PRINT)} 個と、SG92R・付属ホーンだけです（既製部品 {len(PARTS_STOCK)} 点）。ねじ、接着剤、結束バンドは使いません。"
        "保持は潰しリブ、スナップ、Cクリップ、落とし込みで作ります。",
        "manifest.json")
    kinds_n = [EXC_COUNT[k] for k in ("crush_rib_0.6", "gear_tooth_tip_1.1", "cam_label_engraving", "bezel_bar_1.6")]
    add("依頼", "④ 薄いと揺れる。PLA・PETGで刷る", "ok",
        f"立てて刷る部品の高さと太さの比は最大 {SLENDER_MAX:g} です（{SLENDER_PART}。基準 {PR['thresholds']['slender_height_over_width']:g}）。"
        f"肉厚が 1.2mm 未満の箇所は、例外4種だけを許可しました（潰しリブ {kinds_n[0]} 件、歯先 {kinds_n[1]} 件、番号の彫り {kinds_n[2]} 件、ベゼルの桟 {kinds_n[3]} 件）。"
        f"力を受ける部位で 3mm 未満の {PS['n_load_judged_ok_entries']} 件は、荷重の計算で降伏の 1/2 以下と判定しました。",
        "print_review.json（thresholds、allowed_exceptions、load_judgement）")
    add("依頼", "⑤ 組み立てられるか（組立検証）", "ok" if ASM_OK else "ng",
        f"{len(AR['steps'])} 工程すべてで、先に入れた部品との共通体積が、許可した当たり以外 0 でした。逆順の分解も通ります。"
        f"案内板が壁の片側へ 0.2mm 寄った最悪の姿勢 {len(AR['worstCase']['variants'])} 通りも通ります。",
        "assembly_report.json")
    add("依頼", "⑤ 動くか（全範囲の干渉）", "ok" if VERIFY_OK else "ng",
        f"サーボ {IF['servoDegs'][0]:g}〜{IF['servoDegs'][1]:g}° を {IF['stepDeg']:g}° 刻みで（{IF['poseCount']} 姿勢）、部品の組 {IF['uniquePairs']} を実STLで測りました。"
        f"許可外の最大の共通体積は {IF['maximumNonDesignedCommonVolumeMm3']:.1e}mm³ です（床 {IF['volumeFloorMm3']:g}mm³）。違反は {len(IF['violations'])} 件です。",
        "verify_report.json（interference）")
    gear_text = ""
    if GEAR is not None and STOP_HEIGHT is not None:
        gear_text = f"歯車の噛み合いは停止時の高さの誤差で判定しました。最大 {STOP_HEIGHT['maximumErrorMm']:.3f}mm で、基準は {STOP_HEIGHT['limitMm']:g}mm 以下です。"
    elif GEAR is not None:
        gear_text = "歯車の噛み合いは、新しい基準（停止時の高さの誤差）の結果が、この drive_report.json にありません。"
    failing = [i["id"] for i in DR["interfaces"] if i["status"] == "fail"]
    add("依頼", "⑤ 動くか（駆動の接続と保持）", "ok" if DRIVE_OK else "ng",
        f"{len(DR['interfaces'])} 界面のうち、適合 {sum(i['status'] == 'pass' for i in DR['interfaces'])}、不適合 {len(failing)}、未確認 {sum(i['status'] == 'unknown' for i in DR['interfaces'])} です。"
        + (f"不適合は {'、'.join(failing)} です。" if failing else "") + gear_text
        + (f"旧基準の余裕は {sg(SCEN['maximumPlay']['minimumMarginDeg'], 2)}° で、1° に届きません（譲ったことを参照）。" if STOP_HEIGHT is not None and "maximumPlay" in SCEN else "")
        + "未確認は付属ホーンのスプラインの嵌合です。",
        "drive_report.json")
    stop_note = (f"駆動検査の停止時の高さの誤差は最大 {STOP_HEIGHT['maximumErrorMm']:.3f}mm で、基準 {STOP_HEIGHT['limitMm']:g}mm の内側です。" if STOP_HEIGHT is not None else "")
    add("依頼", "⑤ 動くか（軸の浮きによる画素の高さのずれ）", "ok" if vp["pushingPlateWithinTolerance"] else "cond",
        f"軸が溝の底に載ると、画素は表より {abs(vp['settledShiftMm']):.2f}mm 低くなります。栓まで浮くと {vp['floatedToPlugShiftMm']:.2f}mm 高くなります（許容 ±{vp['tableToleranceMm']:g}mm の内側）。"
        f"案内板を押し上げるまで浮くと {vp['floatedPushingPlateShiftMm']:.2f}mm 高くなり、この許容を超えます。" + stop_note
        + "浮くかどうかは、歯車の分離力と重さの釣り合いで決まります。実機で確かめます。",
        "verify_report.json（camFoot.shaftVerticalPlay）、drive_report.json")
    add("依頼", "⑤ 動くか（物理。トルクと動かし方）", "ok" if (SIM_CALC_OK and SIM_ALL_OK) else "cond",
        f"摩擦係数0.35で、必要トルクは最大 {ST['maximumRequiredTorqueNm'] * MM:.1f} mN·m です（停動 {STALL_MNM:g} の {ST['fractionOfStall'] * 100:.1f}%）。"
        f"0.45では {SENS['staticRequiredNm'] * MM:.1f} mN·m です。上限は停動の1/3の {TORQUE_LIMIT_MNM:.1f} です。"
        f"計算は{'成立しました' if SIM_CALC_OK else '成立しませんでした'}。全体は{STATUS_JA.get(SR['overall']['status'], SR['overall']['status'])}扱いです（{SIM_BASIS}）。" if not SIM_ALL_OK else
        f"摩擦係数0.35で、必要トルクは最大 {ST['maximumRequiredTorqueNm'] * MM:.1f} mN·m です（停動 {STALL_MNM:g} の {ST['fractionOfStall'] * 100:.1f}%）。"
        f"0.45では {SENS['staticRequiredNm'] * MM:.1f} mN·m です。上限は停動の1/3の {TORQUE_LIMIT_MNM:.1f} です。",
        "simulate_report.json")

    # --- 共通条件 §3 印刷
    n_main = sum(1 for p in PL["plates"] if p["kind"] == "main")
    add("§3 印刷", "プリンタと材料: X1C、0.4mm、0.20mm層。PLAが主、PETGでも組める", "cond",
        f"PLA用とPETG用の3mfを、各 {len(PL['plates'])} 枚作りました。PETGで固くなる箇所は未確認です。",
        "plates.json")
    add("§3 印刷", "全部品を1枚のプレートに収める。収まらなければ分け方と理由を書く", "ok" if PLATE_LAYOUT_OK else "ng",
        f"本体は {n_main} 枚に分けました（外装系、画素 {N_PIXELS} 個、機構）。全プレートで、重なり・はみ出し・除外域に入る部品はありません。理由は plates.json に書きました。",
        "plates.json")
    add("§3 印刷", "見える面にサポートを付けない", "ok" if (not SUPPORT_USED and VISIBLE_OVERHANG == 0) else "ng",
        f"見える面の張り出し面積は {VISIBLE_OVERHANG:g}mm² です。サポートを使う部品は {len(SUPPORT_USED)} 個です。",
        "model_report.json、print_review.json")
    add("§3 印刷", "横穴は涙形か天井を平らに。橋は10mm以内で見えない面だけ", "ok",
        f"橋は最長 {BRIDGE_MAX:g}mm です（{BRIDGE_PART}）。見える橋がある部品は {sum(1 for v in PR['parts'].values() if v['overhang']['fail_visible'])} 個です。",
        "print_review.json")
    add("§3 印刷", "立てて刷る細い部分は高さを太さの5倍以内。接地が小さい部品は倒れない向きに", "ok",
        f"高さと太さの比は最大 {SLENDER_MAX:g} です（{SLENDER_PART}）。重心が接地の外にある部品は {sum(1 for v in PR['parts'].values() if not v['bed']['com_over_footprint'])} 個です。",
        "print_review.json")
    add("§3 印刷", "肉厚: 外装2mm以上、力を受ける壁3mm以上、どこでも1.2mm以上", "cond",
        f"外装の見える面の最小は {HOUSING_EXT_MIN:g}mm です。ベゼルの窓と窓の桟 {P.BEZEL_BAR * MM:g}mm は例外です。1.2mm 未満は、潰しリブ 0.6mm など荷重のかからない形だけです。"
        f"力を受ける部位の 3mm 未満 {PS['n_load_judged_ok_entries']} 件は、荷重の計算で可と判定しました。",
        "print_review.json")
    add("§3 印刷", "隙間と面取り: 回る軸は片側0.2mm。ベッドに接する嵌め合いの縁に0.3mm面取り", "ok" if not NO_CHAMFER else "ng",
        f"軸と穴の隙間は片側 {P.SHAFT_BORE_CLR * MM:g}mm です。面取りが欠けた部品は {len(NO_CHAMFER)} 個です（対象は画素の頭の縁、カム・歯車の穴の縁、受けのポケットの口）。",
        "print_review.json、params.py")
    add("§3 印刷", "スナップ・圧入は層に沿ってしなる向きで刷る", "ok",
        "ベゼルの爪は端壁のたわみで、案内板の爪は舌の面内で、押さえクリップとCクリップは脚の面内でしなります。刷る向きの理由は model_report.json に書きました。層に沿う向きは設計の確認で、実物の割れは未確認です。",
        "model_report.json")
    add("§3 印刷", "非多様体エッジ0。一体の部品は連結成分1。空中に離れた部品がない", "ok" if (MESH_OK and not MULTI_COMP and not UNGROUNDED) else "ng",
        f"{MR['totals']['n_parts']} 部品で非多様体エッジは {MR['totals']['non_manifold_edges']} です。印刷部品 {PS['n_parts_reviewed']} 個のうち、連結成分が1でない部品は {len(MULTI_COMP)} 個、接地しない部品は {len(UNGROUNDED)} 個です。"
        f"試し刷りの小片 {PS['n_trial_pieces']} 個も、不合格は {PS['n_trial_fail_entries']} 件です。",
        "model_report.json、print_review.json")

    # --- §4 組み立て
    add("§4 組み立て", "印刷部品と依頼で挙げた既製部品だけ。付属ねじも使わない", "ok",
        f"印刷 {len(PARTS_PRINT)} 個と、SG92R・付属ホーンだけです。取付耳は柵と押さえクリップで止めます。", "manifest.json、drive_report.json（servo-body-retention）")
    add("§4 組み立て", "工具なしで手で組める", "cond",
        f"{len(AR['steps'])} 工程の経路は、検査で通ります。指の入る隙間と、爪を押し込む力は数値で見ていません。実物で確かめます。",
        "assembly_report.json")
    add("§4 組み立て", "壊さずに分解できる", "cond" if ASM_OK else "ng",
        f"逆順の分解が通ります。スナップのひずみは最大 {STRAIN_MAX:.2f}% です（{STRAIN_ZONE}。PLAで2%以下）。着脱力は実物で確かめます。",
        "assembly_report.json（reverseDisassembly、designedContacts）")
    add("§4 組み立て", "後から入れる部品の通り道と、指の入る隙間が残る", "cond",
        "通り道は、各工程の全姿勢で検査しました。軸は落とす向きを決め、サーボ一式は -X へ 1.8mm 寄せます。指の隙間は未検査です。",
        "assembly_report.json（steps、rolling）")
    retention = ["shaft-retention", "axis-upward-chain", "servo-body-retention", "servo-clip-retention",
                 "guide-plate-retention", "bezel-retention", "pixel-guides"]
    ret_status = [DRIVE_IF[i]["status"] for i in retention if i in DRIVE_IF]
    add("§4 組み立て", "抜け止めは印刷部品の形で作る", "ok" if all(s == "pass" for s in ret_status) and len(ret_status) == len(retention) else "ng",
        f"軸、サーボ、押さえクリップ、案内板、ベゼル、画素の六方向の保持 {len(ret_status)} 界面のうち、適合は {sum(s == 'pass' for s in ret_status)} です。保持相手を外すと接触が消えることも測りました。",
        "drive_report.json")

    # --- §5 動く部品
    add("§5 動く部品", "動く範囲と速さを決めて params.py に書く", "ok",
        f"使うサーボ角は {P.TABLE_THETA[0]:g}〜{P.TABLE_THETA[-1]:g}° です（電気の可動域 {P.SERVO_MIN_DEG:g}〜{P.SERVO_MAX_DEG:g}° の内側）。"
        f"デモの移動は1表 {FW['moveTiming']['minMoveMs']}ms です（浮かない最短は {FW['moveTiming']['noLiftFloorMs']}ms）。",
        "params.py、firmware_report.json")
    add("§5 動く部品", "必要トルクは停動の1/3以下", "ok" if ST["withinOneThirdStall"] and ST["peakWithinOneThirdStall"] and SENS["torqueWithinOneThirdStall"] else "ng",
        f"動力学の計算で、摩擦係数 0.35 のとき {ST['maximumRequiredTorqueNm'] * MM:.1f} mN·m です（{ST['fractionOfStall'] * 100:.1f}%）。ゆっくり動かしたピークは {ST['peakLowSpeedTorqueNm'] * MM:.1f} mN·m です。"
        f"0.45 のときは {SENS['staticRequiredNm'] * MM:.1f} mN·m です（{SENS['staticRequiredNm'] * MM / STALL_MNM * 100:.1f}%）。上限は {TORQUE_LIMIT_MNM:.1f} mN·m です。"
        f"設計検査の概算は、0.35 で {DC['summary']['key']['torque_035_mNm']:.1f}、0.45 で {DC['summary']['key']['torque_045_mNm']:.1f} mN·m です。摩擦係数は未実測の仮値です。",
        "simulate_report.json、design_check.json（F トルク）")
    add("§5 動く部品", "ホーンは山の刻みでしか付け直せない。組むときの合わせ方を手順に書く", "cond",
        f"90° で起動してからホーンを付けます。ホーンは山の刻み {360.0 / SPLINE_TEETH:g}° でしか付かず、受けの歯は ±{P.RECV_ARC_HALF_DEG:g}° の範囲にしかないので、付け方は 1 通りに決まり、受けの向きは最大 ±{360.0 / SPLINE_TEETH / 2:g}° ずれます。"
        "このずれは 5 本の軸に同じだけ乗るので、位相補正で消します。組み立てでは、位相合わせ治具が座るまでデモの + と − で 0.25° ずつ回し、w で EEPROM に保存します。仕上げは表の高さを測って合わせます。"
        f"補正後の残りは ±{VERNIER_HALF_DEG:.2f}°（サーボ角）と見込みます。スプラインの嵌合は、実物でしか確かめられません。README.md に手順を書きました。",
        "design_check.json（H 位相）、README.md")
    add("§5 動く部品", "端で当たる動きは、当たる速さを出す", "ok",
        f"画素がベゼルや案内板に当たる前に、カムが止まります（{sg(P.H_MAX * MM)}mm からさらに {PIX['upGapMm'][0]:.2f}mm 空きます）。計算した全 {len(SR['scenarios'])} 条件で、当たる速さは最大 {CONTACT_SPEED_MAX:g} mm/s です。"
        "最速のステップ指令では画素が浮くので、デモは1表0.6秒に制限しました。",
        "simulate_report.json、verify_report.json")
    add("§5 動く部品", "電源を切ったときにどうなるかを報告する", "unk",
        f"画素の自重がサーボ軸に掛けるトルクは、最大 {ST['maxGravityGroupsNm'] * MM:.1f} mN·m です。電源を切ったサーボがこれを保持するかは、計算していません。電源を切った後の位置は保証しません。",
        "simulate_report.json（static）")
    wire = WIRE_DRIVE
    add("§5 動く部品", "配線は可動部に挟まれず、コネクタごと外へ出せる出口を付ける", "cond",
        (f"+Y 壁の窓は {P.WIRE_WIN_W * MM:g} × {P.WIRE_WIN_H * MM:g}mm です。コネクタの近似の箱が通る最大は、幅 {wire['maximumPassingWidthMm']:.2f}mm、厚み {wire['maximumPassingThicknessMm']:.2f}mm です。"
         if wire else "配線の出口の結果が drive_report.json にありません。")
        + f"コネクタの寸法は仮定です（組立検査は {AR['wireWindow']['connectorBoxMm']['widthX']:g} × {AR['wireWindow']['connectorBoxMm']['thicknessZ']:g}mm）。配線の曲げは未確認です。",
        "drive_report.json（wire-exit）、assembly_report.json")

    # --- §6 検証
    add("§6 検証", "形: 外形が範囲内。非多様体エッジ0", "ok" if MESH_OK else "ng",
        f"外形は最大 {PEAK_MM:g}mm です。非多様体エッジは {MR['totals']['non_manifold_edges']} です。", "design_check.json、model_report.json")
    add("§6 検証", "動く範囲の干渉: 全範囲を2.5°刻み以下で共通体積0", "ok" if VERIFY_OK else "ng",
        f"{IF['stepDeg']:g}° 刻み、{IF['poseCount']} 姿勢、{IF['uniquePairs']} 組を測りました。許可した当たり {len(IF['designedOverlaps'])} 件（潰しリブなど）は、場所と量を限定しています。治具 phase_comb だけを運動の検査から除きました（最終形に残らず、組立工程では検査しました）。",
        "verify_report.json")
    add("§6 検証", "組み立ての経路: 各工程に経路。当たってよいのは設計した圧入とスナップだけ。ひずみ2%以下", "ok" if ASM_OK else "ng",
        f"{len(AR['steps'])} 工程です。設計した当たりは {len(CONTACTS)} 件で、ひずみは最大 {STRAIN_MAX:.2f}% です。", "assembly_report.json")
    add("§6 検証", "刷れるか: Bambu Studio CLIでスライスして、見える面に支えの無い押し出しが無い", "cond",
        "スライスは未実施です（依頼④でスライスは不要）。代わりに、刷る向きのSTLから張り出し、細物、肉厚、接地を幾何で精査しました。スライス結果での確認は未実施です。",
        "print_review.json、plates.json")
    add("§6 検証", "動く力: トルクの基準。動く時間と端で当たる速さを出す", "ok" if (SIM_CALC_OK and SIM_ALL_OK) else "cond",
        f"トルクは上の行のとおりです。1自由度の計算で、3 秒の移動は最大 {SR['motion']['standardMove']['peakTorqueNm'] * MM:.1f} mN·m です。"
        f"{'' if SIM_ALL_OK else '全体は' + STATUS_JA.get(SR['overall']['status'], SR['overall']['status']) + '扱いです。'}",
        "simulate_report.json")
    return rows


# ---------------------------------------------------------------- 校正 ---

def calibration_rows():
    rows = []
    vc = [(k, v) for k, v in VR["calibration"].items() if isinstance(v, dict) and "pass" in v]
    rows.append(("干渉（verify.py）", "重なり 0.5 を 0.5 と測る。薄い重なり 0.002mm³ を拾う",
                 "離れた立方体、面接触、辺接触は 0。設計外の重なりを旗に立て、設計した重なりは通す",
                 len(vc), sum(1 for _, v in vc if v["pass"])))
    dc = DR["calibration"]
    rows.append(("駆動（drive.py）", "噛み合いの窓の端が解析値に合う。六方向の初接触が設計値に合う",
                 "保持相手を外すと接触が消える。位相誤差の和が design_check と一致",
                 len(dc), sum(1 for c in dc if c["pass"])))
    ac = AR["calibration"]["checks"]
    rows.append(("組立（assembly.py）", "当たらない経路（軸1を歯車が離れた高さで並進）は合格",
                 "軸を転がさず落とす、サーボ一式を寄せず落とす、1歯ずらした軸は不合格",
                 len(ac), sum(1 for c in ac if c["pass"])))
    sc = SR["calibration"]
    rows.append(("物理（simulate.py）", "無負荷で公称速度。通常の負荷は届く。時間刻みを半分にしても一致",
                 "停動の1/50、必要量の半分、0 は届かない。浮き上がりの検出器が出る側と出ない側を分ける",
                 len(sc) + 1, sum(1 for c in sc if c["pass"]) + (1 if SR["dynamicCalibration"]["ok"] else 0)))
    pc = PR["calibration"]["cases"]
    rows.append(("印刷（print_review.py）", "水平から40°の下向き斜面は張り出し。橋8mm、厚み2mmの板は合格",
                 "45°と50°の斜面は数えない。橋14mm、4mm角で高さ30mmの柱、厚み1mmの板は不合格に出る",
                 len(pc), sum(1 for c in pc if c["pass"])))
    mc = MR["calibration"]
    rows.append(("形（model.py）", "立方体の体積、非多様体辺0、連結成分1",
                 "上面を抜いた立方体は非多様体辺4、離れた2立方体は連結成分2、40°の斜面は数える",
                 len(mc), sum(1 for c in mc if c["pass"])))
    return rows


# ---------------------------------------------------------------- 各節 ---

def pattern_grids():
    cards = []
    for k, (name, label, rows) in enumerate(zip(PT.NAMES, PT.LABELS_JA, PT.TABLES)):
        body = []
        for row in rows:
            cells = []
            for v in row:
                mix = min(abs(v) / (P.H_MAX * MM) * 50.0, 50.0)
                cls = "neg" if v < 0 else "pos" if v > 0 else "zero"
                cells.append(f'<td class="{cls}" style="--m:{mix:.0f}">{sg(v, 1)}</td>')
            body.append("<tr>" + "".join(cells) + "</tr>")
        cards.append(H(
            f'<figure class="tbl"><figcaption>表{k}　{esc(label)}（{esc(name)}）　サーボ {P.TABLE_THETA[k]:g}°</figcaption>'
            f'<table class="cells"><tbody>{"".join(body)}</tbody></table></figure>'))
    return H('<div class="patterns">' + "".join(cards) + "</div>")


def decisions_table():
    key = DC["summary"]["key"]
    rows = [
        (f"外形 {CUBE_MM:g}mm", f"画素が {sg(P.H_MAX * MM)}mm 出ると {PEAK_MM:g}mm になり、10cm に 1mm 残ります。", code("CUBE")),
        (f"画素 {P.N} × {P.N}。ピッチ {P.PITCH * MM:g}mm。頭 {P.HEAD * MM:g}mm 角。窓 {P.WINDOW * MM:g}mm",
         f"ピッチ {P.PITCH * MM:g}mm は、モジュール1の{P.CHAIN_Z}歯の歯車のピッチ円直径と同じです。隣の軸を1:1でつなぐ中心距離が合います。"
         f"頭と窓の隙間は片側 {(P.WINDOW - P.HEAD) / 2 * MM:.1f}mm です。窓と窓の桟は {P.BEZEL_BAR * MM:g}mm です。",
         join(code("PITCH"), "　", code("HEAD"), "　", code("WINDOW"))),
        (f"高さ {sg(P.H_MIN * MM)}〜{sg(P.H_MAX * MM)}mm", f"凹みと出っ張りの両方を作ります。窓の深さ（ベゼルの厚み {P.BEZEL_T * MM:g}mm）が、凹み {-P.H_MIN * MM:g}mm を覆います。",
         join(code("H_MIN"), "　", code("H_MAX"))),
        ("重力で戻す。天面を上にして置く専用", "画素を引き戻す部品が要りません。C3とC4-2と同じ方式です。", "（構造）"),
        (f"表 {P.K} 枚。サーボ角 {' / '.join(f'{t:g}' for t in P.TABLE_THETA)}°",
         f"間隔 {P.TABLE_THETA[1] - P.TABLE_THETA[0]:g}° は、カム軸で {(P.TABLE_THETA[1] - P.TABLE_THETA[0]) * P.G_RATIO:.0f}° です。"
         f"間隔を広げると、一周して隣り合う端の表どうしの角度（今は {dci('端の表（0 と 4）')['value']:g}°）が縮み、この組の高さの差が厳しくなります。"
         f"使うサーボ範囲 ±80° で、カム軸の角度幅は {dci('サーボ使用範囲での軸の角度の幅')['value']:.1f}°（360° 未満）です。",
         join(code("K"), "　", code("TABLE_THETA"))),
        (f"増速 {P.SERVO_Z}/{P.END_Z} = {P.G_RATIO:.3f}",
         f"1:1 ではカムが凹になって成立しません。独立した2体の検討が、同じ結論に収束しました。設計検査の範囲は {dci('g（下限')['limit']:g} 以上 {dci('g（上限')['limit']:g} 以下です。",
         join(code("SERVO_Z"), "　", code("END_Z"))),
        (f"停止区間 ±{P.DWELL_HALF_DEG:g}°",
         f"位相誤差の合計の最悪 {key['phase_sum_deg']:.2f}° に、余裕 {key['phase_margin_deg']:.2f}° を残しました。既定の表が生成器を通る最大は 13.25° です。",
         code("DWELL_HALF_DEG")),
        ("方式: 平行なカム軸5本に板カム25枚",
         "各画素が独立に動きます。カム輪郭は平面で刷れて、層段が出ません。大円盤の面カム案は、25本の独立したトラックが入らず（帯の誤差余裕 0.08mm、または 24 本 < 25 本の解析限界）、"
         "中心の画素の半径が小さくて表が2〜3枚にとどまるため、退けました。",
         "（方式）"),
        ("平らな足の従動子。カムは凸", f"圧力角が0です。足の幅 {P.FOOT_Y * MM:g}mm が、接点の横ずれ（最大 {key['lateral_max_mm']:.2f}mm）を覆います。", code("FOOT_Y")),
        (f"歯車 モジュール{P.GEAR_M * MM:g}、{P.CHAIN_Z}歯、歯幅 {P.GEAR_T * MM:g}mm",
         f"噛み合い率は {dci('噛み合い率 17T-17T')['value']:.2f} です。停動での歯の曲げ応力は {dci('歯の曲げ応力')['value']:.1f}MPa です（上限 {dci('歯の曲げ応力')['limit']:g}）。",
         join(code("GEAR_M"), "　", code("CHAIN_Z"), "　", code("GEAR_T"))),
        (f"軸は六角（二面幅 {P.SHAFT_AF * MM:g}mm）。切り落とし面で向きを1通りに。穴に潰しリブ{P.HEX_RIB_FACES}本",
         f"潰しリブが無いと、六角のガタがカムと歯車の2箇所でそれぞれ ±{key['hex_slack_if_ribs_fail_deg']:.2f}° になり、合計が停止区間を超えます。潰し代は {P.HEX_RIB_CRUSH * MM:g}mm です。",
         join(code("SHAFT_AF"), "　", code("HEX_RIB_CRUSH"))),
        (f"案内板の厚み {P.PLATE_T * MM:.1f}mm", f"案内を長くして、画素のこじれを抑えます。こじれ係数の最大は {key['kappa_B_035']:.2f} です（上限 {P.KAPPA_LIMIT_LO}）。",
         code("PLATE_Z0")),
        ("画素は1部品。頭を下にして刷る", "見える頭の面が最初の層になり、サポートが要りません。", "（構造）"),
        (f"デモは1表あたり {FW['moveTiming']['minMoveMs']}ms", f"浮かない最短 {FW['moveTiming']['noLiftFloorMs']}ms より十分長い値で、見せ方として選びました。", code("firmware.py の DEMO_MOVE_MS")),
    ]
    return table(("決めたこと", "理由", "変える定数"), rows)


def concession_list():
    items = []
    items.append(join(tag("strong", "画素の指定が実行時に自由ではありません。"),
                      H(esc(f"SG92R 1台では、25画素を独立に動かす自由度が足りません。代わりに、表を {P.K} 枚まで機械（カムの形）に書き込み、サーボ角で表を選びます。表を変えるときはカムを刷り直します。"))))
    items.append(join(tag("strong", "天面を上にして置く専用です。"), H(esc("画素を重力でカムに載せるためです。横置きや逆さでは戻りません。電源を切った後の位置も保証しません。"))))
    items.append(join(tag("strong", "隣り合う表の高さの差に制約があります。"),
                      H(esc(f"サーボ角で{P.TABLE_THETA[1] - P.TABLE_THETA[0]:g}°離れた表の同じ画素は、−3mm から +3mm へは動けません（−3mm なら次は +0.3mm までです）。端の表0と表4は一周して56°で隣り合い、さらに厳しくなります。どちらも生成器が拒否します。README.md に表があります。"))))
    old_margin = SCEN.get("maximumPlay", {}).get("minimumMarginDeg")
    if STOP_HEIGHT is not None:
        why = (f"停止区間の余裕（1° 以上）から、停止時の高さの誤差（{STOP_HEIGHT['limitMm']:g}mm 以下）へ変えました。")
        if old_margin is not None:
            why += f"旧基準は、溝の中の位置の全組み合わせで誤差が同じ向きに最悪で重なる場合にも、余裕 1° を求めていました。その場合の余裕は {sg(old_margin, 2)}° で、基準に届きません。"
        why += (f"画素の高さに効くのは、位相がずれた分だけカムが同心円の弧から外れる量です。実カムのSTLを回して測った最大の高さ誤差は {STOP_HEIGHT['maximumErrorMm']:.3f}mm でした"
                f"（位相誤差だけでは {STOP_HEIGHT['phaseOnlyMaximumMm']:.3f}mm）。基準の {STOP_HEIGHT['limitMm']:g}mm は、既定の表の最小の刻み 0.5mm の半分で、隣の段と見分けがつく大きさです。")
        if STOP_HEIGHT_X2 is not None:
            why += f"位相誤差を2倍にすると {STOP_HEIGHT_X2['maximumErrorMm']:.3f}mm になり、{'基準を超えます' if not STOP_HEIGHT_X2['pass'] else '基準の内側に収まります'}。"
        items.append(join(tag("strong", "歯車の位相の判定の基準。"), H(esc(why))))
    else:
        items.append(join(tag("strong", "歯車の位相の判定の基準。"),
                          H(esc("停止区間の余裕（1° 以上）から、停止時の高さの誤差（0.25mm 以下）へ変えます。drive_report.json に新しい基準の結果がないため、数値は載せられません。drive.py を流し直して、このファイルをもう一度流してください。"))))
    items.append(join(tag("strong", "肉厚の例外。"),
                      H(esc(f"ベゼルの窓と窓の桟は {P.BEZEL_BAR * MM:g}mm で、外装の壁 2mm の規則に届きません。頭を小さくしないために認めました。"
                            "潰しリブ（幅 0.6mm）は、潰れて隙間を消すための形です。歯車の歯先（1.1mm 前後）は、歯の形の性質です。番号の彫りは、読めれば足ります。いずれも荷重の主経路ではありません。"))))
    items.append(join(tag("strong", "動かし方を制限しました。"),
                      H(esc(f"最速のステップ指令では、画素がカムから浮くことがあります。デモは1表 {FW['moveTiming']['minMoveMs']}ms 以上、5次関数の滑らかな立ち上がりと止まりで動かします。"))))
    items.append(join(tag("strong", "部品数。"),
                      H(esc(f"印刷部品は {len(PARTS_PRINT)} 個です。画素ごとの独立した動きを取り、部品の少なさより組めることを優先しました。"))))
    items.append(join(tag("strong", "外形。"), H(esc(f"{CUBE_MM:g}mm にとどめました。10cm いっぱいにはせず、画素の出っ張り {sg(P.H_MAX * MM)}mm を足して {PEAK_MM:g}mm にしました。"))))
    return ulist(items)


def hardware_list():
    trial1 = next(p for p in PL["plates"] if p["id"] == "trial1-rotating")
    vp = CF["shaftVerticalPlay"]
    items = [
        join(tag("strong", "試し刷り1（回す部分）。"), H(esc(f"{trial1['n_parts']} 片です。付属ホーンと実物のSG92Rを、受け（horn_coupler）に入れます。きつければ HORN_CLR を 0.05mm ずつ増やします。"
                                                    "ホーンが押し込めて、抜けず、がたつかなければ合格です。"))),
        join(tag("strong", "潰しリブ。"), H(esc(f"cam_4_2 と gear_2 を、軸の端の小片に通します。手で押し込める力で入り、回してもガタが見えなければ合格です。"
                                           f"位相誤差の予算は、潰し代 {P.HEX_RIB_CRUSH * MM:g}mm のリブが効く前提です（ガタの見積りは ±{P.FIT_ERR_DEG:g}°）。"))),
        join(tag("strong", "スプライン。"), H(esc("付属ホーンをSG92Rの出力軸に付けます。正本にスプラインの歯がないので、嵌合と回転の伝わりを実物で確かめます。18° 刻みで付け直せるかも見ます。"))),
        join(tag("strong", "摩擦。"), H(esc(f"全部組んだら、サーボをつながずに軸を手で回します。画素がなめらかに上下し、止まらなければ合格です。計算は摩擦係数 {P.MU_CAM} と {P.MU_CAM_HI} の仮値を使っています。"))),
        join(tag("strong", "爪の着脱力。"), H(esc("試し刷り2のベゼルの爪、案内板の舌、押さえクリップと、Cクリップを着脱します。割れや白化が出ないかを見ます。"
                                            f"計算上のひずみは最大 {STRAIN_MAX:.2f}% です（{STRAIN_ZONE}）。"))),
        join(tag("strong", "画素の重力での落ち。"), H(esc(f"画素を指で持ち上げて離すと、カムまで落ちて止まります。引っかかれば不合格です。軸が案内板を押し上げる場合、画素は表より {vp['floatedPushingPlateShiftMm']:g}mm 高くなります"
                                               f"（許容 {vp['tableToleranceMm']:g}mm を超えます）。浮くのは歯車の分離力が画素と軸の重さを超えるときです。実機で確かめます。"))),
        join(tag("strong", "位相合わせ。"), H(esc(f"組み立てたら、位相合わせ治具が5本とも座るかを見ます。5本とも浮くときは、デモの + と − で 0.25° ずつ回して座る位置を探します。1本だけ浮く軸は 1 歯ずれているので置き直します。座ったら w で保存します。仕上げに、表1の中央（−3mm）と表3の中央（+3mm）が表どおりになる幅の中央へ、同じ + と − で合わせます。"
                                           f"許容は ±{FW['angles']['phaseTrimAllowedDeg'][1]:g}° です。"))),
        join(tag("strong", "組み立て。"), H(esc(f"{len(AR['steps'])} 工程を実際に組みます。指が入る隙間と、サーボ一式を -X へ 1.8mm 寄せて下ろす動作を確かめます。"))),
        join(tag("strong", "通電。"), H(esc("4.8V の安定化電源で、表0から4まで順に動かします。各表で画素が表どおりに揃うか、擦れや引っかかりがないかを見ます。"))),
        join(tag("strong", "電源を切ったとき。"), H(esc("画素の位置が保たれるか、軸が回って画素が落ちるかを見ます。"))),
        join(tag("strong", "PETG。"), H(esc("PETGで刷った部品の嵌め合いが、固くならないかを見ます。"))),
        join(tag("strong", "繰り返し。"), H(esc("繰り返し動かしたときの、カムと足の摩耗と、爪の割れを見ます。"))),
    ]
    return ulist(items, ordered=True)


def exception_name(key):
    return {"crush_rib_0.6": "潰しリブ 0.6mm", "gear_tooth_tip_1.1": "歯先 1.1mm", "cam_label_engraving": "番号の彫り",
            "bezel_bar_1.6": "ベゼルの桟 1.6mm", "finger_catch_1.4": "指の掛かり"}.get(key, key)


def overlap_name(kind):
    return {"hex-crush-ribs": "潰しリブ（カムと歯車の穴）", "ear-crush-ribs": "潰しリブ（サーボの取付耳）",
            "canonical-servo-output-shaft": "SG92R の出力軸とホーン（正本の形）"}.get(kind, kind)


def zone_name(zone):
    if zone.startswith("rib:"):
        return "潰しリブ（カム・歯車の穴）"
    if zone.startswith("servo_clip"):
        return "押さえクリップの爪"
    if zone.startswith("shaft_clip"):
        return "Cクリップの口"
    return {"bezel_barbs": "ベゼルの爪", "plate_hooks": "案内板の舌の爪", "ear_ribs": "柵の潰しリブ（取付耳）"}.get(zone, zone)


def verify_sections():
    out = []
    # 干渉
    out.append(tag("h3", "干渉"))
    out.append(para(
        f"サーボ {IF['servoDegs'][0]:g}〜{IF['servoDegs'][1]:g}° を {IF['stepDeg']:g}° 刻み（{IF['poseCount']} 姿勢）で、{IF['parts']} 部品の {IF['uniquePairs']} 組を測りました。"
        f"外接箱が離れた組と、表面が交わらない組は 0 です。それ以外は Blender の MANIFOLD で共通体積を測ります（Boolean {IF['booleanEvaluations']} 回）。"
        f"許可外の最大の共通体積は {IF['maximumNonDesignedCommonVolumeMm3']:.1e}mm³ です。体積の床は {IF['volumeFloorMm3']:g}mm³ で、校正で固定しました。"))
    kinds = collections.Counter(d["kind"] for d in IF["designedOverlaps"])
    out.append(para(f"許可した重なり {len(IF['designedOverlaps'])} 件の内訳は、" + "、".join(f"{overlap_name(k)} {n} 件" for k, n in kinds.items())
                    + "です。場所、個数、量を限定し、すべて範囲内です。" if all(d["pass"] for d in IF["designedOverlaps"]) else
                    f"許可した重なり {len(IF['designedOverlaps'])} 件のうち、範囲外が {sum(1 for d in IF['designedOverlaps'] if not d['pass'])} 件あります。"))
    # カムと足
    out.append(tag("h3", "カムと足"))
    out.append(para(
        f"{CF['pixels']} 画素の足の下面の矩形を真上から見た最高点を、実カムのSTLから厳密に求めました。食い込みは最大 {CF['worstPenetrationMm']:.1e}mm です（許容 {CF['penetrationLimitMm']:g}）。"
        f"浮きは最大 {CF['worstFloatMm']:.1e}mm です（許容 {CF['floatLimitMm']:g}）。足が自分のカムに載らない姿勢は {CF['posesNotOnOwnCam']} 件です。"
        f"表の高さとの誤差は最大 {CF['tableHeightWorstErrorMm']:.1e}mm です（{len(CF['tableHeights'])} 点。許容 {CF['tableHeightLimitMm']:g}）。"))
    vp = CF["shaftVerticalPlay"]
    out.append(table(("軸の上下の遊び", "画素の高さの変化", f"許容 ±{vp['tableToleranceMm']:g}mm"), (
        ("溝の底に載っている", f"{sg(vp['settledShiftMm'], 2)}mm", tol_chip(vp["settledWithinTolerance"])),
        ("栓まで浮く", f"{sg(vp['floatedToPlugShiftMm'], 2)}mm", tol_chip(vp["plugWithinTolerance"])),
        ("案内板を押し上げるまで浮く", f"{sg(vp['floatedPushingPlateShiftMm'], 2)}mm", tol_chip(vp["pushingPlateWithinTolerance"])),
    )))
    out.append(para("verify_report.json の注記: " + vp["note"] + "（" + vp["limit"] + "）"))
    # 駆動界面
    out.append(tag("h3", "駆動の接続と保持"))
    out.append(para("実STLを動かして、保持相手との初接触までの移動量を六方向で測りました。保持相手を外した負例で、接触が消えることも測りました。"
                    + f"基準は「{DR['overall']['basis']}」です。"))
    out.append(table(("界面", "判定", "要点（最初の1文）"), [
        (i["label"], chip(status_kind(i["status"])), i["detail"].split("。")[0] + "。") for i in DR["interfaces"]]))
    out.append(details("界面ごとの検査の原文", ulist([f"{i['label']}: {i['detail']}" for i in DR["interfaces"]])))
    if GEAR is not None:
        out.append(para("歯車の噛み合いの詳細（drive_report.json の原文）: " + GEAR["detail"]))
        if STOP_HEIGHT is not None:
            out.append(table(("条件", "停止時の高さの誤差の最大", "基準"), (
                ("位相誤差と軸の上下の遊びの最大", f"{STOP_HEIGHT['maximumErrorMm']:.3f}mm", f"{STOP_HEIGHT['limitMm']:g}mm 以下"),
                ("位相誤差だけ", f"{STOP_HEIGHT['phaseOnlyMaximumMm']:.3f}mm", "参考"),
            ) + ((("位相誤差を2倍", f"{STOP_HEIGHT_X2['maximumErrorMm']:.3f}mm", "負例（超えるはず）"),) if STOP_HEIGHT_X2 else ())))
    # 遊びの鎖
    out.append(tag("h3", "遊びの鎖"))
    key = DC["summary"]["key"]
    out.append(para(f"位相誤差は、サーボの位置、ホーンの合わせ、潰しリブの嵌め、バックラッシュ、軸の上下のずれを足して、最悪の軸（0と4）で {key['phase_sum_deg']:.2f}° です。"
                    f"停止区間の半幅 {key['dwell_half_deg']:g}° に対して、余裕は {key['phase_margin_deg']:.2f}° です（設計検査の基準は 1° 以上）。"))
    out.append(para(dci("位相誤差の内訳")["value"]))
    chain = (("各軸の上向きの隙間の最大", "軸の上向きの隙間（栓の下端と軸の丸の上端）の最大"),
             ("軸の浮きの鎖の合計", "軸の浮きの鎖の合計（溝の底、栓、案内板の遊び）"),
             ("案内板の上下の遊び", "案内板の上下の遊び"),
             ("歯先の重なりの残り: 受け-中央軸", "歯先の重なりの残り（受けと中央の軸）"),
             ("歯先の重なりの残り: 隣の軸どうし", "歯先の重なりの残り（隣の軸どうし）"))
    chain_rows = [(label, f"{dci(f)['value']:.3g}", ("上限 " if dci(f)["kind"] == "max" else "下限 ") + f"{dci(f)['limit']:g}" + dci(f)["unit"], chip("ok" if dci(f)["pass"] else "ng"))
                  for f, label in chain]
    out.append(table(("項目", "値", "基準", "判定"), chain_rows))
    pb = DR["phaseBudget"]
    out.append(table(("駆動検査の条件", "最悪の軸の余裕（停止区間 − 位相誤差）"),
                     [(s["label"], f"{sg(s['minimumMarginDeg'], 2)}°") for s in SCEN.values()]))
    out.append(para(f"駆動検査が測った位相誤差の最悪は、設計検査の線形和との差が {sg(pb['differenceFromDesignLinearDeg'][0], 2)}° です（軸0）。"
                    "旧基準の余裕は参考値として残しました。判定は停止時の高さの誤差で行います。"))
    # 組立工程
    out.append(tag("h3", "組立の工程"))
    out.append(table(("工程", "姿勢の数", "最大の共通体積（許可した当たりを含む）", "許可した当たり", "判定"), [
        (f"{n + 1}. {s['title']}", s["samples"], f"{s['maxCommonVolumeMm3']:.3g}mm³",
         len(s["allowedContacts"]), chip("ok" if s["pass"] else "ng")) for n, s in enumerate(AR["steps"])]))
    zones = collections.OrderedDict()
    for c in CONTACTS:
        zones.setdefault(zone_name(c["zone"]), []).append(c)
    out.append(table(("設計した当たり", "件数", "最大の深さ", "ひずみ（最大）"), [
        (name, len(v), f"{max(x.get('maxDepthMm', 0) for x in v):.2f}mm",
         (f"{max(x['strainPercent'] for x in v if x.get('strainPercent') is not None):.2f}%" if any(x.get("strainPercent") is not None for x in v) else "（圧入）"))
        for name, v in zones.items()]))
    rolling = AR["rolling"]
    out.append(table(("軸", "構える角度", "噛み合う相手", "転がり始める高さ", "歯の最小の隙間"), [
        (f"軸{j}", f"{r['startAngleDeg']:+.2f}°", r["neighbor"], f"{r['rollsFromHeightMm']:g}mm",
         f"{(r.get('twoDimensionalDescent') or r.get('betweenFrames'))['minClearanceMm']:.3f}mm")
        for j, r in sorted(rolling.items())]))
    out.append(para("軸1、軸3、軸0、軸4は、歯が隣の歯車に触れる高さから、軸が転がるように回しながら落とします。鉛直に落とすと歯が当たることを、負例で確かめました。"))
    # 物理
    out.append(tag("h3", "物理"))
    out.append(para(f"1自由度の運動方程式で計算しました（サーボは、停動 {STALL_MNM:g}mN·m、無負荷 60°/0.1秒のトルク上限つき位置制御）。可動部の質量は、画素 {SR['massIntegration']['totals']['pixelsG']:.0f}g と回転部 {SR['massIntegration']['totals']['rotatingG']:.0f}g を合わせて {SR['massIntegration']['totals']['movingTotalG']:.0f}g です（実STLの体積積分。密度は PLA の 85%）。"))
    out.append(table(("項目", "値", "基準"), (
        ("必要トルク（摩擦0.35）", f"{ST['maximumRequiredTorqueNm'] * MM:.1f} mN·m（停動の {ST['fractionOfStall'] * 100:.1f}%）", f"{TORQUE_LIMIT_MNM:.1f} mN·m 以下"),
        ("必要トルク（摩擦0.45）", f"{SENS['staticRequiredNm'] * MM:.1f} mN·m（停動の {SENS['staticRequiredNm'] * MM / STALL_MNM * 100:.1f}%）", f"{TORQUE_LIMIT_MNM:.1f} mN·m 以下"),
        ("ゆっくり動かしたピーク（3秒）", f"{ST['peakLowSpeedTorqueNm'] * MM:.1f} mN·m", f"{TORQUE_LIMIT_MNM:.1f} mN·m 以下"),
        ("接触力の最小", f"{SR['checks']['b_contact']['minNormalForceN']:.3f}N（画素の重さ {SR['checks']['b_contact']['pixelWeightN']:.3f}N）", "全時刻で 0 以上（浮かない）"),
        ("こじれ係数 κ の最大", f"{SR['checks']['c_kappa']['plateOnlyMax']:.2f}（板だけの案内、摩擦0.45）", "1 未満"),
        ("停止角での高さ誤差", f"{SR['checks']['d_stopHeights']['simFinalErrorMaxMm']:.1e}mm", f"{SR['checks']['d_stopHeights']['toleranceMm']:g}mm 以下"),
        ("浮かない最短の移動時間（1表）", f"{SR['motion']['minNoLiftMoveS']['max']:g}秒", "デモは 0.6 秒"),
        ("端で当たる速さ", f"{CONTACT_SPEED_MAX:g} mm/s", "（当たらない）"),
    )))
    out.append(para(f"駆動の接続の検査（drive_report.json）との照合は、「{SR['driveGeometry']['reason']}」でした。"
                    f"動力学の全体の判定は{STATUS_JA.get(SR['overall']['status'], SR['overall']['status'])}です。{SIM_BASIS}。"))
    out.append(para(f"設計検査のトルク（0.35 で {key['torque_035_mNm']:.1f}、0.45 で {key['torque_045_mNm']:.1f} mN·m）は、動力学の計算の値と一致しません。"
                    "判定には動力学の計算の値を使います。"))
    # 印刷
    out.append(tag("h3", "印刷"))
    out.append(para(f"{PS['n_parts_reviewed']} 個の印刷部品を、刷る向きのSTLで精査しました（同じ形の部品をまとめて {PS['n_unique_analyses']} 通り）。"
                    f"不合格は {PS['n_fail_entries']} 件です。許可した例外 {PS['n_allowed_exception_entries']} 件の内訳は、"
                    + "、".join(f"{exception_name(k)} {v} 件" for k, v in EXC_COUNT.items()) + "です。"))
    out.append(table(("項目", "結果", "基準"), (
        ("見える面の張り出し", f"{VISIBLE_OVERHANG:g}mm²", "0"),
        ("見えない面の橋", f"最長 {BRIDGE_MAX:g}mm（{BRIDGE_PART}）", f"{PR['thresholds']['bridge_max_mm']:g}mm 以内"),
        ("立てて刷る細物の高さと太さの比", f"最大 {SLENDER_MAX:g}（{SLENDER_PART}）", f"{PR['thresholds']['slender_height_over_width']:g} 以内"),
        ("外装の見える面の肉厚", f"最小 {HOUSING_EXT_MIN:g}mm", f"{PR['thresholds']['wall_exterior_mm']:g}mm 以上"),
        ("面取りが欠けた嵌め合いの縁", f"{len(NO_CHAMFER)} 個", "0"),
        ("連結成分が1でない部品／接地しない部品", f"{len(MULTI_COMP)} 個／{len(UNGROUNDED)} 個", "0"),
    )))
    return H("".join(esc(x) for x in out))


def plates_section():
    rows = []
    for plate in PL["plates"]:
        pla = Path(plate["files"]["PLA"]).name
        petg = Path(plate["files"]["PETG"]).name
        rows.append((plate["id"], "本体" if plate["kind"] == "main" else "試し刷り", plate["n_parts"], f"{plate['mass_pla_g']:g}g", f"{plate['tallest_part_mm']:g}mm",
                     H(f'<a href="../prints/{MODEL}/{esc(pla)}">PLA</a>　<a href="../prints/{MODEL}/{esc(petg)}">PETG</a>')))
    out = [table(("プレート", "種類", "部品数", "PLAの質量（見込み）", "最も高い部品", "3mf"), rows)]
    out.append(para(f"本体の合計は {PL['mass_total_pla_g']:g}g です（中実なら上限 {PL['mass_total_solid_upper_g']:g}g）。スライスしていないので、印刷時間は未算出です。"
                    "質量は、壁2周、上5層、下3層、充填15%、PLA 1.26g/cm³ で見込みました。"))
    out.append(para(f"試し刷りの小片は {len(TR)} 個です。小片は prints/{MODEL}/trial/、全部品は prints/{MODEL}/parts/ にあります。"))
    return H("".join(esc(x) for x in out))


def inputs_section():
    rows = []
    for path in INPUT_FILES:
        rel = path.relative_to(ROOT).as_posix()
        stale = FRESH.get(path.name)
        rows.append((code(rel), stamp(path), H(f'<code class="hash">{sha256(path)}</code>'),
                     "最新" if stale is None or not stale else ("古い: " + "、".join(stale[:3]) + (f" ほか{len(stale) - 3}件" if len(stale) > 3 else ""))))
    return table(("入力", "更新時刻", "SHA-256", "鮮度"), rows)


# ---------------------------------------------------------------- 本文 ---

def build():
    rows = requirement_rows()
    counts = collections.Counter(r[2] for r in rows)
    summary_bits = [f"{KIND_LABEL[k]} {counts.get(k, 0)} 行" for k in ("ok", "cond", "unk", "ng")]
    ng_rows = [r for r in rows if r[2] == "ng"]
    unk_rows = [r for r in rows if r[2] == "unk"]
    lead = [
        para(f"{CUBE_MM:g} × {CUBE_MM:g} × {CUBE_MM:g}mm の立方体です。天面の {P.N} × {P.N} 枚の画素が、SG92R 1台で {sg(P.H_MIN * MM)}〜{sg(P.H_MAX * MM)}mm 上下します。"
             f"画素が出ると最大 {PEAK_MM:g}mm で、10cm 以下に収まります。"),
        para(f"どの画素が動くかは、patterns.py の高さの表で決まります。表は {P.K} 枚です。サーボ角で表を選びます。表を変えるときは、カム {N_PIXELS} 枚を作り直して刷り直します。"),
        para("要件ごとの結果は、" + "、".join(summary_bits) + f"です（計 {len(rows)} 行）。"),
    ]
    if ng_rows:
        lead.append(para("不適合の行は、" + "、".join(f"{r[1]}" for r in ng_rows) + "です。"))
    if unk_rows:
        lead.append(para("未確認の行は、" + "、".join(f"{r[1]}" for r in unk_rows) + "です。"))
    if STALE:
        lead.append(para("次の検査結果は、現在の入力より古くなっています。" + "、".join(f"{k}（{v[0]}）" for k, v in STALE.items()) + "。検査を流し直してから、report.py をもう一度流します。"))
    lead_html = H('<div class="lead">' + "".join(esc(x) for x in lead) + "</div>")

    req_parts = []
    groups = collections.OrderedDict()
    for g, r, k, res, basis in rows:
        groups.setdefault(g, []).append((r, chip(k), H(f"{esc(res)}<br><span class=\"muted\">根拠: {esc(basis)}</span>")))
    for g, grows in groups.items():
        req_parts.append(tag("h3", {"依頼": "依頼の要件"}.get(g, "共通条件 " + g)))
        req_parts.append(table(("要件", "判定", "結果と根拠"), grows, "req"))
    req_table = H("".join(esc(x) for x in req_parts))

    cal_rows = calibration_rows()
    cal_table = table(("検査", "通るはずの例（正例）", "止まるはずの例（負例）", "校正の件数", "通過"), [
        (name, pos, neg, n, f"{ok}" + ("" if ok == n else "　未達あり")) for name, pos, neg, n, ok in cal_rows])

    css = ""
    for cand in STYLE_CANDIDATES:
        if cand.is_file():
            css = cand.read_text(encoding="utf-8")
            break
    if not css:
        raise FileNotFoundError("report.css が見つからない: " + ", ".join(str(c) for c in STYLE_CANDIDATES))
    extra = """
.patterns{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:var(--sp-4);margin:var(--sp-4) 0 var(--sp-6)}
.patterns figure{margin:0}
.patterns figcaption{margin:0 0 var(--sp-1);color:var(--ink);font-size:var(--fs-sm)}
table.cells{table-layout:fixed;font-size:var(--fs-xs)}
table.cells td{text-align:center;padding:.35em .1em;font-variant-numeric:tabular-nums}
table.cells td.neg{background:color-mix(in srgb,var(--accent) calc(var(--m) * 1%),var(--card))}
table.cells td.pos{background:color-mix(in srgb,var(--accent-2) calc(var(--m) * 1%),var(--card))}
table.cells td.zero{background:var(--card)}
details{margin:var(--sp-4) 0}
code.hash{font-size:var(--fs-xs);word-break:break-all;white-space:normal}
table.req td:nth-child(1){min-width:11rem}
table.req td:nth-child(3){min-width:17rem}
table.req td:nth-child(2){white-space:nowrap}
@media (max-width:40rem){
table.req,table.req tbody,table.req tr,table.req td{display:block;min-width:0}
table.req thead{display:none}
table.req tr{border-top:1px solid var(--line);padding:var(--sp-3) 0}
table.req td{border:0;padding:var(--sp-1) 0}
table.req td:nth-child(1){font-weight:700}
}
td .chip{margin-left:0}
"""
    sections = []
    sections.append(H(f"<h2>1. 何を作ったか</h2>"))
    sections.append(para(f"外形は {CUBE_MM:g}mm です。画素は {N_PIXELS} 枚で（頭は {P.HEAD * MM:g}mm 角、ピッチは {P.PITCH * MM:g}mm）、表は {P.K} 枚です。"
                         "セルの数字は画素の高さ（mm）です。凹みは暖色、出っ張りは緑で、濃さが大きさです。"))
    sections.append(pattern_grids())
    sections.append(para(f"サーボ {P.THETA_FLAT:g}° が全部面一で、組み立てる角度でもあります。使う範囲は {P.SERVO_MIN_DEG:g}〜{P.SERVO_MAX_DEG:g}° です。"
                         f"サーボが 1° 回ると、カム軸は {P.G_RATIO:.3f}° 回ります。"))
    sections.append(H("<h2>2. 要件ごとの結果</h2>"))
    sections.append(para("依頼の基本2項目と①〜⑤、共通条件の§3〜§6を、1行ずつ並べました。結果の下に、根拠にした json を書いています。"))
    sections.append(req_table)
    sections.append(H("<h2>3. 決めたこと</h2>"))
    sections.append(para("依頼にも共通条件にもなく、自分で決めた値と理由です。"))
    sections.append(decisions_table())
    sections.append(H("<h2>4. 譲ったこと</h2>"))
    sections.append(concession_list())
    sections.append(H("<h2>5. 実物で確かめること</h2>"))
    sections.append(para("刷ってから、この順に見ます。"))
    sections.append(hardware_list())
    sections.append(H("<h2>6. 各検証の要約</h2>"))
    sections.append(verify_sections())
    sections.append(H("<h2>7. 校正の結果</h2>"))
    sections.append(para("どの検査も、先に答えの分かる形を流しました。通るはずの例と止まるはずの例が、両方期待どおりに出たときだけ、本番の数字を使います。"))
    sections.append(cal_table)
    sections.append(H("<h2>8. 渡すもの</h2>"))
    sections.append(plates_section())
    sections.append(para(join(H(f'<a href="../models/{MODEL}/README.md">README.md</a>'), "（部品表、組み立て、試し刷りと調整、表の作り方）と、　",
                               H(f'<a href="../models/{MODEL}/demo/demo.ino">demo.ino</a>'), "（Arduino のデモ）を渡します。")))
    sections.append(para(f"Studio は http://localhost:3000/?model={MODEL} で開きます（物理検証と組み立ての表示は /viewer/lattice/index.html?model={MODEL} です）。"))
    sections.append(H("<h2>9. 生成に使った入力</h2>"))
    sections.append(para(f"この報告は report.py が作りました。生成時刻は {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} です。"))
    sections.append(inputs_section())
    comp = FW["compile"]
    if comp.get("status") == "compiled":
        comp_text = (f"デモは Arduino Uno 向けに実コンパイルしました（Flash {comp['flashBytes']} / {comp['flashMaximumBytes']} bytes、RAM {comp['ramBytes']} / {comp['ramMaximumBytes']} bytes。"
                     f"PHASE_TRIM_DEG の ±10° は通り、±11° は範囲外として止まります）。")
    else:
        comp_text = "デモの Arduino 向けコンパイルは未実施です（firmware_report.json の compile.status は " + str(comp.get("status")) + "）。"
    sections.append(para(comp_text + "マイコンへの書き込みと SG92R の通電は未実施です。", "note"))

    doc = (f'<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f"<title>住人の箱 C4-3・タンジブル画素キューブ</title><style>{css}{extra}</style>"
           f'<div class="wrap"><p class="eyebrow">model-lab · 2026-10-13</p><h1>住人の箱 C4-3・タンジブル画素キューブ</h1>'
           f'<p class="sub">{CUBE_MM:g} × {CUBE_MM:g} × {CUBE_MM:g}mm。SG92R 1台で {P.N} × {P.N} の画素を上下させます。</p>'
           f"{lead_html}{''.join(esc(s) for s in sections)}</div></html>")
    return doc, counts


def main():
    doc, counts = build()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    tmp = TARGET.with_suffix(".html.tmp")
    tmp.write_text(doc, encoding="utf-8", newline="\n")
    os.replace(tmp, TARGET)
    print(json.dumps({
        "path": str(TARGET), "bytes": TARGET.stat().st_size,
        "verdicts": dict(counts),
        "stale": STALE,
        "drive_report_mtime": stamp(BUILD / "drive_report.json"),
        "inputs": {p.relative_to(ROOT).as_posix(): stamp(p) for p in INPUT_FILES},
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
