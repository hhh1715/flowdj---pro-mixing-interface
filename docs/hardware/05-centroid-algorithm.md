# 05 — 質心與向量演算法

本章解釋：離散的多個 pad 如何轉成連續的位置值。

---

## 問題出在哪

假設 slider 有 10 個 pad，手指按下去：
- 只看「按到 / 沒按到」 → 只能得到 10 階（stair-stepping）
- DJ 需要連續滑順的手感

MPR121 其實不只回傳布林值 —— 它有 **10-bit filtered data**（0–1023），記錄每個電極當前的電容強度。用這個做加權平均 → 得到「手指重心在哪」 → **連續位置**。

這套演算法就叫 **Centroid**（質心）。Jog Wheel 是它的圓形版：**Vector Sum**（向量和）。

---

## 一維線性：Centroid

### 公式

```
           Σᵢ (positionᵢ × weightᵢ)
centroid = ─────────────────────────
               Σᵢ (weightᵢ)
```

其中：
- `positionᵢ` = 第 i 個 pad 的實體位置（0, 1, 2, ..., N-1）
- `weightᵢ` = 第 i 個 pad 的「觸碰強度」

### 「強度」怎麼算

MPR121 的 raw 資料：
- `baseline[i]` = 第 i 個電極的「沒按」基線值
- `filtered[i]` = 第 i 個電極當前的 filtered 值

手指靠近時 `filtered` 會**降低**（電容變大 → 充放電時間變長，filtered 值下降）。

強度：
```
delta[i] = baseline[i] - filtered[i]
weight[i] = max(0, delta[i] - noise_threshold)
```

`noise_threshold` 用來濾掉小雜訊，建議設 3–5。

### 具體範例

10 個 pad，手指按在 pad 3 和 4 之間稍微偏 3：

| i | position | filtered | baseline | delta | weight (noise_thr=3) |
|---|---|---|---|---|---|
| 0 | 0 | 200 | 200 | 0 | 0 |
| 1 | 1 | 200 | 200 | 0 | 0 |
| 2 | 2 | 195 | 200 | 5 | 2 |
| 3 | 3 | 120 | 200 | 80 | 77 |
| 4 | 4 | 140 | 200 | 60 | 57 |
| 5 | 5 | 190 | 200 | 10 | 7 |
| 6 | 6 | 200 | 200 | 0 | 0 |
| 7 | 7 | 200 | 200 | 0 | 0 |
| 8 | 8 | 200 | 200 | 0 | 0 |
| 9 | 9 | 200 | 200 | 0 | 0 |

分子 = 0 + 0 + 2×2 + 3×77 + 4×57 + 5×7 + 0 + 0 + 0 + 0
     = 4 + 231 + 228 + 35 = **498**

分母 = 2 + 77 + 57 + 7 = **143**

centroid = 498 / 143 ≈ **3.48**

歸一化到 0–1：
```
normalized = centroid / (N - 1) = 3.48 / 9 ≈ 0.386
```

→ 手指位置 = slider 的 38.6% 處

### Arduino / C++ 程式碼

```cpp
#include "Adafruit_MPR121.h"

Adafruit_MPR121 cap2; // MPR121 #2 @ 0x5B (速度 slider)

const int SLIDER_PADS = 10;
const int NOISE_THR = 3;

float readSliderCentroid() {
  long weighted_sum = 0;
  long weight_sum = 0;

  for (int i = 0; i < SLIDER_PADS; i++) {
    uint16_t filtered = cap2.filteredData(i);
    uint16_t baseline = cap2.baselineData(i);
    int delta = (int)baseline - (int)filtered;
    int weight = max(0, delta - NOISE_THR);

    weighted_sum += (long)i * weight;
    weight_sum += weight;
  }

  if (weight_sum < 10) return -1.0f; // 沒人按（權重太小，返回 -1 代表無效）

  float centroid = (float)weighted_sum / weight_sum;
  return centroid / (SLIDER_PADS - 1); // 歸一化 0–1
}
```

### 注意事項

1. **baseline 從哪來**：Adafruit library 的 `baselineData(i)` 回傳 MPR121 內部自動追蹤的 baseline。記得開機後等 1–2 秒讓 baseline 穩定再開始讀。

