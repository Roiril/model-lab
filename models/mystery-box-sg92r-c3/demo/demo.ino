// mystery-box-sg92r-c3 — SG92R 1台の低速デモ
// Arduino Servoライブラリを使用。信号をD9へ。電源GNDとArduino GNDは共通。
// サーボは適切な4.8V外部電源から給電する。USB端子だけで給電しない。
// ねじを使わないホーンの角度合わせは、このモデルのREADMEに従う。
// 起動後は90度で静止。115200bps: h=開始角へ戻して停止、c=90度へ戻して停止、g=往復、s=現在位置で停止。
// 数値はCADの運動表から生成。実物では試片確認後に狭い角度から始める。
#include <Servo.h>

Servo actuator;
constexpr uint8_t SIGNAL_PIN = 9;
constexpr float LOW_DEG = 15.000f;
constexpr float HIGH_DEG = 165.000f;
constexpr unsigned long MOVE_MS = 2000UL;
bool running = false;
bool continuous = false;
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
  Serial.println("90 deg. Align the horn. h: home, c: 90 deg, g: run, s: stop.");
}

void loop() {
  if (Serial.available()) {
    const char command = Serial.read();
    if (command == 'g' || command == 'h' || command == 'c') {
      running = true;
      continuous = command == 'g';
      fromDeg = currentDeg;
      targetDeg = command == 'c' ? 90.0f : LOW_DEG;
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
    if (!continuous) {
      running = false;
      Serial.println("Target angle. Hold position.");
      return;
    }
    fromDeg = targetDeg;
    towardHigh = !towardHigh;
    targetDeg = towardHigh ? HIGH_DEG : LOW_DEG;
    started = millis();
  }
  delay(15);
}
