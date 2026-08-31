from judge import judge_summary


transcript = """
Alice went to Paris for three days.
She visited the Louvre and the Eiffel Tower.
She returned home on Sunday.
"""

reference_summary = """
Alice visited Paris for three days, including the Louvre and Eiffel Tower,
before returning home on Sunday.
"""


tests = {
    "GOOD": """
- Alice visited Paris for three days.
- She visited the Louvre and Eiffel Tower.
- She returned home on Sunday.
""",

    "BAD_COVERAGE": """
- Alice visited Paris.
""",

    "HALLUCINATION": """
- Alice visited Paris for three days.
- She visited the Louvre and Eiffel Tower.
- She returned home on Monday.
- She also visited Rome.
""",
}


for name, generated_summary in tests.items():

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    result = judge_summary(
        transcript,
        reference_summary,
        generated_summary,
    )

    print(result)