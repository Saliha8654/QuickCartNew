#include "HX711.h"
#include <EEPROM.h>

const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;
const int EEPROM_ADDR = 0;
const float MAGIC_NUMBER = 123.456;

HX711 scale;
bool calibrated = false;
float calibrationFactor = 0;
bool continuousMode = true;

unsigned long lastPrintTime = 0;
const unsigned long printInterval = 500;

void setup() {
  Serial.begin(9600);
  delay(1000); // ✅ Extra startup delay

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  delay(1000); // ✅ Let HX711 fully stabilize

  // Load calibration from EEPROM
  float magic;
  EEPROM.get(EEPROM_ADDR, magic);
  if (magic == MAGIC_NUMBER) {
    EEPROM.get(EEPROM_ADDR + sizeof(float), calibrationFactor);
    scale.set_scale(calibrationFactor);
    calibrated = true;
    Serial.print("Calibration LOADED: ");
    Serial.println(calibrationFactor, 2);
  }

  // ✅ Always tare on startup with nothing on scale
  Serial.println("Taring... REMOVE everything from scale!");
  delay(3000); // Give you time to remove weight
  scale.tare();
  Serial.println("Tare DONE!");

  Serial.println("Commands: c<weight>=calibrate, t=tare, r=resume, s=stop");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("c")) {
      float weight = command.substring(1).toFloat();
      if (weight > 0) {
        calibrateScale(weight);
      } else {
        Serial.println("ERROR: Invalid weight. Example: c123");
      }
    }
    else if (command == "t") {
      Serial.println("Taring... remove all weight first!");
      delay(2000);
      scale.tare();
      Serial.println(">> Tare DONE");
    }
    else if (command == "r") {
      continuousMode = true;
      Serial.println(">> Reading ON");
    }
    else if (command == "s") {
      continuousMode = false;
      Serial.println(">> Reading OFF");
    }
  }

  if (continuousMode && (millis() - lastPrintTime > printInterval)) {
    lastPrintTime = millis();
    if (calibrated) {
      float weight = scale.get_units(20);
      weight = abs(weight);
      if (weight < 1.0) weight = 0.0;
      Serial.print("Weight: ");
      Serial.print(weight, 2);
      Serial.println("g");
    } else {
      Serial.println("NOT CALIBRATED — send: c123");
    }
  }
}

void calibrateScale(float knownWeight) {
  Serial.println("=== CALIBRATION STARTED ===");
  Serial.println("Step 1: Removing all weight from scale...");
  
  scale.set_scale();   // ✅ Reset scale factor
  delay(2000);
  scale.tare();        // ✅ Zero with nothing on it
  Serial.println("Step 1 DONE: Scale zeroed.");

  Serial.print("Step 2: Place your ");
  Serial.print(knownWeight);
  Serial.println("g object on scale NOW...");
  
  delay(7000); // ✅ 7 seconds to place weight
  
  long reading = scale.get_value(30); // ✅ 30 samples for accuracy
  
  Serial.print("Raw reading: ");
  Serial.println(reading);
  
  if (abs(reading) < 100) {
    Serial.println("ERROR: Reading too low! Check wiring.");
    return;
  }

  calibrationFactor = (float)reading / knownWeight;
  scale.set_scale(calibrationFactor);
  calibrated = true;

  EEPROM.put(EEPROM_ADDR, MAGIC_NUMBER);
  EEPROM.put(EEPROM_ADDR + sizeof(float), calibrationFactor);

  Serial.print(">> Calibration Factor: ");
  Serial.println(calibrationFactor, 2);
  Serial.println("=== CALIBRATION SAVED! ===");
  Serial.println("Now test with your known weight.");
}