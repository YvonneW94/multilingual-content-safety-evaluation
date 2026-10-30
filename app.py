import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd
import plotly.express as px
import streamlit as st

from src.llm_classifier import classify_with_llm
from src.error_analysis import assign_error_type
from src.routing import route_prediction
from src.rule_based_classifier import classify_text


RESULTS_PATH = Path("data/results/rule_baseline_predictions.csv")
METRICS_PATH = Path("data/results/rule_baseline_metrics.json")
LLM_METRICS_PATH = Path("data/results/llm_metrics.json")
FEEDBACK_PATH = Path("data/results/reviewer_feedback.csv")
THRESHOLD_PATH = Path(
    "data/results/challenge_llm_threshold_sensitivity.csv"
)
AGREEMENT_PATH = Path("data/results/challenge_agreement.json")
BLIND_REVIEW_PATH = Path(
    "data/processed/challenge_second_review_template.csv"
)
QUALITY_GATE_PATH = Path("data/results/quality_gate.json")
LABELS = ["SAFE", "HATE", "HARASSMENT", "VIOLENCE", "SELF_HARM"]

DATASET_CONFIG = {
    "Pilot": {
        "rule_predictions": RESULTS_PATH,
        "rule_metrics": METRICS_PATH,
        "llm_metrics": LLM_METRICS_PATH,
        "rule_calibration": Path(
            "data/results/rule_baseline_calibration_summary.json"
        ),
        "llm_calibration": Path(
            "data/results/llm_calibration_summary.json"
        ),
        "rule_manifest": Path("data/results/rule_baseline_manifest.json"),
        "llm_manifest": Path("data/results/llm_manifest.json"),
        "description": "20 synthetic workflow-validation examples",
    },
    "Challenge": {
        "rule_predictions": Path(
            "data/results/challenge_rule_predictions.csv"
        ),
        "rule_metrics": Path("data/results/challenge_rule_metrics.json"),
        "llm_metrics": Path("data/results/challenge_llm_metrics.json"),
        "rule_calibration": Path(
            "data/results/challenge_rule_calibration_summary.json"
        ),
        "llm_calibration": Path(
            "data/results/challenge_llm_calibration_summary.json"
        ),
        "rule_manifest": Path("data/results/challenge_rule_manifest.json"),
        "llm_manifest": Path("data/results/challenge_llm_manifest.json"),
        "description": "40 balanced synthetic semantic challenge examples",
    },
    "Adversarial": {
        "rule_predictions": Path("data/results/adversarial_rule_predictions.csv"),
        "rule_metrics": Path("data/results/adversarial_rule_metrics.json"),
        "llm_metrics": Path("data/results/adversarial_llm_metrics.json"),
        "rule_calibration": Path("data/results/adversarial_rule_calibration_summary.json"),
        "llm_calibration": Path("data/results/adversarial_llm_calibration_summary.json"),
        "rule_manifest": Path("data/results/adversarial_rule_manifest.json"),
        "llm_manifest": Path("data/results/adversarial_llm_manifest.json"),
        "description": "50 independently reviewed synthetic adversarial examples",
    },
}


st.set_page_config(
    page_title="Multilingual Content Safety Evaluation",
    page_icon="🛡️",
    layout="wide",
)

if QUALITY_GATE_PATH.exists():
    with QUALITY_GATE_PATH.open(encoding="utf-8") as file:
        quality_gate = json.load(file)
    if quality_gate["status"] == "PASS":
        st.sidebar.success(
            f"Offline quality gate: PASS "
            f"({quality_gate['check_count']} checks)"
        )
    else:
        st.sidebar.error(
            f"Offline quality gate: FAIL "
            f"({quality_gate['failed_check_count']} failed checks)"
        )


def save_feedback(record: dict) -> None:
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not FEEDBACK_PATH.exists()
    with FEEDBACK_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(record))
        if write_header:
            writer.writeheader()
        writer.writerow(record)


