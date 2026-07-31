"""
Local CSV cache for World Bank data.

`scripts/fetch_data.py` populates `data/raw/` once (the CSVs are small — a
few hundred KB total — and are committed to the repo) so the dashboard works
immediately after cloning, without depending on the World Bank API being up
or fast at demo time. `refresh()` re-pulls live data on demand (e.g. via the
`/api/admin/refresh` endpoint) for anyone who wants current figures.
"""

from __future__ import annotations

import logging

import pandas as pd

from app.config import INDICATORS, RAW_DIR
from app.data.worldbank_client import WorldBankClient

logger = logging.getLogger("sdg_dashboard.cache")

COUNTRIES_FILE = RAW_DIR / "countries.csv"
INDICATORS_FILE = RAW_DIR / "indicators.csv"


def countries_cached() -> bool:
    return COUNTRIES_FILE.exists()


def indicators_cached() -> bool:
    return INDICATORS_FILE.exists()


# pandas' default NA-string list includes the literal "NA" -- which is also
# Namibia's real ISO2 country code. This is pandas' default list
# (https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) with
# "NA" removed, so Namibia's row round-trips correctly; blank cells ("")
# keep parsing as NaN as normal.
_NA_VALUES_WITHOUT_NA_CODE = [
    "", "#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN", "-NaN", "-nan",
    "1.#IND", "1.#QNAN", "<NA>", "N/A", "NULL", "NaN", "None", "n/a", "nan", "null",
]


def load_countries() -> pd.DataFrame:
    if not countries_cached():
        raise FileNotFoundError(
            f"{COUNTRIES_FILE} not found. Run `python scripts/fetch_data.py` first."
        )
    return pd.read_csv(
        COUNTRIES_FILE, keep_default_na=False, na_values=_NA_VALUES_WITHOUT_NA_CODE
    )


def load_indicator_data() -> pd.DataFrame:
    """All indicators, all countries, all cached years, in one long dataframe
    with columns: indicator_code, iso3, country_name, year, value."""
    if not indicators_cached():
        raise FileNotFoundError(
            f"{INDICATORS_FILE} not found. Run `python scripts/fetch_data.py` first."
        )
    return pd.read_csv(INDICATORS_FILE)


def refresh(indicator_codes: list[str] | None = None) -> dict:
    """Re-fetch countries + indicators from the live World Bank API and
    overwrite the local cache. Returns a small summary dict."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    client = WorldBankClient()

    countries = client.fetch_countries()
    countries_df = pd.DataFrame(countries)
    countries_df.to_csv(COUNTRIES_FILE, index=False)

    valid_iso3 = set(countries_df["iso3"])
    codes = indicator_codes or list(INDICATORS.keys())

    all_records = []
    for code in codes:
        records = client.fetch_indicator(code)
        all_records.extend(r for r in records if r["iso3"] in valid_iso3)

    indicators_df = pd.DataFrame(all_records)
    indicators_df.to_csv(INDICATORS_FILE, index=False)

    summary = {
        "countries": len(countries_df),
        "indicators_fetched": len(codes),
        "observations": len(indicators_df),
    }
    logger.info("Cache refreshed: %s", summary)
    return summary
