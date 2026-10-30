from pathlib import Path

import pandas as pd

from src.validate_data import validate_dataset
from src.evaluate_baseline import use_final_labels


DATA_PATH = Path("data/processed/adversarial_annotations.csv")


def test_adversarial_dataset_is_valid_and_balanced():
    data = pd.read_csv(DATA_PATH)

    assert validate_dataset(data) == []
    assert len(data) == 50
    assert set(data["language"]) == {"en", "zh"}
    assert set(data["difficulty"]) == {"hard"}
    assert (pd.crosstab(data["language"], data["adjudicated_label"]) == 5).all().all()


def test_adversarial_dataset_does_not_duplicate_existing_text():
    adversarial = pd.read_csv(DATA_PATH)
    existing = pd.concat(
        [
            pd.read_csv("data/processed/pilot_annotations.csv"),
            pd.read_csv("data/processed/challenge_annotations.csv"),
        ],
        ignore_index=True,
    )

    assert set(adversarial["content_id"]).isdisjoint(existing["content_id"])
    assert set(adversarial["text"]).isdisjoint(existing["text"])


def test_evaluation_prefers_final_adjudicated_label():
    data = pd.DataFrame(
        {
            "adjudicated_label": ["SELF_HARM", "VIOLENCE"],
            "final_label": ["SAFE", ""],
        }
    )

    normalized = use_final_labels(data)

    assert normalized["adjudicated_label"].tolist() == ["SAFE", "VIOLENCE"]
