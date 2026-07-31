"""
Auto-generates a short policy brief (Markdown + PDF) from the cached World
Bank data: a ranking table, top improvers over the last decade, the digital
readiness cluster landscape, and a templated narrative tying it back to the
relevant SDG target. This is the "knowledge product" piece of the dashboard —
the kind of quick evidence summary a policy/programme team drafts before a
country brief or portfolio review.

The narrative is deterministic (string templates over computed numbers), not
LLM-generated: every sentence is directly traceable to a number in the
tables above it, which matters more than prose polish for this use case.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone

import matplotlib

matplotlib.use("Agg")  # no display available in a server/container context
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF, XPos, YPos

from app.analysis import clustering, stats
from app.config import INDICATORS

DEFAULT_TOP_N = 5
DEFAULT_YEARS_BACK = 10


def build_brief(
    df: pd.DataFrame,
    countries_df: pd.DataFrame,
    indicator_code: str,
    top_n: int = DEFAULT_TOP_N,
    years_back: int = DEFAULT_YEARS_BACK,
) -> dict:
    if indicator_code not in INDICATORS:
        raise ValueError(f"Unknown indicator: {indicator_code}")

    meta = INDICATORS[indicator_code]
    kpis = stats.summary_kpis(df, indicator_code, countries_df)
    ranked = stats.ranking(df, indicator_code, countries_df, top_n=top_n)
    improvers = stats.change_over_period(
        df, indicator_code, countries_df, years_back=years_back, top_n=top_n
    )

    try:
        clustered = clustering.cluster_countries(df, countries_df)
        cluster_counts = clustered["cluster_label"].value_counts().to_dict()
        cluster_leaders = clustered.head(top_n)[["name", "composite_score", "cluster_label"]]
    except ValueError:
        clustered, cluster_counts, cluster_leaders = None, {}, None

    narrative = _build_narrative(meta, kpis, ranked, improvers, cluster_counts, years_back)

    return {
        "indicator_code": indicator_code,
        "indicator": meta,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kpis": kpis,
        "ranking": ranked,
        "improvers": improvers,
        "clustered": clustered,
        "cluster_counts": cluster_counts,
        "cluster_leaders": cluster_leaders,
        "narrative": narrative,
        "years_back": years_back,
        "top_n": top_n,
    }


def _build_narrative(meta, kpis, ranked, improvers, cluster_counts, years_back) -> list[str]:
    paragraphs = []

    if not ranked.empty:
        leaders = ranked.head(3)["name"].tolist()
        top_value = ranked.iloc[0]["value"]
        paragraphs.append(
            f"As of {kpis.get('latest_year_max', 'the latest reporting year')}, "
            f"{leaders[0]} leads on {meta['name'].lower()} ({top_value:g}{_unit_suffix(meta)}), "
            f"followed by {', '.join(leaders[1:])}. The comparison covers "
            f"{kpis.get('countries_covered', 0)} economies with World Bank data available."
        )

    if not improvers.empty:
        best = improvers.iloc[0]
        direction = "increase" if best["abs_change"] >= 0 else "decrease"
        paragraphs.append(
            f"Over the {years_back} years to {int(best['end_year'])}, the fastest progress came "
            f"from {best['name']}, a {abs(best['abs_change']):.1f}-point {direction} "
            f"({best['start_value']:.1f} → {best['end_value']:.1f}). "
            f"This kind of rapid movement is where targeted digital/education programming "
            f"tends to show up first in the data."
        )

    if cluster_counts:
        leaders_n = cluster_counts.get("Digital Leaders", 0)
        emerging_n = cluster_counts.get("Emerging", 0)
        paragraphs.append(
            f"Clustering countries on internet use, mobile subscriptions, literacy and "
            f"secondary enrollment places {leaders_n} economies in the 'Digital Leaders' "
            f"group and {emerging_n} in 'Emerging' — the gap between these groups is the "
            f"practical target for digital-inclusion investment."
        )

    paragraphs.append(
        f"This indicator maps to {meta['sdg']} ({meta['sdg_label']}). Reducing the spread "
        f"between the highest- and lowest-performing economies is central to the 2030 "
        f"Agenda's commitment to leave no one behind."
    )
    return paragraphs


def _unit_suffix(meta: dict) -> str:
    unit = meta["unit"]
    return "%" if unit.startswith("%") else f" {unit}"


# --------------------------------------------------------------------------
# Markdown rendering — text + tables, no embedded images (keeps the file
# small, portable, and readable in any Markdown viewer or plain text editor).
# --------------------------------------------------------------------------


def render_markdown(brief: dict) -> str:
    meta = brief["indicator"]
    lines = [
        f"# Policy Brief: {meta['name']} ({meta['sdg']})",
        "",
        f"*Generated {brief['generated_at']} from World Bank Open Data — "
        f"SDG Data Insights Dashboard*",
        "",
        "## Summary",
        "",
        *[f"- {p}" for p in brief["narrative"]],
        "",
        f"## Top {brief['top_n']} — {meta['name']} ({meta['unit']})",
        "",
        _markdown_table(
            brief["ranking"],
            columns=["name", "region", "year", "value"],
            headers=["Country", "Region", "Year", "Value"],
        ),
        "",
        f"## Fastest movers — last {brief['years_back']} years",
        "",
        _markdown_table(
            brief["improvers"],
            columns=["name", "start_year", "start_value", "end_year", "end_value", "abs_change"],
            headers=["Country", "From", "Start", "To", "End", "Change"],
        ),
        "",
    ]

    if brief["cluster_leaders"] is not None:
        lines += [
            "## Digital readiness landscape",
            "",
            "Countries clustered on internet use, mobile subscriptions, literacy and "
            "secondary enrollment (KMeans, k=4):",
            "",
            *[f"- **{label}**: {count} countries" for label, count in brief["cluster_counts"].items()],
            "",
            "Top-scoring countries overall:",
            "",
            _markdown_table(
                brief["cluster_leaders"],
                columns=["name", "composite_score", "cluster_label"],
                headers=["Country", "Composite score (0-100)", "Cluster"],
            ),
            "",
        ]

    lines.append(
        "---\n*Source: World Bank Open Data (api.worldbank.org). Narrative is "
        "template-generated directly from the tables above, not editorialized.*"
    )
    return "\n".join(lines)


def _markdown_table(df: pd.DataFrame, columns: list[str], headers: list[str]) -> str:
    if df is None or df.empty:
        return "_No data available._"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for _, row in df.iterrows():
        cells = []
        for col in columns:
            val = row[col]
            cells.append(f"{val:.1f}" if isinstance(val, float) else str(val))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


# --------------------------------------------------------------------------
# PDF rendering — narrative + tables + charts, for sharing/printing.
# --------------------------------------------------------------------------


def render_pdf(brief: dict) -> bytes:
    charts = _build_charts(brief)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    meta = brief["indicator"]
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 8, f"Policy Brief: {meta['name']} ({meta['sdg']})")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(110, 110, 110)
    pdf.cell(
        0,
        6,
        f"Generated {brief['generated_at'][:10]} - SDG Data Insights Dashboard",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Summary", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    for paragraph in brief["narrative"]:
        pdf.multi_cell(0, 6, _pdf_safe(f"- {paragraph}"))
        pdf.ln(1)
    pdf.ln(2)

    if "ranking" in charts:
        pdf.image(charts["ranking"], w=170)
        pdf.ln(4)

    if "improvers" in charts:
        pdf.image(charts["improvers"], w=170)
        pdf.ln(4)

    if "cluster" in charts:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Digital readiness landscape", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.image(charts["cluster"], w=170)

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(130, 130, 130)
    pdf.ln(4)
    pdf.multi_cell(0, 5, "Source: World Bank Open Data (api.worldbank.org).")

    return bytes(pdf.output())


def _pdf_safe(text: str) -> str:
    """fpdf2's built-in Helvetica font is latin-1 only; swap the few
    typographic characters the narrative templates use for ASCII."""
    return (
        text.replace("→", "->")
        .replace("’", "'")
        .replace("‘", "'")
        .replace("–", "-")
        .replace("—", "-")
    )


def _build_charts(brief: dict) -> dict[str, io.BytesIO]:
    charts = {}
    meta = brief["indicator"]

    if not brief["ranking"].empty:
        fig, ax = plt.subplots(figsize=(7, 3.2))
        data = brief["ranking"].iloc[::-1]
        ax.barh(data["name"], data["value"], color="#2f6f4f")
        ax.set_xlabel(meta["unit"])
        ax.set_title(f"Top {brief['top_n']}: {meta['name']}")
        fig.tight_layout()
        charts["ranking"] = _fig_to_buffer(fig)

    if not brief["improvers"].empty:
        fig, ax = plt.subplots(figsize=(7, 3.2))
        data = brief["improvers"].iloc[::-1]
        colors = ["#2f6f4f" if v >= 0 else "#b23a48" for v in data["abs_change"]]
        ax.barh(data["name"], data["abs_change"], color=colors)
        ax.set_xlabel(f"Change over {brief['years_back']} years")
        ax.set_title("Fastest movers")
        fig.tight_layout()
        charts["improvers"] = _fig_to_buffer(fig)

    if brief["clustered"] is not None:
        fig, ax = plt.subplots(figsize=(7, 4.2))
        palette = {
            "Digital Leaders": "#2f6f4f",
            "Established": "#4a8fd1",
            "Advancing": "#e0a52c",
            "Emerging": "#b23a48",
        }
        for label, group in brief["clustered"].groupby("cluster_label"):
            ax.scatter(
                group["pca_x"],
                group["pca_y"],
                label=label,
                s=28,
                alpha=0.8,
                color=palette.get(label, "#888888"),
            )
        ax.set_xlabel("PCA component 1")
        ax.set_ylabel("PCA component 2")
        ax.set_title("Digital readiness clusters (KMeans, k=4)")
        ax.legend(fontsize=8)
        fig.tight_layout()
        charts["cluster"] = _fig_to_buffer(fig)

    return charts


def _fig_to_buffer(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf
