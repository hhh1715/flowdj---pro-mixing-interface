# 01 — Teensy 4.0 腳位說明

## 基本規格

| 項目 | 規格 |
|---|---|
| MCU | NXP i.MX RT1062 (ARM Cortex-M7) |
| 時脈 | 600 MHz |
| 邏輯電壓 | **3.3V**（I/O 不可接 5V，會燒） |
| 供電方式 | USB-C 5V（板上 regulator 降壓到 3.3V） |
| Flash | 2 MB |
| RAM | 1 MB |
| USB | 480 Mbps（高速） |
| I²C 匯流排 | 3 組（Wire / Wire1 / Wire2） |
| 程式開發 | Arduino IDE + Teensyduino 擴充 |

## 腳位卡參考圖

- **正面**：[images/teensy-4.0-pinout-front.png](images/teensy-4.0-pinout-front.png)
- **背面**：[images/teensy-4.0-pinout-back.png](images/teensy-4.0-pinout-back.png)

（來源：PJRC 官方，[https://www.pjrc.com/teensy/pinout.html](https://www.pjrc.com/teensy/pinout.html)）

---

## 本專案實際會用到的腳位

我們只用 **USB + 電源 + 1 組 I²C**，超簡單。

| Teensy 腳位 | 功能 | 本專案用途 |
|---|---|---|
| **USB** | Type-C USB 2.0 | 供電 + USB MIDI 資料 |
| **3.3V** | 3.3V 電源輸出（最大 ~250 mA） | 接到 3 顆 MPR121 的 VIN |
| **GND** | 接地 | 全部共用 GND |
| **Pin 18** | SDA0（Wire） | 接到 3 顆 MPR121 的 SDA（並聯） |
| **Pin 19** | SCL0（Wire） | 接到 3 顆 MPR121 的 SCL（並聯） |

備用（萬一要擴充）：
- **Pin 17**：SDA1（Wire1），若想把某顆 MPR121 掛到第二條 bus
- **Pin 16**：SCL1（Wire1）
- **Pin 0/1**：若要接 MPR121 的 IRQ 中斷線（**本專案不用**，我們用 polling 不用中斷）

## 腳位位置記憶訣竅

Teensy 4.0 是**上視圖 14 孔 × 2 排** 的 DIP 格式。從 USB 端開始，**右邊**那排由上到下是 Pin 0 → 13；**左邊**那排由下到上是 Pin 14 → 23。

簡化圖：

```
         ┌──── USB-C ────┐
    GND ─┤ 0          23 ├─ 3.3V
         ┤ 1          22 │
         ┤ 2          21 │
         ┤ 3          20 │
         ┤ 4          19 │── SCL0  ← 本專案
         ┤ 5          18 │── SDA0  ← 本專案
         ┤ 6          17 │   (SDA1 備用)
         ┤ 7          16 │   (SCL1 備用)
         ┤ 8          15 │
         ┤ 9          14 │
         ┤10          13 │── 板載 LED（測試用）
         ┤11          12 │
         ┤12 Vin GND 3.3V│── 3.3V 電源輸出 ← 本專案
         └───────────────┘
```

**重點：3.3V 跟 GND 在板子尾端（離 USB 最遠那端）；SDA/SCL 在右排中段（Pin 18/19）。**

---

## 供電方式

兩種選擇：

### A. 用 USB 供電（預設、推薦）
- USB 接 PC → PC 透過 USB 提供 5V → Teensy 板上 regulator 降壓到 3.3V → 從 3.3V 腳輸出給 MPR121
- 3 顆 MPR121 平常電流總共 <10 mA，Teensy 的 3.3V 輸出（~250 mA）綽綽有餘

### B. 外接電源
- 如果未來沒接 PC 也要跑（做成獨立裝置），可以用 `Vin` 腳餵 5V
- 本專案 Demo 需要接 PC 所以用 A 就好

---

## Teensyduino 安裝

Teensy 不能直接用 Arduino IDE 原生支援，需要裝 PJRC 的 Teensyduino 擴充。

**安裝步驟：**
1. 先裝 Arduino IDE（建議 2.x 版）
2. 到 [https://www.pjrc.com/teensy/td_download.html](https://www.pjrc.com/teensy/td_download.html) 下載 Teensyduino 安裝包（Win/Mac/Linux 都有）
3. 執行安裝，會把 Teensy 板子支援檔加進 Arduino IDE
4. Arduino IDE 重開，Tools → Board 應該可以選到 **Teensy 4.0**

**編譯上傳流程（跟一般 Arduino 不一樣）：**
1. 點「上傳」按鈕 → Arduino IDE 編譯
2. 編譯完會跳出 **Teensy Loader** 視窗
3. 按 Teensy 板上的「PROGRAM」實體按鈕
4. Teensy Loader 自動燒錄

---

## USB 裝置類型設定（關鍵！）

Teensy 4.0 可以在 USB 上扮演很多角色（鍵盤、滑鼠、MIDI…）。本專案要選 **MIDI 或 Serial + MIDI**：

**Arduino IDE → Tools → USB Type → 選 `Serial + MIDI`**

- **Serial**：給我們 Serial Monitor 印 debug 訊息用
- **MIDI**：給 FlowDJ UI 收控制訊號用
- 兩個同時開，才能邊測邊看 log

（若只選 `MIDI` 會沒有 Serial Monitor 可除錯；只選 `Serial` 則無法送 MIDI。）

---

## 參考資料

- [PJRC Teensy 4.0 商品頁](https://www.pjrc.com/store/teensy40.html)
- [PJRC 官方腳位卡](https://www.pjrc.com/teensy/pinout.html)
- [互動式腳位圖](https://teensy40.pinout.xyz/)
- [Teensyduino 下載](https://www.pjrc.com/teensy/td_download.html)
