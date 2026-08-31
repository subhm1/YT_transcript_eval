import csv
from pathlib import Path

from judge import judge_summary


DATASET_PATH = Path("evaluation/dataset.csv")
GENERATED_RESULTS_PATH = Path("evaluation/generated_results.csv")
TRANSCRIPTS_DIR = Path("evaluation/transcripts")
OUTPUT_PATH = Path("evaluation/judge_results.csv")


def main():
    results = []

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = {
            row["video_id"]: row
            for row in csv.DictReader(file)
        }

    with open(GENERATED_RESULTS_PATH, "r", encoding="utf-8") as file:
        generated_results = csv.DictReader(file)

        for row in generated_results:
            video_id = row["video_id"]
            title = row["title"]

            transcript_path = TRANSCRIPTS_DIR / f"{video_id}.txt"

            with open(transcript_path, "r", encoding="utf-8") as file:
                transcript = file.read()

            reference_summary = dataset[video_id]["reference_summary"]
            generated_summary = row["generated_summary"]

            print("\n" + "=" * 60)
            print(title)
            print("=" * 60)

            try:
                evaluation = judge_summary(
                    transcript=transcript,
                    reference_summary=reference_summary,
                    generated_summary=generated_summary,
                )

                print(f"Coverage:      {evaluation['coverage']}/5")
                print(f"Faithfulness:  {evaluation['faithfulness']}/5")
                print(f"Conciseness:   {evaluation['conciseness']}/5")
                print(f"Overall:       {evaluation['overall']}/5")
                print(f"Reason:        {evaluation['reason']}")

                results.append({
                    "video_id": video_id,
                    "title": title,
                    "coverage": evaluation["coverage"],
                    "faithfulness": evaluation["faithfulness"],
                    "conciseness": evaluation["conciseness"],
                    "overall": evaluation["overall"],
                    "reason": evaluation["reason"],
                })

            except Exception as exc:
                print(f"FAILED: {exc}")

    fieldnames = [
        "video_id",
        "title",
        "coverage",
        "faithfulness",
        "conciseness",
        "overall",
        "reason",
    ]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()