#include <OneWire.h>

#define ONE_WIRE_BUS 4
OneWire oneWire(ONE_WIRE_BUS);

void setup() {
  Serial.begin(9600);
}

void loop() {
  byte address[8];

  if (!oneWire.search(address)) {
    Serial.println("No more devices.");
    oneWire.reset_search();
    delay(5000);
    return;
  }

  Serial.print("Address: ");
  for (int i = 0; i < 8; i++) {
    if (address[i] < 16) Serial.print("0");
    Serial.print(address[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
}
