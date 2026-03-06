"""YouTube download and audio extraction services."""

import os
from pathlib import Path

import yt_dlp


class YouTubeService:
    """Download YouTube audio and clean temporary files."""

    OUTPUT_PATH = "temp_downloads"

    @classmethod
    def download_audio(cls, youtube_url: str) -> str:
        """Download and convert YouTube audio to MP3, then return the file path."""
        Path(cls.OUTPUT_PATH).mkdir(exist_ok=True)

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": os.path.join(cls.OUTPUT_PATH, "%(title)s"),
            "quiet": False,
            "no_warnings": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            audio_file = ydl.prepare_filename(info)
            audio_file = os.path.splitext(audio_file)[0] + ".mp3"

        return audio_file

    @staticmethod
    def cleanup_file(file_path: str) -> None:
        """Delete a temporary file when it exists."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
