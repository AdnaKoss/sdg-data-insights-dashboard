"""ML-backed endpoints: digital-readiness clustering (KMeans + PCA) and a
per-country linear trend/forecast."""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from app.analysis import clustering, trend
from app.config import DIGITAL_READINESS_INDICATORS, INDICATORS, N_CLUSTERS
from app.deps import get_countries_df, get_data_df
from app.schemas import ClusterResponse, TrendResponse

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/clusters", response_model=ClusterResponse)
def get_clusters(
    df: pd.DataFrame = Depends(get_data_df),
    countries_df: pd.DataFrame = Depends(get_countries_df),
):
    try:
        clustered = clustering.cluster_countries(df, countries_df, n_clusters=N_CLUSTERS)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    items = []
    for _, row in clustered.iterrows():
        items.append(
            {
                "iso3": row["iso3"],
                "name": row["name"],
                "region": row["region"],
                "income_level": row["income_level"],
                "composite_score": row["composite_score"],
                "cluster_id": int(row["cluster_id"]),
                "cluster_label": row["cluster_label"],
                "pca_x": row["pca_x"],
                "pca_y": row["pca_y"],
                "values": {code: row[code] for code in DIGITAL_READINESS_INDICATORS},
            }
        )

    return {"n_clusters": N_CLUSTERS, "countries_included": len(items), "items": items}


@router.get("/trend", response_model=TrendResponse)
def get_trend(
    indicator: str = Query(...),
    country: str = Query(..., description="ISO3 country code"),
    forecast_years: int = Query(5, ge=1, le=15),
    df: pd.DataFrame = Depends(get_data_df),
):
    if indicator not in INDICATORS:
        raise HTTPException(status_code=404, detail=f"Unknown indicator: {indicator}")
    return trend.trend_forecast(df, indicator, country.upper(), forecast_years=forecast_years)
