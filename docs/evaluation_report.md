# Content Safety Model Evaluation Report

## 1 Evaluation Status

This report documents the initial rule-based baseline evaluated on a 20-example English and Chinese pilot dataset.

The pilot dataset is intended to validate the evaluation workflow. It is not large enough to support production-readiness claims. A separate 40-example challenge set was subsequently independently reviewed and adjudicated.

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

## 7 LLM Pilot Results

The structured LLM classifier was evaluated on the same 20-example pilot
dataset using `gpt-6-luna`.

| Metric | Rule-based | LLM |
|---|---:|---:|
| Accuracy | 0.850 | 1.000 |
| Macro precision | 0.754 | 1.000 |
| Macro recall | 0.700 | 1.000 |
| Macro F1 | 0.707 | 1.000 |
| High-severity recall | Not separately reported | 1.000 |
| Safe-content false-positive rate | Not separately reported | 0.000 |
| Structured-output success rate | Not applicable | 1.000 |

The LLM improved pilot macro F1 by 0.293 and correctly classified the three
examples missed by the keyword baseline. English and Chinese macro F1 were
both 1.000. Mean LLM request latency was approximately 1.78 seconds.

These results validate the evaluation pipeline and show the expected advantage
of semantic classification over exact keyword matching. They do not establish
production readiness. The dataset is small, synthetic, and weighted toward
clear examples; a perfect score is therefore not surprising and should not be
generalized to natural platform content.

## 8 Product Decision

The LLM is the stronger candidate for semantic classification experiments,
while the rule-based system remains useful as a low-cost, deterministic
baseline and for narrow high-precision rules.

No model should automatically enforce policy based on this pilot. Confidence
scores are uncalibrated, and the current routing thresholds are product
hypotheses that require validation on a larger, harder dataset.

## 9 Next Experiment

The next experiment should expand the dataset with harder and more natural
examples, including:

- Quotation and counterspeech
- Sarcasm and coded language
- Implicit protected-group references
- Chinese slang and culturally specific phrasing
- Mixed English and Chinese content
- Benign mentions of violence and self-harm
- Multi-label and genuinely ambiguous cases

Threshold analysis should then measure the tradeoff between high-severity
recall, safe-content false positives, and human-review volume.

## 10 Balanced Challenge Set

A second synthetic challenge set was created to test semantic and linguistic
variation beyond the initial pilot.

The dataset contains 40 examples:

- 20 English and 20 Chinese examples
- Eight examples for each of the five labels
- 34 hard and six medium examples
- Quotation, counterspeech, sarcasm, implicit threats, indirect self-harm
  language, and protected-group references

| Metric | Rule-based | LLM |
|---|---:|---:|
| Accuracy | 0.250 | 1.000 |
| Macro precision | 0.242 | 1.000 |
| Macro recall | 0.250 | 1.000 |
| Macro F1 | 0.150 | 1.000 |
| English macro F1 | 0.067 | 1.000 |
| Chinese macro F1 | 0.206 | 1.000 |

The keyword baseline predicted SAFE for 38 of 40 examples and missed most
implicit harmful content. The LLM classified all 40 examples correctly and
preserved SAFE labels for quotation, recovery, condemnation, and disagreement.

This remains a workflow result rather than a production claim. The challenge
set is synthetic and was designed against the written taxonomy. It has now
received a blinded independent second review, but the next dataset should
contain naturally occurring or independently authored text and more genuinely
ambiguous cases.

## 11 Routing Analysis

Applying the prototype confidence thresholds to the 40 LLM predictions
produced:

| Routing action | Count | Rate |
|---|---:|---:|
| Automated action | 31 | 77.5% |
| Pass | 8 | 20.0% |
| Human review | 1 | 2.5% |
| Monitor | 0 | 0.0% |

The only human-review case was an indirect English SELF_HARM example with
confidence 0.84. The other harmful examples exceeded the current automated
action thresholds.

This low review rate should not be interpreted as an operational recommendation.
The LLM confidence values are uncalibrated and the dataset is synthetic. In a
real deployment, automated enforcement at this rate could create unacceptable
false-positive risk. The thresholds must be calibrated on independently
labeled data, and severe actions should retain human oversight until error
costs are understood.

## 12 Threshold Sensitivity

Threshold sensitivity was evaluated across harmful-content and safe-content
thresholds from 0.80 to 0.99.

For harmful predictions:

- Thresholds from 0.85 through 0.95 produced a 2.5% human-review rate.
- A 0.98 threshold increased human review to 12.5%.
- A 0.99 threshold increased human review to 42.5%.

For SAFE predictions, thresholds through 0.98 passed all eight SAFE examples.
A 0.99 threshold moved one example to monitoring, producing a 2.5% overall
monitor rate.

No automated-action errors or unsafe passes were observed because the LLM
classified every challenge example correctly. This does not validate the
thresholds. Meaningful calibration requires model errors, independently
labeled examples, and explicit cost assumptions for false positives, false
negatives, and review workload.

