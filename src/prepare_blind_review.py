import argparse
from pathlib import Path

import pandas as pd


def prepare_blind_review(annotations: pd.DataFrame) -> pd.DataFrame:
    review = annotations[["content_id", "text", "language"]].copy()
    review["annotator_2"] = ""
    review["annotator_2_rationale"] = ""
    review["reviewed_at"] = ""
    return review.sample(frac=1, random_state=42).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    annotations = pd.read_csv(args.data)
    review = prepare_blind_review(annotations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    review.to_csv(args.output, index=False)
    print(f"Prepared {len(review)} blinded examples at: {args.output}")


if __name__ == "__main__":
    main()
