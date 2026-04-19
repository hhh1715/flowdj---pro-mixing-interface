# FlowDJ Hardware Manual

本資料夾是 FlowDJ 控制器硬體端的完整手冊，涵蓋從腳位、接線、通訊協定到測試流程。

目標：讓任何人（包含未來的自己）按照這份手冊就能把控制器從零接起來、跑起來、接到 FlowDJ Web UI。

---

## 硬體組成概覽

| 項目 | 規格 | 數量 |
|---|---|---|
| 微控制器 | Teensy 4.0 (Cortex-M7 @ 600 MHz) | 1 |
| 電容觸控 IC | Adafruit MPR121 (12 通道, I²C) | 3 |
| 觸控電極 | 銅箔膠帶（初期測試）→ 導電油墨（最終版） | 30 個電極 |
| 氣墊 | 塑膠氣墊覆蓋於電極上 | 全數 |
| 通訊 | USB MIDI（Class-Compliant，Win/Mac/Linux 免驅動） | — |

## 控制器功能（單邊 deck）

| 功能 | 元件 | 電極數 | 訊號類型 |
|---|---|---|---|
| Jog Wheel | 8 段弧形電極環 | 8 | 向量演算法 → 角度 + 方向 |
| 速度 slider | 10 段弧形電極 | 10 | 質心演算法 → 14-bit CC |
| 音量 fader | 5 段弧形電極 | 5 | 質心演算法 → 7-bit CC |
| CUE 鈕 | 單電極 | 1 | Note On/Off |
| Play/Pause 鈕 | 單電極 | 1 | Note On/Off |
| SYNC 鈕 | 單電極 | 1 | Note On/Off |
| PAD × 4 | 4 單電極 | 4 | Note On/Off |
| **合計** | — | **30** | — |

---

## 文件目錄

依建議閱讀順序排列：

1. [00-glossary.md](00-glossary.md) — 名詞解釋（MIDI、I²C、質心、CC…）
2. [01-teensy-4.0-pinout.md](01-teensy-4.0-pinout.md) — Teensy 4.0 腳位說明
3. [02-mpr121-pinout.md](02-mpr121-pinout.md) — MPR121 腳位說明、位址設定
4. [03-wiring.md](03-wiring.md) — 完整接線圖（Teensy + 3×MPR121 + 麵包板）
5. [04-midi-protocol.md](04-midi-protocol.md) — MIDI 訊息對照表
6. [05-centroid-algorithm.md](05-centroid-algorithm.md) — 質心與向量演算法
7. [06-testing-plan.md](06-testing-plan.md) — 六階段測試流程（含銅箔膠帶原型）
8. [07-fritzing-guide.md](07-fritzing-guide.md) — 用 Fritzing 產生麵包板風格示意圖

## 圖片

| 檔案 | 用途 |
|---|---|
| `images/teensy-4.0-pinout-front.png` | Teensy 4.0 正面腳位卡（來源：PJRC） |
| `images/teensy-4.0-pinout-back.png` | Teensy 4.0 背面腳位卡（來源：PJRC） |
| `images/mpr121-pinout-original.jpg` | MPR121 原版 breakout 腳位（來源：Adafruit） |
| `images/mpr121-pinout-stemma.jpg` | MPR121 STEMMA QT 版腳位（來源：Adafruit） |
| `images/mpr121-pinout-black-generic.jpg` | 黑色通用 MPR121 IC 本體腳位（對照用） |
| `images/wiring-diagram.svg` | 本專案完整接線示意圖（Teensy + 3×MPR121） |

## 推進原則

- **先單元測試再整合**：每個元件先獨立驗證（I²C 掃到、Serial Monitor 讀到、MIDI 送出、UI 收到），再做下一步。
- **銅箔膠帶先行**：測試階段用銅箔代替導電油墨，電氣特性幾乎一樣但好拆好改。油墨只在最終定版時上。
- **一顆 MPR121 一階段**：先讓 1 顆 MPR121 工作，再加到 2 顆、3 顆，最後 USB MIDI 串接。

## 參考資料

- [PJRC Teensy 4.0 pinout](https://www.pjrc.com/teensy/pinout.html)
- [Adafruit MPR121 tutorial](https://learn.adafruit.com/adafruit-mpr121-12-key-capacitive-touch-sensor-breakout-tutorial/overview)
- [BareConductive/mpr121 Arduino library](https://github.com/BareConductive/mpr121)
- [Large capacitive wheel design — Sebastien Dumetz](https://sdumetz.github.io/2016/08/15/capacitive-wheel.html)
- [MPR121 Hookup Guide — SparkFun](https://learn.sparkfun.com/tutorials/mpr121-hookup-guide/all)
