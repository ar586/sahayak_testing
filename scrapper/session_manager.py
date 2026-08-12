# scraper/session_manager.py
import requests

def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })
    return session

def get_phpsessid(session):
    url = "https://www.imsnsit.org/imsnsit/notifications.php"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,en-IN;q=0.8",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "imsnsit.org",
        "Referer": "https://imsnsit.org/imsnsit/student.htm",
        "Sec-Fetch-Dest": "frame",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36 Edg/134.0.0.0",
        "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Microsoft Edge\";v=\"134\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "Android"
    }
    
    # Update session headers with the required ones
    session.headers.update(headers)
    
    response = session.get(url)
    response.raise_for_status()
    
    # Iterate to find the cookie to avoid "Multiple cookies with name" error
    phpsessid = None
    for cookie in session.cookies:
        if cookie.name == "PHPSESSID":
            phpsessid = cookie.value
            # We take the first one we find or the last one? 
            # Usually the last one set is effective, but let's break on first found 
            # if we trust it, or iterate all.
            # Given the error is "multiple cookies", let's just grab one.
            if phpsessid:
                break
    
    return phpsessid
