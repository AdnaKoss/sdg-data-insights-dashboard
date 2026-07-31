"""
Simple linear-regression trend line and short-horizon forecast for one
country/indicator pair. This is intentionally a lightweight, transparent
model (year -> value, ordinary least squares) rather than a full time-series
model (ARIMA/Prophet): the goal is an illustrative "if this trend continues"
projection for a policy brief, not a rigorous forecast, and the API/response
says so explicitly via `method` and `disclaimer`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

MIN_POINTS_FOR_TREND = 4


def trend_forecast(
    df: pd.DataFrame, indicator_code: str, iso3: str, forecast_years: int = 5
) -> dict:
    sub = df[(df["indicator_code"] == indicator_code) & (df["iso3"] == iso3)].sort_values("year")

    if len(sub) < MIN_POINTS_FOR_TREND:
        return {
            "iso3": iso3,
            "indicator_code": indicator_code,
            "available": False,
            "reason": f"Only {len(sub)} data point(s); need at least {MIN_POINTS_FOR_TREND}.",
        }

    years = sub["year"].to_numpy().reshape(-1, 1)
    values = sub["value"].to_numpy()

    model = LinearRegression()
    model.fit(years, values)
    predicted = model.predict(years)
    r2 = float(r2_score(values, predicted))

    last_year = int(sub["year"].max())
    future_years = np.arange(last_year + 1, last_year + forecast_years + 1).reshape(-1, 1)
    forecast_values = model.predict(future_years)

    return {
        "iso3": iso3,
        "indicator_code": indicator_code,
        "available": True,
        "history": [
            {"year": int(y), "value": round(float(v), 3)}
            for y, v in zip(sub["year"], sub["value"])
        ],
        "forecast": [
            {"year": int(y[0]), "value": round(float(v), 3)}
            for y, v in zip(future_years, forecast_values)
        ],
        "slope_per_year": round(float(model.coef_[0]), 4),
        "r2": round(r2, 3),
        "method": "Ordinary least squares (year -> value), linear extrapolation",
        "disclaimer": (
            "Illustrative trend projection, not a rigorous demographic/econometric "
            "forecast. Treat directionally, not as a point prediction."
        ),
    }
