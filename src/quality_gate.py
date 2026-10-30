import argparse
import json
import subprocess
from pathlib import Path

import pandas as pd

from src.experiment_manifest import sha256_file
from src.validate_data import validate_dataset


REQUIRED_DOCUMENTS = [
    Path("README.md"),
    Path("docs/PRD.md"),
    Path("docs/annotation_guidelines.md"),
    Path("docs/evaluation_report.md"),
    Path("docs/data_card.md"),
    Path("docs/model_card.md"),
]

DATASETS = [
    Path("data/processed/pilot_annotations.csv"),
    Path("data/processed/challenge_annotations.csv"),
    Path("data/processed/challenge_final_annotations.csv"),
    Path("data/processed/adversarial_annotations.csv"),
    Path("data/processed/adversarial_final_annotations.csv"),
]

REVIEW_ARTIFACTS = [
    Path("data/processed/challenge_adjudication_decisions.csv"),
    Path("data/results/challenge_agreement.json"),
    Path("data/processed/adversarial_adjudication_decisions.csv"),
    Path("data/results/adversarial_agreement.json"),
]

MANIFESTS = [
    Path("data/results/rule_baseline_manifest.json"),
    Path("data/results/llm_manifest.json"),
    Path("data/results/challenge_rule_manifest.json"),
    Path("data/results/challenge_llm_manifest.json"),
    Path("data/results/adversarial_rule_manifest.json"),
    Path("data/results/adversarial_llm_manifest.json"),
]


def validate_manifest(path: Path) -> list[str]:
    issues = []
    if not path.exists():
        return [f"Missing manifest: {path}"]

    with path.open(encoding="utf-8") as file:
        manifest = json.load(file)

    dataset_path = Path(manifest["dataset"]["path"])
    if not dataset_path.exists():
        issues.append(f"Missing manifest dataset: {dataset_path}")
    elif sha256_file(dataset_path) != manifest["dataset"]["sha256"]:
        issues.append(f"Dataset hash mismatch: {dataset_path}")

    for artifact_name in ("predictions", "metrics"):
        artifact_path = Path(
            manifest["artifacts"][f"{artifact_name}_path"]
        )
        expected_hash = manifest["artifacts"][f"{artifact_name}_sha256"]
        if not artifact_path.exists():
            issues.append(f"Missing artifact: {artifact_path}")
        elif sha256_file(artifact_path) != expected_hash:
            issues.append(f"Artifact hash mismatch: {artifact_path}")

    if dataset_path.exists():
        dataset_rows = len(pd.read_csv(dataset_path))
        if dataset_rows != manifest["dataset"]["sample_size"]:
            issues.append(f"Dataset sample-size mismatch: {dataset_path}")
        if dataset_rows != manifest["result_sample_size"]:
            issues.append(f"Result sample-size mismatch: {path}")

    return issues


def tracked_secret_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    tracked = set(result.stdout.splitlines())
    sensitive = {".env", ".streamlit/secrets.toml"}
    return sorted(tracked & sensitive)


def run_quality_gate() -> dict:
    checks = []

    for document in REQUIRED_DOCUMENTS:
        checks.append(
            {
                "check": f"required_document:{document}",
                "status": "PASS" if document.exists() else "FAIL",
                "details": "" if document.exists() else "File is missing",
            }
        )

    for dataset_path in DATASETS:
        if not dataset_path.exists():
            issues = ["File is missing"]
        else:
            issues = validate_dataset(pd.read_csv(dataset_path))
        checks.append(
            {
                "check": f"dataset_validation:{dataset_path}",
                "status": "PASS" if not issues else "FAIL",
                "details": "; ".join(issues),
            }
        )

    for manifest_path in MANIFESTS:
        issues = validate_manifest(manifest_path)
        checks.append(
            {
                "check": f"manifest_validation:{manifest_path}",
                "status": "PASS" if not issues else "FAIL",
                "details": "; ".join(issues),
            }
        )

    for artifact_path in REVIEW_ARTIFACTS:
        checks.append(
            {
                "check": f"review_artifact:{artifact_path}",
                "status": "PASS" if artifact_path.exists() else "FAIL",
                "details": "" if artifact_path.exists() else "File is missing",
            }
        )

    secrets = tracked_secret_files()
    checks.append(
        {
            "check": "tracked_secrets",
            "status": "PASS" if not secrets else "FAIL",
            "details": ", ".join(secrets),
        }
    )

    failed = [check for check in checks if check["status"] == "FAIL"]
    return {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failed_check_count": len(failed),
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/results/quality_gate.json"),
    )
    args = parser.parse_args()

    result = run_quality_gate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
