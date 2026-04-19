// 05_full_integration — 3 顆 MPR121 → 完整 MIDI 協議
//
// 這是 Phase 5/6 階段要燒的「正式版韌體」。合併 01–04 的測試經驗：
//   - I²C scan 驗三顆都在
//   - touched() 產生按鈕事件
//   - 質心演算法算 tempo slider + volume fader
//   - 向量和演算法算 Jog 角度與相對速度
//
// channel 配置（對齊 docs/hardware/templates/electrode-template.svg）：
//   MPR#1 0x5A  Ch0–7  Jog J0–J7        Ch8 CUE   Ch9 Play   Ch10 SYNC   Ch11 PAD1
//   MPR#2 0x5B  Ch0–9  Tempo T0–T9      Ch10 PAD2   Ch11 PAD3
//   MPR#3 0x5C  Ch0–4  Volume V0–V4     Ch5 PAD4    Ch6–11 未使用
//
// MIDI 對照（docs/hardware/04-midi-protocol.md）：
//   Note 36 CUE, 37 Play, 38 SYNC, 40–43 PAD1–4, 48 JogTouch
//   CC 7 volume (7-bit), CC 14 MSB + CC 46 LSB tempo (14-bit), CC 16 jog delta (signed 7-bit, 64=zero)
//
// 編譯：arduino-cli compile --fqbn teensy:avr:teensy40:usb=serialmidi firmware/tests/05_full_integration
// 上傳：arduino-cli upload -p /dev/ttyACM0 --fqbn teensy:avr:teensy40:usb=serialmidi firmware/tests/05_full_integration

#include <Wire.h>
#include <math.h>
#include "Adafruit_MPR121.h"

// ─── 硬體 ──────────────────────────────────────────────────────────────────────
Adafruit_MPR121 cap1, cap2, cap3;

// ─── 演算法常數 ────────────────────────────────────────────────────────────────
const int NOISE_THR = 3;             // baseline - filtered 小於這個視為雜訊
const int JOG_MIN_WEIGHT = 10;       // Jog 觸發門檻
const int SLIDER_MIN_WEIGHT = 10;
const int VOLUME_DEADBAND = 1;       // CC 7 最小變化才送（7-bit）
const int TEMPO_DEADBAND = 8;        // 14-bit 最小變化才送（約 0.05% 解析）

const float JOG_ANGLES_DEG[8] = {0, 45, 90, 135, 180, 225, 270, 315};

// ─── 排程 ──────────────────────────────────────────────────────────────────────
const unsigned long SCAN_INTERVAL_MS = 10; // 100 Hz
unsigned long lastScan = 0;

// ─── 狀態（給邊緣觸發 / deadband 用） ──────────────────────────────────────────
uint16_t lastTouched1 = 0, lastTouched2 = 0, lastTouched3 = 0;
int lastVolume = -1;
int lastTempo14 = -1;
float lastJogAngle = -1; // -1 = 上一輪沒碰
bool lastJogTouch = false;

// ─── 工具：單一 MPR121 上跑質心演算法 ──────────────────────────────────────────
// 傳回 0.0–1.0 或 -1（未觸碰）。channel 範圍 [start, start+n)。
float sliderCentroid(Adafruit_MPR121 &cap, int start, int n) {
  long ws = 0, wsum = 0;
  for (int i = 0; i < n; i++) {
    int delta = (int)cap.baselineData(start + i) - (int)cap.filteredData(start + i);
    int w = max(0, delta - NOISE_THR);
    ws += (long)i * w;
    wsum += w;
  }
  if (wsum < SLIDER_MIN_WEIGHT) return -1;
  return (float)ws / wsum / (n - 1);
}

// ─── 工具：Jog 向量和 ─────────────────────────────────────────────────────────
// 傳回 angle[0,360) 或 -1（未觸碰）。讀 cap1 ch 0–7。
float jogVectorAngle(Adafruit_MPR121 &cap) {
  float sx = 0, sy = 0;
  long ws = 0;
  for (int i = 0; i < 8; i++) {
    int delta = (int)cap.baselineData(i) - (int)cap.filteredData(i);
    int w = max(0, delta - NOISE_THR);
    float r = JOG_ANGLES_DEG[i] * M_PI / 180.0;
    sx += cos(r) * w;
    sy += sin(r) * w;
    ws += w;
  }
  if (ws < JOG_MIN_WEIGHT) return -1;
  float a = atan2(sy, sx) * 180.0 / M_PI;
  if (a < 0) a += 360.0;
  return a;
}

// ─── 按鈕邊緣觸發 ─────────────────────────────────────────────────────────────
// touched = 當前 touched() bitmap；last = 上次；channel 對應 note number
void emitButtonEdge(uint16_t now, uint16_t last, int channel, int note) {
  bool isNow = (now >> channel) & 1;
  bool wasBefore = (last >> channel) & 1;
  if (isNow && !wasBefore) {
    usbMIDI.sendNoteOn(note, 127, 1);
  } else if (!isNow && wasBefore) {
    usbMIDI.sendNoteOff(note, 0, 1);
  }
}

