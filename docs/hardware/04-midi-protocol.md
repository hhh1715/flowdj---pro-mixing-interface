# 04 — MIDI 訊息對照表

這章定義 Teensy 端韌體送出的所有 MIDI 訊息，也是 FlowDJ Web UI 端要解讀的格式。

## 通則

- **MIDI Channel**：1（程式碼裡是 0，human-readable 是 1）
- **單 deck 模式**：所有訊息都在 Channel 1。未來做 2 個 deck 時，deck 2 用 Channel 2。
- **Note On velocity 慣例**：
  - 按下 → `Note On, velocity = 127`
  - 放開 → `Note Off`（或 `Note On, velocity = 0`，效果一樣）

---

## 完整訊息表

### 按鈕類（Note On/Off）

| 元件 | Note Number | Note 名稱 | 備註 |
|---|---|---|---|
| CUE | 36 | C2 | DJ 慣例起點 |
| Play/Pause | 37 | C#2 | |
| SYNC | 38 | D2 | |
| (保留) | 39 | D#2 | 未來擴充 |
| PAD 1 | 40 | E2 | HOT CUE mode 時觸發 cue point 1 |
| PAD 2 | 41 | F2 | cue point 2 |
| PAD 3 | 42 | F#2 | cue point 3 |
| PAD 4 | 43 | G2 | cue point 4 |
| Jog 觸摸偵測 | 48 | C3 | 任一 Jog 電極被觸碰 → Note On 127；全部放開 → Note Off |

### 連續控制類（CC = Control Change）

| 元件 | CC Number | 解析度 | 範圍 | 說明 |
|---|---|---|---|---|
| 速度 slider MSB | 14 | 7-bit 高位 | 0–127 | 跟 CC 46 配對成 14-bit |
| 速度 slider LSB | 46 | 7-bit 低位 | 0–127 | `(MSB × 128 + LSB)` = 0–16383 |
| 音量 fader | 7 | 7-bit | 0–127 | 標準 MIDI 主音量 CC |
| Jog 旋轉速度 | 16 | 7-bit（相對） | 1–127 | 64=不動, >64=順時針, <64=逆時針。偏離 64 越遠 = 越快 |

---

## 詳細說明

### 為什麼 Jog 要分「觸摸」跟「旋轉」?

DJ 軟體需要知道兩件事：

1. **手指是否在 Jog 上**（Note 48）→ 決定操作模式：
   - 有碰 = **Scratch 模式**（Jog 當刮碟控制）
   - 沒碰 = **Pitch bend 模式**（Jog 當微調 BPM）
2. **Jog 轉了多快/哪個方向**（CC 16）→ 實際動作量

韌體邏輯：
```
每次讀完 8 個 Jog 電極：
    算出新角度 θ_new
    算出角速度 dθ = θ_new - θ_prev
    若有任一電極強度 > threshold:
        若上次沒碰 → 送 Note On 48
        送 CC 16, value = 64 + scaled(dθ)
    否則:
        若上次有碰 → 送 Note Off 48
        （不送 CC 16）
    θ_prev = θ_new
```

### 為什麼速度要 14-bit，音量不用?

**速度（BPM 微調）：**
- 128 階跨越 ±8% BPM 範圍 → 每階 ~0.08% ≈ 0.1 BPM
- DJ 對拍時對 0.01 BPM 差都聽得出來
- 所以用 14-bit：16384 階跨越 ±8% → 每階 ~0.0008 BPM

**音量：**
- 128 階足夠（人耳對 ~1 dB 差已經明顯，128 階夠細了）
- 用標準 CC 7，跟全世界 MIDI 軟體相容

### 14-bit CC 的送法

送兩個訊息，MSB 要先送（軟體慣例）：
```
MIDI Out:
  [Ch1, CC 14, value_MSB]   ← 高位先送
  [Ch1, CC 46, value_LSB]   ← 低位後送
```

