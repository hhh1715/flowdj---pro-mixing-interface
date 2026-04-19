# 07 — Fritzing 接線圖製作手冊

除了文字 + SVG 的接線說明外，這份手冊讓你用 Fritzing 生出一張「麵包板照相機風格」的接線圖，放到 repo 當作正式示意圖。

你的 Fritzing AppImage 位置：
```
/home/wise/Downloads/fritzing-1.0.6-l2239-04e5bb02-qt6.AppImage
```

本手冊預計花費 **20–30 分鐘**完成（第一次用 Fritzing）。

> ⚠️ **Fritzing 1.0+ 官方版本需要付費下載**（約 €8 一次性贊助）。如果不想付費，跳到文末「替代方案」章節。

---

## 準備工作（只做一次）

### 1. 啟動 Fritzing

第一次要給它執行權限：
```bash
chmod +x ~/Downloads/fritzing-1.0.6-l2239-04e5bb02-qt6.AppImage
~/Downloads/fritzing-1.0.6-l2239-04e5bb02-qt6.AppImage
```

或在檔案總管雙擊 AppImage。

### 2. 下載 Teensy 4.0 零件（Fritzing 內建沒有）

⚠️ 截至 2026 年，**沒有官方或廣泛維護的 Teensy 4.0 Fritzing 零件**。取得方式（依靠譜度排序）：

1. **PJRC 官方論壇零件分享串**：
   - https://forum.pjrc.com/ 搜尋「Teensy 4.0 fritzing」
   - 社群常有人貼自己做的 `.fzpz` 檔
2. **Fritzing 官方 Parts Submissions 論壇**：
   - https://forum.fritzing.org/c/parts-submit
3. **自己做**：用 Fritzing 的 Parts Editor 從「Generic 14×2 DIP」改，花 30 分鐘。參考：https://fritzing.org/learning/tutorials/creating-custom-parts
4. **用近似零件**：「Generic 14×2 DIP」或「Arduino Pro Mini」代替，在零件屬性對話框自己標 pin（Fritzing 支援 rename pin）

匯入方式：Fritzing → **File → Open** → 選擇 `.fzpz` 檔，Fritzing 會把它加進「Mine」分類（右下角零件櫃）。

### 3. MPR121 零件

⚠️ **Fritzing 內建零件庫沒有 MPR121**（許多教學寫的是舊版 Fritzing，或根本錯）。取得方式：
- **Adafruit Fritzing Library**（官方社群最齊）：https://github.com/adafruit/Fritzing-Library
  - Clone 下來，找 `parts/Adafruit MPR121 12-Key Capacitive Touch Sensor Breakout.fzpz`
  - 在 Fritzing 中 File → Open 匯入
- 或 Bare Conductive 的 `.fzpz`（他們的 Touch Board 基於 MPR121）

外觀是藍色 PCB，你實際用的是黑色，但**腳位功能一樣**，不影響示意圖目的。

---

## 繪製流程（一步一步）

### Step 1：新建 sketch

Fritzing 開啟後：
- **File → New**
- 切到 **Breadboard View** 頁籤（應該是預設）

### Step 2：放置麵包板

- 右下角零件庫 → 搜尋 `Breadboard` → 拖曳一塊 **Full-Size Breadboard** 到畫布
- （Fritzing 沒有 EIC-104 這種四區麵包板的內建款，用一塊標準 830 點的代替即可；概念一樣）

### Step 3：放置 Teensy 4.0

- 從「Mine」或你剛匯入的 Teensy 零件拖進畫布
- 把 Teensy 跨置麵包板中央溝槽上（**Micro-B USB 端朝左**，不是 USB-C）
- 讓左排 Pin 位於麵包板**左半邊的 E 列**，右排在 **F 列**

### Step 4：放置 3 顆 MPR121

- 搜尋 `MPR121` → 拖出三顆
- 依序放在 Teensy 右方，間隔 ~10 格一顆
- 一樣跨溝槽

### Step 5：拉電源線（紅黑）

- **紅線**（3.3V）：點 Teensy 的 `3.3V` pin → 拉到麵包板上方 `+` rail（整條紅 rail）
- **黑線**（GND）：點 Teensy 的 `GND` pin → 拉到麵包板 `-` rail
- 每顆 MPR121 的 `3.3V` → 紅 rail；`GND` → 黑 rail
- **點線中段**可以拉斜角，Fritzing 會自動 round 成 45°/90°

**訣竅**：在 View → Routing → Auto Route 可自動整理線條，但手動通常比較好看。

### Step 6：拉 I²C 線（藍黃）

建議用顏色區分（要跟 repo 內 `wiring-diagram.svg` 一致）：
- **藍線** = SDA
- **橘線** = SCL（不要用黃色，會跟正電源線混淆）

在 Fritzing 要改顏色：右鍵點線 → `Color` → 選顏色。

連線：
- Teensy `Pin 18` → MPR121 #1 `SDA` → MPR121 #2 `SDA` → MPR121 #3 `SDA`（菊花鏈）
- Teensy `Pin 19` → MPR121 #1 `SCL` → #2 `SCL` → #3 `SCL`

