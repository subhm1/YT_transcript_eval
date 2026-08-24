import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")


client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"


def summarize_chunk(text):
    prompt = f"""
You are summarizing one section of a larger transcript.

Summarize only information explicitly present in the provided transcript.

Preserve:
- Key claims and ideas
- Important facts, numbers, names, examples, and comparisons
- Conclusions and recommendations
- Important relationships between ideas

Do not:
- Add information from outside the transcript
- Guess missing context
- Resolve references using information not present in the transcript
- Invent facts or interpretations
- Mention the transcript, chunk, or summarization process
- Add an introduction or conclusion outside the bullet points

Output requirements:
- Write 3-7 concise bullet points
- Start every point with "- "
- Output ONLY the bullet points
- Keep the wording factual and faithful to the source

Transcript:
{text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text