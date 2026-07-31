"""
SDG Data Insights Dashboard API.

Serves World Bank Open Data indicators (internet access, education,
poverty, gender equality...) plus two lightweight ML analyses — KMeans
digital-readiness clustering and per-country linear trend forecasting —
and an auto-generated policy brief (Markdown/PDF).

Run from backend/:
    python run.py
or:
    python -m uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import ROOT_DIR
from app.data import cache
from app.routers import admin, analysis, catalogue, data, reports

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sdg_dashboard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not cache.indicators_cached():
        logger.warning(
            "No cached data found. Run `python scripts/fetch_data.py` from backend/ first."
        )
        app.state.data_df = None
        app.state.countries_df = None
    else:
        app.state.data_df = cache.load_indicator_data()
        app.state.countries_df = cache.load_countries()
        logger.info(
            "Loaded %d observations for %d countries from cache",
            len(app.state.data_df),
            len(app.state.countries_df),
        )
    yield


app = FastAPI(
    title="SDG Data Insights Dashboard API",
    description=(
        "World Bank Open Data indicators, digital-readiness clustering, trend "
        "forecasting, and auto-generated policy briefs — built to demonstrate "
        "data analysis and AI/ML applied to sustainable-development questions."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(catalogue.router)
app.include_router(data.router)
app.include_router(analysis.router)
app.include_router(reports.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "data_loaded": app.state.data_df is not None,
    }


# Mounted last so it never shadows the /api/* routes above: Starlette tries
# routes in registration order and this Mount only catches what nothing else
# matched. Serves the built React app (frontend/dist) at http://localhost:8000/.
FRONTEND_DIST = ROOT_DIR.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