// ─── Setup ────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000); // 400 kHz — 讓 100 Hz 掃描 budget 內跑得完

  // 三顆 MPR121 — 位址設定請照 02-mpr121-pinout.md
  if (!cap1.begin(0x5A)) { Serial.println("MPR #1 (0x5A) not found"); }
  if (!cap2.begin(0x5B)) { Serial.println("MPR #2 (0x5B) not found"); }
  if (!cap3.begin(0x5C)) { Serial.println("MPR #3 (0x5C) not found"); }

  // 稍微放大銅箔電極的靈敏度（相對於 Adafruit 預設 12/6）
  // 若 Phase 6 加氣墊後不夠靈敏，再降低這組數值
  cap1.setThresholds(12, 6);
  cap2.setThresholds(12, 6);
  cap3.setThresholds(12, 6);

  delay(500);
  Serial.println("05_full_integration ready");
}

// ─── Main loop ────────────────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();
  if (now - lastScan < SCAN_INTERVAL_MS) {
    while (usbMIDI.read()) {} // 每圈清 USB inbox（避免 host 塞住）
    return;
  }
  lastScan = now;

  // ── 1. 按鈕事件（邊緣觸發） ──────────────────────────────────────────────────
  uint16_t t1 = cap1.touched();
  uint16_t t2 = cap2.touched();
  uint16_t t3 = cap3.touched();

  // MPR#1 Ch8 CUE, Ch9 Play, Ch10 SYNC, Ch11 PAD1
  emitButtonEdge(t1, lastTouched1, 8,  36); // CUE
  emitButtonEdge(t1, lastTouched1, 9,  37); // Play
  emitButtonEdge(t1, lastTouched1, 10, 38); // SYNC
  emitButtonEdge(t1, lastTouched1, 11, 40); // PAD1
  // MPR#2 Ch10 PAD2, Ch11 PAD3
  emitButtonEdge(t2, lastTouched2, 10, 41); // PAD2
  emitButtonEdge(t2, lastTouched2, 11, 42); // PAD3
  // MPR#3 Ch5 PAD4
  emitButtonEdge(t3, lastTouched3, 5,  43); // PAD4

  lastTouched1 = t1;
  lastTouched2 = t2;
  lastTouched3 = t3;

  // ── 2. Jog（MPR#1 Ch0–7） ────────────────────────────────────────────────────
  float jogAngle = jogVectorAngle(cap1);
  bool jogTouch = (jogAngle >= 0);

  if (jogTouch != lastJogTouch) {
    if (jogTouch) usbMIDI.sendNoteOn(48, 127, 1);
    else          usbMIDI.sendNoteOff(48, 0, 1);
    lastJogTouch = jogTouch;
  }

  if (jogTouch) {
    if (lastJogAngle >= 0) {
      float delta = jogAngle - lastJogAngle;
      if (delta >  180) delta -= 360;
      if (delta < -180) delta += 360;
      // degrees-per-tick → signed 7-bit。30°/tick ≒ 快速刮碟；clamp 到 ±63
      int scaled = (int)delta;
      if (scaled >  63) scaled =  63;
      if (scaled < -63) scaled = -63;
      usbMIDI.sendControlChange(16, 64 + scaled, 1);
    }
    lastJogAngle = jogAngle;
  } else {
    lastJogAngle = -1;
  }

  // ── 3. Tempo（MPR#2 Ch0–9）→ 14-bit CC 14/46 ───────────────────────────────
  float tempo01 = sliderCentroid(cap2, 0, 10);
  if (tempo01 >= 0) {
    int t14 = (int)(tempo01 * 16383);
    if (t14 < 0) t14 = 0; else if (t14 > 16383) t14 = 16383;
    if (lastTempo14 < 0 || abs(t14 - lastTempo14) >= TEMPO_DEADBAND) {
      usbMIDI.sendControlChange(14, (t14 >> 7) & 0x7F, 1); // MSB 先
      usbMIDI.sendControlChange(46, t14 & 0x7F, 1);         // LSB 後
      lastTempo14 = t14;
    }
  }

  // ── 4. Volume（MPR#3 Ch0–4）→ 7-bit CC 7 ───────────────────────────────────
  float vol01 = sliderCentroid(cap3, 0, 5);
  if (vol01 >= 0) {
    int v7 = (int)(vol01 * 127);
    if (v7 < 0) v7 = 0; else if (v7 > 127) v7 = 127;
    if (lastVolume < 0 || abs(v7 - lastVolume) >= VOLUME_DEADBAND) {
      usbMIDI.sendControlChange(7, v7, 1);
      lastVolume = v7;
    }
  }

  while (usbMIDI.read()) {}
}
