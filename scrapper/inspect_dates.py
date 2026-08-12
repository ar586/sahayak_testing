from database import get_all_notices, get_db, COLLECTION_NAME

def inspect_dates():
    print("--- Top 20 Notices (descending sort) ---")
    notices = get_all_notices(limit=20)
    for n in notices:
        print(f"Date: '{n.get('date')}' - Title: {n.get('title')[:30]}")

    print("\n\n--- Sample of Raw DB Documents (first 10) ---")
    db = get_db()
    cursor = db[COLLECTION_NAME].find({}).limit(10)
    for doc in cursor:
        print(f"Raw Date: '{doc.get('date')}'")

if __name__ == "__main__":
    inspect_dates()
