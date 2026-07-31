"""
Unsupervised ML: group countries into "digital readiness" clusters using
KMeans over four indicators (internet use, mobile subscriptions, literacy,
secondary enrollment), with PCA reducing them to 2 dimensions for plotting.

Only countries with a value for all four indicators are included (~154 of
217 — literacy rate in particular is reported infrequently by many
countries), so the composite is never built from partially-missing data.
"""

from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from app.analysis.stats import latest_values
from app.config import CLUSTER_LABELS, DIGITAL_READINESS_INDICATORS, N_CLUSTERS


def _wide_readiness_table(df: pd.DataFrame, countries_df: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for code in DIGITAL_READINESS_INDICATORS:
        latest = latest_values(df, code, countries_df)[["iso3", "value"]].rename(
            columns={"value": code}
        )
        frames.append(latest.set_index("iso3"))

    wide = pd.concat(frames, axis=1, join="inner")  # inner join: complete rows only
    wide = wide.merge(
        countries_df[["iso3", "name", "region", "income_level"]].set_index("iso3"),
        left_index=True,
        right_index=True,
    )
    return wide.reset_index()


def cluster_countries(
    df: pd.DataFrame, countries_df: pd.DataFrame, n_clusters: int = N_CLUSTERS
) -> pd.DataFrame:
    """Returns one row per country with its 4 raw indicator values, a 0-100
    composite digital-readiness score, its KMeans cluster, a human-readable
    cluster label (ordered by mean composite score, so "Digital Leaders" is
    always the strongest cluster regardless of KMeans' arbitrary numbering),
    and 2D PCA coordinates for scatter-plotting."""
    wide = _wide_readiness_table(df, countries_df)
    if len(wide) < n_clusters:
        raise ValueError(
            f"Only {len(wide)} countries have complete digital-readiness data; "
            f"need at least {n_clusters} to form {n_clusters} clusters."
        )

    features = wide[DIGITAL_READINESS_INDICATORS].to_numpy()
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    composite = scaled.mean(axis=1)
    wide["composite_score"] = _rescale_0_100(composite)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    wide["cluster_id"] = kmeans.fit_predict(scaled)

    # Order cluster labels by mean composite score so they read intuitively.
    cluster_order = (
        wide.groupby("cluster_id")["composite_score"].mean().sort_values().index.tolist()
    )
    label_by_cluster = {
        cluster_id: CLUSTER_LABELS[rank] for rank, cluster_id in enumerate(cluster_order)
    }
    wide["cluster_label"] = wide["cluster_id"].map(label_by_cluster)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(scaled)
    wide["pca_x"] = coords[:, 0]
    wide["pca_y"] = coords[:, 1]

    return wide.sort_values("composite_score", ascending=False).reset_index(drop=True)


def _rescale_0_100(values):
    lo, hi = values.min(), values.max()
    if hi == lo:
        return [50.0] * len(values)
    return [round(float((v - lo) / (hi - lo) * 100), 1) for v in values]
