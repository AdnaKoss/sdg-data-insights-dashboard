"""Static-ish reference data: which indicators exist and which countries we have."""

from fastapi import APIRouter, Depends
import pandas as pd

from app.config import INDICATORS
from app.deps import get_countries_df
from app.schemas import Country, IndicatorMeta

router = APIRouter(prefix="/api", tags=["catalogue"])


@router.get("/indicators", response_model=list[IndicatorMeta])
def list_indicators():
    return [{"code": code, **meta} for code, meta in INDICATORS.items()]


@router.get("/countries", response_model=list[Country])
def list_countries(countries_df: pd.DataFrame = Depends(get_countries_df)):
    # A handful of territories have no capital_city/iso2 in the World Bank
    # data; pandas reads those blanks as NaN, which Pydantic's Optional[str]
    # rejects (NaN is a float, not a string or None).
    clean = countries_df.astype(object).where(countries_df.notna(), None)
    return clean.to_dict(orient="records")
