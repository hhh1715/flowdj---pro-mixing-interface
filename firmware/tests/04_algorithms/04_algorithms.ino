// 04_algorithms — 質心 (slider) + 向量和 (jog) 演算法驗證
// 驗收：slider 輸出 0.000–1.000 平滑；jog 輸出 0.0–360.0 連續跨 0/360 不跳
// 參見 docs/hardware/06-testing-plan.md Phase 4 + docs/hardware/05-centroid-algorithm.md

#include <Wire.h>
#include <math.h>
#include "Adafruit_MPR121.h"

Adafruit_MPR121 cap1, cap2;

const int JOG_CH_START = 4;
const int JOG_N = 8;
const float JOG_ANGLES[8] = {0, 45, 90, 135, 180, 225, 270, 315};
const int NOISE_THR = 3;

// Slider 質心：傳回 0.0–1.0 或 -1（未觸碰）
float readSliderCentroid(Adafruit_MPR121 &cap, int start, int n) {
  long ws = 0, wsum = 0;
  for (int i = 0; i < n; i++) {
    // Adafruit_MPR121::baselineData() 已內部 << 2，外部不要再 shift
    int delta = (int)cap.baselineData(start + i) - (int)cap.filteredData(start + i);
    int w = max(0, delta - NOISE_THR);
    ws += (long)i * w;
    wsum += w;
  }
  if (wsum < 10) return -1;
  return (float)ws / wsum / (n - 1);
}

// Jog 向量和：傳回 0.0–360.0 或 -1（未觸碰）
float readJogAngle(Adafruit_MPR121 &cap) {
  float sx = 0, sy = 0;
  long ws = 0;
  for (int i = 0; i < JOG_N; i++) {
    int delta = (int)cap.baselineData(JOG_CH_START + i) - (int)cap.filteredData(JOG_CH_START + i);
    int w = max(0, delta - NOISE_THR);
    float r = JOG_ANGLES[i] * M_PI / 180.0;
    sx += cos(r) * w;
    sy += sin(r) * w;
    ws += w;
  }
  if (ws < 10) return -1;
  float a = atan2(sy, sx) * 180.0 / M_PI;
  if (a < 0) a += 360;
  return a;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  cap1.begin(0x5A);
  cap2.begin(0x5B);
  delay(1000);
}

void loop() {
  float slider = readSliderCentroid(cap2, 0, 10);
  float jog = readJogAngle(cap1);

  Serial.print("Slider: ");
  if (slider < 0) Serial.print("----");
  else Serial.print(slider, 3);

  Serial.print("   Jog: ");
  if (jog < 0) Serial.println("----");
  else Serial.println(jog, 1);

  delay(100);
}
