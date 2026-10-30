import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score


def calculate_agreement(annotations: pd.DataFrame) -> dict:
    reviewed = annotations[
        annotations["annotator_1"].notna()
        & annotations["annotator_2"].notna()
        & (annotations["annotator_1"].astype(str).str.strip() != "")
        & (annotations["annotator_2"].astype(str).str.strip() != "")
    ].copy()

    if reviewed.empty:
        return {
            "status": "insufficient_data",
            "reviewed_examples": 0,
            "message": "No examples have two independent annotations.",
        }

    overall = {
        "reviewed_examples": len(reviewed),
        "percent_agreement": (
            reviewed["annotator_1"] == reviewed["annotator_2"]
        ).mean(),
        "cohens_kappa": cohen_kappa_score(
            reviewed["annotator_1"], reviewed["annotator_2"]
        ),
    }
    by_language = {}
    for language, group in reviewed.groupby("language"):
        by_language[language] = {
            "reviewed_examples": len(group),
            "percent_agreement": (
                group["annotator_1"] == group["annotator_2"]
            ).mean(),
            "cohens_kappa": cohen_kappa_score(
                group["annotator_1"], group["annotator_2"]
            ),
        }

    return {"status": "complete", "overall": overall, "by_language": by_language}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run-name", required=True)
    args = parser.parse_args()

    annotations = pd.read_csv(args.data)
    result = calculate_agreement(annotations)
    output = Path("data/results") / f"{args.run_name}_agreement.json"
    with output.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print(json.dumps(result, indent=2))
    print(f"Saved annotation agreement report to: {output}")


if __name__ == "__main__":
    main()
