from fetcher import (
    extract_video_id,
    fetch_transcript,
    normalize_transcript,
    clean_text,
    TranscriptFetchError,
)


url = "https://www.youtube.com/watch?v=3YZ5Nv-q0YI"

try:
    video_id = extract_video_id(url)

    transcript = fetch_transcript(video_id, languages=["hi"])
    normalized = normalize_transcript(transcript)
    text = clean_text(normalized)

    print(f"Video ID: {video_id}")
    print(f"Segments: {len(normalized)}")
    print(f"\nClean text:\n{text}")

except TranscriptFetchError as exc:
    print(f"ERROR: {exc}")