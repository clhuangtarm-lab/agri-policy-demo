"""Composite pesticide intelligence route."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import config
from ..services import queries

router = APIRouter()


@router.get("/composite", response_class=HTMLResponse)
async def composite_page(request: Request):
    templates = request.app.state.templates
    summary = queries.get_pesticide_summary()
    pesticide_summary = {
        "kpis": [
            {
                "label": "農藥資料總筆數",
                "value": f"{summary['total_records']:,}",
                "unit": "筆",
                "meta": "主題三的核心監測底表",
                "tone": None,
            },
            {
                "label": "IRAC 已標註",
                "value": f"{summary['irac_records']:,}",
                "unit": "筆",
                "meta": "可直接納入抗性機制分析",
                "tone": "info",
            },
            {
                "label": "有來源製造商",
                "value": f"{summary['foreign_records']:,}",
                "unit": "筆",
                "meta": "支援來源地與供應鏈觀察",
                "tone": None,
            },
            {
                "label": "撤銷或廢止紀錄",
                "value": f"{summary['revoked_records']:,}",
                "unit": "筆",
                "meta": "可做政策風險監測提示",
                "tone": "warn",
            },
        ],
        "irac_distribution": queries.get_pesticide_irac_distribution(12),
        "form_distribution": queries.get_pesticide_form_distribution(8),
        "origin_distribution": queries.get_pesticide_origin_distribution(10),
        "revocation_distribution": queries.get_pesticide_revocation_distribution(8),
        "category_distribution": queries.get_pesticide_category_distribution(8),
    }
    ctx = {
        "request": request,
        "active": "pesticide",
        "page_title": "農藥情報面板",
        "page_subtitle": "主題三聚焦 IRAC、劑型、來源與撤銷狀態，支撐標案的風險情報與管理判讀。",
        "meta": config.PROJECT_META,
        "nav_items": config.NAV_ITEMS,
        "theme_logic": config.THEME_LOGIC,
        "pesticide_summary": pesticide_summary,
    }
    return templates.TemplateResponse("composite.html", ctx)
