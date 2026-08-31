import json

import ollama


MODEL_NAME = "qwen3:4b"


JUDGE_PROMPT = """
You are evaluating the quality of a generated summary of a transcript.

You have three inputs:

1. ORIGINAL TRANSCRIPT
2. REFERENCE SUMMARY
3. GENERATED SUMMARY

Evaluate the GENERATED SUMMARY only.

Scoring:

COVERAGE:
1 = misses almost all important information
2 = captures a small amount of important information
3 = captures some important information but misses substantial content
4 = captures most important information
5 = captures essentially all important information

FAITHFULNESS:
1 = contains major unsupported or contradictory claims
2 = contains several unsupported or inaccurate claims
3 = mostly supported but has some questionable claims
4 = almost entirely supported by the transcript
5 = all substantive claims are clearly supported by the transcript

CONCISENESS:
1 = extremely verbose, repetitive, or filled with irrelevant information
2 = noticeably verbose or repetitive
3 = acceptable but could be tighter
4 = concise with little unnecessary information
5 = highly concise while preserving important information

OVERALL:
Give an overall score from 1 to 5 based on the three dimensions.

Important:
- The ORIGINAL TRANSCRIPT is the source of truth for factual support.
- Use the REFERENCE SUMMARY to judge whether important information was covered.
- Do not assume information is true merely because it appears in the reference summary.
- Do not reward the generated summary simply for being detailed.
- Penalize unsupported claims, contradictions, truncation, and major omissions.

Return ONLY valid JSON.
Do not use markdown.
Do not include additional fields.

JSON format:
{{
  "coverage": <integer 1-5>,
  "faithfulness": <integer 1-5>,
  "conciseness": <integer 1-5>,
  "overall": <integer 1-5>,
  "reason": "<brief explanation>"
}}

ORIGINAL TRANSCRIPT:
{transcript}

REFERENCE SUMMARY:
{reference_summary}

GENERATED SUMMARY:
{generated_summary}
"""


def judge_summary(
    transcript: str,
    reference_summary: str,
    generated_summary: str,
) -> dict:

    prompt = JUDGE_PROMPT.format(
        transcript=transcript,
        reference_summary=reference_summary,
        generated_summary=generated_summary,
    )

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
            "coverage": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
            },
            "faithfulness": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
            },
            "conciseness": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
            },
            "overall": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
            },
            "reason": {
                "type": "string",
            },
        },
        "required": [
            "coverage",
            "faithfulness",
            "conciseness",
            "overall",
            "reason",
        ],
    },
    options={
        "num_ctx": 8192,
        "num_predict": 300,
    },
)

    content = response["message"]["content"].strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Judge returned invalid JSON: {content}"
        ) from exc

    required_fields = {
        "coverage",
        "faithfulness",
        "conciseness",
        "overall",
        "reason",
    }

    if set(result.keys()) != required_fields:
        raise RuntimeError(
            "Judge returned unexpected fields."
        )

    for field in [
        "coverage",
        "faithfulness",
        "conciseness",
        "overall",
    ]:
        if not isinstance(result[field], int):
            raise RuntimeError(
                f"Judge field '{field}' must be an integer."
            )

        if not 1 <= result[field] <= 5:
            raise RuntimeError(
                f"Judge field '{field}' must be between 1 and 5."
            )

    if not isinstance(result["reason"], str):
        raise RuntimeError(
            "Judge field 'reason' must be a string."
        )

    return result