#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ---------- CONFIG ----------
#define ONE_WIRE_BUS 4
#define TDS_PIN A1
#define TURBIDITY_PIN A0
#define VREF 5.0
#define SCOUNT 30

// ---------- OBJECTS ----------
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ---------- GLOBAL ----------
// t1 - Normal Water Temperature
// t2 - Hot Water Temperature

float t1, t2, tdsValue, ntu;
String incomingWQI = "N/A";

// ---------- DS18B20 ADDRESSES ----------
DeviceAddress sensor1 = { 0x28, 0x31, 0x9B, 0x7B, 0x00, 0x00, 0x00, 0x3F };
DeviceAddress sensor2 = { 0x28, 0x4F, 0x41, 0x78, 0x00, 0x00, 0x00, 0xDF };

// =====================================================
// 🧠 GENERIC MEDIAN FILTER (Reusable for ANY sensor)
// =====================================================
float medianFilter(int pin, int samples) {
  int buffer[samples];

  for (int i = 0; i < samples; i++) {
    buffer[i] = analogRead(pin);
    delay(2);
  }

  // sort
  for (int i = 0; i < samples - 1; i++) {
    for (int j = 0; j < samples - i - 1; j++) {
      if (buffer[j] > buffer[j + 1]) {
        int temp = buffer[j];
        buffer[j] = buffer[j + 1];
        buffer[j + 1] = temp;
      }
    }
  }

  if (samples % 2 == 0)
    return (buffer[samples / 2] + buffer[samples / 2 - 1]) / 2.0;
  else
    return buffer[samples / 2];
}

// =====================================================
// 🌡️ TEMPERATURE
// =====================================================
void readTemperatures() {
  sensors.requestTemperatures();
  t1 = sensors.getTempC(sensor1);
  t2 = sensors.getTempC(sensor2);
}

// =====================================================
// 💧 TDS
// =====================================================
float readTDS() {
  float raw = medianFilter(TDS_PIN, SCOUNT);
  float voltage = raw * VREF / 1024.0;

  float compensationCoefficient = 1.0 + 0.02 * (t1 - 25.0);
  float compensationVoltage = voltage / compensationCoefficient;

  return (133.42 * pow(compensationVoltage, 3)
        - 255.86 * pow(compensationVoltage, 2)
        + 857.39 * compensationVoltage) * 0.5;
}


// =====================================================
// TURBIDITY
// =====================================================
float readTurbidity() {
  float raw = medianFilter(TURBIDITY_PIN, 50);
  float voltage = raw * VREF / 1024.0;

  if (voltage < 2.5) return 3000;
  else return -1120.4 * voltage * voltage + 5742.3 * voltage - 4353.8;
}

float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// =====================================================
// TURBIDITY
// =====================================================
float readTurbidityMapped() {
  float raw = medianFilter(TURBIDITY_PIN, 50);
  float voltage = raw * VREF / 1024.0;

  float ntu;
  if (voltage < 2.5) 
    ntu = 3000;
  else 
    ntu = -1120.4 * voltage * voltage + 5742.3 * voltage - 4353.8;

  // Map NTU (1600–2650) → (0–13)
  float mappedValue = mapFloat(ntu, 1600, 2650, 0, 13);

  // Clamp values (important!)
  if (mappedValue < 0) mappedValue = 0;
  if (mappedValue > 13) mappedValue = 13;

  return mappedValue;
}

// =====================================================
// SEND JSON
// =====================================================
void sendJSON() {
  Serial.print("{");
  Serial.print("\"t1\":"); Serial.print(t1,1); Serial.print(",");
  Serial.print("\"t2\":"); Serial.print(t2,1); Serial.print(",");
  Serial.print("\"tds\":"); Serial.print(tdsValue,0); Serial.print(",");
  Serial.print("\"ntu\":"); Serial.print(ntu,1);
  Serial.println("}");
}

// =====================================================
// RECEIVE WQI
// =====================================================
void receiveWQI() {
  if (Serial.available()) {
    incomingWQI = Serial.readStringUntil('\n');
  }
}

// =====================================================
// 🖥LCD DISPLAY
// =====================================================
void updateLCD() {
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("N:");
  lcd.print(t1,1);
  lcd.print(" H:");
  lcd.print(t2,1);

  lcd.setCursor(0, 1);
  lcd.print("WQI:");
  lcd.print(incomingWQI);
}

// =====================================================
// 🚀 SETUP
// =====================================================
void setup() {
  Serial.begin(9600);

  sensors.begin();
  pinMode(TDS_PIN, INPUT);
  pinMode(TURBIDITY_PIN, INPUT);

  lcd.begin();
  lcd.backlight();
}

// =====================================================
// 🔁 LOOP
// =====================================================
void loop() {

  readTemperatures();

  tdsValue = readTDS();
  //ntu = readTurbidity();
  ntu = readTurbidityMapped();

  sendJSON();
  receiveWQI();
  updateLCD();

  delay(1000);
}
