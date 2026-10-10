#include <Servo.h>

// 蓋を65°開き、サーボを電気角90°にしてホーンを付ける。
const int SERVO_PIN = 9;
const float CLOSED_DEG = 169.6f;
const float OPEN_DEG = 90.0f;
const float MIDDLE_DEG = 120.3f;
const float SERVO_MIN_DEG = 0.0f;
const float SERVO_MAX_DEG = 180.0f;
const unsigned long MOTION_MS = 1200;

Servo lid;
float current = OPEN_DEG;
float startAngle = OPEN_DEG;
float targetAngle = OPEN_DEG;
unsigned long started = 0;
unsigned long lastWrite = 0;
bool moving = false;

void beginMotion(float target) {
  startAngle = current;
  targetAngle = constrain(target, SERVO_MIN_DEG, SERVO_MAX_DEG);
  started = millis();
  moving = true;
}

void setup() {
  Serial.begin(115200);
  lid.attach(SERVO_PIN);
  lid.write(int(OPEN_DEG));
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
    current = constrain(startAngle + (targetAngle - startAngle) * eased,
                        SERVO_MIN_DEG, SERVO_MAX_DEG);
    lid.write(int(current + 0.5f));
    lastWrite = now;
    if (x >= 1.0f) moving = false;
  }
}
