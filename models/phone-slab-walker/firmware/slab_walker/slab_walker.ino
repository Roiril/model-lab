// スマホ板ロボットの Leonardo ファーム。
//
// スマホ（または PC）→ USB CDC → Leonardo → Serial1（1Mbps）→ 74HC125 → STS3215 のバス
// 配線は ../../README.md。実機では未確認（コンパイルのみ確認済み）。
//
// SO-101 から借りたサーボを壊さないよう、ID と EEPROM は書き換えない。
// 可動範囲の制限は Lock=1 のまま RAM 側へ書く（電源を切ると元に戻る）。
//
// 1 行 1 命令（115200 の設定は USB CDC では無視される）:
//   ?            状態を 1 行返す
//   Z            今の姿勢を「脚がまっすぐ」として覚える（EEPROM に保存）
//   H            まっすぐへ戻す
//   P l r ms     左右の脚を deg へ ms かけて動かす（前が正）
//   W n          前へ n 周期歩く（gait.h の波形）
//   B n          後ろへ n 周期歩く
//   L n / R n    左 / 右へ曲がりながら n 周期歩く
//   T d          歩きながら曲げる量（左 +d、右 -d。±12 まで）。スマホのジャイロがこれを送る
//   S            止めて、その場で保持
//   O            トルクを切る（手で動かせる）
//   I l r        使うサーボの ID を指定（EEPROM に保存）
//   D l r        回る向きを 1 か -1 で指定（EEPROM に保存）

#include <EEPROM.h>
#include "gait.h"

// --- 配線 -----------------------------------------------------------------
// D2 → 74HC125 の /OE（LOW で送信）。起動中はプルアップで HIGH のまま
const uint8_t PIN_TX_ENABLE_N = 2;
#define TX_ON() (PORTD &= ~_BV(PD1))   // D2 = PD1。digitalWrite より速く受信へ戻す
#define TX_OFF() (PORTD |= _BV(PD1))

// --- STS3215 のメモリ表（mycobot-lab/src/robots/so101/sts3215.py と同じ出典）---
const uint8_t ADDR_MIN_LIMIT = 9;
const uint8_t ADDR_TORQUE = 40;
const uint8_t ADDR_ACC = 41;
const uint8_t ADDR_GOAL = 42;
const uint8_t ADDR_LOCK = 55;
const uint8_t ADDR_PRESENT = 56;   // 位置 2, 速度 2, 負荷 2, 電圧 1, 温度 1
const uint8_t INST_PING = 1, INST_READ = 2, INST_WRITE = 3;
const unsigned long REPLY_TIMEOUT_US = 3000;
const long SPEED_MAX = 3400;                 // 無負荷の最大（45rpm 相当）
const uint8_t STATUS_OVERLOAD_OR_HEAT = 0x2C;  // 応答のエラー: 0x04 過熱、0x08 過電流、0x20 過負荷

// --- 安全 -----------------------------------------------------------------
const int LIMIT_DEG = 45;                  // まっすぐからの最大（機構の可動域より狭い）
const uint8_t TEMP_STOP_C = 65;            // サーボの保護 70℃ の手前
const unsigned long HEALTH_EVERY_MS = 1000;
const int8_t TRIM_MAX_DEG = 12;
// まっすぐの位置がこの外だと、片側の振りが 0〜4095 の端に当たる
const int16_t CENTER_MIN = 512 + 164, CENTER_MAX = 4095 - 512 - 164;   // 164 = 操舵の分
const int EEPROM_MAGIC_ADDR = 0, EEPROM_ID_ADDR = 1, EEPROM_CENTER_ADDR = 3, EEPROM_DIR_ADDR = 7;
const uint8_t EEPROM_MAGIC = 0x5B;

// 左の脚は軸の向きが右と逆なので符号を反転する（実機で逆なら D 命令で直す）
int8_t direction[2] = {-1, 1};

uint8_t servoId[2] = {0, 0};
int16_t centerRaw[2] = {2048, 2048};
int16_t lastGoal[2] = {2048, 2048};
uint8_t lastStatus[2] = {0xFF, 0xFF};

