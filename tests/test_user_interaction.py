# tests\test_user_interaction.py
import unittest
from unittest.mock import patch
from io import StringIO
from datetime import datetime
from user_interaction import (
    get_float_input, get_int_input, get_experience_level_input,
    get_date_input, get_yes_no_input, get_choice_input
)

class TestUserInteraction(unittest.TestCase):
    @patch('builtins.input', return_value='75.5')
    def test_get_float_input(self, mock_input):
        result = get_float_input("Enter weight: ")
        self.assertEqual(result, 75.5)

    @patch('builtins.input', return_value='5')
    def test_get_int_input(self, mock_input):
        result = get_int_input("Enter height in feet: ")
        self.assertEqual(result, 5)

    @patch('builtins.input', return_value='3')
    def test_get_experience_level_input(self, mock_input):
        result = get_experience_level_input("Enter experience level: ")
        self.assertEqual(result, "Intermediate (2-4 years)")

    @patch('builtins.input', return_value='090124')
    def test_get_date_input(self, mock_input):
        result = get_date_input("Enter date: ")
        self.assertEqual(result, datetime(2024, 9, 1))

    @patch('builtins.input', return_value='y')
    def test_get_yes_no_input(self, mock_input):
        result = get_yes_no_input("Are you an athlete? ")
        self.assertTrue(result)

    @patch('builtins.input', return_value='2')
    def test_get_choice_input(self, mock_input):
        choices = [
            ("1", "Option 1"),
            ("2", "Option 2"),
            ("3", "Option 3")
        ]
        result = get_choice_input("Choose an option: ", choices)
        self.assertEqual(result, "2")

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_input(self, mock_stdout):
        with patch('builtins.input', side_effect=['invalid', '75.5']):
            result = get_float_input("Enter weight: ")
        self.assertEqual(result, 75.5)
        self.assertIn("Invalid input", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()