"""Traceability interaction route."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import config
from ..services import queries

router = APIRouter()


@router.get("/traceability", response_class=HTMLResponse)
async def traceability_page(
    request: Request,
    county: str | None = None,
    crop: str | None = None,
    status: str | None = None,
):
    templates = request.app.state.templates

    summary = queries.get_traceability_summary()
    county_rows = queries.get_traceability_county_distribution()
    crop_rows = queries.get_traceability_crop_distribution()
    status_rows = queries.get_traceability_status_distribution()
    inspection_rows = queries.get_traceability_inspection_distribution(24)
    county_crop_rows = queries.get_traceability_county_crop_rows()
    sample_rows = queries.get_traceability_sample_records(240)

    county_options = [row["county"] for row in county_rows]
    crop_options = [row["crop"] for row in crop_rows]
    status_options = [row["label"] for row in status_rows]

    selected_county = county if county in county_options else (county_options[0] if county_options else "")
    selected_crop = crop if crop in crop_options else (crop_options[0] if crop_options else "")
    selected_status = status if status in status_options else (status_options[0] if status_options else "")

    traceability = {
        "summary": summary,
        "counties": county_rows,
        "crops": crop_rows,
        "statuses": status_rows,
        "inspections": inspection_rows,
        "county_crop_rows": county_crop_rows,
        "sample_rows": sample_rows,
        "selected_county": selected_county,
        "selected_crop": selected_crop,
        "selected_status": selected_status,
    }

    ctx = {
        "request": request,
        "active": "traceability",
        "page_title": "產銷履歷互動頁",
        "page_subtitle": "整合履歷生產者、產品與檢驗結果，快速查看縣市與作物的履歷覆蓋輪廓。",
        "meta": config.PROJECT_META,
        "nav_items": config.NAV_ITEMS,
        "theme_logic": config.THEME_LOGIC,
        "traceability": traceability,
    }
    return templates.TemplateResponse("traceability.html", ctx)
