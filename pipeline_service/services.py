"""
Pipeline Service - Orchestriert den kompletten YouTube zu Quiz Workflow.
"""
from typing import Dict

from youtube_service.services import YouTubeService
from transcription_service.services import TranscriptionService
from quiz_generator_service.services import QuizGeneratorService


class PipelineService:
    """
    Orchestriert die komplette Pipeline von YouTube zu Quiz.
    Nutzt alle anderen Services.
    """
    
    def __init__(self, gemini_api_key: str = None):
        """
        Initialisiere die Pipeline mit allen Services.
        
        Args:
            gemini_api_key: Optional - Google Gemini API-Key
        """
        self.youtube_service = YouTubeService()
        self.transcription_service = TranscriptionService()
        self.quiz_generator = QuizGeneratorService(gemini_api_key)
    
    def process_youtube_url(self, youtube_url: str) -> Dict:
        """
        Verarbeite eine YouTube URL komplett: Download → Transkript → Quiz.
        
        Args:
            youtube_url: URL zu YouTube Video
            
        Returns:
            Dictionary mit Quiz-Daten und Transkript
            
        Raises:
            Exception: Bei Fehler in einem Schritt
        """
        # Schritt 1: Download Audio
        audio_file = self.youtube_service.download_audio(youtube_url)
        
        try:
            # Schritt 2: Transkribiere Audio
            transcript = self._transcribe(audio_file)
            
            # Schritt 3: Generiere Quiz
            quiz_data = self._generate_quiz(transcript)
            
            # Schritt 4: Cleanup
            self.youtube_service.cleanup_file(audio_file)
            
            return quiz_data
        except Exception as e:
            self.youtube_service.cleanup_file(audio_file)
            raise e
    
    def _transcribe(self, audio_file: str) -> str:
        """
        Transkribiere die Audio-Datei.
        
        Args:
            audio_file: Pfad zur Audio-Datei
            
        Returns:
            Transkript als Text
        """
        return self.transcription_service.transcribe_audio(audio_file)
    
    def _generate_quiz(self, transcript: str) -> Dict:
        """
        Generiere das Quiz aus dem Transkript.
        
        Args:
            transcript: Transkript des Videos
            
        Returns:
            Quiz-Daten mit Transkript
        """
        quiz_data = self.quiz_generator.generate_quiz(transcript)
        quiz_data['transcript'] = transcript
        return quiz_data
