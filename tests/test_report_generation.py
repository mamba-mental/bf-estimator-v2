# tests/test_report_generation.py

import unittest
from report_generation import save_report
import os
import json
import base64  # Import base64 for decoding

class TestSaveReport(unittest.TestCase):
    def setUp(self):
        # Setup a temporary results directory
        self.results_folder = os.path.abspath('results')
        os.makedirs(self.results_folder, exist_ok=True)
        self.username = 'TestUser'
        self.report_data = {
            'markdown_content': '# Test Report',
            'pdf_content': b'%PDF-1.4 Test PDF Content',
            'json_content': {'key': 'value'}
        }

    def tearDown(self):
        # Clean up saved files after tests
        for key in ['markdown', 'pdf', 'json']:
            filename = f"{self.username}_20240917_123456.{key if key != 'json' else 'json'}"
            filepath = os.path.join(self.results_folder, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_save_markdown_only(self):
        saved_files = save_report(self.report_data, self.username, 'md')
        self.assertIn('markdown', saved_files)
        self.assertTrue(os.path.exists(saved_files['markdown']))
        with open(saved_files['markdown'], 'r') as f:
            content = f.read()
            self.assertEqual(content, '# Test Report')

    def test_save_pdf_only(self):
        saved_files = save_report(self.report_data, self.username, 'pdf')
        self.assertIn('pdf', saved_files)
        self.assertTrue(os.path.exists(saved_files['pdf']))
        with open(saved_files['pdf'], 'rb') as f:
            content = f.read()
            self.assertEqual(content, b'%PDF-1.4 Test PDF Content')

    def test_save_both(self):
        saved_files = save_report(self.report_data, self.username, 'both')
        self.assertIn('markdown', saved_files)
        self.assertIn('pdf', saved_files)
        self.assertTrue(os.path.exists(saved_files['markdown']))
        self.assertTrue(os.path.exists(saved_files['pdf']))
        with open(saved_files['markdown'], 'r') as f:
            content = f.read()
            self.assertEqual(content, '# Test Report')
        with open(saved_files['pdf'], 'rb') as f:
            content = f.read()
            self.assertEqual(content, b'%PDF-1.4 Test PDF Content')

    def test_save_json_only(self):
        saved_files = save_report(self.report_data, self.username, 'json')
        self.assertIn('json', saved_files)
        self.assertTrue(os.path.exists(saved_files['json']))
        with open(saved_files['json'], 'r') as f:
            data = json.load(f)
            # Decode 'pdf_content' from Base64
            if 'pdf_content' in data:
                data['pdf_content'] = base64.b64decode(data['pdf_content'])
        self.assertEqual(data, self.report_data)

if __name__ == '__main__':
    unittest.main()
