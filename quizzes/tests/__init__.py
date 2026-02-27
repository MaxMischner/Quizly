"""
Quizzes Test Package.
"""
from .test_quiz_create import QuizCreateTests
from .test_quiz_list import QuizListTests
from .test_quiz_detail import QuizDetailTests
from .test_quiz_update import QuizPartialUpdateTests
from .test_quiz_delete import QuizDeleteTests
from .test_quiz_actions import QuizStartTests, QuizSubmitAnswerTests, QuizCompleteTests
from .test_quiz_filters import QuizTodayTests, QuizLastSevenDaysTests

__all__ = [
    'QuizCreateTests',
    'QuizListTests',
    'QuizDetailTests',
    'QuizPartialUpdateTests',
    'QuizDeleteTests',
    'QuizStartTests',
    'QuizSubmitAnswerTests',
    'QuizCompleteTests',
    'QuizTodayTests',
    'QuizLastSevenDaysTests',
]
