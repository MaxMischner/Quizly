"""AI quiz generation services."""

import json

from google import genai


class QuizGeneratorService:
    """Generate quiz payloads from transcripts using Gemini."""

    MODEL_NAME = "gemini-2.0-flash"

    def __init__(self, api_key: str | None = None):
        """Initialize the Gemini client with an explicit or environment API key."""
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    def generate_quiz(self, transcript: str) -> dict:
        """Generate a quiz object from transcript text."""
        prompt = self._build_prompt(transcript)
        response = self.client.models.generate_content(model=self.MODEL_NAME, contents=prompt)
        return self._parse_response(response.text)

    @staticmethod
    def _build_prompt(transcript: str) -> str:
        """Build the prompt used to request a strict JSON quiz response."""
        return f"""Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{{
  \"title\": \"Create a concise quiz title based on the topic of the transcript.\",
  \"description\": \"Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.\",
  \"questions\": [
    {{
      \"question_title\": \"The question goes here.\",
      \"question_options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],
      \"answer\": \"The correct answer from the above options\"
    }}
  ]
}}

Requirements:
- Generate exactly 10 questions.
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (for example with json.loads).
- Do not include explanations, comments, or any text outside the JSON.
- Do not wrap the JSON in markdown code blocks.

Transcript:
{transcript}
"""

    @staticmethod
    def _parse_response(response_text: str) -> dict:
        """Parse the model response and normalize it to internal quiz structure."""
        try:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()

            json_start = cleaned_text.find("{")
            json_end = cleaned_text.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("JSON not found in model response")

            raw_data = json.loads(cleaned_text[json_start:json_end])
            quiz_data = {
                "title": raw_data.get("title", "Quiz Title"),
                "description": raw_data.get("description", "Quiz Description"),
                "questions": [],
            }

            for index, question in enumerate(raw_data.get("questions", []), start=1):
                question_title = question.get("question_title", "")
                options = question.get("question_options", [])
                correct_answer = question.get("answer", "")
                answers = [
                    {"text": option, "is_correct": option == correct_answer}
                    for option in options
                ]
                quiz_data["questions"].append(
                    {
                        "order": index,
                        "question": question_title,
                        "answers": answers,
                    }
                )

            return quiz_data
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON parse error: {exc}") from exc
