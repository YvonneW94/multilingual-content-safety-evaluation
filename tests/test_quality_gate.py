import json

import pandas as pd

from src.experiment_manifest import sha256_file
from src.quality_gate import validate_manifest


def test_validate_manifest_detects_hash_mismatch(tmp_path):
    dataset_path = tmp_path / "data.csv"
    predictions_path = tmp_path / "predictions.csv"
    metrics_path = tmp_path / "metrics.json"
    manifest_path = tmp_path / "manifest.json"

    pd.DataFrame(
        {
            "content_id": ["A1"],
            "text": ["Example"],
            "language": ["en"],
            "adjudicated_label": ["SAFE"],
        }
    ).to_csv(dataset_path, index=False)
    pd.DataFrame({"predicted_label": ["SAFE"]}).to_csv(
        predictions_path, index=False
    )
    metrics_path.write_text("{}")

    manifest_path.write_text(
        json.dumps(
            {
                "dataset": {
                    "path": str(dataset_path),
                    "sha256": "incorrect",
                    "sample_size": 1,
                },
                "artifacts": {
                    "predictions_path": str(predictions_path),
                    "predictions_sha256": sha256_file(predictions_path),
                    "metrics_path": str(metrics_path),
                    "metrics_sha256": sha256_file(metrics_path),
                },
                "result_sample_size": 1,
            }
        )
    )

    issues = validate_manifest(manifest_path)
    assert issues == [f"Dataset hash mismatch: {dataset_path}"]
