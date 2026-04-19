# 07 — Fritzing 接線圖製作手冊

除了文字 + SVG 的接線說明外，這份手冊讓你用 Fritzing 生出一張「麵包板照相機風格」的接線圖，放到 repo 當作正式示意圖。

你的 Fritzing AppImage 位置：
```
/home/wise/Downloads/fritzing-1.0.6-l2239-04e5bb02-qt6.AppImage
```

本手冊預計花費 **10 分鐘**完成。

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

Fritzing 內建零件庫沒有 Teensy 4.0，要從 PJRC / 第三方取得。

**推薦：Adafruit 或社群貢獻的 Teensy 4.0 .fzpz 檔**

1. 開瀏覽器到 [github.com/bloomlive/fritzing-teensy](https://github.com/bloomlive/fritzing-teensy) 或 [github.com/MCUdude/MightyCore-Fritzing](https://github.com/MCUdude/MightyCore-Fritzing)（Teensy 系列）
2. 下載 `Teensy_4.0.fzpz`
3. 在 Fritzing 中：**File → Open**，選擇 `.fzpz` 檔，Fritzing 會把它加進「Mine」分類（右下角零件櫃）

**如果找不到現成的 .fzpz**：可以用外觀類似的「Arduino Pro Mini」或「Generic 14×2 DIP」代替，腳位自己標示即可。

### 3. MPR121 零件

Fritzing 內建**有** Adafruit MPR121，直接從零件庫搜尋 `MPR121` 即可。外觀是藍色 PCB，你實際用的是黑色，但**腳位功能一樣**，不影響示意圖目的。

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
- 把 Teensy 跨置麵包板中央溝槽上（USB 那端朝左）
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

建議用顏色區分：
- **藍線** = SDA
- **黃線**（或橘）= SCL

在 Fritzing 要改顏色：右鍵點線 → `Color` → 選顏色。

連線：
- Teensy `Pin 18` → MPR121 #1 `SDA` → MPR121 #2 `SDA` → MPR121 #3 `SDA`（菊花鏈）
- Teensy `Pin 19` → MPR121 #1 `SCL` → #2 `SCL` → #3 `SCL`

### Step 7：拉 ADD 位址線（綠）

用第三個顏色（綠色虛線或綠色）表示：
- MPR121 #1 `ADD` → **GND rail**（位址 0x5A）
- MPR121 #2 `ADD` → **3.3V rail**（位址 0x5B）
- MPR121 #3 `ADD` → **連到 SDA 線上任一節點**（位址 0x5C）

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

也可以同時存 `.fz` 原始檔到 `docs/hardware/wiring.fz`，未來要改時直接打開。

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
| `wiring.fz` | Fritzing 原始檔 |
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

## 參考資料

- [Fritzing 官網](https://fritzing.org/)
- [Fritzing 教學影片（30 分鐘入門）](https://fritzing.org/learning/)
- [Teensy fzpz 零件下載 — bloomlive](https://github.com/bloomlive/fritzing-teensy)
