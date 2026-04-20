"""Theme 1 county and township map routes."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .. import config
from ..services import queries

router = APIRouter(prefix="/theme1")


@router.get("/map", response_class=HTMLResponse)
async def map_page(request: Request, county: str | None = None):
    templates = request.app.state.templates
    county_rows = queries.get_county_risk()
    county_lookup = {row["county"]: row for row in county_rows}
    requested = county if county in county_lookup else None
    selected = requested or (county_rows[0]["county"] if county_rows else "")

    map_data = {
        "counties": county_rows,
        "selected_county": selected,
        "selected_county_key": config.normalize_county_name(selected),
        "county_geo": config.COUNTY_GEO,
        "top_townships": queries.get_township_risk(400),
        "county_crop_mix": {
            row["county_key"]: queries.get_crops_by_county(row["county"], 8) for row in county_rows
        },
    }

    ctx = {
        "request": request,
        "active": "map",
        "page_title": "縣市風險地圖",
        "page_subtitle": "主題一以縣市與鄉鎮暴露排序對應標案中的場域定位與治理優先順序。",
        "meta": config.PROJECT_META,
        "nav_items": config.NAV_ITEMS,
        "theme_logic": config.THEME_LOGIC,
        "map_data": map_data,
    }
    return templates.TemplateResponse("theme1_map.html", ctx)


@router.get("/api/county-crop")
async def api_county_crop(crop: str):
    return JSONResponse(queries.get_county_crop_matrix(crop))
