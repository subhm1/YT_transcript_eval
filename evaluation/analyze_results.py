import pandas as pd


RESULTS_PATH = "evaluation/judge_results.csv"


def main():
    df = pd.read_csv(RESULTS_PATH)

    print("\nIndividual results:")
    print(
        df[
            [
                "title",
                "coverage",
                "faithfulness",
                "conciseness",
                "overall",
            ]
        ].to_string(index=False)
    )

    print("\nAverage scores:")
    print(
        df[
            [
                "coverage",
                "faithfulness",
                "conciseness",
                "overall",
            ]
        ].mean()
    )

    print("\nScore distributions:")
    for column in [
        "coverage",
        "faithfulness",
        "conciseness",
        "overall",
    ]:
        print(f"\n{column}:")
        print(df[column].value_counts().sort_index())


if __name__ == "__main__":
    main()
    