enum Mode : uint8_t { IDLE, WALK };
Mode mode = IDLE;
int8_t gaitSign = 1;
int8_t trimDeg = 0;
bool trimFromGait = false;     // L / R で入れた操舵は歩き終わりで戻す
uint8_t gaitIndex = 0;
uint16_t cyclesLeft = 0;
unsigned long nextKeyAt = 0;
unsigned long nextHealthAt = 0;
char line[40];
uint8_t lineLen = 0;

// --- バス ------------------------------------------------------------------
static void busSend(uint8_t id, uint8_t inst, uint8_t addr, const uint8_t *data, uint8_t n) {
  while (Serial1.available()) Serial1.read();
  uint8_t len = n + 3;
  uint8_t sum = id + len + inst + addr;
  TX_ON();
  Serial1.write(0xFF);
  Serial1.write(0xFF);
  Serial1.write(id);
  Serial1.write(len);
  Serial1.write(inst);
  Serial1.write(addr);
  for (uint8_t i = 0; i < n; i++) {
    Serial1.write(data[i]);
    sum += data[i];
  }
  Serial1.write((uint8_t)~sum);
  Serial1.flush();     // 最後のビットが出終わるまで待つ
  TX_OFF();
  // RX は常にバスを聞いているので、自分の送信の折り返しが入っている
  delayMicroseconds(5);
}

// 折り返しを読み飛ばして応答を受ける。戻り値はデータのバイト数（失敗は -1）
static int busReply(uint8_t id, uint8_t *out, uint8_t want, uint8_t echoBytes) {
  unsigned long start = micros();
  uint8_t state = 0, skipped = 0, len = 0, got = 0, sum = 0;
  while (micros() - start < REPLY_TIMEOUT_US) {
    if (!Serial1.available()) continue;
    uint8_t b = Serial1.read();
    if (skipped < echoBytes) {
      skipped++;
      continue;
    }
    switch (state) {
      case 0: state = (b == 0xFF) ? 1 : 0; break;
      case 1: state = (b == 0xFF) ? 2 : 0; break;
      case 2:
        if (b == 0xFF) break;              // ヘッダの FF が 3 つ続いた
        if (b != id) return -1;
        sum = b;
        state = 3;
        break;
      case 3:
        len = b;
        sum += b;
        if (len < 2 || len - 2 > want) return -1;
        state = 4;
        break;
      case 4:
        lastStatus[id == servoId[0] ? 0 : 1] = b;
        sum += b;
        state = 5;
        if (len == 2) state = 6;
        break;
      case 5:
        out[got++] = b;
        sum += b;
        if (got == len - 2) state = 6;
        break;
      case 6:
        return (uint8_t)~sum == b ? got : -1;
    }
  }
  return -1;
}

static bool pingRaw(uint8_t id) {
  while (Serial1.available()) Serial1.read();
  const uint8_t len = 2;
  const uint8_t sum = ~(id + len + INST_PING);
  TX_ON();
  Serial1.write(0xFF);
  Serial1.write(0xFF);
  Serial1.write(id);
  Serial1.write(len);
  Serial1.write(INST_PING);
  Serial1.write(sum);
  Serial1.flush();
  TX_OFF();
  uint8_t none[1];
  return busReply(id, none, 0, 6) == 0;
}

static void writeByte(uint8_t id, uint8_t addr, uint8_t value) {
  busSend(id, INST_WRITE, addr, &value, 1);
  uint8_t none[1];
  busReply(id, none, 0, 8);
}

static void writeWords(uint8_t id, uint8_t addr, const uint16_t *words, uint8_t n) {
  uint8_t data[8];
  for (uint8_t i = 0; i < n; i++) {
    data[2 * i] = words[i] & 0xFF;
    data[2 * i + 1] = words[i] >> 8;
  }
  busSend(id, INST_WRITE, addr, data, 2 * n);
  uint8_t none[1];
  busReply(id, none, 0, 7 + 2 * n);
}

