from database import get_db, COLLECTION_NAME
from utils import convert_date_to_iso
import re

def force_fix_dates():
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    print("Scanning for bad date formats (DD-MM-YYYY)...")
    
    # Regex for DD-MM-YYYY
    # We can't easily use regex in find({}) unless we use $regex operator
    # querying all for safety
    cursor = collection.find({})
    
    BAD_DATE_REGEX = re.compile(r"^\d{2}-\d{2}-\d{4}$")
    
    fixed_count = 0
    total_checked = 0
    
    for notice in cursor:
        total_checked += 1
        original_date = notice.get("date")
        
        if not original_date:
            continue
            
        if BAD_DATE_REGEX.match(str(original_date)):
            new_date = convert_date_to_iso(original_date)
            if new_date and new_date != original_date:
                # print(f"Fixing: {original_date} -> {new_date}")
                collection.update_one(
                    {"_id": notice["_id"]},
                    {"$set": {"date": new_date}}
                )
                fixed_count += 1
    
    print(f"Scanned {total_checked} documents.")
    print(f"Fixed {fixed_count} documents.")

if __name__ == "__main__":
    force_fix_dates()
