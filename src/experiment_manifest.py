import argparse
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.llm_classifier import SYSTEM_PROMPT


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def get_git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_git_dirty() -> bool | None:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
        return bool(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def create_manifest(
    run_name: str,
    dataset_path: Path,
    predictions_path: Path,
    metrics_path: Path,
    model_type: str,
) -> dict:
    dataset = pd.read_csv(dataset_path)
    predictions = pd.read_csv(predictions_path)
    with metrics_path.open(encoding="utf-8") as file:
        metrics = json.load(file)

    manifest = {
        "run_name": run_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_type": model_type,
        "model": metrics.get("model", model_type),
        "dataset": {
            "path": str(dataset_path),
            "sha256": sha256_file(dataset_path),
            "sample_size": len(dataset),
            "language_distribution": dataset["language"].value_counts().to_dict(),
            "label_distribution": (
                dataset["adjudicated_label"].value_counts().to_dict()
            ),
        },
        "artifacts": {
            "predictions_path": str(predictions_path),
            "predictions_sha256": sha256_file(predictions_path),
            "metrics_path": str(metrics_path),
            "metrics_sha256": sha256_file(metrics_path),
        },
        "result_sample_size": len(predictions),
        "overall_metrics": metrics.get("overall_metrics", {}),
        "git_commit": get_git_commit(),
        "git_dirty": get_git_dirty(),
        "python_version": platform.python_version(),
    }
    if model_type == "structured_llm":
        manifest["prompt_sha256"] = sha256_text(SYSTEM_PROMPT)
        manifest["structured_output_schema"] = "LLMClassification"
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument(
        "--model-type",
        choices=["rule_based", "structured_llm"],
        required=True,
    )
    args = parser.parse_args()

    manifest = create_manifest(
        run_name=args.run_name,
        dataset_path=args.dataset,
        predictions_path=args.predictions,
        metrics_path=args.metrics,
        model_type=args.model_type,
    )
    output = Path("data/results") / f"{args.run_name}_manifest.json"
    with output.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, ensure_ascii=False, indent=2)
    print(json.dumps(manifest, indent=2))
    print(f"Saved experiment manifest to: {output}")


if __name__ == "__main__":
    main()
