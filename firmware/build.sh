#!/usr/bin/env bash
# 用 arduino-cli 編譯所有 tests/ sketch
# 前置：
#   1. arduino-cli 已裝（本 repo 建議 ~/.local/bin/arduino-cli，版本 1.4.1+）
#   2. 已執行 arduino-cli core install teensy:avr
#   3. 已執行 arduino-cli lib install "Adafruit MPR121"
set -e

cd "$(dirname "$0")"

# 03 / 04（需送 usbMIDI）用 serialmidi USB type；01 / 02 不需 MIDI，但用 serialmidi 也可
USB_TYPE="usb=serialmidi"
FQBN="teensy:avr:teensy40:${USB_TYPE}"

SKETCHES=(
  "tests/01_i2c_scan"
  "tests/02_mpr121_raw"
  "tests/03_midi_out"
  "tests/04_algorithms"
)

for s in "${SKETCHES[@]}"; do
  echo "=== Compiling $s ==="
  arduino-cli compile --fqbn "$FQBN" "$s"
done

echo
echo "All 4 sketches compiled OK."
