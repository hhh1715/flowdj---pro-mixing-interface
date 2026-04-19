# 06 — 測試計畫（六階段，獨立驗證）

原則：**最小可動系統先跑通，每加一個元件就驗一次**。出問題時才容易找原因。

整個流程設計成：**不需要導電油墨**也能走完前五個階段。用銅箔膠帶或甚至裸露的杜邦線尾端當電極即可。

---

## 總體時間估算

| 階段 | 預期時間 | 能否獨立驗證 |
|---|---|---|
| Phase 0：環境準備 | 30–60 min | — |
| Phase 1：I²C 掃描 | 10 min | ✓（只要 Arduino Monitor） |
| Phase 2：MPR121 原始資料 | 20 min | ✓（Arduino Monitor） |
| Phase 3：USB MIDI 輸出 | 20 min | ✓（PC 端 MIDI monitor） |
| Phase 4：演算法驗證 | 30 min | ✓（Arduino Monitor） |
| Phase 5：UI 接收 | 30 min | ✓（瀏覽器） |
| Phase 6：整合（油墨 + 氣墊） | 60+ min | 需要實體板子 |

---

## Phase 0 — 環境準備

### 目標
裝好所有軟體，確定 Teensy 能燒程式。

### 步驟

1. **裝 Arduino IDE**（2.x 版） [下載頁面](https://www.arduino.cc/en/software)
2. **裝 Teensyduino** 擴充 [下載頁面](https://www.pjrc.com/teensy/td_download.html)
3. 開 Arduino IDE，**Tools → Board → Teensy 4.0**
4. **Tools → USB Type → Serial + MIDI**
5. **裝 Adafruit MPR121 library**：Tools → Manage Libraries → 搜尋 `Adafruit_MPR121` → Install
6. 把 Teensy 用 USB 線接 PC
7. 燒個「板載 LED 閃爍」範例（File → Examples → Basics → Blink）確認燒錄流程 OK
   - 注意要按 Teensy 上的 PROGRAM 按鈕才會燒

### 驗收
- [ ] Arduino IDE 看得到 Teensy 4.0 選項
- [ ] Blink 範例燒完，板載橘色 LED 每秒閃一次

---

## Phase 1 — I²C 掃描（驗證 3 顆 MPR121 都活著）

### 前置
按 [03-wiring.md](03-wiring.md) 接好 3 顆 MPR121，用 checklist 量過電壓。

### 程式碼

在 `firmware/tests/01_i2c_scan/01_i2c_scan.ino` 建立：

```cpp
#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("I2C Scanner starting...");
}

void loop() {
  byte found = 0;
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("  Found device at 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      found++;
    }
  }
  Serial.print("Total devices: ");
  Serial.println(found);
  Serial.println("-----");
  delay(3000);
}
```

### 操作
1. 燒錄上去
2. 打開 Serial Monitor（115200 baud）

### 驗收
應該看到：
```
I2C Scanner starting...
  Found device at 0x5A
  Found device at 0x5B
  Found device at 0x5C
Total devices: 3
-----
```

**排錯：**
| 看到什麼 | 原因 | 檢查 |
|---|---|---|
| Total devices: 0 | SDA/SCL 根本沒通 | 線路、Teensy USB、Pin 18/19 |
| Total devices: 1（只 0x5A） | 另外兩顆 ADDR 腳接錯 | #2 的 ADDR 是否真的接到 3.3V、#3 是否接到 SDA |
| 看到 0x5D（不該有） | 可能第 4 顆 MPR121 ADDR 接到 SCL 了 | 確認每顆 ADDR 接法 |
| 看到一堆亂七八糟位址 | I²C pull-up 沒有或過弱 | 外加 4.7kΩ pull-up |

**全部 ✓ 才繼續下一階段。**

---

## Phase 2 — MPR121 原始資料（每個電極都能讀）

### 目標
確認每顆 MPR121 的 12 個通道**都能感應到手指**。這階段用**裸露的杜邦線尾端**當電極就好，不用銅箔。

### 程式碼

`firmware/tests/02_mpr121_raw/02_mpr121_raw.ino`：

```cpp
#include <Wire.h>
#include "Adafruit_MPR121.h"

Adafruit_MPR121 cap1, cap2, cap3;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Wire.begin();

  if (!cap1.begin(0x5A)) { Serial.println("MPR121 #1 not found!"); while (1); }
  if (!cap2.begin(0x5B)) { Serial.println("MPR121 #2 not found!"); while (1); }
  if (!cap3.begin(0x5C)) { Serial.println("MPR121 #3 not found!"); while (1); }

  Serial.println("3 MPR121s online. Touch any pad...");
  delay(1000); // 等 baseline 穩定
}

void loop() {
  uint16_t t1 = cap1.touched();
  uint16_t t2 = cap2.touched();
  uint16_t t3 = cap3.touched();

  // 只在有變化時印
  static uint16_t prev1 = 0, prev2 = 0, prev3 = 0;
  if (t1 != prev1 || t2 != prev2 || t3 != prev3) {
    Serial.print("  #1 (0x5A): ");
    for (int i = 0; i < 12; i++) Serial.print((t1 & (1<<i)) ? '1' : '.');
    Serial.print("   #2 (0x5B): ");
    for (int i = 0; i < 12; i++) Serial.print((t2 & (1<<i)) ? '1' : '.');
    Serial.print("   #3 (0x5C): ");
    for (int i = 0; i < 12; i++) Serial.print((t3 & (1<<i)) ? '1' : '.');
    Serial.println();
    prev1 = t1; prev2 = t2; prev3 = t3;
  }

  delay(20);
}
```

### 操作
1. 燒錄
2. 打開 Serial Monitor
3. 拿一條杜邦線插到某顆 MPR121 的某個 Ch 腳，**用手指碰杜邦線另一端**
4. 對應那個位置的 `.` 應該變成 `1`

### 驗收
- [ ] 3 顆 MPR121 初始化都成功
- [ ] 碰 #1 的 Ch 0 → 第一行第一位變 `1`
- [ ] 依次碰 Ch 0–11，全部能觸發
- [ ] 三顆都跑過一次 Ch 0–11

### 進階：讀 filtered data

若上述都過了，想看原始強度值（為 Phase 4 做準備），改用：

```cpp
for (int i = 0; i < 12; i++) {
  Serial.print(cap1.filteredData(i));
  Serial.print("\t");
}
Serial.println();
```

碰下去 filtered 應該**往下掉** 50–200 不等。

---

## Phase 3 — USB MIDI 輸出（跨 OS 驗證）

### 目標
確認 Teensy 能以 USB MIDI 裝置身份出現在 PC 上，且能送出 MIDI 訊息。

### 程式碼

`firmware/tests/03_midi_out/03_midi_out.ino`：

```cpp
#include <Wire.h>
#include "Adafruit_MPR121.h"

Adafruit_MPR121 cap1;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  cap1.begin(0x5A);
  delay(1000);
}

uint16_t prev = 0;
void loop() {
  uint16_t curr = cap1.touched();

  for (int i = 0; i < 12; i++) {
    bool was = prev & (1 << i);
    bool now = curr & (1 << i);
    if (now && !was) {
      // 按下：送 Note On
      usbMIDI.sendNoteOn(36 + i, 127, 1);
      Serial.print("Note On: "); Serial.println(36 + i);
    } else if (!now && was) {
      // 放開：送 Note Off
      usbMIDI.sendNoteOff(36 + i, 0, 1);
      Serial.print("Note Off: "); Serial.println(36 + i);
    }
  }
  prev = curr;

  while (usbMIDI.read()) {} // 清 inbox
  delay(10);
}
```

### PC 端準備 MIDI Monitor

選一個你 OS 對應的：

**Linux：**
```bash
# 安裝（Ubuntu/Debian）
sudo apt install alsa-utils

# 列出 MIDI 裝置
aconnect -l

# 監看（找到 Teensy 的 client ID，假設是 20）
aseqdump -p 20
```

**macOS：**下載 [MIDI Monitor](https://www.snoize.com/midimonitor/)（免費）

**Windows：**下載 [MIDI-OX](http://www.midiox.com/)（免費）

### 操作
1. 燒錄 Teensy
2. OS 應該自動認到 "Teensy MIDI" 裝置
3. 開 MIDI monitor，選 Teensy 為輸入源
4. 碰 MPR121 #1 的 Ch 0 → MIDI monitor 應顯示 `Note On 36 velocity 127 channel 1`

### 驗收
- [ ] OS 認得 Teensy 為 MIDI 裝置（不用裝驅動）
- [ ] 碰 Ch 0 → 看到 Note 36 (C2)
- [ ] 碰 Ch 1 → 看到 Note 37
- [ ] 放開 → 看到 Note Off
- [ ] **三個 OS 都試一次**（User 要 demo 跨平台）

---

## Phase 4 — 演算法驗證（Slider + Jog）

### 目標
centroid 跟 vector sum 的結果合理。

### 程式碼

`firmware/tests/04_algorithms/04_algorithms.ino`：

```cpp
#include <Wire.h>
#include <math.h>
#include "Adafruit_MPR121.h"

Adafruit_MPR121 cap1, cap2;

const int JOG_CH_START = 4;
const int JOG_N = 8;
const float JOG_ANGLES[8] = {0, 45, 90, 135, 180, 225, 270, 315};

float readSliderCentroid(Adafruit_MPR121 &cap, int start, int n) {
  long ws = 0, wsum = 0;
  for (int i = 0; i < n; i++) {
    int delta = ((int)cap.baselineData(start + i) << 2) - (int)cap.filteredData(start + i);
    int w = max(0, delta - 3);
    ws += (long)i * w;
    wsum += w;
  }
  if (wsum < 10) return -1;
  return (float)ws / wsum / (n - 1);
}

float readJogAngle(Adafruit_MPR121 &cap) {
  float sx = 0, sy = 0; long ws = 0;
  for (int i = 0; i < JOG_N; i++) {
    int delta = ((int)cap.baselineData(JOG_CH_START + i) << 2) - (int)cap.filteredData(JOG_CH_START + i);
    int w = max(0, delta - 3);
    float r = JOG_ANGLES[i] * M_PI / 180.0;
    sx += cos(r) * w; sy += sin(r) * w; ws += w;
  }
  if (ws < 10) return -1;
  float a = atan2(sy, sx) * 180.0 / M_PI;
  if (a < 0) a += 360;
  return a;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  cap1.begin(0x5A);
  cap2.begin(0x5B);
  delay(1000);
}

void loop() {
  float slider = readSliderCentroid(cap2, 0, 10);
  float jog = readJogAngle(cap1);

  Serial.print("Slider: ");
  if (slider < 0) Serial.print("----");
  else Serial.print(slider, 3);

  Serial.print("   Jog: ");
  if (jog < 0) Serial.println("----");
  else Serial.println(jog, 1);

  delay(100);
}
```

### 操作

把 10 條杜邦線接到 MPR121 #2 的 Ch 0–9，另一端分別貼 10 小段銅箔（或直接用裸露線尾），排成一列。

把 8 條杜邦線接到 MPR121 #1 的 Ch 4–11，另一端銅箔排成八角形。

### 驗收

**Slider：**
- [ ] 手指放最左（pad 0）→ 印出接近 `0.000`
- [ ] 手指放最右（pad 9）→ 印出接近 `1.000`
- [ ] 手指中間滑 → 數字**平滑**從 0 變到 1，沒有跳階

**Jog：**
- [ ] 手指放 0° 位置 → 印出接近 `0.0`
- [ ] 手指放 90° 位置 → 印出接近 `90.0`
- [ ] 手指繞一圈 → 數字連續走完 0 → 360，跨過 0/360 邊界時不會大跳

---

## Phase 5 — UI 接收（Web MIDI → React）

### 目標
在 Web UI 能即時看到硬體動作。

### 前置

整合 Phase 3 + 4 的韌體，燒一版**完整 MIDI 輸出**（按照 [04-midi-protocol.md](04-midi-protocol.md)）。

### React 端

`src/hardware/webmidi.ts`（M4 階段會建立詳細檔）：

```typescript
export async function initMIDI(onMessage: (msg: MIDIMessageEvent) => void) {
  if (!navigator.requestMIDIAccess) {
    throw new Error('Web MIDI not supported in this browser');
  }
  const access = await navigator.requestMIDIAccess();
  for (const input of access.inputs.values()) {
    console.log('MIDI input:', input.name);
    input.addEventListener('midimessage', onMessage);
  }
}
```

然後在 React 某個 component：

```typescript
useEffect(() => {
  initMIDI((e) => {
    console.log('MIDI:', [...e.data].map(b => b.toString(16).padStart(2, '0')).join(' '));
  });
}, []);
```

### 操作
1. `npm run dev` 起 Vite
2. 瀏覽器打開 `localhost:3000`，開 DevTools Console
3. Teensy 保持接著 USB
4. 碰 MPR121 任何電極 → Console 應該印出 hex MIDI 訊息

### 驗收
- [ ] Console 看到 MIDI 訊息
- [ ] 按按鈕 → 訊息符合 [04-midi-protocol.md](04-midi-protocol.md) 的對應
- [ ] 滑 slider → 看到連續的 CC 14/46

### 瀏覽器限制
- Chrome / Edge / Opera：支援 Web MIDI，需使用者第一次授權
- Safari (macOS 14+)：支援
- Firefox：**不支援**（到 2026 為止）→ Demo 用 Chrome
- 之後若要包 Electron，Electron 內建 Chromium 所以 Web MIDI 一定能用

---

## Phase 6 — 整合實體版（最後一步）

到這一步，**軟體全部已驗證**。剩下的都是機械/美術問題。

### 步驟

1. **把銅箔電極貼到壓克力/3D 列印件上**（按 [要完成功能部份.png](../../../../Desktop/DJ/要完成功能部份.png) 的形狀）
2. **把氣墊蓋上去**
3. **重新跑一次 Phase 2** 驗證每個電極還能觸發
   - 銅箔面積大 → 靈敏度可能**太敏感**，把 `cap.setThresholds(touch, release)` 的 touch 往上調（例如 20/10）
   - 氣墊距離電極太遠 → 不夠敏感，把 touch 往下調（例如 6/3）
4. **重新跑 Phase 4** 看質心值有沒有變化
   - 可能需要調 `noise_threshold` 或加 EMA 平滑
5. **開 UI，完整玩一遍**

### 驗收（Demo-ready）
- [ ] 所有按鈕（CUE/Play/SYNC/PAD×4）按下去 UI 有反應
- [ ] 速度 slider 滑動 UI BPM 數字連續變
- [ ] 音量 fader 滑動 UI 音量條跟著動
- [ ] Jog wheel 轉動 UI 波形跟著刮
- [ ] **三個 OS 都能 work**

---

## 進度追蹤 checklist

複製到你 PR description 或 issue 裡打勾：

```
[ ] Phase 0: 環境 OK
[ ] Phase 1: I²C 掃到 3 顆 MPR121
[ ] Phase 2: 3 顆 × 12 通道全部能讀
[ ] Phase 3: USB MIDI 跨 3 OS 驗證
[ ] Phase 4: Slider centroid 平滑、Jog 角度連續
[ ] Phase 5: React UI 能收 MIDI
[ ] Phase 6: 銅箔電極整合 → 氣墊整合 → 油墨定版
```
