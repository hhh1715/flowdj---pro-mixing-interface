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
| 電源腳標示 | **VIN**（3–5V 皆可，板上有 regulator） | **3.3V**（只吃 3.3V，**沒有 regulator**） |
| 3.3V 輸出 | 有 `3Vo`（regulator 輸出） | 沒有 |
| 位址腳 | `ADDR`（4 字） | `ADD`（3 字） |
| 電極編號 | 同樣 0–11 | 同樣 0–11 |
| I²C pull-up | 板載 10 kΩ（可用跳線短接停用） | 看廠牌，**多數也是 10 kΩ**（要用萬用表確認） |
| ADD 預設 | pull-down 到 GND（0x5A） | 通常也是 0x5A，但**建議外接跳線到 GND 保險**（見下方） |

**👉 重要提醒（會燒機的）：**

- 黑色通用板的 **`3.3V` 腳只能接 3.3V！千萬不要接 5V**，會燒掉 IC。Teensy 4.0 的 3.3V 輸出腳接過去剛好。
- 若你的模組標示的是 `VCC` 而非 `3.3V`，先用萬用表量**「`3.3V` 腳 → IC 第 17 腳（VDD）」是否直接導通**。導通 = 沒 regulator，只能餵 3.3V。若 IC 旁邊有一顆 SOT-23 封裝的小元件，那可能是 regulator，可以餵 5V。

**👉 `ADD` 預設是否為 0x5A 的驗證法：**

沒接東西時用萬用表量 `ADD` 到 `GND` 的電阻：
- 讀到 < 100 kΩ → 板上有 pull-down，懸空就是 0x5A
- 讀到 > 1 MΩ 或無窮大 → 板上**沒有** pull-down，懸空位址不確定，**必須用跳線拉到 GND**才能穩定 0x5A

為了保險，本手冊一律建議 **#1 的 `ADD` 接到 GND**（不依賴預設 pull-down），避免換板時行為不同。

**術語統一：** 本手冊以下都用 `ADD`（3 字，跟黑色通用板絲印一致）。如果你拿的是 Adafruit，心裡把 `ADD` → `ADDR` 對應即可。

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

**下排 — 電源與通訊（以**黑色通用板**絲印為準；括號內為 Adafruit）：**

| 標示 | 意義 | 接到 |
|---|---|---|
| **3.3V**（Adafruit: `VIN`） | 電源正極。黑板只吃 3.3V；Adafruit 吃 3–5V（板上有 regulator） | Teensy 3.3V |
| **—**（Adafruit: `3Vo`） | 僅 Adafruit 有，regulator 輸出 3.3V（給其他裝置用） | **本專案不用** |
| **GND** | 電源地 | Teensy GND |
| **ADD**（Adafruit: `ADDR`） | I²C 位址選擇（決定是 0x5A/0x5B/0x5C/0x5D） | 每顆接不同位置（見下方） |
| **SDA** | I²C 資料線 | Teensy Pin 18 |
| **SCL** | I²C 時脈線 | Teensy Pin 19 |
| **IRQ** | 中斷輸出（有變化時拉低，open-drain） | **本專案不用**（我們用 polling，每 10 ms 讀一次 I²C 就夠） |

---

## I²C 位址設定（重點！三顆 MPR121 的靈魂）

MPR121 的 `ADD` 腳怎麼接決定位址（對照 MPR121 datasheet §5.6）：

| `ADD` 接法 | 位址 | 本專案角色 |
|---|---|---|
| 接 GND | **0x5A** | #1：按鈕 + Jog |
| 接 VCC（3.3V） | **0x5B** | #2：速度 slider |
| 接 SDA | **0x5C** | #3：PAD + 音量 fader |
| 接 SCL | **0x5D** | 保留，本專案不用 |

**實務做法（用跳線直接接，不要懸空）：**
- **#1**：`ADD` → **GND**（不是「懸空」；見上一節說明）
- **#2**：`ADD` → **3.3V**
- **#3**：`ADD` → **SDA 線**（即 Teensy Pin 18，和 #1/#2 的 SDA 共享同一節點）

**為什麼 #3 的 ADD 接到 SDA 不會跳位址？**
MPR121 只在「通電那一刻」latch ADD 腳的電位來決定位址，之後 SDA 怎麼 toggle 都不影響（MPR121 datasheet §Initialization）。安心。

**ADD 接到 SDA/SCL 的副作用：**
會在 I²C bus 上加一點寄生電容（多一條線要充放電）。三顆 MPR121 範圍內可忽略；若之後想擴充到 10+ 顆，可以考慮用 I²C multiplexer（例如 TCA9548A）。

三顆 MPR121 的 SDA/SCL/3.3V/GND **並聯**（接在同一節點），位址區分靠 `ADD` 腳。

---

## 電氣規格重點

| 參數 | 值 | 備註 |
|---|---|---|
| 工作電壓 | 3.3V（IC 本身） | 黑色通用板只吃 3.3V；Adafruit 藍板有 regulator，VIN 可接 3–5V |
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
- **Release Threshold**：差小於這個 → 判「放開」（要小於 touch，避免邊界抖動）

