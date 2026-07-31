"""Downloadable policy brief endpoint (Markdown or PDF)."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.config import INDICATORS
from app.deps import get_countries_df, get_data_df
from app.reports import policy_brief

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/policy-brief")
def get_policy_brief(
    indicator: str = Query(...),
    top_n: int = Query(5, ge=3, le=15),
    years_back: int = Query(10, ge=1, le=24),
    format: str = Query("pdf", pattern="^(pdf|md)$"),
    df: pd.DataFrame = Depends(get_data_df),
    countries_df: pd.DataFrame = Depends(get_countries_df),
):
    if indicator not in INDICATORS:
        raise HTTPException(status_code=404, detail=f"Unknown indicator: {indicator}")

    brief = policy_brief.build_brief(df, countries_df, indicator, top_n=top_n, years_back=years_back)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"policy-brief-{indicator}-{stamp}.{format}"

    if format == "md":
        content = policy_brief.render_markdown(brief)
        media_type = "text/markdown"
    else:
        content = policy_brief.render_pdf(brief)
        media_type = "application/pdf"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
