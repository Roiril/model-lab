#include <Servo.h>

// 蓋95°の組立姿勢でサーボ90°にしてホーンを付ける。閉位置は実物の縁に合わせる。
const int SERVO_PIN = 9;
const float CLOSED_DEG = 160.1f;
const float OPEN_DEG = 106.5f;
const float MIDDLE_DEG = 130.5f;
const unsigned long MOTION_MS = 1200;
Servo lid;
float current = 90.0f;
float startAngle = 90.0f;
float targetAngle = 90.0f;
unsigned long started = 0;
unsigned long lastWrite = 0;
bool moving = false;

void beginMotion(float target) {
  startAngle = current;
  targetAngle = target;
  started = millis();
  moving = true;
}

void setup() {
  Serial.begin(115200);
  lid.attach(SERVO_PIN);
  lid.write(90);
  Serial.println("o=open, c=close, m=middle; < or > adjusts by one degree");
}

void loop() {
  if (Serial.available()) {
    const char key = Serial.read();
    if (key == 'o') beginMotion(OPEN_DEG);
    if (key == 'c') beginMotion(CLOSED_DEG);
    if (key == 'm') beginMotion(MIDDLE_DEG);
    if (key == '<') beginMotion(current - 1.0f);
    if (key == '>') beginMotion(current + 1.0f);
  }
  const unsigned long now = millis();
  if (moving && now - lastWrite >= 20) {
    const float x = min(1.0f, (now - started) / float(MOTION_MS));
    const float eased = x * x * (3.0f - 2.0f * x);
    current = constrain(startAngle + (targetAngle - startAngle) * eased, 90.0f, 161.0f);
    lid.write(int(current + 0.5f));
    lastWrite = now;
    if (x >= 1.0f) moving = false;
  }
}