Adafruit_MPR121 library 預設：
- `MPR121_TOUCH_THRESHOLD_DEFAULT` = 12
- `MPR121_RELEASE_THRESHOLD_DEFAULT` = 6

### 調整 API

用 `setThresholds(touch, release)`（**注意拼寫**；舊版有 `setThreshholds` 拼錯版，已 deprecated）：

```cpp
cap.begin(0x5A);
cap.setThresholds(12, 6);  // 預設
```

或在 `begin()` 時直接傳：`cap.begin(0x5A, 12, 6);`

### 本專案**建議起點**（保守）

先用 Adafruit 預設 **12/6** 跑所有通道（包括 slider/jog）：
- 銅箔膠帶電極 + 杜邦線：12/6 通常直接能動
- 導電油墨電極（高阻抗）：可能要從 **40/20** 開始（Bare Conductive 對導電油墨的建議值）再慢慢往下降
- 頻繁誤觸發 → 往上調（16/8、20/10）
- 邊緣 pad 進不了 centroid 權重 → 往下調（8/4，**但不要直接跳到 6/3 或 3/1，太激進容易雜訊誤觸**）

### Slider / Jog 特殊處理

質心演算法其實**不靠 threshold**判斷位置 —— 它直接讀 `filteredData()` 跟 `baselineData()` 的差當權重。所以 slider/jog 的 threshold 可以比按鈕**稍寬鬆**（例如 10/5），讓「還沒達到 touch 判定」的微弱邊緣訊號也進得來。

實際值要在 [Phase 4 測試](06-testing-plan.md) 階段微調。

---

## Baseline 自動校正

MPR121 有內建 **auto-baseline tracking**：持續觀察每個電極的「靜止電容值」，環境變化（溫度、濕度、附近有金屬）時慢慢跟著漂移 baseline。

細節（來自 MPR121 datasheet §5.5 + NXP AN3891）：
- Baseline 暫存器是 **8-bit**，但對應的 filtered data 是 **10-bit**，所以 Adafruit library 的 `baselineData()` 已經把值左移 2 位還原到 10-bit 範圍（0–1020，步進 4）。
- 📌 **不要在自己的程式碼裡再 `<< 2` 一次** —— 見 [05-centroid-algorithm.md](05-centroid-algorithm.md) 注意事項 #2。
- Baseline tracking 的時間常數可以用 register `MHD_R` / `NHD_R` / `NCL_R` / `FDL_R` 調，Adafruit library 用預設值（對一般應用夠用）。

**陷阱：**如果你**一直壓著** PAD 不放，baseline 會慢慢（預設約 10 秒內）把「壓住」當成新的「沒按」→ 過幾秒後就偵測不到了。這是正常行為（你本來就該放掉再按），不用改設定。

---

## 跟 Bare Conductive library 的關係

- **Adafruit_MPR121 library**（本專案使用）：Arduino 官方生態最常用，API 簡單
  - 預設常數：`MPR121_I2CADDR_DEFAULT = 0x5A`
  - 常用方法：`begin(addr)`、`setThresholds(touch, release)`、`touched()`、`filteredData(ch)`、`baselineData(ch)`
  - GitHub：https://github.com/adafruit/Adafruit_MPR121
- **BareConductive/mpr121 library**：Bare Conductive 家的，API 更完整（有 proximity mode、可設 CDC/CDT register）
  - 做**導電油墨**時會想換到這個，因為他們對高阻抗電極有更多調整參數
  - GitHub：https://github.com/BareConductive/mpr121

兩個都能跑在 Teensy 上，前期用 Adafruit 版就好。油墨上版後若發現靈敏度不穩，再換 Bare Conductive 版本調 CDC/CDT。

## 導電油墨電極的特殊注意

最終用 [Bare Conductive Electric Paint](https://www.bareconductive.com/products/electric-paint-50ml) 或同類油墨時：
- 油墨的 trace 阻抗遠高於銅箔（~1 kΩ/cm²），會改變 MPR121 的充放電時間
- 建議在每條電極線上串 **1 MΩ 電阻接到 GND**（ESD 保護，油墨表面容易累積靜電）
- 若誤觸發變多，可能要把 CDC（charge current）調低（預設 16 µA → 可降到 1–4 µA）
- 參考：https://www.bareconductive.com/blogs/community/using-electric-paint-with-the-mpr121

---

## 參考資料

- [Adafruit MPR121 Tutorial](https://learn.adafruit.com/adafruit-mpr121-12-key-capacitive-touch-sensor-breakout-tutorial)
- [MPR121 Datasheet (NXP)](https://www.nxp.com/docs/en/data-sheet/MPR121.pdf)
- [Adafruit MPR121 Arduino library (GitHub)](https://github.com/adafruit/Adafruit_MPR121)
- [BareConductive MPR121 library (GitHub)](https://github.com/BareConductive/mpr121)
- [MPR121 Hookup Guide — SparkFun](https://learn.sparkfun.com/tutorials/mpr121-hookup-guide/all)
