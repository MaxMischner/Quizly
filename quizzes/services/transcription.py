"""Audio transcription services."""

import whisper


class TranscriptionService:
    """Transcribe audio files with Whisper."""

    MODEL_SIZE = "base"

    @classmethod
    def transcribe_audio(cls, audio_path: str, language: str = "de") -> str:
        """Transcribe an audio file and return plain text."""
        model = whisper.load_model(cls.MODEL_SIZE)
        result = model.transcribe(audio_path, language=language)
        return result["text"]
