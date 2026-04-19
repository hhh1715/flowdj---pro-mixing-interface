# 00 — 名詞解釋

本專案會用到的所有硬體、通訊、演算法名詞，先在這裡統一說明。不熟的時候回來查。

---

## MIDI 相關

### MIDI
**Musical Instrument Digital Interface**。1983 年就訂好的工業標準，樂器跟電腦之間傳「要播哪個音、多大聲、什麼控制器轉到哪」的訊息。DJ 軟體（Traktor、rekordbox、Mixxx、Serato）都用 MIDI 接控制器。

### USB MIDI（Class Compliant）
MIDI 原本走 5-pin DIN 接頭；USB MIDI 是用 USB 傳輸同樣訊息的規格。Teensy 4.0 可以設定成「在 OS 眼中是一台 USB MIDI 裝置」，Win / Mac / Linux **完全免驅動**。

### Note On / Note Off
按鈕類訊息。格式：`Note On, Channel, NoteNumber, Velocity`。
- NoteNumber：0–127（例如 Middle C = 60）
- Velocity：0–127（力道，按鈕通常固定 127）
- Note Off 或 Note On with velocity=0 代表「放開」

### CC（Control Change）
**控制變化**訊息。用於連續控制（音量、旋鈕、推桿）。
格式：`CC, Channel, CCNumber, Value`。
- CCNumber：0–127（每個號碼有慣例用途，例如 CC7 = 主音量）
- Value：0–127（7-bit 解析度 = 128 階）

💡 **類比：** Note On/Off 像電燈開關（只有 0/1），CC 像調光旋鈕（可以是任何亮度）。

### 14-bit CC
標準 CC 只有 128 階，對 BPM、pitch 不夠細。把兩個 CC 組合起來（MSB + LSB）可達到 16384 階。
慣例：CCn 是高位（MSB），CCn+32 是低位（LSB）。例如 CC14（MSB）+ CC46（LSB）配對。

### MSB / LSB
- **MSB** = Most Significant Byte（高位）
- **LSB** = Least Significant Byte（低位）
- 14-bit 值 = MSB × 128 + LSB（×128 不是 ×256，因為 MIDI 資料位元組只有 **7-bit**；最高 bit 保留給 status 標記）

### Channel（MIDI 頻道）
MIDI 有 16 個頻道（1–16）。**Teensy `usbMIDI` API 用 1-based（1–16）**；只有在你手寫 raw status byte 時才會碰到 0-based 編碼（例如 `0x90` = Note On Channel 1）。一般單一 deck 用 Channel 1；未來若做兩個 deck，deck 2 用 Channel 2。

### Web MIDI API
瀏覽器用來讀寫 MIDI 裝置的標準 JavaScript API。入口是 `navigator.requestMIDIAccess()`。
- **支援**：Chrome 43+、Edge 79+、Opera 30+、Firefox 134+（2025-01 起預設開啟）
- **不支援**：Safari（2026 仍未實作）
- 文件：https://developer.mozilla.org/en-US/docs/Web/API/Web_MIDI_API

### Class Compliant
指 USB 裝置遵守 USB-IF 訂的標準 class（例如 MIDI class）。OS 會用內建驅動處理，不用安裝廠商驅動。Teensy 4.0 的 USB MIDI 是 Class Compliant，所以 Win/Mac/Linux 都免驅動。

### Running Status
MIDI 1.0 的頻寬優化：連續送同類型訊息時，後面可以省略 status byte 只送 data bytes。你用 `usbMIDI.sendNoteOn()` 不用管這個，library 會處理。

---

## I²C 相關

### I²C（I-Squared-C / I2C）
**Inter-Integrated Circuit**，主從式同步串列通訊協定。只要 **兩條線** 就能接多個裝置：
- **SDA**：Serial Data（資料線）
- **SCL**：Serial Clock（時脈線）

MPR121 走 I²C，Teensy 當 master，每顆 MPR121 是 slave。

### I²C 位址（Address）
每個 slave 裝置有獨一無二的 7-bit 位址。Teensy 呼叫某個位址時，只有那顆裝置會回應。MPR121 的 `ADD` 腳（Adafruit 版絲印為 `ADDR`）決定它用 4 個位址裡的哪一個：

| ADD 接到 | 位址 |
|---|---|
| GND | 0x5A |
| VCC | 0x5B |
| SDA | 0x5C |
| SCL | 0x5D |

### Pull-up 電阻
I²C 線平常應維持在高電位（HIGH），由 pull-up 電阻把線拉高；裝置要送 0 時才主動把線拉低。**SDA 和 SCL 各需要一顆 4.7–10 kΩ 電阻接到 3.3V**（只要一組，多顆 MPR121 共用）。Adafruit MPR121 跟黑色通用 MPR121 breakout 板上**通常內建 10 kΩ** pull-up，3 顆並聯變 ~3.3 kΩ，仍在 I²C 規格內，實務上不用外接。若 I²C 不穩，量 SDA→3.3V 的阻值檢查。

---

## 電容觸控相關

### MPR121
NXP 做的 **12-channel capacitive touch sensor IC**。特色：
- 12 個電極通道，各自獨立偵測
- 10-bit 分辨率（filtered data）
- 自動 baseline tracking（環境電容變化自動校正）
- I²C 介面
- 3.3V 工作電壓（**不能直接接 5V**）

