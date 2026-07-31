from unittest.mock import MagicMock, patch

from app.data.worldbank_client import WorldBankClient

COUNTRY_LIST_RESPONSE = [
    {"page": 1, "pages": 1, "per_page": 400, "total": 2},
    [
        {
            "id": "USA",
            "iso2Code": "US",
            "name": "United States",
            "region": {"id": "NAC", "iso2code": "XU", "value": "North America"},
            "incomeLevel": {"id": "HIC", "iso2code": "XD", "value": "High income"},
            "capitalCity": "Washington D.C.",
            "longitude": "-77.032",
            "latitude": "38.8895",
        },
        {
            "id": "ZH",
            "iso2Code": "ZH",
            "name": "Africa Eastern and Southern",
            "region": {"id": "NA", "iso2code": "NA", "value": "Aggregates"},
            "incomeLevel": {"id": "NA", "iso2code": "NA", "value": "Aggregates"},
            "capitalCity": "",
            "longitude": "",
            "latitude": "",
        },
    ],
]

INDICATOR_RESPONSE = [
    {"page": 1, "pages": 1, "per_page": 20000, "total": 3},
    [
        {
            "indicator": {"id": "IT.NET.USER.ZS", "value": "Internet users"},
            "country": {"id": "US", "value": "United States"},
            "countryiso3code": "USA",
            "date": "2023",
            "value": 91.5,
        },
        {
            "indicator": {"id": "IT.NET.USER.ZS", "value": "Internet users"},
            "country": {"id": "US", "value": "United States"},
            "countryiso3code": "USA",
            "date": "2022",
            "value": None,  # should be dropped
        },
        {
            "indicator": {"id": "IT.NET.USER.ZS", "value": "Internet users"},
            "country": {"id": "FR", "value": "France"},
            "countryiso3code": "FRA",
            "date": "2023",
            "value": 88.0,
        },
    ],
]


def _mock_response(payload):
    resp = MagicMock()
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def test_fetch_countries_excludes_aggregates():
    client = WorldBankClient()
    with patch.object(client.session, "get", return_value=_mock_response(COUNTRY_LIST_RESPONSE)):
        countries = client.fetch_countries()

    assert len(countries) == 1
    assert countries[0]["iso3"] == "USA"
    assert countries[0]["region"] == "North America"


def test_fetch_indicator_drops_null_values():
    client = WorldBankClient()
    with patch.object(client.session, "get", return_value=_mock_response(INDICATOR_RESPONSE)):
        records = client.fetch_indicator("IT.NET.USER.ZS")

    assert len(records) == 2
    assert all(r["value"] is not None for r in records)
    usa_record = next(r for r in records if r["iso3"] == "USA")
    assert usa_record["year"] == 2023
    assert usa_record["value"] == 91.5


def test_fetch_indicator_handles_empty_payload():
    client = WorldBankClient()
    empty_payload = [{"page": 1, "pages": 1, "per_page": 1, "total": 0}, None]
    with patch.object(client.session, "get", return_value=_mock_response(empty_payload)):
        records = client.fetch_indicator("SOME.CODE")

    assert records == []
