import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "nvidia/nemotron-nano-12b-v2-vl:free"

def generate_summary(text):
    """
    Generates a summary for the given text using OpenRouter API.
    Returns the summary string or empty string on failure/skip.
    """
    if not text or len(text.strip()) < 50:
        return ""

    if not OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY not found. Skipping summarization.")
        return ""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Optional: Add site URL and name for OpenRouter rankings
        "HTTP-Referer": "https://github.com/aryansahayak/scrapper", 
        "X-Title": "Notice Scrapper"
    }

    # Truncate input text to avoid hitting context limits if it's massive
    # The model 12B probably handles 4k-8k context, let's play safe with ~12000 chars (~3000 tokens)
    # Actually nemotron might have larger context but safe side.
    safe_text = text[:12000]

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes academic or official notices. distinctively. Keep the summary concise (2-3 sentences) and highlight the key dates and actions required."
            },
            {
                "role": "user",
                "content": f"Summarize the following notice text:\n\n{safe_text}"
            }
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            summary = data["choices"][0]["message"]["content"].strip()
            return summary
        else:
            print("OpenRouter response did not contain choices.")
            return ""

    except Exception as e:
        print(f"Error generating summary: {e}")
        return ""
