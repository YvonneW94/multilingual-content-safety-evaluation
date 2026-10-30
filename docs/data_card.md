# Data Card

## Dataset Summary

The project contains three synthetic English and Chinese evaluation datasets.

| Dataset | Examples | English | Chinese | Purpose |
|---|---:|---:|---:|---|
| Pilot | 20 | 10 | 10 | Validate the end-to-end evaluation workflow |
| Challenge | 40 | 20 | 20 | Test semantic variation and balanced category performance |
| Adversarial | 50 | 25 | 25 | Stress-test context shifts, euphemisms, negation, and coded language |

The taxonomy contains five mutually exclusive labels: SAFE, HATE, HARASSMENT,
VIOLENCE, and SELF_HARM.

## Creation Process

Examples were written specifically for this prototype and labeled against the
project annotation guidelines. The challenge set includes quotation,
counterspeech, sarcasm, indirect threats, implicit harmful language, recovery
discussion, and protected-group references.

No private user data or production platform data is included.

The 50-example adversarial set was added after the initial challenge evaluation
and subsequently received a blinded independent second review and adjudication.

## Label Distribution

The 40-example challenge set is balanced across language and label:

- 20 English and 20 Chinese examples
- Eight examples per safety label
- Four examples per language-label combination
- 34 hard and six medium examples

The 50-example adversarial set was authored with five examples per
language-label combination. After adjudication changed two SELF_HARM examples
to SAFE, the final distribution is 12 SAFE, 10 each for HATE, HARASSMENT, and
VIOLENCE, and eight SELF_HARM. All examples are marked hard and include a
`challenge_type` field for qualitative slicing.

## Annotation Status

All 40 challenge examples received a blinded independent second review. The
reviewer did not see the initial project labels or model outputs while labeling.
Overall percent agreement was 95.0% and Cohen's kappa was 0.9375. English
agreement was 90.0% (kappa 0.875), and Chinese agreement was 100.0% (kappa
1.0).

Two disagreements were adjudicated against the written guidelines. The final
dataset retains the initial project label, independent reviewer label,
rationales, adjudicated label, adjudicator, and date for traceability.

For the adversarial set, agreement was 78.0% and Cohen's kappa was 0.725.
English agreement was 76.0% (kappa 0.700), and Chinese agreement was 80.0%
(kappa 0.750). Eleven disagreements were adjudicated. Two initially proposed
SELF_HARM labels were changed to SAFE because the isolated text lacked enough
context to support a self-harm interpretation.

## Intended Use

The data may be used to validate evaluation code, compare classifiers,
demonstrate language and category analysis, and test human-review workflows.

## Out-of-Scope Use

The data must not be used to claim production quality, set real enforcement
thresholds, estimate real-world prevalence, or replace professional review.

## Known Limitations

- All examples are synthetic and the sample size is small.
- The challenge set was authored against the evaluation taxonomy.
- Independent review covers two small synthetic sets and one second reviewer;
  the agreement estimates therefore have high uncertainty.
- The data does not represent natural prevalence, dialect distribution, coded
  language, adversarial behavior, or conversational context.
