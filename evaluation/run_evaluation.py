import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import csv

from pipeline import run_pipeline


DATASET_PATH = "evaluation/dataset.csv"
OUTPUT_PATH = "evaluation/generated_results.csv"
TRANSCRIPTS_DIR = "evaluation/transcripts"

Path(TRANSCRIPTS_DIR).mkdir(parents=True, exist_ok=True)


def main():

    results = []

    with open(DATASET_PATH, "r", encoding="utf-8") as file:

        dataset = csv.DictReader(file)

        for row in dataset:

            video_id = row["video_id"]
            title = row["title"]

            url = f"https://www.youtube.com/watch?v={video_id}"

            print("\n" + "=" * 60)
            print(title)
            print("=" * 60)

            try:

                result = run_pipeline(url)

                transcript_path = (
                    Path(TRANSCRIPTS_DIR)
                    / f"{video_id}.txt"
                )

                with open(
                    transcript_path,
                    "w",
                    encoding="utf-8",
                ) as transcript_file:
                    transcript_file.write(
                        result["transcript"]
                    )

                results.append({
                    "video_id": video_id,
                    "title": title,
                    "reference_summary": row["reference_summary"],
                    "generated_summary": result["summary"],
                    "transcript_tokens": result["metrics"]["transcript_tokens"],
                    "number_of_chunks": result["metrics"]["number_of_chunks"],
                    "map_calls": result["metrics"]["map_calls"],
                    "reduce_input_tokens": result["metrics"]["reduce_input_tokens"],
                    "execution_time_seconds": result["metrics"]["execution_time_seconds"],
                })

                print(result["summary"])

            except Exception as exc:

                print(f"FAILED: {exc}")

    fieldnames = [
        "video_id",
        "title",
        "reference_summary",
        "generated_summary",
        "transcript_tokens",
        "number_of_chunks",
        "map_calls",
        "reduce_input_tokens",
        "execution_time_seconds",
    ]

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()