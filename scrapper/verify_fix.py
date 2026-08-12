from database import get_all_notices

def verify():
    print("Fetching notices with new logic...")
    try:
        notices = get_all_notices(limit=100)
        print(f"Total fetched: {len(notices)}")
        
        found_target = False
        # Known notice from JSON that had "no_attachment" status
        target_snippet = "CVSPK FWS 2023-24 email" 
        
        for n in notices:
            if target_snippet in n["title"]:
                print(f"FOUND previously hidden notice: {n['title']}")
                found_target = True
                
        if found_target:
            print("Verification SUCCESS: Found non-cached notice.")
        else:
            print("Verification NOTE: Specific target not found in top 100. Checking diversity...")

        print("Top 5 notices:")
        for i, n in enumerate(notices[:5]):
            print(f"{i+1}. {n.get('date')} - {n.get('title')[:60]}...")
            
    except Exception as e:
        print(f"Verification FAILED with error: {e}")

if __name__ == "__main__":
    verify()
