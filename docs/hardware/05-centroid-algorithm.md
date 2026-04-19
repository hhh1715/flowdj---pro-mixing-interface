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
2. **filtered / baseline 的單位**：MPR121 內部是 10-bit，但 Adafruit library 回傳的 baseline 是 **移位過的 8-bit**，要比較時記得 `baselineData(i) << 2`：
   ```cpp
   int delta = ((int)cap.baselineData(i) << 2) - (int)cap.filteredData(i);
   ```
   （或者兩者都不移位，只要一致就好）
3. **Dead zone（死區）**：手指完全沒按時，演算法輸出可能跳來跳去。加一個 `weight_sum` 最小閾值（上面程式碼的 `< 10`）過濾。
4. **物理排列要跟 channel index 對應**：如果 pad 1 接 Ch0、pad 2 接 Ch1、... 就照順序。如果接亂了，用一個查表陣列轉換：
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

→ 手指在 63.5° 處（在 45° 跟 90° 之間稍微偏 90°，合理！因為 pad 1 的權重比較大但 90° 方向比較單純）

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
    int delta = ((int)cap1.baselineData(ch) << 2) - (int)cap1.filteredData(ch);
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

### 低通濾波輸出
連續幾次 centroid 結果做 EMA（指數移動平均）避免顫抖：
```cpp
static float ema = 0;
float raw = readSliderCentroid();
ema = 0.7 * ema + 0.3 * raw; // α = 0.3 的低通
```

---

## 參考資料

- [Large capacitive wheel design — Sebastien Dumetz](https://sdumetz.github.io/2016/08/15/capacitive-wheel.html)（本章的設計靈感來源）
- [NXP AN3863 — Designing Touch Sensing Electrodes](https://www.nxp.com/docs/en/application-note/AN3863.pdf)（NXP 官方 app note，三角電極、slider 設計）
- [Adafruit MPR121 filtered data API](https://github.com/adafruit/Adafruit_MPR121/blob/master/Adafruit_MPR121.h)
