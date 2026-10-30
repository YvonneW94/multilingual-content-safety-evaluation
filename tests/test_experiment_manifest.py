import json

import pandas as pd

from src.experiment_manifest import create_manifest, sha256_text


def test_sha256_text_is_stable():
    assert sha256_text("content safety") == sha256_text("content safety")
    assert sha256_text("content safety") != sha256_text("Content safety")


def test_create_manifest_records_lineage(tmp_path):
    dataset_path = tmp_path / "dataset.csv"
    predictions_path = tmp_path / "predictions.csv"
    metrics_path = tmp_path / "metrics.json"

    dataset = pd.DataFrame(
        {
            "content_id": ["A1"],
            "text": ["Example"],
            "language": ["en"],
            "adjudicated_label": ["SAFE"],
        }
    )
    dataset.to_csv(dataset_path, index=False)
    dataset.assign(predicted_label="SAFE").to_csv(
        predictions_path, index=False
    )
    metrics_path.write_text(
        json.dumps(
            {
                "model": "test-model",
                "overall_metrics": {"accuracy": 1.0},
            }
        )
    )

    manifest = create_manifest(
        "test_run",
        dataset_path,
        predictions_path,
        metrics_path,
        "structured_llm",
    )

    assert manifest["dataset"]["sample_size"] == 1
    assert manifest["dataset"]["language_distribution"] == {"en": 1}
    assert manifest["model"] == "test-model"
    assert manifest["prompt_sha256"]
