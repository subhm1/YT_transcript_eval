import json

import ollama


MODEL_NAME = "qwen3:4b"


def reduce_summaries(summaries: list[str]) -> str:
    if not summaries:
        raise ValueError("Reducer received no summaries.")

    summaries_text = "\n\n".join(
        f"SECTION {i + 1}:\n{summary}"
        for i, summary in enumerate(summaries)
    )

    prompt = f"""
/no_think

Combine the following text sections into one concise factual summary.

Do not analyze the task.
Do not explain your reasoning.
Do not repeat the instructions.
Do not add information that is not present.

Return ONLY JSON.

The JSON must contain exactly one field:

{{
  "bullets": [
    "bullet 1",
    "bullet 2",
    "bullet 3"
  ]
}}

Requirements:
- 3 to 8 bullets.
- Preserve important information from the sections.
- Every bullet must be concise.
- Do not invent facts.
- Do not mention the sections.
- Do not mention the summarization process.
- Do NOT include "- " at the beginning of bullet strings.

TEXT SECTIONS:

{summaries_text}
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
        format={
            "type": "object",
            "properties": {
                "bullets": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 3,
                    "maxItems": 8,
                }
            },
            "required": ["bullets"],
        },
        options={
            "num_ctx": 4096,
            "num_predict": 250,
            "temperature": 0,
        },
    )

    raw_output = response["message"]["content"].strip()

    if not raw_output:
        raise RuntimeError(
            "Reducer returned empty output."
        )


    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Reducer returned invalid JSON: {raw_output!r}"
        ) from exc

    if not isinstance(result, dict):
        raise RuntimeError(
            "Reducer JSON output must be an object."
        )

    if set(result.keys()) != {"bullets"}:
        raise RuntimeError(
            "Reducer returned unexpected JSON fields."
        )

    bullets = result["bullets"]

    if not isinstance(bullets, list):
        raise RuntimeError(
            "Reducer 'bullets' field must be a list."
        )

    cleaned_bullets = []

    for bullet in bullets:
        if not isinstance(bullet, str):
            continue

        bullet = bullet.strip()

        if not bullet:
            continue

        # Remove an existing markdown bullet prefix.
        if bullet.startswith("- "):
            bullet = bullet[2:].strip()

        # Handle accidental repeated prefixes such as:
        # "- - Some text"
        while bullet.startswith("- "):
            bullet = bullet[2:].strip()

        if bullet:
            cleaned_bullets.append(bullet)

    bullets = cleaned_bullets

    if not 3 <= len(bullets) <= 8:
        raise RuntimeError(
            f"Reducer must return 3-8 bullets, got {len(bullets)}."
        )

    return "\n".join(
        f"- {bullet}"
        for bullet in bullets
    )