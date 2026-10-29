import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()


SafetyLabel = Literal[
    "SAFE",
    "HATE",
    "HARASSMENT",
    "VIOLENCE",
    "SELF_HARM",
]


class LLMClassification(BaseModel):
    label: SafetyLabel
    confidence: float
    policy_reason: str
    evidence_span: str


SYSTEM_PROMPT = """
You are evaluating text for a multilingual content-safety prototype.

Classify each English or Chinese input into exactly one label:

SAFE:
No hate, targeted harassment, violence, or self-harm encouragement.
Neutral discussion, reporting, prevention, disagreement, and
condemnation of harmful behavior are generally SAFE.

HATE:
Attacks, dehumanization, exclusion, or hostility toward people based
on a protected characteristic such as race, ethnicity, nationality,
religion, gender, sexual orientation, or disability.

HARASSMENT:
Direct insults, humiliation, degradation, or intimidation targeting
a specific person or identifiable individual.

VIOLENCE:
Threats, encouragement, praise, or meaningful support for physical
harm against people.

SELF_HARM:
Encouragement, instructions, glorification, or an immediate personal
intention involving self-harm or suicide.

Decision rules:

1. Use only the text provided.
2. Do not assume missing context.
3. Distinguish discussion or condemnation from endorsement.
4. Use this priority when multiple labels apply:
   SELF_HARM, VIOLENCE, HATE, HARASSMENT, SAFE.
5. Return a confidence value between 0 and 1.
6. Keep policy_reason concise.
7. Copy only the shortest relevant portion into evidence_span.
8. If no harmful span exists, return an empty evidence_span.
9. Confidence is a model estimate, not a calibrated probability.
""".strip()


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to the local .env file."
        )

    return OpenAI(api_key=api_key)


def get_model() -> str:
    model = os.getenv("OPENAI_MODEL")

    if not model:
        raise RuntimeError(
            "OPENAI_MODEL is missing. Add an available model to .env."
        )

    return model


def classify_with_llm(
    text: str,
    language: str,
) -> LLMClassification:
    client = get_client()

    completion = client.chat.completions.parse(
        model=get_model(),
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"Language: {language}\n"
                    f"Content: {text}"
                ),
            },
        ],
        response_format=LLMClassification,
    )

    message = completion.choices[0].message

    if message.refusal:
        raise RuntimeError(
            f"Model refused classification: {message.refusal}"
        )

    if message.parsed is None:
        raise RuntimeError(
            "The model did not return a parsed classification."
        )

    result = message.parsed

    if not 0 <= result.confidence <= 1:
        raise ValueError(
            f"Confidence must be between 0 and 1: {result.confidence}"
        )

    return result
