import time

from fetcher import (
    extract_video_id,
    fetch_transcript,
    normalize_transcript,
    clean_text,
)

from chunker import chunk_text
from tokenizer import count_tokens
from ollama_client import summarize_chunk
from reducer import reduce_summaries


def run_pipeline(url: str) -> dict:
    start_time = time.perf_counter()

    # 1. Extract video ID
    try:
        video_id = extract_video_id(url)
    except Exception as exc:
        raise RuntimeError(
            f"Invalid YouTube URL: {exc}"
        ) from exc

    # 2. Fetch transcript
    try:
        transcript = fetch_transcript(
            video_id,
            languages=["en"],
        )
    except Exception as exc:
        raise RuntimeError(
            f"Transcript fetch failed: {exc}"
        ) from exc

    # 3. Normalize and clean transcript
    try:
        segments = normalize_transcript(transcript)
        text = clean_text(segments)
    except Exception as exc:
        raise RuntimeError(
            f"Transcript normalization or cleaning failed: {exc}"
        ) from exc

    if not text.strip():
        raise ValueError(
            "Transcript is empty after cleaning."
        )

    transcript_tokens = count_tokens(text)

    # 4. Chunk transcript
    try:
        chunks = chunk_text(text)
    except Exception as exc:
        raise RuntimeError(
            f"Transcript chunking failed: {exc}"
        ) from exc

    if not chunks:
        raise ValueError(
            "Chunking produced no chunks."
        )

    # 5. Map: summarize each chunk
    summaries = []
    map_calls = 0

    for index, chunk in enumerate(chunks, start=1):
        try:
            summary = summarize_chunk(chunk["text"])
        except Exception as exc:
            raise RuntimeError(
                f"Map step failed on chunk {index}: {exc}"
            ) from exc

        if not summary.strip():
            raise RuntimeError(
                f"Map step returned an empty summary for chunk {index}."
            )

        summaries.append(summary)
        map_calls += 1

    # 6. Prepare reducer input
    try:
        reduce_input = "\n\n".join(summaries)
        reduce_input_tokens = count_tokens(reduce_input)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to prepare reducer input: {exc}"
        ) from exc

    # 7. Reduce: combine all chunk summaries
    try:
        final_summary = reduce_summaries(summaries)
    except Exception as exc:
        raise RuntimeError(
            f"Reduce step failed: {type(exc).__name__}: {exc}"
        ) from exc

    if not final_summary.strip():
        raise RuntimeError(
            "Reduce step returned an empty final summary."
        )

    # 8. Final metrics
    execution_time = time.perf_counter() - start_time

    return {
        "summary": final_summary,
        "transcript": text,
        "metrics": {
            "transcript_tokens": transcript_tokens,
            "number_of_chunks": len(chunks),
            "map_calls": map_calls,
            "reduce_input_tokens": reduce_input_tokens,
            "execution_time_seconds": round(execution_time, 2),
        },
    }


