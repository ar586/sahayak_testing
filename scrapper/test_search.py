import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Adjust path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import search_notices
from chat_api import app
from fastapi.testclient import TestClient

client = TestClient(app)

class TestSearch(unittest.TestCase):
    
    @patch('database.get_db')
    def test_search_notices_db_function(self, mock_get_db):
        # Mock DB and Collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        # Mock cursor
        mock_cursor = MagicMock()
        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
        
        # Mock Data
        mock_notice = {
            "_id": "123",
            "title": "Test Notice",
            "date": "01-01-2025",
            "summary": "This is a test summary",
            "tags": {},
            "cached_url": "http://example.com"
        }
        mock_cursor.__iter__.return_value = [mock_notice]
        
        # Call function
        results = search_notices("Test")
        
        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Test Notice")
        
        # Verify query structure
        args, _ = mock_collection.find.call_args
        query_filter = args[0]
        self.assertIn("$or", query_filter)
        self.assertIn("status", query_filter)

    @patch('database.search_notices')
    def test_search_endpoint(self, mock_search_notices):
        # Mock return value
        mock_search_notices.return_value = [
            {"_id": "1", "title": "API Test", "date": "02-01-2025"}
        ]
        
        # Test valid search
        response = client.get("/notices/search?q=API")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['title'], "API Test")
        
        # Test empty search
        response = client.get("/notices/search?q=  ")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

if __name__ == '__main__':
    unittest.main()
