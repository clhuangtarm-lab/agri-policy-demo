# 農業資料整合分析平臺 DEMO

115 年度運用資料研析農業措施及開發分析平臺（標案 DEMO，FastAPI + SQLite + ECharts）。

## 頁面清單

| 代號 | 路徑 | 說明 |
|------|------|------|
| P-00 | `/` | 首頁儀表、三大主題入口、全國作物 / 縣市 Top 10 |
| P-11 | `/theme1/map` | 主題 1：單一作物縣市分布（可切換作物） |
| P-32 | `/theme3/coverage` | 主題 3：用藥充裕度、analysis_A 高風險作物 |
| P-50 | `/composite` | 主題 4：縣市風險、面積 × 風險散點、充裕度對照 |
| API  | `/api/docs` | FastAPI 自動產生的 OpenAPI UI |

## 技術堆疊

- **Backend**：FastAPI 0.115 + Uvicorn
- **Data**：SQLite（由 `etl/build_db.py` 從 23 支 MOA API + reference CSV 產出 ~88 MB）
- **Frontend**：Jinja2 + HTMX + ECharts 5（無前端 build 流程）
- **Font**：Noto Sans TC + JetBrains Mono

## 本機執行

```bash
cd output/demo_platform

# 1. 安裝套件
pip install -r requirements.txt

# 2. 建 DB（第一次或 reference 更新時才需要）
python -m etl.build_db

# 3. 啟動
uvicorn app.main:app --reload --port 8080
# 瀏覽 http://localhost:8080
```

> Windows + OneDrive 環境：ETL 會先寫到 %TEMP%\agri_demo_build\demo.db，再一次性複製到
> `data/demo.db`；`app/db.py` 亦支援從 OneDrive 同步目錄快取到本機 temp，避免 SQLite 鎖檔。

## Zeabur 部署

1. 先在本地成功跑完 `python -m etl.build_db`，確認 `data/demo.db` > 80 MB。
2. 把整個 `demo_platform/` push 到 GitHub（**含 `data/demo.db`**；或在 CI 跑 ETL）。
3. Zeabur → New Service → From GitHub → 選這個 repo。
4. Zeabur 會自動讀到 `Dockerfile` / `zeabur.json`，暴露 HTTP 8080。
5. 綁好網域即可公網瀏覽。

> DB 88 MB 放 repo 過大，可把 reference CSV + API JSON 上 repo，
> 在 `Dockerfile` 加一行 `RUN python -m etl.build_db` 在 build 時產出。

## 專案結構

```
demo_platform/
├── app/
│   ├── main.py               # FastAPI 入口
│   ├── config.py             # 專案 metadata / 主題 / 政策主軸
│   ├── db.py                 # SQLite 連線（含 OneDrive 快取邏輯）
│   ├── routers/
│   │   ├── home.py           # P-00
│   │   ├── theme1_map.py     # P-11
│   │   ├── theme3_coverage.py# P-32
│   │   └── composite.py      # P-50
│   ├── services/queries.py   # 共用查詢
│   ├── templates/            # Jinja2 模板（dark theme）
│   └── static/css/platform.css
├── etl/build_db.py           # 從 API + CSV 清洗成 SQLite
├── data/demo.db              # ETL 產出
├── requirements.txt
├── Dockerfile
├── zeabur.json
└── README.md
```

## 資料來源（23 支 MOA API + 既有分析）

| 類別 | 檔案 | 說明 |
|------|------|------|
| 作物分類 | `input/reference/作物分類對照表_研究分析版.csv` | 4,370 列，三層階層 + 科別 + 品種 |
| 作物別名 | `input/reference/作物名稱_alias拆分.csv` | 950 列，alias ↔ 標準名對應 |
| 作物面積 | `Pesticide/agri_clean.csv` | 113 年農情調查清洗版，21,356 列 |
| 履歷 | API-19 / API-20 | 106,492 戶、463,625 產品 |
| 藥檢 | API-23 | 15,210 筆，合格率 98.5% |
| 農藥 | `pesticide_full.csv` + coverage_risk + irac_diversity | ~12,000 筆用藥資料 |
| 既有分析 | `analysis_A` ~ `F` | 高風險作物、縣市風險、機制多樣性等 |

## 下一步 roadmap

- P-12 縣市 × 作物 Choropleth（Leaflet + TWN-TOWN GeoJSON）
- P-21 履歷戶家搜尋（rapidfuzz + 歷史藥檢查詢）
- P-31 農藥搜尋頁（作用機制 / 適用作物）
- P-40 政策 KPI：智慧 / 韌性 / 永續 / 安心 四象限
