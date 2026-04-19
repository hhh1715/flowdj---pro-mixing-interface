# FlowDJ 部署與開發手冊

本手冊記錄如何在本機安裝、執行、以及後續與實體板子整合的步驟。

---

## 一、專案簡介

FlowDJ 是一個 Pro Mixing Interface,技術堆疊:

- **前端框架:** React 19 + TypeScript
- **建置工具:** Vite 6
- **UI:** Tailwind CSS 4 + lucide-react + motion
- **AI:** Google Gemini API (`@google/genai`)
- **後端(預留):** Express

---

## 二、環境需求

| 工具 | 版本 |
|------|------|
| Node.js | 18+ (建議 20 以上) |
| npm | 隨 Node 附帶 |
| git | 任意版本 |

確認版本:
```bash
node -v
npm -v
git --version
```

---

## 三、首次安裝步驟

### 1. Clone 專案

```bash
cd ~/Desktop/DJ
git clone https://github.com/hhh1715/flowdj---pro-mixing-interface.git
cd flowdj---pro-mixing-interface
```

### 2. 安裝依賴

```bash
npm install
```

### 3. 設定 Gemini API Key

先到 https://aistudio.google.com/apikey 用 Google 帳號登入,按 **Create API key** 產生一組金鑰並複製。

在專案根目錄建立 `.env.local`:

```bash
echo 'GEMINI_API_KEY="你的API_KEY"' > .env.local
```

> `.env.local` 已被 `.gitignore` 排除,不會推上 GitHub,安全。
> 金鑰千萬不要貼在程式碼或 README 裡。

### 4. 啟動開發伺服器

```bash
npm run dev
```

開啟瀏覽器 → **http://localhost:3000**

---

## 四、常用指令

| 指令 | 作用 |
|------|------|
| `npm run dev` | 啟動開發伺服器 (port 3000) |
| `npm run build` | 建置正式版到 `dist/` |
| `npm run preview` | 預覽 build 結果 |
| `npm run lint` | TypeScript 型別檢查 |
| `npm run clean` | 清除 `dist/` |

---

## 五、專案結構

```
flowdj---pro-mixing-interface/
├── src/
│   ├── main.tsx        # 進入點
│   ├── App.tsx         # 主要元件
│   ├── types.ts        # 型別定義
│   └── index.css       # 全域樣式 (Tailwind)
├── index.html          # HTML 樣板
├── vite.config.ts      # Vite 設定
├── tsconfig.json       # TS 設定
├── package.json        # 依賴與 scripts
├── .env.example        # 環境變數範本
├── .env.local          # 你的本機金鑰(不上傳)
└── SETUP.md            # 本手冊
```

---

## 六、Git 日常操作

```bash
# 看狀態
git status

# 建立新分支開發
git checkout -b feature/硬體整合

# 提交
git add .
git commit -m "描述這次改了什麼"

# 推到 GitHub
git push origin feature/硬體整合
```

---

## 七、後續:與實體板子整合(預留)

後續要讓 FlowDJ 介面控制實體 DJ 板子,常見做法:

### Web 端可選方案

- **Web MIDI API** — 瀏覽器直接讀取 MIDI 訊號(最簡單,不需後端)
- **Web Serial API** — 瀏覽器直接與 USB 序列埠通訊(適合 Arduino/ESP32)
- **WebSocket + Node 後端** — 板子連到本機後端,再由後端轉發到前端(複雜但彈性最大)

### 硬體端常見選擇

- Arduino / Teensy(Teensy 原生支援 USB MIDI,最推薦)
- ESP32(無線,可走 WebSocket)
- Raspberry Pi Pico(便宜,USB HID/MIDI)

### 整合規畫建議

1. 先決定板子與電腦的通訊協定(MIDI / Serial / WebSocket)
2. 在 `src/` 下新增一個資料夾,例如 `src/hardware/`,封裝裝置連線邏輯
3. 用 React context 或 zustand 管理硬體狀態(按鍵、推桿、旋鈕數值)
4. 前端 UI 元件訂閱硬體狀態來反應動作

> 這一段等實際拿到板子規格後,再補實作細節到本手冊。

---

## 八、疑難排解

**問題:`npm install` 失敗**
→ 刪掉 `node_modules/` 和 `package-lock.json` 後重跑。
```bash
rm -rf node_modules package-lock.json
npm install
```

**問題:API 沒反應 / 401 錯誤**
→ 檢查 `.env.local` 的 `GEMINI_API_KEY` 是否正確。改完要重啟 `npm run dev`。

**問題:port 3000 被占用**
→ 編輯 `package.json` 的 `dev` 指令,把 `--port=3000` 改成別的數字。

**問題:想重新 clone 一份**
→ 先把目前資料夾內有用的東西備份,再刪掉重新 clone。

---

## 九、聯絡 / 備註

- 原始專案: https://github.com/guiguiiii/flowdj---pro-mixing-interface
- 本人 fork: https://github.com/hhh1715/flowdj---pro-mixing-interface
- AI Studio 應用頁: https://ai.studio/apps/47137c02-409d-46f6-849b-1b0e30ccee3e
