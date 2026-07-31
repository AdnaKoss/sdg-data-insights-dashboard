import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from "recharts";

function CustomTooltip({ active, payload, unit }) {
  if (!active || !payload || !payload.length) return null;
  const row = payload[0].payload;
  const sign = row.abs_change >= 0 ? "+" : "";
  return (
    <div className="custom-tooltip">
      <div className="tt-title">{row.name}</div>
      <div className="tt-row">
        {sign}
        {row.abs_change.toFixed(1)} {unit} ({row.start_year} → {row.end_year})
      </div>
      <div className="tt-row">
        {row.start_value.toFixed(1)} → {row.end_value.toFixed(1)}
      </div>
    </div>
  );
}

export default function ImproversChart({ data, unit, yearsBack, indicatorName }) {
  if (!data || data.length === 0) {
    return <p className="loading">No data for this selection.</p>;
  }

  const chartData = [...data].reverse();

  return (
    <div className="panel">
      <p className="panel-title">Fastest movers: {indicatorName}</p>
      <p className="panel-subtitle">Largest change over the last {yearsBack} years</p>
      <ResponsiveContainer width="100%" height={Math.max(220, chartData.length * 34)}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 24 }}>
          <CartesianGrid horizontal={false} stroke="var(--gridline)" />
          <XAxis type="number" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
          <YAxis
            type="category"
            dataKey="name"
            width={140}
            stroke="var(--text-muted)"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <ReferenceLine x={0} stroke="var(--baseline)" />
          <Tooltip content={<CustomTooltip unit={unit} />} cursor={{ fill: "rgba(0,0,0,0.04)" }} />
          <Bar dataKey="abs_change" radius={[0, 4, 4, 0]} maxBarSize={22}>
            {chartData.map((entry) => (
              <Cell
                key={entry.iso3}
                fill={entry.abs_change >= 0 ? "var(--status-good)" : "var(--status-critical)"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="chart-legend">
        <span><span className="swatch" style={{ background: "var(--status-good)" }} />Increase</span>
        <span><span className="swatch" style={{ background: "var(--status-critical)" }} />Decrease</span>
      </div>
    </div>
  );
}
