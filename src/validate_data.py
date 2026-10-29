from pathlib import Path

import pandas as pd


DATA_PATH = Path("data/processed/pilot_annotations.csv")

REQUIRED_COLUMNS = [
    "content_id",
    "text",
    "language",
    "source",
    "annotator_1",
    "annotator_2",
    "adjudicated_label",
    "needs_adjudication",
    "ambiguity_reason",
    "difficulty",
]

ALLOWED_LABELS = {
    "SAFE",
    "HATE",
    "HARASSMENT",
    "VIOLENCE",
    "SELF_HARM",
}

ALLOWED_LANGUAGES = {"en", "zh"}
ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}


def validate_dataset(df: pd.DataFrame) -> list[str]:
    """Return a list of data-quality issues."""

    issues = []

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]

    if missing_columns:
        issues.append(f"Missing columns: {missing_columns}")
        return issues

    if df["content_id"].duplicated().any():
        duplicate_ids = df.loc[
            df["content_id"].duplicated(keep=False), "content_id"
        ].tolist()
        issues.append(f"Duplicate content IDs: {duplicate_ids}")

    if df["text"].duplicated().any():
        issues.append("Duplicate text examples detected")

    if df["content_id"].isna().any():
        issues.append("Missing content IDs detected")

    if df["text"].isna().any():
        issues.append("Missing text detected")

    if (df["text"].fillna("").str.strip() == "").any():
        issues.append("Blank text detected")

    invalid_languages = set(df["language"].dropna()) - ALLOWED_LANGUAGES
    if invalid_languages:
        issues.append(f"Invalid languages: {sorted(invalid_languages)}")

    invalid_labels = (
        set(df["adjudicated_label"].dropna()) - ALLOWED_LABELS
    )
    if invalid_labels:
        issues.append(f"Invalid labels: {sorted(invalid_labels)}")

    invalid_difficulties = (
        set(df["difficulty"].dropna()) - ALLOWED_DIFFICULTIES
    )
    if invalid_difficulties:
        issues.append(
            f"Invalid difficulty levels: {sorted(invalid_difficulties)}"
        )

    return issues


def print_summary(df: pd.DataFrame) -> None:
    """Print a compact dataset summary."""

    print("\nDataset summary")
    print("----------------")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nLanguage distribution")
    print(df["language"].value_counts(dropna=False))

    print("\nLabel distribution")
    print(df["adjudicated_label"].value_counts(dropna=False))

    print("\nLanguage and label distribution")
    print(
        pd.crosstab(
            df["language"],
            df["adjudicated_label"],
            margins=True,
        )
    )

    print("\nDifficulty distribution")
    print(df["difficulty"].value_counts(dropna=False))


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    issues = validate_dataset(df)
    print_summary(df)

    print("\nValidation result")
    print("-----------------")

    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")

        raise SystemExit(1)

    print("PASS: No data-quality issues detected")


if __name__ == "__main__":
    main()
