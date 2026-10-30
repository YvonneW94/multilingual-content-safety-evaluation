.PHONY: install test validate baseline challenge quality app

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -q -p no:cacheprovider

validate:
	python src/validate_data.py
	python src/validate_data.py --data data/processed/challenge_annotations.csv

baseline:
	python -m src.evaluate_baseline

challenge:
	python -m src.evaluate_baseline --data data/processed/challenge_annotations.csv --run-name challenge_rule

quality:
	python -m src.quality_gate

app:
	streamlit run app.py
