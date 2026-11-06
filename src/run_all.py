"""One command to reproduce everything:

    python -m src.run_all --data data/raw/city_day.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src import findings, plots
from src.config import DEFAULT_DATA, FIG_DIR, REPORT_DIR
from src.load_clean import load_clean


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--fig-dir", type=Path, default=FIG_DIR)
    ap.add_argument("--report", type=Path, default=REPORT_DIR / "key_findings.md")
    ap.add_argument("--city", default="Delhi", help="city to feature in the deep-dive charts")
    args = ap.parse_args()

    if not args.data.exists():
        raise SystemExit(f"{args.data} not found. Run `python -m src.download_data` or see data/README.md.")

    df = load_clean(args.data)
    print(f"Loaded {len(df):,} rows, {df['City'].nunique()} cities")

    for fn in plots.ALL_FIGURES:
        try:
            path = fn(df, args.fig_dir)
            print(f"  saved {path}")
        except Exception as exc:                       # keep going; one bad chart shouldn't kill the run
            print(f"  !! {fn.__name__} failed: {exc!r}")

    synthetic = "synthetic" in args.data.name.lower()
    rep = findings.write(findings.compute(df, args.city), args.report, args.city, synthetic)
    print(f"  saved {rep}")


if __name__ == "__main__":
    main()
