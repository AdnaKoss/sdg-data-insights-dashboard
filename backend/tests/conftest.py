import sys
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.data import cache  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def data_df() -> pd.DataFrame:
    return cache.load_indicator_data()


@pytest.fixture(scope="session")
def countries_df() -> pd.DataFrame:
    return cache.load_countries()


@pytest.fixture
def synthetic_readiness_data():
    """A small, hand-built panel with 8 countries clearly split into a
    "high" and "low" digital-readiness group, used to test clustering/stats
    logic deterministically without depending on the full real dataset."""
    rows = []
    high_countries = ["AAA", "BBB", "CCC", "DDD"]
    low_countries = ["EEE", "FFF", "GGG", "HHH"]
    for iso3 in high_countries:
        for code, val in [
            ("IT.NET.USER.ZS", 90.0),
            ("IT.CEL.SETS.P2", 120.0),
            ("SE.ADT.LITR.ZS", 98.0),
            ("SE.SEC.ENRR", 100.0),
        ]:
            rows.append(
                {"indicator_code": code, "iso3": iso3, "country_name": iso3, "year": 2023, "value": val}
            )
    for iso3 in low_countries:
        for code, val in [
            ("IT.NET.USER.ZS", 10.0),
            ("IT.CEL.SETS.P2", 30.0),
            ("SE.ADT.LITR.ZS", 40.0),
            ("SE.SEC.ENRR", 35.0),
        ]:
            rows.append(
                {"indicator_code": code, "iso3": iso3, "country_name": iso3, "year": 2023, "value": val}
            )
    return pd.DataFrame(rows)


@pytest.fixture
def synthetic_countries():
    rows = []
    for iso3 in ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH"]:
        rows.append(
            {
                "iso3": iso3,
                "iso2": iso3[:2],
                "name": iso3,
                "region": "Testland",
                "income_level": "High income",
                "capital_city": "Test City",
                "latitude": 0.0,
                "longitude": 0.0,
            }
        )
    return pd.DataFrame(rows)
