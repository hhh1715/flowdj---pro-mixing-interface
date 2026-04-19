# FlowDJ Firmware

Teensy 4.0 韌體，透過 3 顆 MPR121 讀電容觸控，用 USB MIDI 送到 FlowDJ Web UI。

## 目錄結構

```
firmware/
├── README.md           本檔
└── tests/              六階段測試流程的獨立 sketch
    ├── 01_i2c_scan/         Phase 1：掃 I²C bus 驗證 3 顆 MPR121
    ├── 02_mpr121_raw/       Phase 2：讀 touch state 驗證每個電極
    ├── 03_midi_out/         Phase 3：USB MIDI Note On/Off
    └── 04_algorithms/       Phase 4：Slider 質心 + Jog 向量和
```

完整測試流程見 [../docs/hardware/06-testing-plan.md](../docs/hardware/06-testing-plan.md)。

## 環境需求

| 工具 | 版本 | 備註 |
|---|---|---|
| Arduino IDE | 2.3.8（最低 2.0.4） | |
| Teensyduino | 1.60 | |
| Adafruit_MPR121 | 1.1.3 | Tools → Manage Libraries 搜尋安裝 |

## 使用方式

1. Arduino IDE → File → Open → 選擇某支 `.ino`
2. Tools → Board → Teensy → Teensy 4.0
3. Tools → USB Type → **Serial + MIDI**（03/04 必要）
4. Tools → Port → Teensy 對應 port
5. 點上傳按鈕

## 或用 arduino-cli

```bash
arduino-cli core install teensy:avr --additional-urls https://www.pjrc.com/teensy/package_teensy_index.json
arduino-cli lib install "Adafruit MPR121"
arduino-cli compile --fqbn teensy:avr:teensy40 firmware/tests/01_i2c_scan
arduino-cli upload -p /dev/ttyACM0 --fqbn teensy:avr:teensy40 firmware/tests/01_i2c_scan
```
