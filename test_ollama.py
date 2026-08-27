import time
import ollama


text = """
Large language models process text by converting it into tokens. These tokens
are the basic units that the model processes, rather than whole words or
sentences directly. Because every model has a finite context window, there is
a limit to how many tokens can be supplied in a single request. Long YouTube
transcripts can therefore exceed the available context window and need to be
divided into smaller sections.

Chunking a transcript should ideally preserve meaningful semantic boundaries.
Splitting purely by character count can cut ideas in the middle of sentences.
A token-based chunking strategy provides a predictable input budget, while
sentence or paragraph boundaries help preserve meaning. Overlap between
chunks can also preserve context when an idea spans two neighboring chunks.

After chunking, each section can be independently summarized. These individual
summaries can then be combined in a reduction step to produce one final
summary. This Map-Reduce approach allows a long transcript to be processed
without sending the entire transcript to the model in one request.
"""

prompt = f"""
Summarize the following transcript section.

Requirements:
- Output only 3-7 concise bullet points.
- Start every bullet with "- ".
- Preserve important technical concepts.
- Do not add information that is not present.
- Do not mention the summarization process.

Transcript:
{text}
"""

start = time.perf_counter()

response = ollama.chat(
    model="qwen2.5:3b",
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    options={
        "num_ctx": 2048,
        "num_predict": 150,
    },
)

elapsed = time.perf_counter() - start

print(response["message"]["content"])
print()
print(f"Time taken: {elapsed:.2f} seconds")
print(f"Prompt tokens: {response.get('prompt_eval_count')}")
print(f"Generated tokens: {response.get('eval_count')}")
print(
    f"Prompt evaluation: "
    f"{response.get('prompt_eval_duration', 0) / 1e9:.2f}s"
)
print(
    f"Generation: "
    f"{response.get('eval_duration', 0) / 1e9:.2f}s"
)

if response.get("eval_duration") and response.get("eval_count"):
    tok_per_sec = (
        response["eval_count"]
        / (response["eval_duration"] / 1e9)
    )
    print(f"Generation speed: {tok_per_sec:.2f} tokens/sec")