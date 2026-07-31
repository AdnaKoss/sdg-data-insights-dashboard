from pydantic import BaseModel


class IndicatorMeta(BaseModel):
    code: str
    name: str
    unit: str
    category: str
    sdg: str
    sdg_label: str
    higher_is_better: bool


class Country(BaseModel):
    iso3: str
    iso2: str
    name: str
    region: str
    income_level: str
    capital_city: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class DataPoint(BaseModel):
    indicator_code: str
    iso3: str
    country_name: str
    year: int
    value: float


class RankingItem(BaseModel):
    iso3: str
    name: str
    region: str
    income_level: str
    year: int
    value: float


class ImproverItem(BaseModel):
    iso3: str
    name: str
    region: str
    start_year: int
    start_value: float
    end_year: int
    end_value: float
    abs_change: float
    pct_change: float | None = None


class SummaryKpis(BaseModel):
    countries_covered: int
    mean: float | None = None
    median: float | None = None
    min: float | None = None
    max: float | None = None
    latest_year_max: int | None = None


class ClusterItem(BaseModel):
    iso3: str
    name: str
    region: str
    income_level: str
    composite_score: float
    cluster_id: int
    cluster_label: str
    pca_x: float
    pca_y: float
    values: dict[str, float]


class ClusterResponse(BaseModel):
    n_clusters: int
    countries_included: int
    items: list[ClusterItem]


class TrendPoint(BaseModel):
    year: int
    value: float


class TrendResponse(BaseModel):
    iso3: str
    indicator_code: str
    available: bool
    reason: str | None = None
    history: list[TrendPoint] = []
    forecast: list[TrendPoint] = []
    slope_per_year: float | None = None
    r2: float | None = None
    method: str | None = None
    disclaimer: str | None = None


class RefreshResponse(BaseModel):
    countries: int
    indicators_fetched: int
    observations: int
