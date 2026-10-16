"""patterns.py と params.py から Arduino のデモ demo/demo.ino を生成する。書き込みや接続はしない。

表の名前・サーボ角・5 x 5 の高さは patterns.py / params.py から読み、.ino には注釈と定数として生成する（手で書き写さない）。
生成した .ino の SHA-256 と入力の SHA-256 は build/firmware_report.json へ。

  py -3.11 models/tangible-pixel-cube/firmware.py
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import params as P
import patterns as PT

SOURCE = HERE / "demo" / "demo.ino"
BAR_TEMPLATE = HERE / "bar_template.html"
BAR_OUTPUT = HERE / "demo" / "bar.html"
REPORT = HERE / "build" / "firmware_report.json"
SIMULATE_REPORT = HERE / "build" / "simulate_report.json"

# 浮かない最短時間（1 表の間隔 = 隣の表への移動あたりの秒）が simulate_report.json の motion に入ったら読む候補キー。
# まだ入っていないので、無ければ既定の 1 表あたり DEFAULT_MOVE_MS を使う
SAFE_KEYS = ("minNoLiftMoveS", "safeMinTableMoveS", "minSafeTableMoveS", "liftOffFreeMinTableMoveS", "safeMinimumTableMoveS")
DEFAULT_MOVE_MS = 800
DEMO_MOVE_MS = 600             # 見せ方として選んだ 1 表あたりの移動時間。浮かない最短時間 x MARGIN より短くはしない
MARGIN = 1.3                   # 浮かない最短時間に足す余裕（30%）
DWELL_MS = 1500                # 表の途中停止（g / p / b の各表で止まる時間）
PHASE_TRIM_LIMIT_DEG = 10.0    # 位相補正の許容（±10 度。C4-2 と同じ）。コンパイル時の既定と実行時の + / - / EEPROM の両方に効く
TRIM_STEP_DEG = 0.25           # 実行時の + / - の刻み。EEPROM は 0.25 度単位の int8（±40 = ±10 度）で持つ
SERIAL_DIGITS = 10             # 数字キー 0..9 が表の番号に使える


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def record(path):
    return {"file": Path(path).resolve().relative_to(ROOT).as_posix(), "sha256": digest(path)}


def atomic_text(path, text):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with open(temporary, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(temporary, path)


def check_inputs():
    """表と角度の整合を確かめる。壊れていれば生成せずに落ちる"""
    k = P.K
    if not 1 <= k <= SERIAL_DIGITS:
        raise ValueError(f"表の数 K={k} は数字キー 0..{SERIAL_DIGITS - 1} に収まらない")
    if not (len(PT.TABLES) == len(PT.NAMES) == len(PT.LABELS_JA) == len(P.TABLE_THETA) == k):
        raise ValueError("patterns.TABLES / NAMES / LABELS_JA と params.TABLE_THETA / K の長さが一致しない")
    thetas = list(P.TABLE_THETA)
    if thetas != sorted(thetas):
        raise ValueError("TABLE_THETA がサーボ角の昇順でない（途中の表を通る順を並び順で説明できない）")
    for name in PT.NAMES:
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", name):
            raise ValueError(f"表の名前 {name!r} は ASCII の英数字・_・- だけにする（シリアルの表示に使う）")
    for theta in thetas + [P.THETA_FLAT]:
        if not (P.SERVO_MIN_DEG <= theta <= P.SERVO_MAX_DEG):
            raise ValueError(f"サーボ角 {theta} がサーボの使用範囲 {P.SERVO_MIN_DEG}..{P.SERVO_MAX_DEG} の外")
    if PHASE_TRIM_LIMIT_DEG != 10.0:
        raise ValueError("位相補正の許容は C4-2 に揃えて ±10 度")
    for table in PT.TABLES:
        if len(table) != P.N or any(len(row) != P.N for row in table):
            raise ValueError("表が 5 x 5 でない")
    flat = flat_index()
    if any(v != 0 for row in PT.TABLES[flat] for v in row):
        raise ValueError("THETA_FLAT の表が全部 0 でない（組立角 = 平ら）")
    return flat


def flat_index():
    matches = [i for i, t in enumerate(P.TABLE_THETA) if t == P.THETA_FLAT]
    if len(matches) != 1:
        raise ValueError("THETA_FLAT（組立角）に当たる表がちょうど 1 枚ない")
    return matches[0]


def center(table):
    return table[P.N // 2][P.N // 2]


def resolve_extreme(kind):
    """p（dip）/ b（bump）が使う表の番号を決める。名前 dip / bump を優先し、無ければ中央の高さで選ぶ。
    戻り値は (番号 or None, 根拠の文字列)"""
    name = "dip" if kind == "dip" else "bump"
    sign = -1 if kind == "dip" else 1
    if name in PT.NAMES:
        k = PT.NAMES.index(name)
        if sign * center(PT.TABLES[k]) > 0:
            return k, f"name '{name}' (center {center(PT.TABLES[k]):+.1f} mm)"
    candidates = [(sign * center(t), -k, k) for k, t in enumerate(PT.TABLES) if sign * center(t) > 0]
    if not candidates:
        return None, "no table with a " + ("negative" if sign < 0 else "positive") + " center height"
    best = max(candidates)[2]
    return best, f"extreme center height {center(PT.TABLES[best]):+.1f} mm (name '{name}' not usable)"


def find_safe_seconds(report):
    motion = report.get("motion", {}) if isinstance(report, dict) else {}
    for key in SAFE_KEYS:
        value = motion.get(key)
        if isinstance(value, dict):   # simulate.py は {"max": 秒, "byTransition": {...}} の形で書く
            value = value.get("max")
            key = key + ".max"
        if isinstance(value, (int, float)) and value > 0:
            return key, float(value)
    return None, None


def move_timing():
    """MIN_MOVE_MS（隣の表 1 枚ぶんの移動の最短）と、その出どころを決める"""
    info = {"safeKeysSearched": list(SAFE_KEYS), "simulateReport": None, "marginFactor": MARGIN}
    safe_key = safe_s = None
    verified = {}
    if SIMULATE_REPORT.is_file():
        report = json.loads(SIMULATE_REPORT.read_text(encoding="utf-8"))
        info["simulateReport"] = record(SIMULATE_REPORT)
        safe_key, safe_s = find_safe_seconds(report)
        pairs = report.get("motion", {}).get("tablePairs", {})
        fastest = report.get("motion", {}).get("fastestSummary", {})
        verified = {"tablePairsDurationS": pairs.get("durationS"),
                    "tablePairsAllContactFeasible": pairs.get("allContactFeasible"),
                    "fastestLiftOffRuns": fastest.get("liftOffRuns")}
    info["verifiedInSimulation"] = verified
    if safe_s is not None:
        floor_ms = int(round(safe_s * 1000 * MARGIN))
        ms = max(DEMO_MOVE_MS, floor_ms)
        info.update(source="simulate_report.json", key=f"motion.{safe_key}", safeSecondsPerTableStep=safe_s,
                    noLiftFloorMs=floor_ms, demoMoveMs=DEMO_MOVE_MS, defaultUsed=False)
    else:
        ms = DEFAULT_MOVE_MS
        info.update(source=f"default {DEFAULT_MOVE_MS} ms per table step (simulate_report.json has no safe minimum time yet; not verified in simulation)",
                    key=None, safeSecondsPerTableStep=None, defaultUsed=True)
    info["minMoveMs"] = ms
    return ms, info


def heights_comment(k, table, flat):
    theta = P.TABLE_THETA[k]
    mark = "  <- flat = assembly angle" if k == flat else ""
    lines = [f"//   table {k}  {PT.NAMES[k]:<8} servo {theta:6.1f} deg  {PT.LABELS_JA[k]}{mark}"]
    for j in range(P.N):
        lines.append("//     j%d (Y): " % j + " ".join(f"{table[j][i]:+.1f}" for i in range(P.N)) + "   (i = 0..4 along X, mm)")
    return "\n".join(lines)


TEMPLATE = r'''// tangible-pixel-cube: SG92R one-servo, __K__ mechanically programmed 5x5 height tables.
// GENERATED by models/tangible-pixel-cube/firmware.py from patterns.py and params.py. Do not edit by hand.
// A0 signal. External regulated 4.8 V. Controller and servo share GND. No position/force feedback is present.
// Start at 90 deg (= assembly angle, every pixel flush) BEFORE assembly. Serial 115200 bps.
//
// Tables (servo angle ascending; heights in mm, + = out, - = in):
__TABLES_COMMENT__
//
// Moving to a table sweeps the servo angle continuously, so a non-adjacent target passes through the
// tables in between in cam order (table 0 .. table __LAST__ in servo-angle order). Example: 0 -> 4 passes 1, 2, 3.
// The pass-through is physical, not a stop: the servo does not dwell on the intermediate tables.
//
// Commands:
//   0..__LAST__  move to that table          p  push-in show: flat -> "__PUSH_NAME__" -> flat
//   b  push-out show: flat -> "__BUMP_NAME__" -> flat
//   g  play every table in order, then return to flat      s  hold at the current angle
//   c  move to the assembly angle (90 deg)   ?  list
//   a<deg>  e.g. a90.5 + newline: follow that angle (bar / slider). The servo slews toward it at no more than the
//           speed of one table step per MIN_MOVE_MS, so a fast drag cannot lift the pixels off the cams. The PC bar
//           page models/tangible-pixel-cube/demo/bar.html sends this. Any other command ends the following.
//   +  phase trim +0.25 deg    -  phase trim -0.25 deg    z  phase trim 0    w  save the phase trim to EEPROM
//   The trim moves the servo at once (to the current table angle, or 90 deg). Range +-10 deg, and every commanded
//   angle with the trim must stay inside the servo working range. Use it to seat the phase jig, then save with w.
//
// Move time is proportional to the angle travelled, but never shorter than MIN_MOVE_MS (one table step).
// MIN_MOVE_MS source: __TIMING_SOURCE__
#include <Servo.h>
#include <EEPROM.h>

Servo motor;
constexpr uint8_t SIGNAL_PIN = A0;
constexpr uint8_t TABLE_COUNT = __K__;
constexpr float POSES[TABLE_COUNT] = {__POSES__};
constexpr float ASSEMBLY_DEG = __FLAT_DEG__f;
constexpr uint8_t FLAT_INDEX = __FLAT_INDEX__;
constexpr float SERVO_MIN_DEG = __SERVO_MIN__f;
constexpr float SERVO_MAX_DEG = __SERVO_MAX__f;

// Sequences of table numbers. g: every table, then back to flat. p / b: flat, extreme table, flat.
constexpr uint8_t SEQ_ALL[] = {__SEQ_ALL__};
__SEQ_SHOWS__
constexpr uint32_t DWELL_MS = __DWELL_MS__;

// Move time. __TABLE_STEP__ deg is the table spacing; one table step takes MIN_MOVE_MS (the fastest move allowed).
// MS_PER_DEG caps the average servo speed at __TABLE_STEP__ deg / MIN_MOVE_MS. The quintic ease peaks at 1.875x that.
constexpr uint32_t MIN_MOVE_MS = __MIN_MOVE_MS__;
constexpr float TABLE_STEP_DEG = __TABLE_STEP__f;
constexpr float MS_PER_DEG = static_cast<float>(MIN_MOVE_MS) / TABLE_STEP_DEG;

// Phase trim: added to every commanded angle; keeps every relative angle equal. The horn spline is 18 deg per tooth and the
// receiver's half gear can sit up to +-9 deg off the design, the same for all axes. Seat the phase jig with + / -, then save with w.
// PHASE_TRIM_DEG is the compile-time default, used when the EEPROM holds no valid value.
constexpr float PHASE_TRIM_DEG = 0.0f;
static_assert(PHASE_TRIM_DEG >= -10.0f && PHASE_TRIM_DEG <= 10.0f,
              "Check horn mounting if the required phase trim exceeds 10 degrees.");
// Every commanded angle (including the trim) stays inside the servo working range from params.py.
__RANGE_ASSERTS__
static_assert(ASSEMBLY_DEG + PHASE_TRIM_DEG >= SERVO_MIN_DEG && ASSEMBLY_DEG + PHASE_TRIM_DEG <= SERVO_MAX_DEG,
              "Assembly angle with phase trim is outside the servo working range.");

constexpr float TRIM_STEP_DEG = __TRIM_STEP__f;
constexpr float TRIM_LIMIT_DEG = __TRIM_LIMIT__f;
// EEPROM: [0] magic, [1] trim in quarter degrees (int8), [2] bitwise complement of [1]. Written only by w (EEPROM.update).
constexpr int EEPROM_ADDRESS = 0;
constexpr uint8_t EEPROM_MAGIC = 0xA7;
constexpr float EEPROM_UNIT_DEG = 0.25f;

constexpr uint16_t PULSE_MIN_US = 544;    // Servo library default for attach(pin)
constexpr uint16_t PULSE_MAX_US = 2400;

float phaseTrim = PHASE_TRIM_DEG;
bool trimFromEeprom = false;
float commanded = ASSEMBLY_DEG;
float startAngle = ASSEMBLY_DEG;
float targetAngle = ASSEMBLY_DEG;
uint32_t startedAt = 0;
uint32_t moveMs = 0;
uint32_t dwellFrom = 0;
uint32_t lastTick = 0;
bool moving = false;
bool dwelling = false;
bool following = false;
float followTarget = ASSEMBLY_DEG;
const uint8_t* sequence = nullptr;
uint8_t sequenceLength = 0;
uint8_t sequencePos = 0;

// Same mapping as Servo::write(), kept in microseconds so the quintic ease is not rounded to whole degrees.
void writeAngle(float logicalAngle) {
  float angle = logicalAngle + phaseTrim;
  if (angle < SERVO_MIN_DEG) angle = SERVO_MIN_DEG;
  if (angle > SERVO_MAX_DEG) angle = SERVO_MAX_DEG;
  motor.writeMicroseconds(static_cast<int>(PULSE_MIN_US + angle * (PULSE_MAX_US - PULSE_MIN_US) / 180.0f + 0.5f));
}

float ease(float u) {
  if (u <= 0.0f) return 0.0f;
  if (u >= 1.0f) return 1.0f;
  return u * u * u * (10.0f + u * (-15.0f + 6.0f * u));
}

void startMove(float angle) {
  startAngle = commanded;
  targetAngle = angle;
  const float distance = angle > commanded ? angle - commanded : commanded - angle;
  if (distance < 0.05f) {
    moveMs = 0;
  } else {
    const float ms = distance * MS_PER_DEG;
    moveMs = ms < static_cast<float>(MIN_MOVE_MS) ? MIN_MOVE_MS : static_cast<uint32_t>(ms + 0.5f);
  }
  startedAt = millis();
  moving = true;
  dwelling = false;
}

void stopAll() {
  moving = false;
  dwelling = false;
  following = false;
  sequence = nullptr;
  sequenceLength = 0;
}

void startSequence(const uint8_t* steps, uint8_t length) {
  if (length == 0) {
    Serial.println(F("That show needs a table this build does not have."));
    return;
  }
  stopAll();
  sequence = steps;
  sequenceLength = length;
  sequencePos = 0;
  startMove(POSES[sequence[0]]);
}

// A trim is usable when it is inside +-TRIM_LIMIT_DEG and every commanded angle (all tables and the assembly angle) stays in range.
bool trimFits(float trim) {
  if (!(trim >= -TRIM_LIMIT_DEG && trim <= TRIM_LIMIT_DEG)) return false;
  if (ASSEMBLY_DEG + trim < SERVO_MIN_DEG || ASSEMBLY_DEG + trim > SERVO_MAX_DEG) return false;
  for (uint8_t i = 0; i < TABLE_COUNT; i++) {
    if (POSES[i] + trim < SERVO_MIN_DEG || POSES[i] + trim > SERVO_MAX_DEG) return false;
  }
  return true;
}

bool loadTrim(float& trim) {
  if (EEPROM.read(EEPROM_ADDRESS) != EEPROM_MAGIC) return false;
  const uint8_t raw = EEPROM.read(EEPROM_ADDRESS + 1);
  if (static_cast<uint8_t>(~raw) != EEPROM.read(EEPROM_ADDRESS + 2)) return false;
  const float value = static_cast<int8_t>(raw) * EEPROM_UNIT_DEG;
  if (!trimFits(value)) return false;
  trim = value;
  return true;
}

void saveTrim() {
  const int8_t quarters = static_cast<int8_t>(phaseTrim / EEPROM_UNIT_DEG + (phaseTrim < 0.0f ? -0.5f : 0.5f));
  const uint8_t raw = static_cast<uint8_t>(quarters);
  EEPROM.update(EEPROM_ADDRESS, EEPROM_MAGIC);
  EEPROM.update(EEPROM_ADDRESS + 1, raw);
  EEPROM.update(EEPROM_ADDRESS + 2, static_cast<uint8_t>(~raw));
  trimFromEeprom = true;
}

void printTrim() {
  Serial.print(F("Phase trim: "));
  Serial.print(phaseTrim, 2);
  Serial.println(trimFromEeprom ? F(" deg (EEPROM)") : F(" deg (compile-time default or unsaved)"));
}

void changeTrim(float trim) {
  if (!trimFits(trim)) {
    Serial.println(F("Trim limit reached (+-10 deg, and every angle must stay inside the servo range)."));
    return;
  }
  phaseTrim = trim;
  writeAngle(commanded);
  printTrim();
}

void printHelp() {
  Serial.println(F("tangible-pixel-cube. 90 deg = flat = assembly angle."));
__HELP_LINES__
  Serial.println(F("p: push-in show, b: push-out show, g: all tables, c: assembly 90, s: hold, ?: list"));
  Serial.println(F("+ / -: trim +-0.25 deg, z: trim 0, w: save trim to EEPROM"));
  Serial.println(F("a<deg>: follow that angle (bar), e.g. a90.5"));
  printTrim();
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);
  trimFromEeprom = loadTrim(phaseTrim);
  motor.attach(SIGNAL_PIN);
  writeAngle(ASSEMBLY_DEG);
  lastTick = millis();
  printHelp();
}

void handleCommand(char command) {
  if (command == 'a') {
    // Bar. Slew-limited in loop(); a new value only moves the target, so a fast drag never jumps the cam.
    float angle = Serial.parseFloat();
    if (angle < SERVO_MIN_DEG) angle = SERVO_MIN_DEG;
    if (angle > SERVO_MAX_DEG) angle = SERVO_MAX_DEG;
    if (!following) {
      stopAll();
      following = true;
    }
    followTarget = angle;
    return;
  }
  if (command >= '0' && command < static_cast<char>('0' + TABLE_COUNT)) {
    stopAll();
    startMove(POSES[command - '0']);
    Serial.print(F("table "));
    Serial.println(command);
  } else if (command == 'p') {
    startSequence(SEQ_PUSH, sizeof(SEQ_PUSH));
  } else if (command == 'b') {
    startSequence(SEQ_BUMP, sizeof(SEQ_BUMP));
  } else if (command == 'g') {
    startSequence(SEQ_ALL, sizeof(SEQ_ALL));
  } else if (command == 'c') {
    stopAll();
    startMove(ASSEMBLY_DEG);
  } else if (command == 's') {
    stopAll();
    writeAngle(commanded);
    Serial.println(F("Holding the current angle."));
  } else if (command == '+') {
    changeTrim(phaseTrim + TRIM_STEP_DEG);
  } else if (command == '-') {
    changeTrim(phaseTrim - TRIM_STEP_DEG);
  } else if (command == 'z') {
    changeTrim(0.0f);
  } else if (command == 'w') {
    saveTrim();
    Serial.print(F("Saved. "));
    printTrim();
  } else if (command == '?') {
    printHelp();
  }
}

void loop() {
  while (Serial.available()) handleCommand(static_cast<char>(Serial.read()));
  const uint32_t now = millis();
  if (static_cast<uint32_t>(now - lastTick) < 10UL) return;
  lastTick = now;
  if (following) {
    // Same average speed cap as a table move (TABLE_STEP_DEG per MIN_MOVE_MS), as a straight slew toward the bar.
    const float maxStep = 10.0f / MS_PER_DEG;   // 10 ms tick / (ms per deg)
    const float gap = followTarget - commanded;
    commanded += gap > maxStep ? maxStep : (gap < -maxStep ? -maxStep : gap);
    writeAngle(commanded);
  } else if (moving) {
    const uint32_t elapsed = now - startedAt;
    if (elapsed >= moveMs) {
      commanded = targetAngle;
      moving = false;
      if (sequence != nullptr) {
        dwelling = true;
        dwellFrom = now;
      }
    } else {
      commanded = startAngle + (targetAngle - startAngle) * ease(static_cast<float>(elapsed) / static_cast<float>(moveMs));
    }
    writeAngle(commanded);
  } else if (dwelling && static_cast<uint32_t>(now - dwellFrom) >= DWELL_MS) {
    dwelling = false;
    sequencePos++;
    if (sequencePos >= sequenceLength) {
      sequence = nullptr;
      Serial.println(F("Show finished."));
    } else {
      startMove(POSES[sequence[sequencePos]]);
    }
  }
}
'''


def fmt(v):
    """C の float リテラル。整数値でも 22.0 の形にする"""
    return repr(float(v))


def build_source(flat, push, bump, timing_ms, timing_info):
    k = P.K
    thetas = list(P.TABLE_THETA)
    step = max(b - a for a, b in zip(thetas, thetas[1:])) if k > 1 else 1.0
    show_blocks = []
    for const, idx in (("SEQ_PUSH", push), ("SEQ_BUMP", bump)):
        if idx is None:
            show_blocks.append(f"constexpr uint8_t {const}[1] = {{0}};  // unavailable: no matching table. length is reported as 0 below")
        else:
            show_blocks.append(f"constexpr uint8_t {const}[] = {{{flat}, {idx}, {flat}}};  // flat -> table {idx} ({PT.NAMES[idx]}) -> flat")
    # 該当する表が無いときは長さ 0 を返す版にする（sizeof(SEQ_*) ではなく LEN 定数を使うため上書き）
    source = TEMPLATE
    source = source.replace("startSequence(SEQ_PUSH, sizeof(SEQ_PUSH))", "startSequence(SEQ_PUSH, SEQ_PUSH_LEN)")
    source = source.replace("startSequence(SEQ_BUMP, sizeof(SEQ_BUMP))", "startSequence(SEQ_BUMP, SEQ_BUMP_LEN)")
    show_blocks.append(f"constexpr uint8_t SEQ_PUSH_LEN = {0 if push is None else 3};")
    show_blocks.append(f"constexpr uint8_t SEQ_BUMP_LEN = {0 if bump is None else 3};")
    range_asserts = "\n".join(
        f'static_assert(POSES[{i}] + PHASE_TRIM_DEG >= SERVO_MIN_DEG && POSES[{i}] + PHASE_TRIM_DEG <= SERVO_MAX_DEG,\n'
        f'              "Table {i} angle with phase trim is outside the servo working range.");'
        for i in range(k))
    help_lines = "\n".join(
        f'  Serial.println(F("{i}: {PT.NAMES[i]}  servo {P.TABLE_THETA[i]:g} deg{"  (flat)" if i == flat else ""}"));'
        for i in range(k))
    replacements = {
        "__K__": str(k),
        "__LAST__": str(k - 1),
        "__TABLES_COMMENT__": "\n".join(heights_comment(i, PT.TABLES[i], flat) for i in range(k)),
        "__PUSH_NAME__": "none" if push is None else PT.NAMES[push],
        "__BUMP_NAME__": "none" if bump is None else PT.NAMES[bump],
        "__TIMING_SOURCE__": timing_info["source"] + (f" ({timing_info['key']} x {MARGIN})" if timing_info["key"] else ""),
        "__POSES__": ", ".join(fmt(t) + "f" for t in thetas),
        "__FLAT_DEG__": fmt(P.THETA_FLAT),
        "__FLAT_INDEX__": str(flat),
        "__SERVO_MIN__": fmt(P.SERVO_MIN_DEG),
        "__SERVO_MAX__": fmt(P.SERVO_MAX_DEG),
        "__SEQ_ALL__": ", ".join(str(i) for i in range(k)) + f", {flat}",
        "__SEQ_SHOWS__": "\n".join(show_blocks),
        "__DWELL_MS__": f"{DWELL_MS}UL",
        "__TRIM_STEP__": fmt(TRIM_STEP_DEG),
        "__TRIM_LIMIT__": fmt(PHASE_TRIM_LIMIT_DEG),
        "__MIN_MOVE_MS__": f"{timing_ms}UL",
        "__TABLE_STEP__": fmt(step),
        "__RANGE_ASSERTS__": range_asserts,
        "__HELP_LINES__": help_lines,
    }
    for key, value in replacements.items():
        source = source.replace(key, value)
    leftover = re.findall(r"__[A-Z_]+__", source)
    if leftover:
        raise ValueError(f"未置換のプレースホルダが残っている: {sorted(set(leftover))}")
    return source, step


def main():
    flat = check_inputs()
    push, push_basis = resolve_extreme("dip")
    bump, bump_basis = resolve_extreme("bump")
    timing_ms, timing_info = move_timing()
    source, step = build_source(flat, push, bump, timing_ms, timing_info)
    SOURCE.parent.mkdir(exist_ok=True)
    atomic_text(SOURCE, source)
    source_sha = digest(SOURCE)
    bar_data = {"min": P.SERVO_MIN_DEG, "max": P.SERVO_MAX_DEG, "flat": P.THETA_FLAT,
                "tables": [{"name": PT.NAMES[k], "label": PT.LABELS_JA[k], "deg": P.TABLE_THETA[k],
                            "heights": PT.TABLES[k]} for k in range(P.K)]}
    bar = BAR_TEMPLATE.read_text(encoding="utf-8")
    for key, value in {"__DATA__": json.dumps(bar_data, ensure_ascii=False), "__MIN__": f"{P.SERVO_MIN_DEG:g}",
                       "__MAX__": f"{P.SERVO_MAX_DEG:g}", "__FLAT__": f"{P.THETA_FLAT:g}",
                       "__MOVE__": str(timing_ms)}.items():
        bar = bar.replace(key, value)
    if re.search(r"__[A-Z_]+__", bar):
        raise ValueError("bar.html に未置換のプレースホルダが残っている")
    atomic_text(BAR_OUTPUT, bar)

    # compile_demo.py が書いたコンパイル結果は、同じ .ino（SHA 一致）のときだけ残す
    compile_section = {"status": "not-compiled"}
    if REPORT.is_file():
        try:
            previous = json.loads(REPORT.read_text(encoding="utf-8")).get("compile")
            if previous and previous.get("sourceSha256") == source_sha:
                compile_section = previous
        except (ValueError, OSError):
            pass

    sim_hashes = {}
    if SIMULATE_REPORT.is_file():
        sim_hashes = json.loads(SIMULATE_REPORT.read_text(encoding="utf-8")).get("sourceHashes", {})
    inputs = [record(HERE / "patterns.py"), record(HERE / "params.py"), record(Path(__file__))]
    fresh = {}
    for item in inputs[:2]:
        recorded = sim_hashes.get(item["file"])
        fresh[item["file"]] = None if recorded is None else recorded == item["sha256"]
    report = {
        "version": 1,
        "model": "tangible-pixel-cube",
        "generator": "models/tangible-pixel-cube/firmware.py",
        "source": record(SOURCE), "bar": record(BAR_OUTPUT),
        "inputs": inputs,
        "simulateReportSourceHashesMatch": fresh,
        "angles": {
            "assemblyDeg": P.THETA_FLAT, "flatIndex": flat, "tableStepDeg": step,
            "servoRangeDeg": [P.SERVO_MIN_DEG, P.SERVO_MAX_DEG],
            "phaseTrimDeg": 0.0, "phaseTrimAllowedDeg": [-PHASE_TRIM_LIMIT_DEG, PHASE_TRIM_LIMIT_DEG],
        },
        "phaseTrim": {
            "compileDefaultDeg": 0.0, "runtimeStepDeg": TRIM_STEP_DEG,
            "allowedDeg": [-PHASE_TRIM_LIMIT_DEG, PHASE_TRIM_LIMIT_DEG],
            "eeprom": {"address": 0, "layout": "[magic 0xA7][int8 quarter-degrees][bitwise complement]",
                       "unitDeg": 0.25, "writtenBy": "w only (EEPROM.update)",
                       "invalidFallback": "compile-time PHASE_TRIM_DEG"},
        },
        "tables": [{"index": k, "name": PT.NAMES[k], "labelJa": PT.LABELS_JA[k], "servoDeg": P.TABLE_THETA[k],
                    "heightsMm": PT.TABLES[k]} for k in range(P.K)],
        "shows": {
            "push": {"command": "p", "tableIndex": push, "basis": push_basis,
                     "sequence": None if push is None else [flat, push, flat]},
            "bump": {"command": "b", "tableIndex": bump, "basis": bump_basis,
                     "sequence": None if bump is None else [flat, bump, flat]},
            "all": {"command": "g", "sequence": list(range(P.K)) + [flat]},
            "dwellMs": DWELL_MS,
        },
        "moveTiming": timing_info,
        "commands": {"0-%d" % (P.K - 1): "move to table", "p": "push-in show", "b": "push-out show",
                     "g": "all tables then flat", "s": "hold", "c": "assembly angle", "?": "list",
                     "+": "trim +0.25 deg", "-": "trim -0.25 deg", "z": "trim 0", "w": "save trim to EEPROM"},
        "compile": compile_section,
        "hardwareTested": False,
        "hardwareLimitation": "マイコンへの書き込みと SG92R の通電は未実施。位相補正 PHASE_TRIM_DEG は実物で決める。",
    }
    REPORT.parent.mkdir(exist_ok=True)
    atomic_text(REPORT, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"source": str(SOURCE.relative_to(ROOT)), "sha256": source_sha,
                      "minMoveMs": timing_ms, "minMoveSource": timing_info["source"],
                      "push": push, "bump": bump, "flat": flat}, ensure_ascii=False))


if __name__ == "__main__":
    main()
