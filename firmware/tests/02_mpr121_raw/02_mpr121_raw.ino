// 02_mpr121_raw — 軟體版觸控判斷（繞過晶片內建 baseline tracker）
// 因為 conductive ink + 長線造成 filtered 值偏低，晶片內建 baseline 卡 0，
// touch detection 失效。改在 MCU 端自己 EMA 追蹤 baseline 並判斷 touch。
// 參見 docs/hardware/06-testing-plan.md Phase 2

#include <Wire.h>
#include "Adafruit_MPR121.h"

#define NUM_CHIPS  3
#define NUM_ELE    12

// 觸控閾值 — delta = baseline - filtered，碰下去 filtered 會掉
// 你的 idle filtered ≈ 8、touched ≈ 1-3，delta ≈ 5-7，所以 3 是合理門檻
#define TOUCH_DELTA   3
#define RELEASE_DELTA 1

// EMA 係數越接近 1 → baseline 追得越慢（不會被你按住的時候漂移到觸發值）
#define BASELINE_EMA  0.99f

Adafruit_MPR121 caps[NUM_CHIPS];
const uint8_t addrs[NUM_CHIPS] = { 0x5A, 0x5B, 0x5C };
const char* names[NUM_CHIPS]   = { "#1", "#2", "#3" };

float baseline[NUM_CHIPS][NUM_ELE];
bool  touched[NUM_CHIPS][NUM_ELE];

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Wire.begin();

  for (int c = 0; c < NUM_CHIPS; c++) {
    if (!caps[c].begin(addrs[c])) {
      Serial.print("MPR121 "); Serial.print(names[c]);
      Serial.println(" not found!");
      while (1);
    }
  }

  Serial.println("3 MPR121s online.");
  Serial.println("Sampling 500ms for initial baseline...");
  delay(500);

  // 用第一筆 filtered 當初始 baseline
  for (int c = 0; c < NUM_CHIPS; c++) {
    for (int i = 0; i < NUM_ELE; i++) {
      baseline[c][i] = caps[c].filteredData(i);
      touched[c][i] = false;
    }
  }

  Serial.println("Touch any pad. (T=touch, F=filtered, BL=software baseline, D=delta)");
  Serial.println();
}

void loop() {
  // 每 10ms 更新觸控狀態
  for (int c = 0; c < NUM_CHIPS; c++) {
    for (int i = 0; i < NUM_ELE; i++) {
      int filt = caps[c].filteredData(i);
      int delta = (int)baseline[c][i] - filt;

      // 觸控狀態機（hysteresis）
      if (!touched[c][i] && delta >= TOUCH_DELTA) {
        touched[c][i] = true;
      } else if (touched[c][i] && delta <= RELEASE_DELTA) {
        touched[c][i] = false;
      }

      // baseline 只在沒按住時追蹤（避免被按住時漂掉）
      if (!touched[c][i]) {
        baseline[c][i] = baseline[c][i] * BASELINE_EMA + filt * (1.0f - BASELINE_EMA);
      }
    }
  }

  // 每 200ms 印一次狀態
  static uint32_t last_print = 0;
  if (millis() - last_print > 200) {
    last_print = millis();
    for (int c = 0; c < NUM_CHIPS; c++) {
      Serial.print(names[c]);
      Serial.print(" T:");
      for (int i = 0; i < NUM_ELE; i++) Serial.print(touched[c][i] ? '1' : '.');
      Serial.print(" F:");
      for (int i = 0; i < NUM_ELE; i++) {
        Serial.print(' ');
        Serial.print(caps[c].filteredData(i));
      }
      Serial.print(" BL:");
      for (int i = 0; i < NUM_ELE; i++) {
        Serial.print(' ');
        Serial.print((int)baseline[c][i]);
      }
      Serial.print(" D:");
      for (int i = 0; i < NUM_ELE; i++) {
        Serial.print(' ');
        Serial.print((int)baseline[c][i] - caps[c].filteredData(i));
      }
      Serial.println();
    }
    Serial.println("---");
  }

  delay(10);
}
