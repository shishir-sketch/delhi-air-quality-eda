"""Shared constants: paths, palettes, domain knowledge."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DEFAULT_DATA = RAW_DIR / "city_day.csv"
FIG_DIR = ROOT / "figures"
REPORT_DIR = ROOT / "reports"

POLLUTANTS = ["PM2.5", "PM10", "NO", "NO2", "NOx", "NH3", "CO", "SO2", "O3",
              "Benzene", "Toluene", "Xylene"]

# CPCB National AQI categories, best -> worst
BUCKET_ORDER = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
BUCKET_COLORS = {
    "Good": "#00B050", "Satisfactory": "#92D050", "Moderate": "#FFD966",
    "Poor": "#F4B183", "Very Poor": "#E06666", "Severe": "#7B1E1E",
}

# Indian seasons (month -> season)
SEASON_ORDER = ["Winter", "Summer", "Monsoon", "Post-monsoon"]
SEASON_OF_MONTH = {12: "Winter", 1: "Winter", 2: "Winter",
                   3: "Summer", 4: "Summer", 5: "Summer",
                   6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
                   10: "Post-monsoon", 11: "Post-monsoon"}

# Main Diwali day for each year covered by the dataset (2015-2019)
DIWALI = {2015: "2015-11-11", 2016: "2016-10-30", 2017: "2017-10-19",
          2018: "2018-11-07", 2019: "2019-10-27"}

# India's national COVID-19 lockdown began on 25 March 2020
LOCKDOWN_START = "2020-03-25"
LOCKDOWN_END = "2020-05-31"

# India NAAQS 24-hour PM2.5 limit and the stricter WHO 2021 guideline (ug/m3)
NAAQS_PM25_24H = 60
WHO_PM25_24H = 15

HIGHLIGHT_CITY = "Delhi"
