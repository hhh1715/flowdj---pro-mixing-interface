# 02 — MPR121 腳位說明

## IC 是什麼

**MPR121** 是 NXP 做的 12-channel proximity capacitive touch sensor controller。一顆小 IC，負責盯著 12 個電極，偵測電容變化，透過 I²C 把結果傳給 MCU。

## Breakout 板

本專案實際使用的是 **通用黑色 PCB 模組（MC-CVI 等廠牌）**，外觀是黑色 PCB，左側 6 腳（3.3V / IRQ / SCL / SDA / ADD / GND），右側 12 腳（電極 0–11）。

### 腳位圖

- **本專案實際使用（黑色通用版）**：[images/mpr121-pinout-black-generic.jpg](images/mpr121-pinout-black-generic.jpg)（MPR121 IC 本體腳位，對照用）
- **Adafruit 原版（藍色，參考用）**：[images/mpr121-pinout-original.jpg](images/mpr121-pinout-original.jpg)
- **Adafruit STEMMA QT 版（參考用）**：[images/mpr121-pinout-stemma.jpg](images/mpr121-pinout-stemma.jpg)

### 黑色通用模組 vs Adafruit 的關鍵差異 ⚠️

| 比較項 | Adafruit 藍板 | 黑色通用板（本專案） |
|---|---|---|
| 電源腳標示 | **VIN**（3–5V 皆可，板上有 regulator） | **3.3V**（只吃 3.3V，可能**沒有 regulator**） |
| 3.3V 輸出 | 有 `3Vo`（regulator 輸出） | 沒有 |
| 位址腳 | `ADDR` | `ADD` |
| 電極編號 | 同樣 0–11 | 同樣 0–11 |
| I²C pull-up | 板載 10kΩ（可用跳線短接停用） | 看廠牌，通常也有 |
| ADD 預設 | pull-down 到 GND（0x5A） | 需要確認（大多也是 0x5A） |

**👉 重要提醒：**
- 通用板的 **`3.3V` 腳只能接 3.3V！千萬不要接 5V**，會燒掉 IC。Teensy 4.0 的 3.3V 輸出腳接過去剛好。
- 若你的模組標示的是 `VCC` 而非 `3.3V`，先查賣家規格或用萬用表量板上是否有 regulator（通常 IC 旁邊會有一顆小的 SOT-23 封裝元件）。

### 腳位表（原版 Adafruit breakout）

**上排 — 12 個電極 + GND：**

| 標示 | 意義 |
|---|---|
| GND | 電極共用地 |
| 0 | 電極 0（Ch0） |
| 1 | 電極 1 |
| 2 | 電極 2 |
| 3 | 電極 3 |
| 4 | 電極 4 |
| 5 | 電極 5 |
| 6 | 電極 6 |
| 7 | 電極 7 |
| 8 | 電極 8 |
| 9 | 電極 9 |
| 10 | 電極 10 |
| 11 | 電極 11 |

**下排 — 電源與通訊：**

| 標示 | 意義 | 接到 |
|---|---|---|
| **VIN** | 電源正極（3V–5V，板上有 regulator） | Teensy 3.3V |
| **3Vo** | 板上 regulator 輸出 3.3V（可供其他裝置用） | **本專案不用** |
| **GND** | 電源地 | Teensy GND |
| **ADDR** | I²C 位址選擇（決定是 0x5A/0x5B/0x5C/0x5D） | 不同顆接不同位置 |
| **SDA** | I²C 資料線 | Teensy Pin 18 |
| **SCL** | I²C 時脈線 | Teensy Pin 19 |
| **IRQ** | 中斷輸出（有變化時拉低） | **本專案不用**（用 polling） |

---

## I²C 位址設定（重點！三顆 MPR121 的靈魂）

MPR121 的 `ADDR` 腳怎麼接決定位址：

| ADDR 接法 | 位址 | 本專案角色 |
|---|---|---|
| 接 GND（或懸空，板上預設 pull-down 到 GND） | **0x5A** | #1：按鈕 + Jog 前半 |
| 接 VCC（3.3V） | **0x5B** | #2：速度 slider |
| 接 SDA | **0x5C** | #3：PAD + 音量 fader |
| 接 SCL | **0x5D** | 保留 |

**實務做法：**
- **#1**：ADDR 腳不接（或拉到 GND），預設就是 0x5A
- **#2**：ADDR 腳用跳線拉到 3.3V
- **#3**：ADDR 腳用跳線接到 SDA（即 Teensy Pin 18）

這樣三顆 MPR121 的 SDA/SCL/VCC/GND 可以**並聯**接在一起（I²C 匯流排共用），位址區分靠 ADDR 腳。

---

## 電氣規格重點

| 參數 | 值 | 備註 |
|---|---|---|
| 工作電壓 | 3.3V（IC 本身） | breakout 上有 regulator，VIN 可接 3–5V |
| 靜態電流 | ~29 µA | 極省電 |
| 工作電流 | <1 mA | 正常讀取時 |
| 電極數 | 12 | 每顆 |
| 解析度 | 10-bit（0–1023） | filtered data |
| 感測範圍 | 最遠約 5 mm（穿過非導電材料） | 取決於電極大小 |
| I²C 速度 | 100 kHz 或 400 kHz | 預設 100 kHz 夠用 |

---

## 觸控門檻（Threshold）

MPR121 每個通道有兩個門檻：

- **Touch Threshold**：baseline 跟當前讀值的差超過這個 → 判「按下」
- **Release Threshold**：差小於這個 → 判「放開」

Adafruit library 預設：
- Touch = 12
- Release = 6

**本專案建議：**
- 按鈕類（CUE/Play/SYNC/PAD）：用預設 12/6
- Slider / Jog（質心用）：可以降到 **6/3**，讓邊緣 pad 的微弱訊號也能被讀進權重裡（質心靠「所有 pad 的強度」運作，越敏感越平滑）

實際值要在測試階段微調。

---

## Baseline 自動校正

MPR121 有內建 **auto-baseline tracking**：它持續觀察每個電極的「靜止電容值」，環境變化（溫度、濕度、附近有金屬）時慢慢跟著漂移 baseline。

**陷阱：**如果你**一直壓著** PAD 不放，baseline 會慢慢把「壓住」當成新的「沒按」→ 過幾秒後就偵測不到了。這是正常行為（你本來就該放掉再按）。

---

## 跟 Bare Conductive library 的關係

- **Adafruit_MPR121 library**：Arduino 官方生態最常用，API 簡單，本專案就用這個
- **BareConductive/mpr121 library**：Bare Conductive 家的，API 更完整（有 proximity mode、可設更多 register），想調進階設定時用
- 兩個都能跑在 Teensy 上，前期用 Adafruit 版就好

---

## 參考資料

- [Adafruit MPR121 Tutorial](https://learn.adafruit.com/adafruit-mpr121-12-key-capacitive-touch-sensor-breakout-tutorial)
- [MPR121 Datasheet (NXP)](https://www.nxp.com/docs/en/data-sheet/MPR121.pdf)
- [Adafruit MPR121 Arduino library (GitHub)](https://github.com/adafruit/Adafruit_MPR121)
- [BareConductive MPR121 library (GitHub)](https://github.com/BareConductive/mpr121)
- [MPR121 Hookup Guide — SparkFun](https://learn.sparkfun.com/tutorials/mpr121-hookup-guide/all)