static bool readBlock(uint8_t id, uint8_t addr, uint8_t *out, uint8_t n) {
  busSend(id, INST_READ, addr, &n, 1);
  return busReply(id, out, n, 8) == n;
}

// STS は最上位ビットが符号（2 の補数ではない）
static int16_t signMagnitude(uint16_t raw) {
  return (raw & 0x8000) ? -(int16_t)(raw & 0x7FFF) : (int16_t)raw;
}

static int16_t degToTicks(float deg) { return (int16_t)(deg * 4096.0f / 360.0f); }

// --- 動き -------------------------------------------------------------------
static void moveLeg(uint8_t side, float deg, uint16_t ms) {
  if (!servoId[side]) return;
  deg = constrain(deg, -LIMIT_DEG, LIMIT_DEG);
  int16_t goal = centerRaw[side] + direction[side] * degToTicks(deg);
  goal = constrain(goal, 0, 4095);
  // SO-101 の STS は目標速度 [step/s] で動かす。ms で着く速さを計算する
  long ticks = labs((long)goal - lastGoal[side]);
  uint16_t speed = ms ? (uint16_t)constrain(ticks * 1000L / ms, 1L, SPEED_MAX) : (uint16_t)SPEED_MAX;
  const uint16_t words[3] = {(uint16_t)goal, 0, speed};   // 位置・時間（使わない）・速度
  writeWords(servoId[side], ADDR_GOAL, words, 3);
  lastGoal[side] = goal;
}

static void setTorque(bool on) {
  for (uint8_t side = 0; side < 2; side++)
    if (servoId[side]) writeByte(servoId[side], ADDR_TORQUE, on ? 1 : 0);
}

// 今の位置を目標にしてからトルクを入れる（入れた瞬間に跳ねないため）
static void holdHere() {
  for (uint8_t side = 0; side < 2; side++) {
    if (!servoId[side]) continue;
    uint8_t b[2];
    if (readBlock(servoId[side], ADDR_PRESENT, b, 2)) {
      const uint16_t raw = (uint16_t)(b[0] | (b[1] << 8));
      const uint16_t words[3] = {raw, 0, 0};
      writeWords(servoId[side], ADDR_GOAL, words, 3);
      lastGoal[side] = (int16_t)raw;
    }
  }
  setTorque(true);
}

static void stopMotion() {
  mode = IDLE;
  trimDeg = 0;
  trimFromGait = false;
  holdHere();
}

// 歩いている途中に同じ向きの命令が来たら、波形を切らずに残りの周期だけ延ばす。
// スマホが定期的に送り直し、途絶えたら数周期で止まる
static void startGait(int8_t sign, int8_t trim, bool trimEnds, uint16_t cycles) {
  const bool continuing = mode == WALK && gaitSign == sign;
  gaitSign = sign;
  trimDeg = trim;
  trimFromGait = trimEnds;
  cyclesLeft = cycles;
  if (continuing) return;
  gaitIndex = 0;
  nextKeyAt = millis();
  nextHealthAt = nextKeyAt + HEALTH_EVERY_MS;
  mode = WALK;
}

static void stepGait() {
  if (mode != WALK || (long)(millis() - nextKeyAt) < 0) return;
  if (gaitIndex >= GAIT_WALK_LEN) {
    gaitIndex = 0;
    if (cyclesLeft <= 1) {
      moveLeg(0, 0, 600);
      moveLeg(1, 0, 600);
      mode = IDLE;
      if (trimFromGait) trimDeg = 0;
      return;
    }
    cyclesLeft--;
  }
  GaitKey key;
  memcpy_P(&key, &GAIT_WALK[gaitIndex], sizeof(key));
  gaitIndex++;
  // 操舵は左右の脚の中心を逆へずらす
  moveLeg(0, gaitSign * key.left + trimDeg, key.ms);
  moveLeg(1, gaitSign * key.right - trimDeg, key.ms);
  nextKeyAt += key.ms;
}

