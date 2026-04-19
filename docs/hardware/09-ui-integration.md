# 09 — 拿到新 UI 後的 MIDI 整合 checklist

> 這份是寫給**未來的你**：當設計系同學把他們用 AI 做出來的新 UI 程式碼交給你、你要把硬體（MIDI）接進去那一刻要看的東西。
>
> 假設此時：
> - 新 UI 已經 merge 進 `src/`（App.tsx 被換掉、或多了一堆新元件）
> - `src/hardware/webmidi.ts` 還在（這份是你自己維護的，**不要被覆蓋**）
> - 實體 Teensy 控制器可能**還沒接好** — 沒關係，先用 mock mode 排演整合邏輯
>
> 目標：**30 分鐘內確認 MIDI 接通，看到按鈕/slider/Jog 能驅動新 UI。**

---

## Step 0 — 接手前先確認三件事

在碰 UI 之前先跑一次，確定專案本身沒壞：

```bash
npm install
npm run lint       # tsc --noEmit，型別 OK 才繼續
npm run dev        # 能開瀏覽器看到畫面 = 前端沒爆
```

三個都過才往下走。若 `npm run lint` 爆 → 可能是新 UI 有 TS 錯誤，先修那邊再談 MIDI。

---

## Step 1 — 確認 hardware 層還在

```bash
ls src/hardware/
# 應該看到 webmidi.ts 至少還在
```

若 `src/hardware/webmidi.ts` **不見了**（被新 UI 不小心蓋掉）：

```bash
git log --all --oneline -- src/hardware/webmidi.ts | head -5
git checkout <commit-id> -- src/hardware/webmidi.ts
```

把它救回來再繼續。

---

## Step 2 — 事件 → UI 操作的對應表

這是你要一邊看新 UI 一邊配對的查表：

| MIDI 事件 | TypeScript shape | 新 UI 要做什麼 |
|---|---|---|
| CUE 按下 | `{ type: 'button', button: 'cue', pressed: true }` | 呼叫新 UI 的 CUE handler |
| CUE 放開 | `{ type: 'button', button: 'cue', pressed: false }` | （通常沒事做，DJ 軟體慣例） |
| Play/Pause | `{ type: 'button', button: 'play', pressed: true }` | toggle 播放狀態 |
| SYNC | `{ type: 'button', button: 'sync', pressed: true }` | 觸發 sync 動作 |
| PAD 1–4 | `{ type: 'button', button: 'pad1' \| 'pad2' \| 'pad3' \| 'pad4', pressed: true }` | 觸發對應 cue point |
| Jog 觸碰狀態 | `{ type: 'button', button: 'jogTouch', pressed: boolean }` | 切換 scratch vs pitch bend 模式 |
| 音量 fader | `{ type: 'volume', value: 0–127, normalized: 0–1 }` | 設主音量（通常吃 `normalized`） |
| 速度 slider | `{ type: 'tempo', value14bit: 0–16383, normalized: 0–1 }` | 設 BPM 調整量（14-bit 精度） |
| Jog 旋轉 | `{ type: 'jogDelta', delta: -63..+63 }` | 正=順時針；scratch 模式乘以靈敏度，pitch bend 模式乘以較小係數 |

> **看懂這張表 = 整合工作完成 60%。** 剩下就是把右欄接到新 UI 的對應函式/state setter。

---

## Step 3 — 最小接法（3–5 行貼上就通）

假設新 UI 的主 component 是 `<PlayerDeck />` 或類似，找到它之後：

```tsx
import { useMidi } from '../hardware/webmidi';
// 路徑依新 UI 放在哪調整

export function PlayerDeck() {
  // 你原本的新 UI code
  const [playing, setPlaying] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [tempo, setTempo] = useState(0.5);

  // ↓↓↓ 加這一段，其他 UI code 不動 ↓↓↓
  useMidi({
    onEvent: (e) => {
      if (e.type === 'button' && e.button === 'play' && e.pressed) {
        setPlaying(p => !p);
      }
      if (e.type === 'volume')  setVolume(e.normalized);
      if (e.type === 'tempo')   setTempo(e.normalized);
      // ... 其他事件依表補
    },
  });
  // ↑↑↑ 就這樣 ↑↑↑

  return <div>...新 UI 原樣...</div>;
}
```

**重點：** 用 `onEvent` 回呼**不要**用 `lastEvent` 進 useEffect 比較，因為 Jog 100 Hz 會累死 effect。

---

## Step 4 — 沒有實體控制器也能測（Mock Mode）

若此時 Teensy 還沒接好，先用 mock 模式驗整合邏輯：

```tsx
const { emit } = useMidi({ mock: true });

// 在開發工具 console 按鈕或 setTimeout 內叫：
emit({ type: 'button', button: 'play', pressed: true });
emit({ type: 'volume', value: 100, normalized: 100/127 });
emit({ type: 'tempo', value14bit: 8192, normalized: 0.5 });
emit({ type: 'jogDelta', delta: 5 });
```

