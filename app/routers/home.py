"""Overview dashboard route."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import config
from ..services import queries

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    templates = request.app.state.templates
    counts = queries.get_summary_counts()
    high_risk = queries.get_high_risk_crops(12)
    county_risk = queries.get_county_risk(10)
    overview = {
        "kpis": [
            {
                "label": "作物面積資料列",
                "value": f"{counts['crop_area_rows']:,}",
                "unit": "列",
                "meta": f"{counts['county_count']} 縣市 / {counts['town_count']} 鄉鎮",
                "tone": None,
            },
            {
                "label": "總種植面積",
                "value": f"{counts['crop_area_total']:,.1f}",
                "unit": "公頃",
                "meta": f"{counts['crop_count']} 個作物名稱",
                "tone": "info",
            },
            {
                "label": "農藥登記資料",
                "value": f"{counts['pesticide_count']:,}",
                "unit": "筆",
                "meta": f"覆蓋風險作物 {counts['coverage_risk_count']:,} 筆",
                "tone": None,
            },
            {
                "label": "溯源生產者",
                "value": f"{counts['producer_count']:,}",
                "unit": "筆",
                "meta": f"產品資料 {counts['product_count']:,} 筆",
                "tone": None,
            },
            {
                "label": "檢驗合格率",
                "value": f"{counts['inspection_pass_rate']:.1f}",
                "unit": "%",
                "meta": f"共 {counts['inspection_count']:,} 筆檢驗結果",
                "tone": "warn",
            },
        ],
        "risk_crops": high_risk,
        "county_risk": county_risk,
        "findings": queries.get_key_findings(),
        "themes": config.THEME_LOGIC,
    }
    ctx = {
        "request": request,
        "active": "overview",
        "page_title": "總覽儀表板",
        "page_subtitle": "整合主題一區域風險、主題二作物覆蓋、主題三農藥情報的單頁總覽。",
        "meta": config.PROJECT_META,
        "nav_items": config.NAV_ITEMS,
        "theme_logic": config.THEME_LOGIC,
        "overview": overview,
    }
    return templates.TemplateResponse("home.html", ctx)
