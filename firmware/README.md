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
    ├── 04_algorithms/       Phase 4：Slider 質心 + Jog 向量和
    └── 05_full_integration/ Phase 5/6：3 顆 MPR121 完整韌體（30 電極 → 完整 MIDI 協議）
```

完整測試流程見 [../docs/hardware/06-testing-plan.md](../docs/hardware/06-testing-plan.md)。

## 環境需求

| 工具 | 版本 | 備註 |
|---|---|---|
| Arduino IDE | 2.3.8（最低 2.0.4） | |
| Teensyduino | 1.60 | |
| Adafruit_MPR121 | 1.2.1（1.1.3+ 皆可） | Tools → Manage Libraries 搜尋安裝 |

## 使用方式

1. Arduino IDE → File → Open → 選擇某支 `.ino`
2. Tools → Board → Teensy → Teensy 4.0
3. Tools → USB Type → **Serial + MIDI**（03/04 必要）
4. Tools → Port → Teensy 對應 port
5. 點上傳按鈕

## 或用 arduino-cli（免 GUI 編譯）

本 repo 附 `firmware/build.sh`，一次編完所有 sketch。首次安裝：

```bash
# arduino-cli 裝到 ~/.local/bin（不用 sudo）
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh \
  | BINDIR=$HOME/.local/bin sh
export PATH=$HOME/.local/bin:$PATH

# 裝 Teensy core + Adafruit MPR121 library
arduino-cli config init --overwrite
arduino-cli config add board_manager.additional_urls https://www.pjrc.com/teensy/package_teensy_index.json
arduino-cli core update-index
arduino-cli core install teensy:avr
arduino-cli lib install "Adafruit MPR121"
```

然後跑：

```bash
./firmware/build.sh          # 編譯 4 支，全部過才會印 "All 4 sketches compiled OK."
```

**重要 — USB Type 參數：** 03 / 04 會用到 `usbMIDI`，所以 FQBN 要帶 `usb=serialmidi`：

```bash
arduino-cli compile --fqbn teensy:avr:teensy40:usb=serialmidi firmware/tests/03_midi_out
```

省略 `usb=serialmidi` 就會報 `error: 'usbMIDI' was not declared in this scope`。build.sh 已幫你帶。

上傳（需 udev rules — 見 docs/hardware/01-teensy-4.0-pinout.md）：

```bash
arduino-cli upload -p /dev/ttyACM0 --fqbn teensy:avr:teensy40:usb=serialmidi firmware/tests/01_i2c_scan
```
