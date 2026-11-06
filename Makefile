.PHONY: setup data sample run run-sample test clean

setup:
	pip install -r requirements.txt

data:          # download the real dataset (needs kagglehub, or download manually)
	python -m src.download_data

sample:        # generate a SYNTHETIC dataset to try the pipeline offline
	python -m src.make_sample_data

run:           # full analysis on the real data -> figures/ + reports/key_findings.md
	python -m src.run_all --data data/raw/city_day.csv

run-sample:    # pipeline on synthetic data (output is NOT a real finding)
	python -m src.run_all --data data/sample/city_day_synthetic.csv --fig-dir figures_sample --report reports/key_findings_SAMPLE.md

test:
	python -m pytest -q

clean:
	rm -rf figures_sample reports/key_findings_SAMPLE.md
