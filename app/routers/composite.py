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
                "meta": "以農藥清單與監測資料整合而成",
                "tone": None,
            },
            {
                "label": "IRAC 有標記資料",
                "value": f"{summary['irac_records']:,}",
                "unit": "筆",
                "meta": "可支撐 MOA 輪替判讀",
                "tone": "info",
            },
            {
                "label": "國外廠商資料",
                "value": f"{summary['foreign_records']:,}",
                "unit": "筆",
                "meta": "可用於來源結構分析",
                "tone": None,
            },
            {
                "label": "撤銷 / 註銷資料",
                "value": f"{summary['revoked_records']:,}",
                "unit": "筆",
                "meta": "可觀察政策監測與風險管理",
                "tone": "warn",
            },
        ],
        "irac_distribution": queries.get_pesticide_irac_distribution(12),
        "form_distribution": queries.get_pesticide_form_distribution(8),
        "origin_distribution": queries.get_pesticide_origin_distribution(10),
        "revocation_distribution": queries.get_pesticide_revocation_distribution(8),
        "category_distribution": queries.get_pesticide_category_distribution(8),
        "rotation_alerts": queries.get_moa_rotation_alerts(10),
    }
    ctx = {
        "request": request,
        "active": "pesticide",
        "page_title": "農藥情報面板",
        "page_subtitle": "從 IRAC、劑型、來源與 MOA 輪替預警切入，支撐主題三的政策監測情境。",
        "meta": config.PROJECT_META,
        "nav_items": config.NAV_ITEMS,
        "theme_logic": config.THEME_LOGIC,
        "pesticide_summary": pesticide_summary,
    }
    return templates.TemplateResponse("composite.html", ctx)