// 歩いている間も熱とエラーを見る。スマホが落ちても止まれるように、ここはファーム側で持つ
static void checkHealth() {
  if (mode != WALK || (long)(millis() - nextHealthAt) < 0) return;
  nextHealthAt += HEALTH_EVERY_MS;
  for (uint8_t side = 0; side < 2; side++) {
    uint8_t b[8];
    if (!servoId[side] || !readBlock(servoId[side], ADDR_PRESENT, b, 8)) continue;
    if (b[7] >= TEMP_STOP_C || (lastStatus[side] & STATUS_OVERLOAD_OR_HEAT)) {
      mode = IDLE;
      setTorque(false);
      Serial.print(F("{\"stopped\":"));
      Serial.print(b[7] >= TEMP_STOP_C ? F("\"temperature\"") : F("\"servo_error\""));
      Serial.print(F(",\"side\":"));
      Serial.print(side);
      Serial.print(F(",\"tempC\":"));
      Serial.print(b[7]);
      Serial.print(F(",\"status\":"));
      Serial.print(lastStatus[side]);
      Serial.println('}');
      return;
    }
  }
}

// --- 起動 -------------------------------------------------------------------
static void loadSettings() {
  if (EEPROM.read(EEPROM_MAGIC_ADDR) == EEPROM_MAGIC) {
    servoId[0] = EEPROM.read(EEPROM_ID_ADDR);
    servoId[1] = EEPROM.read(EEPROM_ID_ADDR + 1);
    EEPROM.get(EEPROM_CENTER_ADDR, centerRaw);
    EEPROM.get(EEPROM_DIR_ADDR, direction);
  }
}

static void saveSettings() {
  EEPROM.update(EEPROM_MAGIC_ADDR, EEPROM_MAGIC);
  EEPROM.update(EEPROM_ID_ADDR, servoId[0]);
  EEPROM.update(EEPROM_ID_ADDR + 1, servoId[1]);
  EEPROM.put(EEPROM_CENTER_ADDR, centerRaw);
  EEPROM.put(EEPROM_DIR_ADDR, direction);
}

static void findServos() {
  uint8_t found = 0;
  uint8_t ids[2] = {0, 0};
  for (uint8_t id = 1; id <= 12 && found < 2; id++)
    if (pingRaw(id)) ids[found++] = id;
  // 保存した ID が両方いるなら、それを優先する
  bool savedOk = servoId[0] && servoId[1] && pingRaw(servoId[0]) && pingRaw(servoId[1]);
  if (!savedOk) {
    servoId[0] = ids[0];
    servoId[1] = ids[1];
  }
}

static void openLimits() {
  // Lock=1 のまま書くと電源断で消える（memory-sts の記載）。SO-101 の校正値を壊さない
  const uint16_t limits[2] = {0, 4095};
  for (uint8_t side = 0; side < 2; side++) {
    if (!servoId[side]) continue;
    writeByte(servoId[side], ADDR_LOCK, 1);
    writeWords(servoId[side], ADDR_MIN_LIMIT, limits, 2);
    // 単位は 100 step/s²。小さいと 90ms ごとの折れ線に追いつかない（60 で 527°/s²、254 で 2232°/s²）
    writeByte(servoId[side], ADDR_ACC, 254);
  }
}

// --- 状態 -------------------------------------------------------------------
static void printState() {
  Serial.print(F("{\"mode\":"));
  Serial.print(mode == WALK ? F("\"walk\"") : F("\"idle\""));
  Serial.print(F(",\"dir\":["));
  Serial.print(direction[0]);
  Serial.print(',');
  Serial.print(direction[1]);
  Serial.print(']');
  for (uint8_t side = 0; side < 2; side++) {
    Serial.print(side == 0 ? F(",\"left\":") : F(",\"right\":"));
    uint8_t b[8];
    if (!servoId[side] || !readBlock(servoId[side], ADDR_PRESENT, b, 8)) {
      Serial.print(F("null"));
      continue;
    }
    int16_t raw = (int16_t)(b[0] | (b[1] << 8));
    float deg = direction[side] * (raw - centerRaw[side]) * 360.0f / 4096.0f;
    Serial.print(F("{\"id\":"));
    Serial.print(servoId[side]);
    Serial.print(F(",\"raw\":"));
    Serial.print(raw);
    Serial.print(F(",\"deg\":"));
    Serial.print(deg, 1);
    Serial.print(F(",\"load\":"));
    Serial.print(signMagnitude((uint16_t)(b[4] | (b[5] << 8))));
    Serial.print(F(",\"dV\":"));
    Serial.print(b[6]);
    Serial.print(F(",\"tempC\":"));
    Serial.print(b[7]);
    Serial.print(F(",\"status\":"));
    Serial.print(lastStatus[side]);
    Serial.print('}');
  }
  Serial.println('}');
}

