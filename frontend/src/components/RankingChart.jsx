import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

function CustomTooltip({ active, payload, unit }) {
  if (!active || !payload || !payload.length) return null;
  const row = payload[0].payload;
  return (
    <div className="custom-tooltip">
      <div className="tt-title">{row.name}</div>
      <div className="tt-row">
        {row.value.toLocaleString(undefined, { maximumFractionDigits: 1 })} {unit}
      </div>
      <div className="tt-row">{row.region}</div>
    </div>
  );
}

export default function RankingChart({ data, unit, indicatorName }) {
  if (!data || data.length === 0) {
    return <p className="loading">No data for this selection.</p>;
  }

  const chartData = [...data].reverse(); // Recharts vertical bar draws bottom-up

  return (
    <div className="panel">
      <p className="panel-title">Top {data.length}: {indicatorName}</p>
      <p className="panel-subtitle">Most recent available value per country, {unit}</p>
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
          <Tooltip content={<CustomTooltip unit={unit} />} cursor={{ fill: "rgba(0,0,0,0.04)" }} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={22}>
            {chartData.map((entry) => (
              <Cell key={entry.iso3} fill="var(--series-blue)" />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
