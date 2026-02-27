"""
Quiz Generator Service - Quiz-Generierung mit Google Gemini AI.
"""
import os
import json
import google.generativeai as genai


class QuizGeneratorService:
    """
    Service zur Generierung von Quizzes mit Google Gemini Flash AI.
    """
    
    MODEL_NAME = "gemini-1.5-flash"
    
    def __init__(self, api_key: str = None):
        """
        Initialisiere den Service mit API-Key.
        
        Args:
            api_key: Google Gemini API-Key (oder aus .env laden)
            
        Raises:
            ValueError: Wenn kein API-Key vorhanden ist
        """
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY nicht gesetzt!")
        genai.configure(api_key=api_key)
    
    @classmethod
    def generate_quiz(cls, transcript: str) -> dict:
        """
        Generiere ein Quiz aus einem Transkript.
        
        Args:
            transcript: Text-Transkript des Videos
            
        Returns:
            Dictionary mit Quiz-Struktur (Titel, Fragen, Antworten)
            
        Raises:
            ValueError: Wenn Quiz-Generierung fehlschlägt
        """
        model = genai.GenerativeModel(cls.MODEL_NAME)
        
        prompt = cls._build_prompt(transcript)
        response = model.generate_content(prompt)
        
        quiz_data = cls._parse_response(response.text)
        return quiz_data
    
    @staticmethod
    def _build_prompt(transcript: str) -> str:
        """
        Erstelle den Prompt für die AI.
        
        Args:
            transcript: Transkript des Videos
            
        Returns:
            Formatierter Prompt für Gemini
        """
        return f"""
Basierend auf folgendem Text, erstelle ein Quiz mit genau 10 Fragen.
Jede Frage soll genau 4 Antwortmöglichkeiten haben.

Antworte NUR mit gültigem JSON in diesem Format:
{{
    "title": "Quiz Titel basierend auf dem Inhalt",
    "description": "Kurze Beschreibung des Quiz",
    "questions": [
        {{
            "order": 1,
            "question": "Erste Frage?",
            "answers": [
                {{"text": "Richtige Antwort", "is_correct": true}},
                {{"text": "Falsche Antwort 1", "is_correct": false}},
                {{"text": "Falsche Antwort 2", "is_correct": false}},
                {{"text": "Falsche Antwort 3", "is_correct": false}}
            ]
        }}
    ]
}}

TEXT:
{transcript}
"""
    
    @staticmethod
    def _parse_response(response_text: str) -> dict:
        """
        Parse die AI-Response zu JSON.
        
        Args:
            response_text: Response-Text von der AI
            
        Returns:
            Geparste Quiz-Daten als Dictionary
            
        Raises:
            ValueError: Wenn JSON ungültig ist
        """
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("JSON nicht in Response gefunden")
            
            json_str = response_text[json_start:json_end]
            quiz_data = json.loads(json_str)
            
            return quiz_data
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON Parse Error: {str(e)}")
