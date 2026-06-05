# 復健圖生成 Webtool · Rehab Image Webtool

| 繁體中文 | English |
|----------|---------|
| 比較 **A 直接生成** 與 **B 審查迭代** 兩種復健說明圖流程的 Web 工具。使用者自帶 Gemini API Key（BYOK），輸入復健動作描述後即時體驗、對照結果。 | Web tool to compare **Pipeline A (direct generation)** and **Pipeline B (review & iteration)** for rehabilitation exercise infographics. Bring your own Gemini API key (BYOK), enter exercise text, and compare results live. |

---

## 功能特色 · Features

| 繁體中文 | English |
|----------|---------|
| **A 直接生成**：原文（附加語言規則）直接送生圖模型，一次出圖 | **Pipeline A**: Send text (with language rules) directly to the image model — one shot |
| **B 審查迭代**：提示詞生成 → 生圖 → AI 審查 → 未過則修正（v1/v2/v3…） | **Pipeline B**: Prompt generation → image → AI review → refine until pass or max iterations |
| **BYOK**：每人用自己的 [Gemini API Key](https://aistudio.google.com/app/apikey)，伺服器不必代管金鑰 | **BYOK**: Each user supplies their own [Gemini API Key](https://aistudio.google.com/app/apikey) |
| **雙語介面**：繁體中文 / English，含範例 prompt、log、圖片內標註語言 | **Bilingual UI**: Traditional Chinese / English — examples, logs, and on-image labels follow locale |
| **執行紀錄**：即時顯示可讀的步驟 log（非 traceback） | **Activity log**: Human-readable step-by-step progress (no raw tracebacks) |

---

## 技術版本 · Tech Stack

| 元件 Component | 版本 Version |
|----------------|--------------|
| Python | 3.10+ |
| FastAPI | ≥0.115 |
| uvicorn | ≥0.30 |
| Vue | 3.5 |
| Vite | 6 |
| Tailwind CSS | 3.4 |
| google-genai | 見父專案 `requirements.txt` / see parent `requirements.txt` |

---

## 前置需求 · Prerequisites

| 繁體中文 | English |
|----------|---------|
| 本 Webtool **需放在父專案根目錄**（與 `agents/`、`main.py`、`raw_generate.py`、`config.py` 同層的 `Webtool/` 資料夾），後端會 import 既有 Python 流程。 | This Webtool **must live inside the parent rehabilitation project** (`Webtool/` next to `agents/`, `main.py`, `raw_generate.py`, `config.py`). The backend imports existing Python pipelines. |
| 父專案需已建立 venv 並安裝 `requirements.txt`。 | Parent project venv with `requirements.txt` installed. |
| Node.js 18+（前端）。 | Node.js 18+ (frontend). |
| 啟動後端時設 `WEBTOOL_MODE=1`（可不設定伺服器 `.env` 的 `GEMINI_API_KEY`）。 | Set `WEBTOOL_MODE=1` when starting the backend (server `.env` `GEMINI_API_KEY` optional). |

---

## 快速啟動 · Quick Start

### Windows（PowerShell）

```powershell
# 父專案根目錄 · Parent project root
cd "path\to\1150203復健圖生成"
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -r Webtool\backend\requirements.txt

# 終端 1 — 後端 Backend
.\Webtool\start-backend.ps1

# 終端 2 — 前端 Frontend
.\Webtool\start-frontend.ps1
```

瀏覽器 / Browser: **http://localhost:5173**

### 手動啟動 · Manual

| 步驟 Step | 繁體中文 | English |
|-----------|----------|---------|
| 後端 | `cd Webtool\backend` → `$env:WEBTOOL_MODE="1"` → `uvicorn server:app --reload --port 8000` | Same commands |
| 前端 | `cd Webtool\frontend` → `npm install` → `npm run dev` | Same commands |

---

## 使用步驟 · Usage

| # | 繁體中文 | English |
|---|----------|---------|
| 1 | 右上角選擇語言（繁體中文 / English） | Select language (top-right) |
| 2 | 輸入 Gemini API Key → 驗證 | Enter and validate your Gemini API Key |
| 3 | 貼上復健動作描述，或載入範例 | Paste exercise description or load an example |
| 4 | 選擇 A+B / 僅 A / 僅 B → 開始生成 | Choose A+B / A only / B only → Start |
| 5 | 查看 log、B 各階段圖片與審查意見；完成後 A/B 並排對照 | Watch the log, B stage images & reviews; compare A/B when done |

---

## API

| 方法 Method | 路徑 Path | 繁體中文 | English |
|-------------|-----------|----------|---------|
| POST | `/api/validate-key?locale=` | 驗證金鑰；Header: `X-Gemini-Api-Key` | Validate key; header: `X-Gemini-Api-Key` |
| GET | `/api/examples?locale=` | 多語系範例 prompt | Localized example prompts |
| POST | `/api/jobs` | 建立工作；body 含 `prompt`, `modes`, `max_iterations`, `locale` | Create job |
| GET | `/api/jobs/{id}` | 工作狀態與 log | Job status & logs |
| GET | `/api/jobs/{id}/events` | SSE 即時事件 | SSE stream |
| GET | `/api/jobs/{id}/assets/{file}` | 產出圖片 | Output images |

產出暫存於 `Webtool/runtime/jobs/{job_id}/`（已 gitignore）。  
Outputs are stored under `Webtool/runtime/jobs/{job_id}/` (gitignored).

---

## 專案結構 · Project Layout

```
Webtool/
├── README.md
├── plan.md
├── start-backend.ps1
├── start-frontend.ps1
├── backend/          # FastAPI
├── frontend/         # Vue 3 + Vite
├── samples/          # 多語系範例 prompts
└── runtime/jobs/     # 執行暫存（不納入版控）
```

---

## i18n 架構 · Internationalization

| 層級 Layer | 路徑 Path | 用途 Purpose |
|------------|-----------|--------------|
| 前端 UI | `frontend/src/i18n/` | 介面文字、階段名稱 |
| 後端 log | `backend/i18n/messages.py` | 執行紀錄訊息 |
| 圖片 prompt | 父專案 `utils/i18n_prompts.py` | 生圖／審查提示詞語言 |

---

## 規劃文件 · Planning Doc

見 [plan.md](./plan.md) · See [plan.md](./plan.md)

---

## 授權 · License

與父專案相同，供學習與研究使用。  
Same as the parent project — for learning and research.
