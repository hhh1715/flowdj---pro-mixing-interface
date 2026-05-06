// 05_full_integration — 整合版正式韌體
// 03 軟體 baseline + 04 演算法 + docs/hardware/04-midi-protocol.md
// Arduino IDE → Tools → USB Type 必須選 "Serial + MIDI"
//
// 通道對應（跟 03/04 一致）：
//   #1 0x5A  ELE0=CUE  ELE1=Play  ELE2=SYNC  ELE4–11=Jog (0°–315°)
//   #2 0x5B  ELE0–9=速度 slider (top→bottom)
//   #3 0x5C  ELE0–3=PAD1–4  ELE4–8=音量 fader (−→+)
//
// MIDI 訊息（docs/hardware/04-midi-protocol.md）：
//   Note 36/37/38=CUE/Play/SYNC, 40–43=PAD1–4, 48=Jog 觸摸
//   CC 7=音量 7-bit, CC 14/46=速度 14-bit MSB/LSB, CC 16=Jog 旋轉 signed 7-bit (64=zero)

#include <Wire.h>
#include <math.h>
#include "Adafruit_MPR121.h"

#define NUM_CHIPS  3
#define NUM_ELE    12

// 軟體觸控判斷（跟 02/03/04 對齊；晶片內建 baseline 在導電墨設置上失效）
#define TOUCH_DELTA   3
#define RELEASE_DELTA 1
#define BASELINE_EMA  0.99f
#define NOISE_THR     1     // 04 驗過：你的 delta 約 5–7，門檻 1 才不會吃光
#define WSUM_MIN      3

// MIDI 發送門檻（避免雜訊狂送）
#define VOLUME_DEADBAND 1   // 7-bit CC 7
#define TEMPO_DEADBAND  8   // 14-bit ≈ 0.05%

// 防雜訊：所有 fader / jog 都需要的最小總權重，比 WSUM_MIN(=3) 嚴
// 真實手指觸碰會橫跨多 pad（wsum 通常 10+），單 pad baseline 漂移 ghost 約 3–5
// 在雜訊大的環境（不同電腦的 USB 供電 / 接地 / EMI）會把 ghost 完全擋掉
#define VOL_TOUCH_WSUM_MIN   8   // 5 pads
#define TEMPO_TOUCH_WSUM_MIN 8   // 10 pads
#define JOG_TOUCH_WSUM_MIN   5   // 8 pads，但手指通常只覆 1–2 顆 → 門檻較低

// 100 Hz 掃描
#define SCAN_INTERVAL_MS 10

// ── 通道對應 ──────────────────────────────────────────────────────────────────
const int JOG_CHIP = 0, JOG_START = 4, JOG_N = 8;
const float JOG_ANGLES[8] = {0, 45, 90, 135, 180, 225, 270, 315};

const int SPEED_CHIP = 1, SPEED_START = 0, SPEED_N = 10;
const int VOL_CHIP   = 2, VOL_START   = 4, VOL_N   = 5;

struct Button { int chip; int ele; int note; };
const Button BUTTONS[] = {
  {0, 0, 36},  // #1 ELE0 → CUE
  {0, 1, 37},  // #1 ELE1 → Play
  {0, 2, 38},  // #1 ELE2 → SYNC
  {2, 0, 40},  // #3 ELE0 → PAD1
  {2, 1, 41},  // #3 ELE1 → PAD2
  {2, 2, 42},  // #3 ELE2 → PAD3
  {2, 3, 43},  // #3 ELE3 → PAD4
};
const int NUM_BUTTONS = sizeof(BUTTONS) / sizeof(BUTTONS[0]);

const int JOG_TOUCH_NOTE = 48;
const int CC_VOLUME    = 7;
const int CC_TEMPO_MSB = 14;
const int CC_TEMPO_LSB = 46;
const int CC_JOG_DELTA = 16;

// ── 狀態 ──────────────────────────────────────────────────────────────────────
Adafruit_MPR121 caps[NUM_CHIPS];
const uint8_t addrs[NUM_CHIPS] = { 0x5A, 0x5B, 0x5C };
const char*   names[NUM_CHIPS] = { "#1", "#2", "#3" };

