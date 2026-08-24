import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"


def reduce_summaries(summaries):
    summaries_text = "\n\n".join(
        f"Summary {i + 1}:\n{summary}"
        for i, summary in enumerate(summaries)
    )

    prompt = f"""
You are synthesizing multiple summaries of different sections
of the same transcript.

Create one final summary using ONLY information contained
in the provided summaries.

Preserve:
- The main argument or message
- Important facts, numbers, names, and examples
- Important relationships between ideas
- Important conclusions or recommendations

Do not:
- Add information from outside the summaries
- Invent facts
- Repeat the same idea unnecessarily
- Mention chunks, map/reduce, summaries, or the summarization process

Output requirements:
- Write 5-8 concise bullet points
- Start every point with "- "
- Output ONLY the bullet points
- Keep the wording factual and faithful to the source

Input summaries:

{summaries_text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text