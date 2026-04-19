# 01 — Teensy 4.0 腳位說明

## 基本規格

| 項目 | 規格 |
|---|---|
| MCU | NXP i.MX RT1062 (ARM Cortex-M7) |
| 時脈 | 600 MHz |
| 邏輯電壓 | **3.3V**（I/O 不可接 5V，會燒） |
| 供電方式 | **Micro-B USB** 5V（板上 regulator 降壓到 3.3V） |
| USB 接頭 | **Micro-B**（⚠️ 不是 USB-C！買線時別買錯） |
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
| **USB** | **Micro-B** USB 2.0 High Speed（480 Mbps） | 供電 + USB MIDI 資料 |
| **3.3V** | 3.3V 電源輸出（最大 ~250 mA） | 接到 3 顆 MPR121 的 `3.3V` 腳（黑色通用板；Adafruit 叫 `VIN`） |
| **GND** | 接地 | 全部共用 GND |
| **Pin 18** | SDA0（Wire） | 接到 3 顆 MPR121 的 SDA（並聯） |
| **Pin 19** | SCL0（Wire） | 接到 3 顆 MPR121 的 SCL（並聯） |

備用（萬一要擴充）：
- **Pin 17**：SDA1（Wire1），若想把某顆 MPR121 掛到第二條 bus
- **Pin 16**：SCL1（Wire1）
- **Pin 0/1**：若要接 MPR121 的 IRQ 中斷線（**本專案不用**，我們用 polling 不用中斷）

## 腳位位置怎麼找

⚠️ **不要看下面隨便畫的圖就開工**。以 PJRC 官方腳位卡為準：

- 📄 **官方正面卡（PDF）**：https://www.pjrc.com/teensy/card10a_rev2_web.pdf
- 📄 **官方背面卡（PDF）**：https://www.pjrc.com/teensy/card10b_rev2_web.pdf
- 🖼️ **本 repo 圖片**：[images/teensy-4.0-pinout-front.png](images/teensy-4.0-pinout-front.png)、[images/teensy-4.0-pinout-back.png](images/teensy-4.0-pinout-back.png)
- 🌐 **互動式腳位圖**：https://teensy40.pinout.xyz/

本專案**實際只會用到 4 個腳位**，對照官方卡認出以下位置就好：

```
USB（Micro-B）端朝上，正面朝你看：

  左排（從上到下）         右排（從上到下）
  ┌──────────────┐        ┌──────────────┐
  │ GND          │        │ 3.3V         │  ← 3.3V 電源輸出（給 MPR121）
  │ Pin 0        │        │ Pin 23       │
  │ Pin 1        │        │ Pin 22       │
  │ ...          │        │ ...          │
  │ Pin 5        │        │ Pin 19 ← SCL0 │  ← I²C 時脈（接 MPR121 SCL）
  │ Pin 6        │        │ Pin 18 ← SDA0 │  ← I²C 資料（接 MPR121 SDA）
  │ ...          │        │ ...          │
  │ Pin 12       │        │ Pin 13 (LED) │
  └──────────────┘        └──────────────┘
       └────── 板子尾端（非 USB 端）有額外 Vin / GND / 3.3V / program pad ──────┘
```

**要用的 4 個腳位**：`3.3V`（右排最頂）、`GND`（左排最頂）、`Pin 18 / Pin 19`（右排中段偏下）。
實體位置在板子上有白色絲印標示，每一顆都會寫 `3.3`、`GND`、`18`、`19`。

> 若拿到 Teensy 4.1（更大、多一些腳位），Pin 18/19 位置**相同**，但板型不一樣，請改看 [card11a_rev2_web.pdf](https://www.pjrc.com/teensy/card11a_rev2_web.pdf)。

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

**版本鎖（本手冊驗證版本）：**
- Arduino IDE **2.3.x**（最低 2.0.4；2.3.8 是 2026 年的當前版）
- Teensyduino **1.60**（2026 年當前版）
- Adafruit_MPR121 library **1.1.3**

**安裝步驟：**
1. 先裝 Arduino IDE 2.3+： [arduino.cc/en/software](https://www.arduino.cc/en/software)
2. 到 [pjrc.com/teensy/td_download.html](https://www.pjrc.com/teensy/td_download.html) 下載 Teensyduino 安裝包（Win/Mac/Linux 都有）
3. 執行安裝（會自動偵測 Arduino IDE 位置，把 Teensy 板子支援檔灌進去）
4. Arduino IDE 重開，Tools → Board → **Teensy → Teensy 4.0**

### Linux 額外步驟（udev rules）⚠️

Linux 上不裝 udev rules 會**無法上傳**（permission denied）。執行一次：

```bash
curl -L https://www.pjrc.com/teensy/00-teensy.rules \
  | sudo tee /etc/udev/rules.d/00-teensy.rules
sudo udevadm control --reload-rules
```

然後把 Teensy 拔插一次。

### Windows 上的驅動

Teensyduino 安裝時會自動處理，第一次插入 Teensy 會被認成 HID 裝置。不用另外裝。

### PROGRAM 按鈕在哪

Teensy 4.0 板子上**靠近 Micro-B 接頭邊緣**有一顆很小的黑色實體按鈕（旁邊不一定有絲印，但對照 [PJRC 照片](https://www.pjrc.com/store/teensy40.html) 很好認）。Teensyduino 安裝後通常不用每次按 —— 但如果上傳卡住，按一下就強制進入 bootloader。

**編譯上傳流程：**
1. 點「上傳」按鈕 → Arduino IDE 編譯
2. 編譯完會跳出 **Teensy Loader** 視窗
3. 第一次可能需要按 Teensy 板上的實體按鈕，之後通常會自動燒

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
- [PJRC 官方腳位卡（HTML）](https://www.pjrc.com/teensy/pinout.html)
- [互動式腳位圖](https://teensy40.pinout.xyz/)
- [Teensyduino 下載](https://www.pjrc.com/teensy/td_download.html)
- [PJRC Wire library for Teensy](https://www.pjrc.com/teensy/td_libs_Wire.html)（確認 Pin 18/19 = SDA0/SCL0）
- [PJRC USB MIDI 文件](https://www.pjrc.com/teensy/td_midi.html)（`usbMIDI.sendNoteOn` 等 API 參考）
- [PJRC 技術論壇](https://forum.pjrc.com/)（遇到硬體問題最快能找到解答的地方）
- [Paul Stoffregen 官方 Getting Started 影片](https://www.youtube.com/watch?v=G5Nzn9rhOkE)
