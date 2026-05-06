// 03_midi_out — 3 顆 MPR121 觸控 → USB MIDI Note On/Off
// Arduino IDE → Tools → USB Type 必須選 "Serial + MIDI"
// 驗收：PC 端 MIDI monitor 看到 Note On 36-71 (Channel 1)
// 參見 docs/hardware/06-testing-plan.md Phase 3

#include <Wire.h>
#include "Adafruit_MPR121.h"

#define NUM_CHIPS  3
#define NUM_ELE    12

// 跟 02_mpr121_raw 同樣的軟體觸控判斷（晶片內建 touch detection 在
// conductive ink 設置上失效，必須在 MCU 端自己做 baseline + delta）
// 跟 02 對齊用 3/1，2/0 在你的設置上會被雜訊打穿、瘋狂 ON/OFF
#define TOUCH_DELTA   3
#define RELEASE_DELTA 1
#define BASELINE_EMA  0.99f

// MIDI 對應：
//   #1 ELE0-11 → Note 36-47  (CUE=36, Play=37, SYNC=38, Jog 0°-315°=40-47)
//   #2 ELE0-11 → Note 48-59  (速度 slider top=48, bottom=57, 保留=58-59)
//   #3 ELE0-11 → Note 60-71  (PAD1-4=60-63, 音量 fader −=64..+=68, 保留=69-71)
//   全部 Channel 1

Adafruit_MPR121 caps[NUM_CHIPS];
const uint8_t addrs[NUM_CHIPS] = { 0x5A, 0x5B, 0x5C };
const char* names[NUM_CHIPS]   = { "#1", "#2", "#3" };

float baseline[NUM_CHIPS][NUM_ELE];
bool  touched[NUM_CHIPS][NUM_ELE];

void setup() {
  Serial.begin(115200);
  Wire.begin();

  for (int c = 0; c < NUM_CHIPS; c++) {
    if (!caps[c].begin(addrs[c])) {
      Serial.print("MPR121 "); Serial.print(names[c]);
      Serial.println(" not found!");
      while (1);
    }
  }
  delay(500);

  // 用第一筆 filtered 當初始 baseline
  for (int c = 0; c < NUM_CHIPS; c++) {
    for (int i = 0; i < NUM_ELE; i++) {
      baseline[c][i] = caps[c].filteredData(i);
      touched[c][i] = false;
    }
  }

  Serial.println("3 MPR121s online. Sending MIDI Notes 36-71 on Channel 1.");
}

void loop() {
  for (int c = 0; c < NUM_CHIPS; c++) {
    for (int i = 0; i < NUM_ELE; i++) {
      int filt = caps[c].filteredData(i);
      int delta = (int)baseline[c][i] - filt;

      bool prev = touched[c][i];
      bool now = prev;
      if (!prev && delta >= TOUCH_DELTA) now = true;
      else if (prev && delta <= RELEASE_DELTA) now = false;

      if (now != prev) {
        int note = 36 + c * 12 + i;
        if (now) {
          usbMIDI.sendNoteOn(note, 127, 1);
          Serial.print("ON  ");
        } else {
          usbMIDI.sendNoteOff(note, 0, 1);
          Serial.print("OFF ");
        }
        Serial.print(names[c]);
        Serial.print(" ELE");
        Serial.print(i);
        Serial.print(" → Note ");
        Serial.println(note);
      }
      touched[c][i] = now;

      // baseline 只在沒按住時追蹤
      if (!now) {
        baseline[c][i] = baseline[c][i] * BASELINE_EMA + filt * (1.0f - BASELINE_EMA);
      }
    }
  }

  // 清 USB MIDI inbox 避免 host 塞住
  while (usbMIDI.read()) {}
  delay(10);
}
