from database import get_all_notices

def verify_sorting():
    print("Fetching notices to check sorting...")
    try:
        notices = get_all_notices(limit=10)
        
        dates = [n.get("date") for n in notices]
        print("Dates in returned order:")
        for d in dates:
            print(d)
            
        print("-" * 20)
        
        # Check if strictly descending
        is_sorted = True
        for i in range(len(dates) - 1):
            if dates[i] < dates[i+1]: # Descending means i >= i+1. If i < i+1, it's wrong.
                is_sorted = False
                print(f"SORTING ERROR: {dates[i]} is older than {dates[i+1]}")
                break
                
        if is_sorted:
            print("SUCCESS: Notices are sorted correctly descending by date.")
            if dates[0].startswith("2026"):
                print("SUCCESS: 2026 notices are at the top.")
        else:
            print("FAILURE: Sorting order is incorrect.")

    except Exception as e:
        print(f"Verification FAILED with error: {e}")

if __name__ == "__main__":
    verify_sorting()
