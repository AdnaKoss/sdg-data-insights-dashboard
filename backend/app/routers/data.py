"""Raw and lightly-aggregated indicator data: time series, rankings, KPIs,
and top-improver lists — the building blocks the frontend charts consume."""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from app.analysis import stats
from app.config import INDICATORS
from app.deps import get_countries_df, get_data_df
from app.schemas import DataPoint, ImproverItem, RankingItem, SummaryKpis

router = APIRouter(prefix="/api/data", tags=["data"])


def _validate_indicator(indicator: str) -> str:
    if indicator not in INDICATORS:
        raise HTTPException(status_code=404, detail=f"Unknown indicator: {indicator}")
    return indicator


@router.get("", response_model=list[DataPoint])
def get_time_series(
    indicator: str = Query(...),
    countries: str | None = Query(None, description="Comma-separated ISO3 codes"),
    start: int | None = None,
    end: int | None = None,
    df: pd.DataFrame = Depends(get_data_df),
):
    _validate_indicator(indicator)
    sub = df[df["indicator_code"] == indicator]

    if countries:
        iso_list = [c.strip().upper() for c in countries.split(",") if c.strip()]
        sub = sub[sub["iso3"].isin(iso_list)]
    if start is not None:
        sub = sub[sub["year"] >= start]
    if end is not None:
        sub = sub[sub["year"] <= end]

    return sub.sort_values(["iso3", "year"]).to_dict(orient="records")


@router.get("/summary", response_model=SummaryKpis)
def get_summary(
    indicator: str = Query(...),
    df: pd.DataFrame = Depends(get_data_df),
    countries_df: pd.DataFrame = Depends(get_countries_df),
):
    _validate_indicator(indicator)
    return stats.summary_kpis(df, indicator, countries_df)


@router.get("/ranking", response_model=list[RankingItem])
def get_ranking(
    indicator: str = Query(...),
    top_n: int = Query(10, ge=1, le=217),
    ascending: bool = False,
    region: str | None = None,
    df: pd.DataFrame = Depends(get_data_df),
    countries_df: pd.DataFrame = Depends(get_countries_df),
):
    _validate_indicator(indicator)
    result = stats.ranking(df, indicator, countries_df, top_n=top_n, ascending=ascending, region=region)
    return result.to_dict(orient="records")


@router.get("/improvers", response_model=list[ImproverItem])
def get_improvers(
    indicator: str = Query(...),
    years_back: int = Query(10, ge=1, le=24),
    top_n: int = Query(5, ge=1, le=50),
    df: pd.DataFrame = Depends(get_data_df),
    countries_df: pd.DataFrame = Depends(get_countries_df),
):
    _validate_indicator(indicator)
    result = stats.change_over_period(df, indicator, countries_df, years_back=years_back, top_n=top_n)
    return result.to_dict(orient="records")