### Step 7：拉 ADD 位址線（綠）

用第三個顏色（綠色虛線或綠色）表示：
- MPR121 #1 `ADD` → **GND rail**（位址 0x5A）
- MPR121 #2 `ADD` → **3.3V rail**（位址 0x5B）
- MPR121 #3 `ADD` → **連到 SDA 線上任一節點**（位址 0x5C）

💡 **在 Fritzing 把一條線接到另一條線中段：** 右鍵點目標線 → `Add Bendpoint`，然後從 `ADD` 腳拉新線到那個 bendpoint。

### Step 8：加電極（用杜邦線代表）

每顆 MPR121 的 E0–E11 不必全部拉滿，示意即可：
- MPR121 #1：拉 3 條藍線出去（CUE、Play、SYNC 按鈕示意）+ 8 條橘線（Jog 環）
- MPR121 #2：拉 10 條紅線（Tempo slider 10 個電極）
- MPR121 #3：拉 4 條黃線（PAD）+ 5 條紫線（Volume fader）

線尾可以用 Fritzing 的 `Generic single-in-line header` 代表「這裡接到電極」。

### Step 9：加註解

右鍵 → `Add Part Note`（或選 Sketch → Add Note），標註：
- 「USB-C to PC」（在 Teensy 上方）
- 「I²C 0x5A」、「0x5B」、「0x5C」（每顆 MPR121 標示）
- 「Electrodes to conductive ink / copper tape」（在電極線尾）

### Step 10：匯出

- **File → Export → Image → PNG**
- 存到 `docs/hardware/images/wiring-diagram-fritzing.png`
- 解析度建議 300 DPI 以上（Fritzing 預設夠）

也可以同時存 `.fzz` 原始檔（Fritzing 的正確副檔名是 **`.fzz`**，不是 `.fz`）到 `docs/hardware/wiring.fzz`，未來要改時直接打開。

---

## 校對清單

匯出前確認：
- [ ] Teensy 3.3V / GND 有接到 rail
- [ ] 3 顆 MPR121 的 3.3V / GND / SDA / SCL 全部連上
- [ ] 3 顆 ADD 腳接到三個**不同**位置（GND / 3.3V / SDA）
- [ ] 沒有**紅線碰到黑線**這種明顯錯誤
- [ ] 零件都有文字標示

---

## 整合到專案

完成後把圖片加進 [03-wiring.md](03-wiring.md)：

```markdown
## Fritzing 接線示意圖

![Fritzing wiring diagram](images/wiring-diagram-fritzing.png)
```

並在 [README.md](README.md) 的圖片清單加一行：

```markdown
| `images/wiring-diagram-fritzing.png` | Fritzing 風格麵包板接線圖 |
| `wiring.fzz` | Fritzing 原始檔 |
```

---

## 如果 Fritzing 開不起來

AppImage 有時在某些 Linux 發行版會缺 library，錯誤訊息通常會指出缺哪個。常見：
```
error while loading shared libraries: libxcb-xinerama.so.0
```

解法（Ubuntu/Debian）：
```bash
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0
```

若還是跑不起來，**直接用 `images/wiring-diagram.svg`** 當接線圖（在 GitHub 上一樣好看）。

---

## 替代方案（不想付費買 Fritzing）

Fritzing 1.0+ 官方版本需要付費下載。免費替代：

### 1. [Wokwi](https://wokwi.com/)（推薦）
- 線上工具，免費
- 有 Arduino/ESP32/Raspberry Pi Pico 模擬器
- 沒有原生 Teensy 4.0，但有 Arduino Mega / Uno 可以代替畫示意圖
- 匯出 PNG 很乾淨

### 2. [KiCad](https://www.kicad.org/)（完全免費開源）
- 業界標準 EDA 工具
- 學習曲線比 Fritzing 陡，但做得出專業 schematic
- 有 Teensy 4.0 符號（社群庫）

### 3. [CircuitLab](https://www.circuitlab.com/)（免費版可用）
- 瀏覽器內，無需安裝
- 不畫麵包板，只畫 schematic（對本專案其實更清楚）

### 4. 直接用現有的 SVG
本 repo 已有 [images/wiring-diagram.svg](images/wiring-diagram.svg)，繪製所有接線。GitHub 能直接渲染。Fritzing 的「麵包板照相機風格」只是美術加分，不是必需。

---

## 參考資料

- [Fritzing 官網](https://fritzing.org/)
- [Fritzing 教學影片](https://fritzing.org/learning/)
- [Adafruit Fritzing Library（含 MPR121 零件）](https://github.com/adafruit/Fritzing-Library)
- [Fritzing 自製零件教學](https://fritzing.org/learning/tutorials/creating-custom-parts)
- [PJRC 論壇（找 Teensy 社群零件）](https://forum.pjrc.com/)
- [Fritzing Parts Submissions 論壇](https://forum.fritzing.org/c/parts-submit)
