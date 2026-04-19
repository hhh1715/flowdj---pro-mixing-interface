# FlowDJ 部署手冊（給完全沒寫過程式的使用者）

> 這份手冊是寫給**設計系同學**的。假設你：
>
> - 沒寫過程式、沒用過終端機 / 命令提示字元
> - 想在自己的電腦（Mac 或 Windows）把 FlowDJ 跑起來
> - 想把已經組好的 Teensy 控制器接上來用
>
> 我們會一個步驟一張圖、一句話解釋，慢慢帶你走完。
> 若某步卡住，先不要亂點，直接跳到最後的 [疑難排解](#九疑難排解)。

---

## 目錄

1. [要準備什麼](#一要準備什麼)
2. [第一次設定 Mac](#二第一次設定mac使用者)
3. [第一次設定 Windows](#三第一次設定windows-使用者)
4. [下載 FlowDJ 程式](#四下載-flowdj-程式)
5. [取得 Gemini AI 金鑰](#五取得-gemini-ai-金鑰)
6. [第一次啟動](#六第一次啟動)
7. [接上 Teensy 控制器](#七接上-teensy-控制器)
8. [之後每次要用怎麼開](#八之後每次要用怎麼開)
9. [疑難排解](#九疑難排解)
10. [名詞翻譯對照](#十名詞翻譯對照)

---

## 一、要準備什麼

### 硬體

- **筆電 / 桌電**（Mac 或 Windows 都可以）
- 網路（第一次要下載東西）
- **組裝好的 Teensy 控制器**（由電路組同學交給你，含 Micro-B USB 線）
- **Chrome** 或 **Edge** 或 **Firefox 134 以上** 瀏覽器 — ⚠️ **Safari 不能用**

### 心理準備

- 第一次全部做完大約 **30–45 分鐘**
- 會下載：Node.js（約 60 MB）、程式本體（約 100 MB）、第一次裝套件（約 400 MB）
- 需要你自己申請一個免費的 Google Gemini API 金鑰（步驟會帶）

---

## 二、第一次設定（Mac 使用者）

### 2.1 打開「終端機」

Mac 裡面有個 App 叫「終端機」（Terminal）。兩種方法打開：

- 按 `Cmd + 空白鍵` → 輸入 `終端機` → Enter
- 或：Finder → 應用程式 → 工具程式 → 終端機

打開後會看到一個黑黑白白的文字視窗 — 這就是你以後執行指令的地方。

### 2.2 確認有沒有 Node.js

在終端機**複製貼上**這行然後按 Enter：

```bash
node -v
```

- 若看到 `v20.x.x` 或 `v22.x.x` 之類的數字 → ✅ 已經有，跳到下一節 [第四節](#四下載-flowdj-程式)。
- 若看到 `command not found: node` → 沒裝，繼續下面。

### 2.3 安裝 Node.js（Mac）

**最簡單的方法：官方安裝包**

1. 瀏覽器打開 https://nodejs.org/zh-tw
2. 點首頁的「**LTS**」（Long Term Support，穩定版）那顆綠色按鈕
3. 下載 `.pkg` 檔（檔名類似 `node-v20.xx.x.pkg`）
4. 雙擊打開 → 一路按「繼續」→ 需要輸入 Mac 密碼 → 完成
5. **關掉終端機**再重新打開（讓新安裝生效）
6. 重跑 `node -v`，現在應該看得到版本號了

### 2.4 確認有沒有 git

```bash
git --version
```

- 看到 `git version 2.x.x` → ✅
- 若跳出「安裝命令列開發工具？」的視窗 → 點**安裝**，等 5–10 分鐘完成

---

## 三、第一次設定（Windows 使用者）

### 3.1 打開「命令提示字元」或「PowerShell」

兩種都可以：

- 按 `Win` 鍵 → 輸入 `cmd` → Enter（這是命令提示字元）
- 或：按 `Win` 鍵 → 輸入 `powershell` → Enter

本手冊所有指令在兩個裡面都能跑。

### 3.2 確認有沒有 Node.js

```bash
node -v
```

- 若看到 `v20.x.x` 或 `v22.x.x` → ✅ 跳到 [第四節](#四下載-flowdj-程式)
- 若看到紅字「不是內部或外部命令」→ 沒裝，繼續下面

### 3.3 安裝 Node.js（Windows）

1. 瀏覽器打開 https://nodejs.org/zh-tw
2. 點「**LTS**」綠色按鈕
3. 下載 `.msi` 檔（檔名類似 `node-v20.xx.x-x64.msi`）
4. 雙擊打開 → 勾選「**Automatically install the necessary tools**」那一項 → 下一步 → 安裝
5. **關掉**命令提示字元視窗，再重新打開
6. 重跑 `node -v`，應該看得到版本號

### 3.4 安裝 git

1. 瀏覽器打開 https://git-scm.com/download/win
2. 下載「**64-bit Git for Windows Setup**」
3. 一路按「Next」→ 裝完
4. **關掉**命令提示字元，重開 → 跑 `git --version`，看得到版本 = 成功

---

## 四、下載 FlowDJ 程式

你有**兩種方式**，選一種就好：

### 方式 A：用 git clone（推薦，以後更新容易）

終端機 / 命令提示字元切換到你想放專案的地方（以 Desktop 為例）：

**Mac：**
```bash
cd ~/Desktop
git clone https://github.com/hhh1715/flowdj---pro-mixing-interface.git
cd flowdj---pro-mixing-interface
```

**Windows：**
```bash
cd %USERPROFILE%\Desktop
git clone https://github.com/hhh1715/flowdj---pro-mixing-interface.git
cd flowdj---pro-mixing-interface
```

### 方式 B：直接下載 ZIP（更簡單但以後要手動更新）

1. 瀏覽器打開 https://github.com/hhh1715/flowdj---pro-mixing-interface
2. 點綠色「**Code**」按鈕 → 點「**Download ZIP**」
3. 把下載的 ZIP 放到桌面，**解壓縮**
4. 資料夾名稱通常是 `flowdj---pro-mixing-interface-main`，**改名成** `flowdj---pro-mixing-interface`（把尾巴的 `-main` 刪掉）
5. 終端機切過去：
   - Mac: `cd ~/Desktop/flowdj---pro-mixing-interface`
   - Windows: `cd %USERPROFILE%\Desktop\flowdj---pro-mixing-interface`

### 確認切到正確資料夾

跑這行，應該看到一堆檔案包含 `package.json`：

**Mac：** `ls`
**Windows：** `dir`

---

## 五、取得 Gemini AI 金鑰

FlowDJ 裡的 AI 功能（歌單建議等）用的是 Google 的 Gemini。**免費就能申請**。

1. 瀏覽器打開 https://aistudio.google.com/apikey
2. 用你的 **Google 帳號** 登入
3. 點「**Create API key**」→「**Create API key in new project**」
4. 會跳出一串長長的金鑰，類似 `AIzaSyABC...XYZ`
5. 點右邊的複製按鈕 → **保留著，下一步要用**

⚠️ 這串金鑰等於你的密碼。**不要貼到 Line/Discord/公開文件**，不要把它提交到 GitHub。

### 把金鑰存到專案

在專案根目錄（剛才 `cd` 進去的那個資料夾）建立一個檔案叫 `.env.local`，內容只有一行：

```
GEMINI_API_KEY="你剛才複製的那一串金鑰"
```

**Mac 方便做法：**
```bash
echo 'GEMINI_API_KEY="貼你的金鑰在這"' > .env.local
```

**Windows 方便做法（PowerShell）：**
```powershell
'GEMINI_API_KEY="貼你的金鑰在這"' | Out-File -Encoding utf8 .env.local
```

**Windows（命令提示字元）：** 用「記事本」建立：
1. `notepad .env.local`
2. 跳出「找不到檔案，要建立嗎？」→ 是
3. 貼一行 `GEMINI_API_KEY="貼你的金鑰在這"` → 儲存 → 關掉

---

## 六、第一次啟動

### 6.1 安裝套件（這步要等 3–5 分鐘）

確認你還在專案資料夾，然後跑：

```bash
npm install
```

- 跑的時候會刷出很多行，最後出現 `added xxx packages` 就是成功。
- 過程中若跳黃字 warning 不用管它。
- 跑完後資料夾裡會多一個 `node_modules`（大約 400 MB，正常）。

### 6.2 啟動開發伺服器

```bash
npm run dev
```

你應該看到類似這樣：

```
  VITE v6.x.x  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### 6.3 用瀏覽器打開

用 **Chrome** 或 **Edge** 或 **Firefox 134+** 打開：

**http://localhost:3000**

⚠️ **不要用 Safari**（Safari 不支援我們用的 Web MIDI API，之後接控制器會失敗）。

看到 FlowDJ 的 UI → ✅ 到這一步就算成功啟動了（不需要接控制器也能看）！

### 6.4 想停下來怎麼辦？

回到終端機視窗，按 `Ctrl + C`。

---

## 七、接上 Teensy 控制器

### 7.1 物理連接

1. Teensy 控制器用 **Micro-B USB 線**接到你的電腦
2. Teensy 板子上的小紅 LED 會亮（代表有供電）
3. 第一次接 Windows 會自動裝驅動（等 30 秒），不用你做什麼

### 7.2 讓瀏覽器讀到 MIDI

FlowDJ 會自動跳一個提示視窗問：

> `localhost:3000 想要使用你的 MIDI 裝置`

**點「允許 / Allow」**。
（Chrome 會在網址列左邊顯示一個「MIDI」圖示，之後每次都會記住。）

### 7.3 驗證控制器連上了

FlowDJ 畫面右下角有一個小小的「MIDI Monitor」視窗，會顯示：

- **Status：ready**
- **Inputs：Teensy MIDI**（或類似的名字）
- 你手指碰 Jog / 按按鈕時，**Last raw event** 欄位會一直變
- 下方的「Event log」會滾動訊息

看到訊息 = ✅ 全部成功！可以玩了。

### 7.4 沒看到訊息怎麼辦？

常見原因（依順序檢查）：

1. **瀏覽器不是 Chrome/Edge/Firefox 134+** → 換瀏覽器
2. **第一次拒絕了 MIDI 權限** → 網址列左邊的鎖頭圖示 → 網站設定 → MIDI → 允許 → 重新整理頁面
3. **Teensy USB 沒插好** → 拔插一次（紅 LED 會亮）
4. **Teensy 韌體沒燒** → 找電路組同學確認韌體有燒進 Teensy 4.0

---

## 八、之後每次要用怎麼開

最快流程（熟了之後 10 秒搞定）：

1. 開終端機 / 命令提示字元
2. 切到專案資料夾：
   - Mac: `cd ~/Desktop/flowdj---pro-mixing-interface`
   - Windows: `cd %USERPROFILE%\Desktop\flowdj---pro-mixing-interface`
3. `npm run dev`
4. 瀏覽器開 http://localhost:3000
5. 用完按 `Ctrl + C` 結束

---

## 九、疑難排解

### Q1：`npm install` 卡很久 / 失敗

- 先確認網路通暢。
- 若出現「EACCES」「權限」類錯誤（Mac），**不要加 `sudo`**，改跑：
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```
- 公司/學校網路若擋 npm，換 5G 熱點再試。

### Q2：`npm run dev` 跳「port 3000 is already in use」

代表你已經有另一個視窗在跑 FlowDJ，或別的 app 佔了 3000 port。

- **最簡單做法：** 關掉其他開著的終端機視窗，重跑。
- 還是不行 → 編輯 `package.json`，把 `"dev": "vite --port=3000 ..."` 的 `3000` 改成 `3001`。

### Q3：瀏覽器打開是白畫面 / 錯誤訊息

- 按 `F12` 打開開發者工具，看「Console」紅字。
- 最常見：沒裝 Gemini API key → 第五節重做。
- 或按 `Ctrl+Shift+R`（Mac: `Cmd+Shift+R`）強制重新載入。

### Q4：Gemini 沒反應 / 401 錯誤

- `.env.local` 檔的金鑰沒對。金鑰外面一定要有**雙引號**，一行只有一個 `GEMINI_API_KEY="..."`。
- 改完 `.env.local` 要**重啟 `npm run dev`**（`Ctrl+C` 再重跑）才會生效。

### Q5：Safari 打不開 / 沒 MIDI

Safari 不支援 Web MIDI API（2026 年仍然沒支援）。**只能用 Chrome / Edge / Firefox**。

### Q6：Teensy 接上但瀏覽器看不到

依序檢查：

1. 重新整理頁面 → MIDI 權限彈窗再允許一次
2. 拔插 Teensy 重試
3. 用線上 MIDI monitor 確認 OS 看得到 Teensy：
   - https://studiocode.dev/resources/midi-monitor/
   - 看得到 → 問題在 FlowDJ；看不到 → 問題在 Teensy / 韌體

### Q7：我整個搞砸了，想重來

```bash
cd ..
rm -rf flowdj---pro-mixing-interface    # Mac / Linux
rmdir /s flowdj---pro-mixing-interface  # Windows（命令提示字元）
```

再從第四節 clone 一次就好。你的 Gemini 金鑰要重貼。

---

## 十、名詞翻譯對照

第一次看會陌生，寫給自己的備忘：

| 名詞 | 中文 | 簡單解釋 |
|---|---|---|
| Terminal / Command Prompt | 終端機 / 命令提示字元 | 打指令用的黑白文字視窗 |
| Node.js | （不翻） | 讓 JavaScript 能在電腦上跑的引擎 |
| npm | （不翻） | Node.js 的套件管理工具（類似 App Store） |
| Package | 套件 | 別人寫好的功能模組 |
| Repository / Repo | 程式庫 | 一個專案的程式碼集合（GitHub 上面就是） |
| Clone | 複製 | 把 GitHub 上的程式下載到自己電腦 |
| `cd` | 切換目錄 | `cd xxx` = 進到 xxx 這個資料夾 |
| `ls` / `dir` | 列出檔案 | 看目前資料夾裡有什麼 |
| `.env.local` | 本機環境變數檔 | 存你的 API 金鑰的祕密小檔 |
| Web MIDI API | 瀏覽器的 MIDI 介面 | 讓網頁能收 / 送 MIDI 訊號 |
| Teensy | （產品名） | Arduino 的一款微控制器 |

---

## 附錄：給電路組同學的備忘（你可以跳過）

FlowDJ 硬體側的文件：

- [docs/hardware/README.md](../hardware/README.md)：硬體總目錄
- [docs/hardware/06-testing-plan.md](../hardware/06-testing-plan.md)：六階段測試流程
- [docs/hardware/08-prototype-assembly.md](../hardware/08-prototype-assembly.md)：銅箔膠帶組裝手冊

韌體：

- [firmware/README.md](../../firmware/README.md)：Teensy 韌體編譯 / 上傳說明

---

## 參考連結

- Node.js 官方下載：https://nodejs.org/zh-tw
- git 下載（Windows）：https://git-scm.com/download/win
- Gemini AI API 金鑰申請：https://aistudio.google.com/apikey
- FlowDJ 原始專案（GitHub）：https://github.com/hhh1715/flowdj---pro-mixing-interface
- 線上 MIDI Monitor（驗證 Teensy 是否被 OS 看到）：https://studiocode.dev/resources/midi-monitor/
- Web MIDI 瀏覽器支援：https://caniuse.com/midi
