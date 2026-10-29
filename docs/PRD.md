# Multilingual Content Safety Evaluation Platform

## 1 Product Overview

This project is a prototype for evaluating English and Chinese content-safety classification systems.

The platform compares rule-based and LLM classifiers, measures performance across languages and safety categories, and routes uncertain predictions to human review.

It is designed as an evaluation and decision-support product rather than a production moderation system.

## 2 Problem Statement

Global content platforms need to identify harmful content across languages. However, model performance can vary by language, cultural context, safety category, and decision threshold.

Aggregate accuracy alone does not reveal whether a model performs poorly on a particular language or misses severe safety risks.

This project addresses that problem by providing:

- A consistent multilingual safety taxonomy
- A labeled evaluation dataset
- Language-level and category-level performance analysis
- Error analysis for false positives and false negatives
- Confidence-based human-review routing
- Feedback collection for future model iteration

## 3 Target Users

### Trust and Safety Product Manager

Needs to determine whether a classifier meets product requirements and where human review is required.

### Policy and Operations Specialist

Needs consistent label definitions, boundary-case guidance, and a workflow for reviewing uncertain content.

### Machine Learning Engineer or Data Scientist

Needs evaluation results, failure patterns, and structured reviewer feedback to improve the model.

## 4 MVP Scope

The MVP will support:

- English and Chinese text
- Five mutually exclusive labels
- Rule-based baseline classification
- LLM-based classification
- Structured model outputs
- Precision, recall, macro F1, and confusion matrices
- Language-level and category-level evaluation
- Confidence-based routing
- Human confirmation and label correction
- Reviewer feedback storage

## 5 Safety Taxonomy

The MVP uses the following labels:

1. SAFE
2. HATE
3. HARASSMENT
4. VIOLENCE
5. SELF_HARM

## 6 Core User Flow

1. A user enters English or Chinese text.
2. The system detects the language.
3. The classifier returns a label, confidence score, explanation, and evidence span.
4. Routing logic recommends one of three actions:
   - Automated action
   - Human review
   - Monitoring or pass
5. A reviewer confirms or overrides the prediction.
6. The system stores the reviewer decision for evaluation and future iteration.

## 7 Product Requirements

### Content Classification

The system must return:

- Predicted label
- Confidence score
- Detected language
- Brief policy reason
- Relevant evidence span

### Model Evaluation

The system must calculate:

- Precision
- Recall
- F1 score
- Macro F1
- Confusion matrix
- Performance by language
- Performance by category

### Human Review

Reviewers must be able to:

- Confirm a model prediction
- Override the predicted label
- Add a review note
- Escalate an ambiguous example

### Feedback Storage

The system must record:

- Content ID
- Model prediction
- Confidence score
- Reviewer decision
- Corrected label
- Reviewer note
- Review timestamp

## 8 Success Metrics

Initial project targets include:

- At least 800 labeled evaluation examples
- Balanced English and Chinese coverage
- At least 200 independently reviewed examples
- Inter-annotator agreement above 85 percent
- Structured-output success rate above 98 percent
- Macro F1 improvement over the rule-based baseline
- High-severity recall above 85 percent
- Safe-content false-positive rate below 10 percent

These are development targets and must not be reported as achieved results until verified.

## 9 Risks and Limitations

- Public datasets may use incompatible label definitions.
- Machine-translated content may not reflect natural language use.
- LLM confidence scores may not be calibrated probabilities.
- Text without conversational context may be ambiguous.
- Cultural and linguistic differences may affect annotation consistency.
- Evaluation results from a prototype do not justify real-world automated enforcement.

## 10 Non Goals

The MVP will not:

- Make real moderation or enforcement decisions
- Process private user data
- Support images, video, or audio
- Replace trained human reviewers
- Claim production readiness
- Provide legal or policy compliance decisions

## 11 Roadmap

### Phase 1

Define the taxonomy, annotation guidelines, and data schema.

### Phase 2

Build and evaluate a rule-based baseline.

### Phase 3

Add an LLM classifier and structured outputs.

### Phase 4

Conduct language-level, category-level, and threshold analysis.

### Phase 5

Build the Streamlit review and evaluation interface.

### Phase 6

Add reviewer feedback storage and document product recommendations.

