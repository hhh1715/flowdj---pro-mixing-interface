// 04_algorithms — 質心 (slider/fader) + 向量和 (jog) 演算法驗證
// 用 03 同款的軟體 baseline（晶片內建 baseline 在導電墨設置上失效）
// 驗收：slider/fader 輸出 0.000–1.000 平滑；jog 輸出 0.0–360.0 連續跨 0/360 不跳
// 參見 docs/hardware/06-testing-plan.md Phase 4 + docs/hardware/05-centroid-algorithm.md

#include <Wire.h>
#include <math.h>
#include "Adafruit_MPR121.h"

#define NUM_CHIPS  3
#define NUM_ELE    12

// 軟體觸控判斷（跟 02/03 對齊）
#define TOUCH_DELTA   3
#define RELEASE_DELTA 1
#define BASELINE_EMA  0.99f
#define NOISE_THR     1   // 你的 delta 只有 5–7，門檻 3 會把訊號吃光
#define WSUM_MIN      3   // wsum 低於這個 → 視為沒按

#define DEBUG_RAW       0   // 印每組 wsum 總和（除錯用）
#define DEBUG_PER_PAD   0   // 印每片 pad 的 weight（找哪片弱/死掉用）

// 通道對應（跟 03 的 MIDI 註解一致）
//   #1 ELE 4–11  → Jog 8 sectors (0°,45°,90°,...,315°)
//   #2 ELE 0–9   → 速度 slider 10 pads (0=top, 9=bottom)
//   #3 ELE 4–8   → 音量 fader 5 pads (4=−, 8=+)
const int JOG_CHIP = 0;          // #1 = caps[0] = 0x5A
const int JOG_START = 4;
const int JOG_N = 8;
const float JOG_ANGLES[8] = {0, 45, 90, 135, 180, 225, 270, 315};

const int SPEED_CHIP = 1;        // #2 = caps[1] = 0x5B
const int SPEED_START = 0;
const int SPEED_N = 10;

const int VOL_CHIP = 2;          // #3 = caps[2] = 0x5C
const int VOL_START = 4;
const int VOL_N = 5;

Adafruit_MPR121 caps[NUM_CHIPS];
const uint8_t addrs[NUM_CHIPS] = { 0x5A, 0x5B, 0x5C };
const char* names[NUM_CHIPS]   = { "#1", "#2", "#3" };

float baseline[NUM_CHIPS][NUM_ELE];
bool  touched[NUM_CHIPS][NUM_ELE];

// 取得某顆晶片某通道的 weight（baseline - filtered，扣掉雜訊門檻）
int getWeight(int chip, int ch) {
  int filt = caps[chip].filteredData(ch);
  int delta = (int)baseline[chip][ch] - filt;
  return max(0, delta - NOISE_THR);
}

// 一維 centroid → 0.0–1.0，未觸碰回傳 -1
float readCentroid(int chip, int start, int n, long *out_wsum) {
  long ws = 0, wsum = 0;
  for (int i = 0; i < n; i++) {
    int w = getWeight(chip, start + i);
    ws += (long)i * w;
    wsum += w;
  }
  if (out_wsum) *out_wsum = wsum;
  if (wsum < WSUM_MIN) return -1.0f;
  return (float)ws / wsum / (n - 1);
}

// 圓形 vector sum → 0.0–360.0，未觸碰回傳 -1
float readJogAngle(long *out_wsum) {
  float sx = 0, sy = 0;
  long wsum = 0;
  for (int i = 0; i < JOG_N; i++) {
    int w = getWeight(JOG_CHIP, JOG_START + i);
    float r = JOG_ANGLES[i] * M_PI / 180.0f;
    sx += cosf(r) * w;
    sy += sinf(r) * w;
    wsum += w;
  }
  if (out_wsum) *out_wsum = wsum;
  if (wsum < WSUM_MIN) return -1.0f;
  float a = atan2f(sy, sx) * 180.0f / M_PI;
  if (a < 0) a += 360.0f;
  return a;
}

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

  Serial.println("3 MPR121s online. Sampling 500ms for initial baseline...");
  delay(500);

  // 用第一筆 filtered 當初始 baseline
  for (int c = 0; c < NUM_CHIPS; c++) {
    for (int i = 0; i < NUM_ELE; i++) {
      baseline[c][i] = caps[c].filteredData(i);
      touched[c][i] = false;
    }
  }

  Serial.println("Slider | Jog   | Volume");
  Serial.println("-----------------------");
}

void loop() {
  // 先更新觸控狀態 + baseline 追蹤（跟 02/03 一樣）
  for (int c = 0; c < NUM_CHIPS; c++) {
    for (int i = 0; i < NUM_ELE; i++) {
      int filt = caps[c].filteredData(i);
      int delta = (int)baseline[c][i] - filt;

      if (!touched[c][i] && delta >= TOUCH_DELTA) touched[c][i] = true;
      else if (touched[c][i] && delta <= RELEASE_DELTA) touched[c][i] = false;

      if (!touched[c][i]) {
        baseline[c][i] = baseline[c][i] * BASELINE_EMA + filt * (1.0f - BASELINE_EMA);
      }
    }
  }

  // 算三條控制器（同時拿 wsum 做 debug）
  long sw_slider, sw_jog, sw_vol;
  float slider = readCentroid(SPEED_CHIP, SPEED_START, SPEED_N, &sw_slider);
  float jog    = readJogAngle(&sw_jog);
  float vol    = readCentroid(VOL_CHIP, VOL_START, VOL_N, &sw_vol);

  // 每 100ms 印一次
  static uint32_t last_print = 0;
  if (millis() - last_print > 100) {
    last_print = millis();

    if (slider < 0) Serial.print(" ----  ");
    else { Serial.print(" "); Serial.print(slider, 3); }

    Serial.print(" | ");
    if (jog < 0) Serial.print(" ---- ");
    else { Serial.print(jog, 1); if (jog < 100) Serial.print(" "); if (jog < 10) Serial.print(" "); }

    Serial.print(" | ");
    if (vol < 0) Serial.print(" ----");
    else Serial.print(vol, 3);

#if DEBUG_RAW
    Serial.print("   [w: slider=");
    Serial.print(sw_slider);
    Serial.print(" jog=");
    Serial.print(sw_jog);
    Serial.print(" vol=");
    Serial.print(sw_vol);
    Serial.print("]");
#endif
#if DEBUG_PER_PAD
    Serial.print("   S:");
    for (int i = 0; i < SPEED_N; i++) {
      Serial.print(getWeight(SPEED_CHIP, SPEED_START + i));
      if (i < SPEED_N - 1) Serial.print(",");
    }
    Serial.print("  J:");
    for (int i = 0; i < JOG_N; i++) {
      Serial.print(getWeight(JOG_CHIP, JOG_START + i));
      if (i < JOG_N - 1) Serial.print(",");
    }
    Serial.print("  V:");
    for (int i = 0; i < VOL_N; i++) {
      Serial.print(getWeight(VOL_CHIP, VOL_START + i));
      if (i < VOL_N - 1) Serial.print(",");
    }
#endif
    Serial.println();
  }

  delay(10);
}