## 13 Independent Annotation Status

A second human reviewer independently labeled all 40 challenge examples using
a shuffled template that hid the initial project labels and model outputs.

| Slice | Reviewed | Percent agreement | Cohen's kappa |
|---|---:|---:|---:|
| Overall | 40 | 95.0% | 0.9375 |
| English | 20 | 90.0% | 0.8750 |
| Chinese | 20 | 100.0% | 1.0000 |

Two English examples required adjudication. A sarcastic targeted insult was
resolved as HARASSMENT, and an implicit physical threat was resolved as
VIOLENCE. The final dataset preserves both reviewer labels, their rationales,
the initial project label, the final label, and an adjudication audit trail.

The final labels match the labels used in the existing challenge evaluation,
so the reported model metrics do not change. The high agreement supports the
internal consistency of this small review exercise, but it should not be
generalized to production data or broader reviewer populations.

## 14 Structured Error Analysis

The challenge-set rule baseline produced 30 errors, all of which were false
negatives: harmful content was predicted as SAFE.

| Slice | Errors |
|---|---:|
| English | 16 |
| Chinese | 14 |
| HATE | 8 |
| HARASSMENT | 8 |
| VIOLENCE | 8 |
| SELF_HARM | 6 |
| Hard difficulty | 26 |
| Medium difficulty | 4 |

This error profile is more important than aggregate accuracy alone. The
baseline's main product risk is not excessive enforcement of safe content; it
is failure to detect semantically expressed harmful content. Exact keyword
matching therefore should not serve as the primary classifier for this
taxonomy.

The LLM produced no errors on the synthetic challenge set, so false-positive,
false-negative, and cross-category behavior cannot yet be estimated for that
model. The next evaluation set must be difficult enough to produce meaningful
LLM errors and support error-cost analysis.

## 15 Confidence Calibration

Confidence calibration was evaluated by treating model confidence as an
estimate of prediction correctness. Expected calibration error (ECE) and Brier
score are lower when confidence better matches observed accuracy.

| Challenge model | Mean confidence | Accuracy | ECE | Brier score |
|---|---:|---:|---:|---:|
| Rule-based | 0.610 | 0.250 | 0.380 | 0.304 |
| LLM | 0.981 | 1.000 | 0.0195 | 0.00095 |

The rule baseline was substantially miscalibrated because it assigned moderate
confidence to many incorrect SAFE predictions. The LLM confidence aligned more
closely with correctness on this dataset.

The LLM calibration result is not reliable enough for threshold setting. With
no LLM errors and only 40 synthetic examples, low ECE mainly reflects an easy
evaluation set. Calibration should be repeated on a larger independent sample
that contains both correct and incorrect predictions.

## 16 Experiment Lineage

Each evaluated run now includes a machine-readable manifest with:

- Dataset path, SHA-256 hash, sample size, language distribution, and labels
- Prediction and metric artifact paths and hashes
- Model type and model identifier
- Git commit and Python version
- LLM prompt hash and structured-output schema identifier
- UTC manifest creation time

This lineage allows results to be traced to the exact dataset, prompt, code
state, and output artifacts. Secrets such as API keys are never stored in the
manifest.

## 17 Offline Quality Gate

The offline quality gate verifies:

- Presence of all required English project documents
- Pilot, challenge, and final adjudicated dataset schema and value validity
- Presence of the agreement report and adjudication decisions
- Dataset, prediction, and metric hashes in all run manifests
- Dataset and result sample-size consistency
- Absence of tracked `.env` or Streamlit secrets files

The gate runs without an API call and is included in the continuous-integration
workflow. A hash mismatch, missing artifact, invalid dataset, or tracked secret
causes a non-zero exit status.

## 18 Adversarial Evaluation

A 50-example adversarial set was independently reviewed and adjudicated. It
contains 25 English and 25 Chinese examples and targets sarcasm, euphemism,
negation, context shifts, coded language, recovery discussion, and implicit
intent.

Annotation agreement was 78.0% with Cohen's kappa of 0.725. Eleven cases
required adjudication. Two initially proposed SELF_HARM labels were changed to
SAFE because the standalone phrases lacked sufficient context.

| Metric | Rule-based | LLM |
|---|---:|---:|
| Accuracy | 0.280 | 0.980 |
| Macro precision | 0.250 | 0.978 |
| Macro recall | 0.250 | 0.983 |
| Macro F1 | 0.160 | 0.980 |
| High-severity recall | Not separately reported | 1.000 |
| SAFE false-positive rate | Not separately reported | 0.083 |

The rule baseline made 36 false-negative errors. The LLM made one false
positive: it inferred SELF_HARM from an underspecified English phrase that the
adjudication process labeled SAFE. At a harmful threshold of 0.85, confidence
0.83 routes this case to human review; at 0.80 it would become an incorrect
automated action. This is the clearest product finding from the evaluation:
confidence routing can reduce harm only when thresholds reflect the cost of
severe false positives.