float baseline[NUM_CHIPS][NUM_ELE];
bool  touched_now[NUM_CHIPS][NUM_ELE];
bool  touched_prev[NUM_CHIPS][NUM_ELE];

int   prev_volume_cc = -1;
int   prev_tempo_14  = -1;
bool  prev_jog_touch = false;
float prev_jog_angle = -1;
float jog_residual   = 0;  // 小數累加器：避免 (int) 截斷把慢速小角度吃光

unsigned long lastScan = 0;

// ── 工具 ──────────────────────────────────────────────────────────────────────
int getWeight(int chip, int ch) {
  int filt = caps[chip].filteredData(ch);
  int delta = (int)baseline[chip][ch] - filt;
  return max(0, delta - NOISE_THR);
}

float readCentroid(int chip, int start, int n) {
  long ws = 0, wsum = 0;
  for (int i = 0; i < n; i++) {
    int w = getWeight(chip, start + i);
    ws += (long)i * w;
    wsum += w;
  }
  if (wsum < WSUM_MIN) return -1.0f;
  return (float)ws / wsum / (n - 1);
}

float readJogAngle() {
  float sx = 0, sy = 0;
  long wsum = 0;
  for (int i = 0; i < JOG_N; i++) {
    int w = getWeight(JOG_CHIP, JOG_START + i);
    float r = JOG_ANGLES[i] * M_PI / 180.0f;
    sx += cosf(r) * w;
    sy += sinf(r) * w;
    wsum += w;
  }
  if (wsum < WSUM_MIN) return -1.0f;
  float a = atan2f(sy, sx) * 180.0f / M_PI;
  if (a < 0) a += 360.0f;
  return a;
}

// ── Setup ─────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000);  // 400 kHz I²C → 100 Hz 掃描 budget 內跑得完

  for (int c = 0; c < NUM_CHIPS; c++) {
    if (!caps[c].begin(addrs[c])) {
      Serial.print("MPR121 "); Serial.print(names[c]);
      Serial.println(" not found!");
      while (1);
    }
  }

  delay(500);  // 等 baseline 穩

  for (int c = 0; c < NUM_CHIPS; c++) {
    for (int i = 0; i < NUM_ELE; i++) {
      baseline[c][i] = caps[c].filteredData(i);
      touched_now[c][i] = false;
      touched_prev[c][i] = false;
    }
  }

  Serial.println("05 ready - sending full MIDI protocol on Channel 1");
}

