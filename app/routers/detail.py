"""Crop detail route."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import config
from ..services import queries

router = APIRouter()


@router.get("/detail", response_class=HTMLResponse)
async def detail_page(request: Request, crop: str | None = None):
    templates = request.app.state.templates
    resolved_crop = queries.resolve_crop_name(crop)
    detail = queries.get_crop_detail(resolved_crop) if resolved_crop else None
    if detail is None:
        detail = {
            "crop": "",
            "area_ha": 0,
            "high_risk_ratio": 0,
            "exposure": 0,
            "registration_count": 0,
            "total_count": 0,
            "domestic_count": 0,
            "import_count": 0,
            "coverage_level": "無資料",
            "coverage_irac_code_count": 0,
            "irac_code_count": 0,
            "irac_codes": "",
            "irac_diversity": 0,
            "risk_note": "",
        }

    detail["irac_profile"] = queries.get_crop_irac_profile(detail["crop"], 12) if detail["crop"] else []
    detail["county_distribution"] = (
        queries.get_crop_county_distribution(detail["crop"], 10) if detail["crop"] else []
    )
    detail["advisory_points"] = [
        f"高風險機制占比 {detail['high_risk_ratio']:.1%}，可作為政策示警與示範場域優先排序的依據。",
        f"有效登記農藥 {detail['registration_count']:,} 筆，覆蓋充裕度為「{detail['coverage_level']}」。",
        f"IRAC 代碼種數 {detail['coverage_irac_code_count']}，多樣性指標 {detail['irac_diversity']}。",
        "可搭配縣市分布與鄉鎮暴露，作為主題一至主題三的跨頁 drill-down 示範。",
    ]

    ctx = {
        "request": request,
        "active": "detail",
        "page_title": "作物深度頁",
        "page_subtitle": "將單一作物的風險暴露、農藥覆蓋與區域分布串成標案展示時可講述的決策故事。",
        "meta": config.PROJECT_META,
        "nav_items": config.NAV_ITEMS,
        "theme_logic": config.THEME_LOGIC,
        "detail": detail,
    }
    return templates.TemplateResponse("detail.html", ctx)
