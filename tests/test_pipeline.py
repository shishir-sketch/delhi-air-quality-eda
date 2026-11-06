"""Smoke tests on the synthetic data: schema, cleaning rules, key analyses."""
import pandas as pd

from src import analysis as an
from src.load_clean import clean
from src.make_sample_data import make


def _df():
    return clean(make(seed=1))


def test_clean_has_calendar_columns_and_no_duplicates():
    df = _df()
    assert {"Year", "Month", "Season"} <= set(df.columns)
    assert not df.duplicated(["City", "Date"]).any()
    assert df["Date"].is_monotonic_increasing or df.groupby("City")["Date"].apply(lambda s: s.is_monotonic_increasing).all()


def test_clean_does_not_impute():
    raw = make(seed=1)
    df = clean(raw)
    assert df["PM2.5"].isna().sum() > 0          # gaps preserved, not filled


def test_bucket_shares_sum_to_100():
    s = an.bucket_shares(_df(), min_days=100)
    assert (s.iloc[:, :6].sum(axis=1).round(6) == 100).all()


def test_diwali_window_is_aligned_to_offsets():
    w = an.diwali_window(_df(), "Delhi")
    assert w.index.min() == -10 and w.index.max() == 10


def test_lockdown_change_is_a_percentage():
    t = an.lockdown_change(_df(), "PM2.5", min_days=20)
    assert ((t["mean_2020"] / t["mean_2019"] - 1) * 100).round(6).equals(t["pct_change"].round(6))
