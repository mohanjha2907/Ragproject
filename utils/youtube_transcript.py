import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled


def extract_video_id(url: str) -> str:
    """Extract the YouTube video ID from various URL formats."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
        r"(?:embed\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_youtube_transcript(url: str) -> str:
    """
    Fetch the transcript/captions for a YouTube video directly via the
    YouTube Transcript API. This avoids any audio download and works
    from cloud-hosted environments where YouTube blocks yt-dlp.

    Returns the full transcript as a single string.
    Raises an exception if no transcript is available.
    """
    video_id = extract_video_id(url)

    try:
        ytt_api = YouTubeTranscriptApi()

        # List all available transcripts
        transcript_list = ytt_api.list(video_id)

        # Try English transcripts first (manual, then auto-generated), then any language
        transcript = None
        preferred_langs = ["en", "en-US", "en-GB"]

        try:
            transcript = transcript_list.find_manually_created_transcript(preferred_langs)
        except NoTranscriptFound:
            try:
                transcript = transcript_list.find_generated_transcript(preferred_langs)
            except NoTranscriptFound:
                # Fall back to first available transcript translated to English
                available = list(transcript_list)
                if available:
                    transcript = available[0].translate("en")
                else:
                    raise Exception("No transcripts found for this video.")

        # Fetch segments and join into a single string
        segments = transcript.fetch()
        full_text = " ".join(seg.text for seg in segments)
        return full_text.strip()

    except TranscriptsDisabled:
        raise Exception(
            "Transcripts are disabled for this video. "
            "Please try a different video or upload the audio file directly using the 'Upload Audio/Video' option."
        )
    except Exception as e:
        raise Exception(f"Could not fetch transcript from YouTube: {e}")
