"""Theme 3 crop risk and coverage matrix route."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import config
from ..services import queries

router = APIRouter(prefix="/theme3")


@router.get("/coverage", response_class=HTMLResponse)
async def coverage_page(request: Request, q: str = ""):
    templates = request.app.state.templates
    crop_matrix = {
        "query": q,
        "rows": queries.get_crop_matrix_rows(q, 28),
        "high_risk": queries.get_high_risk_crops(10),
        "low_coverage": queries.get_low_coverage_crops(10),
        "coverage_levels": queries.get_coverage_level_distribution(),
        "vulnerable": queries.get_vulnerable_crops(8),
    }
    ctx = {
        "request": request,
        "active": "coverage",
        "page_title": "作物風險矩陣",
        "page_subtitle": "主題二將高風險占比、覆蓋充裕度與 IRAC 多樣性整合成可操作的作物矩陣。",
        "meta": config.PROJECT_META,
        "nav_items": config.NAV_ITEMS,
        "theme_logic": config.THEME_LOGIC,
        "crop_matrix": crop_matrix,
    }
    return templates.TemplateResponse("theme3_coverage.html", ctx)