// ── Main loop ────────────────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();
  if (now - lastScan < SCAN_INTERVAL_MS) {
    while (usbMIDI.read()) {}  // 每圈清 USB inbox（避免 host 塞住）
    return;
  }
  lastScan = now;

  // 1. 更新 baseline + 軟體 touched
  for (int c = 0; c < NUM_CHIPS; c++) {
    for (int i = 0; i < NUM_ELE; i++) {
      int filt = caps[c].filteredData(i);
      int delta = (int)baseline[c][i] - filt;

      touched_prev[c][i] = touched_now[c][i];
      if (!touched_now[c][i] && delta >= TOUCH_DELTA)       touched_now[c][i] = true;
      else if (touched_now[c][i] && delta <= RELEASE_DELTA) touched_now[c][i] = false;

      if (!touched_now[c][i]) {
        baseline[c][i] = baseline[c][i] * BASELINE_EMA + filt * (1.0f - BASELINE_EMA);
      }
    }
  }

  // 2. 按鈕：邊緣觸發
  for (int b = 0; b < NUM_BUTTONS; b++) {
    int c = BUTTONS[b].chip, e = BUTTONS[b].ele;
    if (touched_now[c][e] && !touched_prev[c][e])      usbMIDI.sendNoteOn(BUTTONS[b].note, 127, 1);
    else if (!touched_now[c][e] && touched_prev[c][e]) usbMIDI.sendNoteOff(BUTTONS[b].note, 0, 1);
  }

  // 3. Jog：Note 48 觸摸 + CC 16 旋轉
  // per-pad touched 狀態 + 總權重雙重把關，避免單 pad baseline 漂移 ghost
  bool jogTouch = false;
  long jogWsum = 0;
  for (int i = 0; i < JOG_N; i++) {
    if (touched_now[JOG_CHIP][JOG_START + i]) jogTouch = true;
    jogWsum += getWeight(JOG_CHIP, JOG_START + i);
  }
  if (jogTouch && jogWsum < JOG_TOUCH_WSUM_MIN) jogTouch = false;
  float jogAngle = jogTouch ? readJogAngle() : -1.0f;

  if (jogTouch != prev_jog_touch) {
    if (jogTouch) usbMIDI.sendNoteOn(JOG_TOUCH_NOTE, 127, 1);
    else          usbMIDI.sendNoteOff(JOG_TOUCH_NOTE, 0, 1);
    prev_jog_touch = jogTouch;
  }

  if (jogTouch) {
    if (prev_jog_angle >= 0) {
      float delta = jogAngle - prev_jog_angle;
      if (delta >  180) delta -= 360;  // 環繞處理
      if (delta < -180) delta += 360;
      delta = -delta;                    // 翻方向：硬體 pad 是 CCW 排，DJ 慣例 CW=前進
      jog_residual += delta;             // 累加進殘差
      int scaled = (int)jog_residual;    // 截整數部分送出
      jog_residual -= scaled;            // 小數留下次補
      if (scaled >  63) scaled =  63;
      if (scaled < -63) scaled = -63;
      if (scaled != 0) {                 // 0 不送，省 USB 頻寬
        usbMIDI.sendControlChange(CC_JOG_DELTA, 64 + scaled, 1);
      }
    }
    prev_jog_angle = jogAngle;
  } else {
    prev_jog_angle = -1;
    jog_residual   = 0;                  // 放開重置，避免下次接著觸發
  }

  // 4. 速度 slider → 14-bit CC 14/46（同樣用 per-pad touched + 總權重雙重把關）
  bool speedTouch = false;
  long speedWsum = 0;
  for (int i = 0; i < SPEED_N; i++) {
    if (touched_now[SPEED_CHIP][SPEED_START + i]) speedTouch = true;
    speedWsum += getWeight(SPEED_CHIP, SPEED_START + i);
  }
  if (speedTouch && speedWsum < TEMPO_TOUCH_WSUM_MIN) speedTouch = false;
  float speed = speedTouch ? readCentroid(SPEED_CHIP, SPEED_START, SPEED_N) : -1.0f;
  if (speed >= 0) {
    int t14 = (int)(speed * 16383);
    if (t14 < 0) t14 = 0; else if (t14 > 16383) t14 = 16383;
    if (prev_tempo_14 < 0 || abs(t14 - prev_tempo_14) >= TEMPO_DEADBAND) {
      usbMIDI.sendControlChange(CC_TEMPO_MSB, (t14 >> 7) & 0x7F, 1);
      usbMIDI.sendControlChange(CC_TEMPO_LSB, t14 & 0x7F, 1);
      prev_tempo_14 = t14;
    }
  }

  // 5. 音量 fader → 7-bit CC 7（同理）
  // 雙重把關：per-pad hysteresis 之外，再要求總權重夠強，
  // 否則單 pad baseline 漂移 + 鄰居雜訊會讓 centroid 在小範圍亂跳
  bool volTouch = false;
  long volWsum = 0;
  for (int i = 0; i < VOL_N; i++) {
    if (touched_now[VOL_CHIP][VOL_START + i]) volTouch = true;
    volWsum += getWeight(VOL_CHIP, VOL_START + i);
  }
  if (volTouch && volWsum < VOL_TOUCH_WSUM_MIN) volTouch = false;
  float vol = volTouch ? readCentroid(VOL_CHIP, VOL_START, VOL_N) : -1.0f;
  if (vol >= 0) {
    int v7 = (int)(vol * 127);
    if (v7 < 0) v7 = 0; else if (v7 > 127) v7 = 127;
    if (prev_volume_cc < 0 || abs(v7 - prev_volume_cc) >= VOLUME_DEADBAND) {
      usbMIDI.sendControlChange(CC_VOLUME, v7, 1);
      prev_volume_cc = v7;
    }
  }

  while (usbMIDI.read()) {}
}
