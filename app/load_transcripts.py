import os
from urllib.parse import urlparse, parse_qs
import json

from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube


class NoMachingTranscriptFoundError(BaseException):
    def __str__(self):
        return "Could not detect any Japanese transcripts for the provided video. If this seems to be a mistake, please contact the developer."


class InvalidYoutubeUrl(BaseException):
    def __str__(self):
        return "The provided URL does not seem to be a valid Youtube URL. If this seems to be a mistake, please contact the developer."


def get_youtube_video_id_from_url(url: str) -> str:
    """
    Extracts the video ID from a YouTube video URL.

    Args:
    - url (str): YouTube video URL.

    Returns:
    - str: Video ID if found
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if "v" in query_params:
        return query_params["v"][0]
    elif "watch" in parsed_url.path:
        # Handle URLs with /watch without query parameters
        path_segments = parsed_url.path.split("/")
        if len(path_segments) > 1:
            return path_segments[-1]

    raise InvalidYoutubeUrl()


def _get_best_transcript(videoId: str, targetLang: str) -> str:
    """
    Returns human-created transcripts if possible, otherwise generated transcripts
    """
    bestTranscript = None
    for transcript in YouTubeTranscriptApi.list_transcripts(videoId):
        if transcript.language_code == targetLang:
            bestTranscript = transcript

            if transcript.is_generated:
                break

    if bestTranscript:
        return bestTranscript.fetch()
    else:
        return None


def _get_metadata(url: str) -> str:
    try:
        yt = YouTube(url)
        return {
            "author": yt.author,
            "title": yt.title,
            "publish_date": str(yt.publish_date),
            "id": yt.video_id,
            "description": yt.description,
        }
    except Exception:
        return None


def loadTranscript(url: str, outputPath: str, targetLang: str) -> dict:
    videoId = get_youtube_video_id_from_url(url)
    if videoId is None:
        return None

    serializedTranscriptFn = os.path.join(outputPath, f"{videoId}_{targetLang}.json")
    if os.path.exists(serializedTranscriptFn):
        with open(serializedTranscriptFn, "r") as fd:
            transcriptData = json.loads(fd.read())

    else:
        transcript = _get_best_transcript(videoId, targetLang)
        metadata = _get_metadata(url)
        print(metadata)
        transcriptData = {"transcript": transcript, "metadata": metadata}

        if transcript is None:
            raise NoMachingTranscriptFoundError
        with open(serializedTranscriptFn, "w") as fd:
            fd.write(json.dumps(transcriptData))

    return transcriptData


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=eCSZNINKOKk"
    url = "https://www.youtube.com/watch?v=WBA5aS7pHUE"
    outputPath = "./transcripts"
    transcript = loadTranscript(url, outputPath, "ja")
    print(transcript)