def run_pipeline_stream(url: str):
    start_time = time.perf_counter()

    # ============================================================
    # 1. FETCH
    # ============================================================

    yield {
        "stage": "fetch",
        "status": "running",
        "message": "Fetching transcript",
    }

    try:
        video_id = extract_video_id(url)
    except Exception as exc:
        yield {
            "stage": "fetch",
            "status": "error",
            "message": f"Invalid YouTube URL: {exc}",
        }
        return

    try:
        transcript = fetch_transcript(
            video_id,
            languages=["en"],
        )
    except Exception as exc:
        yield {
            "stage": "fetch",
            "status": "error",
            "message": (
                f"Transcript fetch failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        }
        return

    yield {
        "stage": "fetch",
        "status": "complete",
        "message": "Transcript fetched",
    }

    # ============================================================
    # 2. NORMALIZE
    # ============================================================

    yield {
        "stage": "normalize",
        "status": "running",
        "message": "Cleaning transcript",
    }

    try:
        segments = normalize_transcript(transcript)
        text = clean_text(segments)
    except Exception as exc:
        yield {
            "stage": "normalize",
            "status": "error",
            "message": (
                f"Transcript normalization or cleaning failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        }
        return

    if not text.strip():
        yield {
            "stage": "normalize",
            "status": "error",
            "message": "Transcript is empty after cleaning.",
        }
        return

    # ============================================================
    # 3. TOKEN COUNT
    # ============================================================

    try:
        transcript_tokens = count_tokens(text)
    except Exception as exc:
        yield {
            "stage": "normalize",
            "status": "error",
            "message": (
                f"Token counting failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        }
        return

    yield {
        "stage": "normalize",
        "status": "complete",
        "message": (
            f"Transcript cleaned · "
            f"{transcript_tokens} tokens"
        ),
    }

    # ============================================================
    # 4. CHUNK
    # ============================================================

    yield {
        "stage": "chunk",
        "status": "running",
        "message": "Creating transcript chunks",
    }

    try:
        chunks = chunk_text(text)
    except Exception as exc:
        yield {
            "stage": "chunk",
            "status": "error",
            "message": (
                f"Transcript chunking failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        }
        return

    if not chunks:
        yield {
            "stage": "chunk",
            "status": "error",
            "message": "Chunking produced no chunks.",
        }
        return

    yield {
        "stage": "chunk",
        "status": "complete",
        "message": f"Created {len(chunks)} chunks",
    }

    # ============================================================
    # 5. MAP
    # ============================================================

    summaries = []
    map_calls = 0

    yield {
        "stage": "map",
        "status": "running",
        "message": "Summarizing transcript chunks",
        "total": len(chunks),
        "current": 0,
    }

    for index, chunk in enumerate(chunks, start=1):

        try:
            summary = summarize_chunk(chunk["text"])
        except Exception as exc:
            yield {
                "stage": "map",
                "status": "error",
                "message": (
                    f"Map step failed on chunk {index}: "
                    f"{type(exc).__name__}: {exc}"
                ),
                "total": len(chunks),
                "current": index - 1,
            }
            return

        if not summary.strip():
            yield {
                "stage": "map",
                "status": "error",
                "message": (
                    f"Empty summary returned for chunk {index}."
                ),
                "total": len(chunks),
                "current": index,
            }
            return

        summaries.append(summary)
        map_calls += 1

        yield {
            "stage": "map",
            "status": "running",
            "message": (
                f"Summarized chunk "
                f"{index} / {len(chunks)}"
            ),
            "total": len(chunks),
            "current": index,
        }

    yield {
        "stage": "map",
        "status": "complete",
        "message": f"Completed {map_calls} map calls",
        "total": len(chunks),
        "current": len(chunks),
    }

    # ============================================================
    # 6. REDUCE
    # ============================================================

    yield {
        "stage": "reduce",
        "status": "running",
        "message": "Combining chunk summaries",
    }

    # Prepare reducer input separately so we know exactly
    # whether a failure happens before or during the LLM call.
    try:
        reduce_input = "\n\n".join(summaries)
        reduce_input_tokens = count_tokens(reduce_input)
    except Exception as exc:
        yield {
            "stage": "reduce",
            "status": "error",
            "message": (
                f"Failed to prepare reducer input: "
                f"{type(exc).__name__}: {exc}"
            ),
        }
        return

    yield {
        "stage": "reduce",
        "status": "running",
        "message": (
            f"Reducing {len(summaries)} summaries "
            f"· {reduce_input_tokens} input tokens"
        ),
    }

    try:
        final_summary = reduce_summaries(summaries)
    except Exception as exc:
        yield {
            "stage": "reduce",
            "status": "error",
            "message": (
                f"Reduce step failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        }
        return

    if not final_summary.strip():
        yield {
            "stage": "reduce",
            "status": "error",
            "message": "Reduce step returned an empty summary.",
        }
        return

    yield {
        "stage": "reduce",
        "status": "complete",
        "message": "Final summary generated",
    }

    # ============================================================
    # 7. COMPLETE
    # ============================================================

    execution_time = time.perf_counter() - start_time

    yield {
        "stage": "complete",
        "status": "complete",
        "message": "Pipeline complete",
        "result": {
            "video_id":video_id,
            "summary": final_summary,
            "transcript": text,
            "metrics": {
                "transcript_tokens": transcript_tokens,
                "number_of_chunks": len(chunks),
                "map_calls": map_calls,
                "reduce_input_tokens": reduce_input_tokens,
                "execution_time_seconds": round(
                    execution_time,
                    2,
                ),
            },
        },
    }