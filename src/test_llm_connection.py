from src.llm_classifier import classify_with_llm


TEST_CASES = [
    {
        "text": "I disagree with this proposal.",
        "language": "en",
    },
    {
        "text": "你一点用都没有，没人希望你留在这里。",
        "language": "zh",
    },
]


def main() -> None:
    for case in TEST_CASES:
        result = classify_with_llm(
            text=case["text"],
            language=case["language"],
        )

        print("\nInput")
        print("-----")
        print(case["text"])

        print("\nResult")
        print("------")
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

