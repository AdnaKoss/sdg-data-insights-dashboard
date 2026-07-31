export default function FilterBar({
  indicators,
  indicator,
  onIndicatorChange,
  regions,
  region,
  onRegionChange,
  topN,
  onTopNChange,
  yearsBack,
  onYearsBackChange,
}) {
  return (
    <div className="panel">
      <div className="filter-bar">
        <div className="filter-field">
          <label htmlFor="indicator-select">Indicator</label>
          <select
            id="indicator-select"
            value={indicator}
            onChange={(e) => onIndicatorChange(e.target.value)}
          >
            {indicators.map((ind) => (
              <option key={ind.code} value={ind.code}>
                {ind.name} ({ind.sdg})
              </option>
            ))}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="region-select">Region</label>
          <select
            id="region-select"
            value={region}
            onChange={(e) => onRegionChange(e.target.value)}
          >
            <option value="">All regions</option>
            {regions.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="topn-input">Top N countries</label>
          <input
            id="topn-input"
            type="number"
            min={3}
            max={15}
            value={topN}
            onChange={(e) => onTopNChange(Number(e.target.value))}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="years-input">Years back (movers)</label>
          <input
            id="years-input"
            type="number"
            min={3}
            max={24}
            value={yearsBack}
            onChange={(e) => onYearsBackChange(Number(e.target.value))}
          />
        </div>
      </div>
    </div>
  );
}
