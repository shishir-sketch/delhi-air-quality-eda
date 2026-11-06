"""Generate a SYNTHETIC stand-in for city_day.csv.

!!! Nothing produced from this file is a real finding. !!!
It exists so you (and CI) can run the whole pipeline without downloading the
real data. The schema matches the Kaggle file; the numbers are invented, with
a few deliberate patterns (winter peaks, a Diwali bump, a 2020 dip, gaps) so
every chart has something to draw.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import BUCKET_ORDER, DIWALI, LOCKDOWN_START, ROOT

OUT = ROOT / "data" / "sample" / "city_day_synthetic.csv"

# city -> (baseline PM2.5, winter amplitude)
CITIES = {"Delhi": (110, 1.0), "Lucknow": (100, 0.9), "Patna": (105, 0.9),
          "Kolkata": (70, 0.7), "Ahmedabad": (80, 0.5), "Mumbai": (50, 0.4),
          "Hyderabad": (45, 0.3), "Chennai": (40, 0.2), "Bengaluru": (35, 0.15),
          "Kochi": (30, 0.1)}


def aqi_bucket(aqi: float) -> str | float:
    if np.isnan(aqi):
        return np.nan
    for limit, name in zip([50, 100, 200, 300, 400], BUCKET_ORDER[:5]):
        if aqi <= limit:
            return name
    return "Severe"


def make(seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2015-01-01", "2020-07-01", freq="D")
    doy = dates.dayofyear.values
    # smooth annual cycle peaking around early December/January
    season = 0.5 * (1 + np.cos(2 * np.pi * (doy - 350) / 365.25))
    frames = []
    for city, (base, amp) in CITIES.items():
        pm25 = base * (0.55 + amp * season) * rng.lognormal(0, 0.28, len(dates))
        s = pd.Series(pm25, index=dates)
        for yr, d in DIWALI.items():                      # fireworks bump
            d = pd.Timestamp(d)
            s.loc[d: d + pd.Timedelta(days=2)] *= 1.0 + 1.2 * amp
        s.loc[LOCKDOWN_START:] *= 0.65                    # lockdown dip
        pm25 = s.values
        pm10 = pm25 * rng.normal(1.8, 0.15, len(dates))
        no2 = 18 + 0.15 * pm25 * rng.normal(1, 0.2, len(dates))
        no2[dates >= LOCKDOWN_START] *= 0.6
        df = pd.DataFrame({
            "City": city, "Date": dates, "PM2.5": pm25, "PM10": pm10,
            "NO": no2 * 0.4, "NO2": no2, "NOx": no2 * 1.3,
            "NH3": rng.normal(25, 6, len(dates)).clip(1),
            "CO": rng.lognormal(0, 0.4, len(dates)),
            "SO2": rng.normal(12, 3, len(dates)).clip(1),
            "O3": rng.normal(35, 10, len(dates)).clip(1),
            "Benzene": rng.lognormal(0.3, 0.4, len(dates)),
            "Toluene": rng.lognormal(0.8, 0.5, len(dates)),
            "Xylene": rng.lognormal(0.2, 0.5, len(dates)),
        })
        df["AQI"] = np.maximum(df["PM2.5"] * 2.2, df["PM10"] * 1.1)
        # realistic gaps: some cities start late, random outages
        start = pd.Timestamp("2015-01-01") + pd.Timedelta(days=int(rng.integers(0, 900)))
        df.loc[df["Date"] < start, df.columns[2:]] = np.nan
        outage = rng.random(len(df)) < 0.05                 # whole-day station outage
        df.loc[outage, df.columns[2:]] = np.nan
        # column-level gaps, like the real file (VOCs/NH3 are patchy, PM2.5 mostly present)
        for col, p_missing in [("PM2.5", 0.05), ("PM10", 0.15), ("NO2", 0.04),
                               ("NH3", 0.30), ("Benzene", 0.35), ("Toluene", 0.40), ("Xylene", 0.60)]:
            df.loc[rng.random(len(df)) < p_missing, col] = np.nan
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out["AQI_Bucket"] = out["AQI"].map(aqi_bucket)
    return out.dropna(subset=out.columns[2:-1], how="all")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = make()
    num = df.select_dtypes("number").columns
    df[num] = df[num].round(2)
    df.to_csv(OUT, index=False)
    print(f"Wrote SYNTHETIC data ({len(df):,} rows) -> {OUT}")


if __name__ == "__main__":
    main()
