"""Traceability interaction route."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

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

    county_options = [row["county"] for row in county_rows]
    crop_options = [row["crop"] for row in crop_rows]
    status_options = [row["label"] for row in status_rows]

    selected_county = county if county in county_options else (county_options[0] if county_options else "")
    selected_crop = crop if crop in crop_options else (crop_options[0] if crop_options else "")
    selected_status = status if status in status_options else (status_options[0] if status_options else "")
    practice_profile = queries.get_traceability_practice_profile(
        county=selected_county,
        crop=selected_crop,
        status=selected_status,
    )
    flow_profile = queries.get_traceability_flow(
        county=selected_county,
        crop=selected_crop,
        status=selected_status,
    )

    traceability = {
        "summary": summary,
        "counties": county_rows,
        "crops": crop_rows,
        "statuses": status_rows,
        "inspections": inspection_rows,
        "county_crop_rows": county_crop_rows,
        "practice_profile": practice_profile,
        "flow_profile": flow_profile,
        "selected_county": selected_county,
        "selected_crop": selected_crop,
        "selected_status": selected_status,
    }

    ctx = {
        "request": request,
        "active": "traceability",
        "page_title": "產銷履歷互動頁",
        "page_subtitle": "整合履歷生產者、產品、狀態與檢驗結果，並用文字探勘示範栽培、防治與肥培分析。",
        "meta": config.PROJECT_META,
        "nav_items": config.NAV_ITEMS,
        "theme_logic": config.THEME_LOGIC,
        "traceability": traceability,
    }
    return templates.TemplateResponse("traceability.html", ctx)


@router.get("/traceability/api/records", response_class=JSONResponse)
async def traceability_records_api(
    county: str | None = None,
    crop: str | None = None,
    status: str | None = None,
    limit: int = 20,
):
    rows = queries.get_traceability_filtered_records(
        county=county,
        crop=crop,
        status=status,
        limit=max(1, min(limit, 50)),
    )
    return {"rows": rows}


@router.get("/traceability/api/practices", response_class=JSONResponse)
async def traceability_practices_api(
    county: str | None = None,
    crop: str | None = None,
    status: str | None = None,
):
    profile = queries.get_traceability_practice_profile(
        county=county,
        crop=crop,
        status=status,
    )
    return profile


@router.get("/traceability/api/flow", response_class=JSONResponse)
async def traceability_flow_api(
    county: str | None = None,
    crop: str | None = None,
    status: str | None = None,
):
    profile = queries.get_traceability_flow(
        county=county,
        crop=crop,
        status=status,
    )
    return profile
