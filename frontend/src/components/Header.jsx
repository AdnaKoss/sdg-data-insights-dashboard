export default function Header() {
  return (
    <header className="header">
      <span className="eyebrow">Data &amp; AI for Sustainable Development</span>
      <h1>SDG Data Insights Dashboard</h1>
      <p>
        World Bank Open Data on digital access, education, poverty and gender
        equality, with a KMeans digital-readiness clustering model and a
        linear trend forecast — built to practice the kind of evidence work
        (data analysis, indicator tracking, policy briefs) behind the SDGs.
      </p>
      <div className="sdg-tags">
        <span className="sdg-tag">SDG 1 — No Poverty</span>
        <span className="sdg-tag">SDG 4 — Quality Education</span>
        <span className="sdg-tag">SDG 5 — Gender Equality</span>
        <span className="sdg-tag">SDG 8 — Decent Work &amp; Economic Growth</span>
        <span className="sdg-tag">SDG 9 — Industry, Innovation &amp; Infrastructure</span>
      </div>
    </header>
  );
}
