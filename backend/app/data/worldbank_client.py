"""
Thin client for the World Bank Open Data API (https://api.worldbank.org/v2/).

No API key is required. The API occasionally returns a transient 4xx/5xx for
otherwise-valid requests under load, so every call goes through a retrying
`requests.Session` rather than a bare `requests.get`.
"""

from __future__ import annotations

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import WORLD_BANK_API_BASE, YEAR_END, YEAR_START

logger = logging.getLogger("sdg_dashboard.worldbank_client")


def _session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=0.8,
        status_forcelist=[400, 429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


class WorldBankClient:
    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout
        self.session = _session()

    def fetch_countries(self) -> list[dict]:
        """Return real countries only (World Bank also returns ~78 regional/income
        aggregates like "World" or "Sub-Saharan Africa" in this same endpoint,
        identifiable by region.id == "NA")."""
        resp = self.session.get(
            f"{WORLD_BANK_API_BASE}/country",
            params={"format": "json", "per_page": 400},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        _, rows = resp.json()

        countries = []
        for row in rows:
            if row["region"]["id"] == "NA":
                continue  # aggregate, not a country
            countries.append(
                {
                    "iso3": row["id"],
                    "iso2": row["iso2Code"],
                    "name": row["name"],
                    "region": row["region"]["value"].strip(),
                    "income_level": row["incomeLevel"]["value"],
                    "capital_city": row["capitalCity"],
                    "latitude": float(row["latitude"]) if row["latitude"] else None,
                    "longitude": float(row["longitude"]) if row["longitude"] else None,
                }
            )
        logger.info("Fetched %d countries from World Bank API", len(countries))
        return countries

    def fetch_indicator(
        self, indicator_code: str, year_start: int = YEAR_START, year_end: int = YEAR_END
    ) -> list[dict]:
        """Fetch one indicator for every country/aggregate in a single call
        (World Bank supports up to 32500 rows per page, comfortably above the
        ~5400 rows/25yrs * 217 countries this app ever requests)."""
        resp = self.session.get(
            f"{WORLD_BANK_API_BASE}/country/all/indicator/{indicator_code}",
            params={
                "format": "json",
                "date": f"{year_start}:{year_end}",
                "per_page": 20000,
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
        if len(payload) < 2 or payload[1] is None:
            logger.warning("No data returned for indicator %s", indicator_code)
            return []

        _, rows = payload
        records = []
        for row in rows:
            if row["value"] is None:
                continue
            records.append(
                {
                    "indicator_code": indicator_code,
                    "iso3": row["countryiso3code"],
                    "country_name": row["country"]["value"],
                    "year": int(row["date"]),
                    "value": float(row["value"]),
                }
            )
        logger.info("Fetched %d observations for indicator %s", len(records), indicator_code)
        return records
