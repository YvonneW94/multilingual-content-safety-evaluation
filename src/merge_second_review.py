import argparse
from pathlib import Path

import pandas as pd


ALLOWED_LABELS = {"SAFE", "HATE", "HARASSMENT", "VIOLENCE", "SELF_HARM"}


def merge_second_review(
    annotations: pd.DataFrame,
    second_review: pd.DataFrame,
) -> pd.DataFrame:
    if annotations["content_id"].duplicated().any():
        raise ValueError("Original annotations contain duplicate content IDs.")
    if second_review["content_id"].duplicated().any():
        raise ValueError("Second review contains duplicate content IDs.")

    missing_ids = set(annotations["content_id"]) - set(
        second_review["content_id"]
    )
    extra_ids = set(second_review["content_id"]) - set(
        annotations["content_id"]
    )
    if missing_ids or extra_ids:
        raise ValueError(
            f"Content ID mismatch. Missing: {sorted(missing_ids)}; "
            f"extra: {sorted(extra_ids)}"
        )

    labels = second_review["annotator_2"].fillna("").str.strip()
    if (labels == "").any():
        raise ValueError("Every example must have an annotator_2 label.")
    invalid_labels = set(labels) - ALLOWED_LABELS
    if invalid_labels:
        raise ValueError(f"Invalid annotator_2 labels: {sorted(invalid_labels)}")

    review_fields = second_review[
        ["content_id", "annotator_2", "annotator_2_rationale", "reviewed_at"]
    ].copy()
    merged = annotations.drop(columns=["annotator_2"], errors="ignore").merge(
        review_fields,
        on="content_id",
        how="left",
        validate="one_to_one",
    )
    disagreements = merged["annotator_1"] != merged["annotator_2"]
    merged.loc[disagreements, "needs_adjudication"] = True
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--second-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    annotations = pd.read_csv(args.annotations)
    second_review = pd.read_csv(args.second_review)
    merged = merge_second_review(annotations, second_review)
    merged.to_csv(args.output, index=False)
    disagreements = (merged["annotator_1"] != merged["annotator_2"]).sum()
    print(f"Merged {len(merged)} examples with {disagreements} disagreements.")
    print(f"Saved dual annotations to: {args.output}")


if __name__ == "__main__":
    main()
