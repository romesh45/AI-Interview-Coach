import os
os.environ["OPENAI_API_KEY"] = "mock_key"
import unittest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from question_generator import generate_questions
from evaluator import evaluate_answer

class TestQuestionGenerator(unittest.TestCase):

    def test_empty_input(self):
        result = generate_questions("", "Backend Developer")
        self.assertIn("error", result)
        result = generate_questions("Python dev", "   ")
        self.assertIn("error", result)

    @patch('question_generator.client')
    def test_successful_generation(self, mock_client):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
          "questions": [
            {"type": "technical", "skill": "Python", "difficulty": "easy", "question": "What is a list comprehension?"},
            {"type": "technical", "skill": "Flask", "difficulty": "medium", "question": "How do you handle routing in Flask?"},
            {"type": "technical", "skill": "API", "difficulty": "medium", "question": "Explain RESTful API principles."},
            {"type": "technical", "skill": "Database", "difficulty": "hard", "question": "How to optimize expensive queries?"},
            {"type": "technical", "skill": "Git", "difficulty": "easy", "question": "What is a merge conflict?"},
            {"type": "behavioral", "skill": "Teamwork", "difficulty": "medium", "question": "Tell me about a time you disagreed with your lead."},
            {"type": "behavioral", "skill": "Time Management", "difficulty": "medium", "question": "How do you prioritize tight deadlines?"}
          ]
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        result = generate_questions("Resume...", "Job Description...")
        self.assertNotIn("error", result)
        self.assertEqual(len(result["technical"]), 5)
        self.assertEqual(len(result["behavioral"]), 2)

    @patch('question_generator.client')
    def test_wrong_counts(self, mock_client):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"questions": [{"type": "technical", "skill": "Python", "difficulty": "easy", "question": "Q1"}]}'
        mock_client.chat.completions.create.return_value = mock_response
        result = generate_questions("Resume...", "Job Description...")
        self.assertIn("error", result)


class TestEvaluator(unittest.TestCase):

    def test_empty_input(self):
        result = evaluate_answer("", "some answer")
        self.assertIn("error", result)
        result = evaluate_answer("some question", "")
        self.assertIn("error", result)

    @patch('evaluator.client')
    def test_successful_evaluation(self, mock_client):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
          "score": 8,
          "feedback": "Good answer with clear explanation.",
          "strengths": ["Clear communication", "Correct answer"],
          "gaps": ["Missing edge cases"],
          "improvement_suggestions": ["Add examples", "Mention time complexity", "Cover edge cases"]
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        result = evaluate_answer("What is a list?", "A list is a mutable ordered collection.")
        self.assertNotIn("error", result)
        self.assertEqual(result["score"], 8)
        self.assertEqual(len(result["improvement_suggestions"]), 3)


if __name__ == '__main__':
    unittest.main()
