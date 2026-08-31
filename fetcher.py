import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript


class TranscriptFetchError(Exception):
    """Raised when a YouTube transcript cannot be fetched."""


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    if parsed.hostname in {"www.youtube.com", "youtube.com"}:
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    elif parsed.hostname == "youtu.be":
        video_id = parsed.path.strip("/")

    else:
        video_id = None

    if not video_id:
        raise ValueError("Invalid YouTube URL: video ID not found")

    return video_id


def fetch_transcript(video_id: str, languages=None):
    ytt_api = YouTubeTranscriptApi()

    try:
        transcript_list = ytt_api.list(video_id)

        if languages:
            transcript = transcript_list.find_transcript(languages)
        else:
            transcript = transcript_list.find_transcript(["en"])

        return transcript.fetch()

    except Exception as exc:
        raise TranscriptFetchError(
            f"Could not retrieve transcript for video: {video_id}"
        ) from exc


def normalize_transcript(transcript) -> list[dict]:
    return [
        {
            "start": snippet.start,
            "duration": snippet.duration,
            "text": snippet.text,
        }
        for snippet in transcript
    ]


def clean_text(segments: list[dict]) -> str:
    texts = []

    for segment in segments:
        text = segment["text"]

        text = text.replace("\n", " ")
        text = re.sub(r"\[?[♪♫]+\]?", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        if text:
            texts.append(text)

    return " ".join(texts)