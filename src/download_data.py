"""Download the dataset from Kaggle into data/raw/.

Dataset: "Air Quality Data in India (2015 - 2020)" by Rohan Rao
https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india

If this fails (e.g. Kaggle asks for credentials), download city_day.csv by hand
from the page above and drop it into data/raw/. See data/README.md.
"""
import shutil
from pathlib import Path

from src.config import RAW_DIR

SLUG = "rohanrao/air-quality-data-in-india"
WANTED = ["city_day.csv"]


def main() -> None:
    try:
        import kagglehub
    except ImportError:
        raise SystemExit("Run `pip install kagglehub`, or download the file manually "
                         "(see data/README.md).")
    src_dir = Path(kagglehub.dataset_download(SLUG))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name in WANTED:
        shutil.copy(src_dir / name, RAW_DIR / name)
        print(f"Copied {name} -> {RAW_DIR / name}")


if __name__ == "__main__":
    main()
