"""AI quiz generation services."""

import json
import os
import re
import time

from google import genai


class QuizGeneratorService:
    """Generate quiz payloads from transcripts using Gemini."""

    MODEL_NAME = "gemini-2.0-flash"
    DEFAULT_MODEL_CANDIDATES = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
    ]

    def __init__(self, api_key: str | None = None):
        """Initialize the Gemini client with an explicit or environment API key."""
        resolved_api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if resolved_api_key:
            self.client = genai.Client(api_key=resolved_api_key)
            return
        self.client = genai.Client()

    def generate_quiz(self, transcript: str) -> dict:
        """Generate a quiz object from transcript text."""
        prompt = self._build_prompt(transcript)
        last_error = None

        for model_name in self._get_model_candidates():
            try:
                response_text = self._generate_with_retries(model_name, prompt)
                return self._parse_response(response_text)
            except Exception as exc:
                last_error = exc
                # Try next model only for transient/quota/model-availability failures.
                if not self._is_fallback_eligible_error(exc):
                    raise

        if last_error:
            raise last_error
        raise RuntimeError("No model candidates available for quiz generation")

    def _get_model_candidates(self) -> list[str]:
        """Return ordered model candidates from env var or defaults."""
        configured = os.getenv("GEMINI_MODEL_CANDIDATES", "").strip()
        if configured:
            candidates = [item.strip() for item in configured.split(",") if item.strip()]
        else:
            candidates = [self.MODEL_NAME] + [
                model for model in self.DEFAULT_MODEL_CANDIDATES if model != self.MODEL_NAME
            ]

        # Keep order but remove duplicates.
        deduped = list(dict.fromkeys(candidates))
        return deduped

    def _generate_with_retries(self, model_name: str, prompt: str) -> str:
        """Call Gemini with short exponential backoff for transient failures."""
        retry_delays = [0.6, 1.2]
        attempts = len(retry_delays) + 1

        for attempt in range(attempts):
            try:
                response = self.client.models.generate_content(model=model_name, contents=prompt)
                return response.text
            except Exception as exc:
                if attempt == attempts - 1 or not self._is_retryable_error(exc):
                    raise
                time.sleep(retry_delays[attempt])

        raise RuntimeError("Retry loop exited unexpectedly")

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        """Return True for transient backend errors where retry can help."""
        message = str(exc).upper()
        return any(
            token in message
            for token in [
                "429",
                "RESOURCE_EXHAUSTED",
                "503",
                "UNAVAILABLE",
                "504",
                "DEADLINE_EXCEEDED",
            ]
        )

    @staticmethod
    def _is_fallback_eligible_error(exc: Exception) -> bool:
        """Return True when switching to another model is a sensible fallback."""
        message = str(exc).upper()
        return any(
            token in message
            for token in [
                "429",
                "RESOURCE_EXHAUSTED",
                "503",
                "UNAVAILABLE",
                "504",
                "DEADLINE_EXCEEDED",
                "404",
                "NOT_FOUND",
            ]
        )

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
    }},
    ...
    (exactly 10 questions)
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
    def _strip_markdown_fences(text: str) -> str:
        """Remove optional markdown code fences around model output."""
        cleaned = text.strip()
        # Handle ```json, ```JSON and plain ``` wrappers.
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    @staticmethod
    def _parse_response(response_text: str) -> dict:
        """Parse the model response and normalize it to internal quiz structure."""
        try:
            cleaned_text = QuizGeneratorService._strip_markdown_fences(response_text)

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
