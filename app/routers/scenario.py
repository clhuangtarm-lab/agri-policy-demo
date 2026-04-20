"""Interactive scenario sandbox route."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import config
from ..services import queries

router = APIRouter()

SCENARIO_STRATEGIES = [
    {
        "id": "monitoring",
        "label": "巡查強化",
        "description": "提高高風險鄉鎮巡查頻率，優先處理暴露熱點。",
        "effect": 0.18,
        "coverage_bonus": 0.08,
        "diversity_bonus": 0.12,
        "focus": "主題一 / 空間熱點調度",
    },
    {
        "id": "rotation",
        "label": "輪替管理",
        "description": "以 IRAC 輪替為核心，降低少數作用機制過度集中。",
        "effect": 0.24,
        "coverage_bonus": 0.12,
        "diversity_bonus": 0.22,
        "focus": "主題二 / 覆蓋與抗性韌性",
    },
    {
        "id": "combined",
        "label": "綜合介入",
        "description": "同步結合巡查、藥劑配置與風險溝通，適合展示完整政策情境。",
        "effect": 0.32,
        "coverage_bonus": 0.18,
        "diversity_bonus": 0.3,
        "focus": "主題三 / 政策整合模擬",
    },
]


def _clamp_intensity(value: int) -> int:
    return max(0, min(100, value))


@router.get("/scenario", response_class=HTMLResponse)
async def scenario_page(
    request: Request,
    county: str | None = None,
    crop: str | None = None,
    strategy: str = "combined",
    intensity: int = 55,
):
    templates = request.app.state.templates

    county_rows = queries.get_county_risk()
    crop_rows = queries.get_crop_matrix_rows("", 100)

    county_names = {row["county"] for row in county_rows}
    crop_names = {row["crop"] for row in crop_rows}

    selected_county = county if county in county_names else (county_rows[0]["county"] if county_rows else "")
    selected_crop = crop if crop in crop_names else (crop_rows[0]["crop"] if crop_rows else "")

    strategy_ids = {item["id"] for item in SCENARIO_STRATEGIES}
    selected_strategy = strategy if strategy in strategy_ids else "combined"
    selected_intensity = _clamp_intensity(intensity)

    county_crop_rows: list[dict] = []
    irac_profiles: dict[str, list[dict]] = {}
    for row in crop_rows:
        crop_name = row["crop"]
        irac_profiles[crop_name] = queries.get_crop_irac_profile(crop_name, 8)
        for county_dist in queries.get_crop_county_distribution(crop_name, 30):
            county_crop_rows.append(
                {
                    "county": county_dist["county"],
                    "crop": crop_name,
                    "area_ha": county_dist["area_ha"],
                    "town_count": county_dist["town_count"],
                    "exposure": county_dist["exposure_estimate"],
                }
            )

    scenario_data = {
        "strategies": SCENARIO_STRATEGIES,
        "selected_strategy": selected_strategy,
        "selected_intensity": selected_intensity,
        "selected_county": selected_county,
        "selected_crop": selected_crop,
        "counties": county_rows,
        "crops": crop_rows,
        "county_crop_rows": county_crop_rows,
        "townships": queries.get_township_risk(500),
        "irac_profiles": irac_profiles,
    }

    ctx = {
        "request": request,
        "active": "scenario",
        "page_title": "情境沙盤模擬",
        "page_subtitle": "以真實風險、覆蓋與 IRAC 結構作為基線，透過輕量互動模擬政策介入後的可能變化。",
        "meta": config.PROJECT_META,
        "nav_items": config.NAV_ITEMS,
        "theme_logic": config.THEME_LOGIC,
        "scenario": scenario_data,
    }
    return templates.TemplateResponse("scenario.html", ctx)
