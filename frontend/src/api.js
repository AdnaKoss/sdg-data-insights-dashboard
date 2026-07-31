const BASE = "/api";

async function getJson(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  indicators: () => getJson("/indicators"),
  countries: () => getJson("/countries"),
  summary: (indicator) => getJson(`/data/summary?indicator=${encodeURIComponent(indicator)}`),
  ranking: (indicator, topN, region) => {
    const params = new URLSearchParams({ indicator, top_n: topN });
    if (region) params.set("region", region);
    return getJson(`/data/ranking?${params}`);
  },
  improvers: (indicator, yearsBack, topN) => {
    const params = new URLSearchParams({
      indicator,
      years_back: yearsBack,
      top_n: topN,
    });
    return getJson(`/data/improvers?${params}`);
  },
  clusters: () => getJson("/analysis/clusters"),
  trend: (indicator, country, forecastYears = 5) => {
    const params = new URLSearchParams({
      indicator,
      country,
      forecast_years: forecastYears,
    });
    return getJson(`/analysis/trend?${params}`);
  },
  policyBriefUrl: (indicator, topN, yearsBack, format) => {
    const params = new URLSearchParams({
      indicator,
      top_n: topN,
      years_back: yearsBack,
      format,
    });
    return `${BASE}/reports/policy-brief?${params}`;
  },
};
