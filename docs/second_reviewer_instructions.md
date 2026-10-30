# Independent Second Reviewer Instructions

## Purpose

You are independently labeling 40 English and Chinese content-safety examples.
Your labels will be compared with a first review to measure annotation
agreement and identify cases that require adjudication.

Do not ask for or inspect the first reviewer's labels, model predictions, model
confidence scores, or evaluation results before completing your review.

## File to Complete

Use `data/processed/challenge_second_review_template.csv`.

Do not change:

- `content_id`
- `text`
- `language`

Complete:

- `annotator_2`
- `annotator_2_rationale`
- `reviewed_at`

## Allowed Labels

Assign exactly one of the following labels to every example:

- `SAFE`
- `HATE`
- `HARASSMENT`
- `VIOLENCE`
- `SELF_HARM`

Use uppercase spelling exactly as shown.

## Labeling Rules

Read `docs/annotation_guidelines.md` before starting.

Apply these principles:

1. Use only the information explicitly present in the text.
2. Do not infer missing intent or context.
3. Distinguish endorsement from quotation, reporting, prevention, recovery, or
   condemnation.
4. Use the documented priority order when multiple labels apply.
5. Add a concise rationale when a case is ambiguous, indirect, sarcastic, or
   depends on cultural or linguistic interpretation.
6. Do not consult any classifier while labeling.

## Review Timestamp

Enter the completion date in ISO format, for example:

`2026-10-30`

## Completion Checklist

Before returning the file, confirm that:

- All 40 rows have an `annotator_2` label.
- Every label is one of the five allowed values.
- No content IDs, text, or language values were changed.
- Ambiguous cases include a short rationale.
- No first-review labels or model outputs were consulted.

## Privacy

The file contains synthetic examples only. Do not add names, contact details,
private information, or examples from real users.
