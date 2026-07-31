import pytest

from app.analysis import clustering, stats, trend


def test_latest_values_picks_most_recent_year(synthetic_readiness_data, synthetic_countries):
    latest = stats.latest_values(synthetic_readiness_data, "IT.NET.USER.ZS", synthetic_countries)
    assert set(latest["iso3"]) == {"AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH"}
    assert (latest["year"] == 2023).all()


def test_ranking_orders_descending_by_default(synthetic_readiness_data, synthetic_countries):
    ranked = stats.ranking(synthetic_readiness_data, "IT.NET.USER.ZS", synthetic_countries, top_n=3)
    assert len(ranked) == 3
    assert ranked.iloc[0]["value"] >= ranked.iloc[1]["value"] >= ranked.iloc[2]["value"]
    assert ranked.iloc[0]["iso3"] in {"AAA", "BBB", "CCC", "DDD"}


def test_ranking_region_filter(synthetic_readiness_data, synthetic_countries):
    # all synthetic countries share region "Testland"; filtering to a region
    # with no matches should return an empty frame, not raise.
    ranked = stats.ranking(
        synthetic_readiness_data, "IT.NET.USER.ZS", synthetic_countries, region="Nowhere"
    )
    assert ranked.empty


def test_change_over_period_computes_delta():
    import pandas as pd

    rows = [
        {"indicator_code": "X", "iso3": "AAA", "country_name": "AAA", "year": 2010, "value": 10.0},
        {"indicator_code": "X", "iso3": "AAA", "country_name": "AAA", "year": 2020, "value": 40.0},
    ]
    df = pd.DataFrame(rows)
    countries = pd.DataFrame(
        [{"iso3": "AAA", "name": "AAA", "region": "Testland", "income_level": "High income"}]
    )
    result = stats.change_over_period(df, "X", countries, years_back=10, top_n=5)
    assert len(result) == 1
    assert result.iloc[0]["abs_change"] == pytest.approx(30.0)
    assert result.iloc[0]["pct_change"] == pytest.approx(300.0)


def test_summary_kpis_reports_coverage(synthetic_readiness_data, synthetic_countries):
    kpis = stats.summary_kpis(synthetic_readiness_data, "IT.NET.USER.ZS", synthetic_countries)
    assert kpis["countries_covered"] == 8
    assert kpis["min"] == 10.0
    assert kpis["max"] == 90.0


def test_cluster_countries_separates_high_and_low_groups(
    synthetic_readiness_data, synthetic_countries
):
    result = clustering.cluster_countries(synthetic_readiness_data, synthetic_countries, n_clusters=2)
    assert len(result) == 8

    high = result[result["iso3"].isin(["AAA", "BBB", "CCC", "DDD"])]
    low = result[result["iso3"].isin(["EEE", "FFF", "GGG", "HHH"])]
    assert high["cluster_label"].nunique() == 1
    assert low["cluster_label"].nunique() == 1
    assert high["cluster_label"].iloc[0] != low["cluster_label"].iloc[0]
    assert high["composite_score"].min() > low["composite_score"].max()


def test_cluster_countries_raises_when_too_few_countries(
    synthetic_readiness_data, synthetic_countries
):
    with pytest.raises(ValueError):
        clustering.cluster_countries(synthetic_readiness_data, synthetic_countries, n_clusters=20)


def test_trend_forecast_with_enough_points():
    import pandas as pd

    rows = [
        {"indicator_code": "X", "iso3": "AAA", "country_name": "AAA", "year": y, "value": 10.0 + i}
        for i, y in enumerate(range(2015, 2023))
    ]
    df = pd.DataFrame(rows)
    result = trend.trend_forecast(df, "X", "AAA", forecast_years=3)

    assert result["available"] is True
    assert len(result["forecast"]) == 3
    assert result["slope_per_year"] == pytest.approx(1.0, abs=0.01)
    assert result["r2"] > 0.99


def test_trend_forecast_with_too_few_points():
    import pandas as pd

    df = pd.DataFrame(
        [{"indicator_code": "X", "iso3": "AAA", "country_name": "AAA", "year": 2020, "value": 10.0}]
    )
    result = trend.trend_forecast(df, "X", "AAA")
    assert result["available"] is False
    assert "reason" in result
