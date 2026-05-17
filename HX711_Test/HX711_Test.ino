#include "HX711.h"
#include <EEPROM.h>

const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;

HX711 scale;

const float MAGIC_NUMBER = 123.456;
const int EEPROM_ADDR = 0;

bool calibrated = false;
bool debugMode = false;

float calibrationFactor = 1.0;

unsigned long lastPrintTime = 0;
const unsigned long printInterval = 500;

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(9600);
  delay(2000);

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

  // Load EEPROM calibration
  float magic;
  EEPROM.get(EEPROM_ADDR, magic);

  if (magic == MAGIC_NUMBER) {
    EEPROM.get(EEPROM_ADDR + sizeof(float), calibrationFactor);
    scale.set_scale(calibrationFactor);
    calibrated = true;
    Serial.println("Calibration LOADED");
  }

  Serial.println("Remove all weight...");
  delay(3000);
  scale.tare();
  Serial.println("Tare done");
}

// ---------------- LOOP ----------------
void loop() {

  // SERIAL COMMANDS
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("c")) {
      float knownWeight = cmd.substring(1).toFloat();
      calibrateScale(knownWeight);
    }

    if (cmd == "d") {
      debugMode = !debugMode;
      Serial.println(debugMode ? "DEBUG ON" : "DEBUG OFF");
    }
  }

  // LIVE WEIGHT OUTPUT
  if (calibrated && millis() - lastPrintTime > printInterval) {
    lastPrintTime = millis();

    float weight = scale.get_units(10);

    if (weight < 0) weight = 0;
    if (weight < 1.0) weight = 0;

    Serial.println(weight, 2);
  }
}

// ---------------- CALIBRATION ----------------
void calibrateScale(float knownWeight) {

  Serial.println("CALIBRATION START");

  scale.set_scale(1);
  delay(2000);

  scale.tare();
  delay(2000);

  Serial.println("Place known weight...");
  delay(6000);

  float reading = scale.read_average(20);

  Serial.print("RAW: ");
  Serial.println(reading);

  if (abs(reading) < 100) {
    Serial.println("ERROR: unstable reading");
    return;
  }

  calibrationFactor = reading / knownWeight;

  scale.set_scale(calibrationFactor);
  calibrated = true;

  EEPROM.put(EEPROM_ADDR, MAGIC_NUMBER);
  EEPROM.put(EEPROM_ADDR + sizeof(float), calibrationFactor);

  Serial.print("CAL FACTOR: ");
  Serial.println(calibrationFactor);

  Serial.println("CALIBRATION DONE");
}