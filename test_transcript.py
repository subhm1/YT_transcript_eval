from youtube_transcript_api import YouTubeTranscriptApi

video_id = "dQw4w9WgXcQ"

ytt_api = YouTubeTranscriptApi()

transcript = ytt_api.fetch(video_id)

print(f"Number of snippets: {len(transcript)}")

for snippet in transcript[:5]:
    print(snippet)