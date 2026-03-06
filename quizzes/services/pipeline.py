"""Pipeline orchestration for YouTube to quiz processing."""

from typing import Dict

from quizzes.services.quiz_generator import QuizGeneratorService
from quizzes.services.transcription import TranscriptionService
from quizzes.services.youtube import YouTubeService


class PipelineService:
    """Run download, transcription, and quiz generation in sequence."""

    def __init__(self, gemini_api_key: str | None = None):
        """Initialize dependent services."""
        self.youtube_service = YouTubeService()
        self.transcription_service = TranscriptionService()
        self.quiz_generator = QuizGeneratorService(gemini_api_key)

    def process_youtube_url(self, youtube_url: str) -> Dict:
        """Process a YouTube URL and return generated quiz data."""
        audio_file = self.youtube_service.download_audio(youtube_url)
        try:
            transcript = self.transcription_service.transcribe_audio(audio_file)
            quiz_data = self.quiz_generator.generate_quiz(transcript)
            quiz_data["transcript"] = transcript
            self.youtube_service.cleanup_file(audio_file)
            return quiz_data
        except Exception:
            self.youtube_service.cleanup_file(audio_file)
            raise
