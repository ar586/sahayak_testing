import os
import pymongo
import certifi
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "notices_db"
COLLECTION_NAME = "notices"

def get_db():
    if not MONGO_URI:
        raise ValueError("MONGODB_URI not found in environment variables")
    client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    return client[DB_NAME]

def load_cache_from_db():
    """
    Loads existing notices from MongoDB to build the cache map.
    Returns a dict: (title, date) -> notice_dict
    """
    db = get_db()
    collection = db[COLLECTION_NAME]
    cache = {}
    try:
        # Fetch all notices
        cursor = collection.find({})
        for item in cursor:
            # Remove _id for cleaner cache usage if needed, or keep it
            if "_id" in item:
                item["_id"] = str(item["_id"])
            
            key = (item.get("title"), item.get("date"))
            if item.get("title"):
                cache[key] = item
        print(f"Loaded {len(cache)} entries from MongoDB cache.")
    except Exception as e:
        print(f"Error loading cache from MongoDB: {e}")
    return cache

def save_notice_to_db(notice):
    """
    Upserts a single notice into MongoDB.
    """
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    key_filter = {
        "title": notice.get("title"),
        "date": notice.get("date")
    }
    
    # If notice has _id, remove it before saving to avoid immutable field error during update
    notice_to_save = notice.copy()
    if "_id" in notice_to_save:
        del notice_to_save["_id"]
    
    # Remove link from storage as requested
    if "link" in notice_to_save:
        del notice_to_save["link"]

    try:
        result = collection.update_one(key_filter, {"$set": notice_to_save}, upsert=True)
        # print(f"Saved to DB: {notice.get('title')[:30]}")
        
        # Return True if a new document was inserted (upserted_id is set)
        return result.upserted_id is not None
    except Exception as e:
        print(f"Error saving notice to MongoDB: {e}")
        return False

# Chat history functions
CHAT_COLLECTION = "chat_history"

def save_chat_message(user_id, notice_id, role, content, user_branch=None, user_year=None):
    """
    Saves a chat message to MongoDB.
    Per-user, per-notice chat history.
    """
    db = get_db()
    collection = db[CHAT_COLLECTION]
    
    from datetime import datetime
    
    message = {
        "user_id": user_id,
        "notice_id": notice_id,
        "timestamp": datetime.utcnow(),
        "role": role,  # "user" or "assistant"
        "content": content,
        "user_branch": user_branch,
        "user_year": user_year
    }
    
    try:
        collection.insert_one(message)
    except Exception as e:
        print(f"Error saving chat message: {e}")

def get_chat_history(user_id, notice_id, limit=10):
    """
    Retrieves chat history for a specific user and notice.
    Returns list of messages in chronological order.
    """
    db = get_db()
    collection = db[CHAT_COLLECTION]
    
    try:
        cursor = collection.find(
            {"user_id": user_id, "notice_id": notice_id}
        ).sort("timestamp", 1).limit(limit)
        
        messages = []
        for msg in cursor:
            messages.append({
                "role": msg.get("role"),
                "content": msg.get("content")
            })
        return messages
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return []

def get_all_notices(page=1, limit=20):
    """
    Retrieves all successfully processed notices with pagination.
    Returns list of notices with basic info for frontend display.
    """
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    skip = (page - 1) * limit
    
    try:
        cursor = collection.find(
            {"status": {"$in": ["cached", "no_attachment", "external_doc", "gdrive_unhandled", "external_unknown"]}}
        ).sort("date", -1).skip(skip).limit(limit)
        
        notices = []
        for notice in cursor:
            notices.append({
                "_id": str(notice["_id"]),
                "title": notice.get("title"),
                "date": notice.get("date"),
                "summary": notice.get("summary", ""),
                "tags": notice.get("tags", {}),
                "cached_url": notice.get("cached_url", "")
            })
        
        return notices
    except Exception as e:
        print(f"Error retrieving notices: {e}")
        return []

