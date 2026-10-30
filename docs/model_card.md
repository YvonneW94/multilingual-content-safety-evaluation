# Model Evaluation Card

## Evaluated Systems

### Rule-Based Baseline

The baseline performs exact English and Chinese keyword matching. It is
deterministic, inexpensive, and easy to explain, but has limited semantic and
contextual understanding.

### Structured LLM Classifier

The LLM receives the five-label taxonomy and returns a schema-constrained
label, confidence estimate, policy reason, and evidence span. Confidence is a
model estimate and is not a calibrated probability.

## Evaluation Results

| Dataset | Model | Accuracy | Macro F1 |
|---|---|---:|---:|
| Pilot | Rule-based | 0.850 | 0.707 |
| Pilot | LLM | 1.000 | 1.000 |
| Challenge | Rule-based | 0.250 | 0.150 |
| Challenge | LLM | 1.000 | 1.000 |
| Adversarial | Rule-based | 0.280 | 0.160 |
| Adversarial | LLM | 0.980 | 0.980 |

On the challenge set, the rule baseline predicted SAFE for 38 of 40 examples.
The LLM correctly handled the synthetic quotation, counterspeech, indirect
threat, and implicit harmful-language cases.

## Product Interpretation

The evaluation demonstrates that semantic classification can address failure
modes that exact keyword matching cannot. It does not demonstrate production
readiness. Perfect synthetic-set results indicate that the current dataset is
not sufficiently challenging for the evaluated LLM.

## Routing

Prototype routing maps predictions to automated action, human review,
monitoring, or pass. Raising the harmful threshold from 0.95 to 0.99 increases
the challenge-set review rate from 2.5% to 42.5%.

These thresholds are hypotheses and must not be used for real enforcement
without independent calibration and explicit error-cost analysis.

## Calibration

On the 40-example challenge set, the rule baseline produced ECE 0.380 and
Brier score 0.304. The LLM produced ECE 0.0195 and Brier score 0.00095.

The LLM result is not sufficient for operational threshold setting because the
model made no errors on the small synthetic set. A larger independent dataset
with meaningful model errors is required for reliable calibration.

## Risks

- False positives may suppress safe expression.
- False negatives may leave severe harmful content unaddressed.
- Performance may vary across languages, dialects, and cultural contexts.
- Explanations may sound plausible when a classification is wrong.
- Model behavior may change between versions.
- User-entered text may contain sensitive information.

## Recommended Next Evaluation

- Expand independent review to a larger and more diverse reviewer pool.
- Add naturally authored and adversarial examples.
- Measure calibration instead of relying on raw confidence.
- Evaluate conversational context.
- Define category-specific error costs and review-capacity constraints.

## Adversarial Evaluation

A separate 50-example adversarial set targets quotation, sarcasm, coded
exclusion, euphemism, negation, recovery context, and implicit intent. After
independent review and adjudication, the structured LLM made one false-positive
SELF_HARM prediction on an English phrase whose missing context made SAFE the
final label. The equivalent Chinese example was classified correctly.

At the prototype harmful threshold of 0.85, the false positive is sent to human
review because its confidence is 0.83. Lowering the threshold to 0.80 would
automate the incorrect action, showing why threshold selection must reflect
error severity rather than aggregate F1 alone.
