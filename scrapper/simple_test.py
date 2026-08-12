#!/usr/bin/env python3
"""
Simple script to test the chat API with a real request.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("=== Testing Chat API ===\n")
    
    # Step 1: Get a notice
    print("1. Fetching notices...")
    response = requests.get(f"{BASE_URL}/notices")
    
    if response.status_code != 200:
        print(f"Error fetching notices: {response.status_code}")
        return
    
    notices = response.json()
    if not notices:
        print("No notices found!")
        return
    
    # Use the first notice
    notice = notices[0]
    notice_id = notice["_id"]
    print(f"   Selected notice: {notice['title'][:60]}...")
    print(f"   Notice ID: {notice_id}\n")
    
    # Step 2: Send a chat message
    print("2. Sending chat message...")
    chat_payload = {
        "query": "What is this notice about?",
        "user_id": "demo_user_001",
        "notice_id": notice_id,
        "user_branch": "CSE",
        "user_year": "3"
    }
    
    print(f"   Request: {json.dumps(chat_payload, indent=2)}\n")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=chat_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Response:\n{result['response']}\n")
        
        # Step 3: Check chat history
        print("3. Checking chat history...")
        history_response = requests.get(
            f"{BASE_URL}/chat/history/demo_user_001/{notice_id}"
        )
        
        if history_response.status_code == 200:
            history = history_response.json()
            print(f"   Found {len(history['messages'])} messages in history")
            for msg in history['messages']:
                role = msg['role'].upper()
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                print(f"   [{role}]: {content}")
        
        print("\n✅ Test completed successfully!")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    main()
