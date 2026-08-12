from database import get_db, COLLECTION_NAME
from utils import convert_date_to_iso

def migrate_dates():
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    # Verify connection
    count = collection.count_documents({})
    print(f"Found {count} documents in collection '{COLLECTION_NAME}'")
    
    cursor = collection.find({})
    modified_count = 0
    
    for notice in cursor:
        original_date = notice.get("date")
        if not original_date:
            continue
            
        # Check if already ISO (Basic check: YYYY-MM-DD has '-' at index 4)
        if len(original_date) == 10 and original_date[4] == "-":
            continue
            
        new_date = convert_date_to_iso(original_date)
        if new_date and new_date != original_date:
            collection.update_one(
                {"_id": notice["_id"]},
                {"$set": {"date": new_date}}
            )
            modified_count += 1
            if modified_count % 50 == 0:
                print(f"Migrated {modified_count} notices...")
                
    print(f"Migration completed. Total updated: {modified_count}")

if __name__ == "__main__":
    migrate_dates()
