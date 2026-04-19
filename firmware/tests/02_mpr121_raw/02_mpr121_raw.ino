// 02_mpr121_raw — 讀 3 顆 MPR121 每個電極的 touch state
// 驗收：碰任一通道對應位元變 1
// 參見 docs/hardware/06-testing-plan.md Phase 2

#include <Wire.h>
#include "Adafruit_MPR121.h"

Adafruit_MPR121 cap1, cap2, cap3;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Wire.begin();

  if (!cap1.begin(0x5A)) { Serial.println("MPR121 #1 not found!"); while (1); }
  if (!cap2.begin(0x5B)) { Serial.println("MPR121 #2 not found!"); while (1); }
  if (!cap3.begin(0x5C)) { Serial.println("MPR121 #3 not found!"); while (1); }

  Serial.println("3 MPR121s online. Touch any pad...");
  delay(1000); // 等 baseline 穩定
}

void loop() {
  uint16_t t1 = cap1.touched();
  uint16_t t2 = cap2.touched();
  uint16_t t3 = cap3.touched();

  static uint16_t prev1 = 0, prev2 = 0, prev3 = 0;
  if (t1 != prev1 || t2 != prev2 || t3 != prev3) {
    Serial.print("  #1 (0x5A): ");
    for (int i = 0; i < 12; i++) Serial.print((t1 & (1 << i)) ? '1' : '.');
    Serial.print("   #2 (0x5B): ");
    for (int i = 0; i < 12; i++) Serial.print((t2 & (1 << i)) ? '1' : '.');
    Serial.print("   #3 (0x5C): ");
    for (int i = 0; i < 12; i++) Serial.print((t3 & (1 << i)) ? '1' : '.');
    Serial.println();
    prev1 = t1; prev2 = t2; prev3 = t3;
  }

  delay(20);
}

// 進階：讀 filtered data（為 Phase 4 做準備）
//   for (int i = 0; i < 12; i++) {
//     Serial.print(cap1.filteredData(i));
//     Serial.print("\t");
//   }
//   Serial.println();
