# FlowDJ Hardware Manual

本資料夾是 FlowDJ 控制器硬體端的完整手冊，涵蓋從腳位、接線、通訊協定到測試流程。

目標：讓任何人（包含未來的自己）按照這份手冊就能把控制器從零接起來、跑起來、接到 FlowDJ Web UI。

---

## 硬體組成概覽

| 項目 | 規格 | 數量 |
|---|---|---|
| 微控制器 | Teensy 4.0 (Cortex-M7 @ 600 MHz)，**Micro-B USB** | 1 |
| 電容觸控 IC | MPR121（12 通道, I²C），黑色通用模組（3.3V-only） | 3 |
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
| `images/deck-layout-target.png` | 目標 deck 版型（單邊 deck 的功能配置） |

## 推進原則

- **先單元測試再整合**：每個元件先獨立驗證（I²C 掃到、Serial Monitor 讀到、MIDI 送出、UI 收到），再做下一步。
- **銅箔膠帶先行**：測試階段用銅箔代替導電油墨，電氣特性幾乎一樣但好拆好改。油墨只在最終定版時上。
- **一顆 MPR121 一階段**：先讓 1 顆 MPR121 工作，再加到 2 顆、3 顆，最後 USB MIDI 串接。

---

## 軟體版本鎖

本手冊以下軟體版本驗證過：

| 工具 | 版本 | 用途 |
|---|---|---|
| Arduino IDE | 2.3.8（最低 2.0.4） | 寫 / 編譯 / 上傳 Teensy 韌體 |
| Teensyduino | 1.60 | Arduino IDE 的 Teensy 支援 |
| Adafruit_MPR121 library | 1.2.1（1.1.3+ 皆可） | 讀 MPR121 |
| Node.js | 18+ | React UI 開發 |
| Chrome / Edge | 任何近期版本 | Web MIDI 測試（Safari 不支援） |

詳見 [06-testing-plan.md 的 Phase 0](06-testing-plan.md#phase-0--環境準備)。

---

## Bill of Materials (BOM)

預估總價 < NT$2,000（不含桌上工具）：

| 料件 | 數量 | 參考來源 | 估價 (TWD) |
|---|---|---|---|
| Teensy 4.0 | 1 | [PJRC 直購](https://www.pjrc.com/store/teensy40.html) / 露天 / 蝦皮 | $800 |
| MPR121 模組（黑色通用版） | 3 | 蝦皮 / 露天 / Aliexpress | $60 × 3 |
| Micro-B USB 線 | 1 | 任何 3C 店 | $50 |
| 標準麵包板（830 點）或 EIC-104 | 1 | 露天 / 蝦皮 | $80 |
| 公對公杜邦線（彩色 40 條） | 1 組 | 露天 / 蝦皮 | $50 |
| 22 AWG 單芯線 | 0.5 m | 五金行 / 電料行 | $30 |
| 銅箔膠帶（0.5–2 cm 寬） | 1 捲 | 文具店 / 五金行 | $80 |
| 10 kΩ 電阻（1/4 W） | 2 (備用) | 電料行 | $5 |
| 0.1 µF 陶瓷電容（選配） | 3 | 電料行 | $10 |
| 萬用電表 | 1 | 必備工具，建議投資 | $500–$2,000 |
| **導電油墨**（最終版用） | 50 ml | [Bare Conductive Electric Paint](https://www.bareconductive.com/products/electric-paint-50ml) | €15–25 |
| 壓克力 / 3D 列印機身 | — | 自行設計 | 因設計而異 |
| 塑膠氣墊 | — | 已有 | — |

---

## 常見問題速查（Troubleshooting Index）

| 遇到 | 去哪看 |
|---|---|
| 上傳 Teensy 失敗（Linux permission denied） | [01 - Linux udev rules](01-teensy-4.0-pinout.md#linux-額外步驟udev-rules-) |
| I²C scanner 掃不到裝置 | [03 - 常見接錯](03-wiring.md#常見接錯) |
| 掃到裝置但位址不對 | [02 - I²C 位址設定](02-mpr121-pinout.md#ic-位址設定重點三顆-mpr121-的靈魂) |
| Slider / Jog 數值一直跳 | [05 - 校正與微調](05-centroid-algorithm.md#校正與微調) |
| Safari 收不到 MIDI | [04 - 瀏覽器支援表](04-midi-protocol.md#瀏覽器-web-midi-支援2026-現況) |
| 銅箔電極不靈敏 | [02 - 觸控門檻](02-mpr121-pinout.md#觸控門檻threshold) |
| 上油墨後整個變不準 | [02 - 導電油墨電極的特殊注意](02-mpr121-pinout.md#導電油墨電極的特殊注意) |

---

## 參考資料

**硬體：**
- [PJRC Teensy 4.0 pinout](https://www.pjrc.com/teensy/pinout.html)
- [PJRC Teensy 4.0 spec & 購買](https://www.pjrc.com/store/teensy40.html)
- [PJRC 論壇](https://forum.pjrc.com/)（遇到硬體問題最快解答）
- [Adafruit MPR121 tutorial](https://learn.adafruit.com/adafruit-mpr121-12-key-capacitive-touch-sensor-breakout-tutorial/overview)
- [MPR121 Hookup Guide — SparkFun](https://learn.sparkfun.com/tutorials/mpr121-hookup-guide/all)
- [MPR121 Datasheet (NXP)](https://www.nxp.com/docs/en/data-sheet/MPR121.pdf)

**軟體 library：**
- [Adafruit_MPR121 (GitHub)](https://github.com/adafruit/Adafruit_MPR121)
- [BareConductive/mpr121 (GitHub)](https://github.com/BareConductive/mpr121)（導電油墨調整進階）
- [Teensy Wire library 文件](https://www.pjrc.com/teensy/td_libs_Wire.html)
- [Teensy USB MIDI 文件](https://www.pjrc.com/teensy/td_midi.html)

**MIDI / Web MIDI：**
- [MIDI 1.0 訊息總表](https://midi.org/summary-of-midi-1-0-messages)
- [Web MIDI API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Web_MIDI_API)
- [caniuse: Web MIDI 瀏覽器支援](https://caniuse.com/midi)

**演算法：**
- [Cypress AN64846 — Getting Started with CapSense](https://www.infineon.com/dgdl/Infineon-AN64846_Getting_Started_with_CapSense-ApplicationNotes-v18_00-EN.pdf)（centroid 算法最清楚的文件）
- [Microchip AN1334 — Robust Touch Sensing Design](https://ww1.microchip.com/downloads/en/Appnotes/01334A.pdf)
- [Large capacitive wheel design — Sebastien Dumetz](https://sdumetz.github.io/2016/08/15/capacitive-wheel.html)
- [Circular mean (Wikipedia)](https://en.wikipedia.org/wiki/Circular_mean)
