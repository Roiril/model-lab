"""運動表の範囲からArduinoのSG92Rデモを作る。書き込みや接続はしない。"""
import argparse
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = '''// __TITLE__ — SG92R 1台の低速デモ
// Arduino Servoライブラリを使用。信号をD9へ。電源GNDとArduino GNDは共通。
// サーボは適切な4.8V外部電源から給電する。USB端子だけで給電しない。
// ねじを使わないホーンの角度合わせは、このモデルのREADMEに従う。
// 起動後は90度で静止。シリアルモニター115200bps: g=往復、s=現在位置で停止。
// 数値はCADの運動表から生成。実物では試片確認後に狭い角度から始める。
#include <Servo.h>

Servo actuator;
constexpr uint8_t SIGNAL_PIN = 9;
constexpr float LOW_DEG = __LOW__f;
constexpr float HIGH_DEG = __HIGH__f;
constexpr unsigned long MOVE_MS = __MILLISECONDS__UL;
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
'''


def main(model):
    folder = ROOT / "models" / model
    motion = json.loads((folder / "build/motion.json").read_text(encoding="utf-8"))
    values = [f["servo_deg"] for f in motion["frames"]]
    source = TEMPLATE.replace("__TITLE__", model)
    source = source.replace("__LOW__", f"{min(values):.3f}").replace("__HIGH__", f"{max(values):.3f}")
    source = source.replace("__MILLISECONDS__", str(round(motion.get("duration_s", 2) * 1000)))
    path = folder / "demo" / "demo.ino"
    path.parent.mkdir(exist_ok=True)
    path.write_text(source, encoding="utf-8", newline="\n")
    print(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=("mystery-box-sg92r-c3", "mystery-box-sg92r-c4"))
    main(parser.parse_args().model)
