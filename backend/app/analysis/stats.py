"""
Descriptive statistics over the cached World Bank panel: latest values,
country rankings, and change-over-time (improvers/decliners).
"""

from __future__ import annotations

import pandas as pd


def indicator_slice(df: pd.DataFrame, indicator_code: str) -> pd.DataFrame:
    return df[df["indicator_code"] == indicator_code]


def latest_values(df: pd.DataFrame, indicator_code: str, countries_df: pd.DataFrame) -> pd.DataFrame:
    """One row per country: its most recent available (year, value) for the
    given indicator, joined with region/income metadata."""
    sub = indicator_slice(df, indicator_code)
    if sub.empty:
        return sub

    latest = sub.sort_values("year").groupby("iso3", as_index=False).last()
    merged = latest.merge(
        countries_df[["iso3", "name", "region", "income_level"]], on="iso3", how="left"
    )
    return merged[["iso3", "name", "region", "income_level", "year", "value"]]


def ranking(
    df: pd.DataFrame,
    indicator_code: str,
    countries_df: pd.DataFrame,
    top_n: int = 10,
    ascending: bool = False,
    region: str | None = None,
) -> pd.DataFrame:
    """Top/bottom N countries by latest available value, optionally filtered
    to one region."""
    latest = latest_values(df, indicator_code, countries_df)
    if region:
        latest = latest[latest["region"] == region]
    return latest.sort_values("value", ascending=ascending).head(top_n).reset_index(drop=True)


def change_over_period(
    df: pd.DataFrame,
    indicator_code: str,
    countries_df: pd.DataFrame,
    years_back: int = 10,
    top_n: int = 5,
) -> pd.DataFrame:
    """Countries with the largest change in the indicator over the last
    `years_back` years of available data. For each country independently we
    compare its latest observation to the observation closest to
    (latest_year - years_back), so countries with different reporting years
    are still comparable."""
    sub = indicator_slice(df, indicator_code)
    if sub.empty:
        return sub

    rows = []
    for iso3, group in sub.groupby("iso3"):
        group = group.sort_values("year")
        if len(group) < 2:
            continue
        end_row = group.iloc[-1]
        target_year = end_row["year"] - years_back
        start_candidates = group[group["year"] <= target_year]
        if start_candidates.empty:
            start_row = group.iloc[0]
        else:
            start_row = start_candidates.iloc[-1]
        if start_row["year"] == end_row["year"]:
            continue

        abs_change = end_row["value"] - start_row["value"]
        pct_change = (abs_change / start_row["value"] * 100) if start_row["value"] else None
        rows.append(
            {
                "iso3": iso3,
                "start_year": int(start_row["year"]),
                "start_value": start_row["value"],
                "end_year": int(end_row["year"]),
                "end_value": end_row["value"],
                "abs_change": abs_change,
                "pct_change": pct_change,
            }
        )

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    result = result.merge(countries_df[["iso3", "name", "region"]], on="iso3", how="left")
    return result.sort_values("abs_change", ascending=False).head(top_n).reset_index(drop=True)


def summary_kpis(df: pd.DataFrame, indicator_code: str, countries_df: pd.DataFrame) -> dict:
    """Global summary stats for the KPI cards: mean/median/min/max across the
    latest value per country, and how many countries have data at all."""
    latest = latest_values(df, indicator_code, countries_df)
    if latest.empty:
        return {"countries_covered": 0}

    return {
        "countries_covered": int(latest["value"].notna().sum()),
        "mean": round(float(latest["value"].mean()), 2),
        "median": round(float(latest["value"].median()), 2),
        "min": round(float(latest["value"].min()), 2),
        "max": round(float(latest["value"].max()), 2),
        "latest_year_max": int(latest["year"].max()),
    }
