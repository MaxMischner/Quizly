"""
Quiz Generator Service - Quiz-Generierung mit Google Gemini AI.
"""
import os
import json
from google import genai


class QuizGeneratorService:
    """
    Service zur Generierung von Quizzes mit Google Gemini Flash AI.
    """
    
    MODEL_NAME = "gemini-2.0-flash"
    
    def __init__(self, api_key: str = None):
        """
        Initialisiere den Service mit API-Key.
        
        Args:
            api_key: Google Gemini API-Key (oder aus .env laden)
            
        Raises:
            ValueError: Wenn kein API-Key vorhanden ist
        """
        if api_key:
            # Expliziter API-Key übergeben
            self.client = genai.Client(api_key=api_key)
        else:
            # Client lädt GEMINI_API_KEY automatisch aus Umgebungsvariablen
            self.client = genai.Client()
    
    def generate_quiz(self, transcript: str) -> dict:
        """
        Generiere ein Quiz aus einem Transkript.
        
        Args:
            transcript: Text-Transkript des Videos
            
        Returns:
            Dictionary mit Quiz-Struktur (Titel, Fragen, Antworten)
            
        Raises:
            ValueError: Wenn Quiz-Generierung fehlschlägt
        """
        prompt = self._build_prompt(transcript)
        
        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=prompt
        )
        
        quiz_data = self._parse_response(response.text)
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
        return f"""Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {{
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    }}
  ]
}}

Requirements:
- Generate exactly 10 questions.
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON.
- Do not wrap the JSON in markdown code blocks (no ```json or ```).

Transcript:
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
            # Remove markdown code blocks if present
            cleaned_text = response_text.strip()
            
            # Remove ```json at start
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            
            # Remove ``` at end
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Find JSON boundaries
            json_start = cleaned_text.find('{')
            json_end = cleaned_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("JSON nicht in Response gefunden")
            
            json_str = cleaned_text[json_start:json_end]
            raw_data = json.loads(json_str)
            
            # Convert from Gemini format to our internal format
            quiz_data = {
                'title': raw_data.get('title', 'Quiz Title'),
                'description': raw_data.get('description', 'Quiz Description'),
                'questions': []
            }
            
            for idx, q in enumerate(raw_data.get('questions', []), start=1):
                question_title = q.get('question_title', '')
                options = q.get('question_options', [])
                correct_answer = q.get('answer', '')
                
                answers = []
                for opt in options:
                    answers.append({
                        'text': opt,
                        'is_correct': opt == correct_answer
                    })
                
                quiz_data['questions'].append({
                    'order': idx,
                    'question': question_title,
                    'answers': answers
                })
            
            return quiz_data
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON Parse Error: {str(e)}")