// --- 命令 -------------------------------------------------------------------
static void handleLine(char *s) {
  char *rest = s + 1;
  while (*rest == ' ') rest++;
  int a = 0, b = 0, c = 0;
  sscanf(rest, "%d %d %d", &a, &b, &c);
  switch (s[0]) {
    case '?': printState(); return;
    case 'Z': {
      int16_t found[2] = {centerRaw[0], centerRaw[1]};
      for (uint8_t side = 0; side < 2; side++) {
        uint8_t raw[2];
        if (!servoId[side] || !readBlock(servoId[side], ADDR_PRESENT, raw, 2)) {
          Serial.println(F("{\"error\":\"servo_not_found\"}"));
          return;
        }
        found[side] = (int16_t)(raw[0] | (raw[1] << 8));
        if (found[side] < CENTER_MIN || found[side] > CENTER_MAX) {
          // ホーンの付け位置が端に寄っている。歩くと片側で 0 や 4095 に当たる
          Serial.print(F("{\"error\":\"center_near_end\",\"side\":"));
          Serial.print(side);
          Serial.print(F(",\"raw\":"));
          Serial.print(found[side]);
          Serial.println('}');
          return;
        }
      }
      centerRaw[0] = found[0];
      centerRaw[1] = found[1];
      saveSettings();
      stopMotion();
      break;
    }
    case 'H':
      mode = IDLE;
      moveLeg(0, 0, 1000);
      moveLeg(1, 0, 1000);
      break;
    case 'P':
      mode = IDLE;
      moveLeg(0, a, c > 0 ? c : 500);
      moveLeg(1, b, c > 0 ? c : 500);
      break;
    case 'W': startGait(1, trimDeg, false, a > 0 ? a : 1); break;
    case 'B': startGait(-1, trimDeg, false, a > 0 ? a : 1); break;
    case 'L': startGait(1, TURN_TRIM_DEG, true, a > 0 ? a : 1); break;
    case 'R': startGait(1, -TURN_TRIM_DEG, true, a > 0 ? a : 1); break;
    case 'T':
      trimDeg = constrain(a, -TRIM_MAX_DEG, TRIM_MAX_DEG);
      trimFromGait = false;
      break;
    case 'D':
      if ((a != 1 && a != -1) || (b != 1 && b != -1)) {
        Serial.println(F("{\"error\":\"direction_is_1_or_-1\"}"));
        return;
      }
      direction[0] = a;
      direction[1] = b;
      saveSettings();
      break;
    case 'S': stopMotion(); break;
    case 'O':
      mode = IDLE;
      setTorque(false);
      break;
    case 'I':
      servoId[0] = a;
      servoId[1] = b;
      saveSettings();
      openLimits();
      break;
    default:
      Serial.println(F("{\"error\":\"unknown\"}"));
      return;
  }
  Serial.println(F("{\"ok\":true}"));
}

void setup() {
  pinMode(PIN_TX_ENABLE_N, OUTPUT);
  TX_OFF();
  Serial.begin(115200);
  Serial1.begin(1000000);
  loadSettings();
  delay(300);   // サーボの起動待ち
  findServos();
  openLimits();
  holdHere();
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') {
      if (lineLen) {
        line[lineLen] = 0;
        handleLine(line);
        lineLen = 0;
      }
    } else if (lineLen < sizeof(line) - 1) {
      line[lineLen++] = ch;
    }
  }
  stepGait();
  checkHealth();
}
