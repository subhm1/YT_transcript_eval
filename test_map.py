import json

from chunker import chunk_text
from gemini_client import summarize_chunk


with open("data_test_transcript.txt", encoding="utf-8") as f:
    text = f.read()


chunks = chunk_text(
    text,
    max_tokens=1000,
    overlap_tokens=100,
)


summaries = []

for i, chunk in enumerate(chunks, start=1):
    print(f"\nProcessing chunk {i}/{len(chunks)}...")
    print(f"Tokens: {chunk['token_count']}")

    summary = summarize_chunk(chunk["text"])

    summaries.append({
        "chunk_number": i,
        "token_count": chunk["token_count"],
        "summary": summary,
    })


with open("map_summaries.json", "w", encoding="utf-8") as f:
    json.dump(summaries, f, ensure_ascii=False, indent=2)


print("\nMAP STEP COMPLETE")
print(f"Chunks processed: {len(summaries)}")
print("Saved to: map_summaries.json")