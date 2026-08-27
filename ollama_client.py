import ollama


MODEL_NAME = "qwen3:4b"


def summarize_chunk(text: str) -> str:
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

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        think=False,
        options={
            "num_ctx": 2048,
            "num_predict": 150,
        },
    )

    return response["message"]["content"]