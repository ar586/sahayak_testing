#!/usr/bin/env python3
"""
Test script for the chat API.
"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def get_first_notice_id():
    """Get a valid notice ID to test with."""
    print("Fetching notices...")
    response = requests.get(f"{BASE_URL}/notices")
    if response.status_code == 200:
        notices = response.json()
        if notices and len(notices) > 0:
            return notices[0]['_id']
    return None

def test_chat(notice_id):
    """Test the chat endpoint."""
    print(f"Testing chat endpoint with notice_id: {notice_id}...")
    
    user_id = str(uuid.uuid4())
    
    payload = {
        "query": "What is this notice about?",
        "user_id": user_id,
        "notice_id": notice_id,
        "user_branch": "CSE",
        "user_year": "3"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['response']}\n")
        return user_id, notice_id
    else:
        print(f"Error: {response.text}\n")
        return None, None

def test_history(user_id, notice_id):
    """Test chat history retrieval."""
    print("Testing chat history...")
    
    response = requests.get(f"{BASE_URL}/chat/history/{user_id}/{notice_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Messages: {json.dumps(data.get('messages', []), indent=2)}\n")

if __name__ == "__main__":
    print("=== Chat API Test Suite ===\n")
    
    # Test health check
    test_health_check()
    
    # Get notice ID
    notice_id = get_first_notice_id()
    
    if notice_id:
        # Test chat
        user_id, nid = test_chat(notice_id)
        
        if user_id:
            # Test history
            test_history(user_id, notice_id)
    else:
        print("No notices found to test with.")
    
    print("=== Tests Complete ===")

