import os
import json
import firebase_admin
from firebase_admin import credentials, messaging

_firebase_initialized = False

def init_firebase():
    """
    Initializes Firebase Admin SDK if not already initialized.
    Uses FIREBASE_CREDENTIALS environment variable.
    """
    global _firebase_initialized
    if _firebase_initialized:
        return

    try:
        # Check if already initialized by another part of the app or previous run
        if firebase_admin._apps:
            _firebase_initialized = True
            return

        firebase_creds_json = os.environ.get("FIREBASE_CREDENTIALS")
        cred = None
        
        if firebase_creds_json:
            try:
                # Clean up key if it was pasted with quotes on deployment platform
                clean_json = firebase_creds_json.strip().strip("'").strip('"')
                cred_dict = json.loads(clean_json)
                cred = credentials.Certificate(cred_dict)
                print("Loaded Firebase credentials from environment variable.")
            except json.JSONDecodeError as e:
                print(f"Error decoding FIREBASE_CREDENTIALS: {e}")
        
        if not cred:
            print("Warning: FIREBASE_CREDENTIALS env var not found or invalid. Notifications will not function.")
            return

        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        print("Firebase Admin SDK initialized.")

    except Exception as e:
        print(f"Error initializing Firebase Admin: {e}")

def send_multicast_message(title, body, tokens):
    """
    Sends a multicast message to a list of tokens.
    """
    if not tokens:
        return {"success_count": 0, "failure_count": 0}

    init_firebase()
    if not _firebase_initialized:
        print("Firebase not initialized. Skipping notification.")
        return {"success_count": 0, "failure_count": 0}

    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            tokens=tokens,
        )
        
        response = messaging.send_each_for_multicast(message)
        print(f"Sent notification '{title}'. Success: {response.success_count}, Failed: {response.failure_count}")
        return {
            "success_count": response.success_count,
            "failure_count": response.failure_count
        }
    except Exception as e:
        print(f"Error sending multicast message: {e}")
        return {"success_count": 0, "failure_count": 0}

def send_notice_notification(notice):
    """
    Sends a notification to all users about a new notice.
    """
    try:
        from database import get_all_fcm_tokens, is_notification_sent, mark_notification_sent
        
        # Check if already sent
        if is_notification_sent(notice.get("title"), notice.get("date")):
            print(f"Notification already sent for: {notice.get('title')[:30]}")
            return

        tokens = get_all_fcm_tokens()
        if not tokens:
            print("No users to notify.")
            return

        title = "New Notice Available"
        body = notice.get("title", "")
        # Fallback if title is empty
        if not body:
            body = "Check the app for a new update."
        
        # Truncate body if too long for notification
        if len(body) > 100:
            body = body[:97] + "..."

        result = send_multicast_message(title, body, tokens)
        
        # Mark as sent if we attempted to send
        # Even if success_count is 0, we mark it to avoid spamming indefinitely on failure
        mark_notification_sent(notice.get("title"), notice.get("date"))
        
    except Exception as e:
        print(f"Error in send_notice_notification: {e}")
