"""Pure-pandas analysis helpers (no plotting). Each returns a DataFrame/Series
so the numbers behind a chart can be inspected, tested and quoted in the README."""
from __future__ import annotations

import pandas as pd

from src.config import (BUCKET_ORDER, DIWALI, HIGHLIGHT_CITY, LOCKDOWN_END,
                        LOCKDOWN_START, POLLUTANTS)


def city_ranking(df: pd.DataFrame, min_days: int = 365) -> pd.DataFrame:
    """Median & mean AQI per city, for cities with at least `min_days` AQI readings."""
    g = df.dropna(subset=["AQI"]).groupby("City")["AQI"]
    out = g.agg(days="count", median="median", mean="mean", p95=lambda s: s.quantile(.95))
    return out[out["days"] >= min_days].sort_values("median", ascending=False)


def bucket_shares(df: pd.DataFrame, min_days: int = 365) -> pd.DataFrame:
    """% of days in each AQI bucket per city, sorted by share of 'Poor or worse'."""
    d = df.dropna(subset=["AQI_Bucket"])
    counts = d.groupby(["City", "AQI_Bucket"], observed=False).size().unstack(fill_value=0)
    counts = counts.reindex(columns=BUCKET_ORDER, fill_value=0)
    counts = counts[counts.sum(axis=1) >= min_days]
    shares = counts.div(counts.sum(axis=1), axis=0) * 100
    shares["poor_or_worse"] = shares[["Poor", "Very Poor", "Severe"]].sum(axis=1)
    return shares.sort_values("poor_or_worse", ascending=False)


def monthly_matrix(df: pd.DataFrame, city: str, col: str = "PM2.5") -> pd.DataFrame:
    """Year x Month matrix of mean `col` for one city."""
    d = df[df["City"] == city].dropna(subset=[col])
    return d.pivot_table(index="Year", columns="Month", values=col, aggfunc="mean")


def season_means(df: pd.DataFrame, city: str, col: str = "PM2.5") -> pd.Series:
    d = df[df["City"] == city].dropna(subset=[col])
    return d.groupby("Season")[col].mean()


def annual_means(df: pd.DataFrame, col: str = "PM2.5", min_days: int = 240) -> pd.DataFrame:
    """City x Year mean of `col`, keeping only city-years with >= min_days of data
    (avoids comparing a full year against a few weeks)."""
    d = df.dropna(subset=[col])
    g = d.groupby(["City", "Year"])[col].agg(["mean", "count"]).reset_index()
    g = g[g["count"] >= min_days]
    return g.pivot(index="Year", columns="City", values="mean")


def diwali_window(df: pd.DataFrame, city: str = HIGHLIGHT_CITY, col: str = "PM2.5",
                  before: int = 10, after: int = 10) -> pd.DataFrame:
    """Rows = day offset from Diwali (-before..+after), columns = year."""
    d = df[df["City"] == city].set_index("Date")[col]
    rows = {}
    for year, day in DIWALI.items():
        day = pd.Timestamp(day)
        w = d.loc[day - pd.Timedelta(days=before): day + pd.Timedelta(days=after)]
        if len(w) < (before + after + 1) * 0.6:       # too many gaps -> skip the year
            continue
        w.index = (w.index - day).days
        rows[year] = w
    return pd.DataFrame(rows).reindex(range(-before, after + 1))


def diwali_bump(window: pd.DataFrame) -> dict:
    """Mean PM2.5 on the 2 days after Diwali vs the pre-festival baseline (days -10..-4)."""
    base = window.loc[-10:-4].mean().mean()
    peak = window.loc[1:2].mean().mean()
    return {"baseline": base, "post_diwali": peak, "ratio": peak / base if base else float("nan"),
            "years_used": list(window.columns)}


def lockdown_change(df: pd.DataFrame, col: str = "PM2.5", min_days: int = 30) -> pd.DataFrame:
    """% change in mean `col` for the 2020 lockdown window vs the same dates in 2019.

    Same calendar window in the previous year controls (roughly) for season.
    Cities need >= min_days valid readings in BOTH windows."""
    def window(year: int) -> pd.Series:
        s = pd.Timestamp(LOCKDOWN_START).replace(year=year)
        e = pd.Timestamp(LOCKDOWN_END).replace(year=year)
        d = df[(df["Date"] >= s) & (df["Date"] <= e)].dropna(subset=[col])
        return d.groupby("City")[col].agg(["mean", "count"])
    a, b = window(2019), window(2020)
    m = a.join(b, lsuffix="_2019", rsuffix="_2020", how="inner")
    m = m[(m["count_2019"] >= min_days) & (m["count_2020"] >= min_days)]
    m["pct_change"] = (m["mean_2020"] / m["mean_2019"] - 1) * 100
    return m.sort_values("pct_change")


def pollutant_corr(df: pd.DataFrame, min_obs: int = 2000) -> pd.DataFrame:
    cols = [c for c in POLLUTANTS + ["AQI"] if c in df.columns and df[c].notna().sum() >= min_obs]
    return df[cols].corr(method="spearman")