2. **不要對 `baselineData()` 再左移 2 位** ⚠️：MPR121 內部 baseline 存成 8-bit（是 10-bit filtered 值的高 8 位），但 **Adafruit library 在 `baselineData()` 內部已經 `<< 2` 還原成 10-bit**（見 [Adafruit_MPR121.cpp](https://github.com/adafruit/Adafruit_MPR121/blob/master/Adafruit_MPR121.cpp) 中 `return (bl << 2);`）。所以**外部不要再 shift**，否則會乘 4 倍變成負數，整個 delta 算錯：
   ```cpp
   // ✅ 正確
   int delta = (int)cap.baselineData(i) - (int)cap.filteredData(i);

   // ❌ 錯誤（會 over-shift，delta 恆為負）
   int delta = ((int)cap.baselineData(i) << 2) - (int)cap.filteredData(i);
   ```
   只是注意：`baselineData()` 的值是 4 的倍數（8-bit 左移 2 位），所以 delta 的「最小可分辨單位」是 4。

3. **Dead zone（死區）**：手指完全沒按時，演算法輸出可能跳來跳去。加一個 `weight_sum` 最小閾值（上面程式碼的 `< 10`）過濾。這個閾值建議設成 `NOISE_THR × pad 數 × 某係數`，例如 `NOISE_THR × SLIDER_PADS / 3`，而不是寫死 10。

4. **Palm reject（整個手掌壓下去）**：如果 `weight_sum` 超過某上限（例如單一 pad 最大權重 × 3），代表不是手指點觸而是整隻手壓上去，可以回傳 `-1` 忽略：
   ```cpp
   if (weight_sum > MAX_WEIGHT * 3) return -1.0f;  // palm reject
   ```

5. **物理排列要跟 channel index 對應**：如果 pad 1 接 Ch0、pad 2 接 Ch1、... 就照順序。如果接亂了，用一個查表陣列轉換：
   ```cpp
   int padOrder[] = {3, 1, 5, 0, 7, 2, 4, 6, 8, 9}; // 例如：實體 pad 0 接到 MPR121 Ch3
   ```

---

## 二維圓形：Vector Sum（Jog Wheel）

### 為什麼不用 Centroid

圓形的位置用角度表示（0°–360°），但 0° 和 360° 是同一個點。手指跨過那個「接縫」時，線性平均會算出 180°（完全錯）。

解法：把每個 pad 當成一個向量，向量加總後取角度。

### 公式

每個 pad 是一個向量：
```
vector_i = (cos(θᵢ) × weightᵢ, sin(θᵢ) × weightᵢ)
```

其中 `θᵢ` 是第 i 個 pad 在圓上的角度。8 個 pad 均勻分佈：
```
θ₀ = 0°     θ₁ = 45°    θ₂ = 90°    θ₃ = 135°
θ₄ = 180°   θ₅ = 225°   θ₆ = 270°   θ₇ = 315°
```

合向量：
```
sum_x = Σᵢ cos(θᵢ) × weightᵢ
sum_y = Σᵢ sin(θᵢ) × weightᵢ
```

手指角度：
```
angle = atan2(sum_y, sum_x)   // 回傳 -π 到 π
angle_deg = angle × 180 / π
if (angle_deg < 0) angle_deg += 360
```

### 具體範例

手指按在 pad 1（45°）跟 pad 2（90°）之間：
- weight[1] = 70, weight[2] = 50, 其他都是 0

```
sum_x = cos(45°)×70 + cos(90°)×50
      = 0.707×70 + 0×50
      = 49.5

sum_y = sin(45°)×70 + sin(90°)×50
      = 0.707×70 + 1×50
      = 99.5

angle = atan2(99.5, 49.5)
      = 1.108 rad
      = 63.5°
```

→ 手指在 63.5° 處（在 45° 跟 90° 之間，稍微偏 90° 那側 —— 因為 pad 2（90°）的 y 分量全部集中在 y 軸，而 pad 1（45°）的能量被拆到 x 與 y 各一半，所以 `sum_y`（99.5）遠大於 `sum_x`（49.5），合向量被拉向 y 軸方向）

### Arduino / C++ 程式碼

```cpp
#include <math.h>
#include "Adafruit_MPR121.h"

Adafruit_MPR121 cap1; // MPR121 #1 @ 0x5A (Jog 在 Ch 4–11)

const int JOG_PADS = 8;
const int JOG_START_CH = 4; // Jog 佔 Ch 4–11
const float JOG_ANGLES[8] = {0, 45, 90, 135, 180, 225, 270, 315};

float readJogAngle(bool *touched) {
  float sum_x = 0, sum_y = 0;
  long weight_sum = 0;

  for (int i = 0; i < JOG_PADS; i++) {
    int ch = JOG_START_CH + i;
    int delta = (int)cap1.baselineData(ch) - (int)cap1.filteredData(ch);
    int weight = max(0, delta - 3);

    float theta_rad = JOG_ANGLES[i] * M_PI / 180.0;
    sum_x += cos(theta_rad) * weight;
    sum_y += sin(theta_rad) * weight;
    weight_sum += weight;
  }

  *touched = (weight_sum >= 10);
  if (!*touched) return -1.0f;

  float angle = atan2(sum_y, sum_x) * 180.0 / M_PI;
  if (angle < 0) angle += 360;
  return angle; // 0–360
}
```

### 角速度 → CC 16 相對值

主迴圈裡：
```cpp
static float prev_angle = 0;
static bool prev_touched = false;

void updateJog() {
  bool touched;
  float angle = readJogAngle(&touched);

  // 觸摸狀態變化 → Note
  if (touched && !prev_touched) {
    usbMIDI.sendNoteOn(48, 127, 1);
  } else if (!touched && prev_touched) {
    usbMIDI.sendNoteOff(48, 0, 1);
  }

  // 角速度 → CC 16
  if (touched) {
    float delta = angle - prev_angle;
    // 處理環繞（跨過 0/360 邊界）
    if (delta > 180)  delta -= 360;
    if (delta < -180) delta += 360;

    // 限制在 ±63
    int delta_int = (int)constrain(delta, -63, 63);
    usbMIDI.sendControlChange(16, 64 + delta_int, 1);
    prev_angle = angle;
  }

  prev_touched = touched;
}
```

---

## 校正與微調

### Noise threshold
預設 3。若空閒時偶爾有誤觸發 → 調高到 5 或 7。若敏感度太低、邊緣 pad 進不了權重 → 調低到 1 或 2。

### 加權形式
除了簡單線性權重 `weight = delta - noise`，也可以試：
- **平方**：`weight = delta² `（大訊號拉更大，抗雜訊佳）
- **開根**：`weight = sqrt(delta)`（讓小訊號也有一定貢獻，邊緣更滑）

### 低通濾波輸出（Slider）
連續幾次 centroid 結果做 EMA（Exponential Moving Average，指數移動平均）避免顫抖：
```cpp
static float ema = 0;
float raw = readSliderCentroid();
if (raw >= 0) {
  ema = 0.7f * ema + 0.3f * raw; // α = 0.3 的低通
}
```
- α 越小越平滑（但反應越慢）；DJ 用途建議 α = 0.2–0.4
- 取樣 100 Hz 時，α = 0.3 對應約 5 Hz 截止頻率（`f_c ≈ α × f_s / (2π)`），手感跟雜訊抑制都還好

### 低通濾波（Jog 的正確做法）⚠️

Jog 的角度**不能**直接 EMA —— 因為 359° 跟 1° 平均會變 180°（錯得離譜）。正確做法：**對 `sum_x` / `sum_y` 做 EMA，最後才 `atan2`**：

```cpp
static float ema_x = 0, ema_y = 0;

float readJogAngleSmooth(bool *touched) {
  float sum_x = 0, sum_y = 0;
  long weight_sum = 0;
  // ... (同前面的向量加總程式碼，算出 sum_x, sum_y, weight_sum) ...

  // 對分量做 EMA，不要對角度做！
  ema_x = 0.7f * ema_x + 0.3f * sum_x;
  ema_y = 0.7f * ema_y + 0.3f * sum_y;

  *touched = (weight_sum >= 10);
  if (!*touched) return -1.0f;

  float angle = atan2(ema_y, ema_x) * 180.0f / M_PI;
  if (angle < 0) angle += 360;
  return angle;
}
```

---

## 參考資料

**演算法（centroid / 向量和）：**
- [Cypress AN64846 — Getting Started with CapSense](https://www.infineon.com/dgdl/Infineon-AN64846_Getting_Started_with_CapSense-ApplicationNotes-v18_00-EN.pdf)：業界最清楚的 centroid 算法說明（含 slider/wheel/trackpad）
- [Microchip AN1334 — Techniques for Robust Touch Sensing Design](https://ww1.microchip.com/downloads/en/Appnotes/01334A.pdf)：另一家 MCU 廠對 centroid 的詳細處理
- [Circular mean — Wikipedia](https://en.wikipedia.org/wiki/Circular_mean)：向量和 (vector sum) 的數學背景
- [Large capacitive wheel design — Sebastien Dumetz](https://sdumetz.github.io/2016/08/15/capacitive-wheel.html)：實作靈感來源（開源 DJ 轉盤）

**MPR121 專用：**
- [NXP AN3863 — Designing Touch Sensing Electrodes](https://www.nxp.com/docs/en/application-note/AN3863.pdf)：三角電極、slider 設計
- [NXP AN3944 — MPR121 Baseline System](https://www.nxp.com/docs/en/application-note/AN3944.pdf)：baseline 追蹤演算法細節
- [NXP AN3891 — Proximity Sensing with MPR121](https://www.nxp.com/docs/en/application-note/AN3891.pdf)：近距離偵測（若之後想做 hover）
- [Adafruit_MPR121 library source](https://github.com/adafruit/Adafruit_MPR121/blob/master/Adafruit_MPR121.cpp)：確認 `baselineData()` 已內部 `<< 2`
- [Bare Conductive MPR121 library](https://github.com/BareConductive/mpr121)：進階 API（可設 CDC/CDT、proximity mode），做導電油墨時會用到
- [SparkFun MPR121 Hookup Guide — Advanced Usage](https://learn.sparkfun.com/tutorials/mpr121-hookup-guide/all)：baseline 跟 threshold 調教的入門
