import { useMemo } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
} from "recharts";

const CLUSTER_STYLE = {
  "Digital Leaders": { color: "var(--cluster-leaders)", shape: "circle" },
  Advancing: { color: "var(--cluster-advancing)", shape: "triangle" },
  Emerging: { color: "var(--cluster-emerging)", shape: "diamond" },
  Established: { color: "var(--cluster-established)", shape: "square" },
};
const CLUSTER_ORDER = ["Digital Leaders", "Established", "Advancing", "Emerging"];

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const row = payload[0].payload;
  return (
    <div className="custom-tooltip">
      <div className="tt-title">{row.name}</div>
      <div className="tt-row">{row.cluster_label}</div>
      <div className="tt-row">Composite score: {row.composite_score.toFixed(1)} / 100</div>
    </div>
  );
}

export default function ClusterScatter({ items }) {
  const byCluster = useMemo(() => {
    const groups = {};
    for (const item of items) {
      groups[item.cluster_label] = groups[item.cluster_label] || [];
      groups[item.cluster_label].push(item);
    }
    return groups;
  }, [items]);

  const counts = useMemo(() => {
    const c = {};
    for (const item of items) c[item.cluster_label] = (c[item.cluster_label] || 0) + 1;
    return c;
  }, [items]);

  if (!items || items.length === 0) {
    return <p className="loading">Clustering unavailable.</p>;
  }

  return (
    <div className="panel">
      <p className="panel-title">Digital readiness landscape</p>
      <p className="panel-subtitle">
        KMeans clustering (k=4) on internet use, mobile subscriptions, literacy and
        secondary enrollment; PCA projects the 4 indicators to 2D for plotting. Shape
        and color both carry cluster identity.
      </p>
      <ResponsiveContainer width="100%" height={380}>
        <ScatterChart margin={{ left: 4, right: 16, top: 8, bottom: 8 }}>
          <CartesianGrid stroke="var(--gridline)" />
          <XAxis
            type="number"
            dataKey="pca_x"
            name="PCA 1"
            stroke="var(--text-muted)"
            fontSize={12}
            tickLine={false}
          />
          <YAxis
            type="number"
            dataKey="pca_y"
            name="PCA 2"
            stroke="var(--text-muted)"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <ZAxis range={[60, 60]} />
          <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: "3 3" }} />
          {CLUSTER_ORDER.filter((label) => byCluster[label]).map((label) => (
            <Scatter
              key={label}
              name={label}
              data={byCluster[label]}
              fill={CLUSTER_STYLE[label].color}
              shape={CLUSTER_STYLE[label].shape}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
      <div className="chart-legend">
        {CLUSTER_ORDER.filter((label) => counts[label]).map((label) => (
          <span key={label}>
            <span className="swatch" style={{ background: CLUSTER_STYLE[label].color }} />
            {label} ({counts[label]})
          </span>
        ))}
      </div>
    </div>
  );
}
