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
            "Invalid YouTube URL."
        ) from exc

    # 2. Fetch transcript
    try:
        transcript = fetch_transcript(
            video_id,
            languages=["hi"],
        )
    except Exception as exc:
        raise RuntimeError(
            "Transcript fetch failed."
        ) from exc

    # 3. Normalize and clean transcript
    try:
        segments = normalize_transcript(transcript)
        text = clean_text(segments)
    except Exception as exc:
        raise RuntimeError(
            "Transcript normalization or cleaning failed."
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
            "Transcript chunking failed."
        ) from exc

    if not chunks:
        raise ValueError(
            "Chunking produced no chunks."
        )

    # 5. Map: summarize each chunk
    summaries = []
    map_calls = 0

    for chunk in chunks:
        try:
            summary = summarize_chunk(chunk["text"])
            map_calls += 1
        except Exception as exc:
            raise RuntimeError(
                "Map step failed while summarizing a transcript chunk."
            ) from exc

        if not summary.strip():
            raise RuntimeError(
                "Map step returned an empty summary."
            )

        summaries.append(summary)

    # 6. Reduce: combine all chunk summaries
    reduce_input = "\n\n".join(summaries)
    reduce_input_tokens = count_tokens(reduce_input)

    try:
        final_summary = reduce_summaries(summaries)
    except Exception as exc:
        raise RuntimeError(
            "Reduce step failed while generating the final summary."
        ) from exc

    if not final_summary.strip():
        raise RuntimeError(
            "Reduce step returned an empty final summary."
        )

    execution_time = time.perf_counter() - start_time

    return {
        "summary": final_summary,
        "metrics": {
            "transcript_tokens": transcript_tokens,
            "number_of_chunks": len(chunks),
            "map_calls": map_calls,
            "reduce_input_tokens": reduce_input_tokens,
            "execution_time_seconds": round(execution_time, 2),
        },
    }