Teensy Arduino 程式碼範例：
```cpp
uint16_t tempo_14bit = 8192; // 中間值
uint8_t msb = (tempo_14bit >> 7) & 0x7F;
uint8_t lsb = tempo_14bit & 0x7F;
usbMIDI.sendControlChange(14, msb, 1); // Ch 1
usbMIDI.sendControlChange(46, lsb, 1);
```

### Jog 相對速度的 2's complement 編碼

CC 16 的值用 **signed 7-bit**（以 64 為零點）：

| CC 16 值 | 含意 |
|---|---|
| 64 | 靜止不動 |
| 65 | 順時針 1 tick |
| 66 | 順時針 2 ticks（更快） |
| 72 | 順時針 8 ticks（快速轉動） |
| 63 | 逆時針 1 tick |
| 62 | 逆時針 2 ticks |
| 1 | 逆時針最快 |
| 127 | 順時針最快 |

Teensy 程式碼：
```cpp
int delta = angle_new - angle_prev; // 可能為負
// 限制在 [-63, +63] 範圍
if (delta > 63) delta = 63;
if (delta < -63) delta = -63;
uint8_t cc_value = 64 + delta;
usbMIDI.sendControlChange(16, cc_value, 1);
```

---

## UI 端解讀（Web MIDI）

參考 `src/hardware/webmidi.ts`（M4 階段會建立）：

```typescript
midiInput.addEventListener('midimessage', (e) => {
  const [status, data1, data2] = e.data;
  const msgType = status & 0xF0;
  const channel = (status & 0x0F) + 1;

  if (msgType === 0x90) {
    // Note On
    handleNoteOn(data1, data2);
  } else if (msgType === 0x80) {
    // Note Off
    handleNoteOff(data1);
  } else if (msgType === 0xB0) {
    // CC
    handleCC(data1, data2);
  }
});
```

MSB/LSB 合併：
```typescript
let tempoMSB = 0, tempoLSB = 0;
function handleCC(cc: number, value: number) {
  if (cc === 14) { tempoMSB = value; updateTempo(); }
  if (cc === 46) { tempoLSB = value; updateTempo(); }
  if (cc === 7)  setVolume(value / 127);
  if (cc === 16) handleJogDelta(value - 64);
}
function updateTempo() {
  const raw = (tempoMSB << 7) | tempoLSB; // 0–16383
  setTempo(raw / 16383);
}
```

---

## 訊息送出頻率（Rate）

- **按鈕**：事件驅動，只在狀態變化（按下/放開）時送
- **速度 / 音量**：只在值變化時送（加一個 deadband，避免雜訊狂送）
- **Jog**：固定頻率（例如 **100 Hz**）送一次，因為要連續刮碟

韌體主迴圈：
```
每 10 ms (100 Hz):
    讀 3 顆 MPR121
    處理按鈕事件 → 有變化才送
    處理 sliders → 有變化才送（變化 > 2 階才送）
    處理 Jog → 每次都送 Note + CC
```

---

## 測試用「小抄」對照表

燒韌體後用 MIDI monitor 驗證，看到的訊息應該是：

| 操作 | 預期看到的 MIDI 訊息 |
|---|---|
| 按 CUE | `[90 24 7F]` (Note On C2 Ch1) |
| 放開 CUE | `[80 24 00]` (Note Off C2 Ch1) |
| 按 Play | `[90 25 7F]` |
| 按 SYNC | `[90 26 7F]` |
| 按 PAD 1 | `[90 28 7F]` |
| 摸 Jog | `[90 30 7F]` (Note On C3) |
| 轉 Jog 順時針 | `[B0 10 46]` (CC 16 val=70 = 64+6 順) |
| 拉 tempo 到頂 | `[B0 0E 7F]` + `[B0 2E 7F]` (MSB=127, LSB=127, 14-bit=16383) |
| 推 volume 到中 | `[B0 07 40]` (CC 7 val=64) |

（訊息格式為 16 進位，3-byte MIDI 標準）
