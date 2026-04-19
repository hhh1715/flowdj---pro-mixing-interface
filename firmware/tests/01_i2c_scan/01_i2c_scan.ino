// 01_i2c_scan — 掃描 I²C bus 驗證 3 顆 MPR121 都活著
// 驗收：Serial Monitor 看到 0x5A / 0x5B / 0x5C 三個位址
// 參見 docs/hardware/06-testing-plan.md Phase 1

#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("I2C Scanner starting...");
}

void loop() {
  byte found = 0;
  for (byte addr = 1; addr <= 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("  Found device at 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      found++;
    }
  }
  Serial.print("Total devices: ");
  Serial.println(found);
  Serial.println("-----");
  delay(3000);
}
