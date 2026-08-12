import requests
import json
import time

def verify_streaming():
    url = "http://localhost:8000/chat"
    
    # We need a valid notice_id and user_id. 
    # For test, we use dummy values, assuming the backend might error on ID check 
    # OR we fetch a real one first. Let's try to fetch a real notice first.
    
    try:
        print("Fetching a notice ID...")
        notices_res = requests.get("http://localhost:8000/notices?limit=1")
        if notices_res.status_code != 200:
            print("Failed to fetch notices.")
            return

        notices = notices_res.json()
        if not notices:
            print("No notices found.")
            return
            
        notice_id = notices[0]["_id"]
        print(f"Using Notice ID: {notice_id}")
        
        payload = {
            "query": "Summarize this notice",
            "user_id": "test_user_123",
            "notice_id": notice_id,
            "user_branch": "CSE",
            "user_year": "3"
        }
        
        print("\nSending stream request...")
        start_time = time.time()
        
        with requests.post(url, json=payload, stream=True) as r:
            if r.status_code == 200:
                print("Response received. Reading stream...")
                for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        print(chunk, end="", flush=True)
            else:
                print(f"Request failed: {r.status_code} - {r.text}")
                
        duration = time.time() - start_time
        print(f"\n\nStream completed in {duration:.2f} seconds.")
        
    except Exception as e:
        print(f"Verification script failed: {e}")
        print("Ensure the server is running on localhost:8000")

if __name__ == "__main__":
    verify_streaming()
