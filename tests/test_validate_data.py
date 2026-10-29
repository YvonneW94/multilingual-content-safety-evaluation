import pandas as pd

from src.validate_data import validate_dataset


def make_valid_dataframe():
    return pd.DataFrame(
        [
            {
                "content_id": "EN001",
                "text": "This is a neutral example.",
                "language": "en",
                "source": "synthetic",
                "annotator_1": "SAFE",
                "annotator_2": "",
                "adjudicated_label": "SAFE",
                "needs_adjudication": False,
                "ambiguity_reason": "",
                "difficulty": "easy",
            }
        ]
    )


def test_valid_dataset_has_no_issues():
    df = make_valid_dataframe()

    issues = validate_dataset(df)

    assert issues == []


def test_duplicate_content_id_is_detected():
    df = make_valid_dataframe()
    df = pd.concat([df, df], ignore_index=True)

    issues = validate_dataset(df)

    assert any("Duplicate content IDs" in issue for issue in issues)


def test_invalid_label_is_detected():
    df = make_valid_dataframe()
    df.loc[0, "adjudicated_label"] = "UNKNOWN"

    issues = validate_dataset(df)

    assert any("Invalid labels" in issue for issue in issues)
