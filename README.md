# Multilingual Content Safety Evaluation Platform

[**Live Demo**](https://multilingual-content-safety-evaluation.streamlit.app/) ·
[**System Architecture**](docs/assets/system-architecture.svg) ·
[**Evaluation Report**](docs/evaluation_report.md) ·
[**Annotation Guidelines**](docs/annotation_guidelines.md)

A product-oriented prototype for evaluating English and Chinese text-safety
classifiers. The project connects policy definitions, labeled data, model
evaluation, confidence routing, and human-review operations.

> Evaluation prototype only. It is not intended for real-world automated
> enforcement or production safety decisions.

**At a glance:** 110 bilingual synthetic examples · five safety categories ·
two independent-review rounds · macro F1 from 0.160 to 0.980 on the
adversarial set · 100% high-severity recall · confidence-based human-review
routing

![Adversarial rule-based and LLM comparison](docs/assets/dashboard-model-comparison.png)

## Portfolio Highlights

- Built a five-category English and Chinese evaluation system across 110
  synthetic examples, including 50 independently reviewed adversarial cases
- Designed blinded review, Cohen's kappa measurement, disagreement analysis,
  and traceable adjudication; observed kappa from 0.725 to 0.938
- Improved adversarial macro F1 from 0.160 for deterministic rules to 0.980
  for the structured LLM while maintaining 100% high-severity recall
- Identified one severe false positive caused by missing context and showed
  that a 0.85 confidence threshold routed it to human review instead of an
  incorrect automated action
- Added reproducible manifests, calibration and error analysis, 32 offline
  tests, and a 22-check quality gate

## System Architecture

![System architecture](docs/assets/system-architecture.svg)

The feedback loop connects reviewer decisions to policy clarification, prompt
iteration, and routing-threshold adjustment. Model confidence is treated as an
input to product routing, not as proof that a prediction is correct.

## What the Platform Does

- Classifies English and Chinese text into five safety labels
- Compares a deterministic rule baseline with a structured LLM classifier
- Reports precision, recall, macro F1, confusion matrices, and language slices
- Reviews false positives, false negatives, and recurring failure patterns
- Tests confidence thresholds against automation and human-review volume
- Supports human confirmation, correction, notes, and escalation
- Provides a blinded second-review workflow and agreement calculation

## Taxonomy

The MVP uses SAFE, HATE, HARASSMENT, VIOLENCE, and SELF_HARM.

## Current Results

| Dataset | Examples | Model | Accuracy | Macro F1 |
|---|---:|---|---:|---:|
| Pilot | 20 | Rule-based | 0.850 | 0.707 |
| Pilot | 20 | Structured LLM | 1.000 | 1.000 |
| Challenge | 40 | Rule-based | 0.250 | 0.150 |
| Challenge | 40 | Structured LLM | 1.000 | 1.000 |
| Adversarial | 50 | Rule-based | 0.280 | 0.160 |
| Adversarial | 50 | Structured LLM | 0.980 | 0.980 |

The perfect challenge-set score is not a production claim. All datasets are
small and synthetic. See the [evaluation report](docs/evaluation_report.md),
[data card](docs/data_card.md), and [model card](docs/model_card.md).

## Product Interface

Try the deployed application:
[multilingual-content-safety-evaluation.streamlit.app](https://multilingual-content-safety-evaluation.streamlit.app/)

![Adversarial dashboard overview](docs/assets/dashboard-adversarial.png)

The Streamlit application includes five English-language views:

- **Evaluate content** for live rule-based classification in the public demo;
  local deployments can also enable LLM classification with environment
  credentials
- **Model dashboard** for Pilot, Challenge, and Adversarial result comparison
- **Threshold analysis** for automation and review-volume tradeoffs
- **Annotation quality** for independent-review status and template download
- **Reviewer feedback** for confirmation, correction, notes, and escalation

The public deployment does not expose an API key. Saved LLM evaluation results
remain available in the dashboard for model comparison and error analysis.

Chinese appears only in Chinese evaluation content and keyword rules. All
interface labels, documentation, metadata, and analysis outputs are English.

## Repository Structure

```text
app.py                         Streamlit product interface
data/processed/                Pilot, challenge, and review-template data
data/results/                  Model, routing, and threshold outputs
docs/                          PRD, guidelines, report, data card, model card
src/evaluate_baseline.py       Deterministic baseline evaluation
src/evaluate_llm.py            Resumable structured LLM evaluation
src/analyze_routing.py         Routing-volume analysis
src/analyze_thresholds.py      Threshold sensitivity analysis
src/error_analysis.py          Error taxonomy and slice analysis
src/calibration.py             ECE, Brier score, and reliability bins
src/experiment_manifest.py     Dataset, prompt, artifact, and code lineage
src/quality_gate.py             Offline artifact and privacy validation
src/agreement.py               Percent agreement and Cohen's kappa
src/merge_second_review.py     Validated second-review merge
src/adjudicate_annotations.py  Traceable disagreement resolution
tests/                         Offline unit tests
```

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add an available model and API key to `.env` only for the LLM path:

```text
OPENAI_API_KEY=your_key
OPENAI_MODEL=your_model
```

Never commit `.env`.

## Reproduce the Offline Workflow

```bash
make test
make validate
make baseline
make challenge
make quality
streamlit run app.py
```

Tests, data validation, rule baselines, dashboards, and saved-result inspection
do not require an API key.

## Run LLM Evaluation

```bash
python -m src.evaluate_llm
python -m src.evaluate_llm \
  --data data/processed/challenge_annotations.csv \
  --run-name challenge_llm \
  --rule-run-name challenge_rule
```

Successful predictions are cached after every request. Rerunning resumes
incomplete work. Use `--refresh` only when intentionally reclassifying every
example.

## Analyze Routing and Thresholds

```bash
python -m src.analyze_routing \
  --predictions data/results/challenge_llm_predictions.csv \
  --run-name challenge_llm

python -m src.analyze_thresholds \
  --predictions data/results/challenge_llm_predictions.csv \
  --run-name challenge_llm

python -m src.error_analysis \
  --predictions data/results/challenge_rule_predictions.csv \
  --run-name challenge_rule

python -m src.calibration \
  --predictions data/results/challenge_llm_predictions.csv \
  --run-name challenge_llm

python -m src.experiment_manifest \
  --run-name challenge_llm \
  --dataset data/processed/challenge_annotations.csv \
  --predictions data/results/challenge_llm_predictions.csv \
  --metrics data/results/challenge_llm_metrics.json \
  --model-type structured_llm
```

## Independent Review Workflow

Generate a shuffled template that hides existing labels:

```bash
python -m src.prepare_blind_review \
  --data data/processed/challenge_annotations.csv \
  --output data/processed/challenge_second_review_template.csv
```

After a second reviewer completes every label, merge and evaluate the review:

```bash
python -m src.merge_second_review \
  --annotations data/processed/challenge_annotations.csv \
  --second-review data/processed/challenge_second_review_template.csv \
  --output data/processed/challenge_dual_annotations.csv

python -m src.agreement \
  --data data/processed/challenge_dual_annotations.csv \
  --run-name challenge

python -m src.adjudicate_annotations \
  --annotations data/processed/challenge_dual_annotations.csv \
  --decisions data/processed/challenge_adjudication_decisions.csv \
  --output data/processed/challenge_final_annotations.csv
```

The completed independent review covers all 40 challenge examples. Overall
agreement is 95.0% with Cohen's kappa of 0.9375; two disagreements were
adjudicated and preserved in the final annotation audit trail.

The adversarial round uses 50 hard English and Chinese examples designed to
stress context, euphemisms, negation, and coded language. Independent review
produced 78.0% agreement and Cohen's kappa of 0.725. After adjudication, the
rule baseline reached macro F1 0.160 and the structured LLM reached 0.980.

For this round, give the reviewer only
`adversarial_second_review_template.csv`,
`docs/annotation_guidelines.md`, and
`docs/adversarial_reviewer_instructions.md`.

## Privacy and Safety

- Do not enter private or personally identifying content.
- Local reviewer feedback is excluded from version control.
- No production user data is included.
- Model outputs and explanations should always be treated as fallible.
- Severe or ambiguous cases should retain meaningful human oversight.
