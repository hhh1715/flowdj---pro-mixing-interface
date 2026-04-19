// 03_midi_out — 用 MPR121 #1 的 12 通道送 Note On/Off
// Arduino IDE → Tools → USB Type 必須選 "Serial + MIDI"
// 驗收：PC 端 MIDI monitor 看到 Note On 36 + i (Channel 1)
// 參見 docs/hardware/06-testing-plan.md Phase 3

#include <Wire.h>
#include "Adafruit_MPR121.h"

Adafruit_MPR121 cap1;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  cap1.begin(0x5A);
  delay(1000);
}

uint16_t prev = 0;
void loop() {
  uint16_t curr = cap1.touched();

  for (int i = 0; i < 12; i++) {
    bool was = prev & (1 << i);
    bool now = curr & (1 << i);
    if (now && !was) {
      usbMIDI.sendNoteOn(36 + i, 127, 1);   // Channel 1, Note 36+i, velocity 127
      Serial.print("Note On: "); Serial.println(36 + i);
    } else if (!now && was) {
      usbMIDI.sendNoteOff(36 + i, 0, 1);
      Serial.print("Note Off: "); Serial.println(36 + i);
    }
  }
  prev = curr;

  while (usbMIDI.read()) {} // 清 USB inbox 避免 host 塞住
  delay(10);
}
