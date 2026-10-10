// mystery-box-sg92r-c4 — SG92R 1台の低速デモ
// Arduino Servoライブラリを使用。信号をD9へ。電源GNDとArduino GNDは共通。
// サーボは適切な4.8V外部電源から給電する。USB端子だけで給電しない。
// ねじを使わないホーンの角度合わせは、このモデルのREADMEに従う。
// 起動後は90度で静止。シリアルモニター115200bps: g=往復、s=現在位置で停止。
// 数値はCADの運動表から生成。実物では試片確認後に狭い角度から始める。
#include <Servo.h>

Servo actuator;
constexpr uint8_t SIGNAL_PIN = 9;
constexpr float LOW_DEG = 10.000f;
constexpr float HIGH_DEG = 170.000f;
constexpr unsigned long MOVE_MS = 1500UL;
bool running = false;
bool towardHigh = false;
float fromDeg = 90.0f;
float targetDeg = LOW_DEG;
float currentDeg = 90.0f;
unsigned long started = 0;

float ease(float t) {
  return t * t * t * (10.0f + t * (-15.0f + 6.0f * t));
}

void setup() {
  Serial.begin(115200);
  actuator.attach(SIGNAL_PIN);
  actuator.write(90);
  Serial.println("90 deg. Align the horn. g: run, s: stop.");
}

void loop() {
  if (Serial.available()) {
    const char command = Serial.read();
    if (command == 'g') {
      running = true;
      fromDeg = currentDeg;
      targetDeg = LOW_DEG;
      towardHigh = false;
      started = millis();
    } else if (command == 's') {
      running = false;
      Serial.println("Stopped at current angle.");
    }
  }
  if (!running) return;
  const unsigned long elapsed = millis() - started;
  const float t = min(1.0f, float(elapsed) / float(MOVE_MS));
  currentDeg = fromDeg + (targetDeg - fromDeg) * ease(t);
  actuator.write(int(currentDeg + 0.5f));
  if (elapsed >= MOVE_MS + 600UL) {
    fromDeg = targetDeg;
    towardHigh = !towardHigh;
    targetDeg = towardHigh ? HIGH_DEG : LOW_DEG;
    started = millis();
  }
  delay(15);
}
