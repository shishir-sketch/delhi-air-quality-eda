"""Matplotlib/seaborn figures. Each function saves one PNG and returns its path."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")                       # headless-safe; notebooks override this
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src import analysis as an
from src.config import (BUCKET_COLORS, BUCKET_ORDER, HIGHLIGHT_CITY, LOCKDOWN_START,
                        NAAQS_PM25_24H, SEASON_ORDER, WHO_PM25_24H, DIWALI)

ACCENT = "#C0392B"      # highlight colour (Delhi)
MUTED = "#9AA5B1"

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 160, "axes.titleweight": "bold",
                     "axes.titlesize": 13, "axes.spines.top": False, "axes.spines.right": False})


def _save(fig, out_dir: Path, name: str) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def fig_coverage(df, out_dir):
    """01 - Where do we actually have data? (honesty before insight)"""
    cov = df.dropna(subset=["PM2.5"]).groupby(["City", "Year"]).size().unstack(fill_value=0)
    cov = cov.loc[cov.sum(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(8, 0.35 * len(cov) + 2))
    sns.heatmap(cov, annot=True, fmt="d", cmap="Blues", cbar_kws={"label": "days with PM2.5 reading"},
                linewidths=.5, ax=ax, annot_kws={"size": 8})
    ax.set_title("Data coverage: days with a PM2.5 reading, by city and year")
    ax.set_xlabel(""); ax.set_ylabel("")
    return _save(fig, out_dir, "01_data_coverage.png")


def fig_city_ranking(df, out_dir):
    """02 - Which cities are the most polluted?"""
    r = an.city_ranking(df)
    fig, ax = plt.subplots(figsize=(8, 0.36 * len(r) + 1.5))
    colors = [ACCENT if c == HIGHLIGHT_CITY else MUTED for c in r.index]
    ax.barh(r.index[::-1], r["median"][::-1], color=colors[::-1])
    for y, (m, p) in enumerate(zip(r["median"][::-1], r["p95"][::-1])):
        ax.plot([m, p], [y, y], color="black", lw=1, alpha=.6)           # median -> 95th pct
        ax.plot(p, y, "|", color="black")
    ax.set_xlabel("AQI (bar = median day; whisker = 95th-percentile day)")
    ax.set_title("Typical vs bad-day air quality by city, 2015-2020")
    return _save(fig, out_dir, "02_city_ranking.png")


def fig_bucket_shares(df, out_dir):
    """03 - How many days are actually 'Poor' or worse?"""
    s = an.bucket_shares(df).head(15)[::-1]          # reversed so worst city is on top
    fig, ax = plt.subplots(figsize=(9, 0.4 * len(s) + 1.8))
    left = np.zeros(len(s))
    for b in BUCKET_ORDER:
        ax.barh(s.index, s[b], left=left, color=BUCKET_COLORS[b], label=b, edgecolor="white", lw=.5)
        left += s[b].values
    ax.set_xlim(0, 100); ax.set_xlabel("% of days")
    ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False, fontsize=8)
    ax.set_title("Share of days in each CPCB AQI category (15 worst cities by 'Poor or worse')")
    return _save(fig, out_dir, "03_aqi_bucket_shares.png")


def fig_delhi_timeseries(df, out_dir, city=HIGHLIGHT_CITY):
    """04 - The Delhi story in one picture."""
    d = df[df["City"] == city].dropna(subset=["PM2.5"]).set_index("Date")["PM2.5"]
    d = d.asfreq("D")
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(d.index, d, color=MUTED, lw=.6, alpha=.7, label="daily")
    ax.plot(d.index, d.rolling(30, min_periods=15).mean(), color=ACCENT, lw=2, label="30-day mean")
    x_right = d.index[-1]
    ax.axhline(NAAQS_PM25_24H, color="black", ls="--", lw=1)
    ax.text(x_right, NAAQS_PM25_24H + 6, f"India NAAQS 24h limit ({NAAQS_PM25_24H})",
            fontsize=8, ha="right", bbox=dict(fc="white", ec="none", pad=1, alpha=.8))
    ax.axhline(WHO_PM25_24H, color="green", ls=":", lw=1)
    ax.text(x_right, WHO_PM25_24H + 6, f"WHO 2021 guideline ({WHO_PM25_24H})",
            fontsize=8, color="green", ha="right")
    ax.axvline(pd.Timestamp(LOCKDOWN_START), color="steelblue", lw=1)
    ax.annotate("lockdown", (pd.Timestamp(LOCKDOWN_START), ax.get_ylim()[1] * .62),
                xytext=(-6, 0), textcoords="offset points", ha="right", color="steelblue", fontsize=9)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("PM2.5 (µg/m³)"); ax.legend(loc="upper left", frameon=False)
    ax.set_title(f"{city}: daily PM2.5 with 30-day average")
    return _save(fig, out_dir, "04_delhi_timeseries.png")


def fig_delhi_calendar(df, out_dir, city=HIGHLIGHT_CITY):
    """05 - Seasonality: month x year heatmap."""
    m = an.monthly_matrix(df, city).reindex(columns=range(1, 13))
    m.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    sns.heatmap(m, annot=True, fmt=".0f", cmap="YlOrRd", linewidths=.5, ax=ax,
                cbar_kws={"label": "mean PM2.5 (µg/m³)"}, annot_kws={"size": 8})
    ax.set_xlabel(""); ax.set_ylabel("")
    ax.set_title(f"{city}: monthly mean PM2.5 - the winter wall")
    return _save(fig, out_dir, "05_delhi_calendar.png")


def fig_seasons(df, out_dir, cities=("Delhi", "Lucknow", "Kolkata", "Mumbai", "Hyderabad", "Chennai", "Bengaluru")):
    """06 - Is the seasonal swing unique to the north?"""
    cities = [c for c in cities if c in set(df["City"])]
    d = df[df["City"].isin(cities)].dropna(subset=["PM2.5"])
    fig, ax = plt.subplots(figsize=(10, 4.8))
    sns.boxplot(data=d, x="City", y="PM2.5", hue="Season", order=cities, hue_order=SEASON_ORDER,
                palette=["#5B8DB8", "#F2B05E", "#6BBF8A", "#B0715E"], showfliers=False, ax=ax, linewidth=.8)
    ax.set_ylabel("PM2.5 (µg/m³), outliers hidden"); ax.set_xlabel("")
    ax.legend(ncol=4, frameon=False, loc="upper right", fontsize=8)
    ax.set_title("PM2.5 by season: the north swings, the south barely moves")
    return _save(fig, out_dir, "06_seasonal_boxplots.png")


def fig_diwali(df, out_dir, city=HIGHLIGHT_CITY):
    """07 - Does Diwali leave a fingerprint?"""
    w = an.diwali_window(df, city)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for yr in w.columns:
        ax.plot(w.index, w[yr], lw=1, alpha=.7, label=str(yr))
    ax.plot(w.index, w.mean(axis=1), color="black", lw=3, label="mean")
    ax.axvline(0, color=ACCENT, ls="--"); ax.text(0.2, ax.get_ylim()[1] * .95, "Diwali", color=ACCENT)
    ax.set_xlabel("days relative to Diwali"); ax.set_ylabel("PM2.5 (µg/m³)")
    ax.legend(ncol=3, frameon=False, fontsize=8)
    ax.set_title(f"{city}: PM2.5 in the 10 days either side of Diwali")
    return _save(fig, out_dir, "07_diwali_window.png")


def fig_lockdown(df, out_dir):
    """08 - A natural experiment: the 2020 lockdown."""
    pm, no2 = an.lockdown_change(df, "PM2.5"), an.lockdown_change(df, "NO2")
    order = [c for c in pm.index if c in no2.index] or list(pm.index)   # one shared city order
    fig, axes = plt.subplots(1, 2, figsize=(11, 0.42 * max(len(order), 4) + 2), sharey=True,
                             gridspec_kw={"wspace": 0.08})
    for ax, col, t in zip(axes, ["PM2.5", "NO2"], [pm, no2]):
        t = t.reindex(order)
        colors = [ACCENT if c == HIGHLIGHT_CITY else "#5B8DB8" for c in t.index]
        ax.barh(t.index, t["pct_change"], color=colors)
        ax.axvline(0, color="black", lw=.8)
        ax.set_title(col); ax.set_xlabel("% change vs same dates in 2019")
    axes[0].invert_yaxis()
    fig.suptitle("Lockdown window (25 Mar - 31 May 2020) vs 2019: particulates (PM2.5) vs traffic pollutant (NO2)",
                 fontweight="bold", fontsize=12, y=1.0)
    return _save(fig, out_dir, "08_lockdown_effect.png")


def fig_trend(df, out_dir, cities=("Delhi", "Lucknow", "Kolkata", "Mumbai", "Hyderabad", "Chennai", "Bengaluru")):
    """09 - Is it getting better?"""
    a = an.annual_means(df)
    cities = [c for c in cities if c in a.columns]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for c in cities:
        s = a[c].dropna()
        ax.plot(s.index, s.values, marker="o", lw=2.5 if c == HIGHLIGHT_CITY else 1.3,
                color=ACCENT if c == HIGHLIGHT_CITY else None, label=c)
    ax.axhline(40, color="black", ls="--", lw=1)
    ax.text(a.index.min(), 41, "India NAAQS annual limit (40)", fontsize=8)
    ax.set_xticks(sorted(a.index)); ax.set_ylabel("annual mean PM2.5 (µg/m³)")
    ax.legend(ncol=4, frameon=False, fontsize=8)
    ax.set_title("Annual mean PM2.5 (only city-years with ≥240 days of data)")
    return _save(fig, out_dir, "09_annual_trend.png")


def fig_corr(df, out_dir):
    """10 - What moves together?"""
    c = an.pollutant_corr(df)
    mask = np.triu(np.ones_like(c, dtype=bool), k=1)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    sns.heatmap(c, mask=mask, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, ax=ax,
                annot_kws={"size": 8}, cbar_kws={"label": "Spearman ρ"})
    ax.set_title("Pollutant correlations (all cities pooled)")
    return _save(fig, out_dir, "10_pollutant_correlations.png")


ALL_FIGURES = [fig_coverage, fig_city_ranking, fig_bucket_shares, fig_delhi_timeseries,
               fig_delhi_calendar, fig_seasons, fig_diwali, fig_lockdown, fig_trend, fig_corr]
