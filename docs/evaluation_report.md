# Content Safety Model Evaluation Report

## 1 Evaluation Status

This report documents the initial rule-based baseline evaluated on a 20-example English and Chinese pilot dataset.

The pilot dataset is intended to validate the evaluation workflow. It is not large enough to support production-readiness claims.

## 2 Dataset

The pilot dataset contains:

- 20 total examples
- 10 English examples
- 10 Chinese examples
- Five safety labels
- Synthetic examples created for workflow validation

The five labels are:

- SAFE
- HATE
- HARASSMENT
- VIOLENCE
- SELF_HARM

The dataset is not class-balanced. SAFE examples are more common than the individual safety categories.

## 3 Rule-Based Baseline

The baseline searches for predefined English and Chinese keywords.

When a keyword is matched, the system assigns the corresponding safety label. If no keyword is matched, the system returns SAFE.

The classifier uses the following priority order:

1. SELF_HARM
2. VIOLENCE
3. HATE
4. HARASSMENT
5. SAFE

The confidence values used by the baseline are heuristic routing values. They are not calibrated probabilities.

## 4 Pilot Results

The rule-based baseline produced the following approximate results:

| Metric | Result |
|---|---:|
| Sample size | 20 |
| Accuracy | 0.850 |
| Macro precision | 0.754 |
| Macro recall | 0.700 |
| Macro F1 | 0.707 |
| Incorrect predictions | 3 |

These figures should be replaced automatically or verified against the saved metrics file if the pilot dataset changes.

## 5 Error Analysis

### Failure Pattern 1 Abstract Hate References

Two HATE examples were incorrectly classified as SAFE.

The examples referred to a protected group without naming a specific race, religion, gender, or nationality. The keyword system did not understand the semantic relationship between the target and a protected characteristic.

Product implication:

A keyword-only system may have low recall for implicit or abstract hate content.

Potential improvement:

Use a semantic classifier that can interpret group identity and policy definitions rather than relying only on literal keywords.

### Failure Pattern 2 Word Form Variation

One English SELF_HARM example was incorrectly classified as SAFE.

The rule included the phrase `hurt myself`, while the example used `hurting myself`.

Product implication:

Exact phrase matching is brittle and may miss grammatical variations, slang, spelling changes, or coded language.

Potential improvement:

Use stemming, lemmatization, semantic embeddings, or an LLM-based classifier.

## 6 Product Interpretation

The rule-based classifier has several advantages:

- Low implementation complexity
- Low inference cost
- Deterministic behavior
- Easy explanation of matched rules
- Fast execution

It also has important limitations:

- Limited semantic understanding
- Low coverage of implicit harmful content
- Sensitivity to wording changes
- Difficulty handling cultural and linguistic variation
- No reliable understanding of context, quotation, or intent

## 7 Next Experiment

The next experiment will compare the rule-based baseline with an LLM classifier using the same pilot dataset and label definitions.

The LLM classifier will return:

- Predicted label
- Confidence score
- Policy reason
- Evidence span

The comparison will focus on:

- Overall macro F1
- Recall for high-severity categories
- English and Chinese performance
- Reduction in false negatives
- New false positives introduced by semantic classification
- Structured-output reliability

