# Data

## Source

**Air Quality Data in India (2015 – 2020)** by Rohan Rao, on Kaggle:
<https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india>

The underlying measurements come from India's **Central Pollution Control Board (CPCB)**
([CAAQM portal](https://app.cpcbccr.com/ccr/)). This project uses one file:

| File | Grain | Rows (approx.) |
|---|---|---|
| `city_day.csv` | one row per city per day (station readings aggregated by CPCB) | ~29,000 |

Columns: `City, Date, PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, Xylene, AQI, AQI_Bucket`.
Pollutant units are µg/m³ except CO (mg/m³).

## Getting it

**Option A – script** (needs `pip install kagglehub`):

```bash
python -m src.download_data
```

**Option B – by hand** (always works):

1. Open the Kaggle page above, download `city_day.csv`.
2. Place it at `data/raw/city_day.csv`.

## Why isn't the data in this repo?

It's a third-party dataset; check the licence shown on the Kaggle page before
redistributing it. `data/raw/` is git-ignored so you can't commit it by accident.

## Try it without downloading anything

`data/sample/city_day_synthetic.csv` is **fabricated** data with the same schema, used for
tests and CI. Never quote numbers computed from it.

```bash
python -m src.make_sample_data   # regenerate it
make run-sample                  # run the pipeline on it
```