def render_single_text_evaluation() -> None:
    st.subheader("Single text evaluation")
    language = st.selectbox("Language", ["en", "zh"])
    text = st.text_area(
        "Content",
        height=130,
        placeholder="Enter English or Chinese text for evaluation.",
    )
    model_type = st.radio(
        "Classifier",
        ["Rule-based baseline", "LLM classifier"],
        horizontal=True,
    )

    if st.button("Evaluate", type="primary", disabled=not text.strip()):
        try:
            if model_type == "Rule-based baseline":
                raw = classify_text(text, language)
                result = {
                    "label": raw.label,
                    "confidence": raw.confidence,
                    "policy_reason": raw.reason,
                    "evidence_span": raw.matched_keyword or "",
                }
            else:
                raw = classify_with_llm(text, language)
                result = raw.model_dump()

            decision = route_prediction(
                result["label"],
                float(result["confidence"]),
            )
            st.session_state["latest_result"] = {
                **result,
                "text": text,
                "language": language,
                "model_type": model_type,
                "routing_action": decision.action,
                "routing_reason": decision.reason,
            }
        except Exception as error:
            st.error(f"Evaluation failed: {error}")

    result = st.session_state.get("latest_result")
    if not result:
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Predicted label", result["label"])
    col2.metric("Confidence", f'{result["confidence"]:.0%}')
    col3.metric("Routing action", result["routing_action"])

    st.write("**Policy reason:**", result["policy_reason"])
    st.write("**Evidence span:**", result["evidence_span"] or "None")
    st.caption(result["routing_reason"])

    st.markdown("#### Human review")
    corrected_label = st.selectbox(
        "Reviewer label",
        LABELS,
        index=LABELS.index(result["label"]),
    )
    review_note = st.text_input("Reviewer note")
    escalate = st.checkbox("Escalate as ambiguous")

    if st.button("Save review"):
        save_feedback(
            {
                "review_id": str(uuid4()),
                "review_timestamp": datetime.now(timezone.utc).isoformat(),
                "language": result["language"],
                "text": result["text"],
                "model_type": result["model_type"],
                "model_label": result["label"],
                "model_confidence": result["confidence"],
                "routing_action": result["routing_action"],
                "reviewer_label": corrected_label,
                "prediction_confirmed": corrected_label == result["label"],
                "escalated": escalate,
                "review_note": review_note,
            }
        )
        st.success("Review saved to the local feedback file.")


def render_baseline_dashboard() -> None:
    st.subheader("Model evaluation")
    dataset_name = st.selectbox("Evaluation dataset", list(DATASET_CONFIG))
    config = DATASET_CONFIG[dataset_name]
    results_path = config["rule_predictions"]
    rule_metrics_path = config["rule_metrics"]
    llm_metrics_path = config["llm_metrics"]
    rule_calibration_path = config["rule_calibration"]
    llm_calibration_path = config["llm_calibration"]
    rule_manifest_path = config["rule_manifest"]
    llm_manifest_path = config["llm_manifest"]

    st.caption(config["description"])
    if not results_path.exists():
        st.info("Run `python -m src.evaluate_baseline` to generate results.")
        return

    df = pd.read_csv(results_path)
    df["error_type"] = df.apply(assign_error_type, axis=1)
    accuracy = (df["adjudicated_label"] == df["predicted_label"]).mean()
    errors = df[df["adjudicated_label"] != df["predicted_label"]]

    col1, col2, col3 = st.columns(3)
    col1.metric("Examples", len(df))
    col2.metric("Accuracy", f"{accuracy:.1%}")
    col3.metric("Errors", len(errors))

    language_summary = (
        df.assign(correct=df["adjudicated_label"] == df["predicted_label"])
        .groupby("language", as_index=False)["correct"]
        .mean()
    )
    figure = px.bar(
        language_summary,
        x="language",
        y="correct",
        range_y=[0, 1],
        labels={"correct": "Accuracy", "language": "Language"},
        title="Accuracy by language",
    )
    st.plotly_chart(figure, width="stretch")

    st.markdown("#### Error review")
    if errors.empty:
        st.success("No errors in the current result file.")
    else:
        error_summary = (
            errors.groupby(
                ["adjudicated_label", "error_type"], as_index=False
            )
            .size()
            .rename(columns={"size": "Errors"})
        )
        error_figure = px.bar(
            error_summary,
            x="adjudicated_label",
            y="Errors",
            color="error_type",
            barmode="stack",
            title="Errors by true category and error type",
            labels={"adjudicated_label": "True label"},
        )
        st.plotly_chart(error_figure, width="stretch")
        st.dataframe(
            errors[
                [
                    "content_id",
                    "language",
                    "text",
                    "adjudicated_label",
                    "predicted_label",
                    "predicted_confidence",
                    "error_type",
                ]
            ],
            width="stretch",
            hide_index=True,
        )

    if llm_metrics_path.exists() and rule_metrics_path.exists():
        with rule_metrics_path.open(encoding="utf-8") as file:
            rule_metrics = json.load(file)
        with llm_metrics_path.open(encoding="utf-8") as file:
            llm_metrics = json.load(file)

        comparison = pd.DataFrame(
            [
                {
                    "Model": "Rule-based",
                    **rule_metrics["overall_metrics"],
                },
                {
                    "Model": llm_metrics["model"],
                    **llm_metrics["overall_metrics"],
                },
            ]
        )
        st.markdown("#### Rule-based and LLM comparison")
        st.dataframe(comparison, width="stretch", hide_index=True)
        st.caption(
            "Synthetic results validate the workflow; they are not evidence "
            "of production readiness."
        )

    if rule_calibration_path.exists() and llm_calibration_path.exists():
        with rule_calibration_path.open(encoding="utf-8") as file:
            rule_calibration = json.load(file)
        with llm_calibration_path.open(encoding="utf-8") as file:
            llm_calibration = json.load(file)
        calibration_table = pd.DataFrame(
            [
                {"Model": "Rule-based", **rule_calibration},
                {"Model": "Structured LLM", **llm_calibration},
            ]
        )[
            [
                "Model",
                "mean_confidence",
                "empirical_accuracy",
                "expected_calibration_error",
                "brier_score",
            ]
        ]
        st.markdown("#### Confidence calibration")
        st.dataframe(
            calibration_table,
            width="stretch",
            hide_index=True,
        )
        st.caption(
            "Lower ECE and Brier scores are better. Results remain unstable "
            "on small synthetic datasets."
        )

    if rule_manifest_path.exists() and llm_manifest_path.exists():
        with rule_manifest_path.open(encoding="utf-8") as file:
            rule_manifest = json.load(file)
        with llm_manifest_path.open(encoding="utf-8") as file:
            llm_manifest = json.load(file)
        with st.expander("Experiment lineage"):
            lineage = pd.DataFrame(
                [
                    {
                        "Run": rule_manifest["run_name"],
                        "Model": rule_manifest["model"],
                        "Dataset SHA-256": rule_manifest["dataset"]["sha256"],
                        "Git commit": rule_manifest["git_commit"],
                        "Uncommitted changes": rule_manifest.get("git_dirty"),
                    },
                    {
                        "Run": llm_manifest["run_name"],
                        "Model": llm_manifest["model"],
                        "Dataset SHA-256": llm_manifest["dataset"]["sha256"],
                        "Git commit": llm_manifest["git_commit"],
                        "Uncommitted changes": llm_manifest.get("git_dirty"),
                    },
                ]
            )
            st.dataframe(lineage, width="stretch", hide_index=True)
            st.caption(
                "LLM manifests also store a prompt hash and structured-output "
                "schema identifier. API keys are never included."
            )


