// C4-2: SG92R one-servo, five mechanically programmed patterns.
// D9 signal. External regulated 4.8 V. Controller and servo share GND.
// Start at 90 deg BEFORE assembly. No position/force feedback is present.
#include <Servo.h>

Servo motor;
constexpr uint8_t SIGNAL_PIN = 9;
constexpr uint32_t MOVE_MS = 3000;
constexpr uint32_t DWELL_MS = 1600;
constexpr float POSES[] = {15.0f, 50.0f, 90.0f, 130.0f, 165.0f};
// Measure the horn mounting phase on hardware. Keep every relative angle equal.
constexpr float PHASE_TRIM_DEG = 0.0f;
static_assert(PHASE_TRIM_DEG >= -10.0f && PHASE_TRIM_DEG <= 10.0f,
              "Check horn mounting if the required phase trim exceeds 10 degrees.");
float commanded = 90.0f;
float startAngle = 90.0f;
float targetAngle = 90.0f;
uint32_t startedAt = 0;
uint32_t stoppedAt = 0;
uint8_t cycleIndex = 0;
bool moving = false;
bool cycling = false;

void writeAngle(float logicalAngle) {
  motor.write(static_cast<int>(logicalAngle + PHASE_TRIM_DEG + 0.5f));
}

float ease(float u) {
  if (u <= 0.0f) return 0.0f;
  if (u >= 1.0f) return 1.0f;
  return u * u * u * (10.0f + u * (-15.0f + 6.0f * u));
}

void select(float angle) {
  startAngle = commanded;
  targetAngle = angle;
  startedAt = millis();
  moving = true;
}

void setup() {
  Serial.begin(115200);
  motor.attach(SIGNAL_PIN);
  writeAngle(90.0f);
  stoppedAt = millis();
  Serial.println(F("C4-2: h=flat, 1=upper-left, 2=center, 3=upper-right, 4=lower-pair, g=cycle, c=assembly 90, s=hold"));
}

void loop() {
  if (Serial.available()) {
    const char command = Serial.read();
    if (command == 'g') {
      cycling = true;
      cycleIndex = 0;
      select(POSES[cycleIndex]);
    } else if (command == 's') {
      cycling = false;
      moving = false;
      writeAngle(commanded);
    } else if (command == 'h' || command == 'c' || (command >= '1' && command <= '4')) {
      cycling = false;
      select(command == 'h' ? 15.0f : command == 'c' ? 90.0f : POSES[command - '0']);
    }
  }
  const uint32_t now = millis();
  if (moving) {
    const uint32_t elapsed = now - startedAt;
    commanded = startAngle + (targetAngle - startAngle) * ease(static_cast<float>(elapsed) / MOVE_MS);
    writeAngle(commanded);
    if (elapsed >= MOVE_MS) {
      commanded = targetAngle;
      moving = false;
      stoppedAt = now;
    }
  } else if (cycling && static_cast<uint32_t>(now - stoppedAt) >= DWELL_MS) {
    cycleIndex = static_cast<uint8_t>((cycleIndex + 1) % 5);
    select(POSES[cycleIndex]);
  }
}
