import csv
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipeline import run_pipeline_stream
from evaluation.judge import judge_summary


app = FastAPI(title="YouTube Transcript Summarizer")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "evaluation" / "dataset.csv"
TRANSCRIPTS_DIR = BASE_DIR / "evaluation" / "transcripts"


# ============================================================
# REQUEST MODELS
# ============================================================


class SummarizeRequest(BaseModel):
    url: str


class EvaluateRequest(BaseModel):
    video_id: str
    generated_summary: str


# ============================================================
# HEALTH
# ============================================================


@app.get("/health")
def health():
    return {"status": "ok"}


# ============================================================
# SUMMARIZATION STREAM
# ============================================================


@app.post("/summarize/stream")
def summarize_stream(request: SummarizeRequest):

    def event_generator():
        for event in run_pipeline_stream(request.url):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


# ============================================================
# EVALUATION
# ============================================================


@app.post("/evaluate")
def evaluate_summary(request: EvaluateRequest):

    video_id = request.video_id.strip()
    generated_summary = request.generated_summary.strip()

    if not video_id:
        raise HTTPException(
            status_code=400,
            detail="video_id is required.",
        )

    if not generated_summary:
        raise HTTPException(
            status_code=400,
            detail="generated_summary is required.",
        )

    # --------------------------------------------------------
    # Load benchmark dataset
    # --------------------------------------------------------

    if not DATASET_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Evaluation dataset not found.",
        )

    try:
        with open(
            DATASET_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            dataset = {
                row["video_id"]: row
                for row in csv.DictReader(file)
            }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load evaluation dataset: {exc}",
        ) from exc

    # --------------------------------------------------------
    # Check whether this video is part of the benchmark
    # --------------------------------------------------------

    if video_id not in dataset:
        raise HTTPException(
            status_code=404,
            detail=(
                "This video is not part of the evaluation "
                "benchmark."
            ),
        )

    dataset_row = dataset[video_id]

    reference_summary = dataset_row["reference_summary"]
    title = dataset_row["title"]

    # --------------------------------------------------------
    # Load benchmark transcript
    # --------------------------------------------------------

    transcript_path = TRANSCRIPTS_DIR / f"{video_id}.txt"

    if not transcript_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Benchmark transcript not found.",
        )

    try:
        with open(
            transcript_path,
            "r",
            encoding="utf-8",
        ) as file:
            transcript = file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load benchmark transcript: {exc}",
        ) from exc

    # --------------------------------------------------------
    # Run LLM-as-a-judge
    # --------------------------------------------------------

    try:
        evaluation = judge_summary(
            transcript=transcript,
            reference_summary=reference_summary,
            generated_summary=generated_summary,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {exc}",
        ) from exc

    # --------------------------------------------------------
    # Return structured evaluation
    # --------------------------------------------------------

    return {
        "video_id": video_id,
        "title": title,
        "evaluation": evaluation,
    }