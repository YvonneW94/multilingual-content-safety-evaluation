import pandas as pd

from src.adjudicate_annotations import adjudicate_annotations


def test_adjudication_preserves_history_and_sets_final_label():
    annotations = pd.DataFrame(
        {
            "content_id": ["A1", "A2"],
            "annotator_1": ["SAFE", "VIOLENCE"],
            "annotator_2": ["SAFE", "HARASSMENT"],
            "adjudicated_label": ["SAFE", "VIOLENCE"],
        }
    )
    decisions = pd.DataFrame(
        {
            "content_id": ["A2"],
            "final_label": ["VIOLENCE"],
            "adjudication_rationale": ["Implicit physical threat"],
            "adjudicator": ["project_owner"],
            "adjudicated_at": ["2026-10-30"],
        }
    )
    final = adjudicate_annotations(annotations, decisions)
    assert final.loc[0, "adjudication_status"] == "not_required"
    assert final.loc[1, "adjudication_status"] == "complete"
    assert final.loc[1, "adjudicated_label"] == "VIOLENCE"
    assert final.loc[1, "initial_adjudicated_label"] == "VIOLENCE"
    assert final.loc[1, "annotator_2"] == "HARASSMENT"