### 電極（Electrode）
任何導電面都可當電極：銅箔、導電漆、金屬片、鋁箔。手指靠近時，電極與手指之間形成電容，MPR121 偵測這個電容變化。

### Touch Threshold / Release Threshold
MPR121 的靈敏度設定。baseline 跟當前讀值的差超過 touch threshold → 判定「按下」；差小於 release threshold → 判定「放開」。Adafruit 預設 12 / 6，可調整。

### Baseline
MPR121 持續追蹤的「沒按」時的電容值。環境溫度、濕度變時 baseline 會漂移，MPR121 自動校正（時間常數約 10 秒）。

### Filtered Data
MPR121 讀到的原始電容值經濾波後的 10-bit 數字（0–1023）。我們用它來做質心演算法（強度權重）。

### Baseline `<< 2` 陷阱 ⚠️
MPR121 的 baseline 暫存器內部是 **8-bit**，filtered data 是 **10-bit**。Adafruit library 的 `baselineData()` 方法**已經把值左移 2 位**還原到 10-bit（見 [Adafruit_MPR121.cpp](https://github.com/adafruit/Adafruit_MPR121/blob/master/Adafruit_MPR121.cpp)）。所以在你的程式碼裡：
```cpp
int delta = (int)cap.baselineData(i) - (int)cap.filteredData(i);  // ✅
int delta = ((int)cap.baselineData(i) << 2) - (int)cap.filteredData(i);  // ❌ 會乘 4 倍
```

### Baseline Delta
`baseline - filtered data`。這才是「手指造成的變化量」，質心演算法用這個當權重。

---

## 演算法相關

### Centroid（質心）
一維位置加權平均。公式：
```
centroid = Σ(positionᵢ × weightᵢ) / Σ(weightᵢ)
```
用來把「幾個離散 pad 的強度」轉成「一個連續位置」。詳見 [05-centroid-algorithm.md](05-centroid-algorithm.md)。

### Vector Sum（向量和）
二維位置加權平均。每個電極視為一個向量（方向 = 它在圓上的角度，長度 = 強度），全部相加得到「平均指向的方向」。用在 Jog Wheel。數學上等同「circular mean」（[Wikipedia](https://en.wikipedia.org/wiki/Circular_mean)）。

### EMA（Exponential Moving Average）
指數移動平均，一種低通濾波器。公式 `ema_new = α × raw + (1 − α) × ema_old`，α 越小越平滑但反應越慢。DJ 用途建議 α = 0.2–0.4。取樣 100 Hz 時 α = 0.3 對應約 5 Hz 截止頻率。

### Noise Threshold
質心演算法裡的「忽略小訊號」閾值。`weight = max(0, delta - noise_threshold)`。建議起點 3–5；誤觸多 → 調高，邊緣 pad 感應不到 → 調低。注意這跟 MPR121 的 touch/release threshold **不同層級**：noise_threshold 是你自己在軟體裡加的二次過濾。

---

## 電氣名詞

### VCC / 3.3V / 5V
電源正極。**Adafruit 版** MPR121 的 `VIN` 接 3.3V 或 5V 都可以（板上有 regulator），`3Vo` 是 regulator 輸出。**黑色通用版**（本專案用）只有 `3.3V` 腳且**沒有 regulator**，只能接 3.3V。**Teensy 4.0 本身是 3.3V 邏輯，絕對不能把 5V 輸入接到 Teensy 的 I/O 腳**，會燒掉。

### GND
接地 / 電源負極。所有裝置必須共用同一個 GND，否則 I²C 不會動。

### I²C Pull-up
見上方「Pull-up 電阻」。

### Breadboard（麵包板）
免焊接的塑膠板，有一格一格的金屬夾可以插元件。本專案的 Teensy + 3×MPR121 先在麵包板上搭，確認都 work 才考慮焊 PCB 或洞洞板。

### Breakout Board（轉接板）
把一顆 surface-mount 小 IC（例如 MPR121 只有 3×3 mm）焊到一塊有 0.1 吋間距排針的小 PCB 上，方便插麵包板用。本專案的 3 顆 MPR121 就是以 breakout 形式使用。

### Decoupling Capacitor（去耦電容）
接在 IC 的 VCC 跟 GND 之間（通常 0.1 µF 陶瓷）。抑制電源噪聲、穩定 IC 運作。選配但推薦。

---

## FlowDJ 專用術語

### Deck
DJ 界的「音軌」，一台 controller 通常有兩個 deck（左右）可以各自播不同歌。本專案先做 **1 個 deck**。

### Jog Wheel（轉盤）
DJ 機正中央的大圓盤。用來：(a) 微調播放速度（pitch bend）(b) 快速搜尋歌曲位置（seek）(c) 刮碟（scratch）。

### CUE
歌曲的「起點記號」。按 CUE 跳到記號位置；長按 CUE 從記號播放。

### SYNC
自動對拍。按下後 FlowDJ 把這個 deck 的 BPM 對齊另一個 deck。

### PAD
演出觸發墊。可以切換模式：HOT CUE（跳到預設點）、FX（觸發效果）、Sampler（觸發取樣音）。
