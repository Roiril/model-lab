// Reference sketch only: board unspecified, not compiled or physically tested.
// Use a separate suitable servo supply and common controller GND.
// Slow pulse ramps DO NOT limit stall force. Keep hands away from the lid.
#include <Servo.h>
Servo actuator;
const int SERVO_PIN = 9; // change for the actual board
const bool CALIBRATED = false;
// Fill measured pulses after unloaded-servo and horn-phase calibration.
// They should represent a supported starting lid pose and roughly1..63deg.
const int PULSE_START_US = 0;
const int PULSE_CLOSED_US = 0;
const int PULSE_OPEN_US = 0;
int currentPulse = PULSE_START_US;
bool armed = false;
bool ready() {
  return CALIBRATED && PULSE_START_US >= 600 && PULSE_START_US <= 2400
    && PULSE_CLOSED_US >= 600 && PULSE_CLOSED_US <= 2400
    && PULSE_OPEN_US >= 600 && PULSE_OPEN_US <= 2400;
}
void rampTo(int target) {
  if (!armed) return;
  while (currentPulse != target) {
    if (Serial.available() && Serial.peek() == 'x') {
      Serial.read(); actuator.detach(); armed = false; return;
    }
    int delta = target - currentPulse;
    currentPulse += delta > 0 ? min(delta, 2) : max(delta, -2);
    actuator.writeMicroseconds(currentPulse);
    delay(20);
  }
}
void setup() {
  Serial.begin(115200);
  Serial.println("Disabled until actual pulse calibration. No automatic motion.");
  Serial.println("a: arm at aligned supported start; o: open; c: close; x: detach");
}
void loop() {
  if (!Serial.available()) return;
  char cmd = Serial.read();
  if (cmd == 'x') { actuator.detach(); armed = false; return; }
  if (!ready()) { Serial.println("Set CALIBRATED and all measured pulses first."); return; }
  if (cmd == 'a' && !armed) {
    currentPulse = PULSE_START_US;
    // Check the actual board/library behavior. Support/align the lid first.
    actuator.writeMicroseconds(currentPulse);
    actuator.attach(SERVO_PIN);
    armed = true;
  } else if (cmd == 'o') rampTo(PULSE_OPEN_US);
  else if (cmd == 'c') rampTo(PULSE_CLOSED_US);
}
