def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["data_loaded"] is True


def test_indicators_list(client):
    resp = client.get("/api/indicators")
    assert resp.status_code == 200
    codes = {item["code"] for item in resp.json()}
    assert "IT.NET.USER.ZS" in codes


def test_countries_list_and_namibia_iso2(client):
    resp = client.get("/api/countries")
    assert resp.status_code == 200
    countries = resp.json()
    assert len(countries) == 217

    namibia = next(c for c in countries if c["iso3"] == "NAM")
    assert namibia["iso2"] == "NA"  # pandas NA-string gotcha regression check


def test_ranking_endpoint_sorted_descending(client):
    resp = client.get("/api/data/ranking", params={"indicator": "IT.NET.USER.ZS", "top_n": 5})
    assert resp.status_code == 200
    values = [row["value"] for row in resp.json()]
    assert values == sorted(values, reverse=True)


def test_ranking_endpoint_unknown_indicator_404(client):
    resp = client.get("/api/data/ranking", params={"indicator": "NOT.REAL"})
    assert resp.status_code == 404


def test_summary_endpoint(client):
    resp = client.get("/api/data/summary", params={"indicator": "IT.NET.USER.ZS"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["countries_covered"] > 100


def test_improvers_endpoint(client):
    resp = client.get(
        "/api/data/improvers", params={"indicator": "IT.NET.USER.ZS", "years_back": 10, "top_n": 5}
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 5


def test_clusters_endpoint(client):
    resp = client.get("/api/analysis/clusters")
    assert resp.status_code == 200
    body = resp.json()
    assert body["countries_included"] > 100
    labels = {item["cluster_label"] for item in body["items"]}
    assert labels <= {"Emerging", "Advancing", "Established", "Digital Leaders"}


def test_trend_endpoint_available(client):
    resp = client.get(
        "/api/analysis/trend", params={"indicator": "IT.NET.USER.ZS", "country": "USA"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is True
    assert len(body["forecast"]) == 5


def test_trend_endpoint_unavailable_for_missing_country(client):
    resp = client.get(
        "/api/analysis/trend", params={"indicator": "IT.NET.USER.ZS", "country": "ZZZ"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is False


def test_policy_brief_markdown_download(client):
    resp = client.get(
        "/api/reports/policy-brief", params={"indicator": "IT.NET.USER.ZS", "format": "md"}
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/markdown")
    assert resp.text.startswith("# Policy Brief")


def test_policy_brief_pdf_download(client):
    resp = client.get(
        "/api/reports/policy-brief", params={"indicator": "IT.NET.USER.ZS", "format": "pdf"}
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")