def search_notices(query, page=1, limit=20):
    """
    Search notices by title or summary using regex.
    """
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    skip = (page - 1) * limit
    
    try:
        # Case-insensitive regex search
        regex_query = {"$regex": query, "$options": "i"}
        
        search_filter = {
            "$or": [
                {"title": regex_query},
                {"summary": regex_query}
            ],
            "status": {"$in": ["cached", "no_attachment", "external_doc", "gdrive_unhandled", "external_unknown"]}
        }
        
        cursor = collection.find(search_filter).sort("date", -1).skip(skip).limit(limit)
        
        notices = []
        for notice in cursor:
            notices.append({
                "_id": str(notice["_id"]),
                "title": notice.get("title"),
                "date": notice.get("date"),
                "summary": notice.get("summary", ""),
                "tags": notice.get("tags", {}),
                "cached_url": notice.get("cached_url", "")
            })
            
        return notices
    except Exception as e:
        print(f"Error searching notices: {e}")
        return []

def get_notice_by_id(notice_id):
    """
    Retrieves a single notice by ID with full details.
    """
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    try:
        from bson import ObjectId
        notice = collection.find_one({"_id": ObjectId(notice_id)})
        
        if notice:
            return {
                "_id": str(notice.get("_id")),
                "title": notice.get("title"),
                "date": notice.get("date"),
                "extracted_text": notice.get("extracted_text", ""),
                "summary": notice.get("summary", ""),
                "tags": notice.get("tags", {}),
                "link": notice.get("link", ""),
                "cached_url": notice.get("cached_url", "")
            }
        return None
    except Exception as e:
        print(f"Error retrieving notice: {e}")
        return None

# FCM Token Management
TOKEN_COLLECTION = "fcm_tokens"

def save_fcm_token(user_id, token):
    """
    Saves or updates an FCM token for a user.
    """
    db = get_db()
    collection = db[TOKEN_COLLECTION]
    
    try:
        # We can store usage metadata if needed
        collection.update_one(
            {"user_id": user_id},
            {"$addToSet": {"tokens": token}}, # Add to set to avoid duplicates
            upsert=True
        )
    except Exception as e:
        print(f"Error saving FCM token: {e}")

def remove_fcm_token(user_id, token):
    """
    Removes a specific FCM token for a user.
    """
    db = get_db()
    collection = db[TOKEN_COLLECTION]
    
    try:
        collection.update_one(
            {"user_id": user_id},
            {"$pull": {"tokens": token}}
        )
        print(f"Removed FCM token for user {user_id}")
    except Exception as e:
        print(f"Error removing FCM token: {e}")

def get_fcm_tokens(user_id):
    """
    Retrieves all FCM tokens for a user.
    """
    db = get_db()
    collection = db[TOKEN_COLLECTION]
    
    try:
        doc = collection.find_one({"user_id": user_id})
        if doc and "tokens" in doc:
            return doc["tokens"]
        return []
    except Exception as e:
        print(f"Error getting FCM tokens: {e}")
        return []

def get_all_fcm_tokens():
    """
    Retrieves all FCM tokens from all users.
    Returns a flat list of unique tokens.
    """
    db = get_db()
    collection = db[TOKEN_COLLECTION]
    
    unique_tokens = set()
    
    try:
        cursor = collection.find({})
        for doc in cursor:
            if "tokens" in doc and isinstance(doc["tokens"], list):
                for token in doc["tokens"]:
                    if token:
                        unique_tokens.add(token)
        
        return list(unique_tokens)
    except Exception as e:
        print(f"Error retrieval all FCM tokens: {e}")
        return []

# Notification Log Management
NOTIFICATION_LOG_COLLECTION = "notification_logs"

def is_notification_sent(title, date):
    """
    Checks if a notification has already been sent for a specific notice.
    """
    db = get_db()
    collection = db[NOTIFICATION_LOG_COLLECTION]
    
    try:
        doc = collection.find_one({"title": title, "date": date})
        return doc is not None
    except Exception as e:
        print(f"Error checking notification log: {e}")
        return False

def mark_notification_sent(title, date):
    """
    Marks a notification as sent in the log to prevent duplicates.
    """
    db = get_db()
    collection = db[NOTIFICATION_LOG_COLLECTION]
    
    try:
        from datetime import datetime
        collection.update_one(
            {"title": title, "date": date},
            {"$set": {
                "title": title,
                "date": date,
                "sent_at": datetime.utcnow()
            }},
            upsert=True
        )
    except Exception as e:
        print(f"Error marking notification as sent: {e}")
