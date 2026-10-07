// Reference only: board unspecified; not compiled or physically tested.
// Test the unloaded servo first. Supply servo from a suitable external source.
// Common GND with controller. Calibrate actual direction and endpoints.
#include <Servo.h>
Servo opener;
const uint8_t SIGNAL_PIN = 9;
const int CLOSED_US = 1500; // Set only after unloaded calibration.
const int OPEN_US = 1700;   // Small initial trial, NOT the CAD 65 degree endpoint.
const int LOWER_US = 1200, UPPER_US = 1800;
const unsigned long STEP_MS = 20;
int currentUs = CLOSED_US, targetUs = CLOSED_US;
unsigned long previousStep = 0;
void setup() {
  Serial.begin(115200);
  // First power-on motion cannot be slowed by this loop. Keep servo unloaded.
  opener.writeMicroseconds(currentUs);
  opener.attach(SIGNAL_PIN, 1000, 2000);
  opener.writeMicroseconds(currentUs);
  Serial.println("o=open, c=close, s=hold current position");
}
void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    if (command == 'o') targetUs = constrain(OPEN_US, LOWER_US, UPPER_US);
    if (command == 'c') targetUs = constrain(CLOSED_US, LOWER_US, UPPER_US);
    if (command == 's') targetUs = currentUs; // Still energized: holds position.
  }
  unsigned long now = millis();
  if (now - previousStep >= STEP_MS) {
    previousStep = now;
    if (currentUs < targetUs) ++currentUs;
    else if (currentUs > targetUs) --currentUs;
    opener.writeMicroseconds(currentUs);
  }
}
