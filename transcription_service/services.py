"""
Transcription Service - Audio zu Text Konvertierung mit Whisper AI.
"""
import whisper


class TranscriptionService:
    """
    Service zum Transkribieren von Audio-Dateien mit Whisper AI.
    """
    
    MODEL_SIZE = "base"  # base, small, medium, large
    
    @classmethod
    def transcribe_audio(cls, audio_path: str, language: str = "de") -> str:
        """
        Transkribiere eine Audio-Datei mit Whisper.
        
        Args:
            audio_path: Pfad zur Audio-Datei (MP3, WAV, etc.)
            language: Sprachen-Code (de, en, fr, etc.)
            
        Returns:
            Vollständiges Transkript als Text
            
        Raises:
            Exception: Bei Transkriptions-Fehlern
        """
        model = whisper.load_model(cls.MODEL_SIZE)
        result = model.transcribe(audio_path, language=language)
        return result["text"]
