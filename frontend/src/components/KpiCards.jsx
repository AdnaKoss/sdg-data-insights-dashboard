function formatValue(v) {
  if (v === null || v === undefined) return "—";
  return Number(v).toLocaleString(undefined, { maximumFractionDigits: 1 });
}

export default function KpiCards({ summary, unit }) {
  if (!summary) return null;

  const cards = [
    { label: "Countries covered", value: summary.countries_covered },
    { label: `Mean (${unit})`, value: formatValue(summary.mean) },
    { label: `Median (${unit})`, value: formatValue(summary.median) },
    { label: `Min (${unit})`, value: formatValue(summary.min) },
    { label: `Max (${unit})`, value: formatValue(summary.max) },
    { label: "Latest data year", value: summary.latest_year_max },
  ];

  return (
    <div className="kpi-row">
      {cards.map((c) => (
        <div className="kpi-card" key={c.label}>
          <div className="kpi-label">{c.label}</div>
          <div className="kpi-value">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
