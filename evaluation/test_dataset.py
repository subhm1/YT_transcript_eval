from youtube_transcript_api import YouTubeTranscriptApi


VIDEOS = [
    ("D9Ihs241zeg", "The Danger of a Single Story"),
    ("Ks-_Mh1QhMc", "Your Body Language May Shape Who You Are"),
    ("yqc9zX04DXs", "The History of Our World in 18 Minutes"),
]


ytt_api = YouTubeTranscriptApi()


for video_id, title in VIDEOS:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    try:
        transcript_list = ytt_api.list(video_id)

        transcript = transcript_list.find_transcript(["en"])

        print(f"Language: {transcript.language}")
        print(f"Language code: {transcript.language_code}")
        print(f"Auto-generated: {transcript.is_generated}")

    except Exception as exc:
        print(f"FAILED: {exc}")