def render_threshold_dashboard() -> None:
    st.subheader("Threshold sensitivity")
    if not THRESHOLD_PATH.exists():
        st.info("Run the threshold sensitivity analysis to generate results.")
        return

    analysis = pd.read_csv(THRESHOLD_PATH)
    safe_threshold = st.select_slider(
        "SAFE pass threshold",
        options=sorted(analysis["safe_threshold"].unique()),
        value=0.95,
    )
    filtered = analysis[analysis["safe_threshold"] == safe_threshold].copy()
    chart_data = filtered.melt(
        id_vars=["harmful_threshold"],
        value_vars=[
            "automated_action_rate",
            "human_review_rate",
            "pass_rate",
            "monitor_rate",
        ],
        var_name="Routing metric",
        value_name="Rate",
    )
    figure = px.line(
        chart_data,
        x="harmful_threshold",
        y="Rate",
        color="Routing metric",
        markers=True,
        range_y=[0, 1],
        title="Routing volume by harmful-content threshold",
    )
    st.plotly_chart(figure, width="stretch")
    st.dataframe(filtered, width="stretch", hide_index=True)
    st.warning(
        "Model confidence is not a calibrated probability. These thresholds "
        "are product hypotheses, not enforcement recommendations."
    )


def render_annotation_quality() -> None:
    st.subheader("Annotation quality")
    if AGREEMENT_PATH.exists():
        with AGREEMENT_PATH.open(encoding="utf-8") as file:
            agreement = json.load(file)
        if agreement["status"] == "insufficient_data":
            st.info(agreement["message"])
        else:
            overall = agreement["overall"]
            col1, col2, col3 = st.columns(3)
            col1.metric("Dual-reviewed examples", overall["reviewed_examples"])
            col2.metric(
                "Percent agreement", f'{overall["percent_agreement"]:.1%}'
            )
            col3.metric("Cohen's kappa", f'{overall["cohens_kappa"]:.3f}')

    if BLIND_REVIEW_PATH.exists():
        st.markdown("#### Blinded second-review template")
        st.write(
            "The template excludes the existing labels so a second reviewer "
            "can annotate independently."
        )
        st.download_button(
            "Download review template",
            data=BLIND_REVIEW_PATH.read_bytes(),
            file_name=BLIND_REVIEW_PATH.name,
            mime="text/csv",
        )


def render_feedback_summary() -> None:
    st.subheader("Reviewer feedback")
    if not FEEDBACK_PATH.exists():
        st.info("No review decisions have been saved yet.")
        return

    feedback = pd.read_csv(FEEDBACK_PATH)
    col1, col2, col3 = st.columns(3)
    col1.metric("Reviews", len(feedback))
    col2.metric("Confirmed", int(feedback["prediction_confirmed"].sum()))
    col3.metric("Escalated", int(feedback["escalated"].sum()))
    st.dataframe(feedback, width="stretch", hide_index=True)


st.title("Multilingual Content Safety Evaluation Platform")
st.caption(
    "English and Chinese model evaluation, confidence routing, and "
    "human-review workflow. Prototype only; not for real enforcement."
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Evaluate content",
        "Model dashboard",
        "Threshold analysis",
        "Annotation quality",
        "Reviewer feedback",
    ]
)

with tab1:
    render_single_text_evaluation()

with tab2:
    render_baseline_dashboard()

with tab3:
    render_threshold_dashboard()

with tab4:
    render_annotation_quality()

with tab5:
    render_feedback_summary()
