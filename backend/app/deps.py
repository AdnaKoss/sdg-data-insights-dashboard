"""FastAPI dependencies that hand routers the in-memory dataframes loaded at
startup (and replaced in place by the /api/admin/refresh-data endpoint)."""

from __future__ import annotations

import pandas as pd
from fastapi import Request


def get_data_df(request: Request) -> pd.DataFrame:
    return request.app.state.data_df


def get_countries_df(request: Request) -> pd.DataFrame:
    return request.app.state.countries_df
