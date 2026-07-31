"""Live-refresh endpoint: re-pulls current data from the World Bank API and
swaps it into the running app's in-memory state (see app.deps). The
committed CSVs in data/raw/ stay untouched unless you also rerun
scripts/fetch_data.py, so a bad refresh never corrupts the repo's demo
dataset."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.data import cache
from app.schemas import RefreshResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/refresh-data", response_model=RefreshResponse)
def refresh_data(request: Request):
    summary = cache.refresh()
    request.app.state.data_df = cache.load_indicator_data()
    request.app.state.countries_df = cache.load_countries()
    return summary
