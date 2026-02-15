/*
  HX711 Load Cell Test Sketch
  This sketch reads weight data from HX711 module and sends it to Serial
  
  Connections:
  HX711 Module -> Arduino
  VCC -> 5V
  GND -> GND
  DT (Data) -> Digital Pin 3
  SCK (Clock) -> Digital Pin 2
  
  Make sure to install the HX711 library:
  1. Go to Sketch > Include Library > Manage Libraries
  2. Search for "HX711"
  3. Install "HX711 Arduino Library" by Bogdan Necula
*/

#include "HX711.h"

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;

HX711 scale;

void setup() {
  Serial.begin(9600);
  Serial.println("	HX711 Load Cell Test");
  Serial.println("========================");
  
  // Initialize library with data pin, clock pin
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  
  Serial.println("Removing tare weight...");
  // Remove any existing tare weight
  scale.tare();  
  
  Serial.println("Place a known weight on the scale to calibrate.");
  Serial.println("Send 'c' followed by the weight in grams (e.g., 'c500') to calibrate.");
  Serial.println("Send 't' to tare the scale.");
  Serial.println("Send 'r' to read weight continuously.");
  Serial.println();
}

void loop() {
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("c")) {
      // Calibration command (e.g., "c500")
      float knownWeight = command.substring(1).toFloat();
      if (knownWeight > 0) {
        Serial.print("Calibrating with ");
        Serial.print(knownWeight);
        Serial.println("g...");
        
        // Get raw reading
        long rawReading = scale.get_units(10); // Average 10 readings
        
        // Calculate calibration factor
        float calibrationFactor = rawReading / knownWeight;
        
        // Set calibration factor
        scale.set_scale(calibrationFactor);
        
        Serial.print("Calibration factor set to: ");
        Serial.println(calibrationFactor);
        Serial.println("Calibration complete!");
        Serial.println();
      } else {
        Serial.println("Invalid calibration weight. Send 'c' followed by weight in grams.");
      }
    } 
    else if (command == "t") {
      // Tare command
      Serial.println("Taring scale...");
      scale.tare();
      Serial.println("Scale tared!");
      Serial.println();
    }
    else if (command == "r") {
      // Continuous read mode
      Serial.println("Entering continuous read mode. Send any character to stop.");
      while (!Serial.available()) {
        float weight = scale.get_units(5); // Average 5 readings
        Serial.print("Weight: ");
        Serial.print(weight);
        Serial.println("g");
        delay(500);
      }
      // Clear buffer
      while (Serial.available()) {
        Serial.read();
      }
      Serial.println("Continuous read mode stopped.");
      Serial.println();
    }
  }
  
  // Read weight periodically
  float weight = scale.get_units(5); // Average 5 readings
  Serial.print("Weight: ");
  Serial.print(weight);
  Serial.println("g");
  
  delay(1000);
}