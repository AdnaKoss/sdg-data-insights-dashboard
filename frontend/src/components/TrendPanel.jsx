import { useMemo } from "react";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function CustomTooltip({ active, payload, label, unit }) {
  if (!active || !payload || !payload.length) return null;
  const actual = payload.find((p) => p.dataKey === "actual");
  const forecast = payload.find((p) => p.dataKey === "forecast");
  return (
    <div className="custom-tooltip">
      <div className="tt-title">{label}</div>
      {actual && actual.value != null && (
        <div className="tt-row">Actual: {actual.value.toFixed(1)} {unit}</div>
      )}
      {forecast && forecast.value != null && (
        <div className="tt-row">Forecast: {forecast.value.toFixed(1)} {unit}</div>
      )}
    </div>
  );
}

export default function TrendPanel({
  countries,
  selectedCountry,
  onCountryChange,
  trend,
  unit,
  indicatorName,
}) {
  const mergedData = useMemo(() => {
    if (!trend || !trend.available) return [];
    const rows = trend.history.map((h) => ({ year: h.year, actual: h.value }));
    if (trend.forecast.length && rows.length) {
      rows[rows.length - 1] = {
        ...rows[rows.length - 1],
        forecast: rows[rows.length - 1].actual,
      };
      trend.forecast.forEach((f) => rows.push({ year: f.year, forecast: f.value }));
    }
    return rows;
  }, [trend]);

  return (
    <div className="panel">
      <p className="panel-title">Trend &amp; forecast: {indicatorName}</p>
      <p className="panel-subtitle">
        Ordinary-least-squares trend line, extrapolated 5 years — illustrative, not a
        rigorous forecast.
      </p>

      <div className="filter-field" style={{ marginBottom: 14 }}>
        <label htmlFor="country-select">Country</label>
        <select
          id="country-select"
          value={selectedCountry}
          onChange={(e) => onCountryChange(e.target.value)}
        >
          {countries.map((c) => (
            <option key={c.iso3} value={c.iso3}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {trend && !trend.available && (
        <p className="loading">Not enough data points for this country ({trend.reason}).</p>
      )}

      {trend && trend.available && (
        <>
          <ResponsiveContainer width="100%" height={280}>
            <ComposedChart data={mergedData} margin={{ left: 4, right: 16, top: 8 }}>
              <CartesianGrid stroke="var(--gridline)" vertical={false} />
              <XAxis dataKey="year" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
              <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip unit={unit} />} />
              <Line
                type="monotone"
                dataKey="actual"
                stroke="var(--series-blue)"
                strokeWidth={2}
                dot={false}
                connectNulls
                name="Actual"
              />
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="var(--series-blue)"
                strokeWidth={2}
                strokeDasharray="5 4"
                dot={false}
                connectNulls
                name="Forecast"
              />
            </ComposedChart>
          </ResponsiveContainer>
          <div className="chart-legend">
            <span><span className="swatch" style={{ background: "var(--series-blue)" }} />Actual</span>
            <span>
              <span
                className="swatch"
                style={{
                  background:
                    "repeating-linear-gradient(90deg, var(--series-blue) 0 4px, transparent 4px 7px)",
                }}
              />
              Forecast (linear extrapolation)
            </span>
            <span>Slope: {trend.slope_per_year.toFixed(2)} {unit}/year · R² {trend.r2.toFixed(2)}</span>
          </div>
        </>
      )}
    </div>
  );
}
