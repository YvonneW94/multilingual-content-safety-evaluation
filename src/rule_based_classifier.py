from dataclasses import asdict, dataclass


@dataclass
class ClassificationResult:
    label: str
    confidence: float
    matched_keyword: str | None
    reason: str


KEYWORDS = {
    "en": {
        "SELF_HARM": [
            "hurt myself",
            "harming myself",
            "end my life",
            "suicide",
        ],
        "VIOLENCE": [
            "physically hurt you",
            "attack you",
            "kill you",
            "beat you",
        ],
        "HATE": [
            "because of their race",
            "because of their religion",
            "because of their gender",
            "inferior race",
        ],
        "HARASSMENT": [
            "you are useless",
            "you are worthless",
            "insulting messages",
            "nobody wants you",
        ],
    },
    "zh": {
        "SELF_HARM": [
            "伤害自己",
            "自杀",
            "不想活了",
            "结束生命",
        ],
        "VIOLENCE": [
            "伤害你",
            "攻击你",
            "杀了你",
            "打你",
        ],
        "HATE": [
            "因为他们的种族",
            "因为他们的宗教",
            "因为他们的性别",
            "劣等种族",
        ],
        "HARASSMENT": [
            "你一点用都没有",
            "没人希望你",
            "侮辱性消息",
            "你很没用",
        ],
    },
}

LABEL_PRIORITY = [
    "SELF_HARM",
    "VIOLENCE",
    "HATE",
    "HARASSMENT",
]


def classify_text(text: str, language: str) -> ClassificationResult:
    normalized_text = str(text).strip().lower()

    if language not in KEYWORDS:
        return ClassificationResult(
            label="SAFE",
            confidence=0.50,
            matched_keyword=None,
            reason=f"Unsupported language: {language}",
        )

    for label in LABEL_PRIORITY:
        for keyword in KEYWORDS[language][label]:
            if keyword.lower() in normalized_text:
                return ClassificationResult(
                    label=label,
                    confidence=0.80,
                    matched_keyword=keyword,
                    reason=f"Matched a {label} keyword rule",
                )

    return ClassificationResult(
        label="SAFE",
        confidence=0.60,
        matched_keyword=None,
        reason="No safety keyword rule matched",
    )


def classify_as_dict(text: str, language: str) -> dict:
    return asdict(classify_text(text, language))
