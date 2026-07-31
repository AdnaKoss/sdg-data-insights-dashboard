import { api } from "../api.js";

export default function PolicyBriefPanel({ indicator, indicatorName, topN, yearsBack }) {
  const pdfUrl = api.policyBriefUrl(indicator, topN, yearsBack, "pdf");
  const mdUrl = api.policyBriefUrl(indicator, topN, yearsBack, "md");

  return (
    <div className="panel">
      <p className="panel-title">Auto-generated policy brief</p>
      <p className="panel-subtitle">
        A ready-to-share brief for <strong>{indicatorName}</strong>: top {topN}
        ranking, fastest movers over {yearsBack} years, the digital-readiness cluster
        breakdown, and a short templated narrative — every sentence traceable to a
        number in the tables above it.
      </p>
      <div className="brief-actions">
        <a className="brief-btn" href={pdfUrl}>
          Download PDF
        </a>
        <a className="brief-btn secondary" href={mdUrl}>
          Download Markdown
        </a>
      </div>
    </div>
  );
}
