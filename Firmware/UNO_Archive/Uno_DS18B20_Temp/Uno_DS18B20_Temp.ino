#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 4

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Replace with your sensor addresses
DeviceAddress sensor1 = { 0x28, 0x31, 0x9B, 0x7B, 0x00, 0x00, 0x00, 0x3F };
DeviceAddress sensor2 = { 0x28, 0x4F, 0x41, 0x78, 0x00, 0x00, 0x00, 0xDF };

void setup(void)
{
  Serial.begin(9600);
  sensors.begin();

  // Optional: check if sensors are connected
  if (!sensors.isConnected(sensor1)) {
    Serial.println("Sensor 1 not connected!");
  }
  if (!sensors.isConnected(sensor2)) {
    Serial.println("Sensor 2 not connected!");
  }
}

void loop(void)
{
  sensors.requestTemperatures();

  float temp1 = sensors.getTempC(sensor1);
  float temp2 = sensors.getTempC(sensor2);

  Serial.print("Sensor 1 (C): ");
  Serial.print(temp1);
  Serial.print("  |  Sensor 2 (C): ");
  Serial.println(temp2);

  delay(1000);
}
