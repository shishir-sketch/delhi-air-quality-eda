"""Compute headline numbers and write them to a markdown file.

The README's 'Key findings' should be copied from this output, so every number
in the write-up is reproducible from code rather than typed by hand.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import analysis as an
from src.config import HIGHLIGHT_CITY


def compute(df: pd.DataFrame, city: str = HIGHLIGHT_CITY) -> dict:
    f: dict = {}
    f["rows"], f["cities"] = len(df), df["City"].nunique()
    f["date_min"], f["date_max"] = df["Date"].min().date(), df["Date"].max().date()

    rank = an.city_ranking(df)
    f["rank"] = rank
    shares = an.bucket_shares(df)
    f["shares"] = shares

    if city in rank.index:
        f["city_rank_pos"] = list(rank.index).index(city) + 1
        f["city_median_aqi"] = rank.loc[city, "median"]
    if city in shares.index:
        f["city_poor_or_worse"] = shares.loc[city, "poor_or_worse"]
        f["city_very_poor_or_worse"] = shares.loc[city, ["Very Poor", "Severe"]].sum()

    seas = an.season_means(df, city)
    if {"Winter", "Monsoon"} <= set(seas.index):
        f["winter_pm25"], f["monsoon_pm25"] = seas["Winter"], seas["Monsoon"]
        f["winter_vs_monsoon"] = seas["Winter"] / seas["Monsoon"]
    f["season_means"] = seas

    w = an.diwali_window(df, city)
    if not w.empty:
        f["diwali"] = an.diwali_bump(w)

    f["lockdown_pm25"] = an.lockdown_change(df, "PM2.5")
    f["lockdown_no2"] = an.lockdown_change(df, "NO2")

    corr = an.pollutant_corr(df)
    if "PM2.5" in corr:
        s = corr["PM2.5"].drop(["PM2.5", "AQI"], errors="ignore").sort_values(ascending=False)
        f["pm25_top_corr"] = s.head(3)
    return f


def to_markdown(f: dict, city: str = HIGHLIGHT_CITY, synthetic: bool = False) -> str:
    L = []
    if synthetic:
        L += ["> ⚠️ **SYNTHETIC DATA - these numbers are NOT real findings.** "
              "They only prove the pipeline runs.", ""]
    L += [f"# Key findings (auto-generated)", "",
          f"Data: {f['rows']:,} city-day rows, {f['cities']} cities, {f['date_min']} to {f['date_max']}.", ""]

    if "city_rank_pos" in f:
        L += [f"- **{city} ranks #{f['city_rank_pos']}** of {len(f['rank'])} cities by median AQI "
              f"(median {f['city_median_aqi']:.0f})."]
    if "city_poor_or_worse" in f:
        L += [f"- In {city}, **{f['city_poor_or_worse']:.0f}%** of days were 'Poor' or worse and "
              f"**{f['city_very_poor_or_worse']:.0f}%** 'Very Poor' or 'Severe'."]
    if "winter_vs_monsoon" in f:
        L += [f"- {city} winter PM2.5 averaged **{f['winter_pm25']:.0f} µg/m³** vs "
              f"**{f['monsoon_pm25']:.0f}** in the monsoon ({f['winter_vs_monsoon']:.1f}x)."]
    if "diwali" in f:
        d = f["diwali"]
        L += [f"- Diwali effect in {city}: PM2.5 on the 2 days after Diwali averaged "
              f"**{d['post_diwali']:.0f}** vs a pre-festival baseline of {d['baseline']:.0f} "
              f"(**{d['ratio']:.1f}x**; years used: {', '.join(map(str, d['years_used']))}). "
              "Weather also changes over those days, so treat this as association, not proof."]
    for key, label in [("lockdown_pm25", "PM2.5"), ("lockdown_no2", "NO2")]:
        t = f[key]
        if not t.empty:
            L += [f"- Lockdown vs same dates in 2019, **{label}**: median change across {len(t)} cities "
                  f"**{t['pct_change'].median():+.0f}%** (largest drop {t['pct_change'].idxmin()} "
                  f"{t['pct_change'].min():+.0f}%; smallest {t['pct_change'].idxmax()} "
                  f"{t['pct_change'].max():+.0f}%)."]
    if "pm25_top_corr" in f:
        c = f["pm25_top_corr"]
        L += ["- Pollutants most correlated (Spearman) with PM2.5: "
              + ", ".join(f"{k} ({v:.2f})" for k, v in c.items()) + "."]

    L += ["", "## Top 10 cities by median AQI", "",
          f["rank"].head(10).round(0).to_markdown() if _has_tabulate() else f["rank"].head(10).round(0).to_string()]
    return "\n".join(L) + "\n"


def _has_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False


def write(f: dict, path: Path, city: str = HIGHLIGHT_CITY, synthetic: bool = False) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_markdown(f, city, synthetic), encoding="utf-8")
    return path
