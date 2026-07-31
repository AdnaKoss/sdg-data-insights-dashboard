import { useEffect, useMemo, useState } from "react";
import { api } from "./api.js";
import Header from "./components/Header.jsx";
import FilterBar from "./components/FilterBar.jsx";
import KpiCards from "./components/KpiCards.jsx";
import RankingChart from "./components/RankingChart.jsx";
import ImproversChart from "./components/ImproversChart.jsx";
import TrendPanel from "./components/TrendPanel.jsx";
import ClusterScatter from "./components/ClusterScatter.jsx";
import PolicyBriefPanel from "./components/PolicyBriefPanel.jsx";

const DEFAULT_INDICATOR = "IT.NET.USER.ZS";
const DEFAULT_TREND_COUNTRY = "USA";

export default function App() {
  const [indicators, setIndicators] = useState([]);
  const [countries, setCountries] = useState([]);
  const [clusterItems, setClusterItems] = useState([]);

  const [indicator, setIndicator] = useState(DEFAULT_INDICATOR);
  const [region, setRegion] = useState("");
  const [topN, setTopN] = useState(8);
  const [yearsBack, setYearsBack] = useState(10);
  const [trendCountry, setTrendCountry] = useState(DEFAULT_TREND_COUNTRY);

  const [summary, setSummary] = useState(null);
  const [ranking, setRanking] = useState([]);
  const [improvers, setImprovers] = useState([]);
  const [trend, setTrend] = useState(null);

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load reference data once.
  useEffect(() => {
    Promise.all([api.indicators(), api.countries(), api.clusters()])
      .then(([indicatorsRes, countriesRes, clustersRes]) => {
        setIndicators(indicatorsRes);
        setCountries(countriesRes);
        setClusterItems(clustersRes.items);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  // Re-fetch indicator-dependent data whenever the filters change.
  useEffect(() => {
    let cancelled = false;
    setError(null);
    Promise.all([
      api.summary(indicator),
      api.ranking(indicator, topN, region || undefined),
      api.improvers(indicator, yearsBack, topN),
    ])
      .then(([summaryRes, rankingRes, improversRes]) => {
        if (cancelled) return;
        setSummary(summaryRes);
        setRanking(rankingRes);
        setImprovers(improversRes);
      })
      .catch((e) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [indicator, region, topN, yearsBack]);

  // Trend depends on indicator + selected country.
  useEffect(() => {
    let cancelled = false;
    api
      .trend(indicator, trendCountry)
      .then((res) => !cancelled && setTrend(res))
      .catch((e) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [indicator, trendCountry]);

  const indicatorMeta = useMemo(
    () => indicators.find((i) => i.code === indicator),
    [indicators, indicator]
  );
  const regions = useMemo(
    () => [...new Set(countries.map((c) => c.region))].sort(),
    [countries]
  );
  const sortedCountries = useMemo(
    () => [...countries].sort((a, b) => a.name.localeCompare(b.name)),
    [countries]
  );

  if (loading) {
    return (
      <div className="app">
        <Header />
        <p className="loading">Loading dataset…</p>
      </div>
    );
  }

  return (
    <div className="app">
      <Header />

      {error && <p className="error-text">Error: {error}</p>}

      <FilterBar
        indicators={indicators}
        indicator={indicator}
        onIndicatorChange={setIndicator}
        regions={regions}
        region={region}
        onRegionChange={setRegion}
        topN={topN}
        onTopNChange={setTopN}
        yearsBack={yearsBack}
        onYearsBackChange={setYearsBack}
      />

      <KpiCards summary={summary} unit={indicatorMeta?.unit ?? ""} />

      <div className="chart-grid">
        <RankingChart
          data={ranking}
          unit={indicatorMeta?.unit ?? ""}
          indicatorName={indicatorMeta?.name ?? indicator}
        />
        <ImproversChart
          data={improvers}
          unit={indicatorMeta?.unit ?? ""}
          yearsBack={yearsBack}
          indicatorName={indicatorMeta?.name ?? indicator}
        />
      </div>

      <TrendPanel
        countries={sortedCountries}
        selectedCountry={trendCountry}
        onCountryChange={setTrendCountry}
        trend={trend}
        unit={indicatorMeta?.unit ?? ""}
        indicatorName={indicatorMeta?.name ?? indicator}
      />

      <ClusterScatter items={clusterItems} />

      <PolicyBriefPanel
        indicator={indicator}
        indicatorName={indicatorMeta?.name ?? indicator}
        topN={topN}
        yearsBack={yearsBack}
      />

      <footer className="footer">
        Source: World Bank Open Data (api.worldbank.org). Digital-readiness clusters
        and trend forecasts are illustrative models built for this project, not
        official UN/World Bank statistics. Built as a portfolio project exploring
        data analysis and applied ML for sustainable-development questions.
      </footer>
    </div>
  );
}
