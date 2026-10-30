# Adversarial Set Independent Review Instructions

## Purpose

Independently label 50 English and Chinese content-safety examples. Your labels
will be compared with the initial project labels only after your review is
complete.

Do not inspect the source annotation file, model predictions, confidence
scores, or evaluation results before submitting the completed template.

## Files

- Read `docs/annotation_guidelines.md` before labeling.
- Complete `data/processed/adversarial_second_review_template.csv`.
- Do not open `data/processed/adversarial_annotations.csv` while reviewing.

## Required Fields

For every row, complete:

- `annotator_2`: one of `SAFE`, `HATE`, `HARASSMENT`, `VIOLENCE`, or
  `SELF_HARM`
- `annotator_2_rationale`: a short reason grounded in the written taxonomy
- `reviewed_at`: the review date

Do not change `content_id`, `text`, or `language`. Do not reorder, add, or
remove rows.

## Independence Check

Before returning the file, confirm that:

- All 50 rows have a label, rationale, and review date.
- Only the five allowed labels are used.
- No initial labels or model outputs were consulted.
- Ambiguous cases were still assigned the single best label with uncertainty
  noted in the rationale.
