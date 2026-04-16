import os
os.environ["OPENAI_API_KEY"] = "mock_key"
import unittest
from unittest.mock import patch, MagicMock
from question_generator import generate_questions

class TestQuestionGenerator(unittest.TestCase):

    def test_empty_input(self):
        result = generate_questions("", "Backend Developer")
        self.assertIn("error", result)

        result = generate_questions("Python dev", "   ")
        self.assertIn("error", result)

    @patch('question_generator.client')
    def test_successful_generation(self, mock_client):
        # Mock successful API response
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
    def test_invalid_json_format(self, mock_client):
        # Mock invalid API response (missing questions)
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"wrong_key": []}'
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_questions("Resume...", "Job Description...")
        self.assertIn("error", result)
        
    @patch('question_generator.client')
    def test_wrong_counts(self, mock_client):
        # Mock API returning wrong ratio
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
          "questions": [
            {"type": "technical", "skill": "Python", "difficulty": "easy", "question": "Q1"},
            {"type": "behavioral", "skill": "Teamwork", "difficulty": "easy", "question": "Q2"}
          ]
        }
        ''' # Only 1 technical and 1 behavioral
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_questions("Resume...", "Job Description...")
        self.assertIn("error", result)
        self.assertIn("failed to strictly generate 5 technical and 2 behavioral", result["error"])

if __name__ == '__main__':
    unittest.main()
