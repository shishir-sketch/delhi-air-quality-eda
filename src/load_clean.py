"""Loading and light cleaning of CPCB's city_day.csv."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import BUCKET_ORDER, POLLUTANTS, SEASON_OF_MONTH

REQUIRED = {"City", "Date", "AQI", "AQI_Bucket"}


def load_raw(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {sorted(missing)}")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return a tidy copy: typed dates, derived calendar columns, no empty rows.

    Deliberately *no imputation*: pollution data is missing for real reasons
    (stations offline, cities added later) and filling it would invent signal.
    Each analysis drops NaNs locally and states its own coverage threshold.
    """
    out = df.copy()
    out["Date"] = pd.to_datetime(out["Date"], errors="coerce")
    out = out.dropna(subset=["Date", "City"])
    out["City"] = out["City"].astype(str).str.strip()

    measured = [c for c in POLLUTANTS + ["AQI"] if c in out.columns]
    out = out.dropna(subset=measured, how="all")      # rows with no measurement at all
    out = out.drop_duplicates(subset=["City", "Date"])

    out["Year"] = out["Date"].dt.year
    out["Month"] = out["Date"].dt.month
    out["Season"] = out["Month"].map(SEASON_OF_MONTH)
    out["AQI_Bucket"] = pd.Categorical(out["AQI_Bucket"], categories=BUCKET_ORDER, ordered=True)
    return out.sort_values(["City", "Date"]).reset_index(drop=True)


def load_clean(path: str | Path) -> pd.DataFrame:
    return clean(load_raw(path))


def coverage_by_city_year(df: pd.DataFrame, col: str = "PM2.5") -> pd.DataFrame:
    """Number of days with a valid `col` reading per city and year."""
    return (df.dropna(subset=[col]).groupby(["City", "Year"]).size()
              .unstack(fill_value=0))