mock 模式下：
- 不會呼叫 `navigator.requestMIDIAccess()`（所以不會跳權限要求）
- `status` 會立刻變 `'ready'`
- `inputNames` 會是 `['(mock)']`
- 手動 `emit()` 會觸發跟真硬體完全一樣的 `onEvent` / state 更新

邏輯接好 + mock 測過 → 實體控制器一到就能直接把 `mock: true` 拿掉。

---

## Step 5 — 接實體硬體

1. 拔掉 `{ mock: true }`，改回 `useMidi({ onEvent: ... })`
2. Teensy 用 Micro-B USB 接電腦
3. 瀏覽器開頁面 → 跳「允許使用 MIDI 裝置」→ **允許**
4. 動一下控制器 → 新 UI 應該要有反應

**沒反應時查 3 件事：**
- 瀏覽器是否 Chrome / Edge / Firefox 134+（Safari 永遠不通）
- 網址列左邊鎖頭 → 網站設定 → MIDI → 是否為「允許」
- `useMidi()` 回傳的 `status` / `error` / `inputNames` 印出來看（可暫時塞進 `<pre>{JSON.stringify(...)}</pre>`，整合完再拿掉）

---

## Step 6 — 驗收 TL;DR

新 UI 接完 MIDI 後，用實體控制器逐項驗：

- [ ] 按 CUE → 新 UI 的 CUE 反應
- [ ] 按 Play → 新 UI 播放/暫停 toggle
- [ ] 按 SYNC → 新 UI 同步動作
- [ ] 按 PAD 1–4 → 四個 cue points 各自觸發
- [ ] 摸 Jog（不轉）→ 新 UI 顯示「scratch 模式」或類似狀態
- [ ] 放開 Jog → 回到 pitch bend 模式
- [ ] 轉 Jog 順時針/逆時針 → 新 UI 方向正確
- [ ] 推音量 fader → 新 UI 音量條跟著動
- [ ] 拉速度 slider → 新 UI BPM 微調跟著動

---

## 常見坑（踩過才知道）

### 坑 1：新 UI 有自己的 state management（zustand / context / redux）

不是用 `useState` 的話，在 `onEvent` 裡直接呼對應的 action：

```tsx
// zustand
const play = usePlayerStore(s => s.play);
useMidi({
  onEvent: (e) => {
    if (e.type === 'button' && e.button === 'play' && e.pressed) play();
  },
});
```

### 坑 2：Jog 事件太頻繁（100 Hz）讓 React 卡

- 不要把 `lastEvent` 當 useEffect 的 dep（會重渲染 100 次/秒）
- 一律用 `onEvent` 回呼
- Jog 的 delta 可在回呼裡累積，用 `requestAnimationFrame` 或節流把更新降到 60 Hz 以下再 setState

### 坑 3：hook 被放在**條件式 render 內**，觸發 hook 規則錯誤

```tsx
{isEnabled && <Something />}  // ❌ 如果 Something 裡面呼 useMidi，會違反 hook 規則
```

`useMidi()` 要放在**永遠會執行**的 component 裡。通常是根 component。

### 坑 4：新 UI 自己也在搶 MIDI access

若新 UI 的 AI 生成碼裡不小心也呼了 `navigator.requestMIDIAccess()`，兩邊會打架。搜一下：

```bash
grep -r "requestMIDIAccess" src/
```

只能留 `src/hardware/webmidi.ts` 裡那一個。其他地方呼的刪掉。

### 坑 5：Safari 使用者一進來就白畫面

`useMidi()` 在 Safari 會回 `status: 'unsupported'`。新 UI 要處理這個狀態：

```tsx
const { status } = useMidi();
if (status === 'unsupported') return <div>請改用 Chrome / Edge / Firefox</div>;
```

---

## 附：事件型別完整定義（copy-paste 參考）

```typescript
// 從 webmidi.ts export：
export type FlowDjButton =
  | 'cue' | 'play' | 'sync' | 'pad1' | 'pad2' | 'pad3' | 'pad4' | 'jogTouch';

export type FlowDjEvent =
  | { type: 'button';   button: FlowDjButton; pressed: boolean }
  | { type: 'tempo';    value14bit: number;   normalized: number } // 0–16383, 0–1
  | { type: 'volume';   value: number;        normalized: number } // 0–127, 0–1
  | { type: 'jogDelta'; delta: number };                            // -63 … +63
```

---

## 相關文件

- [04-midi-protocol.md](04-midi-protocol.md) — MIDI 訊息完整對照（你要改事件型別時看這份）
- `src/hardware/webmidi.ts` — 實作本體
- `src/hardware/MidiMonitor.tsx` — 舊 UI 時期的除錯元件，新 UI 可能已被刪掉。若要保留，直接 `<MidiMonitor />` 放在 App 根即可
- [06-testing-plan.md](06-testing-plan.md) — 若 MIDI 完全不通，回去 hardware 那邊從 Phase 1 重驗
