from src.rule_based_classifier import classify_text


def test_safe_english_text():
    result = classify_text(
        "I disagree with this proposal.",
        "en",
    )

    assert result.label == "SAFE"


def test_english_harassment():
    result = classify_text(
        "You are useless and nobody wants you.",
        "en",
    )

    assert result.label == "HARASSMENT"


def test_chinese_violence():
    result = classify_text(
        "我明天要伤害你。",
        "zh",
    )

    assert result.label == "VIOLENCE"


def test_chinese_self_harm():
    result = classify_text(
        "我有伤害自己的想法。",
        "zh",
    )

    assert result.label == "SELF_HARM"


def test_unsupported_language():
    result = classify_text(
        "Texto de ejemplo",
        "es",
    )

    assert result.label == "SAFE"
    assert result.confidence == 0.50
