import unittest
from unittest.mock import patch, MagicMock
import os
from extractor import extract_text_from_image

class TestGeminiFallback(unittest.TestCase):
    
    @patch('extractor.os.environ.get')
    @patch('extractor.Mistral')
    @patch('extractor._extract_with_gemini')
    def test_fallback_on_mistral_exception(self, mock_gemini, mock_mistral_cls, mock_env):
        # Setup: Mistral Key present, but Mistral raises exception
        mock_env.return_value = "fake_mistral_key"
        mock_mistral_cls.side_effect = Exception("Mistral Error")
        mock_gemini.return_value = "Gemini Text"
        
        result = extract_text_from_image(b"fake_bytes")
        
        self.assertEqual(result, "Gemini Text")
        mock_gemini.assert_called_once()
        
    @patch('extractor.os.environ.get')
    @patch('extractor.Mistral')
    @patch('extractor._extract_with_gemini')
    def test_fallback_on_empty_mistral_result(self, mock_gemini, mock_mistral_cls, mock_env):
        # Setup: Mistral Key present, Mistral returns empty markdown
        mock_env.return_value = "fake_mistral_key"
        
        mock_client = MagicMock()
        mock_mistral_cls.return_value = mock_client
        
        # Mock response with empty pages or empty markdown
        mock_response = MagicMock()
        mock_page = MagicMock()
        mock_page.markdown = ""
        mock_response.pages = [mock_page]
        mock_client.ocr.process.return_value = mock_response
        
        mock_gemini.return_value = "Gemini Text"
        
        result = extract_text_from_image(b"fake_bytes")
        
        self.assertEqual(result, "Gemini Text")
        mock_gemini.assert_called_once()

    @patch('extractor.os.environ.get')
    @patch('extractor._extract_with_gemini')
    def test_fallback_on_missing_mistral_key(self, mock_gemini, mock_env):
        # Setup: Mistral Key missing
        mock_env.return_value = None
        
        mock_gemini.return_value = "Gemini Text"
        
        result = extract_text_from_image(b"fake_bytes")
        
        self.assertEqual(result, "Gemini Text")
        # Mistral shouldn't even be called, but Gemini should
        mock_gemini.assert_called_once()

if __name__ == '__main__':
    unittest.main()
