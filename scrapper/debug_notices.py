import requests
import sys

try:
    print("Testing /notices endpoint...")
    response = requests.get("http://localhost:8000/notices?page=1&limit=20")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Retrieved {len(data)} notices.")
        if len(data) > 0:
            print(f"First notice: {data[0]['title']}")
        else:
            print("Warning: Retrieved 0 notices. The DB might be empty or query failed.")
    else:
        print(f"Error: Status code {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Exception: {e}")
