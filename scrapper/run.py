from session_manager import create_session
from database import load_cache_from_db, save_notice_to_db
from fetch_html import fetch_notices_html
from parse_notices import parse_notices
from downloader import download_protected_resource
from cloudinary_client import upload_to_cloudinary
import json
from processor import process_notice
import requests


import os

from notification_service import init_firebase, send_notice_notification

def scrape_notices():
    # Ensure Firebase is ready for notifications
    init_firebase()

    session = create_session()

    html = fetch_notices_html(session)
    notices = parse_notices(html)

    # Load existing cache
    existing_cache = load_cache_from_db()

    processed = []
    for notice in notices:
        # Check if already cached successfully using (title, date)
        key = (notice.get("title"), notice.get("date"))
        
        if key in existing_cache and existing_cache[key].get("status") == "cached":
            print(f"Skipping (already cached): {notice['title'][:30]}...")
            processed.append(existing_cache[key])
            continue

        try:
            print(f"Processing: {notice['title'][:30]}...")
            processed_notice = process_notice(session, notice)
            
            # Save to MongoDB immediately
            is_new_insert = save_notice_to_db(processed_notice)
            
            # Send notification ONLY if it was a newly inserted document
            if is_new_insert:
                 print(f"New notice inserted. Sending notification for: {processed_notice['title'][:30]}")
                 send_notice_notification(processed_notice)
            else:
                 print(f"Notice updated or already exists in DB. Skipping notification.")
            
            processed.append(processed_notice)
        except Exception as e:
            print("Failed:", notice["title"], e)

    with open("notices_final.json", "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)

    print(f"Processed {len(processed)} notices")
    return len(processed)

if __name__ == "__main__":
    scrape_notices()
