import argparse
from pathlib import Path

import pandas as pd


ALLOWED_LABELS = {"SAFE", "HATE", "HARASSMENT", "VIOLENCE", "SELF_HARM"}


def adjudicate_annotations(
    dual_annotations: pd.DataFrame,
    decisions: pd.DataFrame,
) -> pd.DataFrame:
    disagreements = dual_annotations[
        dual_annotations["annotator_1"] != dual_annotations["annotator_2"]
    ]
    disagreement_ids = set(disagreements["content_id"])
    decision_ids = set(decisions["content_id"])
    if disagreement_ids != decision_ids:
        raise ValueError(
            "Adjudication decisions must exactly match disagreement IDs. "
            f"Expected: {sorted(disagreement_ids)}; "
            f"received: {sorted(decision_ids)}"
        )

    if decisions["content_id"].duplicated().any():
        raise ValueError("Adjudication decisions contain duplicate content IDs.")
    invalid_labels = set(decisions["final_label"]) - ALLOWED_LABELS
    if invalid_labels:
        raise ValueError(f"Invalid final labels: {sorted(invalid_labels)}")

    decision_fields = decisions[
        [
            "content_id",
            "final_label",
            "adjudication_rationale",
            "adjudicator",
            "adjudicated_at",
        ]
    ]
    final = dual_annotations.copy()
    final["initial_adjudicated_label"] = final["adjudicated_label"]
    final = final.merge(
        decision_fields,
        on="content_id",
        how="left",
        validate="one_to_one",
    )
    agreement = final["annotator_1"] == final["annotator_2"]
    final.loc[agreement, "final_label"] = final.loc[agreement, "annotator_1"]
    final.loc[agreement, "adjudication_rationale"] = ""
    final.loc[agreement, "adjudicator"] = ""
    final.loc[agreement, "adjudicated_at"] = ""
    final["adjudication_status"] = "not_required"
    final.loc[~agreement, "adjudication_status"] = "complete"
    final["adjudicated_label"] = final["final_label"]
    return final


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    dual_annotations = pd.read_csv(args.annotations, keep_default_na=False)
    decisions = pd.read_csv(args.decisions, keep_default_na=False)
    final = adjudicate_annotations(dual_annotations, decisions)
    final.to_csv(args.output, index=False)
    completed = (final["adjudication_status"] == "complete").sum()
    print(f"Saved {len(final)} final annotations with {completed} adjudications.")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
