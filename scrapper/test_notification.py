import sys
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

# Add current dir to path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the database function BEFORE importing app/routes if they use it at module level, 
# but here it is used inside the endpoint.
from chat_api import app

client = TestClient(app)

def test_send_notification():
    user_id = "test_user"
    fake_token = "fake_device_token_for_testing"
    
    # Patch the get_fcm_tokens function in chat_api (or where it's imported)
    # Since chat_api imports it from database, we patch where it is used: chat_api.get_fcm_tokens
    with patch("chat_api.get_fcm_tokens", return_value=[fake_token]):
        print(f"Sending notification to {user_id} with token {fake_token}...")
        
        response = client.post(
            "/api/fcm/send",
            json={
                "user_id": user_id,
                "title": "Test Title",
                "body": "Test Body"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response JSON: {response.json()}")

if __name__ == "__main__":
    test_send_notification()
