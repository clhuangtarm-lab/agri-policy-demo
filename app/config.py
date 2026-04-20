"""Application configuration and shared UI metadata."""
from __future__ import annotations

from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional for local inspection scripts
    def load_dotenv(*_args, **_kwargs):
        return False


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "data" / "demo.db"))
DATA_ROOT = Path(os.getenv("DATA_ROOT", BASE_DIR.parent.parent)).resolve()
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

PROJECT_META = {
    "title": "農業政策互動決策 Demo 平台",
    "subtitle": "整合作物風險、產銷履歷、農藥覆蓋與政策情境的互動展示版本",
    "version": "DEMO v0.3 Interactive",
    "build_date": "2026-04-20",
}

NAV_ITEMS = [
    {"id": "overview", "code": "01", "label": "總覽儀表板", "path": "/"},
    {"id": "map", "code": "02", "label": "縣市風險地圖", "path": "/theme1/map"},
    {"id": "coverage", "code": "03", "label": "作物風險矩陣", "path": "/theme3/coverage"},
    {"id": "pesticide", "code": "04", "label": "農藥情報面板", "path": "/composite"},
    {"id": "detail", "code": "05", "label": "作物深度頁", "path": "/detail"},
    {"id": "scenario", "code": "06", "label": "情境沙盤模擬", "path": "/scenario"},
    {"id": "traceability", "code": "07", "label": "產銷履歷互動頁", "path": "/traceability"},
]

THEME_LOGIC = [
    {"code": "主題一", "label": "區域風險定位", "description": "以縣市與鄉鎮暴露排序掌握場域輪廓。"},
    {"code": "主題二", "label": "作物覆蓋診斷", "description": "以作物面積、登記數與 IRAC 多樣性評估可用性。"},
    {"code": "主題三", "label": "農藥監測情報", "description": "以 IRAC、劑型、來源與撤銷狀態支撐政策判讀。"},
]

COUNTY_GEO = {
    "連江縣": {"cx": 265, "cy": 48, "size": 10},
    "基隆市": {"cx": 248, "cy": 68, "size": 14},
    "台北市": {"cx": 240, "cy": 80, "size": 18},
    "新北市": {"cx": 226, "cy": 92, "size": 26},
    "桃園市": {"cx": 210, "cy": 112, "size": 18},
    "新竹市": {"cx": 188, "cy": 128, "size": 10},
    "新竹縣": {"cx": 200, "cy": 136, "size": 18},
    "苗栗縣": {"cx": 188, "cy": 164, "size": 20},
    "台中市": {"cx": 178, "cy": 202, "size": 22},
    "彰化縣": {"cx": 156, "cy": 228, "size": 16},
    "南投縣": {"cx": 202, "cy": 228, "size": 18},
    "雲林縣": {"cx": 145, "cy": 260, "size": 18},
    "嘉義市": {"cx": 144, "cy": 284, "size": 10},
    "嘉義縣": {"cx": 160, "cy": 292, "size": 18},
    "台南市": {"cx": 135, "cy": 330, "size": 20},
    "高雄市": {"cx": 160, "cy": 370, "size": 22},
    "屏東縣": {"cx": 180, "cy": 416, "size": 22},
    "宜蘭縣": {"cx": 270, "cy": 116, "size": 18},
    "花蓮縣": {"cx": 260, "cy": 224, "size": 22},
    "台東縣": {"cx": 240, "cy": 340, "size": 22},
    "澎湖縣": {"cx": 60, "cy": 310, "size": 12},
    "金門縣": {"cx": 40, "cy": 180, "size": 12},
}


def normalize_county_name(name: str) -> str:
    """Normalize county names for geometry lookup."""
    return (name or "").replace("臺", "台").strip()
