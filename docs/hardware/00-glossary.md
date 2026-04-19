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

### 14-bit CC
標準 CC 只有 128 階，對 BPM、pitch 不夠細。把兩個 CC 組合起來（MSB + LSB）可達到 16384 階。
慣例：CCn 是高位（MSB），CCn+32 是低位（LSB）。例如 CC14（MSB）+ CC46（LSB）配對。

### MSB / LSB
- **MSB** = Most Significant Byte（高位）
- **LSB** = Least Significant Byte（低位）
- 14-bit 值 = MSB × 128 + LSB

### Channel（MIDI 頻道）
MIDI 有 16 個頻道（1–16，程式裡通常寫 0–15）。一般單一 deck 用 Channel 1；未來若做兩個 deck，deck 2 用 Channel 2。

---

## I²C 相關

### I²C（I-Squared-C / I2C）
**Inter-Integrated Circuit**，主從式同步串列通訊協定。只要 **兩條線** 就能接多個裝置：
- **SDA**：Serial Data（資料線）
- **SCL**：Serial Clock（時脈線）

MPR121 走 I²C，Teensy 當 master，每顆 MPR121 是 slave。

### I²C 位址（Address）
每個 slave 裝置有獨一無二的 7-bit 位址。Teensy 呼叫某個位址時，只有那顆裝置會回應。MPR121 的 `ADDR` 腳決定它用 4 個位址裡的哪一個：

| ADDR 接到 | 位址 |
|---|---|
| GND | 0x5A |
| VCC | 0x5B |
| SDA | 0x5C |
| SCL | 0x5D |

### Pull-up 電阻
I²C 線平常應維持在高電位（HIGH），由 pull-up 電阻把線拉高；裝置要送 0 時才主動把線拉低。**SDA 和 SCL 各需要一顆 4.7 kΩ 電阻接到 3.3V**（只要一組，多顆 MPR121 共用）。Adafruit MPR121 breakout 板上**已經內建** pull-up，所以實務上可能不用外接，但若 I²C 不穩要檢查。

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
MPR121 持續追蹤的「沒按」時的電容值。環境溫度、濕度變時 baseline 會漂移，MPR121 自動校正。

### Filtered Data
MPR121 讀到的原始電容值經濾波後的 10-bit 數字（0–1023）。我們用它來做質心演算法（強度權重）。

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
二維位置加權平均。每個電極視為一個向量（方向 = 它在圓上的角度，長度 = 強度），全部相加得到「平均指向的方向」。用在 Jog Wheel。

---

## 電氣名詞

### VCC / 3.3V / 5V
電源正極。MPR121 的 `VIN` 接 3.3V 或 5V 都可以（板上有 regulator），`3Vo` 是 regulator 輸出的 3.3V（可輸出給其他裝置用）。**Teensy 4.0 本身是 3.3V 邏輯，絕對不能把 5V 輸入接到 Teensy 的 I/O 腳**，會燒掉。

### GND
接地 / 電源負極。所有共用同一個 GND，否則 I²C 不會動。

### I²C Pull-up
見上方「Pull-up 電阻」。

### Breadboard（麵包板）
免焊接的塑膠板，有一格一格的金屬夾可以插元件。本專案的 Teensy + 3×MPR121 先在麵包板上搭，確認都 work 才考慮焊 PCB 或洞洞板。

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
