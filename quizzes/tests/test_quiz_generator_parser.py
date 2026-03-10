"""Tests for quiz generator parsing helpers."""

from django.test import SimpleTestCase

from quizzes.services.quiz_generator import QuizGeneratorService


class QuizGeneratorParserTests(SimpleTestCase):
    """Validate parser behavior for markdown-wrapped model output."""

    def test_parse_response_accepts_json_code_fence_uppercase(self):
        response_text = """```JSON
        {
          \"title\": \"Demo\",
          \"description\": \"Kurz\",
          \"questions\": [
            {
              \"question_title\": \"Frage 1\",
              \"question_options\": [\"A\", \"B\", \"C\", \"D\"],
              \"answer\": \"A\"
            }
          ]
        }
        ```"""

        parsed = QuizGeneratorService._parse_response(response_text)

        self.assertEqual(parsed["title"], "Demo")
        self.assertEqual(len(parsed["questions"]), 1)
        self.assertEqual(parsed["questions"][0]["question"], "Frage 1")
        self.assertEqual(len(parsed["questions"][0]["answers"]), 4)

    def test_parse_response_accepts_plain_code_fence(self):
        response_text = """```
        {
          \"title\": \"Demo 2\",
          \"description\": \"Kurz\",
          \"questions\": []
        }
        ```"""

        parsed = QuizGeneratorService._parse_response(response_text)
        self.assertEqual(parsed["title"], "Demo 2")
