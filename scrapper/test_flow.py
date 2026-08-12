import unittest
from unittest.mock import MagicMock, patch
import requests
from session_manager import get_phpsessid
from downloader import download_protected_resource
from processor import process_notice

class TestScraperFlow(unittest.TestCase):
    
    @patch('session_manager.requests.Session')
    def test_get_phpsessid(self, mock_session_cls):
        # Mock session and its behavior
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        
        # Mock cookies
        mock_session.cookies.get.return_value = "test_sess_id"
        
        session = mock_session
        phpsessid = get_phpsessid(session)
        
        self.assertEqual(phpsessid, "test_sess_id")
        
        # Verify specific URL was hit
        mock_session.get.assert_called_with("https://www.imsnsit.org/imsnsit/notifications.php")
        
        # Verify headers were updated
        # session.headers.update is called. Check the args.
        self.assertTrue(session.headers.update.called)
        args, _ = session.headers.update.call_args
        headers_arg = args[0]
        self.assertIn("User-Agent", headers_arg)
        self.assertIn("Referer", headers_arg)
        
    def test_download_protected_resource(self):
        # No need to patch requests here as we pass the session
        session = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.content = b"fake_pdf_content"
        
        session.get.return_value = mock_response
        
        content, ctype = download_protected_resource(session, "http://test.com", phpsessid="12345")
        
        self.assertEqual(content, b"fake_pdf_content")
        self.assertEqual(ctype, "application/pdf")
        
        # Check if cookie header was passed
        args, kwargs = session.get.call_args
        self.assertIn("headers", kwargs)
        self.assertIn("Cookie", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["Cookie"], "PHPSESSID=12345")
        # Check for user provided header
        self.assertEqual(kwargs["headers"]["DNT"], "1")

    @patch('processor.get_phpsessid')
    @patch('processor.download_protected_resource')
    @patch('processor.upload_to_cloudinary')
    def test_process_notice_internal(self, mock_upload, mock_download, mock_get_sessid):
        mock_get_sessid.return_value = "mock_id"
        mock_download.return_value = (b"pdf_bytes", "application/pdf")
        mock_upload.return_value = "http://cloudinary.com/doc.pdf"
        
        session = MagicMock()
        notice = {"link": "http://imsnsit.org/test.pdf", "title": "Test Notice"}
        
        result = process_notice(session, notice)
        
        self.assertEqual(result["cached_url"], "http://cloudinary.com/doc.pdf")
        self.assertEqual(result["status"], "cached")
        
        # Verify flow
        mock_get_sessid.assert_called_once()
        mock_download.assert_called_once_with(session, "http://imsnsit.org/test.pdf", phpsessid="mock_id")

if __name__ == '__main__':
    unittest.main()
