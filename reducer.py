import ollama


MODEL_NAME = "qwen3:4b"


def reduce_summaries(summaries: list[str]) -> str:
    summaries_text = "\n\n".join(
        f"Summary {i + 1}:\n{summary}"
        for i, summary in enumerate(summaries)
    )

    prompt = f"""
You are a factual synthesis system.

Combine the information from the input summaries into one final summary.

STRICT RULES:
- Preserve every distinct important idea from the input.
- Do not add information that is not present.
- Do not invent facts.
- Do not merge unrelated ideas just to reduce the number of bullets.
- Do not mention the input summaries.
- Do not mention the summarization process.
- Do not explain your reasoning.
- Output 3 to 8 concise bullet points.
- Every bullet MUST start with "- ".
- Output ONLY the bullet points.

Input summaries:

{summaries_text}

Final summary:
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
            "temperature": 0.2,
        },
    )

    raw_output = response["message"]["content"]

    # Keep only lines that follow the required bullet format.
    bullets = [
        line.strip()
        for line in raw_output.splitlines()
        if line.strip().startswith("- ")
    ]

    if not bullets:
        raise RuntimeError(
            "Reducer produced no valid bullet points."
        )

    return "\n".join(bullets[:8])