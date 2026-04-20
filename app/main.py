"""FastAPI application entrypoint."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import config
from .routers import composite, detail, home, scenario, theme1_map, theme3_coverage, traceability

BASE = Path(__file__).resolve().parent

app = FastAPI(
    title=config.PROJECT_META["title"],
    version=config.PROJECT_META["version"],
    docs_url="/api/docs",
    redoc_url=None,
)

app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")
app.state.templates = templates

app.include_router(home.router)
app.include_router(theme1_map.router)
app.include_router(theme3_coverage.router)
app.include_router(composite.router)
app.include_router(detail.router)
app.include_router(scenario.router)
app.include_router(traceability.router)


@app.get("/healthz")
async def health():
    return {"status": "ok", "version": config.PROJECT_META["version"]}
